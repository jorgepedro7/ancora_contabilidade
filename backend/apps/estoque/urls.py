from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import LocalEstoqueViewSet, MovimentacaoEstoqueViewSet, LoteEstoqueViewSet, InventarioEstoqueViewSet, PosicaoEstoqueView

router = DefaultRouter()
router.register(r'locais', LocalEstoqueViewSet, basename='local-estoque')
router.register(r'movimentacoes', MovimentacaoEstoqueViewSet, basename='movimentacao-estoque')
router.register(r'lotes', LoteEstoqueViewSet, basename='lote-estoque')
router.register(r'inventarios', InventarioEstoqueViewSet, basename='inventario-estoque')

urlpatterns = [
    path('', include(router.urls)),
    path('posicao/', PosicaoEstoqueView.as_view(), name='posicao-estoque'),
]
