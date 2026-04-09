from rest_framework import viewsets, filters, generics, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from backend.apps.core.permissions import IsActiveCompany
from backend.apps.core.utils import obter_empresa_ativa_ou_erro
from .models import ContaBancaria, PlanoContas, ContaAPagar, ContaAReceber, MovimentacaoFinanceira
from .serializers import ContaBancariaSerializer, PlanoContasSerializer, ContaAPagarSerializer, ContaAReceberSerializer, MovimentacaoFinanceiraSerializer
from django.db.models import Sum
from datetime import date, timedelta

class BaseFinanceiroViewSet(viewsets.ModelViewSet):
    permission_classes = [IsActiveCompany]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    
    def get_queryset(self):
        if self.request.user.is_authenticated and self.request.user.empresa_ativa:
            return self.queryset.filter(empresa=self.request.user.empresa_ativa, ativo=True)
        return self.queryset.none()

    def perform_create(self, serializer):
        serializer.save(empresa=obter_empresa_ativa_ou_erro(self.request.user))

    def perform_destroy(self, instance):
        instance.soft_delete()

class ContaBancariaViewSet(BaseFinanceiroViewSet):
    queryset = ContaBancaria.objects.all()
    serializer_class = ContaBancariaSerializer
    filterset_fields = ['tipo_conta', 'ativo']
    search_fields = ['descricao']

class PlanoContasViewSet(BaseFinanceiroViewSet):
    queryset = PlanoContas.objects.all()
    serializer_class = PlanoContasSerializer
    filterset_fields = ['tipo_conta', 'ativo', 'conta_pai']
    search_fields = ['codigo', 'descricao']

