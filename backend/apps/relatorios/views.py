from datetime import date, timedelta
from decimal import Decimal

from django.db.models import Sum, Count, F, ExpressionWrapper, DecimalField
from rest_framework.response import Response
from rest_framework.views import APIView

from backend.apps.core.permissions import IsBackofficeCompany
from backend.apps.core.utils import garantir_empresa_padrao


def _empresa(request):
    return garantir_empresa_padrao(request.user)


class DashboardView(APIView):
    """
    KPIs consolidados da empresa-cliente ativa.
    """
    permission_classes = [IsBackofficeCompany]

    def get(self, request):
        from backend.apps.fiscal.models import NotaFiscal
        from backend.apps.financeiro.models import ContaAPagar, ContaAReceber, ContaBancaria

        empresa = _empresa(request)
        hoje = date.today()
        inicio_mes = hoje.replace(day=1)
        proximo_mes = (inicio_mes.replace(day=28) + timedelta(days=4)).replace(day=1)
        daqui_5_dias = hoje + timedelta(days=5)

        nfe_mes = NotaFiscal.objects.filter(
            empresa=empresa,
            status='AUTORIZADA',
            data_emissao__date__gte=inicio_mes,
            data_emissao__date__lt=proximo_mes,
        ).count()

        # valor_saldo é property (valor_total - valor_pago), calculamos via expressão
        pagar_qs = ContaAPagar.objects.filter(
            empresa=empresa,
            ativo=True,
            status__in=['ABERTA', 'PARCIAL'],
            data_vencimento__lte=daqui_5_dias,
        ).aggregate(
            total=Sum('valor_total'),
            pago=Sum('valor_pago'),
        )
        contas_pagar_vencendo = (pagar_qs['total'] or Decimal('0')) - (pagar_qs['pago'] or Decimal('0'))

        contas_pagar_vencidas = ContaAPagar.objects.filter(
            empresa=empresa,
            ativo=True,
            status__in=['ABERTA', 'PARCIAL'],
            data_vencimento__lt=hoje,
        ).count()

        receber_qs = ContaAReceber.objects.filter(
            empresa=empresa,
            ativo=True,
            status__in=['ABERTA', 'PARCIAL'],
            data_vencimento__lte=daqui_5_dias,
        ).aggregate(
            total=Sum('valor_total'),
            recebido=Sum('valor_recebido'),
        )
        contas_receber_vencendo = (receber_qs['total'] or Decimal('0')) - (receber_qs['recebido'] or Decimal('0'))

        contas_receber_vencidas = ContaAReceber.objects.filter(
            empresa=empresa,
            ativo=True,
            status__in=['ABERTA', 'PARCIAL'],
            data_vencimento__lt=hoje,
        ).count()

        saldo_total = ContaBancaria.objects.filter(
            empresa=empresa,
            ativo=True,
        ).aggregate(total=Sum('saldo_atual'))['total'] or Decimal('0')

        return Response({
            'nfe_emitidas_mes': nfe_mes,
            'contas_pagar_vencendo_5d': str(contas_pagar_vencendo),
            'contas_pagar_vencidas_qtd': contas_pagar_vencidas,
            'contas_receber_vencendo_5d': str(contas_receber_vencendo),
            'contas_receber_vencidas_qtd': contas_receber_vencidas,
            'saldo_total_contas': str(saldo_total),
        })


