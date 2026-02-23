from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from backend.apps.empresas.models import Empresa
from backend.apps.core.models import PerfilPermissao
from backend.apps.cadastros.models import Cliente, Fornecedor, Produto

class CadastrosAPITestCase(APITestCase):
    def setUp(self):
        self.User = get_user_model()
        self.user = self.User.objects.create_user(
            email='test@example.com',
            nome='Test User',
            password='password123'
        )

        self.empresa1 = Empresa.objects.create(
            razao_social='Empresa Cadastros 1',
            nome_fantasia='Cadastros 1',
            cnpj='00000000000101',
            regime_tributario='SN',
            cnae_principal='1234567',
            cep='00000000',
            logradouro='Rua Cadastro',
            numero='1',
            bairro='Centro',
            municipio='Cidade Cadastro',
            uf='SP'
        )
        self.empresa2 = Empresa.objects.create(
            razao_social='Empresa Cadastros 2',
            nome_fantasia='Cadastros 2',
            cnpj='00000000000202',
            regime_tributario='LP',
            cnae_principal='7654321',
            cep='00000000',
            logradouro='Av Cadastro',
            numero='2',
            bairro='Bairro Cadastro',
            municipio='Outra Cadastro',
            uf='RJ'
        )

        PerfilPermissao.objects.create(usuario=self.user, empresa=self.empresa1, perfil='ADMIN')
        self.user.empresa_ativa = self.empresa1
        self.user.save()

        self.token = self._get_auth_token(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

        self.cliente_url = reverse('cliente-list')
        self.fornecedor_url = reverse('fornecedor-list')
        self.produto_url = reverse('produto-list')

    def _get_auth_token(self, user):
        response = self.client.post(reverse('token_obtain_pair'), {
            'email': user.email,
            'password': 'password123'
        }, format='json')
        return response.data['access']

    # --- Cliente Tests ---
    def test_create_cliente(self):
        data = {
            'nome_razao_social': 'Cliente Teste PF',
            'tipo_pessoa': 'PF',
            'documento': '11122233344',
            'email': 'cliente@test.com',
            'cep': '01001000',
            'logradouro': 'Rua Cliente',
            'numero': '123',
            'bairro': 'Bairro Cliente',
            'municipio': 'Sao Paulo',
            'uf': 'SP',
            'limite_credito': '1000.00'
        }
        response = self.client.post(self.cliente_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Cliente.objects.count(), 1)
        self.assertEqual(Cliente.objects.first().empresa, self.empresa1)

    def test_create_cliente_invalid_cnpj(self):
        data = {
            'nome_razao_social': 'Cliente Teste PJ',
            'tipo_pessoa': 'PJ',
            'documento': '11122233344', # CPF em campo de CNPJ
            'email': 'cliente_pj@test.com'
        }
        response = self.client.post(self.cliente_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('documento', response.data)

    def test_list_clientes_only_active_company(self):
        Cliente.objects.create(
            empresa=self.empresa1,
            nome_razao_social='Cliente 1 Empresa 1', tipo_pessoa='PF', documento='11111111111',
            cep='00000000', logradouro='Rua', numero='1', bairro='Bairro', municipio='Cidade', uf='SP'
        )
        Cliente.objects.create(
            empresa=self.empresa2,
            nome_razao_social='Cliente 1 Empresa 2', tipo_pessoa='PF', documento='22222222222',
            cep='00000000', logradouro='Rua', numero='1', bairro='Bairro', municipio='Cidade', uf='SP'
        ) # Should not be visible
        response = self.client.get(self.cliente_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['nome_razao_social'], 'Cliente 1 Empresa 1')

    # --- Fornecedor Tests ---
    def test_create_fornecedor(self):
        data = {
            'nome_razao_social': 'Fornecedor Teste PJ',
            'tipo_pessoa': 'PJ',
            'documento': '00000000000191',
            'email': 'fornecedor@test.com',
            'banco': 'Banco do Brasil',
            'agencia': '1234',
            'conta': '56789-0',
            'tipo_conta': 'CC',
            'cep': '01001000',
            'logradouro': 'Rua Fornecedor',
            'numero': '456',
            'bairro': 'Bairro Fornecedor',
            'municipio': 'Sao Paulo',
            'uf': 'SP',
        }
        response = self.client.post(self.fornecedor_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Fornecedor.objects.count(), 1)
        self.assertEqual(Fornecedor.objects.first().empresa, self.empresa1)

    # --- Produto Tests ---
    def test_create_produto(self):
        data = {
            'descricao': 'Produto Teste 1',
            'codigo_interno': 'PROD001',
            'ean': '1234567890123',
            'ncm': '12345678',
            'origem': '0',
            'preco_venda': '99.99',
            'preco_custo': '50.00',
            'estoque_atual': '10.000',
            'controla_estoque': True,
        }
        response = self.client.post(self.produto_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Produto.objects.count(), 1)
        self.assertEqual(Produto.objects.first().empresa, self.empresa1)

    def test_create_produto_duplicate_codigo_interno(self):
        Produto.objects.create(
            empresa=self.empresa1,
            descricao='Produto Existente',
            codigo_interno='PRODDUPLICADO',
            ncm='12345678',
            preco_venda='10.00'
        )
        data = {
            'descricao': 'Outro Produto',
            'codigo_interno': 'PRODDUPLICADO',
            'ncm': '87654321',
            'preco_venda': '20.00'
        }
        response = self.client.post(self.produto_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data) # IntegrityError se transforma em non_field_errors
