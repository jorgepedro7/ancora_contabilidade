from django.core.management.base import BaseCommand
from backend.apps.empresas.models import Empresa
from backend.apps.folha.models import Cargo, Departamento, Funcionario, ContratoTrabalho, FolhaPagamento, HoleriteFuncionario, RegistroPonto, JustificativaPonto
from datetime import date, time, timedelta
from decimal import Decimal
import random

class Command(BaseCommand):
    help = 'Seeds the database with a dummy employee and payroll data'

    def handle(self, *args, **options):
        self.stdout.write("Iniciando o seeding do módulo de Folha de Pagamento...")

        # 1. Garantir que temos uma Empresa
        empresa, created = Empresa.objects.get_or_create(
            cnpj='12345678000199',
            defaults={
                'razao_social': 'Âncora Tecnologia e Contabilidade LTDA',
                'nome_fantasia': 'Âncora Contabilidade',
                'regime_tributario': 'SN',
                'porte': 'EPP',
                'cep': '01001000',
                'logradouro': 'Praça da Sé',
                'numero': '100',
                'bairro': 'Centro',
                'municipio': 'São Paulo',
                'uf': 'SP',
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"Empresa '{empresa.nome_fantasia}' criada."))

        # 2. Criar Cargo e Departamento
        cargo, _ = Cargo.objects.get_or_create(
            empresa=empresa,
            nome='Analista Contábil Pleno',
            defaults={'cbo': '252210'}
        )
        
        depto, _ = Departamento.objects.get_or_create(
            empresa=empresa,
            nome='Departamento Pessoal',
            defaults={'centro_custo': '1.02.01'}
        )

        # 3. Criar Funcionário Fictício
        funcionario, created = Funcionario.objects.get_or_create(
            empresa=empresa,
            cpf='12345678901',
            defaults={
                'nome_completo': 'João da Silva Santos',
                'data_nascimento': date(1990, 5, 20),
                'estado_civil': 'CASADO',
                'sexo': 'M',
                'email': 'joao.silva@ancora.com.br',
                'telefone_celular': '11988887777',
                'cep': '01234567',
                'logradouro': 'Rua dos Exemplos',
                'numero': '123',
                'bairro': 'Bairro Modelo',
                'municipio': 'São Paulo',
                'uf': 'SP',
                'pis': '12345678901',
                'banco': 'Itaú Unibanco',
                'agencia': '0001',
                'conta': '12345-6',
                'tipo_conta': 'CC',
                'dependentes': 1
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"Funcionário '{funcionario.nome_completo}' criado."))

        # 4. Criar Contrato de Trabalho
        contrato, created = ContratoTrabalho.objects.get_or_create(
            funcionario=funcionario,
            empresa=empresa,
            data_inicio=date(2023, 1, 1),
            defaults={
                'cargo': cargo,
                'departamento': depto,
                'tipo_contrato': 'CLT',
                'salario_base': Decimal('4500.00'),
                'categoria_esocial': '101'
            }
        )

        # 5. Criar Folha de Pagamento para a competência atual (ou anterior)
        # Vamos usar Fevereiro de 2026 como base
        competencia = date(2026, 2, 1)
        folha, created = FolhaPagamento.objects.get_or_create(
            empresa=empresa,
            competencia=competencia,
            tipo_folha='MENSAL',
            defaults={
                'status': 'ABERTA',
                'observacoes': 'Folha de teste gerada automaticamente.'
            }
        )

        # 6. Gerar Pontos para o mês
        self.stdout.write("Gerando registros de ponto...")
        for dia in range(1, 29): # Fevereiro 2026 tem 28 dias
            data_ponto = date(2026, 2, dia)
            # Pular finais de semana para simplificar, ou marcar como DSR? 
            # Na CLT, DSR é repouso remunerado. O ponto costuma registrar apenas dias trabalhados.
            if data_ponto.weekday() >= 5: # Sábado ou Domingo
                continue
            
            # Simular algumas horas extras no dia 10
            he = Decimal('0.00')
            if dia == 10:
                he = Decimal('2.00')
            
            # Simular um atraso no dia 15
            atraso = Decimal('0.00')
            if dia == 15:
                atraso = Decimal('0.50')

            RegistroPonto.objects.get_or_create(
                funcionario=funcionario,
                empresa=empresa,
                data=data_ponto,
                defaults={
                    'entrada_1': time(8, 0),
                    'saida_1': time(12, 0),
                    'entrada_2': time(13, 0),
                    'saida_2': time(17, 0) if dia != 10 else time(19, 0),
                    'total_horas': Decimal('8.00'),
                    'horas_extras': he,
                    'atrasos': atraso,
                    'manual': False
                }
            )

        # 7. Criar um Atestado Médico (Justificativa) para os dias 20 e 21
        JustificativaPonto.objects.get_or_create(
            funcionario=funcionario,
            empresa=empresa,
            data_inicio=date(2026, 2, 20),
            data_fim=date(2026, 2, 21),
            defaults={
                'tipo': 'ATESTADO_MEDICO',
                'descricao': 'Gripe forte, repouso de 2 dias.',
                'abona_ponto': True
            }
        )

        # 8. Calcular Holerite
        self.stdout.write("Calculando holerite...")
        holerite, _ = HoleriteFuncionario.objects.get_or_create(
            funcionario=funcionario,
            folha_pagamento=folha,
            empresa=empresa
        )
        try:
            holerite.calcular()
            self.stdout.write(self.style.SUCCESS(f"Holerite de {funcionario.nome_completo} calculado com sucesso!"))
            self.stdout.write(f"Líquido: R$ {holerite.liquido_receber}")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Erro ao calcular holerite: {e}"))

        self.stdout.write(self.style.SUCCESS("Seeding concluído com sucesso!"))
