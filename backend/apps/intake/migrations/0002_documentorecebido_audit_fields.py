# Generated manually on 2026-04-15

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('intake', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='documentorecebido',
            name='enviado_por',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='documentos_enviados', to=settings.AUTH_USER_MODEL, help_text='Usuário que enviou o documento'),
        ),
        migrations.AddField(
            model_name='documentorecebido',
            name='validado_por',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='documentos_validados', to=settings.AUTH_USER_MODEL, help_text='Usuário que validou o documento'),
        ),
        migrations.AddField(
            model_name='documentorecebido',
            name='validado_em',
            field=models.DateTimeField(blank=True, null=True, help_text='Data e hora da validação'),
        ),
        migrations.AddField(
            model_name='documentorecebido',
            name='origem_upload',
            field=models.CharField(choices=[('BACKOFFICE', 'Backoffice'), ('CLIENTE', 'Cliente'), ('API', 'API')], default='BACKOFFICE', help_text='Origem do upload do documento', max_length=20),
        ),
        migrations.AddField(
            model_name='documentorecebido',
            name='referencia_cliente',
            field=models.TextField(blank=True, null=True, help_text='Referência ou identificador do cliente para o documento'),
        ),
    ]
