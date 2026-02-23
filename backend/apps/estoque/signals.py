from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import MovimentacaoEstoque
from backend.apps.cadastros.models import Produto
from django.db import transaction

@receiver(post_save, sender=MovimentacaoEstoque)
def update_produto_estoque_on_movimentacao_save(sender, instance, created, **kwargs):
    if instance.produto.controla_estoque:
        with transaction.atomic():
            # Refresh from DB to get the latest estoque_atual, avoiding race conditions
            instance.produto.refresh_from_db()
            
            if instance.tipo_movimentacao == 'ENTRADA':
                instance.produto.estoque_atual += instance.quantidade
            elif instance.tipo_movimentacao == 'SAIDA':
                instance.produto.estoque_atual -= instance.quantidade
            elif instance.tipo_movimentacao == 'AJUSTE':
                # Ajuste pode ser positivo ou negativo, dependendo da lógica de inventário
                # Por simplicidade, assumimos que a 'quantidade' já representa o ajuste líquido
                # Ou que o ajuste é para 'setar' um valor. Aqui, vou somar/subtrair
                # Idealmente, um ajuste seria mais complexo, comparando o valor atual com o valor "correto"
                pass # Lógica de ajuste será implementada em outro local, ou diretamente na view
            
            # Transferencia não altera o estoque total do produto, apenas de local
            # Inventario também é tratado de forma mais complexa

            instance.produto.save(update_fields=['estoque_atual'])

@receiver(post_delete, sender=MovimentacaoEstoque)
def update_produto_estoque_on_movimentacao_delete(sender, instance, **kwargs):
    if instance.produto.controla_estoque:
        with transaction.atomic():
            instance.produto.refresh_from_db()
            if instance.tipo_movimentacao == 'ENTRADA':
                instance.produto.estoque_atual -= instance.quantidade
            elif instance.tipo_movimentacao == 'SAIDA':
                instance.produto.estoque_atual += instance.quantidade
            instance.produto.save(update_fields=['estoque_atual'])
