import re
import requests
import json
import random
from datetime import date
from decimal import Decimal
from rest_framework.exceptions import ValidationError


def obter_empresas_acessiveis(usuario):
    from backend.apps.core.models import PerfilPermissao
    from backend.apps.empresas.models import Empresa

    if not usuario or not getattr(usuario, 'is_authenticated', False):
        return Empresa.objects.none()

    if getattr(usuario, 'is_superuser', False):
        return Empresa.objects.filter(ativo=True)

    empresas_ids = PerfilPermissao.objects.filter(
        usuario=usuario,
        ativo=True,
        empresa__ativo=True,
    ).values_list('empresa_id', flat=True)
    return Empresa.objects.filter(id__in=empresas_ids, ativo=True)


def obter_empresas_backoffice(usuario):
    from backend.apps.core.models import PerfilPermissao
    from backend.apps.empresas.models import Empresa

    if not usuario or not getattr(usuario, 'is_authenticated', False):
        return Empresa.objects.none()

    if getattr(usuario, 'is_superuser', False):
        return Empresa.objects.filter(ativo=True)

    empresas_ids = PerfilPermissao.objects.filter(
        usuario=usuario,
        ativo=True,
        empresa__ativo=True,
    ).exclude(
        perfil='CLIENTE',
    ).values_list('empresa_id', flat=True)
    return Empresa.objects.filter(id__in=empresas_ids, ativo=True)


def usuario_tem_acesso_empresa(usuario, empresa):
    if not usuario or not getattr(usuario, 'is_authenticated', False) or not empresa:
        return False

    if getattr(usuario, 'is_superuser', False):
        return empresa.ativo

    from backend.apps.core.models import PerfilPermissao

    return PerfilPermissao.objects.filter(
        usuario=usuario,
        empresa=empresa,
        ativo=True,
        empresa__ativo=True,
    ).exists()


def obter_perfil_empresa(usuario, empresa=None):
    if not usuario or not getattr(usuario, 'is_authenticated', False):
        return None

    empresa = empresa or getattr(usuario, 'empresa_ativa', None)
    if not empresa:
        return None

    from backend.apps.core.models import PerfilPermissao

    try:
        return PerfilPermissao.objects.get(
            usuario=usuario,
            empresa=empresa,
            ativo=True,
            empresa__ativo=True,
        )
    except PerfilPermissao.DoesNotExist:
        return None


def usuario_tem_perfil_backoffice(usuario, empresa=None):
    if not usuario or not getattr(usuario, 'is_authenticated', False):
        return False

    if getattr(usuario, 'is_superuser', False):
        return True

    perfil = obter_perfil_empresa(usuario, empresa) if empresa else None
    if perfil is not None:
        return perfil.perfil != 'CLIENTE'

    from backend.apps.core.models import PerfilPermissao

    return PerfilPermissao.objects.filter(
        usuario=usuario,
        ativo=True,
        empresa__ativo=True,
    ).exclude(
        perfil='CLIENTE',
    ).exists()


def calcular_score_empresa(empresa):
    from backend.apps.cadastros.models import Cliente, Fornecedor, Produto
    from backend.apps.fiscal.models import NotaFiscal
    from backend.apps.financeiro.models import ContaAPagar, ContaAReceber, ContaBancaria
    from backend.apps.folha.models import Funcionario

    return sum([
        Cliente.objects.filter(empresa=empresa, ativo=True).count(),
        Fornecedor.objects.filter(empresa=empresa, ativo=True).count(),
        Produto.objects.filter(empresa=empresa, ativo=True).count(),
        NotaFiscal.objects.filter(empresa=empresa, ativo=True).count(),
        ContaAPagar.objects.filter(empresa=empresa, ativo=True).count(),
        ContaAReceber.objects.filter(empresa=empresa, ativo=True).count(),
        ContaBancaria.objects.filter(empresa=empresa, ativo=True).count(),
        Funcionario.objects.filter(empresa=empresa, ativo=True).count(),
    ])


def obter_empresa_principal(usuario=None):
    if usuario is None:
        from backend.apps.empresas.models import Empresa
        empresas = list(Empresa.objects.filter(ativo=True))
    else:
        empresas = list(obter_empresas_acessiveis(usuario))
        empresas_backoffice_ids = set(
            obter_empresas_backoffice(usuario).values_list('id', flat=True),
        )
        if empresas_backoffice_ids:
            empresas = [empresa for empresa in empresas if empresa.id in empresas_backoffice_ids]
    if not empresas:
        return None

    empresas.sort(
        key=lambda empresa: (-calcular_score_empresa(empresa), empresa.criado_em),
    )
    return empresas[0]


