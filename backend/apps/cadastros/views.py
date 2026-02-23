from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from backend.apps.core.permissions import IsActiveCompany
from .models import Cliente, Fornecedor, Produto
from .serializers import ClienteSerializer, FornecedorSerializer, ProdutoSerializer

class BaseCadastroViewSet(viewsets.ModelViewSet):
    permission_classes = [IsActiveCompany]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    
    def get_queryset(self):
        # Garante que o usuário só veja cadastros da empresa ativa
        if self.request.user.is_authenticated and self.request.user.empresa_ativa:
            return self.queryset.filter(empresa=self.request.user.empresa_ativa, ativo=True)
        return self.queryset.none() # Retorna queryset vazia se não houver empresa ativa ou autenticação

    def perform_create(self, serializer):
        serializer.save(empresa=self.request.user.empresa_ativa)

    def perform_destroy(self, instance):
        instance.soft_delete() # Soft delete instead of hard delete

class ClienteViewSet(BaseCadastroViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    filterset_fields = ['tipo_pessoa', 'ativo']
    search_fields = ['nome_razao_social', 'documento']

class FornecedorViewSet(BaseCadastroViewSet):
    queryset = Fornecedor.objects.all()
    serializer_class = FornecedorSerializer
    filterset_fields = ['tipo_pessoa', 'ativo']
    search_fields = ['nome_razao_social', 'documento']

class ProdutoViewSet(BaseCadastroViewSet):
    queryset = Produto.objects.all()
    serializer_class = ProdutoSerializer
    filterset_fields = ['origem', 'ativo', 'controla_estoque']
    search_fields = ['descricao', 'codigo_interno', 'ean', 'ncm']
