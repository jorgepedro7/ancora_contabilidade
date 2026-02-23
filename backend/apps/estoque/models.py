from django.db import models
from backend.apps.core.models import ModelBaseEmpresa
from backend.apps.cadastros.models import Produto
from datetime import date
from django.db import transaction

class LocalEstoque(ModelBaseEmpresa):
    TIPO_LOCAL_CHOICES = [
        ('CD', 'Centro de Distribuição'),
        ('LOJA', 'Loja/Varejo'),
        ('ARM', 'Armazém'),
        ('PRAT', 'Prateleira'),
        ('OUTRO', 'Outro'),
    ]

    nome = models.CharField(max_length=100, verbose_name="Nome do Local")
    tipo_local = models.CharField(max_length=5, choices=TIPO_LOCAL_CHOICES, default='ARM', verbose_name="Tipo de Local")
    endereco_completo = models.TextField(blank=True, null=True, verbose_name="Endereço Completo")

    class Meta:
        verbose_name = "Local de Estoque"
        verbose_name_plural = "Locais de Estoque"
        unique_together = ('empresa', 'nome')

    def __str__(self):
        return self.nome

class MovimentacaoEstoque(ModelBaseEmpresa):
    TIPO_MOVIMENTACAO_CHOICES = [
        ('ENTRADA', 'Entrada'),
        ('SAIDA', 'Saída'),
        ('TRANSFERENCIA', 'Transferência'),
        ('AJUSTE', 'Ajuste de Estoque'),
        ('INVENTARIO', 'Inventário'),
    ]

    produto = models.ForeignKey(Produto, on_delete=models.PROTECT, related_name='movimentacoes_estoque')
    tipo_movimentacao = models.CharField(max_length=15, choices=TIPO_MOVIMENTACAO_CHOICES, verbose_name="Tipo de Movimentação")
    quantidade = models.DecimalField(max_digits=15, decimal_places=3, verbose_name="Quantidade")
    local_origem = models.ForeignKey(LocalEstoque, on_delete=models.PROTECT, blank=True, null=True, related_name='saidas_estoque', verbose_name="Local de Origem")
    local_destino = models.ForeignKey(LocalEstoque, on_delete=models.PROTECT, blank=True, null=True, related_name='entradas_estoque', verbose_name="Local de Destino")
    data_movimentacao = models.DateTimeField(auto_now_add=True, verbose_name="Data da Movimentação")
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")

    class Meta:
        verbose_name = "Movimentação de Estoque"
        verbose_name_plural = "Movimentações de Estoque"
        ordering = ['-data_movimentacao']

    def __str__(self):
        return f"{self.get_tipo_movimentacao_display()} de {self.quantidade} {self.produto.descricao}"

class LoteEstoque(ModelBaseEmpresa):
    produto = models.ForeignKey(Produto, on_delete=models.PROTECT, related_name='lotes')
    local_estoque = models.ForeignKey(LocalEstoque, on_delete=models.PROTECT, related_name='lotes_armazenados')
    codigo_lote = models.CharField(max_length=100, blank=True, null=True, verbose_name="Código do Lote")
    data_fabricacao = models.DateField(blank=True, null=True, verbose_name="Data de Fabricação")
    data_validade = models.DateField(blank=True, null=True, verbose_name="Data de Validade")
    quantidade = models.DecimalField(max_digits=15, decimal_places=3, default=0.000, verbose_name="Quantidade em Lote")

    class Meta:
        verbose_name = "Lote de Estoque"
        verbose_name_plural = "Lotes de Estoque"
        unique_together = ('empresa', 'produto', 'local_estoque', 'codigo_lote')
    
    def __str__(self):
        return f"Lote {self.codigo_lote} de {self.produto.descricao} em {self.local_estoque.nome}"

class InventarioEstoque(ModelBaseEmpresa):
    STATUS_CHOICES = [
        ('ABERTO', 'Aberto'),
        ('FINALIZADO', 'Finalizado'),
        ('CANCELADO', 'Cancelado'),
    ]
    data_inventario = models.DateField(default=date.today, verbose_name="Data do Inventário")
    local_estoque = models.ForeignKey(LocalEstoque, on_delete=models.PROTECT, related_name='inventarios', verbose_name="Local Inventariado")
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='ABERTO', verbose_name="Status")

    class Meta:
        verbose_name = "Inventário de Estoque"
        verbose_name_plural = "Inventários de Estoque"
        unique_together = ('empresa', 'local_estoque', 'data_inventario')
    
    def __str__(self):
        return f"Inventário de {self.local_estoque.nome} em {self.data_inventario}"
