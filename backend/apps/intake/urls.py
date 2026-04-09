from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    ChecklistCompetenciaViewSet,
    DocumentoRecebidoViewSet,
    ExportarQuestorView,
    LoteExportacaoQuestorViewSet,
    PendenciaViewSet,
    PortalClienteViewSet,
    ConfirmarRecebimentoView,
)

router = DefaultRouter()
router.register(r'portal', PortalClienteViewSet, basename='portal-cliente')
router.register(r'recebimentos', DocumentoRecebidoViewSet, basename='recebimento')
router.register(r'checklists', ChecklistCompetenciaViewSet, basename='checklist-competencia')
router.register(r'pendencias', PendenciaViewSet, basename='pendencia')
router.register(r'lotes', LoteExportacaoQuestorViewSet, basename='lote-questor')

urlpatterns = [
    path('', include(router.urls)),
    path('confirmar/', ConfirmarRecebimentoView.as_view(), name='intake-confirmar'),
    path('exportar/questor/', ExportarQuestorView.as_view(), name='intake-exportar-questor'),
]
