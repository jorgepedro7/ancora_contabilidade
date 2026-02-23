from django.apps import AppConfig

class FolhaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'backend.apps.folha'
    verbose_name = 'Folha de Pagamento'

    def ready(self):
        import backend.apps.folha.signals
