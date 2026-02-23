from django.urls import path
from .views import PerfilUsuarioView, HealthCheckView

urlpatterns = [
    path('perfil/', PerfilUsuarioView.as_view(), name='perfil_usuario'),
    path('health/', HealthCheckView.as_view(), name='health_check'),
    # Outras URLs do módulo core
]
