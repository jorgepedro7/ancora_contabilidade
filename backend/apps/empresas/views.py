from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from backend.apps.core.permissions import IsActiveCompany
from backend.apps.core.utils import buscar_cep
from .models import Empresa
from .serializers import EmpresaSerializer

class EmpresaViewSet(viewsets.ModelViewSet):
    queryset = Empresa.objects.all()
    serializer_class = EmpresaSerializer
    permission_classes = [IsActiveCompany]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['regime_tributario', 'uf', 'ativo', 'porte']
    search_fields = ['razao_social', 'nome_fantasia', 'cnpj']

    def get_queryset(self):
        # Apenas superusuários podem ver todas as empresas
        if self.request.user.is_superuser:
            return Empresa.objects.all()
        
        # O usuário deve ver todas as empresas que ele tem permissão de acesso,
        # independentemente de qual está "ativa" no momento.
        return Empresa.objects.filter(
            id__in=self.request.user.perfis_permissoes.values_list('empresa_id', flat=True),
            ativo=True
        )

    def perform_destroy(self, instance):
        instance.soft_delete() # Soft delete instead of hard delete

    @action(detail=True, methods=['post'])
    def selecionar(self, request, pk=None):
        empresa = self.get_object()
        request.user.empresa_ativa = empresa
        request.user.save()
        return Response({'status': 'Empresa selecionada', 'empresa_id': str(empresa.id)}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def buscar_cep(self, request):
        cep = request.data.get('cep')
        if not cep:
            return Response({'error': 'CEP é obrigatório.'}, status=status.HTTP_400_BAD_REQUEST)
        
        endereco_data = buscar_cep(cep)
        if endereco_data:
            return Response(endereco_data, status=status.HTTP_200_OK)
        return Response({'error': 'CEP não encontrado ou inválido.'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['get'])
    def resumo_fiscal(self, request, pk=None):
        empresa = self.get_object()
        # Aqui, você buscará dados fiscais resumidos da empresa
        # Por exemplo, número de NF-e emitidas no mês, status, etc.
        # Por enquanto, apenas um placeholder
        data = {
            'empresa_id': str(empresa.id),
            'nome_fantasia': empresa.nome_fantasia,
            'cnpj': empresa.cnpj,
            'nfe_emitidas_mes': 0, # Placeholder
            'nfe_pendentes': 0,    # Placeholder
            'certificado_vencido': empresa.certificado_vencido,
            'regime_tributario': empresa.get_regime_tributario_display(),
        }
        return Response(data, status=status.HTTP_200_OK)
