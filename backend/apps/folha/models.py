from django.db import models
from django.db.models import Q
from backend.apps.core.models import ModelBaseEmpresa
from backend.apps.core.utils import validar_cpf, formatar_cpf
from datetime import date, timedelta
from decimal import Decimal
import io
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

class Cargo(ModelBaseEmpresa):
    nome = models.CharField(max_length=100, verbose_name="Nome do Cargo")
    cbo = models.CharField(max_length=7, blank=True, null=True, verbose_name="CBO") # Classificação Brasileira de Ocupações

    class Meta:
        verbose_name = "Cargo"
        verbose_name_plural = "Cargos"
        unique_together = ('empresa', 'nome')

    def __str__(self):
        return self.nome

class Departamento(ModelBaseEmpresa):
    nome = models.CharField(max_length=100, verbose_name="Nome do Departamento")
    centro_custo = models.CharField(max_length=50, blank=True, null=True, verbose_name="Centro de Custo")

    class Meta:
        verbose_name = "Departamento"
        verbose_name_plural = "Departamentos"
        unique_together = ('empresa', 'nome')

    def __str__(self):
        return self.nome

class Funcionario(ModelBaseEmpresa):
    ESTADO_CIVIL_CHOICES = [
        ('SOLTEIRO', 'Solteiro(a)'),
        ('CASADO', 'Casado(a)'),
        ('DIVORCIADO', 'Divorciado(a)'),
        ('VIUVO', 'Viúvo(a)'),
    ]

    nome_completo = models.CharField(max_length=255, verbose_name="Nome Completo")
    cpf = models.CharField(max_length=11, unique=True, verbose_name="CPF")
    rg = models.CharField(max_length=20, blank=True, null=True, verbose_name="RG")
    data_nascimento = models.DateField(verbose_name="Data de Nascimento")
    estado_civil = models.CharField(max_length=15, choices=ESTADO_CIVIL_CHOICES, blank=True, null=True, verbose_name="Estado Civil")
    sexo = models.CharField(max_length=1, choices=[('M', 'Masculino'), ('F', 'Feminino')], blank=True, null=True, verbose_name="Sexo")

    # Contato
    email = models.EmailField(blank=True, null=True, verbose_name="E-mail")
    telefone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telefone")
    telefone_celular = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telefone Celular/WhatsApp")

    # Endereço
    cep = models.CharField(max_length=8, blank=True, null=True, verbose_name="CEP")
    logradouro = models.CharField(max_length=255, blank=True, null=True, verbose_name="Logradouro")
    numero = models.CharField(max_length=10, blank=True, null=True, verbose_name="Número")
    complemento = models.CharField(max_length=255, blank=True, null=True, verbose_name="Complemento")
    bairro = models.CharField(max_length=100, blank=True, null=True, verbose_name="Bairro")
    municipio = models.CharField(max_length=100, blank=True, null=True, verbose_name="Município")
    uf = models.CharField(max_length=2, blank=True, null=True, verbose_name="UF")

    # Documentação Trabalhista
    ctps = models.CharField(max_length=11, blank=True, null=True, verbose_name="CTPS")
    pis = models.CharField(max_length=11, blank=True, null=True, verbose_name="PIS")
    titulo_eleitor = models.CharField(max_length=12, blank=True, null=True, verbose_name="Título de Eleitor")
    reservista = models.CharField(max_length=15, blank=True, null=True, verbose_name="Certificado de Reservista")

    # Dados Bancários
    banco = models.CharField(max_length=100, blank=True, null=True, verbose_name="Banco para Pagamento")
    agencia = models.CharField(max_length=20, blank=True, null=True, verbose_name="Agência")
    conta = models.CharField(max_length=30, blank=True, null=True, verbose_name="Conta")
    tipo_conta = models.CharField(max_length=20, choices=[('CC', 'Conta Corrente'), ('CP', 'Conta Poupança')], blank=True, null=True, verbose_name="Tipo de Conta")

    dependentes = models.IntegerField(default=0, verbose_name="Número de Dependentes IRRF")

    class Meta:
        verbose_name = "Funcionário"
        verbose_name_plural = "Funcionários"
        unique_together = ('empresa', 'cpf')

    def __str__(self):
        return self.nome_completo

    def clean(self):
        if self.cpf and not validar_cpf(self.cpf):
            raise models.ValidationError({'cpf': 'CPF inválido.'})

