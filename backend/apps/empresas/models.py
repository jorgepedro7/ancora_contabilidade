from django.db import models
from django.db.models import F
from django.db import transaction
from backend.apps.core.models import ModelBase
from datetime import date
import uuid

class Empresa(ModelBase):
    REGIME_TRIBUTARIO_CHOICES = [
        ('SN', 'Simples Nacional'),
        ('SNEI', 'Simples Nacional - Excesso de Ingresso'),
        ('LP', 'Lucro Presumido'),
        ('LR', 'Lucro Real'),
        ('LA', 'Lucro Arbitrado'),
        ('MEI', 'Microempreendedor Individual'),
        ('ENTE', 'Entidade Imune ou Isenta'),
    ]

    PORTE_CHOICES = [
        ('MEI', 'Microempreendedor Individual'),
        ('ME', 'Microempresa'),
        ('EPP', 'Empresa de Pequeno Porte'),
        ('MEDIO', 'Empresa de Médio Porte'),
        ('GRANDE', 'Grande Empresa'),
    ]

    razao_social = models.CharField(max_length=255, verbose_name="Razão Social")
    nome_fantasia = models.CharField(max_length=255, blank=True, null=True, verbose_name="Nome Fantasia")
    cnpj = models.CharField(max_length=14, unique=True, verbose_name="CNPJ")
    inscricao_estadual = models.CharField(max_length=20, blank=True, null=True, verbose_name="Inscrição Estadual")
    inscricao_municipal = models.CharField(max_length=20, blank=True, null=True, verbose_name="Inscrição Municipal")
    cnae_principal = models.CharField(max_length=7, verbose_name="CNAE Principal")
    cnae_secundarios = models.JSONField(blank=True, null=True, verbose_name="CNAEs Secundários")

    regime_tributario = models.CharField(max_length=5, choices=REGIME_TRIBUTARIO_CHOICES, verbose_name="Regime Tributário")
    porte = models.CharField(max_length=10, choices=PORTE_CHOICES, blank=True, null=True, verbose_name="Porte da Empresa")

    cep = models.CharField(max_length=8, verbose_name="CEP")
    logradouro = models.CharField(max_length=255, verbose_name="Logradouro")
    numero = models.CharField(max_length=10, verbose_name="Número")
    complemento = models.CharField(max_length=255, blank=True, null=True, verbose_name="Complemento")
    bairro = models.CharField(max_length=100, verbose_name="Bairro")
    municipio = models.CharField(max_length=100, verbose_name="Município")
    uf = models.CharField(max_length=2, verbose_name="UF")
    ibge = models.CharField(max_length=7, blank=True, null=True, verbose_name="Código IBGE do Município")

    certificado_digital_pfx = models.FileField(upload_to='certificados/', blank=True, null=True, verbose_name="Certificado Digital (.pfx)")
    certificado_senha = models.CharField(max_length=255, blank=True, null=True, verbose_name="Senha do Certificado (Criptografada)")
    certificado_data_validade = models.DateField(blank=True, null=True, verbose_name="Data de Validade do Certificado")

    class Meta:
        verbose_name = "Empresa"
        verbose_name_plural = "Empresas"
        indexes = [
            models.Index(fields=['cnpj']),
            models.Index(fields=['nome_fantasia']),
            models.Index(fields=['ativo']),
        ]

    def __str__(self):
        return self.nome_exibicao

    @property
    def certificado_vencido(self):
        if self.certificado_data_validade and self.certificado_data_validade < date.today():
            return True
        return False

    @property
    def nome_exibicao(self):
        return self.nome_fantasia if self.nome_fantasia else self.razao_social

    @property
    def endereco_completo(self):
        parts = [self.logradouro, self.numero]
        if self.complemento:
            parts.append(self.complemento)
        parts.extend([self.bairro, self.municipio, self.uf, self.cep])
        return ", ".join(parts)

class ConfiguracaoFiscalEmpresa(ModelBase):
    AMBIENTE_CHOICES = [
        ('1', 'Produção'),
        ('2', 'Homologação'),
    ]
    empresa = models.OneToOneField(Empresa, on_delete=models.CASCADE, related_name='configuracao_fiscal')
    
    ambiente_sefaz = models.CharField(max_length=1, choices=AMBIENTE_CHOICES, default='2', verbose_name="Ambiente SEFAZ")

    serie_nfe = models.CharField(max_length=3, default='001', verbose_name="Série NF-e")
    proximo_numero_nfe = models.BigIntegerField(default=1, verbose_name="Próximo Número NF-e")

    serie_nfce = models.CharField(max_length=3, default='001', verbose_name="Série NFC-e")
    proximo_numero_nfce = models.BigIntegerField(default=1, verbose_name="Próximo Número NFC-e")

    serie_nfse = models.CharField(max_length=3, default='001', verbose_name="Série NFS-e")
    proximo_numero_nfse = models.BigIntegerField(default=1, verbose_name="Próximo Número NFS-e") # Para notas de serviço

    csc_id_nfce = models.CharField(max_length=10, blank=True, null=True, verbose_name="CSC ID NFC-e")
    csc_token_nfce = models.CharField(max_length=255, blank=True, null=True, verbose_name="CSC Token NFC-e (Criptografado)")

    class Meta:
        verbose_name = "Configuração Fiscal da Empresa"
        verbose_name_plural = "Configurações Fiscais da Empresa"

    def __str__(self):
        return f"Configuração Fiscal para {self.empresa.nome_exibicao}"

    def gerar_proximo_numero_nfe(self):
        with transaction.atomic():
            self.refresh_from_db() # Garante que estamos com a versão mais recente do banco
            proximo = self.proximo_numero_nfe
            self.proximo_numero_nfe = F('proximo_numero_nfe') + 1
            self.save(update_fields=['proximo_numero_nfe'])
            return proximo

    def gerar_proximo_numero_nfce(self):
        with transaction.atomic():
            self.refresh_from_db()
            proximo = self.proximo_numero_nfce
            self.proximo_numero_nfce = F('proximo_numero_nfce') + 1
            self.save(update_fields=['proximo_numero_nfce'])
            return proximo

    def gerar_proximo_numero_nfse(self):
        with transaction.atomic():
            self.refresh_from_db()
            proximo = self.proximo_numero_nfse
            self.proximo_numero_nfse = F('proximo_numero_nfse') + 1
            self.save(update_fields=['proximo_numero_nfse'])
            return proximo
