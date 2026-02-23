from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import FolhaPagamento, HoleriteFuncionario

# @receiver(post_save, sender=FolhaPagamento)
# def generate_holerites_on_folha_process(sender, instance, created, **kwargs):
#     if instance.status == 'PROCESSADA' and created:
#         # Lógica para gerar holerites para todos os funcionários ativos da empresa
#         # com contratos ativos na competência da folha
#         pass

# Você pode adicionar sinais aqui para atualizar totais da folha, etc.
