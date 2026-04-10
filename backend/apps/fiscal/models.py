from django.db import models
from backend.apps.core.models import ModelBaseEmpresa
from backend.apps.cadastros.models import Produto
from backend.apps.empresas.models import Empresa, ConfiguracaoFiscalEmpresa
from django.db import transaction
import uuid

class NotaFiscal(ModelBaseEmpresa):
    STATUS_CHOICES = [
        ('RASCUNHO', 'Rascunho'),
        ('PENDENTE', 'Pendente de Autorização'),
        ('PROCESSANDO', 'Processando Autorização'),
        ('AUTORIZADA', 'Autorizada'),
        ('REJEITADA', 'Rejeitada'),
        ('CANCELADA', 'Cancelada'),
        ('DENEGADA', 'Denegada'),
        ('PROCESSAMENTO', 'Em Processamento (Evento)'),
    ]

    TIPO_NF_CHOICES = [
        ('1', 'NF-e (Modelo 55)'),
        ('2', 'NFC-e (Modelo 65)'),
    ]

    FINALIDADE_CHOICES = [
        ('1', 'NF-e Normal'),
        ('2', 'NF-e Complementar'),
        ('3', 'NF-e de Ajuste'),
        ('4', 'Devolução de Mercadoria'),
    ]

    # Identificação
    chave_acesso = models.CharField(max_length=44, unique=True, blank=True, null=True, verbose_name="Chave de Acesso")
    protocolo = models.CharField(max_length=15, blank=True, null=True, verbose_name="Protocolo de Autorização/Cancelamento")
    numero = models.BigIntegerField(verbose_name="Número da NF")
    serie = models.CharField(max_length=3, verbose_name="Série")
    modelo = models.CharField(max_length=2, default='55', verbose_name="Modelo do Documento Fiscal")
    tipo_nf = models.CharField(max_length=1, choices=TIPO_NF_CHOICES, verbose_name="Tipo de NF")
    finalidade = models.CharField(max_length=1, choices=FINALIDADE_CHOICES, verbose_name="Finalidade da Emissão")
    data_emissao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Emissão")
    data_saida_entrada = models.DateTimeField(blank=True, null=True, verbose_name="Data de Saída/Entrada")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='RASCUNHO', verbose_name="Status da NF")

    # Destinatário
    destinatario_nome = models.CharField(max_length=255, verbose_name="Nome/Razão Social Destinatário")
    destinatario_documento = models.CharField(max_length=14, verbose_name="CPF/CNPJ Destinatário")
    destinatario_ie = models.CharField(max_length=20, blank=True, null=True, verbose_name="IE Destinatário")
    destinatario_email = models.EmailField(blank=True, null=True, verbose_name="E-mail Destinatário")
    destinatario_cep = models.CharField(max_length=8, verbose_name="CEP Destinatário")
    destinatario_logradouro = models.CharField(max_length=255, verbose_name="Logradouro Destinatário")
    destinatario_numero = models.CharField(max_length=10, verbose_name="Número Destinatário")
    destinatario_complemento = models.CharField(max_length=255, blank=True, null=True, verbose_name="Complemento Destinatário")
    destinatario_bairro = models.CharField(max_length=100, verbose_name="Bairro Destinatário")
    destinatario_municipio = models.CharField(max_length=100, verbose_name="Município Destinatário")
    destinatario_uf = models.CharField(max_length=2, verbose_name="UF Destinatário")
    destinatario_ibge = models.CharField(max_length=7, blank=True, null=True, verbose_name="IBGE Município Destinatário")

    # Valores Totais (calculados)
    valor_produtos = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, verbose_name="Valor Total dos Produtos")
    valor_desconto = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, verbose_name="Valor Total do Desconto")
    valor_frete = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, verbose_name="Valor Total do Frete")
    valor_seguro = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, verbose_name="Valor Total do Seguro")
    valor_outras_despesas = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, verbose_name="Valor Outras Despesas")
    valor_icms = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, verbose_name="Valor Total ICMS")
    valor_icms_st = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, verbose_name="Valor Total ICMS ST")
    valor_ipi = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, verbose_name="Valor Total IPI")
    valor_pis = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, verbose_name="Valor Total PIS")
    valor_cofins = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, verbose_name="Valor Total COFINS")
    valor_total_nf = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, verbose_name="Valor Total da NF")

    # Transporte
    MODALIDADE_FRETE_CHOICES = [
        ('0', 'Por conta do emitente'),
        ('1', 'Por conta do destinatário'),
        ('2', 'Por conta de terceiros'),
        ('3', 'Transporte próprio por conta do emitente'),
        ('4', 'Transporte próprio por conta do destinatário'),
        ('9', 'Sem ocorrência de transporte'),
    ]
    modalidade_frete = models.CharField(max_length=1, choices=MODALIDADE_FRETE_CHOICES, default='9', verbose_name="Modalidade do Frete")
    transportadora = models.ForeignKey('cadastros.Fornecedor', on_delete=models.SET_NULL, blank=True, null=True, related_name='nfe_transportadas')
    # Campos para volume, peso, etc.

    # Arquivos
    xml_autorizado = models.FileField(upload_to='nfe/xmls/', blank=True, null=True, verbose_name="XML Autorizado")
    xml_cancelamento = models.FileField(upload_to='nfe/xmls/', blank=True, null=True, verbose_name="XML Cancelamento")
    pdf_danfe = models.FileField(upload_to='nfe/danfes/', blank=True, null=True, verbose_name="PDF DANFE")

    # Retorno SEFAZ
    codigo_retorno = models.CharField(max_length=10, blank=True, null=True, verbose_name="Código de Retorno SEFAZ")
    mensagem_retorno = models.TextField(blank=True, null=True, verbose_name="Mensagem de Retorno SEFAZ")

    class Meta:
        verbose_name = "Nota Fiscal"
        verbose_name_plural = "Notas Fiscais"
        unique_together = ('empresa', 'numero', 'serie', 'tipo_nf')
        indexes = [
            models.Index(fields=['empresa', 'status']),
            models.Index(fields=['empresa', 'chave_acesso']),
        ]
    
    def __str__(self):
        return f"NF {self.numero}/{self.serie} - {self.get_status_display()}"

    def save(self, *args, **kwargs):
        if not self.serie and self.tipo_nf == '1': # NF-e
            self.serie = self.empresa.configuracao_fiscal.serie_nfe
        elif not self.serie and self.tipo_nf == '2': # NFC-e
            self.serie = self.empresa.configuracao_fiscal.serie_nfce
        
        if not self.numero and self.tipo_nf == '1':
            self.numero = self.empresa.configuracao_fiscal.gerar_proximo_numero_nfe()
        elif not self.numero and self.tipo_nf == '2':
            self.numero = self.empresa.configuracao_fiscal.gerar_proximo_numero_nfce()
            
        super().save(*args, **kwargs)

    def calcular_totais(self):
        self.valor_produtos = sum(item.valor_total for item in self.itens.all())
        # Re-calcular outros totais (desconto, frete, impostos) baseados nos itens
        # Isso pode ser complexo e depender das regras fiscais
        self.valor_total_nf = (self.valor_produtos - self.valor_desconto + self.valor_frete + 
                              self.valor_seguro + self.valor_outras_despesas + 
                              self.valor_icms + self.valor_icms_st + self.valor_ipi)
        self.save(update_fields=[
            'valor_produtos', 'valor_desconto', 'valor_frete', 'valor_seguro',
            'valor_outras_despesas', 'valor_icms', 'valor_icms_st', 'valor_ipi',
            'valor_pis', 'valor_cofins', 'valor_total_nf'
        ])


