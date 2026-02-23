from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import LancamentoContabilViewSet, PartidaLancamentoViewSet, DREView, BalancoPatrimonialView
from rest_framework_nested import routers as nested_routers

router = DefaultRouter()
router.register(r'lancamentos', LancamentoContabilViewSet, basename='lancamento-contabil')

lancamentos_router = nested_routers.NestedSimpleRouter(router, r'lancamentos', lookup='lancamento')
lancamentos_router.register(r'partidas', PartidaLancamentoViewSet, basename='lancamento-partida')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(lancamentos_router.urls)),
    path('dre/', DREView.as_view(), name='dre-report'),
    path('balanco-patrimonial/', BalancoPatrimonialView.as_view(), name='balanco-patrimonial-report'),
]
