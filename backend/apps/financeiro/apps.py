from django.apps import AppConfig

class FinanceiroConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'backend.apps.financeiro'
    verbose_name = 'Gestão Financeira'

    def ready(self):
        import backend.apps.financeiro.signals
