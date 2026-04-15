from rest_framework import generics, status, viewsets, filters
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.http import FileResponse, Http404

from backend.apps.core.permissions import IsBackofficeCompany, IsIntakeClientCompany
from backend.apps.core.utils import obter_empresa_ativa_ou_erro

from .models import ChecklistCompetencia, DocumentoRecebido, LoteExportacaoQuestor, Pendencia, PortalCliente
from .serializers import (
    ChecklistCompetenciaSerializer,
    ClientePortalConfigSerializer,
    ClienteRecebimentoSerializer,
    DocumentoRecebidoSerializer,
    LoteExportacaoQuestorSerializer,
    PendenciaSerializer,
    PortalClienteSerializer,
)
from .services import gerar_lote_questor, parse_competencia, sincronizar_pendencias_documento


class PortalClienteViewSet(viewsets.ModelViewSet):
    queryset = PortalCliente.objects.all()
    serializer_class = PortalClienteSerializer
    permission_classes = [IsBackofficeCompany]

    def get_queryset(self):
        empresa = obter_empresa_ativa_ou_erro(self.request.user)
        return self.queryset.filter(empresa=empresa, ativo=True)

    def perform_create(self, serializer):
        serializer.save(empresa=obter_empresa_ativa_ou_erro(self.request.user))


class DocumentoRecebidoViewSet(viewsets.ModelViewSet):
    queryset = DocumentoRecebido.objects.all()
    serializer_class = DocumentoRecebidoSerializer
    permission_classes = [IsBackofficeCompany]
    parser_classes = [MultiPartParser, FormParser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['status', 'tipo_documento', 'competencia']
    search_fields = ['titulo', 'observacoes']

    def get_queryset(self):
        empresa = obter_empresa_ativa_ou_erro(self.request.user)
        return self.queryset.filter(empresa=empresa, ativo=True)

    def perform_destroy(self, instance):
        instance.soft_delete()


class ChecklistCompetenciaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ChecklistCompetencia.objects.all()
    serializer_class = ChecklistCompetenciaSerializer
    permission_classes = [IsBackofficeCompany]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['competencia', 'modulo', 'status']

    def get_queryset(self):
        empresa = obter_empresa_ativa_ou_erro(self.request.user)
        return self.queryset.filter(empresa=empresa, ativo=True)


class PendenciaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Pendencia.objects.all()
    serializer_class = PendenciaSerializer
    permission_classes = [IsBackofficeCompany]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['status', 'severidade', 'checklist__competencia']
    search_fields = ['titulo', 'descricao']

    def get_queryset(self):
        empresa = obter_empresa_ativa_ou_erro(self.request.user)
        return self.queryset.filter(empresa=empresa, ativo=True)


class LoteExportacaoQuestorViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = LoteExportacaoQuestor.objects.all()
    serializer_class = LoteExportacaoQuestorSerializer
    permission_classes = [IsBackofficeCompany]

    def get_queryset(self):
        empresa = obter_empresa_ativa_ou_erro(self.request.user)
        return self.queryset.filter(empresa=empresa, ativo=True)

    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        lote = self.get_object()
        if not lote.arquivo_exportado:
            raise Http404('Arquivo de exportação não encontrado.')

        return FileResponse(
            lote.arquivo_exportado.open('rb'),
            as_attachment=True,
            filename=lote.arquivo_exportado.name.split('/')[-1],
        )


class ClientePortalConfigViewSet(viewsets.ReadOnlyModelViewSet):
    """GET /api/intake/cliente/portal/<slug>/ — configuração do portal."""
    permission_classes = [IsIntakeClientCompany]
    serializer_class = ClientePortalConfigSerializer
    lookup_field = 'slug'

    def get_queryset(self):
        empresa = obter_empresa_ativa_ou_erro(self.request.user)
        return PortalCliente.objects.filter(empresa=empresa, ativo=True)


class ClienteRecebimentoViewSet(viewsets.ModelViewSet):
    """GET/POST /api/intake/cliente/recebimentos/ — envio/listagem pelo cliente."""
    permission_classes = [IsIntakeClientCompany]
    serializer_class = ClienteRecebimentoSerializer
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        empresa = obter_empresa_ativa_ou_erro(self.request.user)
        return DocumentoRecebido.objects.filter(
            empresa=empresa,
            enviado_por=self.request.user,
            ativo=True,
        ).order_by('-criado_em')

    def perform_create(self, serializer):
        empresa = obter_empresa_ativa_ou_erro(self.request.user)
        portal = PortalCliente.objects.filter(empresa=empresa, ativo=True).first()
        serializer.save(
            empresa=empresa,
            enviado_por=self.request.user,
            origem_upload='CLIENTE',
            portal_cliente=portal,
            status='NOVO',
        )


class ConfirmarRecebimentoView(generics.GenericAPIView):
    permission_classes = [IsBackofficeCompany]
    serializer_class = DocumentoRecebidoSerializer

    def post(self, request, *args, **kwargs):
        empresa = obter_empresa_ativa_ou_erro(request.user)
        documento_id = request.data.get('documento_id')
        status_documento = request.data.get('status')
        observacoes = request.data.get('observacoes')

        if status_documento not in {'VALIDADO', 'REPROVADO'}:
            return Response({'error': 'Status inválido. Use VALIDADO ou REPROVADO.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            documento = DocumentoRecebido.objects.get(id=documento_id, empresa=empresa, ativo=True)
        except DocumentoRecebido.DoesNotExist:
            return Response({'error': 'Documento não encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        documento.status = status_documento
        if observacoes:
            logs = documento.log_validacao or []
            logs.append({'nivel': 'info', 'mensagem': observacoes})
            documento.log_validacao = logs
            documento.observacoes = observacoes
        documento.save(update_fields=['status', 'log_validacao', 'observacoes', 'atualizado_em'])
        sincronizar_pendencias_documento(documento)

        serializer = self.get_serializer(documento, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class ExportarQuestorView(generics.GenericAPIView):
    permission_classes = [IsBackofficeCompany]
    serializer_class = LoteExportacaoQuestorSerializer

    def post(self, request, *args, **kwargs):
        empresa = obter_empresa_ativa_ou_erro(request.user)
        competencia_value = request.data.get('competencia')

        if not competencia_value:
            return Response({'error': 'Competência é obrigatória.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            competencia = parse_competencia(competencia_value)
        except ValueError as exc:
            return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        lote = gerar_lote_questor(empresa, competencia)
        serializer = self.get_serializer(lote, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)
