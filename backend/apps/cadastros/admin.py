from django.contrib import admin
from .models import Cliente, Fornecedor, Produto

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nome_razao_social', 'documento', 'tipo_pessoa', 'ativo', 'empresa')
    search_fields = ('nome_razao_social', 'documento', 'empresa__nome_fantasia')
    list_filter = ('ativo', 'tipo_pessoa', 'empresa')

@admin.register(Fornecedor)
class FornecedorAdmin(admin.ModelAdmin):
    list_display = ('nome_razao_social', 'documento', 'tipo_pessoa', 'ativo', 'empresa')
    search_fields = ('nome_razao_social', 'documento', 'empresa__nome_fantasia')
    list_filter = ('ativo', 'tipo_pessoa', 'empresa')

@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('descricao', 'codigo_interno', 'ncm', 'ean', 'preco_venda', 'estoque_atual', 'ativo', 'empresa')
    search_fields = ('descricao', 'codigo_interno', 'ean', 'empresa__nome_fantasia')
    list_filter = ('ativo', 'empresa', 'origem')
