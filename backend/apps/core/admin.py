from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario

class UsuarioAdmin(UserAdmin):
    list_display = ('email', 'nome', 'is_staff', 'is_active', 'empresa_ativa')
    search_fields = ('email', 'nome')
    ordering = ('email',)
    filter_horizontal = ()
    list_filter = ('is_staff', 'is_active', 'empresa_ativa')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Informações Pessoais', {'fields': ('nome', 'telefone', 'avatar', 'empresa_ativa')}),
        ('Permissões', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Datas Importantes', {'fields': ('last_login', 'date_joined')}),
    )

admin.site.register(Usuario, UsuarioAdmin)
