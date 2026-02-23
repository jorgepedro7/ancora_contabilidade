from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from backend.apps.empresas.models import Empresa
from backend.apps.core.models import PerfilPermissao
from .models import Cargo, Departamento, Funcionario, ContratoTrabalho, FolhaPagamento, HoleriteFuncionario
from decimal import Decimal
from datetime import date

class FolhaAPITestCase(APITestCase):
    def setUp(self):
        self.User = get_user_model()
        self.user = self.User.objects.create_user(
            email='test@example.com',
            nome='Test User',
            password='password123'
        )

        self.empresa = Empresa.objects.create(
            razao_social='Empresa Folha',
            nome_fantasia='Folha Test',
            cnpj='00000000000600',
            regime_tributario='SN',
            cnae_principal='1234567',
            cep='00000000',
            logradouro='Rua Folha',
            numero='1',
            bairro='Centro',
            municipio='Cidade Folha',
            uf='SP'
        )
        PerfilPermissao.objects.create(usuario=self.user, empresa=self.empresa, perfil='ADMIN')
        self.user.empresa_ativa = self.empresa
        self.user.save()

        self.token = self._get_auth_token(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

        self.cargo = Cargo.objects.create(empresa=self.empresa, nome='Desenvolvedor', cbo='2120-10')
        self.departamento = Departamento.objects.create(empresa=self.empresa, nome='TI', centro_custo='1000')
        self.funcionario = Funcionario.objects.create(
            empresa=self.empresa,
            nome_completo='Funcionario Teste',
            cpf='11122233344',
            data_nascimento='1990-01-01',
            dependentes=1
        )
        self.contrato = ContratoTrabalho.objects.create(
            empresa=self.empresa,
            funcionario=self.funcionario,
            cargo=self.cargo,
            departamento=self.departamento,
            tipo_contrato='CLT',
            salario_base=Decimal('2000.00'),
            data_inicio='2023-01-01',
            ativo=True
        )
        self.folha_pagamento = FolhaPagamento.objects.create(
            empresa=self.empresa,
            competencia='2024-02-01',
            tipo_folha='MENSAL',
            status='ABERTA'
        )

    def _get_auth_token(self, user):
        response = self.client.post(reverse('token_obtain_pair'), {
            'email': user.email,
            'password': 'password123'
        }, format='json')
        return response.data['access']

    def test_cargo_list(self):
        response = self.client.get(reverse('cargo-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_funcionario_create(self):
        data = {
            'nome_completo': 'Novo Funcionario',
            'cpf': '55566677788',
            'data_nascimento': '1995-05-05',
        }
        response = self.client.post(reverse('funcionario-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Funcionario.objects.count(), 2)
        self.assertTrue(Funcionario.objects.filter(cpf='55566677788').exists())
    
    def test_folha_pagamento_calcular_action(self):
        url = reverse('folha-pagamento-calcular', kwargs={'pk': self.folha_pagamento.id})
        response = self.client.post(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.folha_pagamento.refresh_from_db()
        self.assertEqual(self.folha_pagamento.status, 'PROCESSADA')
        self.assertEqual(HoleriteFuncionario.objects.count(), 1)
        holerite = HoleriteFuncionario.objects.first()
        self.assertAlmostEqual(holerite.salario_bruto, Decimal('2000.00'))
        self.assertAlmostEqual(holerite.desconto_inss, Decimal('180.00')) # 9% de 2000
        self.assertAlmostEqual(holerite.desconto_irrf, Decimal('0.00')) # Para 2000 com 1 dependente
    
    def test_folha_pagamento_fechar_action(self):
        # Primeiro calcula a folha
        self.test_folha_pagamento_calcular_action()
        url = reverse('folha-pagamento-fechar', kwargs={'pk': self.folha_pagamento.id})
        response = self.client.post(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.folha_pagamento.refresh_from_db()
        self.assertEqual(self.folha_pagamento.status, 'FECHADA')