class ContratoTrabalho(ModelBaseEmpresa):
    TIPO_CONTRATO_CHOICES = [
        ('CLT', 'CLT'),
        ('PJ', 'Pessoa Jurídica (Serviço)'),
        ('APRENDIZ', 'Aprendiz'),
        ('ESTAGIO', 'Estágio'),
        ('TEMPORARIO', 'Temporário'),
    ]

    CATEGORIA_ESOCIAL_CHOICES = [
        ('101', 'Empregado (exceto doméstico)'),
        ('102', 'Empregado Doméstico'),
        # ... Adicionar mais categorias conforme necessidade do eSocial
    ]

    funcionario = models.ForeignKey(Funcionario, on_delete=models.PROTECT, related_name='contratos')
    cargo = models.ForeignKey(Cargo, on_delete=models.PROTECT, related_name='contratos')
    departamento = models.ForeignKey(Departamento, on_delete=models.PROTECT, related_name='contratos', blank=True, null=True)
    tipo_contrato = models.CharField(max_length=15, choices=TIPO_CONTRATO_CHOICES, verbose_name="Tipo de Contrato")
    salario_base = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Salário Base")
    data_inicio = models.DateField(verbose_name="Data de Início")
    data_fim = models.DateField(blank=True, null=True, verbose_name="Data de Fim")
    ativo = models.BooleanField(default=True, verbose_name="Contrato Ativo")
    categoria_esocial = models.CharField(max_length=3, choices=CATEGORIA_ESOCIAL_CHOICES, blank=True, null=True, verbose_name="Categoria eSocial")
    
    # Horas Extras
    horas_extras_50 = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, verbose_name="Horas Extras 50%")
    horas_extras_100 = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, verbose_name="Horas Extras 100%")

    class Meta:
        verbose_name = "Contrato de Trabalho"
        verbose_name_plural = "Contratos de Trabalho"
        unique_together = ('funcionario', 'data_inicio')

    def __str__(self):
        return f"Contrato de {self.funcionario.nome_completo} - {self.cargo.nome}"

class FolhaPagamento(ModelBaseEmpresa):
    TIPO_FOLHA_CHOICES = [
        ('MENSAL', 'Mensal'),
        ('DECIMO_TERCEIRO', 'Décimo Terceiro'),
        ('FERIAS', 'Férias'),
        ('RESCISAO', 'Rescisão'),
    ]
    STATUS_CHOICES = [
        ('ABERTA', 'Aberta'),
        ('PROCESSADA', 'Processada'),
        ('FECHADA', 'Fechada'),
    ]

    competencia = models.DateField(verbose_name="Competência (Mês/Ano)")
    tipo_folha = models.CharField(max_length=15, choices=TIPO_FOLHA_CHOICES, default='MENSAL', verbose_name="Tipo de Folha")
    data_processamento = models.DateField(auto_now_add=True, verbose_name="Data de Processamento")
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='ABERTA', verbose_name="Status")
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")

    class Meta:
        verbose_name = "Folha de Pagamento"
        verbose_name_plural = "Folhas de Pagamento"
        unique_together = ('empresa', 'competencia', 'tipo_folha')

    def __str__(self):
        return f"Folha {self.get_tipo_folha_display()} - {self.competencia.strftime('%m/%Y')}"

