from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import MovimentacaoEstoque
from django.db import transaction


@receiver(post_save, sender=MovimentacaoEstoque)
def update_produto_estoque_on_movimentacao_save(sender, instance, created, **kwargs):
    if not instance.produto.controla_estoque:
        return

    with transaction.atomic():
        instance.produto.refresh_from_db()

        if instance.tipo_movimentacao == 'ENTRADA':
            instance.produto.estoque_atual += instance.quantidade
        elif instance.tipo_movimentacao == 'SAIDA':
            instance.produto.estoque_atual -= instance.quantidade
        elif instance.tipo_movimentacao == 'AJUSTE':
            # quantidade representa delta: positivo = acréscimo, negativo = decréscimo
            instance.produto.estoque_atual += instance.quantidade
        # TRANSFERENCIA e INVENTARIO não alteram o estoque total do produto

        instance.produto.save(update_fields=['estoque_atual'])


@receiver(post_delete, sender=MovimentacaoEstoque)
def update_produto_estoque_on_movimentacao_delete(sender, instance, **kwargs):
    if not instance.produto.controla_estoque:
        return

    with transaction.atomic():
        instance.produto.refresh_from_db()
        if instance.tipo_movimentacao == 'ENTRADA':
            instance.produto.estoque_atual -= instance.quantidade
        elif instance.tipo_movimentacao == 'SAIDA':
            instance.produto.estoque_atual += instance.quantidade
        elif instance.tipo_movimentacao == 'AJUSTE':
            instance.produto.estoque_atual -= instance.quantidade
        instance.produto.save(update_fields=['estoque_atual'])
