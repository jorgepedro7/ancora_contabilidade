from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from backend.apps.core.models import PerfilPermissao
from backend.apps.core.utils import (
    buscar_cep,
    garantir_empresa_padrao,
    obter_empresas_acessiveis,
)
from .models import Empresa
from .serializers import EmpresaSerializer


class EmpresaViewSet(viewsets.ModelViewSet):
    queryset = Empresa.objects.all()
    serializer_class = EmpresaSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['regime_tributario', 'uf', 'ativo', 'porte']
    search_fields = ['razao_social', 'nome_fantasia', 'cnpj']

    def get_queryset(self):
        return obter_empresas_acessiveis(self.request.user).order_by('nome_fantasia', 'razao_social')

    def perform_create(self, serializer):
        empresa = serializer.save()
        PerfilPermissao.objects.get_or_create(
            usuario=self.request.user,
            empresa=empresa,
            defaults={'perfil': 'ADMIN'},
        )

        if not self.request.user.empresa_ativa_id:
            self.request.user.empresa_ativa = empresa
            self.request.user.save(update_fields=['empresa_ativa'])

    def perform_destroy(self, instance):
        instance.soft_delete()

        if self.request.user.empresa_ativa_id == instance.id:
            self.request.user.empresa_ativa = None
            self.request.user.save(update_fields=['empresa_ativa'])
            garantir_empresa_padrao(self.request.user)

    @action(detail=True, methods=['post'])
    def selecionar(self, request, pk=None):
        empresa = self.get_object()
        request.user.empresa_ativa = empresa
        request.user.save(update_fields=['empresa_ativa'])
        return Response({'status': 'Empresa selecionada', 'empresa_id': str(empresa.id)}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='desselecionar')
    def desselecionar(self, request):
        request.user.empresa_ativa = None
        request.user.save(update_fields=['empresa_ativa'])
        return Response({'status': 'Empresa desmarcada', 'empresa_id': None}, status=status.HTTP_200_OK)

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
