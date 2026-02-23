from django.contrib import admin
from .models import ObrigacaoFiscal

@admin.register(ObrigacaoFiscal)
class ObrigacaoFiscalAdmin(admin.ModelAdmin):
    list_display = ('tipo_obrigacao', 'data_vencimento', 'status', 'empresa', 'criado_em')
    list_filter = ('tipo_obrigacao', 'status', 'empresa')
    search_fields = ('descricao',)
