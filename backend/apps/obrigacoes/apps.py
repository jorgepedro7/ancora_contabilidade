from django.apps import AppConfig

class ObrigacoesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'backend.apps.obrigacoes'
    verbose_name = 'Obrigações Acessórias'

    def ready(self):
        import backend.apps.obrigacoes.signals
