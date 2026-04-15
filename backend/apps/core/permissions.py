from rest_framework import permissions
from backend.apps.core.utils import (
    garantir_empresa_padrao,
    obter_perfil_empresa,
    usuario_tem_perfil_backoffice,
)


def _get_object_company_id(obj):
    direct_company_id = getattr(obj, 'empresa_id', None)
    if direct_company_id:
        return direct_company_id

    for relation_name in ('nota_fiscal', 'lancamento', 'checklist', 'documento'):
        related_obj = getattr(obj, relation_name, None)
        related_company_id = getattr(related_obj, 'empresa_id', None)
        if related_company_id:
            return related_company_id

    return None

class IsActiveCompany(permissions.BasePermission):
    """
    Custom permission to only allow users of the active company to access objects.
    Assumes the object has an 'empresa' attribute.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        return garantir_empresa_padrao(request.user) is not None


    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False

        empresa_ativa = garantir_empresa_padrao(request.user)
        if not empresa_ativa:
            return False

        obj_company_id = _get_object_company_id(obj)
        if obj_company_id:
            return obj_company_id == empresa_ativa.id

        return request.method in permissions.SAFE_METHODS


class IsBackofficeUser(permissions.BasePermission):
    """
    Allows access only to users with at least one active backoffice profile.
    """

    def has_permission(self, request, view):
        return (
            bool(request.user and request.user.is_authenticated)
            and usuario_tem_perfil_backoffice(request.user)
        )


class IsIntakeClientCompany(permissions.BasePermission):
    """
    Permite acesso ao portal cliente para:
    - Usuários com perfil CLIENTE e empresa ativa
    - Usuários de backoffice (para debug/teste)
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if not getattr(request.user, 'empresa_ativa', None):
            return False
        perfil = getattr(request.user, 'perfil', None)
        if perfil == 'CLIENTE':
            return True
        # Backoffice access for debug/testing
        return usuario_tem_perfil_backoffice(request.user)


class IsBackofficeCompany(permissions.BasePermission):
    """
    Allows access only when the active company exists and the active profile is not CLIENTE.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        empresa_ativa = garantir_empresa_padrao(request.user)
        if not empresa_ativa:
            return False

        perfil = obter_perfil_empresa(request.user, empresa_ativa)
        if perfil is None:
            return getattr(request.user, 'is_superuser', False)

        return perfil.perfil != 'CLIENTE'

    def has_object_permission(self, request, view, obj):
        if not self.has_permission(request, view):
            return False

        empresa_ativa = garantir_empresa_padrao(request.user)
        obj_company_id = _get_object_company_id(obj)
        if obj_company_id:
            return obj_company_id == empresa_ativa.id

        return request.method in permissions.SAFE_METHODS