class HoleriteFuncionario(ModelBaseEmpresa):
    funcionario = models.ForeignKey(Funcionario, on_delete=models.PROTECT, related_name='holerites')
    folha_pagamento = models.ForeignKey(FolhaPagamento, on_delete=models.PROTECT, related_name='holerites')

    # Proventos
    salario_bruto = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, verbose_name="Salário Bruto")
    valor_horas_extras_50 = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, verbose_name="Valor Horas Extras 50%")
    valor_horas_extras_100 = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, verbose_name="Valor Horas Extras 100%")
    outros_proventos = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, verbose_name="Outros Proventos")
    total_proventos = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, verbose_name="Total Proventos")

    # Descontos
    desconto_inss = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, verbose_name="Desconto INSS")
    desconto_irrf = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, verbose_name="Desconto IRRF")
    desconto_fgts = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, verbose_name="Desconto FGTS") # FGTS é depósito, não desconto, mas para holerite pode ser exibido
    outros_descontos = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, verbose_name="Outros Descontos")
    total_descontos = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, verbose_name="Total Descontos")

    # Totais
    liquido_receber = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, verbose_name="Líquido a Receber")
    valor_dsr = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, verbose_name="Valor DSR sobre HE")
    data_pagamento = models.DateField(blank=True, null=True, verbose_name="Data de Pagamento")

    # Valores para eSocial
    base_calculo_inss = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, verbose_name="Base de Cálculo INSS")
    base_calculo_irrf = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, verbose_name="Base de Cálculo IRRF")
    base_calculo_fgts = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, verbose_name="Base de Cálculo FGTS")

    # PDF do Holerite
    pdf_holerite = models.FileField(upload_to='holerites/', blank=True, null=True, verbose_name="PDF do Holerite")
    whatsapp_enviado = models.BooleanField(default=False, verbose_name="Enviado por WhatsApp")
    data_envio_whatsapp = models.DateTimeField(blank=True, null=True, verbose_name="Data de Envio WhatsApp")

    class Meta:
        verbose_name = "Holerite de Funcionário"
        verbose_name_plural = "Holerites de Funcionários"
        unique_together = ('funcionario', 'folha_pagamento')

    def __str__(self):
        return f"Holerite de {self.funcionario.nome_completo} ({self.folha_pagamento.competencia.strftime('%m/%Y')})"

    def calcular(self):
        from backend.apps.core.utils import calcular_inss, calcular_irrf, calcular_fgts

        # Salário base do contrato ativo
        contrato_ativo = self.funcionario.contratos.filter(
            ativo=True,
            data_inicio__lte=self.folha_pagamento.competencia
        ).filter(
            Q(data_fim__isnull=True) | Q(data_fim__gte=self.folha_pagamento.competencia)
        ).order_by('-data_inicio').first()
        if not contrato_ativo:
            raise ValueError(f"Funcionário {self.funcionario.nome_completo} não possui contrato ativo para a competência {self.folha_pagamento.competencia.strftime('%m/%Y')}.")
        
        self.salario_bruto = contrato_ativo.salario_base
        
        # Horas Extras
        # Soma as horas extras do RegistroPonto para a competência (mês/ano)
        inicio_mes = self.folha_pagamento.competencia.replace(day=1)
        if self.folha_pagamento.competencia.month == 12:
            fim_mes = self.folha_pagamento.competencia.replace(year=self.folha_pagamento.competencia.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            fim_mes = self.folha_pagamento.competencia.replace(month=self.folha_pagamento.competencia.month + 1, day=1) - timedelta(days=1)

        pontos = RegistroPonto.objects.filter(
            funcionario=self.funcionario,
            data__range=(inicio_mes, fim_mes)
        )
        
        total_he_50 = pontos.aggregate(total=models.Sum('horas_extras'))['total'] or Decimal('0.00')
        total_atrasos = pontos.aggregate(total=models.Sum('atrasos'))['total'] or Decimal('0.00')

        # Horas Faltas (não justificadas ou não abonadas)
        # Verificamos justificativas no período que NÃO abonam o ponto
        justificativas_nao_abonadas = JustificativaPonto.objects.filter(
            funcionario=self.funcionario,
            abona_ponto=False,
            data_inicio__lte=fim_mes,
            data_fim__gte=inicio_mes
        )
        
        # Simplificação: cada dia de falta não abonada desconta 8h (pode ser melhorado para ler a carga horária do funcionário)
        horas_faltas_justificadas = Decimal('0.00')
        for just in justificativas_nao_abonadas:
            # Calcula dias sobrepostos com o mês atual
            d_inicio = max(just.data_inicio, inicio_mes)
            d_fim = min(just.data_fim, fim_mes)
            dias = (d_fim - d_inicio).days + 1
            horas_faltas_justificadas += Decimal(str(dias * 8))

        valor_hora_base = (contrato_ativo.salario_base / Decimal('220.00'))
        
        self.valor_horas_extras_50 = valor_hora_base * Decimal('1.5') * total_he_50
        self.valor_horas_extras_100 = valor_hora_base * Decimal('2.0') * contrato_ativo.horas_extras_100

        # Cálculo de DSR sobre Horas Extras (Simplificado: 1/6 ou baseado em dias úteis/domingos)
        # Para ser mais preciso, deveríamos contar dias úteis e domingos no mês.
        # Vamos usar a média padrão de 1/6 para este exemplo, ou contar se possível.
        dias_uteis = 25 # Média
        domingos_feriados = 5 # Média
        self.valor_dsr = round((self.valor_horas_extras_50 + self.valor_horas_extras_100) / Decimal(str(dias_uteis)) * Decimal(str(domingos_feriados)), 2)

        self.total_proventos = self.salario_bruto + self.valor_horas_extras_50 + self.valor_horas_extras_100 + self.valor_dsr + self.outros_proventos

        # Cálculo de Descontos de Faltas/Atrasos
        valor_atrasos = valor_hora_base * (total_atrasos + horas_faltas_justificadas)
        self.outros_descontos += valor_atrasos

        # Base de Cálculo INSS é o total de proventos (sem deduções) - Faltas (incidência negativa)
        self.base_calculo_inss = self.total_proventos - valor_atrasos
        self.desconto_inss = Decimal(str(calcular_inss(self.base_calculo_inss)))

        # Base de Cálculo IRRF: base INSS - INSS - dependentes
        self.base_calculo_irrf = self.base_calculo_inss - self.desconto_inss
        self.desconto_irrf = Decimal(str(calcular_irrf(self.base_calculo_irrf, self.funcionario.dependentes)))

        # FGTS (depósito, não desconto do funcionário)
        self.base_calculo_fgts = self.base_calculo_inss
        self.desconto_fgts = Decimal(str(calcular_fgts(self.base_calculo_fgts)))

        self.total_descontos = self.desconto_inss + self.desconto_irrf + self.outros_descontos
        self.liquido_receber = round(self.total_proventos - self.total_descontos, 2)

        # Salva o holerite calculado
        self.save()

    def gerar_pdf(self):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
        elements = []
        styles = getSampleStyleSheet()
        
        # Estilo customizado para o título
        title_style = ParagraphStyle(
            'TitleStyle',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.black,
            alignment=1, # Center
            spaceAfter=20
        )

        # Cabeçalho do Holerite
        elements.append(Paragraph(f"RECIBO DE PAGAMENTO DE SALÁRIO", title_style))
        
        data_header = [
            [f"Empregador: {self.empresa.razao_social}", f"CNPJ: {self.empresa.cnpj}"],
            [f"Funcionário: {self.funcionario.nome_completo}", f"CPF: {self.funcionario.cpf}"],
            [f"Cargo: {self.funcionario.contratos.filter(ativo=True).first().cargo.nome}", f"Referência: {self.folha_pagamento.competencia.strftime('%m/%Y')}"]
        ]
        t_header = Table(data_header, colWidths=[350, 150])
        t_header.setStyle(TableStyle([
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,0), (-1,-1), 9),
            ('INNERGRID', (0,0), (-1,-1), 0.25, colors.grey),
            ('BOX', (0,0), (-1,-1), 0.25, colors.black),
        ]))
        elements.append(t_header)
        elements.append(Spacer(1, 12))

        # Tabela de Itens (Proventos e Descontos)
        data_itens = [
            ['Descrição', 'Referência', 'Proventos', 'Descontos']
        ]
        
        # Salário Base
        data_itens.append(['Salário Base', '30 dias', f"{self.salario_bruto:,.2f}", ''])
        
        # Horas Extras
        if self.valor_horas_extras_50 > 0:
            data_itens.append(['Horas Extras 50%', '', f"{self.valor_horas_extras_50:,.2f}", ''])
        if self.valor_horas_extras_100 > 0:
            data_itens.append(['Horas Extras 100%', '', f"{self.valor_horas_extras_100:,.2f}", ''])
        
        # DSR
        if self.valor_dsr > 0:
            data_itens.append(['DSR s/ Horas Extras', '', f"{self.valor_dsr:,.2f}", ''])

        # Descontos
        data_itens.append(['INSS', '', '', f"{self.desconto_inss:,.2f}"])
        if self.desconto_irrf > 0:
            data_itens.append(['IRRF', '', '', f"{self.desconto_irrf:,.2f}"])
        if self.outros_descontos > 0:
            data_itens.append(['Faltas/Atrasos/Outros', '', '', f"{self.outros_descontos:,.2f}"])

        t_itens = Table(data_itens, colWidths=[250, 80, 85, 85])
        t_itens.setStyle(TableStyle([
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
            ('ALIGN', (2,0), (-1,-1), 'RIGHT'),
            ('INNERGRID', (0,0), (-1,-1), 0.25, colors.grey),
            ('BOX', (0,0), (-1,-1), 0.25, colors.black),
        ]))
        elements.append(t_itens)
        elements.append(Spacer(1, 12))

        # Totais
        data_totais = [
            ['Total Proventos', f"R$ {self.total_proventos:,.2f}", 'Total Descontos', f"R$ {self.total_descontos:,.2f}"],
            ['', '', 'Valor Líquido', f"R$ {self.liquido_receber:,.2f}"]
        ]
        t_totais = Table(data_totais, colWidths=[120, 130, 120, 130])
        t_totais.setStyle(TableStyle([
            ('FONTNAME', (2,1), (3,1), 'Helvetica-Bold'),
            ('FONTSIZE', (2,1), (3,1), 12),
            ('ALIGN', (1,0), (1,1), 'RIGHT'),
            ('ALIGN', (3,0), (3,1), 'RIGHT'),
            ('BOX', (2,1), (3,1), 1, colors.black),
        ]))
        elements.append(t_totais)
        
        # Bases
        elements.append(Spacer(1, 24))
        bases_text = f"Base FGTS: R$ {self.base_calculo_fgts:,.2f} | FGTS Mês: R$ {self.desconto_fgts:,.2f} | Base INSS: R$ {self.base_calculo_inss:,.2f} | Base IRRF: R$ {self.base_calculo_irrf:,.2f}"
        elements.append(Paragraph(bases_text, styles['Normal']))

        doc.build(elements)
        pdf = buffer.getvalue()
        buffer.close()
        return pdf

