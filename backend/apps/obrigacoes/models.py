from django.db import models
from backend.apps.core.models import ModelBaseEmpresa
from datetime import date

class ObrigacaoFiscal(ModelBaseEmpresa):
    TIPO_OBRIGACAO_CHOICES = [
        ('DARF', 'DARF (Documento de Arrecadação de Receitas Federais)'),
        ('PGDAS', 'PGDAS-D (Programa Gerador do Documento de Arrecadação do Simples Nacional)'),
        ('DAE', 'DAE (Documento de Arrecadação do eSocial)'),
        ('DAS_MEI', 'DAS-MEI (Documento de Arrecadação do Simples Nacional para o MEI)'),
        ('DIRF', 'DIRF (Declaração do Imposto de Renda Retido na Fonte)'),
        ('DCTF', 'DCTF (Declaração de Débitos e Créditos Tributários Federais)'),
        ('DEFIS', 'DEFIS (Declaração de Informações Socioeconômicas e Fiscais)'),
        ('GIA', 'GIA (Guia de Informação e Apuração do ICMS)'),
        ('DESTDA', 'DeSTDA (Declaração de Substituição Tributária, Diferencial de Alíquotas e Antecipação)'),
        ('ESOCIAL', 'eSocial'),
        ('EFD', 'EFD (Escrituração Fiscal Digital - ICMS/IPI e Contribuições)'),
        ('OUTRO', 'Outro'),
    ]

    STATUS_CHOICES = [
        ('ABERTO', 'Aberto'),
        ('ATRASADO', 'Atrasado'),
        ('PAGO', 'Pago'),
        ('ENVIADO', 'Enviado'),
        ('CONCLUIDO', 'Concluído'),
        ('CANCELADO', 'Cancelado'),
    ]

    tipo_obrigacao = models.CharField(max_length=10, choices=TIPO_OBRIGACAO_CHOICES, verbose_name="Tipo de Obrigação")
    descricao = models.CharField(max_length=255, blank=True, null=True, verbose_name="Descrição Detalhada")
    data_vencimento = models.DateField(verbose_name="Data de Vencimento")
    data_envio_pagamento = models.DateField(blank=True, null=True, verbose_name="Data de Envio/Pagamento")
    valor = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True, verbose_name="Valor")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='ABERTO', verbose_name="Status")
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    link_documento = models.URLField(max_length=500, blank=True, null=True, verbose_name="Link para Documento/Comprovante")

    class Meta:
        verbose_name = "Obrigação Fiscal"
        verbose_name_plural = "Obrigações Fiscais"
        unique_together = ('empresa', 'tipo_obrigacao', 'data_vencimento') # Evita duplicidade para a mesma empresa/obrigação/vencimento
        ordering = ['data_vencimento']

    def __str__(self):
        return f"{self.get_tipo_obrigacao_display()} - {self.data_vencimento.strftime('%d/%m/%Y')} ({self.empresa.nome_fantasia})"
    
    @property
    def esta_vencida(self):
        return self.data_vencimento < date.today() and self.status not in ['PAGO', 'ENVIADO', 'CONCLUIDO']
