from rest_framework import serializers
from .models import LocalEstoque, MovimentacaoEstoque, LoteEstoque, InventarioEstoque
from backend.apps.cadastros.serializers import ProdutoSerializer

class LocalEstoqueSerializer(serializers.ModelSerializer):
    class Meta:
        model = LocalEstoque
        fields = '__all__'
        read_only_fields = ['id', 'empresa', 'criado_em', 'atualizado_em']

class MovimentacaoEstoqueSerializer(serializers.ModelSerializer):
    produto_detail = ProdutoSerializer(source='produto', read_only=True)
    local_origem_detail = LocalEstoqueSerializer(source='local_origem', read_only=True)
    local_destino_detail = LocalEstoqueSerializer(source='local_destino', read_only=True)

    class Meta:
        model = MovimentacaoEstoque
        fields = '__all__'
        read_only_fields = ['id', 'empresa', 'data_movimentacao', 'criado_em', 'atualizado_em']

class LoteEstoqueSerializer(serializers.ModelSerializer):
    produto_detail = ProdutoSerializer(source='produto', read_only=True)
    local_estoque_detail = LocalEstoqueSerializer(source='local_estoque', read_only=True)

    class Meta:
        model = LoteEstoque
        fields = '__all__'
        read_only_fields = ['id', 'empresa', 'criado_em', 'atualizado_em']

class InventarioEstoqueSerializer(serializers.ModelSerializer):
    local_estoque_detail = LocalEstoqueSerializer(source='local_estoque', read_only=True)

    class Meta:
        model = InventarioEstoque
        fields = '__all__'
        read_only_fields = ['id', 'empresa', 'criado_em', 'atualizado_em']
