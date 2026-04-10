from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from backend.apps.core.models import PerfilPermissao
from backend.apps.empresas.models import Empresa
from .models import DocumentoRecebido, LoteExportacaoQuestor, Pendencia, PortalCliente


class IntakeAPITestCase(APITestCase):
    def setUp(self):
        self.user_model = get_user_model()
        self.user = self.user_model.objects.create_user(
            email='intake@example.com',
            nome='Usuário Intake',
            password='password123',
        )
        self.portal_user = self.user_model.objects.create_user(
            email='portal@example.com',
            nome='Usuário Cliente',
            password='clientpassword',
        )
        self.empresa = Empresa.objects.create(
            razao_social='Empresa Intake',
            nome_fantasia='Intake',
            cnpj='12345678000195',
            regime_tributario='SN',
            cnae_principal='1234567',
            cep='01001000',
            logradouro='Praça da Sé',
            numero='100',
            bairro='Centro',
            municipio='São Paulo',
            uf='SP',
        )
        PerfilPermissao.objects.create(usuario=self.user, empresa=self.empresa, perfil='ADMIN')
        PerfilPermissao.objects.create(usuario=self.portal_user, empresa=self.empresa, perfil='CLIENTE')
        self.user.empresa_ativa = self.empresa
        self.user.save(update_fields=['empresa_ativa'])
        self.portal_user.empresa_ativa = self.empresa
        self.portal_user.save(update_fields=['empresa_ativa'])

        token = self.client.post(reverse('token_obtain_pair'), {
            'email': self.user.email,
            'password': 'password123',
        }, format='json').data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    def authenticate_portal_user(self):
        token = self.client.post(reverse('token_obtain_pair'), {
            'email': self.portal_user.email,
            'password': 'clientpassword',
        }, format='json').data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    def test_upload_documento_recebido(self):
        portal = PortalCliente.objects.create(
            empresa=self.empresa,
            slug='cliente-intake',
            email_responsavel='cliente@example.com',
        )
        arquivo = SimpleUploadedFile('extrato.pdf', b'arquivo-de-teste', content_type='application/pdf')
        response = self.client.post(
            reverse('recebimento-list'),
            {
                'titulo': 'Extrato Bancário Março',
                'tipo_documento': 'FINANCEIRO',
                'tipo_entrega': 'UPLOAD',
                'competencia': '2026-03-01',
                'portal_cliente': str(portal.id),
                'arquivo': arquivo,
            },
            format='multipart',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(DocumentoRecebido.objects.count(), 1)
        self.assertEqual(DocumentoRecebido.objects.first().status, 'VALIDADO')
        self.assertEqual(response.data['portal_cliente_slug'], 'cliente-intake')

    def test_criar_portal_cliente(self):
        response = self.client.post(
            reverse('portal-cliente-list'),
            {
                'slug': 'cliente-portal',
                'email_responsavel': 'portal@example.com',
                'telefone_responsavel': '71999999999',
                'recebe_alertas': True,
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(PortalCliente.objects.count(), 1)
        self.assertEqual(PortalCliente.objects.first().empresa, self.empresa)

    def test_documento_fiscal_sem_nota_gera_pendencia(self):
        arquivo = SimpleUploadedFile('nota.xml', b'<xml></xml>', content_type='application/xml')
        response = self.client.post(
            reverse('recebimento-list'),
            {
                'titulo': 'XML de nota sem vínculo',
                'tipo_documento': 'FISCAL',
                'tipo_entrega': 'UPLOAD',
                'competencia': '2026-03-01',
                'arquivo': arquivo,
            },
            format='multipart',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'REPROVADO')
        self.assertEqual(Pendencia.objects.count(), 1)

    def test_exportar_questor(self):
        DocumentoRecebido.objects.create(
            empresa=self.empresa,
            titulo='Contrato validado',
            tipo_documento='GERAL',
            tipo_entrega='MANUAL',
            competencia='2026-03-01',
            arquivo=SimpleUploadedFile('contrato.pdf', b'conteudo', content_type='application/pdf'),
            status='VALIDADO',
        )

        response = self.client.post(
            reverse('intake-exportar-questor'),
            {'competencia': '2026-03'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(LoteExportacaoQuestor.objects.count(), 1)
        self.assertEqual(LoteExportacaoQuestor.objects.first().status, 'EXPORTADO')

    def test_cliente_profile_cannot_access_intake_backoffice(self):
        self.authenticate_portal_user()

        response = self.client.get(reverse('recebimento-list'), format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_rejects_disallowed_upload_extension(self):
        arquivo = SimpleUploadedFile('payload.html', b'<script>alert(1)</script>', content_type='text/html')

        response = self.client.post(
            reverse('recebimento-list'),
            {
                'titulo': 'Arquivo inválido',
                'tipo_documento': 'GERAL',
                'tipo_entrega': 'UPLOAD',
                'competencia': '2026-03-01',
                'arquivo': arquivo,
            },
            format='multipart',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['errors'][0]['field'], 'arquivo')
