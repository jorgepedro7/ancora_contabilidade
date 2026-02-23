from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ObrigacaoFiscal
from datetime import date

@receiver(post_save, sender=ObrigacaoFiscal)
def check_obrigacao_overdue(sender, instance, **kwargs):
    if instance.data_vencimento < date.today() and instance.status == 'ABERTO':
        instance.status = 'ATRASADO'
        instance.save(update_fields=['status'])

# Você pode adicionar mais sinais aqui, por exemplo, para gerar alertas
# ou interagir com outras partes do sistema.