class RegistroPonto(ModelBaseEmpresa):
    funcionario = models.ForeignKey(Funcionario, on_delete=models.CASCADE, related_name='registros_ponto')
    data = models.DateField(verbose_name="Data do Registro")
    entrada_1 = models.TimeField(null=True, blank=True, verbose_name="Entrada 1")
    saida_1 = models.TimeField(null=True, blank=True, verbose_name="Saída 1")
    entrada_2 = models.TimeField(null=True, blank=True, verbose_name="Entrada 2")
    saida_2 = models.TimeField(null=True, blank=True, verbose_name="Saída 2")
    
    total_horas = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, verbose_name="Total de Horas Trabalhadas")
    horas_extras = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, verbose_name="Horas Extras")
    atrasos = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, verbose_name="Atrasos/Faltas (Horas)")
    
    justificativa = models.TextField(null=True, blank=True, verbose_name="Justificativa/Ocorrência")
    manual = models.BooleanField(default=False, verbose_name="Lançamento Manual")

    class Meta:
        verbose_name = "Registro de Ponto"
        verbose_name_plural = "Registros de Ponto"
        unique_together = ('funcionario', 'data')
        ordering = ['-data']

    def __str__(self):
        return f"Ponto {self.funcionario.nome_completo} - {self.data.strftime('%d/%m/%Y')}"

