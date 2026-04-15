import csv
import hashlib
import io
import os
from datetime import date, datetime

from django.core.files.base import ContentFile
from django.utils import timezone

from .models import ChecklistCompetencia, DocumentoRecebido, LoteExportacaoQuestor, Pendencia


ALLOWED_EXTENSIONS = {'.pdf', '.xml', '.csv', '.zip', '.jpg', '.jpeg', '.png'}


def get_allowed_extensions():
    """Extensões permitidas para upload pelo cliente no MVP."""
    return ['.pdf', '.xml', '.csv', '.zip', '.jpg', '.jpeg', '.png']


def validate_file_extension(filename):
    """Retorna (is_valid, error_message)."""
    _, ext = os.path.splitext(filename or '')
    ext = ext.lower()

    allowed = get_allowed_extensions()
    if ext not in allowed:
        return False, f"Extensão {ext or '(sem extensão)'} não permitida. Permitidas: {', '.join(allowed)}"
    return True, None


def validate_file_size(file_obj, max_size_mb=10):
    """Retorna (is_valid, error_message)."""
    if not file_obj:
        return False, 'Arquivo não fornecido'

    max_bytes = max_size_mb * 1024 * 1024
    if getattr(file_obj, 'size', 0) > max_bytes:
        return False, f'Arquivo excede {max_size_mb}MB'
    return True, None


def parse_competencia(value):
    if isinstance(value, date):
        return value.replace(day=1)

    for fmt in ('%Y-%m-%d', '%Y-%m'):
        try:
            parsed = datetime.strptime(value, fmt).date()
            return parsed.replace(day=1)
        except (TypeError, ValueError):
            continue
    raise ValueError('Competência inválida. Use YYYY-MM ou YYYY-MM-DD.')


def classificar_modulo(tipo_documento):
    if tipo_documento in {'FISCAL', 'FOLHA', 'FINANCEIRO', 'CONTRATUAL'}:
        return tipo_documento
    return 'GERAL'


def calcular_hash_arquivo(arquivo):
    hash_obj = hashlib.sha256()
    for chunk in arquivo.chunks():
        hash_obj.update(chunk)
    arquivo.seek(0)
    return hash_obj.hexdigest()


def validar_documento(attrs):
    problemas = []
    arquivo = attrs.get('arquivo')
    tipo_documento = attrs.get('tipo_documento')
    competencia = attrs.get('competencia')

    if arquivo:
        ext = os.path.splitext(arquivo.name)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            problemas.append(f'Extensão {ext or "desconhecida"} não suportada.')

    if competencia and competencia > date.today().replace(day=1):
        problemas.append('Competência futura não é permitida.')

    if tipo_documento == 'FISCAL' and not attrs.get('nota_fiscal'):
        problemas.append('Documento fiscal precisa estar vinculado a uma nota fiscal.')

    if tipo_documento in {'FOLHA', 'CONTRATUAL'} and not attrs.get('funcionario') and not attrs.get('contrato_trabalho'):
        problemas.append('Documento de folha/contratual precisa estar vinculado a um funcionário ou contrato.')

    status = 'VALIDADO' if not problemas else 'REPROVADO'
    logs = [{'nivel': 'erro', 'mensagem': mensagem} for mensagem in problemas]
    if not logs:
        logs.append({'nivel': 'info', 'mensagem': 'Documento validado automaticamente.'})
    return status, logs


def obter_ou_criar_checklist(empresa, competencia, tipo_documento):
    checklist, _ = ChecklistCompetencia.objects.get_or_create(
        empresa=empresa,
        competencia=competencia,
        modulo=classificar_modulo(tipo_documento),
    )
    return checklist


def atualizar_status_checklist(checklist):
    documentos = checklist.documentos.all()
    pendencias_abertas = checklist.pendencias.exclude(status='RESOLVIDA').count()

    if not documentos.exists():
        checklist.status = 'PENDENTE'
    elif pendencias_abertas:
        checklist.status = 'EM_ANDAMENTO'
    elif documentos.filter(status='REPROVADO').exists():
        checklist.status = 'EM_ANDAMENTO'
    else:
        checklist.status = 'CONCLUIDO'

    checklist.save(update_fields=['status', 'atualizado_em'])
    return checklist


def sincronizar_pendencias_documento(documento):
    if documento.status == 'VALIDADO':
        documento.pendencias.exclude(status='RESOLVIDA').update(status='RESOLVIDA')
        if documento.checklist:
            atualizar_status_checklist(documento.checklist)
        return

    descricao = '\n'.join(item['mensagem'] for item in (documento.log_validacao or []))
    pendencia, created = Pendencia.objects.get_or_create(
        empresa=documento.empresa,
        documento=documento,
        defaults={
            'checklist': documento.checklist,
            'titulo': f'Pendência no documento {documento.titulo}',
            'descricao': descricao or 'Documento reprovado na validação.',
            'status': 'ABERTA',
            'severidade': 'ALTA',
        },
    )
    if not created:
        pendencia.checklist = documento.checklist
        pendencia.descricao = descricao or pendencia.descricao
        pendencia.status = 'ABERTA'
        pendencia.severidade = 'ALTA'
        pendencia.save()

    if documento.checklist:
        atualizar_status_checklist(documento.checklist)


def gerar_lote_questor(empresa, competencia):
    documentos = DocumentoRecebido.objects.filter(
        empresa=empresa,
        competencia=competencia,
        status='VALIDADO',
    ).select_related('funcionario', 'contrato_trabalho', 'nota_fiscal')

    lote = LoteExportacaoQuestor.objects.create(
        empresa=empresa,
        competencia=competencia,
        status='PROCESSANDO',
    )

    output = io.StringIO()
    writer = csv.writer(output, delimiter=';')
    writer.writerow([
        'titulo',
        'tipo_documento',
        'tipo_entrega',
        'competencia',
        'funcionario',
        'contrato',
        'nota_fiscal',
        'arquivo',
        'hash_arquivo',
    ])

    for documento in documentos:
        writer.writerow([
            documento.titulo,
            documento.tipo_documento,
            documento.tipo_entrega,
            documento.competencia.isoformat(),
            documento.funcionario.nome_completo if documento.funcionario else '',
            documento.contrato_trabalho.id if documento.contrato_trabalho else '',
            documento.nota_fiscal.numero if documento.nota_fiscal else '',
            documento.arquivo.name,
            documento.hash_arquivo or '',
        ])

    file_name = f'questor_{empresa.cnpj}_{competencia:%Y%m}_{timezone.now():%Y%m%d%H%M%S}.csv'
    lote.arquivo_exportado.save(file_name, ContentFile(output.getvalue().encode('utf-8')))
    lote.status = 'EXPORTADO'
    lote.processado_em = timezone.now()
    lote.resumo = {
        'documentos_exportados': documentos.count(),
        'competencia': competencia.isoformat(),
    }
    lote.save(update_fields=['arquivo_exportado', 'status', 'processado_em', 'resumo', 'atualizado_em'])
    return lote
