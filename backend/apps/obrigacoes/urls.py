from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import ObrigacaoFiscalViewSet

router = DefaultRouter()
router.register(r'obrigacoes', ObrigacaoFiscalViewSet, basename='obrigacao-fiscal')

urlpatterns = [
    path('', include(router.urls)),
]
