from rest_framework import serializers
from .models import Empresa, ConfiguracaoFiscalEmpresa
from backend.apps.core.utils import validar_cnpj


MAX_CERTIFICADO_SIZE = 5 * 1024 * 1024
ALLOWED_CERTIFICADO_EXTENSIONS = {'.pfx', '.p12'}

class ConfiguracaoFiscalEmpresaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConfiguracaoFiscalEmpresa
        fields = [
            'id',
            'empresa',
            'ambiente_sefaz',
            'serie_nfe',
            'proximo_numero_nfe',
            'serie_nfce',
            'proximo_numero_nfce',
            'serie_nfse',
            'proximo_numero_nfse',
            'csc_id_nfce',
            'csc_token_nfce',
            'ativo',
            'criado_em',
            'atualizado_em',
        ]
        read_only_fields = ('empresa',)
        extra_kwargs = {
            'csc_token_nfce': {
                'write_only': True,
                'required': False,
                'allow_null': True,
                'allow_blank': True,
            },
        }

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
        extra_kwargs = {
            'certificado_digital_pfx': {
                'write_only': True,
                'required': False,
                'allow_null': True,
            },
            'certificado_senha': {
                'write_only': True,
                'required': False,
                'allow_null': True,
                'allow_blank': True,
            },
        }

    def validate_cnpj(self, value):
        if not validar_cnpj(value):
            raise serializers.ValidationError("CNPJ inválido.")
        return value

    def validate_certificado_digital_pfx(self, value):
        if not value:
            return value

        filename = (getattr(value, 'name', '') or '').lower()
        if not any(filename.endswith(extension) for extension in ALLOWED_CERTIFICADO_EXTENSIONS):
            raise serializers.ValidationError('Envie apenas certificados .pfx ou .p12.')

        if getattr(value, 'size', 0) > MAX_CERTIFICADO_SIZE:
            raise serializers.ValidationError('O certificado excede o tamanho máximo permitido de 5 MB.')

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
