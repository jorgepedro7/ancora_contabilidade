from rest_framework import serializers
from .models import NotaFiscal, ItemNotaFiscal, EventoNotaFiscal
from backend.apps.cadastros.models import Produto
from backend.apps.cadastros.serializers import ProdutoSerializer

class ItemNotaFiscalSerializer(serializers.ModelSerializer):
    produto_detail = ProdutoSerializer(source='produto', read_only=True) # Para exibir detalhes do produto

    class Meta:
        model = ItemNotaFiscal
        fields = '__all__'
        read_only_fields = ['valor_total'] # Calculado automaticamente no save()

class NotaFiscalSerializer(serializers.ModelSerializer):
    itens = ItemNotaFiscalSerializer(many=True, read_only=True) # Itens são criados/atualizados separadamente ou aninhados
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    tipo_nf_display = serializers.CharField(source='get_tipo_nf_display', read_only=True)
    finalidade_display = serializers.CharField(source='get_finalidade_display', read_only=True)
    modalidade_frete_display = serializers.CharField(source='get_modalidade_frete_display', read_only=True)

    class Meta:
        model = NotaFiscal
        fields = '__all__'
        read_only_fields = [
            'id', 'empresa', 'chave_acesso', 'protocolo', 'numero', 'serie',
            'data_emissao', 'status', 'criado_em', 'atualizado_em',
            'valor_produtos', 'valor_desconto', 'valor_frete', 'valor_seguro',
            'valor_outras_despesas', 'valor_icms', 'valor_icms_st', 'valor_ipi',
            'valor_pis', 'valor_cofins', 'valor_total_nf',
            'codigo_retorno', 'mensagem_retorno',
            'itens', # Itens serão manipulados via sub-endpoints ou nested writable serializer
            'status_display', 'tipo_nf_display', 'finalidade_display', 'modalidade_frete_display'
        ]

    def create(self, validated_data):
        validated_data['empresa'] = self.context['request'].user.empresa_ativa
        return super().create(validated_data)


class EventoNotaFiscalSerializer(serializers.ModelSerializer):
    tipo_evento_display = serializers.CharField(source='get_tipo_evento_display', read_only=True)

    class Meta:
        model = EventoNotaFiscal
        fields = '__all__'
        read_only_fields = ['id', 'empresa', 'nota_fiscal', 'data_registro', 'protocolo_retorno']
