from rest_framework import routers
from rest_framework_nested import routers as nested_routers
from django.urls import path, include
from .views import NotaFiscalViewSet, ItemNotaFiscalViewSet, EventoNotaFiscalViewSet

router = routers.DefaultRouter()
router.register(r'notas-fiscais', NotaFiscalViewSet, basename='notafiscal')

notas_router = nested_routers.NestedSimpleRouter(router, r'notas-fiscais', lookup='notafiscal')
notas_router.register(r'itens', ItemNotaFiscalViewSet, basename='notafiscal-item')
notas_router.register(r'eventos', EventoNotaFiscalViewSet, basename='notafiscal-evento')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(notas_router.urls)),
]
