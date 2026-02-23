from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import MovimentacaoFinanceira

@receiver(post_save, sender=MovimentacaoFinanceira)
def update_conta_bancaria_on_movimentacao_save(sender, instance, created, **kwargs):
    if created:
        # Quando uma nova movimentação é criada
        if instance.tipo_movimentacao == 'E': # Entrada
            instance.conta_bancaria.saldo_atual += instance.valor
        elif instance.tipo_movimentacao == 'S': # Saída
            instance.conta_bancaria.saldo_atual -= instance.valor
        # Transferência não afeta o saldo total de uma única conta diretamente
        # A lógica para transferência entre contas seria mais complexa (duas movimentações)
        instance.conta_bancaria.save(update_fields=['saldo_atual'])

@receiver(post_delete, sender=MovimentacaoFinanceira)
def update_conta_bancaria_on_movimentacao_delete(sender, instance, **kwargs):
    # Quando uma movimentação é excluída, reverter o efeito no saldo
    if instance.tipo_movimentacao == 'E': # Entrada
        instance.conta_bancaria.saldo_atual -= instance.valor
    elif instance.tipo_movimentacao == 'S': # Saída
        instance.conta_bancaria.saldo_atual += instance.valor
    instance.conta_bancaria.save(update_fields=['saldo_atual'])
