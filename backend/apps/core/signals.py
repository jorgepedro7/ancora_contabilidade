from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from rest_framework_simplejwt.tokens import RefreshToken
from .models import LogAtividade, Usuario
import json

@receiver(post_save, sender=Usuario)
def log_usuario_save(sender, instance, created, **kwargs):
    acao = 'CREATE' if created else 'UPDATE'
    # Evita loop infinito se LogAtividade também dispara post_save
    if isinstance(instance, LogAtividade):
        return

    # A lógica de LogAtividade para Usuario pode ser mais complexa
    # Aqui, um exemplo simples. O ideal é capturar os dados anteriores e novos.
    LogAtividade.objects.create(
        usuario=instance,
        acao=acao,
        modulo='core.Usuario',
        objeto_tipo='Usuario',
        objeto_id=instance.id,
        descricao=f'{acao} de Usuário: {instance.email}'
        # dados_anteriores e dados_novos podem ser populados com mais detalhes
    )

@receiver(post_delete, sender=Usuario)
def log_usuario_delete(sender, instance, **kwargs):
    # Evita loop infinito se LogAtividade também dispara post_delete
    if isinstance(instance, LogAtividade):
        return

    LogAtividade.objects.create(
        usuario=instance,
        acao='DELETE',
        modulo='core.Usuario',
        objeto_tipo='Usuario',
        objeto_id=instance.id,
        descricao=f'DELETE de Usuário: {instance.email}'
    )

# Exemplo de como invalidar tokens antigos no login/logout
# @receiver(user_logged_in)
# def invalidate_old_tokens(sender, request, user, **kwargs):
#     # Esta é uma abordagem mais complexa e talvez não necessária para v1
#     # Se usar, certifique-se de que o BLACKLIST_AFTER_ROTATION esteja True no settings
#     pass

# Outros signals para outros models podem ser adicionados aqui
# Ex:
# @receiver(post_save, sender=Empresa)
# def log_empresa_save(sender, instance, created, **kwargs):
#    ...