class DREView(APIView):
    """
    Demonstração do Resultado do Exercício por período.
    Parâmetros: data_inicio (YYYY-MM-DD), data_fim (YYYY-MM-DD)
    """
    permission_classes = [IsBackofficeCompany]

    def get(self, request):
        from backend.apps.financeiro.models import MovimentacaoFinanceira

        empresa = _empresa(request)
        hoje = date.today()
        data_inicio = request.query_params.get('data_inicio', hoje.replace(day=1).isoformat())
        data_fim = request.query_params.get('data_fim', hoje.isoformat())

        movimentacoes = MovimentacaoFinanceira.objects.filter(
            empresa=empresa,
            ativo=True,
            data_movimentacao__gte=data_inicio,
            data_movimentacao__lte=data_fim,
        )

        receitas = movimentacoes.filter(
            tipo_movimentacao='E'
        ).aggregate(total=Sum('valor'))['total'] or Decimal('0')

        despesas = movimentacoes.filter(
            tipo_movimentacao='S'
        ).aggregate(total=Sum('valor'))['total'] or Decimal('0')

        resultado = receitas - despesas

        receitas_por_conta = list(
            movimentacoes.filter(tipo_movimentacao='E')
            .values('conta_contabil__descricao')
            .annotate(total=Sum('valor'))
            .order_by('-total')[:10]
        )
        despesas_por_conta = list(
            movimentacoes.filter(tipo_movimentacao='S')
            .values('conta_contabil__descricao')
            .annotate(total=Sum('valor'))
            .order_by('-total')[:10]
        )

        return Response({
            'periodo': {'data_inicio': data_inicio, 'data_fim': data_fim},
            'receita_bruta': str(receitas),
            'total_despesas': str(despesas),
            'resultado_liquido': str(resultado),
            'receitas_por_conta': [
                {'conta': r['conta_contabil__descricao'] or 'Sem conta', 'total': str(r['total'])}
                for r in receitas_por_conta
            ],
            'despesas_por_conta': [
                {'conta': r['conta_contabil__descricao'] or 'Sem conta', 'total': str(r['total'])}
                for r in despesas_por_conta
            ],
        })


class LivroFiscalView(APIView):
    """
    Livro de entradas e saídas de NF-e no período.
    Parâmetros: data_inicio (YYYY-MM-DD), data_fim (YYYY-MM-DD), tipo_nf ('1'=NF-e, '2'=NFC-e)
    """
    permission_classes = [IsBackofficeCompany]

    def get(self, request):
        from backend.apps.fiscal.models import NotaFiscal

        empresa = _empresa(request)
        hoje = date.today()
        data_inicio = request.query_params.get('data_inicio', hoje.replace(day=1).isoformat())
        data_fim = request.query_params.get('data_fim', hoje.isoformat())

        notas = NotaFiscal.objects.filter(
            empresa=empresa,
            ativo=True,
            status='AUTORIZADA',
            data_emissao__date__gte=data_inicio,
            data_emissao__date__lte=data_fim,
        ).order_by('data_emissao')

        if tipo_nf := request.query_params.get('tipo_nf'):
            notas = notas.filter(tipo_nf=tipo_nf)

        totais = notas.aggregate(
            qtd=Count('id'),
            total_produtos=Sum('valor_produtos'),
            total_icms=Sum('valor_icms'),
            total_ipi=Sum('valor_ipi'),
            total_nf=Sum('valor_total_nf'),
        )

        registros = list(notas.values(
            'numero', 'serie', 'tipo_nf', 'data_emissao',
            'destinatario_nome', 'destinatario_documento',
            'valor_produtos', 'valor_icms', 'valor_ipi', 'valor_total_nf',
            'status',
        ))

        return Response({
            'periodo': {'data_inicio': data_inicio, 'data_fim': data_fim},
            'totais': {
                'quantidade': totais['qtd'] or 0,
                'total_produtos': str(totais['total_produtos'] or 0),
                'total_icms': str(totais['total_icms'] or 0),
                'total_ipi': str(totais['total_ipi'] or 0),
                'total_nf': str(totais['total_nf'] or 0),
            },
            'registros': [
                {
                    **{k: v for k, v in r.items() if k != 'data_emissao'},
                    'data_emissao': r['data_emissao'].isoformat() if r['data_emissao'] else None,
                    'valor_produtos': str(r['valor_produtos'] or 0),
                    'valor_icms': str(r['valor_icms'] or 0),
                    'valor_ipi': str(r['valor_ipi'] or 0),
                    'valor_total_nf': str(r['valor_total_nf'] or 0),
                }
                for r in registros
            ],
        })


