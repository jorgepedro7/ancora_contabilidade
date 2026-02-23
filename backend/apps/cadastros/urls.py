from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import ClienteViewSet, FornecedorViewSet, ProdutoViewSet

router = DefaultRouter()
router.register(r'clientes', ClienteViewSet, basename='cliente')
router.register(r'fornecedores', FornecedorViewSet, basename='fornecedor')
router.register(r'produtos', ProdutoViewSet, basename='produto')

urlpatterns = [
    path('', include(router.urls)),
]