class JustificativaPonto(ModelBaseEmpresa):
    TIPO_CHOICES = [
        ('ATESTADO_MEDICO', 'Atestado Médico'),
        ('FALTA_JUSTIFICADA', 'Falta Justificada'),
        ('FALTA_NAO_JUSTIFICADA', 'Falta Não Justificada'),
        ('SUSPENSAO', 'Suspensão'),
        ('FERIAS', 'Férias'),
        ('LICENÇA_MATERNIDADE', 'Licença Maternidade/Paternidade'),
        ('TREINAMENTO', 'Treinamento/Cursos'),
        ('OUTROS', 'Outros'),
    ]

    funcionario = models.ForeignKey(Funcionario, on_delete=models.CASCADE, related_name='justificativas')
    data_inicio = models.DateField(verbose_name="Data de Início")
    data_fim = models.DateField(verbose_name="Data de Fim")
    tipo = models.CharField(max_length=30, choices=TIPO_CHOICES, verbose_name="Tipo de Justificativa")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição/Observação")
    
    # Campos específicos para Atestado Médico
    cid = models.CharField(max_length=10, blank=True, null=True, verbose_name="CID")
    crm_medico = models.CharField(max_length=20, blank=True, null=True, verbose_name="CRM do Médico")
    nome_medico = models.CharField(max_length=100, blank=True, null=True, verbose_name="Nome do Médico")

    documento = models.FileField(upload_to='folha/justificativas/', blank=True, null=True, verbose_name="Documento Comprobatório (PDF/Img)")
    abona_ponto = models.BooleanField(default=True, verbose_name="Abona o Ponto (Não desconta)")

    class Meta:
        verbose_name = "Justificativa de Ponto"
        verbose_name_plural = "Justificativas de Ponto"

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.funcionario.nome_completo} ({self.data_inicio} a {self.data_fim})"

