from django.apps import AppConfig

class EmpresasConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'backend.apps.empresas'
    verbose_name = 'Gestão de Empresas'

    def ready(self):
        import backend.apps.empresas.signals
