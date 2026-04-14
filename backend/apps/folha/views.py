from django.http import HttpResponse
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from backend.apps.core.permissions import IsBackofficeCompany
from backend.apps.core.utils import obter_empresa_ativa_ou_erro
from .models import (
    Cargo, Departamento, Funcionario, ContratoTrabalho, 
    FolhaPagamento, HoleriteFuncionario, RegistroPonto, 
    JustificativaPonto, DocumentoFuncionario
)
from .serializers import (
    CargoSerializer, DepartamentoSerializer, FuncionarioSerializer, 
    ContratoTrabalhoSerializer, FolhaPagamentoSerializer, 
    HoleriteFuncionarioSerializer, RegistroPontoSerializer,
    JustificativaPontoSerializer, DocumentoFuncionarioSerializer
)

class BaseFolhaViewSet(viewsets.ModelViewSet):
    permission_classes = [IsBackofficeCompany]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    
    def get_queryset(self):
        if self.request.user.is_authenticated and self.request.user.empresa_ativa:
            return self.queryset.filter(empresa=self.request.user.empresa_ativa, ativo=True)
        return self.queryset.none()

    def perform_create(self, serializer):
        serializer.save(empresa=obter_empresa_ativa_ou_erro(self.request.user))

    def perform_destroy(self, instance):
        instance.soft_delete()

class CargoViewSet(BaseFolhaViewSet):
    queryset = Cargo.objects.all()
    serializer_class = CargoSerializer
    filterset_fields = ['ativo']
    search_fields = ['nome', 'cbo']

class DepartamentoViewSet(BaseFolhaViewSet):
    queryset = Departamento.objects.all()
    serializer_class = DepartamentoSerializer
    filterset_fields = ['ativo']
    search_fields = ['nome', 'centro_custo']

class FuncionarioViewSet(BaseFolhaViewSet):
    queryset = Funcionario.objects.all()
    serializer_class = FuncionarioSerializer
    filterset_fields = ['estado_civil', 'sexo', 'ativo']
    search_fields = ['nome_completo', 'cpf', 'pis', 'ctps']

class ContratoTrabalhoViewSet(BaseFolhaViewSet):
    queryset = ContratoTrabalho.objects.all()
    serializer_class = ContratoTrabalhoSerializer
    filterset_fields = ['funcionario', 'cargo', 'departamento', 'tipo_contrato', 'ativo']
    search_fields = ['funcionario__nome_completo', 'cargo__nome']

class FolhaPagamentoViewSet(BaseFolhaViewSet):
    queryset = FolhaPagamento.objects.all()
    serializer_class = FolhaPagamentoSerializer
    filterset_fields = ['competencia', 'tipo_folha', 'status']
    search_fields = ['competencia']

    @action(detail=True, methods=['post'])
    def calcular(self, request, pk=None):
        folha_pagamento = self.get_object()
        empresa = obter_empresa_ativa_ou_erro(request.user)
        
        if folha_pagamento.status != 'ABERTA':
            return Response({'error': 'A folha de pagamento não pode ser calculada neste status.'}, status=status.HTTP_400_BAD_REQUEST)
        
        contratos_ativos = ContratoTrabalho.objects.filter(
            empresa=empresa,
            ativo=True,
            data_inicio__lte=folha_pagamento.competencia # Contratos ativos na competência
        )
        
        resultados_holerites = []
        for contrato in contratos_ativos:
            holerite, created = HoleriteFuncionario.objects.get_or_create(
                folha_pagamento=folha_pagamento,
                funcionario=contrato.funcionario,
                empresa=empresa
            )
            try:
                holerite.calcular()
                resultados_holerites.append(HoleriteFuncionarioSerializer(holerite).data)
            except ValueError as e:
                return Response({'error': f'Erro ao calcular holerite para {contrato.funcionario.nome_completo}: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
        
        folha_pagamento.status = 'PROCESSADA'
        folha_pagamento.save()

        return Response({
            'status': 'Folha processada com sucesso.',
            'holerites': resultados_holerites
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def fechar(self, request, pk=None):
        folha_pagamento = self.get_object()
        if folha_pagamento.status != 'PROCESSADA':
            return Response({'error': 'A folha de pagamento só pode ser fechada após processamento.'}, status=status.HTTP_400_BAD_REQUEST)
        
        folha_pagamento.status = 'FECHADA'
        folha_pagamento.save()
        return Response(self.get_serializer(folha_pagamento).data, status=status.HTTP_200_OK)

class HoleriteFuncionarioViewSet(BaseFolhaViewSet):
    queryset = HoleriteFuncionario.objects.all()
    serializer_class = HoleriteFuncionarioSerializer
    filterset_fields = ['funcionario', 'folha_pagamento', 'data_pagamento']
    search_fields = ['funcionario__nome_completo']

    @action(detail=True, methods=['get'])
    def pdf(self, request, pk=None):
        holerite = self.get_object()
        try:
            # Assumindo que você tem uma função que gera o PDF do holerite
            pdf_bytes = holerite.gerar_pdf() # Este método precisa ser implementado no model
            response = HttpResponse(pdf_bytes, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="holerite_{holerite.funcionario.nome_completo}_{holerite.folha_pagamento.competencia.strftime("%Y%m")}.pdf"'
            return response
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class RegistroPontoViewSet(BaseFolhaViewSet):
    queryset = RegistroPonto.objects.all()
    serializer_class = RegistroPontoSerializer
    filterset_fields = ['funcionario', 'data']
    search_fields = ['funcionario__nome_completo']

class JustificativaPontoViewSet(BaseFolhaViewSet):
    queryset = JustificativaPonto.objects.all()
    serializer_class = JustificativaPontoSerializer
    filterset_fields = ['funcionario', 'tipo', 'abona_ponto']
    search_fields = ['funcionario__nome_completo', 'descricao']

class DocumentoFuncionarioViewSet(BaseFolhaViewSet):
    queryset = DocumentoFuncionario.objects.all()
    serializer_class = DocumentoFuncionarioSerializer
    filterset_fields = ['funcionario', 'tipo']
    search_fields = ['funcionario__nome_completo', 'descricao']
