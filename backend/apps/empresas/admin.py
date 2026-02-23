from django.contrib import admin
from .models import Empresa, ConfiguracaoFiscalEmpresa

@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ('nome_fantasia', 'razao_social', 'cnpj', 'ativo', 'regime_tributario', 'certificado_vencido')
    search_fields = ('nome_fantasia', 'razao_social', 'cnpj')
    list_filter = ('ativo', 'regime_tributario', 'porte')
    readonly_fields = ('certificado_vencido',)

@admin.register(ConfiguracaoFiscalEmpresa)
class ConfiguracaoFiscalEmpresaAdmin(admin.ModelAdmin):
    list_display = ('empresa', 'ambiente_sefaz', 'proximo_numero_nfe', 'proximo_numero_nfce', 'proximo_numero_nfse')
    search_fields = ('empresa__nome_fantasia',)
    list_filter = ('ambiente_sefaz',)
