from django.urls import path
from .views import DashboardView, DREView, LivroFiscalView, PosicaoEstoqueView, FolhaCompetenciaView

urlpatterns = [
    path('dashboard/', DashboardView.as_view(), name='relatorio-dashboard'),
    path('dre/', DREView.as_view(), name='relatorio-dre'),
    path('livro-fiscal/', LivroFiscalView.as_view(), name='relatorio-livro-fiscal'),
    path('posicao-estoque/', PosicaoEstoqueView.as_view(), name='relatorio-posicao-estoque'),
    path('folha-competencia/', FolhaCompetenciaView.as_view(), name='relatorio-folha-competencia'),
]
