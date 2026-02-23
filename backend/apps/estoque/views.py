from rest_framework import viewsets, filters, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from backend.apps.core.permissions import IsActiveCompany
from .models import LocalEstoque, MovimentacaoEstoque, LoteEstoque, InventarioEstoque
from .serializers import LocalEstoqueSerializer, MovimentacaoEstoqueSerializer, LoteEstoqueSerializer, InventarioEstoqueSerializer
from backend.apps.cadastros.models import Produto
from backend.apps.cadastros.serializers import ProdutoSerializer

class BaseEstoqueViewSet(viewsets.ModelViewSet):
    permission_classes = [IsActiveCompany]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    
    def get_queryset(self):
        if self.request.user.is_authenticated and self.request.user.empresa_ativa:
            return self.queryset.filter(empresa=self.request.user.empresa_ativa, ativo=True)
        return self.queryset.none()

    def perform_create(self, serializer):
        serializer.save(empresa=self.request.user.empresa_ativa)

    def perform_destroy(self, instance):
        instance.soft_delete()

class LocalEstoqueViewSet(BaseEstoqueViewSet):
    queryset = LocalEstoque.objects.all()
    serializer_class = LocalEstoqueSerializer
    filterset_fields = ['tipo_local', 'ativo']
    search_fields = ['nome', 'endereco_completo']

class MovimentacaoEstoqueViewSet(BaseEstoqueViewSet):
    queryset = MovimentacaoEstoque.objects.all()
    serializer_class = MovimentacaoEstoqueSerializer
    filterset_fields = ['tipo_movimentacao', 'produto', 'local_origem', 'local_destino', 'ativo']
    search_fields = ['observacoes', 'produto__descricao']

    @action(detail=False, methods=['post'])
    def entrada(self, request):
        produto_id = request.data.get('produto')
        quantidade = request.data.get('quantidade')
        local_destino_id = request.data.get('local_destino')
        observacoes = request.data.get('observacoes')

        if not all([produto_id, quantidade, local_destino_id]):
            return Response({'error': 'Produto, quantidade e local de destino são obrigatórios.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            produto = Produto.objects.get(id=produto_id, empresa=self.request.user.empresa_ativa)
            local_destino = LocalEstoque.objects.get(id=local_destino_id, empresa=self.request.user.empresa_ativa)
            quantidade = float(quantidade)

            mov = MovimentacaoEstoque.objects.create(
                empresa=self.request.user.empresa_ativa,
                produto=produto,
                tipo_movimentacao='ENTRADA',
                quantidade=quantidade,
                local_destino=local_destino,
                observacoes=observacoes
            )
            return Response(MovimentacaoEstoqueSerializer(mov).data, status=status.HTTP_201_CREATED)
        except (Produto.DoesNotExist, LocalEstoque.DoesNotExist) as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError as e:
            return Response({'error': 'Quantidade deve ser um número válido.'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def saida(self, request):
        produto_id = request.data.get('produto')
        quantidade = request.data.get('quantidade')
        local_origem_id = request.data.get('local_origem')
        observacoes = request.data.get('observacoes')

        if not all([produto_id, quantidade, local_origem_id]):
            return Response({'error': 'Produto, quantidade e local de origem são obrigatórios.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            produto = Produto.objects.get(id=produto_id, empresa=self.request.user.empresa_ativa)
            local_origem = LocalEstoque.objects.get(id=local_origem_id, empresa=self.request.user.empresa_ativa)
            quantidade = float(quantidade)

            # Verificar se há estoque suficiente antes de registrar a saída
            if produto.estoque_atual < quantidade:
                return Response({'error': 'Estoque insuficiente para esta saída.'}, status=status.HTTP_400_BAD_REQUEST)

            mov = MovimentacaoEstoque.objects.create(
                empresa=self.request.user.empresa_ativa,
                produto=produto,
                tipo_movimentacao='SAIDA',
                quantidade=quantidade,
                local_origem=local_origem,
                observacoes=observacoes
            )
            return Response(MovimentacaoEstoqueSerializer(mov).data, status=status.HTTP_201_CREATED)
        except (Produto.DoesNotExist, LocalEstoque.DoesNotExist) as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError as e:
            return Response({'error': 'Quantidade deve ser um número válido.'}, status=status.HTTP_400_BAD_REQUEST)

class LoteEstoqueViewSet(BaseEstoqueViewSet):
    queryset = LoteEstoque.objects.all()
    serializer_class = LoteEstoqueSerializer
    filterset_fields = ['produto', 'local_estoque', 'data_validade', 'ativo']
    search_fields = ['codigo_lote', 'produto__descricao']

class InventarioEstoqueViewSet(BaseEstoqueViewSet):
    queryset = InventarioEstoque.objects.all()
    serializer_class = InventarioEstoqueSerializer
    filterset_fields = ['local_estoque', 'status', 'data_inventario', 'ativo']
    search_fields = ['observacoes', 'local_estoque__nome']

    @action(detail=True, methods=['post'])
    def finalizar_inventario(self, request, pk=None):
        inventario = self.get_object()
        if inventario.status != 'ABERTO':
            return Response({'error': 'Apenas inventários com status ABERTO podem ser finalizados.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Lógica para processar as contagens do inventário e ajustar o estoque
        # Isso geralmente envolve comparar o estoque teórico com o físico e gerar movimentos de ajuste
        # Por simplicidade, apenas mudamos o status aqui
        inventario.status = 'FINALIZADO'
        inventario.save()
        return Response(InventarioEstoqueSerializer(inventario).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def cancelar_inventario(self, request, pk=None):
        inventario = self.get_object()
        if inventario.status != 'ABERTO':
            return Response({'error': 'Apenas inventários com status ABERTO podem ser cancelados.'}, status=status.HTTP_400_BAD_REQUEST)
        
        inventario.status = 'CANCELADO'
        inventario.save()
        return Response(InventarioEstoqueSerializer(inventario).data, status=status.HTTP_200_OK)

class PosicaoEstoqueView(generics.ListAPIView):
    permission_classes = [IsActiveCompany]
    serializer_class = ProdutoSerializer # Reutiliza o serializer de Produto para a posição

    def get_queryset(self):
        empresa = self.request.user.empresa_ativa
        queryset = Produto.objects.filter(empresa=empresa, ativo=True)
        # Pode adicionar filtros por local de estoque ou outras propriedades
        return queryset
