from django.contrib import admin
from .models import LocalEstoque, MovimentacaoEstoque, LoteEstoque, InventarioEstoque

@admin.register(LocalEstoque)
class LocalEstoqueAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tipo_local', 'empresa', 'ativo')
    list_filter = ('tipo_local', 'ativo', 'empresa')
    search_fields = ('nome',)

@admin.register(MovimentacaoEstoque)
class MovimentacaoEstoqueAdmin(admin.ModelAdmin):
    list_display = ('data_movimentacao', 'tipo_movimentacao', 'produto', 'quantidade', 'local_origem', 'local_destino', 'empresa')
    list_filter = ('tipo_movimentacao', 'empresa', 'local_origem', 'local_destino')
    search_fields = ('produto__descricao',)
    raw_id_fields = ('produto', 'local_origem', 'local_destino')

@admin.register(LoteEstoque)
class LoteEstoqueAdmin(admin.ModelAdmin):
    list_display = ('produto', 'codigo_lote', 'data_validade', 'quantidade', 'local_estoque', 'empresa')
    list_filter = ('data_validade', 'local_estoque', 'empresa')
    search_fields = ('produto__descricao', 'codigo_lote')

@admin.register(InventarioEstoque)
class InventarioEstoqueAdmin(admin.ModelAdmin):
    list_display = ('data_inventario', 'local_estoque', 'status', 'empresa')
    list_filter = ('status', 'local_estoque', 'empresa')
    search_fields = ('local_estoque__nome',)
