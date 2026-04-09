from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from backend.apps.core.utils import obter_empresa_principal
from backend.apps.intake.models import ChecklistCompetencia, DocumentoRecebido, PortalCliente
from backend.apps.intake.services import (
    calcular_hash_arquivo,
    obter_ou_criar_checklist,
    parse_competencia,
    sincronizar_pendencias_documento,
    validar_documento,
)


class Command(BaseCommand):
    help = 'Cria dados básicos de demonstração para o módulo intake.'

    def handle(self, *args, **options):
        empresa = obter_empresa_principal()
        if not empresa:
            self.stdout.write(self.style.WARNING('Nenhuma empresa ativa encontrada.'))
            return

        portal, _ = PortalCliente.objects.get_or_create(
            empresa=empresa,
            slug='portal-ancora',
            defaults={'email_responsavel': 'financeiro@ancora.local'},
        )

        competencia = parse_competencia('2026-03')
        checklist = obter_ou_criar_checklist(empresa, competencia, 'FINANCEIRO')
        documento, created = DocumentoRecebido.objects.get_or_create(
            empresa=empresa,
            titulo='Extrato Bancário Março',
            tipo_documento='FINANCEIRO',
            tipo_entrega='UPLOAD',
            competencia=competencia,
            defaults={
                'portal_cliente': portal,
                'checklist': checklist,
                'arquivo': ContentFile(b'extrato-marco', name='extrato_marco.pdf'),
            },
        )

        if created or not documento.hash_arquivo:
            documento.hash_arquivo = calcular_hash_arquivo(documento.arquivo)
            status, logs = validar_documento({
                'arquivo': documento.arquivo,
                'tipo_documento': documento.tipo_documento,
                'competencia': documento.competencia,
            })
            documento.status = status
            documento.log_validacao = logs
            documento.save(update_fields=['hash_arquivo', 'status', 'log_validacao', 'atualizado_em'])
            sincronizar_pendencias_documento(documento)

        self.stdout.write(self.style.SUCCESS('Seed do intake concluído.'))
