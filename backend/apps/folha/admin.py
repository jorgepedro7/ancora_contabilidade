from django.contrib import admin
from .models import (
    Cargo, Departamento, Funcionario, ContratoTrabalho, 
    FolhaPagamento, HoleriteFuncionario, RegistroPonto, 
    JustificativaPonto, DocumentoFuncionario
)

@admin.register(Cargo)
class CargoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cbo', 'empresa')
    list_filter = ('empresa',)
    search_fields = ('nome', 'cbo')

@admin.register(Departamento)
class DepartamentoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'centro_custo', 'empresa')
    list_filter = ('empresa',)
    search_fields = ('nome', 'centro_custo')

@admin.register(Funcionario)
class FuncionarioAdmin(admin.ModelAdmin):
    list_display = ('nome_completo', 'cpf', 'rg', 'pis', 'ativo', 'empresa')
    list_filter = ('ativo', 'empresa')
    search_fields = ('nome_completo', 'cpf')

@admin.register(ContratoTrabalho)
class ContratoTrabalhoAdmin(admin.ModelAdmin):
    list_display = ('funcionario', 'tipo_contrato', 'cargo', 'salario_base', 'data_inicio', 'ativo', 'empresa')
    list_filter = ('tipo_contrato', 'ativo', 'empresa', 'cargo')
    search_fields = ('funcionario__nome_completo',)
    raw_id_fields = ('funcionario', 'cargo', 'departamento')

@admin.register(FolhaPagamento)
class FolhaPagamentoAdmin(admin.ModelAdmin):
    list_display = ('competencia', 'tipo_folha', 'status', 'data_processamento', 'empresa')
    list_filter = ('tipo_folha', 'status', 'empresa', 'competencia')
    search_fields = ('competencia',)

@admin.register(HoleriteFuncionario)
class HoleriteFuncionarioAdmin(admin.ModelAdmin):
    list_display = ('funcionario', 'folha_pagamento', 'salario_bruto', 'liquido_receber', 'data_pagamento')
    list_filter = ('folha_pagamento__competencia', 'funcionario__empresa')
    search_fields = ('funcionario__nome_completo',)
    raw_id_fields = ('funcionario', 'folha_pagamento')
@admin.register(RegistroPonto)
class RegistroPontoAdmin(admin.ModelAdmin):
    list_display = ('funcionario', 'data', 'total_horas', 'horas_extras', 'atrasos', 'manual')
    list_filter = ('data', 'manual', 'funcionario__empresa')
    search_fields = ('funcionario__nome_completo',)

@admin.register(JustificativaPonto)
class JustificativaPontoAdmin(admin.ModelAdmin):
    list_display = ('funcionario', 'tipo', 'data_inicio', 'data_fim', 'abona_ponto')
    list_filter = ('tipo', 'abona_ponto', 'funcionario__empresa')
    search_fields = ('funcionario__nome_completo', 'descricao')

@admin.register(DocumentoFuncionario)
class DocumentoFuncionarioAdmin(admin.ModelAdmin):
    list_display = ('funcionario', 'tipo', 'descricao', 'data_upload')
    list_filter = ('tipo', 'funcionario__empresa')
    search_fields = ('funcionario__nome_completo', 'descricao')
