from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from backend.apps.empresas.models import Empresa
from backend.apps.core.models import PerfilPermissao
from .models import ObrigacaoFiscal
from datetime import date, timedelta

class ObrigacoesAPITestCase(APITestCase):
    def setUp(self):
        self.User = get_user_model()
        self.user = self.User.objects.create_user(
            email='test@example.com',
            nome='Test User',
            password='password123'
        )

        self.empresa = Empresa.objects.create(
            razao_social='Empresa Obrigacoes',
            nome_fantasia='Obrigacoes Test',
            cnpj='00000000000800',
            regime_tributario='SN',
            cnae_principal='1234567',
            cep='00000000',
            logradouro='Rua Obrigacoes',
            numero='1',
            bairro='Centro',
            municipio='Cidade Obrigacoes',
            uf='SP'
        )
        PerfilPermissao.objects.create(usuario=self.user, empresa=self.empresa, perfil='ADMIN')
        self.user.empresa_ativa = self.empresa
        self.user.save()

        self.token = self._get_auth_token(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

        self.obrigacao_hoje = ObrigacaoFiscal.objects.create(
            empresa=self.empresa,
            tipo_obrigacao='DARF',
            data_vencimento=date.today(),
            status='ABERTO'
        )
        self.obrigacao_futura = ObrigacaoFiscal.objects.create(
            empresa=self.empresa,
            tipo_obrigacao='GIA',
            data_vencimento=date.today() + timedelta(days=5),
            status='ABERTO'
        )
        self.obrigacao_atrasada = ObrigacaoFiscal.objects.create(
            empresa=self.empresa,
            tipo_obrigacao='DCTF',
            data_vencimento=date.today() - timedelta(days=10),
            status='ABERTO'
        )
        self.obrigacao_paga = ObrigacaoFiscal.objects.create(
            empresa=self.empresa,
            tipo_obrigacao='DAS_MEI',
            data_vencimento=date.today() - timedelta(days=1),
            status='PAGO'
        )

    def _get_auth_token(self, user):
        response = self.client.post(reverse('token_obtain_pair'), {
            'email': user.email,
            'password': 'password123'
        }, format='json')
        return response.data['access']

    def test_obrigacao_fiscal_list(self):
        response = self.client.get(reverse('obrigacao-fiscal-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 4) # Todas as obrigações da empresa

    def test_obrigacao_fiscal_create(self):
        data = {
            'tipo_obrigacao': 'EFD',
            'data_vencimento': '2024-03-31',
            'descricao': 'EFD ICMS/IPI Março',
            'valor': '100.00'
        }
        response = self.client.post(reverse('obrigacao-fiscal-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ObrigacaoFiscal.objects.count(), 5)
        self.assertTrue(ObrigacaoFiscal.objects.filter(tipo_obrigacao='EFD').exists())
    
    def test_obrigacao_fiscal_vencendo_hoje(self):
        url = reverse('obrigacao-fiscal-vencendo-hoje')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['tipo_obrigacao'], 'DARF')
    
    def test_obrigacao_fiscal_vencendo_proximos_dias(self):
        url = reverse('obrigacao-fiscal-vencendo-proximos-dias') + '?dias=10'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2) # DARF de hoje e GIA futura
        self.assertIn('DARF', [o['tipo_obrigacao'] for o in response.data])
        self.assertIn('GIA', [o['tipo_obrigacao'] for o in response.data])