def garantir_empresa_padrao(usuario, persist=True):
    if not usuario or not getattr(usuario, 'is_authenticated', False):
        return None

    empresa_atual = getattr(usuario, 'empresa_ativa', None)
    if empresa_atual and empresa_atual.ativo and usuario_tem_acesso_empresa(usuario, empresa_atual):
        return empresa_atual

    empresa_principal = obter_empresa_principal(usuario)
    if not empresa_principal:
        return None

    if persist and getattr(usuario, 'pk', None) and usuario.empresa_ativa_id != empresa_principal.id:
        usuario.__class__.objects.filter(pk=usuario.pk).update(empresa_ativa=empresa_principal)

    usuario.empresa_ativa = empresa_principal
    return empresa_principal


def obter_empresa_ativa_ou_erro(user):
    empresa = garantir_empresa_padrao(user)
    if not empresa:
        raise ValidationError({'empresa': 'Selecione uma empresa antes de continuar.'})
    return empresa

def validar_cpf(cpf):
    cpf = re.sub(r'[^0-9]', '', cpf)
    if len(cpf) != 11 or len(set(cpf)) == 1:
        return False
    # Valida 1o digito
    soma = 0
    for i in range(9):
        soma += int(cpf[i]) * (10 - i)
    resto = 11 - (soma % 11)
    digito1 = 0 if resto > 9 else resto
    if digito1 != int(cpf[9]):
        return False
    # Valida 2o digito
    soma = 0
    for i in range(10):
        soma += int(cpf[i]) * (11 - i)
    resto = 11 - (soma % 11)
    digito2 = 0 if resto > 9 else resto
    if digito2 != int(cpf[10]):
        return False
    return True

def validar_cnpj(cnpj):
    cnpj = re.sub(r'[^0-9]', '', cnpj)
    if len(cnpj) != 14 or len(set(cnpj)) == 1:
        return False
    
    def calculate_special_digit(numbers, factors):
        soma = 0
        for i in range(len(numbers)):
            soma += int(numbers[i]) * factors[i]
        resto = soma % 11
        return 0 if resto < 2 else 11 - resto

    # Valida 1o digito
    fatores1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    digito1 = calculate_special_digit(cnpj[:12], fatores1)
    if digito1 != int(cnpj[12]):
        return False

    # Valida 2o digito
    fatores2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    digito2 = calculate_special_digit(cnpj[:13], fatores2)
    if digito2 != int(cnpj[13]):
        return False
    
    return True

def formatar_cpf(cpf):
    cpf = re.sub(r'[^0-9]', '', cpf)
    if len(cpf) == 11:
        return f'{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}'
    return cpf

def formatar_cnpj(cnpj):
    cnpj = re.sub(r'[^0-9]', '', cnpj)
    if len(cnpj) == 14:
        return f'{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}'
    return cnpj

def buscar_cep(cep):
    cep = re.sub(r'[^0-9]', '', cep)
    if len(cep) != 8:
        return None
    url = f'https://viacep.com.br/ws/{cep}/json/'
    try:
        response = requests.get(url)
        response.raise_for_status() # Raises HTTPError for bad responses (4xx or 5xx)
        data = response.json()
        if 'erro' not in data:
            return {
                'cep': data.get('cep'),
                'logradouro': data.get('logradouro'),
                'complemento': data.get('complemento'),
                'bairro': data.get('bairro'),
                'localidade': data.get('localidade'),
                'uf': data.get('uf'),
                'ibge': data.get('ibge'),
            }
        return None
    except requests.exceptions.RequestException as e:
        print(f"Erro ao buscar CEP: {e}")
        return None

def calcular_inss(salario_bruto):
    # Ensure it's Decimal
    if not isinstance(salario_bruto, Decimal):
        salario_bruto = Decimal(str(salario_bruto))

    # Tabela INSS 2024 (simplificada)
    if salario_bruto <= Decimal('1412.00'):
        aliquota = Decimal('0.075')
        deducao = Decimal('0')
    elif salario_bruto <= Decimal('2666.68'):
        aliquota = Decimal('0.09')
        deducao = Decimal('21.18')
    elif salario_bruto <= Decimal('4000.03'):
        aliquota = Decimal('0.12')
        deducao = Decimal('101.18')
    elif salario_bruto <= Decimal('7786.02'): # Teto
        aliquota = Decimal('0.14')
        deducao = Decimal('181.18')
    else:
        return Decimal('908.85') # Teto de contribuição

    inss = (salario_bruto * aliquota) - deducao
    return round(inss, 2)

