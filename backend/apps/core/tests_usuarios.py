from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from backend.apps.core.models import PerfilPermissao
from backend.apps.empresas.models import Empresa

User = get_user_model()


def _make_empresa():
    return Empresa.objects.create(
        razao_social='Empresa Teste',
        nome_fantasia='Teste',
        cnpj='12345678000195',
        regime_tributario='SN',
        cnae_principal='1234567',
        cep='01001000',
        logradouro='Rua A',
        numero='1',
        bairro='Centro',
        municipio='São Paulo',
        uf='SP',
    )


def _make_user(email, nome, empresa, perfil, password='senha123'):
    user = User.objects.create_user(email=email, nome=nome, password=password)
    user.empresa_ativa = empresa
    user.save(update_fields=['empresa_ativa'])
    PerfilPermissao.objects.create(usuario=user, empresa=empresa, perfil=perfil)
    return user


def _token(client, email, password='senha123'):
    resp = client.post(reverse('token_obtain_pair'), {'email': email, 'password': password}, format='json')
    return resp.data['access']


class UsuarioGestaoSerializerTest(APITestCase):
    def setUp(self):
        self.empresa = _make_empresa()
        self.admin = _make_user('admin@t.test', 'Admin', self.empresa, 'ADMIN')
        token = _token(self.client, 'admin@t.test')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    def test_cria_usuario_equipe(self):
        url = reverse('usuarios-list')
        payload = {
            'email': 'novo@t.test',
            'nome': 'Novo Membro',
            'perfil': 'CONTADOR',
            'senha_temporaria': 'temp1234',
        }
        resp = self.client.post(url, payload, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED, resp.data)
        self.assertEqual(resp.data['email'], 'novo@t.test')
        self.assertEqual(resp.data['perfil_empresa'], 'CONTADOR')
        self.assertTrue(User.objects.filter(email='novo@t.test').exists())
        self.assertTrue(PerfilPermissao.objects.filter(usuario__email='novo@t.test', perfil='CONTADOR').exists())

    def test_cria_cliente_portal(self):
        url = reverse('usuarios-list')
        payload = {
            'email': 'cliente@t.test',
            'nome': 'Cliente Portal',
            'perfil': 'CLIENTE',
            'senha_temporaria': 'temp1234',
        }
        resp = self.client.post(url, payload, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED, resp.data)
        self.assertEqual(resp.data['perfil_empresa'], 'CLIENTE')

    def test_lista_equipe_exclui_clientes(self):
        _make_user('equipe@t.test', 'Equipe', self.empresa, 'CONTADOR')
        _make_user('cliente@t.test', 'Cliente', self.empresa, 'CLIENTE')
        url = reverse('usuarios-list') + '?tipo=equipe'
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        emails = [u['email'] for u in resp.data['results']]
        self.assertIn('equipe@t.test', emails)
        self.assertNotIn('cliente@t.test', emails)

    def test_lista_clientes_inclui_so_clientes(self):
        _make_user('equipe@t.test', 'Equipe', self.empresa, 'CONTADOR')
        _make_user('cliente@t.test', 'Cliente', self.empresa, 'CLIENTE')
        url = reverse('usuarios-list') + '?tipo=cliente'
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        emails = [u['email'] for u in resp.data['results']]
        self.assertIn('cliente@t.test', emails)
        self.assertNotIn('equipe@t.test', emails)

    def test_edita_perfil(self):
        membro = _make_user('membro@t.test', 'Membro', self.empresa, 'AUXILIAR')
        url = reverse('usuarios-detail', args=[membro.id])
        resp = self.client.patch(url, {'perfil': 'FINANCEIRO'}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK, resp.data)
        self.assertEqual(
            PerfilPermissao.objects.get(usuario=membro, empresa=self.empresa).perfil,
            'FINANCEIRO',
        )
        self.assertEqual(resp.data['perfil_empresa'], 'FINANCEIRO')

    def test_desativa_usuario(self):
        membro = _make_user('membro2@t.test', 'Membro2', self.empresa, 'CONSULTA')
        url = reverse('usuarios-detail', args=[membro.id])
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        membro.refresh_from_db()
        self.assertFalse(membro.is_active)
        self.assertFalse(
            PerfilPermissao.objects.get(usuario=membro, empresa=self.empresa).ativo
        )

    def test_nao_pode_desativar_si_mesmo(self):
        url = reverse('usuarios-detail', args=[self.admin.id])
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_contador_nao_pode_criar_usuario(self):
        contador = _make_user('contador@t.test', 'Contador', self.empresa, 'CONTADOR')
        token = _token(self.client, 'contador@t.test')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        url = reverse('usuarios-list')
        resp = self.client.post(url, {'email': 'x@t.test', 'nome': 'X', 'perfil': 'CONSULTA', 'senha_temporaria': 'abc'}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_reativa_usuario(self):
        membro = _make_user('inativo@t.test', 'Inativo', self.empresa, 'CONSULTA')
        # First deactivate
        membro.is_active = False
        membro.save(update_fields=['is_active'])
        PerfilPermissao.objects.filter(usuario=membro, empresa=self.empresa).update(ativo=False)
        # Reactivate via endpoint
        url = reverse('usuarios-reativar', args=[membro.id])
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK, resp.data)
        membro.refresh_from_db()
        self.assertTrue(membro.is_active)
        self.assertTrue(PerfilPermissao.objects.get(usuario=membro, empresa=self.empresa).ativo)

    def test_portal_slug_no_jwt(self):
        """portal_cliente_slug aparece no JWT quando o CLIENTE tem portal vinculado."""
        from backend.apps.intake.models import PortalCliente
        from backend.apps.empresas.models import Empresa
        empresa = Empresa.objects.create(
            razao_social='Empresa Portal',
            nome_fantasia='Portal',
            cnpj='11111111000191',
            regime_tributario='SN',
            cnae_principal='1234567',
            cep='01001000',
            logradouro='Rua A',
            numero='1',
            bairro='Centro',
            municipio='São Paulo',
            uf='SP',
        )
        portal = PortalCliente.objects.create(
            empresa=empresa,
            slug='acme-portal',
            email_responsavel='p@acme.com',
        )
        cliente = _make_user('portal_jwt@test.com', 'Portal JWT', empresa, 'CLIENTE')
        from backend.apps.core.models import PerfilPermissao
        PerfilPermissao.objects.filter(usuario=cliente, empresa=empresa).update(portal_cliente=portal)

        token_resp = self.client.post(reverse('token_obtain_pair'), {
            'email': 'portal_jwt@test.com',
            'password': 'senha123',
        }, format='json')
        self.assertEqual(token_resp.status_code, 200)
        import jwt
        payload = jwt.decode(token_resp.data['access'], options={'verify_signature': False})
        self.assertEqual(payload.get('portal_cliente_slug'), 'acme-portal')

    def test_cria_cliente_com_portal(self):
        """Criar CLIENTE vinculando portal_cliente — o PerfilPermissao fica com portal_cliente preenchido."""
        from backend.apps.intake.models import PortalCliente
        from backend.apps.empresas.models import Empresa
        empresa = Empresa.objects.create(
            razao_social='Empresa CP',
            nome_fantasia='CP',
            cnpj='22222222000188',
            regime_tributario='SN',
            cnae_principal='1234567',
            cep='01001000',
            logradouro='Rua A',
            numero='1',
            bairro='Centro',
            municipio='São Paulo',
            uf='SP',
        )
        admin = _make_user('admin_cp@test.com', 'Admin CP', empresa, 'ADMIN')
        token = _token(self.client, 'admin_cp@test.com')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        portal = PortalCliente.objects.create(
            empresa=empresa,
            slug='test-portal',
            email_responsavel='p@test.com',
        )
        resp = self.client.post(
            '/api/core/usuarios/',
            {
                'nome': 'Cliente Portal',
                'email': 'cportal@test.com',
                'senha_temporaria': 'senha123',
                'perfil': 'CLIENTE',
                'portal_cliente': str(portal.id),
            },
            format='json',
        )
        self.assertEqual(resp.status_code, 201, resp.data)
        from backend.apps.core.models import PerfilPermissao, Usuario
        u = Usuario.objects.get(email='cportal@test.com')
        p = PerfilPermissao.objects.get(usuario=u, empresa=empresa)
        self.assertEqual(str(p.portal_cliente_id), str(portal.id))

    def test_isolamento_empresa(self):
        """Admin de outra empresa não vê usuários desta empresa."""
        from backend.apps.empresas.models import Empresa
        outra_empresa = Empresa.objects.create(
            razao_social='Outra Empresa',
            nome_fantasia='Outra',
            cnpj='98765432000199',
            regime_tributario='LP',
            cnae_principal='9999999',
            cep='01001000',
            logradouro='Av B',
            numero='2',
            bairro='Centro',
            municipio='SP',
            uf='SP',
        )
        outro_admin = _make_user('outro@t.test', 'Outro Admin', outra_empresa, 'ADMIN')
        token = _token(self.client, 'outro@t.test')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        url = reverse('usuarios-list') + '?tipo=equipe'
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        emails = [u['email'] for u in resp.data['results']]
        self.assertNotIn('admin@t.test', emails)
        self.assertIn('outro@t.test', emails)  # outro_admin vê apenas sua própria empresa
        self.assertEqual(len(resp.data['results']), 1)
