from django.db import models

from backend.apps.core.models import ModelBaseEmpresa


class PortalCliente(ModelBaseEmpresa):
    slug = models.SlugField(max_length=80, unique=True)
    email_responsavel = models.EmailField(blank=True, null=True)
    telefone_responsavel = models.CharField(max_length=20, blank=True, null=True)
    recebe_alertas = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Portal do Cliente'
        verbose_name_plural = 'Portais dos Clientes'

    def __str__(self):
        return f'Portal {self.slug}'


class ChecklistCompetencia(ModelBaseEmpresa):
    MODULO_CHOICES = [
        ('FISCAL', 'Fiscal'),
        ('FOLHA', 'Folha'),
        ('FINANCEIRO', 'Financeiro'),
        ('CONTRATUAL', 'Contratual'),
        ('GERAL', 'Geral'),
    ]
    STATUS_CHOICES = [
        ('PENDENTE', 'Pendente'),
        ('EM_ANDAMENTO', 'Em andamento'),
        ('CONCLUIDO', 'Concluído'),
    ]

    competencia = models.DateField()
    modulo = models.CharField(max_length=20, choices=MODULO_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDENTE')
    observacoes = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Checklist por Competência'
        verbose_name_plural = 'Checklists por Competência'
        unique_together = ('empresa', 'competencia', 'modulo')
        ordering = ['-competencia', 'modulo']

    def __str__(self):
        return f'{self.get_modulo_display()} {self.competencia:%m/%Y}'


class DocumentoRecebido(ModelBaseEmpresa):
    TIPO_DOCUMENTO_CHOICES = [
        ('FISCAL', 'Fiscal'),
        ('FOLHA', 'Folha'),
        ('FINANCEIRO', 'Financeiro'),
        ('CONTRATUAL', 'Contratual'),
        ('GERAL', 'Geral'),
    ]
    TIPO_ENTREGA_CHOICES = [
        ('UPLOAD', 'Upload'),
        ('EMAIL', 'E-mail'),
        ('API', 'API'),
        ('MANUAL', 'Manual'),
    ]
    STATUS_CHOICES = [
        ('NOVO', 'Novo'),
        ('VALIDADO', 'Validado'),
        ('REPROVADO', 'Reprovado'),
    ]

    portal_cliente = models.ForeignKey(PortalCliente, on_delete=models.SET_NULL, blank=True, null=True, related_name='documentos')
    checklist = models.ForeignKey(ChecklistCompetencia, on_delete=models.SET_NULL, blank=True, null=True, related_name='documentos')
    funcionario = models.ForeignKey('folha.Funcionario', on_delete=models.SET_NULL, blank=True, null=True, related_name='documentos_intake')
    contrato_trabalho = models.ForeignKey('folha.ContratoTrabalho', on_delete=models.SET_NULL, blank=True, null=True, related_name='documentos_intake')
    nota_fiscal = models.ForeignKey('fiscal.NotaFiscal', on_delete=models.SET_NULL, blank=True, null=True, related_name='documentos_intake')

    titulo = models.CharField(max_length=255)
    tipo_documento = models.CharField(max_length=20, choices=TIPO_DOCUMENTO_CHOICES)
    tipo_entrega = models.CharField(max_length=20, choices=TIPO_ENTREGA_CHOICES, default='UPLOAD')
    competencia = models.DateField()
    arquivo = models.FileField(upload_to='intake/documentos/')
    hash_arquivo = models.CharField(max_length=64, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='NOVO')
    log_validacao = models.JSONField(blank=True, null=True)
    observacoes = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Documento Recebido'
        verbose_name_plural = 'Documentos Recebidos'
        ordering = ['-criado_em']
        indexes = [
            models.Index(fields=['empresa', 'competencia']),
            models.Index(fields=['empresa', 'status']),
            models.Index(fields=['empresa', 'tipo_documento']),
        ]

    def __str__(self):
        return self.titulo


class Pendencia(ModelBaseEmpresa):
    STATUS_CHOICES = [
        ('ABERTA', 'Aberta'),
        ('EM_TRATAMENTO', 'Em tratamento'),
        ('RESOLVIDA', 'Resolvida'),
    ]
    SEVERIDADE_CHOICES = [
        ('BAIXA', 'Baixa'),
        ('MEDIA', 'Média'),
        ('ALTA', 'Alta'),
    ]

    checklist = models.ForeignKey(ChecklistCompetencia, on_delete=models.CASCADE, related_name='pendencias', blank=True, null=True)
    documento = models.ForeignKey(DocumentoRecebido, on_delete=models.CASCADE, related_name='pendencias', blank=True, null=True)
    titulo = models.CharField(max_length=255)
    descricao = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ABERTA')
    severidade = models.CharField(max_length=10, choices=SEVERIDADE_CHOICES, default='MEDIA')

    class Meta:
        verbose_name = 'Pendência'
        verbose_name_plural = 'Pendências'
        ordering = ['status', '-criado_em']

    def __str__(self):
        return self.titulo


class LoteExportacaoQuestor(ModelBaseEmpresa):
    STATUS_CHOICES = [
        ('PENDENTE', 'Pendente'),
        ('PROCESSANDO', 'Processando'),
        ('EXPORTADO', 'Exportado'),
        ('ERRO', 'Erro'),
    ]

    competencia = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDENTE')
    arquivo_exportado = models.FileField(upload_to='intake/questor/', blank=True, null=True)
    resumo = models.JSONField(blank=True, null=True)
    processado_em = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = 'Lote de Exportação Questor'
        verbose_name_plural = 'Lotes de Exportação Questor'
        ordering = ['-criado_em']

    def __str__(self):
        return f'Lote Questor {self.competencia:%m/%Y}'