class ContaAPagarViewSet(BaseFinanceiroViewSet):
    queryset = ContaAPagar.objects.all()
    serializer_class = ContaAPagarSerializer
    filterset_fields = ['status', 'data_vencimento', 'fornecedor', 'conta_contabil', 'ativo']
    search_fields = ['descricao', 'fornecedor__nome_razao_social']

    @action(detail=True, methods=['post'])
    def pagar(self, request, pk=None):
        conta_a_pagar = self.get_object()
        valor = request.data.get('valor')
        conta_bancaria_id = request.data.get('conta_bancaria_id')

        if not valor or not conta_bancaria_id:
            return Response({'error': 'Valor e ID da conta bancária são obrigatórios.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            valor = float(valor)
            conta_bancaria = ContaBancaria.objects.get(id=conta_bancaria_id, empresa=self.request.user.empresa_ativa)
            conta_a_pagar.pagar(valor, conta_bancaria)
            return Response(self.get_serializer(conta_a_pagar).data, status=status.HTTP_200_OK)
        except (ValueError, ContaBancaria.DoesNotExist) as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class ContaAReceberViewSet(BaseFinanceiroViewSet):
    queryset = ContaAReceber.objects.all()
    serializer_class = ContaAReceberSerializer
    filterset_fields = ['status', 'data_vencimento', 'cliente', 'conta_contabil', 'ativo']
    search_fields = ['descricao', 'cliente__nome_razao_social']

    @action(detail=True, methods=['post'])
    def receber(self, request, pk=None):
        conta_a_receber = self.get_object()
        valor = request.data.get('valor')
        conta_bancaria_id = request.data.get('conta_bancaria_id')

        if not valor or not conta_bancaria_id:
            return Response({'error': 'Valor e ID da conta bancária são obrigatórios.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            valor = float(valor)
            conta_bancaria = ContaBancaria.objects.get(id=conta_bancaria_id, empresa=self.request.user.empresa_ativa)
            conta_a_receber.receber(valor, conta_bancaria)
            return Response(self.get_serializer(conta_a_receber).data, status=status.HTTP_200_OK)
        except (ValueError, ContaBancaria.DoesNotExist) as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class MovimentacaoFinanceiraViewSet(BaseFinanceiroViewSet):
    queryset = MovimentacaoFinanceira.objects.all()
    serializer_class = MovimentacaoFinanceiraSerializer
    filterset_fields = ['tipo_movimentacao', 'conta_bancaria', 'conta_contabil', 'data_movimentacao']
    search_fields = ['descricao']

class FluxoCaixaView(generics.GenericAPIView):
    permission_classes = [IsActiveCompany]

    def get(self, request, *args, **kwargs):
        empresa = obter_empresa_ativa_ou_erro(request.user)
        data_inicio_str = request.query_params.get('data_inicio')
        data_fim_str = request.query_params.get('data_fim')

        if not data_inicio_str or not data_fim_str:
            return Response({'error': 'Os parâmetros data_inicio e data_fim são obrigatórios.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            data_inicio = date.fromisoformat(data_inicio_str)
            data_fim = date.fromisoformat(data_fim_str)
        except ValueError:
            return Response({'error': 'Formato de data inválido. Use AAAA-MM-DD.'}, status=status.HTTP_400_BAD_REQUEST)

        movimentacoes = MovimentacaoFinanceira.objects.filter(
            empresa=empresa,
            data_movimentacao__range=(data_inicio, data_fim)
        )

        entradas = movimentacoes.filter(tipo_movimentacao='E').aggregate(total=Sum('valor'))['total'] or 0
        saidas = movimentacoes.filter(tipo_movimentacao='S').aggregate(total=Sum('valor'))['total'] or 0
        transferencias_entrada = movimentacoes.filter(tipo_movimentacao='T').aggregate(total=Sum('valor'))['total'] or 0
        transferencias_saida = movimentacoes.filter(tipo_movimentacao='T').aggregate(total=Sum('valor'))['total'] or 0 # Para balanço, transferências saem de uma conta e entram em outra. Para fluxo de caixa, elas se anulam se considerarmos o total da empresa.

        saldo_inicial = ContaBancaria.objects.filter(empresa=empresa).aggregate(total=Sum('saldo_inicial'))['total'] or 0
        # O calculo de saldo inicial e final para o periodo de fluxo de caixa é mais complexo
        # e precisa considerar o saldo das contas antes do data_inicio
        # Por simplicidade, faremos um calculo básico aqui:
        
        # Saldo inicial ajustado ao período
        saldo_inicial_periodo = 0 # Isso precisaria de lógica mais avançada para buscar o saldo acumulado antes do período
        # Fora do escopo para uma primeira versão de fluxo de caixa simples

        saldo_final_contas = ContaBancaria.objects.filter(empresa=empresa).aggregate(total=Sum('saldo_atual'))['total'] or 0

        fluxo_caixa_liquido = entradas - saidas

        data = {
            'data_inicio': data_inicio.isoformat(),
            'data_fim': data_fim.isoformat(),
            'total_entradas': entradas,
            'total_saidas': saidas,
            'fluxo_caixa_liquido': fluxo_caixa_liquido,
            'saldo_final_contas_atuais': saldo_final_contas, # Saldo atual das contas bancarias da empresa
        }
        return Response(data, status=status.HTTP_200_OK)

class ContasVencendoHojeView(generics.ListAPIView):
    permission_classes = [IsActiveCompany]

    def get(self, request, *args, **kwargs):
        empresa = obter_empresa_ativa_ou_erro(request.user)
        today = date.today()
        five_days_from_now = today + timedelta(days=5)

        contas_a_pagar = ContaAPagar.objects.filter(
            empresa=empresa,
            data_vencimento__range=(today, five_days_from_now),
            status='ABERTA'
        ).select_related('fornecedor')
        
        contas_a_receber = ContaAReceber.objects.filter(
            empresa=empresa,
            data_vencimento__range=(today, five_days_from_now),
            status='ABERTA'
        ).select_related('cliente')
        
        contas_a_pagar_serializer = ContaAPagarSerializer(contas_a_pagar, many=True)
        contas_a_receber_serializer = ContaAReceberSerializer(contas_a_receber, many=True)

        return Response({
            'contas_a_pagar_hoje': contas_a_pagar_serializer.data,
            'contas_a_receber_hoje': contas_a_receber_serializer.data,
        }, status=status.HTTP_200_OK)
