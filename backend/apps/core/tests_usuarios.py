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
