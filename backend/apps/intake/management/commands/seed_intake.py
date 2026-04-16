from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone

from backend.apps.core.models import PerfilPermissao
from backend.apps.empresas.models import Empresa
from backend.apps.intake.models import DocumentoRecebido, PortalCliente

User = get_user_model()


class Command(BaseCommand):
    help = 'Popula dados iniciais para o módulo intake (idempotente).'

    def handle(self, *args, **options):
        # Empresa de teste
        empresa, _ = Empresa.objects.get_or_create(
            cnpj='00000000000000',
            defaults={
                'razao_social': 'Âncora Contabilidade Teste LTDA',
                'nome_fantasia': 'Âncora Contabilidade Teste',
                'regime_tributario': 'SN',
                'cnae_principal': '1234567',
                'cep': '01001000',
                'logradouro': 'Praça da Sé',
                'numero': '100',
                'bairro': 'Centro',
                'municipio': 'São Paulo',
                'uf': 'SP',
            },
        )
        self.stdout.write(f'Empresa: {empresa.nome_fantasia}')

        # Usuário backoffice
        backoffice, created = User.objects.get_or_create(
            email='backoffice@seed.test',
            defaults={
                'nome': 'Backoffice Seed',
                'empresa_ativa': empresa,
                'is_active': True,
            },
        )
        if created:
            backoffice.set_password('senha123')
            backoffice.save()
        PerfilPermissao.objects.get_or_create(usuario=backoffice, empresa=empresa, defaults={'perfil': 'ADMIN'})
        self.stdout.write(f'Backoffice: {backoffice.email}')

        # Usuário cliente
        cliente, created = User.objects.get_or_create(
            email='cliente@seed.test',
            defaults={
                'nome': 'Cliente Seed',
                'empresa_ativa': empresa,
                'is_active': True,
            },
        )
        if created:
            cliente.set_password('senha123')
            cliente.save()
        PerfilPermissao.objects.get_or_create(usuario=cliente, empresa=empresa, defaults={'perfil': 'CLIENTE'})
        self.stdout.write(f'Cliente: {cliente.email}')

        # Portal — lookup por empresa+slug para garantir que aponta para a empresa correta
        portal, _ = PortalCliente.objects.get_or_create(
            slug='portal-ancora',
            empresa=empresa,
            defaults={
                'email_responsavel': 'contato@ancora.local',
                'telefone_responsavel': '(11) 3000-0000',
                'recebe_alertas': True,
            },
        )
        self.stdout.write(f'Portal: {portal.slug}')

        # Documento validado (backoffice)
        DocumentoRecebido.objects.get_or_create(
            portal_cliente=portal,
            empresa=empresa,
            titulo='Documentação de Teste - Validado',
            tipo_documento='FINANCEIRO',
            competencia='2026-04-01',
            defaults={
                'tipo_entrega': 'UPLOAD',
                'arquivo': ContentFile(b'seed-backoffice', name='seed_backoffice.pdf'),
                'status': 'VALIDADO',
                'origem_upload': 'BACKOFFICE',
                'enviado_por': backoffice,
                'validado_por': backoffice,
                'validado_em': timezone.now(),
                'observacoes': 'Criado pelo seed',
            },
        )
        self.stdout.write('Doc validado: criado')

        # Documento novo do cliente
        DocumentoRecebido.objects.get_or_create(
            portal_cliente=portal,
            empresa=empresa,
            titulo='Documentação de Cliente - Em Triagem',
            tipo_documento='FISCAL',
            competencia='2026-04-01',
            defaults={
                'tipo_entrega': 'UPLOAD',
                'arquivo': ContentFile(b'seed-cliente', name='seed_cliente.pdf'),
                'status': 'NOVO',
                'origem_upload': 'CLIENTE',
                'enviado_por': cliente,
                'referencia_cliente': 'NF-2026-001',
                'observacoes': 'Enviado por cliente para teste',
            },
        )
        self.stdout.write('Doc novo (cliente): criado')

        self.stdout.write(self.style.SUCCESS('Seed completo!'))
