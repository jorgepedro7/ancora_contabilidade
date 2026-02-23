from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import ContaBancariaViewSet, PlanoContasViewSet, ContaAPagarViewSet, ContaAReceberViewSet, MovimentacaoFinanceiraViewSet, FluxoCaixaView, ContasVencendoHojeView

router = DefaultRouter()
router.register(r'contas-bancarias', ContaBancariaViewSet, basename='conta-bancaria')
router.register(r'planos-contas', PlanoContasViewSet, basename='plano-contas')
router.register(r'contas-pagar', ContaAPagarViewSet, basename='conta-pagar')
router.register(r'contas-receber', ContaAReceberViewSet, basename='conta-receber')
router.register(r'movimentacoes', MovimentacaoFinanceiraViewSet, basename='movimentacao-financeira')

urlpatterns = [
    path('', include(router.urls)),
    path('fluxo-caixa/', FluxoCaixaView.as_view(), name='fluxo-caixa'),
    path('vencendo-hoje/', ContasVencendoHojeView.as_view(), name='contas-vencendo-hoje'),
]
