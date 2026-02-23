from rest_framework import viewsets, filters, generics, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from backend.apps.core.permissions import IsActiveCompany
from .models import ObrigacaoFiscal
from .serializers import ObrigacaoFiscalSerializer
from datetime import date, timedelta

class ObrigacaoFiscalViewSet(viewsets.ModelViewSet):
    queryset = ObrigacaoFiscal.objects.all()
    serializer_class = ObrigacaoFiscalSerializer
    permission_classes = [IsActiveCompany]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['tipo_obrigacao', 'status', 'data_vencimento', 'empresa']
    search_fields = ['descricao']

    def get_queryset(self):
        if self.request.user.is_authenticated and self.request.user.empresa_ativa:
            return self.queryset.filter(empresa=self.request.user.empresa_ativa, ativo=True)
        return self.queryset.none()

    def perform_create(self, serializer):
        serializer.save(empresa=self.request.user.empresa_ativa)

    def perform_destroy(self, instance):
        instance.soft_delete()

    @action(detail=False, methods=['get'])
    def vencendo_hoje(self, request):
        empresa = self.request.user.empresa_ativa
        today = date.today()
        obrigacoes = ObrigacaoFiscal.objects.filter(
            empresa=empresa,
            data_vencimento=today,
            status__in=['ABERTO', 'ATRASADO']
        )
        serializer = self.get_serializer(obrigacoes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def vencendo_proximos_dias(self, request):
        empresa = self.request.user.empresa_ativa
        dias = int(request.query_params.get('dias', 7))
        today = date.today()
        future_date = today + timedelta(days=dias)

        obrigacoes = ObrigacaoFiscal.objects.filter(
            empresa=empresa,
            data_vencimento__range=(today, future_date),
            status__in=['ABERTO']
        )
        serializer = self.get_serializer(obrigacoes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
