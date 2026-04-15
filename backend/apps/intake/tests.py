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

    def test_documento_recebido_with_audit_fields(self):
        """Test that DocumentoRecebido can be created with all audit fields."""
        from django.utils import timezone

        validador = self.user_model.objects.create_user(
            email='validador@example.com',
            nome='Usuário Validador',
            password='validpass123',
        )

        arquivo = SimpleUploadedFile('contrato.pdf', b'conteudo-teste', content_type='application/pdf')
        agora = timezone.now()

        documento = DocumentoRecebido.objects.create(
            empresa=self.empresa,
            titulo='Documento com Auditoria',
            tipo_documento='GERAL',
            tipo_entrega='UPLOAD',
            competencia='2026-03-01',
            arquivo=arquivo,
            status='VALIDADO',
            enviado_por=self.user,
            validado_por=validador,
            validado_em=agora,
            origem_upload='BACKOFFICE',
            referencia_cliente='REF-001-2026',
        )

        # Verify all fields are set and queryable
        self.assertEqual(documento.enviado_por, self.user)
        self.assertEqual(documento.validado_por, validador)
        self.assertEqual(documento.validado_em, agora)
        self.assertEqual(documento.origem_upload, 'BACKOFFICE')
        self.assertEqual(documento.referencia_cliente, 'REF-001-2026')

        # Verify document can be queried by audit fields
        documento_encontrado = DocumentoRecebido.objects.get(enviado_por=self.user)
        self.assertEqual(documento_encontrado.id, documento.id)

        documento_encontrado = DocumentoRecebido.objects.get(validado_por=validador)
        self.assertEqual(documento_encontrado.id, documento.id)

    def test_documento_recebido_audit_fields_optional(self):
        """Test that audit fields can be null."""
        arquivo = SimpleUploadedFile('contrato.pdf', b'conteudo-teste', content_type='application/pdf')

        documento = DocumentoRecebido.objects.create(
            empresa=self.empresa,
            titulo='Documento sem Auditoria',
            tipo_documento='GERAL',
            tipo_entrega='UPLOAD',
            competencia='2026-03-01',
            arquivo=arquivo,
            status='NOVO',
            enviado_por=None,
            validado_por=None,
            validado_em=None,
            origem_upload='CLIENTE',
            referencia_cliente=None,
        )

        self.assertIsNone(documento.enviado_por)
        self.assertIsNone(documento.validado_por)
        self.assertIsNone(documento.validado_em)
        self.assertEqual(documento.origem_upload, 'CLIENTE')


class IsIntakeClientCompanyPermissionTest(APITestCase):
    def test_permission_grants_cliente_and_denies_anonymous(self):
        from rest_framework.test import APIRequestFactory
        from django.contrib.auth.models import AnonymousUser
        from backend.apps.core.permissions import IsIntakeClientCompany

        User = get_user_model()
        factory = APIRequestFactory()
        empresa = Empresa.objects.create(
            razao_social='Perm Test LTDA',
            nome_fantasia='Perm Test',
            cnpj='99999999000100',
            regime_tributario='SN',
            cnae_principal='1234567',
            cep='01001000',
            logradouro='Rua Teste',
            numero='1',
            bairro='Centro',
            municipio='São Paulo',
            uf='SP',
        )
        cliente = User.objects.create_user(
            email='cliente@example.com', nome='Cliente', password='x', perfil='CLIENTE',
        )
        cliente.empresa_ativa = empresa
        cliente.save(update_fields=['empresa_ativa'])
        PerfilPermissao.objects.create(usuario=cliente, empresa=empresa, perfil='CLIENTE')

        request = factory.get('/')
        request.user = cliente
        self.assertTrue(IsIntakeClientCompany().has_permission(request, None))

        request.user = AnonymousUser()
        self.assertFalse(IsIntakeClientCompany().has_permission(request, None))


