from django.contrib import admin
from .models import LancamentoContabil, PartidaLancamento

class PartidaLancamentoInline(admin.TabularInline):
    model = PartidaLancamento
    extra = 1

@admin.register(LancamentoContabil)
class LancamentoContabilAdmin(admin.ModelAdmin):
    list_display = ('data_lancamento', 'historico', 'tipo_lancamento', 'empresa', 'criado_em')
    list_filter = ('tipo_lancamento', 'empresa')
    search_fields = ('historico',)
    inlines = [PartidaLancamentoInline]

# Plano de Contas já é registrado no app financeiro
# @admin.register(PlanoContas)
# class PlanoContasAdmin(admin.ModelAdmin):
#    list_display = ('codigo', 'descricao', 'tipo_conta', 'conta_pai', 'empresa', 'ativo')
