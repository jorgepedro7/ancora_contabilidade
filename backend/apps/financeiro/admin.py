from django.contrib import admin
from .models import ContaBancaria, PlanoContas, ContaAPagar, ContaAReceber, MovimentacaoFinanceira

@admin.register(ContaBancaria)
class ContaBancariaAdmin(admin.ModelAdmin):
    list_display = ('descricao', 'tipo_conta', 'saldo_atual', 'ativo', 'empresa')
    list_filter = ('tipo_conta', 'ativo', 'empresa')
    search_fields = ('descricao', 'empresa__nome_fantasia')
    readonly_fields = ('saldo_atual',)

@admin.register(PlanoContas)
class PlanoContasAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'descricao', 'tipo_conta', 'conta_pai', 'empresa', 'ativo')
    list_filter = ('tipo_conta', 'ativo', 'empresa')
    search_fields = ('codigo', 'descricao', 'empresa__nome_fantasia')

@admin.register(ContaAPagar)
class ContaAPagarAdmin(admin.ModelAdmin):
    list_display = ('descricao', 'valor_total', 'valor_pago', 'data_vencimento', 'status', 'fornecedor', 'empresa')
    list_filter = ('status', 'data_vencimento', 'empresa')
    search_fields = ('descricao', 'fornecedor__nome_razao_social', 'empresa__nome_fantasia')
    readonly_fields = ('valor_pago', 'valor_saldo')

@admin.register(ContaAReceber)
class ContaAReceberAdmin(admin.ModelAdmin):
    list_display = ('descricao', 'valor_total', 'valor_recebido', 'data_vencimento', 'status', 'cliente', 'empresa')
    list_filter = ('status', 'data_vencimento', 'empresa')
    search_fields = ('descricao', 'cliente__nome_razao_social', 'empresa__nome_fantasia')
    readonly_fields = ('valor_recebido', 'valor_saldo')

@admin.register(MovimentacaoFinanceira)
class MovimentacaoFinanceiraAdmin(admin.ModelAdmin):
    list_display = ('data_movimentacao', 'tipo_movimentacao', 'valor', 'conta_bancaria', 'empresa')
    list_filter = ('tipo_movimentacao', 'conta_bancaria', 'empresa')
    search_fields = ('descricao', 'conta_bancaria__descricao', 'empresa__nome_fantasia')
