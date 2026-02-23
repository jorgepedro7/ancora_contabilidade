import datetime
from decimal import Decimal
import requests
import xml.etree.ElementTree as ET

from django.conf import settings
from django.core.files.base import ContentFile
from django.db import transaction

from lxml import etree
from signxml import XMLSigner, XMLVerifier
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

# Import ReportLab if available
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER
    from reportlab.lib import colors
except ImportError:
    # If ReportLab is not installed, mock its components
    class MockReportLab:
        def __getattr__(self, name):
            return lambda *args, **kwargs: None
    
    A4 = None
    SimpleDocTemplate = MockReportLab
    Paragraph = MockReportLab
    Spacer = MockReportLab
    Table = MockReportLab
    TableStyle = MockReportLab
    getSampleStyleSheet = MockReportLab
    ParagraphStyle = MockReportLab
    TA_CENTER = None
    colors = MockReportLab()

from backend.apps.core.utils import gerar_chave_acesso_nfe
from .models import NotaFiscal, EventoNotaFiscal
from backend.apps.empresas.models import Empresa

class NFeService:
    @staticmethod
    def _load_certificate(empresa):
        if not empresa.certificado_digital_pfx:
            raise ValueError("Certificado digital não configurado para a empresa.")
        
        # O certificado.read() retorna bytes
        pfx_data = empresa.certificado_digital_pfx.read()

        # A senha do certificado deve ser descriptografada se estiver armazenada de forma segura
        # Por simplicidade, assumimos que está em texto claro aqui (NÃO RECOMENDADO EM PRODUÇÃO)
        pfx_password = empresa.certificado_senha.encode('utf-8')

        # Carrega a chave privada e os certificados
        private_key, certificate, additional_certs = serialization.pkcs12.load_key_and_certificates(
            pfx_data,
            pfx_password,
            default_backend()
        )
        return private_key, certificate, additional_certs

    @staticmethod
    def gerar_xml(nota_fiscal: NotaFiscal) -> str:
        # Exemplo simplificado de geração de XML da NF-e
        # Em um sistema real, isso seria muito mais complexo, usando bibliotecas como nfelib
        
        # Cria o elemento raiz
        nfe_tag = etree.Element("NFe", nsmap={
            None: "http://www.portalfiscal.inf.br/nfe",
            "xsi": "http://www.w3.org/2001/XMLSchema-instance"
        })
        infNFe = etree.SubElement(nfe_tag, "infNFe", Id=f"NFe{nota_fiscal.chave_acesso}", versao="4.00")

        # Ide (Identificação da NF-e)
        ide = etree.SubElement(infNFe, "ide")
        etree.SubElement(ide, "cUF").text = "35" # Código IBGE da UF do emitente (SP)
        etree.SubElement(ide, "cNF").text = nota_fiscal.chave_acesso[35:43] # Código numérico NF-e
        etree.SubElement(ide, "natOp").text = "VENDA"
        etree.SubElement(ide, "mod").text = nota_fiscal.modelo
        etree.SubElement(ide, "serie").text = str(nota_fiscal.serie)
        etree.SubElement(ide, "nNF").text = str(nota_fiscal.numero)
        etree.SubElement(ide, "dhEmi").text = nota_fiscal.data_emissao.astimezone(datetime.timezone.utc).isoformat(timespec='seconds') + "-03:00" # Exemplo, ajustar timezone
        etree.SubElement(ide, "tpNF").text = "1" # Saída
        etree.SubElement(ide, "idDest").text = "1" # Operação Interna
        etree.SubElement(ide, "cMunFG").text = "3550308" # Código IBGE do município do Fato Gerador (SP)
        etree.SubElement(ide, "tpImp").text = "1" # Retrato
        etree.SubElement(ide, "tpEmis").text = "1" # Normal
        etree.SubElement(ide, "cDV").text = nota_fiscal.chave_acesso[43] # Dígito Verificador
        etree.SubElement(ide, "tpAmb").text = nota_fiscal.empresa.configuracao_fiscal.ambiente_sefaz # 1-Produção, 2-Homologação
        etree.SubElement(ide, "finNFe").text = nota_fiscal.finalidade
        etree.SubElement(ide, "procEmi").text = "0" # Emissão de NF-e com aplicativo do contribuinte
        etree.SubElement(ide, "verProc").text = "1.0" # Versão do processo de emissão

        # Emitente (Simplificado)
        emit = etree.SubElement(infNFe, "emit")
        etree.SubElement(emit, "CNPJ").text = nota_fiscal.empresa.cnpj
        etree.SubElement(emit, "xNome").text = nota_fiscal.empresa.razao_social
        # ... outros campos do emitente

        # Destinatário (Simplificado)
        dest = etree.SubElement(infNFe, "dest")
        if len(nota_fiscal.destinatario_documento) == 11:
            etree.SubElement(dest, "CPF").text = nota_fiscal.destinatario_documento
        else:
            etree.SubElement(dest, "CNPJ").text = nota_fiscal.destinatario_documento
        etree.SubElement(dest, "xNome").text = nota_fiscal.destinatario_nome
        # ... outros campos do destinatário

        # Itens (Produtos e Serviços)
        for i, item_nf in enumerate(nota_fiscal.itens.all(), 1):
            det = etree.SubElement(infNFe, "det", nItem=str(i))
            prod = etree.SubElement(det, "prod")
            etree.SubElement(prod, "cProd").text = str(item_nf.produto.codigo_interno if item_nf.produto else i)
            etree.SubElement(prod, "xProd").text = item_nf.produto_descricao
            etree.SubElement(prod, "NCM").text = item_nf.produto_ncm
            etree.SubElement(prod, "CFOP").text = item_nf.produto_cfop
            etree.SubElement(prod, "uCom").text = "UN" # Unidade comercial
            etree.SubElement(prod, "qCom").text = str(item_nf.quantidade)
            etree.SubElement(prod, "vUnCom").text = str(item_nf.valor_unitario)
            etree.SubElement(prod, "vProd").text = str(item_nf.valor_total)
            # ... outros campos de produto e impostos (muito complexo para um exemplo simples)

        # Totais
        total = etree.SubElement(infNFe, "total")
        icmsTot = etree.SubElement(total, "ICMSTot")
        etree.SubElement(icmsTot, "vProd").text = str(nota_fiscal.valor_produtos)
        etree.SubElement(icmsTot, "vDesc").text = str(nota_fiscal.valor_desconto)
        etree.SubElement(icmsTot, "vFrete").text = str(nota_fiscal.valor_frete)
        etree.SubElement(icmsTot, "vSeg").text = str(nota_fiscal.valor_seguro)
        etree.SubElement(icmsTot, "vOutro").text = str(nota_fiscal.valor_outras_despesas)
        etree.SubElement(icmsTot, "vICMS").text = str(nota_fiscal.valor_icms)
        etree.SubElement(icmsTot, "vICMSDeson").text = "0.00" # Exemplo
        etree.SubElement(icmsTot, "vNF").text = str(nota_fiscal.valor_total_nf)
        # ... outros totais

        # Informações Adicionais (opcional)
        infAdic = etree.SubElement(infNFe, "infAdic")
        etree.SubElement(infAdic, "infCpl").text = "Documento emitido por software Âncora Contabilidade"


        # Envelopa a NF-e
        nfeProc_tag = etree.Element("nfeProc", versao="4.00", nsmap={None: "http://www.portalfiscal.inf.br/nfe"})
        nfeProc_tag.append(nfe_tag)

        return etree.tostring(nfeProc_tag, encoding="UTF-8", xml_declaration=True, pretty_print=True).decode('utf-8')

    @staticmethod
    def assinar_xml(xml_content: str, empresa: Empresa) -> str:
        private_key, certificate, _ = NFeService._load_certificate(empresa)
        
        root = etree.fromstring(xml_content.encode('utf-8'))
        
        # Encontra o elemento a ser assinado (infNFe)
        signature_node_id = None
        for element in root.iter("{http://www.portalfiscal.inf.br/nfe}infNFe"):
            signature_node_id = element.get("Id")
            break
        
        if not signature_node_id:
            raise ValueError("Não foi possível encontrar o elemento infNFe para assinar.")

        signer = XMLSigner(method=etree.QName("http://www.w3.org/2001/04/xmldsig-more#", "rsa-sha256"),
                           digest_algorithm="sha256",
                           c14n_algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315") # C14N sem comentarios

        # O certificado deve ser uma lista de bytes (PEM ou DER)
        cert_pem = certificate.public_bytes(serialization.Encoding.PEM)

        signed_root = signer.sign(root,
                                  key=private_key,
                                  certs=[cert_pem],
                                  reference_uri=f"#{signature_node_id}")

        return etree.tostring(signed_root, encoding="UTF-8", xml_declaration=True, pretty_print=True).decode('utf-8')

    @staticmethod
    def enviar_sefaz(xml_assinado: str, uf: str, ambiente: str) -> dict:
        # Este é um placeholder. A integração com SEFAZ é via SOAP e muito complexa.
        # Envolve URLs de webservices específicos para cada UF e ambiente,
        # certificados de cadeia, etc.
        # Aqui, apenas um mock para simular o envio.

        print(f"Simulando envio para SEFAZ (UF: {uf}, Ambiente: {ambiente})...")
        print("XML Assinado:\n", xml_assinado[:500], "...") # Log do XML para debug", xml_assinado[:500], "...") # Log do XML para debug
        
        # Simular resposta do SEFAZ
        if ambiente == '2': # Homologação
            # Em homologação, sempre "autoriza" para fins de teste
            return {
                'status_sefaz': 'AUTORIZADA',
                'codigo_retorno': '100',
                'mensagem_retorno': 'Autorizado o uso da NF-e (Simulação Homologação)',
                'protocolo': f'{uf}H{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}'
            }
        else: # Produção - simula sucesso ou falha aleatória
            if datetime.datetime.now().second % 2 == 0: # 50% de chance de sucesso
                return {
                    'status_sefaz': 'AUTORIZADA',
                    'codigo_retorno': '100',
                    'mensagem_retorno': 'Autorizado o uso da NF-e',
                    'protocolo': f'{uf}P{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}'
                }
            else:
                return {
                    'status_sefaz': 'REJEITADA',
                    'codigo_retorno': '204',
                    'mensagem_retorno': 'Rejeição: Duplicidade de NF-e',
                    'protocolo': None
                }

    @staticmethod
    def processar_retorno(nota_fiscal: NotaFiscal, retorno_sefaz: dict):
        with transaction.atomic():
            nota_fiscal.status = retorno_sefaz['status_sefaz']
            nota_fiscal.codigo_retorno = retorno_sefaz['codigo_retorno']
            nota_fiscal.mensagem_retorno = retorno_sefaz['mensagem_retorno']
            if retorno_sefaz['protocolo']:
                nota_fiscal.protocolo = retorno_sefaz['protocolo']
            nota_fiscal.save()

            if nota_fiscal.status == 'AUTORIZADA':
                # Salvar o XML autorizado (placeholder)
                pass
            
            EventoNotaFiscal.objects.create(
                empresa=nota_fiscal.empresa,
                nota_fiscal=nota_fiscal,
                tipo_evento='PROCESSAMENTO', # Criar um tipo de evento para autorização
                justificativa=retorno_sefaz['mensagem_retorno'],
                protocolo_retorno=retorno_sefaz['protocolo']
            )

    @staticmethod
    def gerar_danfe(nota_fiscal: NotaFiscal) -> bytes:
        if not (SimpleDocTemplate and A4):
            raise ImportError("ReportLab não está instalado ou configurado corretamente.")
        
        # Cria um buffer para o PDF
        from io import BytesIO
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, title=f"DANFE NF-e {nota_fiscal.numero}")
        styles = getSampleStyleSheet()
        
        story = []

        # Título
        story.append(Paragraph(f"DANFE - Documento Auxiliar da Nota Fiscal Eletrônica", styles['h2']))
        story.append(Paragraph(f"NF-e Nº {nota_fiscal.numero} - Série {nota_fiscal.serie}", styles['h3']))
        story.append(Spacer(1, 0.2 * A4[1])) # Espaçamento

        # Dados da Empresa Emitente
        story.append(Paragraph(f"<b>EMITENTE:</b> {nota_fiscal.empresa.razao_social}", styles['Normal']))
        story.append(Paragraph(f"CNPJ: {nota_fiscal.empresa.cnpj} - IE: {nota_fiscal.empresa.inscricao_estadual}", styles['Normal']))
        story.append(Paragraph(nota_fiscal.empresa.endereco_completo, styles['Normal']))
        story.append(Spacer(1, 0.1 * A4[1]))

        # Dados do Destinatário
        story.append(Paragraph(f"<b>DESTINATÁRIO:</b> {nota_fiscal.destinatario_nome}", styles['Normal']))
        story.append(Paragraph(f"CPF/CNPJ: {nota_fiscal.destinatario_documento} - IE: {nota_fiscal.destinatario_ie if nota_fiscal.destinatario_ie else 'ISENTO'}", styles['Normal']))
        story.append(Paragraph(f"{nota_fiscal.destinatario_logradouro}, {nota_fiscal.destinatario_numero}, {nota_fiscal.destinatario_bairro}", styles['Normal']))
        story.append(Paragraph(f"{nota_fiscal.destinatario_municipio} - {nota_fiscal.destinatario_uf} - CEP: {nota_fiscal.destinatario_cep}", styles['Normal']))
        story.append(Spacer(1, 0.1 * A4[1]))

        # Chave de Acesso
        chave_style = ParagraphStyle(
            'chave_acesso',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=12,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#C6A348') # Dourado Institucional
        )
        story.append(Paragraph(f"CHAVE DE ACESSO: <font size=14>{nota_fiscal.chave_acesso}</font>", chave_style))
        story.append(Spacer(1, 0.1 * A4[1]))
        
        # Itens da NF
        story.append(Paragraph("<b>PRODUTOS/SERVIÇOS DA NOTA</b>", styles['h3']))
        data = [['Cód. Prod', 'Descrição', 'NCM', 'CFOP', 'Qtd', 'Un', 'Vl Unit', 'Vl Total']]
        for item in nota_fiscal.itens.all():
            data.append([
                item.produto.codigo_interno if item.produto else '',
                item.produto_descricao,
                item.produto_ncm,
                item.produto_cfop,
                str(item.quantidade),
                'UN', # placeholder
                str(item.valor_unitario),
                str(item.valor_total)
            ])
        
        item_table = Table(data, colWidths=[60, 180, 60, 40, 40, 20, 60, 60])
        item_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0F1E3A')), # Azul Marinho
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#111111')), # Preto Institucional
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#C6A348')), # Dourado Institucional
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#C6A348')),
        ]))
        story.append(item_table)
        story.append(Spacer(1, 0.1 * A4[1]))

        # Totais da NF
        story.append(Paragraph("<b>TOTAIS DA NOTA</b>", styles['h3']))
        totais_data = [
            ['Valor Total dos Produtos', str(nota_fiscal.valor_produtos)],
            ['Valor do Frete', str(nota_fiscal.valor_frete)],
            ['Valor do Desconto', str(nota_fiscal.valor_desconto)],
            ['Valor Total da Nota', str(nota_fiscal.valor_total_nf)],
        ]
        totais_table = Table(totais_data, colWidths=[250, 250])
        totais_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#111111')),
            ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#0F1E3A')),
            ('BACKGROUND', (0, 2), (-1, 2), colors.HexColor('#111111')),
            ('BACKGROUND', (0, 3), (-1, 3), colors.HexColor('#0F1E3A')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#C6A348')),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#C6A348')),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, -1), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, -1), (1, -1), 'Helvetica-Bold'),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
        ]))
        story.append(totais_table)

        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

    @staticmethod
    def cancelar_nota(nota_fiscal: NotaFiscal, justificativa: str):
        if nota_fiscal.status != 'AUTORIZADA':
            raise ValueError("A nota fiscal não pode ser cancelada pois não está autorizada.")
        if len(justificativa) < 15: # Exemplo de validação
            raise ValueError("Justificativa para cancelamento deve ter no mínimo 15 caracteres.")

        # Gerar XML de evento de cancelamento (simplificado)
        xml_evento_str = f"<evento><justificativa>{justificativa}</justificativa></evento>"
        
        # Assinar XML do evento (reutiliza lógica de assinatura)
        # Em um cenário real, o XML do evento seria bem estruturado conforme a SEFAZ
        xml_assinado = NFeService.assinar_xml(xml_evento_str, nota_fiscal.empresa)

        # Simular envio para SEFAZ
        retorno_sefaz = NFeService.enviar_sefaz(xml_assinado, nota_fiscal.empresa.uf, nota_fiscal.empresa.configuracao_fiscal.ambiente_sefaz)

        if retorno_sefaz['status_sefaz'] == 'AUTORIZADA': # Em eventos, "autorizada" significa que o evento foi processado
            with transaction.atomic():
                nota_fiscal.status = 'CANCELADA'
                nota_fiscal.protocolo = retorno_sefaz['protocolo'] # Protocolo de cancelamento
                nota_fiscal.mensagem_retorno = retorno_sefaz['mensagem_retorno']
                nota_fiscal.save()

                EventoNotaFiscal.objects.create(
                    empresa=nota_fiscal.empresa,
                    nota_fiscal=nota_fiscal,
                    tipo_evento='110110', # Código de evento de cancelamento
                    justificativa=justificativa,
                    xml_evento=ContentFile(xml_assinado.encode('utf-8'), name=f'cancelamento_{nota_fiscal.chave_acesso}.xml'),
                    protocolo_retorno=retorno_sefaz['protocolo']
                )
                return True
        else:
            raise Exception(f"Falha ao cancelar NF-e: {retorno_sefaz['mensagem_retorno']}")

    @staticmethod
    def carta_correcao(nota_fiscal: NotaFiscal, texto_correcao: str):
        if nota_fiscal.status != 'AUTORIZADA':
            raise ValueError("Carta de Correção só pode ser emitida para NF-e autorizada.")
        if len(texto_correcao) < 15: # Exemplo de validação
            raise ValueError("Texto da Carta de Correção deve ter no mínimo 15 caracteres.")

        # Gerar XML de evento de carta de correção (simplificado)
        xml_evento_str = f"<evento><textoCorrecao>{texto_correcao}</textoCorrecao></evento>"
        xml_assinado = NFeService.assinar_xml(xml_evento_str, nota_fiscal.empresa)

        # Simular envio para SEFAZ
        retorno_sefaz = NFeService.enviar_sefaz(xml_assinado, nota_fiscal.empresa.uf, nota_fiscal.empresa.configuracao_fiscal.ambiente_sefaz)

        if retorno_sefaz['status_sefaz'] == 'AUTORIZADA': # Evento processado
            with transaction.atomic():
                EventoNotaFiscal.objects.create(
                    empresa=nota_fiscal.empresa,
                    nota_fiscal=nota_fiscal,
                    tipo_evento='110114', # Código de evento de carta de correção
                    justificativa=texto_correcao,
                    xml_evento=ContentFile(xml_assinado.encode('utf-8'), name=f'correcao_{nota_fiscal.chave_acesso}.xml'),
                    protocolo_retorno=retorno_sefaz['protocolo']
                )
                return True
        else:
            raise Exception(f"Falha ao emitir Carta de Correção: {retorno_sefaz['mensagem_retorno']}")
