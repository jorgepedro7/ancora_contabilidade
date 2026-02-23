from django.db import models
from django.db.models import Sum, F
from backend.apps.core.models import ModelBaseEmpresa
from backend.apps.cadastros.models import Cliente, Fornecedor
from django.db import transaction
from decimal import Decimal
from datetime import date

class ContaBancaria(ModelBaseEmpresa):
    TIPO_CONTA_CHOICES = [
        ('CC', 'Conta Corrente'),
        ('CP', 'Conta Poupança'),
        ('APL', 'Aplicação Financeira'),
        ('CX', 'Caixa Interno'),
    ]

    descricao = models.CharField(max_length=255, verbose_name="Descrição da Conta")
    tipo_conta = models.CharField(max_length=3, choices=TIPO_CONTA_CHOICES, default='CC', verbose_name="Tipo de Conta")
    saldo_inicial = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, verbose_name="Saldo Inicial")
    saldo_atual = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, verbose_name="Saldo Atual")

    class Meta:
        verbose_name = "Conta Bancária/Caixa"
        verbose_name_plural = "Contas Bancárias/Caixa"
        unique_together = ('empresa', 'descricao')

    def __str__(self):
        return f"{self.descricao} ({self.get_tipo_conta_display()})"

class PlanoContas(ModelBaseEmpresa):
    TIPO_CHOICES = [
        ('RC', 'Receita'),
        ('DS', 'Despesa'),
        ('AT', 'Ativo'),
        ('PA', 'Passivo'),
        ('PL', 'Patrimônio Líquido'),
    ]

    codigo = models.CharField(max_length=20, verbose_name="Código da Conta")
    descricao = models.CharField(max_length=255, verbose_name="Descrição da Conta")
    tipo_conta = models.CharField(max_length=2, choices=TIPO_CHOICES, verbose_name="Tipo da Conta")
    conta_pai = models.ForeignKey('self', on_delete=models.SET_NULL, blank=True, null=True, related_name='sub_contas')

    class Meta:
        verbose_name = "Plano de Contas"
        verbose_name_plural = "Plano de Contas"
        unique_together = ('empresa', 'codigo')
        ordering = ['codigo']

    def __str__(self):
        return f"{self.codigo} - {self.descricao}"

class ContaBase(ModelBaseEmpresa):
    STATUS_CHOICES = [
        ('ABERTA', 'Aberta'),
        ('PARCIAL', 'Paga/Recebida Parcialmente'),
        ('PAGA_RECEBIDA', 'Paga/Recebida'),
        ('CANCELADA', 'Cancelada'),
    ]

    descricao = models.CharField(max_length=255, verbose_name="Descrição")
    valor_total = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Valor Total")
    data_vencimento = models.DateField(verbose_name="Data de Vencimento")
    data_liquidacao = models.DateField(blank=True, null=True, verbose_name="Data de Liquidação")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ABERTA', verbose_name="Status")
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")

    # Campos para parcelamento
    parcela_atual = models.IntegerField(default=1, verbose_name="Parcela Atual")
    total_parcelas = models.IntegerField(default=1, verbose_name="Total de Parcelas")

    # Juros, multa e desconto
    juros = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, verbose_name="Juros")
    multa = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, verbose_name="Multa")
    desconto = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, verbose_name="Desconto")

    class Meta:
        abstract = True

    @property
    def valor_saldo(self):
        # Implementado nas subclasses pois o campo de valor pago/recebido é diferente
        raise NotImplementedError

    @property
    def esta_vencida(self):
        return self.status == 'ABERTA' and self.data_vencimento < date.today()

