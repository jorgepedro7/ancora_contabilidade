from rest_framework import viewsets, filters, generics, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from backend.apps.core.permissions import IsActiveCompany
from .models import LancamentoContabil, PartidaLancamento
from .serializers import LancamentoContabilSerializer, PartidaLancamentoSerializer
from backend.apps.financeiro.models import PlanoContas
from django.db.models import Sum
from datetime import date

class BaseContabilViewSet(viewsets.ModelViewSet):
    permission_classes = [IsActiveCompany]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    
    def get_queryset(self):
        if self.request.user.is_authenticated and self.request.user.empresa_ativa:
            return self.queryset.filter(empresa=self.request.user.empresa_ativa, ativo=True)
        return self.queryset.none()

    def perform_create(self, serializer):
        serializer.save(empresa=self.request.user.empresa_ativa)

    def perform_destroy(self, instance):
        instance.soft_delete()

class LancamentoContabilViewSet(BaseContabilViewSet):
    queryset = LancamentoContabil.objects.all()
    serializer_class = LancamentoContabilSerializer
    filterset_fields = ['data_lancamento', 'tipo_lancamento', 'ativo']
    search_fields = ['historico']

    def get_queryset(self):
        # Para evitar N+1 queries ao listar lançamentos com partidas
        return super().get_queryset().prefetch_related('partidas')

class PartidaLancamentoViewSet(BaseContabilViewSet):
    queryset = PartidaLancamento.objects.all()
    serializer_class = PartidaLancamentoSerializer
    filterset_fields = ['lancamento', 'conta_contabil', 'tipo_partida', 'ativo']
    search_fields = ['historico_complementar']

class DREView(generics.GenericAPIView):
    permission_classes = [IsActiveCompany]

    def get(self, request, *args, **kwargs):
        empresa = request.user.empresa_ativa
        data_inicio_str = request.query_params.get('data_inicio')
        data_fim_str = request.query_params.get('data_fim')

        if not data_inicio_str or not data_fim_str:
            return Response({'error': 'Os parâmetros data_inicio e data_fim são obrigatórios.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            data_inicio = date.fromisoformat(data_inicio_str)
            data_fim = date.fromisoformat(data_fim_str)
        except ValueError:
            return Response({'error': 'Formato de data inválido. Use AAAA-MM-DD.'}, status=status.HTTP_400_BAD_REQUEST)

        # Lógica simplificada para DRE
        # Receitas
        contas_receita = PlanoContas.objects.filter(empresa=empresa, tipo_conta='RC')
        total_receitas = PartidaLancamento.objects.filter(
            lancamento__empresa=empresa,
            lancamento__data_lancamento__range=(data_inicio, data_fim),
            conta_contabil__in=contas_receita,
            tipo_partida='C' # Receitas são geralmente Crédito
        ).aggregate(sum_valor=Sum('valor'))['sum_valor'] or 0

        # Despesas
        contas_despesa = PlanoContas.objects.filter(empresa=empresa, tipo_conta='DS')
        total_despesas = PartidaLancamento.objects.filter(
            lancamento__empresa=empresa,
            lancamento__data_lancamento__range=(data_inicio, data_fim),
            conta_contabil__in=contas_despesa,
            tipo_partida='D' # Despesas são geralmente Débito
        ).aggregate(sum_valor=Sum('valor'))['sum_valor'] or 0
        
        resultado_liquido = total_receitas - total_despesas

        data = {
            'periodo_inicio': data_inicio.isoformat(),
            'periodo_fim': data_fim.isoformat(),
            'total_receitas': total_receitas,
            'total_despesas': total_despesas,
            'resultado_liquido': resultado_liquido
        }
        return Response(data, status=status.HTTP_200_OK)

class BalancoPatrimonialView(generics.GenericAPIView):
    permission_classes = [IsActiveCompany]

    def get(self, request, *args, **kwargs):
        empresa = request.user.empresa_ativa
        data_base_str = request.query_params.get('data_base')

        if not data_base_str:
            return Response({'error': 'O parâmetro data_base é obrigatório.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            data_base = date.fromisoformat(data_base_str)
        except ValueError:
            return Response({'error': 'Formato de data inválido. Use AAAA-MM-DD.'}, status=status.HTTP_400_BAD_REQUEST)

        # Lógica simplificada para Balanço Patrimonial
        # Ativo
        contas_ativo = PlanoContas.objects.filter(empresa=empresa, tipo_conta='AT')
        total_ativo = PartidaLancamento.objects.filter(
            lancamento__empresa=empresa,
            lancamento__data_lancamento__lte=data_base,
            conta_contabil__in=contas_ativo
        ).aggregate(
            sum_debitos=Sum('valor', filter=models.Q(tipo_partida='D')),
            sum_creditos=Sum('valor', filter=models.Q(tipo_partida='C'))
        )
        valor_ativo = (total_ativo['sum_debitos'] or 0) - (total_ativo['sum_creditos'] or 0)

        # Passivo
        contas_passivo = PlanoContas.objects.filter(empresa=empresa, tipo_conta='PA')
        total_passivo = PartidaLancamento.objects.filter(
            lancamento__empresa=empresa,
            lancamento__data_lancamento__lte=data_base,
            conta_contabil__in=contas_passivo
        ).aggregate(
            sum_debitos=Sum('valor', filter=models.Q(tipo_partida='D')),
            sum_creditos=Sum('valor', filter=models.Q(tipo_partida='C'))
        )
        valor_passivo = (total_passivo['sum_creditos'] or 0) - (total_passivo['sum_debitos'] or 0)

        # Patrimônio Líquido
        contas_patrimonio_liquido = PlanoContas.objects.filter(empresa=empresa, tipo_conta='PL')
        total_patrimonio_liquido = PartidaLancamento.objects.filter(
            lancamento__empresa=empresa,
            lancamento__data_lancamento__lte=data_base,
            conta_contabil__in=contas_patrimonio_liquido
        ).aggregate(
            sum_debitos=Sum('valor', filter=models.Q(tipo_partida='D')),
            sum_creditos=Sum('valor', filter=models.Q(tipo_partida='C'))
        )
        valor_patrimonio_liquido = (total_patrimonio_liquido['sum_creditos'] or 0) - (total_patrimonio_liquido['sum_debitos'] or 0)

        data = {
            'data_base': data_base.isoformat(),
            'total_ativo': valor_ativo,
            'total_passivo': valor_passivo,
            'total_patrimonio_liquido': valor_patrimonio_liquido,
            'balanco_patrimonial_quadra': valor_ativo - (valor_passivo + valor_patrimonio_liquido) # Deve ser zero em balanço ideal
        }
        return Response(data, status=status.HTTP_200_OK)
