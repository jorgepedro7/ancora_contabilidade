from django.core.management.base import BaseCommand, CommandError

from backend.apps.core.utils import obter_empresa_principal
from backend.apps.intake.services import gerar_lote_questor, parse_competencia


class Command(BaseCommand):
    help = 'Gera um lote Questor a partir dos documentos validados do intake.'

    def add_arguments(self, parser):
        parser.add_argument('--competencia', required=True, help='Competência no formato YYYY-MM ou YYYY-MM-DD.')

    def handle(self, *args, **options):
        empresa = obter_empresa_principal()
        if not empresa:
            raise CommandError('Nenhuma empresa ativa encontrada.')

        try:
            competencia = parse_competencia(options['competencia'])
        except ValueError as exc:
            raise CommandError(str(exc)) from exc

        lote = gerar_lote_questor(empresa, competencia)
        self.stdout.write(self.style.SUCCESS(f'Lote gerado: {lote.id}'))
