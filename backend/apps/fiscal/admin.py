from django.contrib import admin
from .models import NotaFiscal, ItemNotaFiscal, EventoNotaFiscal

@admin.register(NotaFiscal)
class NotaFiscalAdmin(admin.ModelAdmin):
    list_display = ('numero', 'serie', 'tipo_nf', 'finalidade', 'status', 'empresa', 'criado_em')
    list_filter = ('status', 'tipo_nf', 'finalidade', 'empresa')
    search_fields = ('numero', 'chave_acesso', 'destinatario_nome')
    readonly_fields = ('chave_acesso', 'protocolo', 'criado_em', 'atualizado_em')

@admin.register(ItemNotaFiscal)
class ItemNotaFiscalAdmin(admin.ModelAdmin):
    list_display = ('nota_fiscal', 'produto_descricao', 'quantidade', 'valor_unitario', 'valor_total')
    search_fields = ('nota_fiscal__numero', 'produto_descricao')
    raw_id_fields = ('nota_fiscal', 'produto')

    def produto_descricao(self, obj):
        return obj.produto.descricao if obj.produto else 'N/A'
    produto_descricao.short_description = 'Produto'

@admin.register(EventoNotaFiscal)
class EventoNotaFiscalAdmin(admin.ModelAdmin):
    list_display = ('nota_fiscal', 'tipo_evento', 'protocolo_retorno', 'criado_em')
    list_filter = ('tipo_evento',)
    search_fields = ('nota_fiscal__numero',)
