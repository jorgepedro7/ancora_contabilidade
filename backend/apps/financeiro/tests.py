from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from backend.apps.empresas.models import Empresa
from backend.apps.core.models import PerfilPermissao
from backend.apps.cadastros.models import Fornecedor, Cliente
from .models import ContaBancaria, PlanoContas, ContaAPagar, ContaAReceber, MovimentacaoFinanceira
from decimal import Decimal
from datetime import date

class FinanceiroAPITestCase(APITestCase):
    def setUp(self):
        self.User = get_user_model()
        self.user = self.User.objects.create_user(
            email='test@example.com',
            nome='Test User',
            password='password123'
        )

        self.empresa = Empresa.objects.create(
            razao_social='Empresa Financeiro',
            nome_fantasia='Financeiro Test',
            cnpj='00000000000400',
            regime_tributario='SN',
            cnae_principal='1234567',
            cep='00000000',
            logradouro='Rua Financeiro',
            numero='1',
            bairro='Centro',
            municipio='Cidade Financeiro',
            uf='SP'
        )
        PerfilPermissao.objects.create(usuario=self.user, empresa=self.empresa, perfil='ADMIN')
        self.user.empresa_ativa = self.empresa
        self.user.save()

        self.token = self._get_auth_token(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

        self.conta_bancaria = ContaBancaria.objects.create(
            empresa=self.empresa,
            descricao='Conta Principal',
            tipo_conta='CC',
            saldo_inicial=Decimal('1000.00'),
            saldo_atual=Decimal('1000.00')
        )
        self.plano_contas_receita = PlanoContas.objects.create(
            empresa=self.empresa,
            codigo='1.01.01',
            descricao='Vendas de Produtos',
            tipo_conta='RC'
        )
        self.plano_contas_despesa = PlanoContas.objects.create(
            empresa=self.empresa,
            codigo='2.01.01',
            descricao='Contas de Consumo',
            tipo_conta='DS'
        )
        self.fornecedor = Fornecedor.objects.create(
            empresa=self.empresa,
            nome_razao_social='Fornecedor Teste',
            tipo_pessoa='PJ',
            documento='00000000000191',
            cep='01001000', logradouro='Rua', numero='1', bairro='Bairro', municipio='Cidade', uf='SP'
        )
        self.cliente = Cliente.objects.create(
            empresa=self.empresa,
            nome_razao_social='Cliente Teste',
            tipo_pessoa='PF',
            documento='11122233344',
            cep='01001000', logradouro='Rua', numero='1', bairro='Bairro', municipio='Cidade', uf='SP'
        )
        self.conta_a_pagar = ContaAPagar.objects.create(
            empresa=self.empresa,
            descricao='Aluguel',
            valor_total=Decimal('500.00'),
            data_vencimento=date(2026, 3, 1),
            fornecedor=self.fornecedor,
            conta_contabil=self.plano_contas_despesa
        )
        self.conta_a_receber = ContaAReceber.objects.create(
            empresa=self.empresa,
            descricao='Venda Produto X',
            valor_total=Decimal('750.00'),
            data_vencimento=date(2026, 2, 25),
            cliente=self.cliente,
            conta_contabil=self.plano_contas_receita
        )

    def _get_auth_token(self, user):
        response = self.client.post(reverse('token_obtain_pair'), {
            'email': user.email,
            'password': 'password123'
        }, format='json')
        return response.data['access']

    def test_conta_bancaria_list(self):
        response = self.client.get(reverse('conta-bancaria-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_plano_contas_list(self):
        response = self.client.get(reverse('plano-contas-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)

    def test_conta_a_pagar_pagar_action(self):
        url = reverse('conta-pagar-pagar', kwargs={'pk': self.conta_a_pagar.id})
        response = self.client.post(url, {
            'valor': '300.00',
            'conta_bancaria_id': str(self.conta_bancaria.id)
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.conta_a_pagar.refresh_from_db()
        self.conta_bancaria.refresh_from_db()
        self.assertEqual(self.conta_a_pagar.valor_pago, Decimal('300.00'))
        self.assertEqual(self.conta_a_pagar.status, 'PARCIAL')
        self.assertEqual(self.conta_bancaria.saldo_atual, Decimal('700.00'))
        self.assertTrue(MovimentacaoFinanceira.objects.filter(
            empresa=self.empresa,
            conta_bancaria=self.conta_bancaria,
            valor=Decimal('300.00'),
            tipo_movimentacao='S'
        ).exists())

    def test_conta_a_receber_receber_action(self):
        url = reverse('conta-receber-receber', kwargs={'pk': self.conta_a_receber.id})
        response = self.client.post(url, {
            'valor': '750.00',
            'conta_bancaria_id': str(self.conta_bancaria.id)
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.conta_a_receber.refresh_from_db()
        self.conta_bancaria.refresh_from_db()
        self.assertEqual(self.conta_a_receber.valor_recebido, Decimal('750.00'))
        self.assertEqual(self.conta_a_receber.status, 'PAGA_RECEBIDA')
        self.assertEqual(self.conta_bancaria.saldo_atual, Decimal('1750.00'))
        self.assertTrue(MovimentacaoFinanceira.objects.filter(
            empresa=self.empresa,
            conta_bancaria=self.conta_bancaria,
            valor=Decimal('750.00'),
            tipo_movimentacao='E'
        ).exists())

    def test_fluxo_caixa_view(self):
        # Criar algumas movimentações para testar o fluxo de caixa
        MovimentacaoFinanceira.objects.create(
            empresa=self.empresa,
            conta_bancaria=self.conta_bancaria,
            tipo_movimentacao='E', valor=Decimal('200.00'), descricao='Entrada Teste',
            data_movimentacao=date(2026, 2, 20), conta_contabil=self.plano_contas_receita
        )
        MovimentacaoFinanceira.objects.create(
            empresa=self.empresa,
            conta_bancaria=self.conta_bancaria,
            tipo_movimentacao='S', valor=Decimal('100.00'), descricao='Saída Teste',
            data_movimentacao=date(2026, 2, 21), conta_contabil=self.plano_contas_despesa
        )
        
        url = reverse('fluxo-caixa') + '?data_inicio=2026-02-15&data_fim=2026-02-28'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_entradas'], Decimal('200.00'))
        self.assertEqual(response.data['total_saidas'], Decimal('100.00'))
        self.assertEqual(response.data['fluxo_caixa_liquido'], Decimal('100.00'))
    
    def test_contas_vencendo_hoje_view(self):
        # Ajustar data de vencimento para hoje
        ContaAPagar.objects.create(
            empresa=self.empresa,
            descricao='Conta Hoje',
            valor_total=Decimal('150.00'),
            data_vencimento=date.today(),
            fornecedor=self.fornecedor,
            conta_contabil=self.plano_contas_despesa
        )
        url = reverse('contas-vencendo-hoje')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['contas_a_pagar_hoje']), 1)
        self.assertEqual(response.data['contas_a_pagar_hoje'][0]['descricao'], 'Conta Hoje')
        self.assertEqual(len(response.data['contas_a_receber_hoje']), 0) # Nenhuma para hoje ainda
