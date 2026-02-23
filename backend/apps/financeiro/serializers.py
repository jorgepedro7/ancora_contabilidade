from rest_framework import serializers
from .models import ContaBancaria, PlanoContas, ContaAPagar, ContaAReceber, MovimentacaoFinanceira
from backend.apps.cadastros.serializers import FornecedorSerializer, ClienteSerializer

class ContaBancariaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContaBancaria
        fields = '__all__'
        read_only_fields = ['id', 'empresa', 'saldo_atual', 'criado_em', 'atualizado_em']

class PlanoContasSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlanoContas
        fields = '__all__'
        read_only_fields = ['id', 'empresa', 'criado_em', 'atualizado_em']

class ContaAPagarSerializer(serializers.ModelSerializer):
    fornecedor_detail = FornecedorSerializer(source='fornecedor', read_only=True)
    conta_contabil_detail = PlanoContasSerializer(source='conta_contabil', read_only=True)
    esta_vencida = serializers.BooleanField(read_only=True)
    valor_saldo = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)

    class Meta:
        model = ContaAPagar
        fields = '__all__'
        read_only_fields = ['id', 'empresa', 'valor_pago', 'status', 'data_liquidacao', 'criado_em', 'atualizado_em']

class ContaAReceberSerializer(serializers.ModelSerializer):
    cliente_detail = ClienteSerializer(source='cliente', read_only=True)
    conta_contabil_detail = PlanoContasSerializer(source='conta_contabil', read_only=True)
    esta_vencida = serializers.BooleanField(read_only=True)
    valor_saldo = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)

    class Meta:
        model = ContaAReceber
        fields = '__all__'
        read_only_fields = ['id', 'empresa', 'valor_recebido', 'status', 'data_liquidacao', 'criado_em', 'atualizado_em']

class MovimentacaoFinanceiraSerializer(serializers.ModelSerializer):
    conta_bancaria_detail = ContaBancariaSerializer(source='conta_bancaria', read_only=True)
    conta_contabil_detail = PlanoContasSerializer(source='conta_contabil', read_only=True)

    class Meta:
        model = MovimentacaoFinanceira
        fields = '__all__'
        read_only_fields = ['id', 'empresa', 'criado_em', 'atualizado_em']
