from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from backend.apps.empresas.models import Empresa
from backend.apps.core.models import PerfilPermissao
from backend.apps.financeiro.models import PlanoContas
from .models import LancamentoContabil, PartidaLancamento
from decimal import Decimal
from datetime import date

class ContabilAPITestCase(APITestCase):
    def setUp(self):
        self.User = get_user_model()
        self.user = self.User.objects.create_user(
            email='test@example.com',
            nome='Test User',
            password='password123'
        )

        self.empresa = Empresa.objects.create(
            razao_social='Empresa Contábil',
            nome_fantasia='Contabil Test',
            cnpj='00000000000700',
            regime_tributario='SN',
            cnae_principal='1234567',
            cep='00000000',
            logradouro='Rua Contabil',
            numero='1',
            bairro='Centro',
            municipio='Cidade Contabil',
            uf='SP'
        )
        PerfilPermissao.objects.create(usuario=self.user, empresa=self.empresa, perfil='ADMIN')
        self.user.empresa_ativa = self.empresa
        self.user.save()

        self.token = self._get_auth_token(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

        self.plano_contas_receita = PlanoContas.objects.create(
            empresa=self.empresa, codigo='1.01.01', descricao='Receita de Vendas', tipo_conta='RC'
        )
        self.plano_contas_despesa = PlanoContas.objects.create(
            empresa=self.empresa, codigo='2.01.01', descricao='Despesas Gerais', tipo_conta='DS'
        )
        self.plano_contas_ativo = PlanoContas.objects.create(
            empresa=self.empresa, codigo='3.01.01', descricao='Caixa', tipo_conta='AT'
        )
        self.plano_contas_passivo = PlanoContas.objects.create(
            empresa=self.empresa, codigo='4.01.01', descricao='Fornecedores', tipo_conta='PA'
        )
        self.plano_contas_pl = PlanoContas.objects.create(
            empresa=self.empresa, codigo='5.01.01', descricao='Capital Social', tipo_conta='PL'
        )

    def _get_auth_token(self, user):
        response = self.client.post(reverse('token_obtain_pair'), {
            'email': user.email,
            'password': 'password123'
        }, format='json')
        return response.data['access']

    def test_lancamento_contabil_create(self):
        data = {
            'data_lancamento': '2024-01-15',
            'historico': 'Lançamento de teste',
            'tipo_lancamento': 'SIMPLES',
            'partidas': [
                {'conta_contabil': str(self.plano_contas_ativo.id), 'tipo_partida': 'D', 'valor': '1000.00'},
                {'conta_contabil': str(self.plano_contas_receita.id), 'tipo_partida': 'C', 'valor': '1000.00'},
            ]
        }
        response = self.client.post(reverse('lancamento-contabil-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(LancamentoContabil.objects.count(), 1)
        self.assertEqual(PartidaLancamento.objects.count(), 2)
    
    def test_lancamento_contabil_unbalanced_create_fails(self):
        data = {
            'data_lancamento': '2024-01-15',
            'historico': 'Lançamento desbalanceado',
            'tipo_lancamento': 'SIMPLES',
            'partidas': [
                {'conta_contabil': str(self.plano_contas_ativo.id), 'tipo_partida': 'D', 'valor': '1000.00'},
                {'conta_contabil': str(self.plano_contas_receita.id), 'tipo_partida': 'C', 'valor': '900.00'}, # Desbalanceado
            ]
        }
        response = self.client.post(reverse('lancamento-contabil-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('total de débitos deve ser igual ao total de créditos', response.data['error'])

    def test_dre_report(self):
        # Lançamentos para DRE (Receita e Despesa no período)
        lancamento1 = LancamentoContabil.objects.create(
            empresa=self.empresa, data_lancamento='2024-01-10', historico='Venda', tipo_lancamento='SIMPLES'
        )
        PartidaLancamento.objects.create(
            lancamento=lancamento1, empresa=self.empresa, conta_contabil=self.plano_contas_ativo, tipo_partida='D', valor='500.00'
        )
        PartidaLancamento.objects.create(
            lancamento=lancamento1, empresa=self.empresa, conta_contabil=self.plano_contas_receita, tipo_partida='C', valor='500.00'
        )
        lancamento2 = LancamentoContabil.objects.create(
            empresa=self.empresa, data_lancamento='2024-01-20', historico='Conta de Luz', tipo_lancamento='SIMPLES'
        )
        PartidaLancamento.objects.create(
            lancamento=lancamento2, empresa=self.empresa, conta_contabil=self.plano_contas_despesa, tipo_partida='D', valor='100.00'
        )
        PartidaLancamento.objects.create(
            lancamento=lancamento2, empresa=self.empresa, conta_contabil=self.plano_contas_ativo, tipo_partida='C', valor='100.00'
        )

        url = reverse('dre-report') + '?data_inicio=2024-01-01&data_fim=2024-01-31'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_receitas'], Decimal('500.00'))
        self.assertEqual(response.data['total_despesas'], Decimal('100.00'))
        self.assertEqual(response.data['resultado_liquido'], Decimal('400.00'))

    def test_balanco_patrimonial_report(self):
        # Lançamentos para Balanço (Ativo, Passivo, PL até a data base)
        lancamento1 = LancamentoContabil.objects.create(
            empresa=self.empresa, data_lancamento='2023-12-31', historico='Capital Inicial', tipo_lancamento='SIMPLES'
        )
        PartidaLancamento.objects.create(
            lancamento=lancamento1, empresa=self.empresa, conta_contabil=self.plano_contas_ativo, tipo_partida='D', valor='10000.00'
        )
        PartidaLancamento.objects.create(
            lancamento=lancamento1, empresa=self.empresa, conta_contabil=self.plano_contas_pl, tipo_partida='C', valor='10000.00'
        )
        lancamento2 = LancamentoContabil.objects.create(
            empresa=self.empresa, data_lancamento='2024-01-15', historico='Compra a Prazo', tipo_lancamento='SIMPLES'
        )
        PartidaLancamento.objects.create(
            lancamento=lancamento2, empresa=self.empresa, conta_contabil=self.plano_contas_despesa, tipo_partida='D', valor='2000.00'
        )
        PartidaLancamento.objects.create(
            lancamento=lancamento2, empresa=self.empresa, conta_contabil=self.plano_contas_passivo, tipo_partida='C', valor='2000.00'
        )

        url = reverse('balanco-patrimonial-report') + '?data_base=2024-01-31'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Os valores aqui refletem os lançamentos de débito/crédito nas contas de ativo/passivo/PL
        # e precisam ser calculados acumuladamente até a data_base
        self.assertGreater(response.data['total_ativo'], Decimal('0.00'))
        self.assertGreater(response.data['total_passivo'], Decimal('0.00'))
        self.assertGreater(response.data['total_patrimonio_liquido'], Decimal('0.00'))
        # Em um balanço real, a diferença entre Ativo e Passivo+PL deveria ser 0
        self.assertAlmostEqual(response.data['balanco_patrimonial_quadra'], Decimal('0.00'))
