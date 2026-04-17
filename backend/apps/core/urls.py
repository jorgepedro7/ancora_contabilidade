from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import PerfilUsuarioView, HealthCheckView, UsuarioViewSet

router = DefaultRouter()
router.register(r'usuarios', UsuarioViewSet, basename='usuarios')

urlpatterns = [
    path('perfil/', PerfilUsuarioView.as_view(), name='perfil_usuario'),
    path('health/', HealthCheckView.as_view(), name='health_check'),
    path('', include(router.urls)),
]
