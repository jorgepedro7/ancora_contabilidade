from django.db import models
from backend.apps.core.models import ModelBaseEmpresa
from backend.apps.core.utils import validar_cpf, validar_cnpj
import uuid

class PessoaBase(ModelBaseEmpresa):
    TIPO_PESSOA_CHOICES = [
        ('PF', 'Pessoa Física'),
        ('PJ', 'Pessoa Jurídica'),
        ('EX', 'Exterior'),
    ]
    INDICADOR_IE_CHOICES = [
        ('1', 'Contribuinte ICMS'),
        ('2', 'Contribuinte Isento de Inscrição no Cadastro de Contribuintes do ICMS'),
        ('9', 'Não Contribuinte'),
    ]

    nome_razao_social = models.CharField(max_length=255, verbose_name="Nome/Razão Social")
    nome_fantasia_apelido = models.CharField(max_length=255, blank=True, null=True, verbose_name="Nome Fantasia/Apelido")
    tipo_pessoa = models.CharField(max_length=2, choices=TIPO_PESSOA_CHOICES, default='PF', verbose_name="Tipo de Pessoa")
    documento = models.CharField(max_length=14, unique=False, blank=True, null=True, verbose_name="CPF/CNPJ") # Unique por empresa será tratado no serializer/view
    inscricao_estadual = models.CharField(max_length=20, blank=True, null=True, verbose_name="Inscrição Estadual")
    indicador_ie = models.CharField(max_length=1, choices=INDICADOR_IE_CHOICES, default='9', verbose_name="Indicador IE")
    
    email = models.EmailField(blank=True, null=True, verbose_name="E-mail")
    telefone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telefone")

    cep = models.CharField(max_length=8, blank=True, null=True, verbose_name="CEP")
    logradouro = models.CharField(max_length=255, blank=True, null=True, verbose_name="Logradouro")
    numero = models.CharField(max_length=10, blank=True, null=True, verbose_name="Número")
    complemento = models.CharField(max_length=255, blank=True, null=True, verbose_name="Complemento")
    bairro = models.CharField(max_length=100, blank=True, null=True, verbose_name="Bairro")
    municipio = models.CharField(max_length=100, blank=True, null=True, verbose_name="Município")
    uf = models.CharField(max_length=2, blank=True, null=True, verbose_name="UF")
    ibge = models.CharField(max_length=7, blank=True, null=True, verbose_name="Código IBGE do Município")

    class Meta:
        abstract = True
        indexes = [
            models.Index(fields=['empresa', 'documento']),
            models.Index(fields=['empresa', 'nome_razao_social']),
        ]

    def __str__(self):
        return self.nome_razao_social

class Cliente(PessoaBase):
    # Campos específicos de Cliente, se houver
    limite_credito = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, verbose_name="Limite de Crédito")

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        unique_together = ('empresa', 'documento') # Garante que o documento é único por empresa

class Fornecedor(PessoaBase):
    # Dados bancários do fornecedor
    banco = models.CharField(max_length=100, blank=True, null=True, verbose_name="Banco")
    agencia = models.CharField(max_length=20, blank=True, null=True, verbose_name="Agência")
    conta = models.CharField(max_length=30, blank=True, null=True, verbose_name="Conta")
    tipo_conta = models.CharField(max_length=20, choices=[('CC', 'Conta Corrente'), ('CP', 'Conta Poupança')], blank=True, null=True, verbose_name="Tipo de Conta")
    chave_pix = models.CharField(max_length=255, blank=True, null=True, verbose_name="Chave PIX")

    class Meta:
        verbose_name = "Fornecedor"
        verbose_name_plural = "Fornecedores"
        unique_together = ('empresa', 'documento') # Garante que o documento é único por empresa

class Produto(ModelBaseEmpresa):
    ORIGEM_CHOICES = [
        ('0', 'Nacional'), ('1', 'Estrangeira - Importação Direta'), ('2', 'Estrangeira - Adquirida no Mercado Interno'),
        ('3', 'Nacional, Conteúdo de Importação > 40% e <= 70%'), ('4', 'Nacional, Processos Produtivos Básicos'),
        ('5', 'Nacional, Conteúdo de Importação <= 40%'), ('6', 'Estrangeira - Importação Direta, sem similar Nacional'),
        ('7', 'Estrangeira - Adquirida no Mercado Interno, sem similar Nacional'),
        ('8', 'Nacional, Conteúdo de Importação > 70%'),
    ]

    descricao = models.CharField(max_length=255, verbose_name="Descrição do Produto")
    codigo_interno = models.CharField(max_length=50, unique=False, blank=True, null=True, verbose_name="Código Interno") # Unique por empresa
    ean = models.CharField(max_length=14, blank=True, null=True, verbose_name="EAN/GTIN")

    ncm = models.CharField(max_length=8, verbose_name="NCM")
    cest = models.CharField(max_length=7, blank=True, null=True, verbose_name="CEST")
    cfop_padrao = models.CharField(max_length=4, blank=True, null=True, verbose_name="CFOP Padrão")
    origem = models.CharField(max_length=1, choices=ORIGEM_CHOICES, default='0', verbose_name="Origem")

    # Tributação ICMS
    cst_icms = models.CharField(max_length=3, blank=True, null=True, verbose_name="CST ICMS") # Para Simples Nacional CSOSN
    aliquota_icms = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, verbose_name="Alíquota ICMS (%)")
    mva_st = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, verbose_name="MVA-ST (%)")

    # Tributação IPI
    cst_ipi = models.CharField(max_length=2, blank=True, null=True, verbose_name="CST IPI")
    aliquota_ipi = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, verbose_name="Alíquota IPI (%)")

    # Tributação PIS/COFINS
    cst_pis_cofins = models.CharField(max_length=2, blank=True, null=True, verbose_name="CST PIS/COFINS")
    aliquota_pis = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, verbose_name="Alíquota PIS (%)")
    aliquota_cofins = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, verbose_name="Alíquota COFINS (%)")

    # Preços
    preco_custo = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, verbose_name="Preço de Custo")
    preco_venda = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Preço de Venda")

    # Estoque
    estoque_atual = models.DecimalField(max_digits=15, decimal_places=3, default=0.000, verbose_name="Estoque Atual")
    estoque_minimo = models.DecimalField(max_digits=15, decimal_places=3, default=0.000, verbose_name="Estoque Mínimo")
    estoque_maximo = models.DecimalField(max_digits=15, decimal_places=3, default=0.000, verbose_name="Estoque Máximo")
    controla_estoque = models.BooleanField(default=True, verbose_name="Controla Estoque")

    # Peso e Dimensões (para transporte na NF-e)
    peso_liquido = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True, verbose_name="Peso Líquido (kg)")
    peso_bruto = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True, verbose_name="Peso Bruto (kg)")
    largura = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True, verbose_name="Largura (cm)")
    altura = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True, verbose_name="Altura (cm)")
    profundidade = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True, verbose_name="Profundidade (cm)")

    class Meta:
        verbose_name = "Produto"
        verbose_name_plural = "Produtos"
        unique_together = ('empresa', 'codigo_interno') # Código interno único por empresa
        indexes = [
            models.Index(fields=['empresa', 'descricao']),
            models.Index(fields=['empresa', 'ean']),
            models.Index(fields=['empresa', 'ncm']),
        ]

    @property
    def margem_lucro(self):
        if self.preco_venda > 0 and self.preco_custo > 0:
            return ((self.preco_venda - self.preco_custo) / self.preco_venda) * 100
        return 0.00