class ItemNotaFiscal(models.Model):
    nota_fiscal = models.ForeignKey(NotaFiscal, on_delete=models.CASCADE, related_name='itens')
    produto = models.ForeignKey(Produto, on_delete=models.PROTECT, blank=True, null=True) # Pode ser nulo se for um item digitado
    
    # Dados do produto no momento da venda (redundância intencional para histórico)
    produto_descricao = models.CharField(max_length=255, verbose_name="Descrição do Produto")
    produto_ncm = models.CharField(max_length=8, verbose_name="NCM")
    produto_cest = models.CharField(max_length=7, blank=True, null=True, verbose_name="CEST")
    produto_cfop = models.CharField(max_length=4, verbose_name="CFOP")
    produto_ean = models.CharField(max_length=14, blank=True, null=True, verbose_name="EAN/GTIN")

    quantidade = models.DecimalField(max_digits=15, decimal_places=4, verbose_name="Quantidade")
    valor_unitario = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Valor Unitário")
    valor_desconto_item = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, verbose_name="Desconto no Item")
    valor_total = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Valor Total")

    # Impostos (valores calculados para o item)
    icms_cst_csosn = models.CharField(max_length=3, blank=True, null=True, verbose_name="ICMS CST/CSOSN")
    icms_base_calculo = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, verbose_name="ICMS BC")
    icms_aliquota = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, verbose_name="ICMS Alíquota")
    icms_valor = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, verbose_name="ICMS Valor")

    ipi_cst = models.CharField(max_length=2, blank=True, null=True, verbose_name="IPI CST")
    ipi_base_calculo = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, verbose_name="IPI BC")
    ipi_aliquota = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, verbose_name="IPI Alíquota")
    ipi_valor = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, verbose_name="IPI Valor")

    pis_cst = models.CharField(max_length=2, blank=True, null=True, verbose_name="PIS CST")
    pis_base_calculo = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, verbose_name="PIS BC")
    pis_aliquota = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, verbose_name="PIS Alíquota")
    pis_valor = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, verbose_name="PIS Valor")

    cofins_cst = models.CharField(max_length=2, blank=True, null=True, verbose_name="COFINS CST")
    cofins_base_calculo = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, verbose_name="COFINS BC")
    cofins_aliquota = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, verbose_name="COFINS Alíquota")
    cofins_valor = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, verbose_name="COFINS Valor")

    class Meta:
        verbose_name = "Item da Nota Fiscal"
        verbose_name_plural = "Itens da Nota Fiscal"
    

    def __str__(self):
        return f"{self.produto_descricao} ({self.quantidade}x)"

    def save(self, *args, **kwargs):
        self.valor_total = (self.quantidade * self.valor_unitario) - self.valor_desconto_item
        super().save(*args, **kwargs)
        # Atualiza os totais da NF após salvar o item
        self.nota_fiscal.calcular_totais()


class EventoNotaFiscal(ModelBaseEmpresa):
    TIPO_EVENTO_CHOICES = [
        ('110110', 'Cancelamento'),
        ('110114', 'Carta de Correção'),
        ('110115', 'EPEC'), # Evento Prévio de Emissão em Contingência
        ('PROCESSAMENTO', 'Processamento de NF'), # New event type
    ]
    nota_fiscal = models.ForeignKey(NotaFiscal, on_delete=models.CASCADE, related_name='eventos')
    tipo_evento = models.CharField(max_length=20, choices=TIPO_EVENTO_CHOICES, verbose_name="Tipo de Evento")
    justificativa = models.TextField(blank=True, null=True, verbose_name="Justificativa/Texto")
    xml_evento = models.FileField(upload_to='nfe/eventos/', blank=True, null=True, verbose_name="XML do Evento")
    protocolo_retorno = models.CharField(max_length=15, blank=True, null=True, verbose_name="Protocolo de Retorno")
    data_registro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Registro")

    class Meta:
        verbose_name = "Evento da Nota Fiscal"
        verbose_name_plural = "Eventos da Nota Fiscal"
    
    def __str__(self):
        return f"Evento de {self.get_tipo_evento_display()} para NF {self.nota_fiscal.numero}"
