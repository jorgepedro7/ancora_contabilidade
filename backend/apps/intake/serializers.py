from rest_framework import serializers

from backend.apps.core.utils import obter_empresa_ativa_ou_erro

from .models import ChecklistCompetencia, DocumentoRecebido, LoteExportacaoQuestor, Pendencia, PortalCliente
from .services import calcular_hash_arquivo, obter_ou_criar_checklist, sincronizar_pendencias_documento, validar_documento


MAX_DOCUMENTO_SIZE = 10 * 1024 * 1024
ALLOWED_DOCUMENT_EXTENSIONS = {
    '.pdf', '.xml', '.csv', '.txt', '.zip', '.xls', '.xlsx', '.jpg', '.jpeg', '.png',
}
ALLOWED_DOCUMENT_CONTENT_TYPES = {
    'application/pdf',
    'application/xml',
    'text/xml',
    'text/plain',
    'text/csv',
    'application/zip',
    'application/x-zip-compressed',
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'image/jpeg',
    'image/png',
}


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

    def validate_arquivo(self, value):
        if not value:
            raise serializers.ValidationError('Arquivo é obrigatório.')

        filename = (getattr(value, 'name', '') or '').lower()
        if not any(filename.endswith(extension) for extension in ALLOWED_DOCUMENT_EXTENSIONS):
            raise serializers.ValidationError('Tipo de arquivo não permitido para o intake.')

        if getattr(value, 'size', 0) > MAX_DOCUMENTO_SIZE:
            raise serializers.ValidationError('O arquivo excede o tamanho máximo permitido de 10 MB.')

        content_type = getattr(value, 'content_type', None)
        if content_type and content_type not in ALLOWED_DOCUMENT_CONTENT_TYPES:
            raise serializers.ValidationError('Content-Type do arquivo não é aceito pelo intake.')

        return value

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