class DocumentoFuncionario(ModelBaseEmpresa):
    TIPO_DOCUMENTO_CHOICES = [
        ('CONTRATO', 'Contrato de Trabalho'),
        ('ADITIVO', 'Aditivo Contratual'),
        ('TERMO_RESPONSABILIDADE', 'Termo de Responsabilidade'),
        ('OPCAO_VT', 'Opção de Vale Transporte'),
        ('FICHA_REGISTRO', 'Ficha de Registro'),
        ('OUTROS', 'Outros'),
    ]
    funcionario = models.ForeignKey(Funcionario, on_delete=models.CASCADE, related_name='documentos')
    tipo = models.CharField(max_length=30, choices=TIPO_DOCUMENTO_CHOICES, verbose_name="Tipo de Documento")
    descricao = models.CharField(max_length=255, blank=True, null=True, verbose_name="Descrição")
    arquivo = models.FileField(upload_to='folha/documentos/', verbose_name="Arquivo")
    data_upload = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Documento de Funcionário"
        verbose_name_plural = "Documentos de Funcionários"

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.funcionario.nome_completo}"

class ImportacaoPonto(ModelBaseEmpresa):
    STATUS_CHOICES = [
        ('PENDENTE', 'Pendente'),
        ('PROCESSANDO', 'Processando'),
        ('CONCLUIDO', 'Concluído'),
        ('ERRO', 'Erro'),
    ]
    arquivo = models.FileField(upload_to='folha/pontos/', verbose_name="Arquivo de Ponto")
    data_importacao = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='PENDENTE')
    formato = models.CharField(max_length=20, default='CSV', verbose_name="Formato do Arquivo")
    log_processamento = models.TextField(blank=True, null=True, verbose_name="Log de Processamento")

    class Meta:
        verbose_name = "Importação de Ponto"
        verbose_name_plural = "Importações de Ponto"

    def __str__(self):
        return f"Importação {self.id} - {self.data_importacao.strftime('%d/%m/%Y %H:%M')}"