def calcular_irrf(base_calculo, numero_dependentes=0):
    if not isinstance(base_calculo, Decimal):
        base_calculo = Decimal(str(base_calculo))

    deducao_dependente = Decimal('189.59') * Decimal(str(numero_dependentes))
    base_com_deducao = base_calculo - deducao_dependente

    if base_com_deducao <= Decimal('2259.20'):
        aliquota = Decimal('0')
        parcela_deduzir = Decimal('0')
    elif base_com_deducao <= Decimal('2826.65'):
        aliquota = Decimal('0.075')
        parcela_deduzir = Decimal('169.44')
    elif base_com_deducao <= Decimal('3751.05'):
        aliquota = Decimal('0.15')
        parcela_deduzir = Decimal('381.44')
    elif base_com_deducao <= Decimal('4664.68'):
        aliquota = Decimal('0.225')
        parcela_deduzir = Decimal('662.77')
    else:
        aliquota = Decimal('0.275')
        parcela_deduzir = Decimal('896.00')
    
    irrf = (base_com_deducao * aliquota) - parcela_deduzir
    return round(irrf, 2) if irrf > 0 else Decimal('0.00')

def calcular_fgts(salario_bruto):
    if not isinstance(salario_bruto, Decimal):
        salario_bruto = Decimal(str(salario_bruto))
    fgts = salario_bruto * Decimal('0.08')
    return round(fgts, 2)

def gerar_chave_acesso_nfe(cUF, AAMM, CNPJ, mod, serie, nNF, tpEmis, cNF, cDV=None):
    """
    Gera a Chave de Acesso da NF-e com 44 dígitos.
    Args:
        cUF (str): Código da UF do emitente (2 dígitos).
        AAMM (str): Ano e Mês de emissão da NF-e (4 dígitos).
        CNPJ (str): CNPJ do emitente (14 dígitos).
        mod (str): Modelo do documento fiscal (2 dígitos, ex: '55' para NF-e).
        serie (str): Série do documento fiscal (3 dígitos, ex: '001').
        nNF (str): Número do Documento Fiscal (9 dígitos).
        tpEmis (str): Forma de emissão da NF-e (1 dígito, ex: '1' para normal).
        cNF (str): Código Numérico que compõe a Chave de Acesso (8 dígitos).
        cDV (str, optional): Dígito Verificador da Chave de Acesso. Se não informado, será calculado.
    Returns:
        str: Chave de Acesso da NF-e com 44 dígitos.
    """
    
    # Remove caracteres não numéricos
    CNPJ = re.sub(r'\D', '', CNPJ)
    serie = re.sub(r'\D', '', serie)
    nNF = re.sub(r'\D', '', nNF)
    cNF = re.sub(r'\D', '', cNF)

    # Preenchimento com zeros à esquerda
    serie = serie.zfill(3)
    nNF = nNF.zfill(9)
    cNF = cNF.zfill(8)

    chave_sem_dv = f"{cUF}{AAMM}{CNPJ}{mod}{serie}{nNF}{tpEmis}{cNF}"

    if len(chave_sem_dv) != 43:
        raise ValueError(f"A chave sem DV deve ter 43 dígitos, mas tem {len(chave_sem_dv)}. Dados: {chave_sem_dv}")

    if cDV is None:
        cDV = str(_calcular_dv_nfe(chave_sem_dv))
    
    return chave_sem_dv + cDV

def _calcular_dv_nfe(chave_43_digitos):
    """
    Calcula o Dígito Verificador da Chave de Acesso da NF-e.
    Utiliza o algoritmo de Luhn (módulo 11 com pesos de 2 a 9).
    """
    soma = 0
    peso = 2
    for digito in reversed(chave_43_digitos):
        soma += int(digito) * peso
        peso += 1
        if peso > 9:
            peso = 2
    dv = 11 - (soma % 11)
    if dv == 10 or dv == 11:
        return 0
    return dv
