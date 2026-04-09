from rest_framework import serializers

from backend.apps.core.utils import obter_empresa_ativa_ou_erro

from .models import ChecklistCompetencia, DocumentoRecebido, LoteExportacaoQuestor, Pendencia, PortalCliente
from .services import calcular_hash_arquivo, obter_ou_criar_checklist, sincronizar_pendencias_documento, validar_documento


class PortalClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = PortalCliente
        fields = '__all__'
        read_only_fields = ['id', 'empresa', 'criado_em', 'atualizado_em']


class ChecklistCompetenciaSerializer(serializers.ModelSerializer):
    total_documentos = serializers.SerializerMethodField()
    total_pendencias_abertas = serializers.SerializerMethodField()

    class Meta:
        model = ChecklistCompetencia
        fields = '__all__'
        read_only_fields = ['id', 'empresa', 'criado_em', 'atualizado_em', 'total_documentos', 'total_pendencias_abertas']

    def get_total_documentos(self, obj):
        return obj.documentos.count()

    def get_total_pendencias_abertas(self, obj):
        return obj.pendencias.exclude(status='RESOLVIDA').count()


class PendenciaSerializer(serializers.ModelSerializer):
    checklist_detail = ChecklistCompetenciaSerializer(source='checklist', read_only=True)

    class Meta:
        model = Pendencia
        fields = '__all__'
        read_only_fields = ['id', 'empresa', 'criado_em', 'atualizado_em', 'checklist_detail']


class DocumentoRecebidoSerializer(serializers.ModelSerializer):
    checklist_detail = ChecklistCompetenciaSerializer(source='checklist', read_only=True)
    arquivo_nome = serializers.SerializerMethodField()
    portal_cliente_slug = serializers.CharField(source='portal_cliente.slug', read_only=True)

    class Meta:
        model = DocumentoRecebido
        fields = '__all__'
        read_only_fields = [
            'id', 'empresa', 'hash_arquivo', 'status', 'log_validacao',
            'criado_em', 'atualizado_em', 'checklist', 'checklist_detail', 'arquivo_nome', 'portal_cliente_slug'
        ]

    def get_arquivo_nome(self, obj):
        return obj.arquivo.name.split('/')[-1] if obj.arquivo else None

    def validate(self, attrs):
        empresa = obter_empresa_ativa_ou_erro(self.context['request'].user)

        for related_field in ('funcionario', 'contrato_trabalho', 'nota_fiscal', 'portal_cliente'):
            related_obj = attrs.get(related_field)
            if related_obj and getattr(related_obj, 'empresa_id', None) != empresa.id:
                raise serializers.ValidationError({related_field: 'O registro vinculado não pertence à empresa ativa.'})

        return attrs

    def create(self, validated_data):
        empresa = obter_empresa_ativa_ou_erro(self.context['request'].user)
        arquivo = validated_data['arquivo']
        validated_data['empresa'] = empresa
        validated_data['hash_arquivo'] = calcular_hash_arquivo(arquivo)
        validated_data['competencia'] = validated_data['competencia'].replace(day=1)

        checklist = obter_ou_criar_checklist(
            empresa,
            validated_data['competencia'],
            validated_data['tipo_documento'],
        )
        validated_data['checklist'] = checklist

        status, logs = validar_documento(validated_data)
        validated_data['status'] = status
        validated_data['log_validacao'] = logs

        documento = super().create(validated_data)
        sincronizar_pendencias_documento(documento)
        return documento


class LoteExportacaoQuestorSerializer(serializers.ModelSerializer):
    download_url = serializers.SerializerMethodField()

    class Meta:
        model = LoteExportacaoQuestor
        fields = '__all__'
        read_only_fields = ['id', 'empresa', 'arquivo_exportado', 'resumo', 'processado_em', 'criado_em', 'atualizado_em', 'download_url']

    def get_download_url(self, obj):
        request = self.context.get('request')
        if not request:
            return None
        return request.build_absolute_uri(f'/api/intake/lotes/{obj.id}/download/')
