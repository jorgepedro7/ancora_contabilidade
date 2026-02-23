from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from backend.apps.empresas.models import Empresa
from backend.apps.core.models import PerfilPermissao
from backend.apps.cadastros.models import Produto
from .models import LocalEstoque, MovimentacaoEstoque, LoteEstoque, InventarioEstoque
from decimal import Decimal
from datetime import date

class EstoqueAPITestCase(APITestCase):
    def setUp(self):
        self.User = get_user_model()
        self.user = self.User.objects.create_user(
            email='test@example.com',
            nome='Test User',
            password='password123'
        )

        self.empresa = Empresa.objects.create(
            razao_social='Empresa Estoque',
            nome_fantasia='Estoque Test',
            cnpj='00000000000500',
            regime_tributario='SN',
            cnae_principal='1234567',
            cep='00000000',
            logradouro='Rua Estoque',
            numero='1',
            bairro='Centro',
            municipio='Cidade Estoque',
            uf='SP'
        )
        PerfilPermissao.objects.create(usuario=self.user, empresa=self.empresa, perfil='ADMIN')
        self.user.empresa_ativa = self.empresa
        self.user.save()

        self.token = self._get_auth_token(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

        self.produto = Produto.objects.create(
            empresa=self.empresa,
            descricao='Produto A',
            codigo_interno='PROD001',
            ncm='12345678',
            preco_venda=Decimal('10.00'),
            preco_custo=Decimal('5.00'),
            estoque_atual=Decimal('100.000'),
            controla_estoque=True
        )
        self.local_estoque = LocalEstoque.objects.create(
            empresa=self.empresa,
            nome='Armazém Central',
            tipo_local='ARM'
        )

    def _get_auth_token(self, user):
        response = self.client.post(reverse('token_obtain_pair'), {
            'email': user.email,
            'password': 'password123'
        }, format='json')
        return response.data['access']

    def test_entrada_estoque(self):
        url = reverse('movimentacao-estoque-entrada')
        data = {
            'produto': str(self.produto.id),
            'quantidade': '50.000',
            'local_destino': str(self.local_estoque.id),
            'observacoes': 'Entrada via compra'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.produto.refresh_from_db()
        self.assertEqual(self.produto.estoque_atual, Decimal('150.000'))
        self.assertEqual(MovimentacaoEstoque.objects.count(), 1)
        self.assertEqual(MovimentacaoEstoque.objects.first().tipo_movimentacao, 'ENTRADA')

    def test_saida_estoque(self):
        url = reverse('movimentacao-estoque-saida')
        data = {
            'produto': str(self.produto.id),
            'quantidade': '30.000',
            'local_origem': str(self.local_estoque.id),
            'observacoes': 'Saída via venda'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.produto.refresh_from_db()
        self.assertEqual(self.produto.estoque_atual, Decimal('70.000'))
        self.assertEqual(MovimentacaoEstoque.objects.count(), 1)
        self.assertEqual(MovimentacaoEstoque.objects.first().tipo_movimentacao, 'SAIDA')

    def test_saida_estoque_insuficiente(self):
        url = reverse('movimentacao-estoque-saida')
        data = {
            'produto': str(self.produto.id),
            'quantidade': '150.000', # Mais do que o estoque atual
            'local_origem': str(self.local_estoque.id),
            'observacoes': 'Tentativa de saída excessiva'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Estoque insuficiente', response.data['error'])
        self.produto.refresh_from_db()
        self.assertEqual(self.produto.estoque_atual, Decimal('100.000')) # Estoque não deve mudar

    def test_posicao_estoque_list(self):
        Produto.objects.create(
            empresa=self.empresa,
            descricao='Produto B', codigo_interno='PROD002', ncm='87654321',
            preco_venda=Decimal('20.00'), estoque_atual=Decimal('50.000')
        )
        url = reverse('posicao-estoque')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2) # Dois produtos cadastrados
        self.assertIn('Produto A', [p['descricao'] for p in response.data['results']])
    
    def test_lote_estoque_create(self):
        url = reverse('lote-estoque-list')
        data = {
            'produto': str(self.produto.id),
            'local_estoque': str(self.local_estoque.id),
            'codigo_lote': 'LOTE001',
            'data_validade': '2027-12-31',
            'quantidade': '25.000'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(LoteEstoque.objects.count(), 1)