class PosicaoEstoqueView(APIView):
    """
    Posição atual de estoque por produto da empresa ativa.
    """
    permission_classes = [IsBackofficeCompany]

    def get(self, request):
        from backend.apps.cadastros.models import Produto

        empresa = _empresa(request)

        produtos = list(Produto.objects.filter(
            empresa=empresa,
            ativo=True,
            controla_estoque=True,
        ).order_by('descricao').values(
            'id', 'codigo_interno', 'descricao', 'ncm',
            'estoque_atual', 'estoque_minimo', 'estoque_maximo',
            'preco_custo', 'preco_venda',
        ))

        abaixo_minimo = sum(
            1 for p in produtos
            if (p['estoque_atual'] or 0) < (p['estoque_minimo'] or 0)
        )

        return Response({
            'total_produtos': len(produtos),
            'produtos_abaixo_minimo': abaixo_minimo,
            'produtos': [
                {
                    **{k: v for k, v in p.items() if k not in (
                        'estoque_atual', 'estoque_minimo', 'estoque_maximo',
                        'preco_custo', 'preco_venda',
                    )},
                    'estoque_atual': str(p['estoque_atual'] or 0),
                    'estoque_minimo': str(p['estoque_minimo'] or 0),
                    'estoque_maximo': str(p['estoque_maximo'] or 0),
                    'preco_custo': str(p['preco_custo'] or 0),
                    'preco_venda': str(p['preco_venda'] or 0),
                    'alerta_minimo': (p['estoque_atual'] or 0) < (p['estoque_minimo'] or 0),
                }
                for p in produtos
            ],
        })


class FolhaCompetenciaView(APIView):
    """
    Resumo da folha de pagamento por competência.
    Parâmetro: competencia (YYYY-MM, ex: 2024-03). Padrão: mês atual.
    """
    permission_classes = [IsBackofficeCompany]

    def get(self, request):
        from backend.apps.folha.models import FolhaPagamento, HoleriteFuncionario

        empresa = _empresa(request)
        hoje = date.today()
        competencia_param = request.query_params.get('competencia', hoje.strftime('%Y-%m'))

        try:
            ano, mes = competencia_param.split('-')
            ano, mes = int(ano), int(mes)
        except (ValueError, AttributeError):
            return Response(
                {'error': 'Parâmetro competencia inválido. Use o formato YYYY-MM.'},
                status=400,
            )

        folhas = FolhaPagamento.objects.filter(
            empresa=empresa,
            ativo=True,
            competencia__year=ano,
            competencia__month=mes,
        )

        totais = HoleriteFuncionario.objects.filter(
            folha_pagamento__in=folhas,
            ativo=True,
        ).aggregate(
            qtd_funcionarios=Count('id'),
            total_salario_bruto=Sum('salario_bruto'),
            total_inss=Sum('desconto_inss'),
            total_irrf=Sum('desconto_irrf'),
            total_fgts=Sum('desconto_fgts'),
            total_proventos=Sum('total_proventos'),
            total_descontos=Sum('total_descontos'),
            total_liquido=Sum('liquido_receber'),
        )

        return Response({
            'competencia': competencia_param,
            'folhas_abertas': folhas.count(),
            'resumo': {
                'funcionarios': totais['qtd_funcionarios'] or 0,
                'total_bruto': str(totais['total_salario_bruto'] or 0),
                'total_proventos': str(totais['total_proventos'] or 0),
                'total_inss': str(totais['total_inss'] or 0),
                'total_irrf': str(totais['total_irrf'] or 0),
                'total_fgts': str(totais['total_fgts'] or 0),
                'total_descontos': str(totais['total_descontos'] or 0),
                'total_liquido': str(totais['total_liquido'] or 0),
            },
        })
