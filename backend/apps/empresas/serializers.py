from rest_framework import serializers
from .models import Empresa, ConfiguracaoFiscalEmpresa
from backend.apps.core.utils import validar_cnpj, buscar_cep

class ConfiguracaoFiscalEmpresaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConfiguracaoFiscalEmpresa
        fields = '__all__'
        read_only_fields = ('empresa',)

class EmpresaSerializer(serializers.ModelSerializer):
    configuracao_fiscal = ConfiguracaoFiscalEmpresaSerializer(required=False)
    certificado_vencido = serializers.BooleanField(read_only=True)
    nome_exibicao = serializers.CharField(read_only=True)
    endereco_completo = serializers.CharField(read_only=True)

    class Meta:
        model = Empresa
        fields = [
            'id', 'razao_social', 'nome_fantasia', 'cnpj', 'inscricao_estadual',
            'inscricao_municipal', 'cnae_principal', 'cnae_secundarios',
            'regime_tributario', 'porte', 'cep', 'logradouro', 'numero',
            'complemento', 'bairro', 'municipio', 'uf', 'ibge',
            'certificado_digital_pfx', 'certificado_senha', 'certificado_data_validade',
            'ativo', 'criado_em', 'atualizado_em',
            'configuracao_fiscal', 'certificado_vencido', 'nome_exibicao', 'endereco_completo'
        ]
        read_only_fields = ['id', 'criado_em', 'atualizado_em']

    def validate_cnpj(self, value):
        if not validar_cnpj(value):
            raise serializers.ValidationError("CNPJ inválido.")
        return value
    
    def create(self, validated_data):
        config_data = validated_data.pop('configuracao_fiscal', {})
        empresa = super().create(validated_data)
        config_instance, _ = ConfiguracaoFiscalEmpresa.objects.get_or_create(empresa=empresa)
        if config_data:
            for attr, value in config_data.items():
                setattr(config_instance, attr, value)
            config_instance.save()
        return empresa

    def update(self, instance, validated_data):
        config_data = validated_data.pop('configuracao_fiscal', None)
        
        # Atualiza os dados da empresa
        instance = super().update(instance, validated_data)
        
        # Atualiza a configuração fiscal se fornecida
        if config_data:
            config_instance = instance.configuracao_fiscal
            for attr, value in config_data.items():
                setattr(config_instance, attr, value)
            config_instance.save()
            
        return instance
