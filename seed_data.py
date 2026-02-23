import os
import django
import uuid
from decimal import Decimal
from datetime import date, timedelta

# Configura o ambiente Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.config.settings')
django.setup()

from backend.apps.core.models import Usuario
from backend.apps.empresas.models import Empresa, ConfiguracaoFiscalEmpresa
from backend.apps.cadastros.models import Cliente, Fornecedor, Produto
from backend.apps.fiscal.models import NotaFiscal, ItemNotaFiscal
from backend.apps.financeiro.models import ContaBancaria, PlanoContas, ContaAPagar, ContaAReceber

def seed_data():
    print("Iniciando o seeding de dados...")

    # 1. Garantir que o usuário admin tenha uma empresa vinculada
    admin = Usuario.objects.filter(email='admin@ancora.com').first()
    if not admin:
        print("Usuário admin@ancora.com não encontrado. Crie-o primeiro.")
        return

    # 2. Criar Empresa de Teste
    empresa, created = Empresa.objects.get_or_create(
        cnpj='12345678000195',
        defaults={
            'razao_social': 'Âncora Contabilidade LTDA',
            'nome_fantasia': 'Âncora Contabilidade',
            'cnae_principal': '6920601',
            'regime_tributario': 'SN',
            'porte': 'ME',
            'cep': '01001000',
            'logradouro': 'Praça da Sé',
            'numero': '100',
            'bairro': 'Centro',
            'municipio': 'São Paulo',
            'uf': 'SP',
            'ativo': True
        }
    )
    if created:
        print(f"Empresa '{empresa.nome_fantasia}' criada.")
        # Criar Configuração Fiscal
        ConfiguracaoFiscalEmpresa.objects.get_or_create(
            empresa=empresa,
            defaults={
                'ambiente_sefaz': '2',
                'serie_nfe': '001',
                'proximo_numero_nfe': 1,
            }
        )
    else:
        print(f"Empresa '{empresa.nome_fantasia}' já existe.")

    # Vincular empresa ao admin
    admin.empresa_ativa = empresa
    admin.save()
    
    # Criar Perfil de Permissão para o Admin na Empresa
    from backend.apps.core.models import PerfilPermissao
    PerfilPermissao.objects.get_or_create(
        usuario=admin,
        empresa=empresa,
        defaults={
            'perfil': 'ADMIN',
            'pode_emitir_nf': True,
            'pode_cancelar_nf': True,
            'pode_ver_folha': True
        }
    )
    print(f"Perfil ADMIN criado para o usuário na empresa '{empresa.nome_fantasia}'.")
    print(f"Empresa '{empresa.nome_fantasia}' definida como ativa para o admin.")

    # 3. Criar Plano de Contas Básico
    receita_vendas, _ = PlanoContas.objects.get_or_create(
        empresa=empresa, codigo='1.01.01', 
        defaults={'descricao': 'Receita de Venda de Produtos', 'tipo_conta': 'RC'}
    )
    despesa_aluguel, _ = PlanoContas.objects.get_or_create(
        empresa=empresa, codigo='2.01.01', 
        defaults={'descricao': 'Despesa com Aluguel', 'tipo_conta': 'DS'}
    )
    print("Plano de Contas básico criado.")

    # 4. Criar Conta Bancária
    conta_bb, _ = ContaBancaria.objects.get_or_create(
        empresa=empresa, descricao='Banco do Brasil - Principal',
        defaults={'tipo_conta': 'CC', 'saldo_inicial': Decimal('5000.00'), 'saldo_atual': Decimal('5000.00')}
    )
    print("Conta bancária criada.")

    # 5. Criar Cliente e Fornecedor
    cliente, _ = Cliente.objects.get_or_create(
        empresa=empresa, documento='83742465000101',
        defaults={
            'nome_razao_social': 'Cliente Exemplo S.A.',
            'tipo_pessoa': 'PJ',
            'indicador_ie': '1',
            'logradouro': 'Rua das Flores',
            'numero': '50',
            'cep': '01234000',
            'municipio': 'São Paulo',
            'uf': 'SP'
        }
    )
    fornecedor, _ = Fornecedor.objects.get_or_create(
        empresa=empresa, documento='12345678000100',
        defaults={
            'nome_razao_social': 'Fornecedor de Energia LTDA',
            'tipo_pessoa': 'PJ',
            'indicador_ie': '1',
            'logradouro': 'Av. Central',
            'numero': '1000',
            'cep': '01000000',
            'municipio': 'São Paulo',
            'uf': 'SP'
        }
    )
    print("Cliente e Fornecedor criados.")

    # 6. Criar Produto
    produto, _ = Produto.objects.get_or_create(
        empresa=empresa, codigo_interno='PROD001',
        defaults={
            'descricao': 'Notebook Gamer Pro',
            'ncm': '84713012',
            'origem': '0',
            'preco_custo': Decimal('3500.00'),
            'preco_venda': Decimal('5000.00'),
            'estoque_atual': Decimal('10.000'),
            'cst_icms': '101'
        }
    )
    print("Produto criado.")

    # 7. Criar Contas a Pagar/Receber
    ContaAPagar.objects.get_or_create(
        empresa=empresa, descricao='Aluguel Mensal',
        defaults={
            'fornecedor': fornecedor,
            'conta_contabil': despesa_aluguel,
            'valor_total': Decimal('1200.00'),
            'data_vencimento': date.today() + timedelta(days=5),
            'status': 'ABERTA'
        }
    )
    ContaAReceber.objects.get_or_create(
        empresa=empresa, descricao='Venda Direta #001',
        defaults={
            'cliente': cliente,
            'conta_contabil': receita_vendas,
            'valor_total': Decimal('5000.00'),
            'data_vencimento': date.today() + timedelta(days=3),
            'status': 'ABERTA'
        }
    )
    print("Financeiro populado.")

    # 8. Criar Nota Fiscal de Exemplo
    nf, created = NotaFiscal.objects.get_or_create(
        empresa=empresa, numero=1, serie='001', tipo_nf='1',
        defaults={
            'modelo': '55',
            'finalidade': '1',
            'status': 'AUTORIZADA',
            'destinatario_nome': cliente.nome_razao_social,
            'destinatario_documento': cliente.documento,
            'destinatario_cep': cliente.cep,
            'destinatario_logradouro': cliente.logradouro,
            'destinatario_numero': cliente.numero,
            'destinatario_bairro': 'Vila Maria',
            'destinatario_municipio': cliente.municipio,
            'destinatario_uf': cliente.uf,
            'valor_total_nf': Decimal('5000.00')
        }
    )
    if created:
        ItemNotaFiscal.objects.create(
            nota_fiscal=nf,
            produto=produto,
            produto_descricao=produto.descricao,
            produto_ncm=produto.ncm,
            produto_cfop='5102',
            quantidade=Decimal('1.0000'),
            valor_unitario=Decimal('5000.00'),
            valor_total=Decimal('5000.00')
        )
    print("Notas Fiscais populadas.")

    print("\nSeeding concluído com sucesso!")
    print("Agora você pode entrar no sistema com admin@ancora.com / admin.")

if __name__ == '__main__':
    seed_data()
