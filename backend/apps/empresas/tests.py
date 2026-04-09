from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from unittest.mock import patch
from backend.apps.empresas.models import Empresa, ConfiguracaoFiscalEmpresa
from backend.apps.core.models import PerfilPermissao

class EmpresaAPITestCase(APITestCase):
    def setUp(self):
        self.User = get_user_model()
        self.user = self.User.objects.create_user(
            email='test@example.com',
            nome='Test User',
            password='password123'
        )
        self.user_admin = self.User.objects.create_superuser(
            email='admin@example.com',
            nome='Admin User',
            password='adminpassword'
        )

        self.empresa_url = reverse('empresa-list')
        self.empresa1 = Empresa.objects.create(
            razao_social='Empresa Teste 1',
            nome_fantasia='EmpTest 1',
            cnpj='00000000000100',
            regime_tributario='SN',
            cnae_principal='1234567',
            cep='00000000',
            logradouro='Rua Teste',
            numero='100',
            bairro='Centro',
            municipio='Cidade Teste',
            uf='SP'
        )
        self.empresa2 = Empresa.objects.create(
            razao_social='Empresa Teste 2',
            nome_fantasia='EmpTest 2',
            cnpj='00000000000200',
            regime_tributario='LP',
            cnae_principal='7654321',
            cep='00000000',
            logradouro='Av Exemplo',
            numero='200',
            bairro='Bairro Exemplo',
            municipio='Outra Cidade',
            uf='RJ'
        )

        PerfilPermissao.objects.create(usuario=self.user, empresa=self.empresa1, perfil='ADMIN')
        PerfilPermissao.objects.create(usuario=self.user_admin, empresa=self.empresa1, perfil='ADMIN')
        PerfilPermissao.objects.create(usuario=self.user_admin, empresa=self.empresa2, perfil='ADMIN')
        
        self.user.empresa_ativa = self.empresa1
        self.user.save()
        self.user_admin.empresa_ativa = self.empresa1
        self.user_admin.save()


    def get_auth_token(self, user):
        response = self.client.post(reverse('token_obtain_pair'), {
            'email': user.email,
            'password': 'password123' if not user.is_superuser else 'adminpassword'
        }, format='json')
        return response.data['access']

    def test_create_empresa(self):
        token = self.get_auth_token(self.user_admin)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        data = {
            'razao_social': 'Nova Empresa Ltda',
            'nome_fantasia': 'NovaEmp',
            'cnpj': '12345678000195',
            'regime_tributario': 'MEI',
            'cnae_principal': '5000000',
            'cep': '01001000',
            'logradouro': 'Rua Nova',
            'numero': '300',
            'bairro': 'Centro',
            'municipio': 'Sao Paulo',
            'uf': 'SP'
        }
        response = self.client.post(self.empresa_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Empresa.objects.count(), 3)
        self.assertTrue(
            PerfilPermissao.objects.filter(
                usuario=self.user_admin,
                empresa__cnpj='12345678000195',
                perfil='ADMIN',
            ).exists()
        )
    
    def test_list_empresas_regular_user(self):
        token = self.get_auth_token(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get(self.empresa_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1) # User should only see his active company
        self.assertEqual(response.data['results'][0]['id'], str(self.empresa1.id))
    
    def test_list_empresas_superuser(self):
        token = self.get_auth_token(self.user_admin)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get(self.empresa_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)

    def test_regular_user_cannot_access_other_company(self):
        token = self.get_auth_token(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get(reverse('empresa-detail', kwargs={'pk': self.empresa2.id}), format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_empresa(self):
        token = self.get_auth_token(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get(reverse('empresa-detail', kwargs={'pk': self.empresa1.id}), format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nome_fantasia'], 'EmpTest 1')

    def test_update_empresa(self):
        token = self.get_auth_token(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        data = {'nome_fantasia': 'Empresa Teste 1 Modificada'}
        response = self.client.patch(reverse('empresa-detail', kwargs={'pk': self.empresa1.id}), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.empresa1.refresh_from_db()
        self.assertEqual(self.empresa1.nome_fantasia, 'Empresa Teste 1 Modificada')

    def test_soft_delete_empresa(self):
        token = self.get_auth_token(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.delete(reverse('empresa-detail', kwargs={'pk': self.empresa1.id}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.empresa1.refresh_from_db()
        self.assertFalse(self.empresa1.ativo)

    def test_select_empresa(self):
        token = self.get_auth_token(self.user_admin) # Using superuser to access both companies
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.post(reverse('empresa-selecionar', kwargs={'pk': self.empresa2.id}), format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user_admin.refresh_from_db()
        self.assertEqual(self.user_admin.empresa_ativa, self.empresa2)

    def test_desselecionar_empresa(self):
        token = self.get_auth_token(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.post(reverse('empresa-desselecionar'), format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertIsNone(self.user.empresa_ativa)
    
    def test_buscar_cep_action(self):
        token = self.get_auth_token(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        with patch('backend.apps.empresas.views.buscar_cep') as mock_buscar_cep:
            mock_buscar_cep.return_value = {
                'cep': '01001-000', 'logradouro': 'Praça da Sé', 'bairro': 'Sé',
                'localidade': 'São Paulo', 'uf': 'SP', 'ibge': '3550308'
            }
            response = self.client.post(reverse('empresa-buscar-cep'), {'cep': '01001000'}, format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data['uf'], 'SP')
    
    def test_resumo_fiscal_action(self):
        token = self.get_auth_token(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get(reverse('empresa-resumo-fiscal', kwargs={'pk': self.empresa1.id}), format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nome_fantasia'], 'EmpTest 1')
        self.assertIn('nfe_emitidas_mes', response.data)
