from rest_framework import serializers
from .models import (
    Cargo, Departamento, Funcionario, ContratoTrabalho, 
    FolhaPagamento, HoleriteFuncionario, RegistroPonto, 
    JustificativaPonto, DocumentoFuncionario
)
from backend.apps.core.utils import validar_cpf

class CargoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cargo
        fields = '__all__'
        read_only_fields = ['id', 'empresa', 'criado_em', 'atualizado_em']

class DepartamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Departamento
        fields = '__all__'
        read_only_fields = ['id', 'empresa', 'criado_em', 'atualizado_em']

class FuncionarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Funcionario
        fields = [
            'id', 'nome_completo', 'cpf', 'rg', 'data_nascimento', 'estado_civil', 
            'sexo', 'email', 'telefone', 'telefone_celular', 'cep', 'logradouro', 
            'numero', 'complemento', 'bairro', 'municipio', 'uf', 'ctps', 'pis', 
            'titulo_eleitor', 'reservista', 'banco', 'agencia', 'conta', 'tipo_conta', 
            'dependentes', 'empresa', 'ativo', 'contrato_ativo_detail', 
            'total_horas_extras_mes', 'possui_pendencias_documentais'
        ]
        read_only_fields = ['id', 'empresa', 'criado_em', 'atualizado_em']
        extra_kwargs = {
            'cpf': {'validators': []}, # Remove default unique validator if any, handled by custom validation
        }

    def validate_cpf(self, value):
        if not validar_cpf(value):
            raise serializers.ValidationError("CPF inválido.")
        # Verifica se já existe um funcionário com este CPF na mesma empresa (multi-tenancy)
        empresa = self.context['request'].user.empresa_ativa
        if Funcionario.objects.filter(empresa=empresa, cpf=value).exists():
            # Se for uma atualização e o CPF pertencer ao próprio funcionário, permite
            if self.instance and self.instance.cpf == value:
                pass
            else:
                raise serializers.ValidationError("Já existe um funcionário com este CPF nesta empresa.")
        return value

    def get_contrato_ativo_detail(self, obj):
        contrato = obj.contratos.filter(ativo=True).first()
        if contrato:
            return {
                'id': contrato.id,
                'cargo_detail': {
                    'nome': contrato.cargo.nome,
                    'cbo': contrato.cargo.cbo
                },
                'departamento_detail': {
                    'nome': contrato.departamento.nome if contrato.departamento else None
                },
                'salario_base': contrato.salario_base,
                'data_inicio': contrato.data_inicio
            }
        return None

    contrato_ativo_detail = serializers.SerializerMethodField(read_only=True)

    # Adicionando contadores ou resumos para o eSocial/Gestão
    total_horas_extras_mes = serializers.SerializerMethodField(read_only=True)
    possui_pendencias_documentais = serializers.SerializerMethodField(read_only=True)

    def get_total_horas_extras_mes(self, obj):
        from django.utils import timezone
        from django.db.models import Sum
        hoje = timezone.now().date()
        total = obj.registros_ponto.filter(
            data__month=hoje.month, 
            data__year=hoje.year
        ).aggregate(total=Sum('horas_extras'))['total'] or 0
        return total

    def get_possui_pendencias_documentais(self, obj):
        # Exemplo: Se não tiver contrato ou termo de responsabilidade
        tipos_subidos = obj.documentos.values_list('tipo', flat=True)
        return 'CONTRATO' not in tipos_subidos

class ContratoTrabalhoSerializer(serializers.ModelSerializer):
    cargo_detail = CargoSerializer(source='cargo', read_only=True)
    departamento_detail = DepartamentoSerializer(source='departamento', read_only=True)
    funcionario_detail = FuncionarioSerializer(source='funcionario', read_only=True)

    class Meta:
        model = ContratoTrabalho
        fields = '__all__'
        read_only_fields = ['id', 'empresa', 'criado_em', 'atualizado_em']

class FolhaPagamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = FolhaPagamento
        fields = '__all__'
        read_only_fields = ['id', 'empresa', 'data_processamento', 'status', 'criado_em', 'atualizado_em']

class HoleriteFuncionarioSerializer(serializers.ModelSerializer):
    funcionario_detail = FuncionarioSerializer(source='funcionario', read_only=True)
    folha_pagamento_detail = FolhaPagamentoSerializer(source='folha_pagamento', read_only=True)

    class Meta:
        model = HoleriteFuncionario
        fields = '__all__'
        read_only_fields = [
            'id', 'empresa', 'salario_bruto', 'valor_horas_extras_50', 'valor_horas_extras_100',
            'outros_proventos', 'total_proventos', 'desconto_inss', 'desconto_irrf',
            'desconto_fgts', 'outros_descontos', 'total_descontos', 'liquido_receber',
            'base_calculo_inss', 'base_calculo_irrf', 'base_calculo_fgts',
            'pdf_holerite', 'criado_em', 'atualizado_em'
        ]
class RegistroPontoSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegistroPonto
        fields = '__all__'
        read_only_fields = ['id', 'empresa', 'criado_em', 'atualizado_em']

class JustificativaPontoSerializer(serializers.ModelSerializer):
    class Meta:
        model = JustificativaPonto
        fields = '__all__'
        read_only_fields = ['id', 'empresa', 'criado_em', 'atualizado_em']

class DocumentoFuncionarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentoFuncionario
        fields = '__all__'
        read_only_fields = ['id', 'empresa', 'data_upload', 'criado_em', 'atualizado_em']
