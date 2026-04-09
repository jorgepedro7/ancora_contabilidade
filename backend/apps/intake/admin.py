from django.contrib import admin

from .models import ChecklistCompetencia, DocumentoRecebido, LoteExportacaoQuestor, Pendencia, PortalCliente


admin.site.register(PortalCliente)
admin.site.register(ChecklistCompetencia)
admin.site.register(DocumentoRecebido)
admin.site.register(Pendencia)
admin.site.register(LoteExportacaoQuestor)
