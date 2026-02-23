from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import (
    CargoViewSet, DepartamentoViewSet, FuncionarioViewSet, 
    ContratoTrabalhoViewSet, FolhaPagamentoViewSet, 
    HoleriteFuncionarioViewSet, RegistroPontoViewSet, 
    JustificativaPontoViewSet, DocumentoFuncionarioViewSet
)

router = DefaultRouter()
router.register(r'cargos', CargoViewSet, basename='cargo')
router.register(r'departamentos', DepartamentoViewSet, basename='departamento')
router.register(r'funcionarios', FuncionarioViewSet, basename='funcionario')
router.register(r'contratos', ContratoTrabalhoViewSet, basename='contrato')
router.register(r'folha-pagamento', FolhaPagamentoViewSet, basename='folha-pagamento')
router.register(r'holerites', HoleriteFuncionarioViewSet, basename='holerite')
router.register(r'pontos', RegistroPontoViewSet, basename='ponto')
router.register(r'justificativas', JustificativaPontoViewSet, basename='justificativa')
router.register(r'documentos', DocumentoFuncionarioViewSet, basename='documento')

urlpatterns = [
    path('', include(router.urls)),
]