class ClientePermissionIsolationTest(APITestCase):
    def test_cliente_permission_isolation(self):
        """Verify CLIENTE is blocked from backoffice endpoints but can access cliente endpoints."""
        from rest_framework.test import APIClient

        User = get_user_model()
        client = APIClient()

        empresa = Empresa.objects.create(
            razao_social='Isolation LTDA',
            nome_fantasia='Isolation',
            cnpj='88888888000111',
            regime_tributario='SN',
            cnae_principal='1234567',
            cep='01001000',
            logradouro='Rua Iso',
            numero='1',
            bairro='Centro',
            municipio='São Paulo',
            uf='SP',
        )
        portal = PortalCliente.objects.create(empresa=empresa, slug='test-iso')
        arquivo = SimpleUploadedFile('doc.pdf', b'x', content_type='application/pdf')
        DocumentoRecebido.objects.create(
            portal_cliente=portal,
            empresa=empresa,
            titulo='Test',
            tipo_documento='FINANCEIRO',
            tipo_entrega='UPLOAD',
            competencia='2026-04-01',
            arquivo=arquivo,
        )

        cliente_user = User.objects.create_user(
            email='cliente_iso@example.com',
            nome='Cliente Iso',
            password='x',
            perfil='CLIENTE',
        )
        cliente_user.empresa_ativa = empresa
        cliente_user.save(update_fields=['empresa_ativa'])
        PerfilPermissao.objects.create(usuario=cliente_user, empresa=empresa, perfil='CLIENTE')

        client.force_authenticate(user=cliente_user)

        # Should be blocked from backoffice endpoints
        self.assertEqual(client.get('/api/intake/recebimentos/').status_code, 403)
        self.assertEqual(client.get('/api/intake/checklists/').status_code, 403)
        self.assertEqual(client.get('/api/intake/pendencias/').status_code, 403)

        # Should be allowed on cliente endpoints
        self.assertEqual(client.get('/api/intake/cliente/recebimentos/').status_code, 200)
        self.assertEqual(client.get('/api/intake/cliente/portal/test-iso/').status_code, 200)

    def test_cliente_upload_creates_novo(self):
        """Verify client upload creates document with status=NOVO."""
        from rest_framework.test import APIClient

        User = get_user_model()
        client = APIClient()

        empresa = Empresa.objects.create(
            razao_social='Upload LTDA',
            nome_fantasia='Upload',
            cnpj='77777777000122',
            regime_tributario='SN',
            cnae_principal='1234567',
            cep='01001000',
            logradouro='Rua Up',
            numero='1',
            bairro='Centro',
            municipio='São Paulo',
            uf='SP',
        )
        PortalCliente.objects.create(empresa=empresa, slug='test-upload')

        cliente_user = User.objects.create_user(
            email='cliente_up@example.com',
            nome='Cliente Up',
            password='x',
            perfil='CLIENTE',
        )
        cliente_user.empresa_ativa = empresa
        cliente_user.save(update_fields=['empresa_ativa'])
        PerfilPermissao.objects.create(usuario=cliente_user, empresa=empresa, perfil='CLIENTE')

        client.force_authenticate(user=cliente_user)

        arquivo = SimpleUploadedFile('doc.pdf', b'fake pdf', content_type='application/pdf')

        response = client.post('/api/intake/cliente/recebimentos/', {
            'titulo': 'Test Doc',
            'tipo_documento': 'FINANCEIRO',
            'competencia': '2026-04-01',
            'arquivo': arquivo,
        }, format='multipart')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['status'], 'NOVO')
        self.assertEqual(response.data['titulo'], 'Test Doc')

        doc = DocumentoRecebido.objects.get(id=response.data['id'])
        self.assertEqual(doc.origem_upload, 'CLIENTE')
        self.assertEqual(doc.enviado_por, cliente_user)


class FileValidationTest(APITestCase):
    def test_valid_and_invalid_extensions(self):
        from backend.apps.intake.services import validate_file_extension

        for ext in ['.pdf', '.xml', '.csv', '.zip', '.jpg', '.jpeg', '.png']:
            is_valid, err = validate_file_extension(f'doc{ext}')
            self.assertTrue(is_valid, f'extension {ext} should be allowed')
            self.assertIsNone(err)

        for ext in ['.exe', '.txt', '.html', '.sh']:
            is_valid, err = validate_file_extension(f'doc{ext}')
            self.assertFalse(is_valid, f'extension {ext} must be blocked')
            self.assertIsNotNone(err)

    def test_file_size_validation(self):
        from backend.apps.intake.services import validate_file_size

        class FakeFile:
            def __init__(self, size):
                self.size = size

        is_valid, _ = validate_file_size(FakeFile(1024), max_size_mb=10)
        self.assertTrue(is_valid)

        is_valid, err = validate_file_size(FakeFile(11 * 1024 * 1024), max_size_mb=10)
        self.assertFalse(is_valid)
        self.assertIn('10MB', err)
