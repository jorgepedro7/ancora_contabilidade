from django.apps import AppConfig

class EstoqueConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'backend.apps.estoque'
    verbose_name = 'Gestão de Estoque'

    def ready(self):
        import backend.apps.estoque.signals
