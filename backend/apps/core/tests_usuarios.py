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
