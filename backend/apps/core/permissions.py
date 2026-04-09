from rest_framework import permissions
from backend.apps.core.utils import garantir_empresa_padrao

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
        # Read permissions are allowed to any request for authenticated users
        if request.method in permissions.SAFE_METHODS:
            return True

        if not request.user or not request.user.is_authenticated:
            return False

        empresa_ativa = garantir_empresa_padrao(request.user)
        if not empresa_ativa:
            return False

        # If the object has an 'empresa' attribute, check if it matches the user's active company
        if hasattr(obj, 'empresa'):
            return obj.empresa == empresa_ativa
        
        # If the object doesn't have an 'empresa' attribute, it might be a global resource
        # or a resource directly related to the user, in which case default to True
        return True
