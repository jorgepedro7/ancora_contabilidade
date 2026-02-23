from rest_framework import serializers
from .models import Cliente, Fornecedor, Produto
from backend.apps.core.utils import validar_cpf, validar_cnpj, formatar_cpf, formatar_cnpj, buscar_cep
from django.db import IntegrityError

class PessoaBaseSerializer(serializers.ModelSerializer):
    # Adicione campos de empresa e validações comuns aqui, se necessário
    # empresa_id = serializers.UUIDField(source='empresa.id', read_only=True)
    # empresa_nome = serializers.CharField(source='empresa.nome_fantasia', read_only=True)

    class Meta:
        abstract = True # Esta é uma classe base para herança de serializers, não um serializer real.

    def validate_documento(self, value):
        tipo_pessoa = self.initial_data.get('tipo_pessoa')
        if tipo_pessoa == 'PF':
            if not validar_cpf(value):
                raise serializers.ValidationError("CPF inválido.")
        elif tipo_pessoa == 'PJ':
            if not validar_cnpj(value):
                raise serializers.ValidationError("CNPJ inválido.")
        return value

    def create(self, validated_data):
        # A empresa será adicionada pelo ViewSet
        validated_data['empresa'] = self.context['request'].user.empresa_ativa
        return super().create(validated_data)

class ClienteSerializer(PessoaBaseSerializer):
    class Meta:
        model = Cliente
        fields = '__all__'
        read_only_fields = ['id', 'empresa', 'criado_em', 'atualizado_em']

class FornecedorSerializer(PessoaBaseSerializer):
    class Meta:
        model = Fornecedor
        fields = '__all__'
        read_only_fields = ['id', 'empresa', 'criado_em', 'atualizado_em']

class ProdutoSerializer(serializers.ModelSerializer):
    margem_lucro = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)

    class Meta:
        model = Produto
        fields = '__all__'
        read_only_fields = ['id', 'empresa', 'criado_em', 'atualizado_em', 'estoque_atual']
    
    def create(self, validated_data):
        validated_data['empresa'] = self.context['request'].user.empresa_ativa
        try:
            return super().create(validated_data)
        except IntegrityError:
            raise serializers.ValidationError("Já existe um produto com o mesmo código interno nesta empresa.")
