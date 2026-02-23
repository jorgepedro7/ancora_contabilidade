from django.db import models
from backend.apps.core.models import ModelBaseEmpresa
from backend.apps.financeiro.models import PlanoContas
from django.db import transaction

class LancamentoContabil(ModelBaseEmpresa):
    TIPO_LANCAMENTO_CHOICES = [
        ('SIMPLES', 'Simples (Débito e Crédito)'),
        ('COMPOSTO', 'Composto (Múltiplos Débitos/Créditos)'),
    ]

    data_lancamento = models.DateField(verbose_name="Data do Lançamento")
    historico = models.TextField(verbose_name="Histórico")
    tipo_lancamento = models.CharField(max_length=10, choices=TIPO_LANCAMENTO_CHOICES, default='SIMPLES', verbose_name="Tipo de Lançamento")
    
    class Meta:
        verbose_name = "Lançamento Contábil"
        verbose_name_plural = "Lançamentos Contábeis"
        ordering = ['-data_lancamento']

    def __str__(self):
        return f"Lançamento {self.id} em {self.data_lancamento} - {self.historico[:50]}..."

    @transaction.atomic
    def salvar_lancamento_com_partidas(self, partidas_data: list):
        # Salva o lançamento principal
        self.save()

        # Salva as partidas e verifica o balanço
        total_debito = 0
        total_credito = 0
        for partida_data in partidas_data:
            partida_data['lancamento'] = self
            partida_data['empresa'] = self.empresa
            partida = PartidaLancamento(**partida_data)
            partida.save()
            if partida.tipo_partida == 'D':
                total_debito += partida.valor
            else:
                total_credito += partida.valor
        
        if total_debito != total_credito:
            raise ValueError("O total de débitos deve ser igual ao total de créditos.")

class PartidaLancamento(ModelBaseEmpresa):
    TIPO_PARTIDA_CHOICES = [
        ('D', 'Débito'),
        ('C', 'Crédito'),
    ]

    lancamento = models.ForeignKey(LancamentoContabil, on_delete=models.CASCADE, related_name='partidas')
    conta_contabil = models.ForeignKey(PlanoContas, on_delete=models.PROTECT, related_name='partidas')
    tipo_partida = models.CharField(max_length=1, choices=TIPO_PARTIDA_CHOICES, verbose_name="Tipo de Partida")
    valor = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Valor")
    historico_complementar = models.TextField(blank=True, null=True, verbose_name="Histórico Complementar")

    class Meta:
        verbose_name = "Partida de Lançamento"
        verbose_name_plural = "Partidas de Lançamento"
        unique_together = ('lancamento', 'conta_contabil', 'tipo_partida') # Evitar duplicidade de D/C para mesma conta no mesmo lançamento

    def __str__(self):
        return f"{self.get_tipo_partida_display()} de R$ {self.valor} na conta {self.conta_contabil.codigo}"
