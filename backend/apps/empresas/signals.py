from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Empresa, ConfiguracaoFiscalEmpresa

@receiver(post_save, sender=Empresa)
def create_default_configuracao_fiscal(sender, instance, created, **kwargs):
    if created:
        ConfiguracaoFiscalEmpresa.objects.create(empresa=instance)