class ContaAPagar(ContaBase):
    fornecedor = models.ForeignKey(Fornecedor, on_delete=models.PROTECT, related_name='contas_a_pagar')
    conta_contabil = models.ForeignKey(PlanoContas, on_delete=models.PROTECT, related_name='contas_a_pagar_contabil')
    valor_pago = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, verbose_name="Valor Pago")

    class Meta:
        verbose_name = "Conta a Pagar"
        verbose_name_plural = "Contas a Pagar"
    
    @property
    def valor_saldo(self):
        return self.valor_total - self.valor_pago

    @transaction.atomic
    def pagar(self, valor: Decimal, conta_bancaria: ContaBancaria):
        if self.status == 'PAGA_RECEBIDA':
            raise ValueError("Esta conta já foi paga.")
        if valor <= 0:
            raise ValueError("O valor de pagamento deve ser positivo.")
        if valor > self.valor_saldo:
            raise ValueError("Valor de pagamento excede o saldo da conta.")
        
        self.valor_pago += valor
        conta_bancaria.saldo_atual -= valor
        
        if self.valor_pago >= self.valor_total:
            self.status = 'PAGA_RECEBIDA'
            self.data_liquidacao = date.today()
        elif self.valor_pago > 0:
            self.status = 'PARCIAL'

        self.save()
        conta_bancaria.save()

        # Registrar movimentação financeira
        MovimentacaoFinanceira.objects.create(
            empresa=self.empresa,
            conta_bancaria=conta_bancaria,
            tipo_movimentacao='S', # Saída
            valor=valor,
            descricao=f"Pagamento Ref. {self.descricao} ({self.fornecedor.nome_razao_social})",
            conta_contabil=self.conta_contabil
        )


class ContaAReceber(ContaBase):
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name='contas_a_receber')
    conta_contabil = models.ForeignKey(PlanoContas, on_delete=models.PROTECT, related_name='contas_a_receber_contabil')
    valor_recebido = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, verbose_name="Valor Recebido")

    class Meta:
        verbose_name = "Conta a Receber"
        verbose_name_plural = "Contas a Receber"

    @property
    def valor_saldo(self):
        return self.valor_total - self.valor_recebido

    @transaction.atomic
    def receber(self, valor: Decimal, conta_bancaria: ContaBancaria):
        if self.status == 'PAGA_RECEBIDA':
            raise ValueError("Esta conta já foi recebida.")
        if valor <= 0:
            raise ValueError("O valor de recebimento deve ser positivo.")
        if valor > self.valor_saldo:
            raise ValueError("Valor de recebimento excede o saldo da conta.")
        
        self.valor_recebido += valor
        conta_bancaria.saldo_atual += valor
        
        if self.valor_recebido >= self.valor_total:
            self.status = 'PAGA_RECEBIDA'
            self.data_liquidacao = date.today()
        elif self.valor_recebido > 0:
            self.status = 'PARCIAL'

        self.save()
        conta_bancaria.save()

        # Registrar movimentação financeira
        MovimentacaoFinanceira.objects.create(
            empresa=self.empresa,
            conta_bancaria=conta_bancaria,
            tipo_movimentacao='E', # Entrada
            valor=valor,
            descricao=f"Recebimento Ref. {self.descricao} ({self.cliente.nome_razao_social})",
            conta_contabil=self.conta_contabil
        )

class MovimentacaoFinanceira(ModelBaseEmpresa):
    TIPO_MOVIMENTACAO_CHOICES = [
        ('E', 'Entrada'),
        ('S', 'Saída'),
        ('T', 'Transferência'),
    ]

    data_movimentacao = models.DateField(default=date.today, verbose_name="Data da Movimentação")
    tipo_movimentacao = models.CharField(max_length=1, choices=TIPO_MOVIMENTACAO_CHOICES, verbose_name="Tipo de Movimentação")
    valor = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Valor")
    descricao = models.CharField(max_length=255, blank=True, null=True, verbose_name="Descrição")
    conta_bancaria = models.ForeignKey(ContaBancaria, on_delete=models.PROTECT, related_name='movimentacoes')
    conta_contabil = models.ForeignKey(PlanoContas, on_delete=models.PROTECT, related_name='movimentacoes', blank=True, null=True)

    class Meta:
        verbose_name = "Movimentação Financeira"
        verbose_name_plural = "Movimentações Financeiras"
        ordering = ['-data_movimentacao', '-criado_em']

    def __str__(self):
        return f"{self.data_movimentacao} - {self.get_tipo_movimentacao_display()} de R$ {self.valor} em {self.conta_bancaria}"
