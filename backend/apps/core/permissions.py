from rest_framework import permissions

class IsActiveCompany(permissions.BasePermission):
    """
    Custom permission to only allow users of the active company to access objects.
    Assumes the object has an 'empresa' attribute.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Superusers have access to everything
        if request.user.is_superuser:
            return True
        
        # Allow if no active company is set for the user (e.g., during company selection)
        if not request.user.empresa_ativa:
            return True
        
        # Check if the user has a PerfilPermissao for the active company
        # This prevents users without any profile in the active company from accessing data
        return request.user.perfis_permissoes.filter(empresa=request.user.empresa_ativa).exists()


    def has_object_permission(self, request, view, obj):
        # Superusers have full object permissions
        if request.user and request.user.is_superuser:
            return True

        # Read permissions are allowed to any request for authenticated users
        if request.method in permissions.SAFE_METHODS:
            return True

        if not request.user or not request.user.is_authenticated:
            return False

        # If the object has an 'empresa' attribute, check if it matches the user's active company
        if hasattr(obj, 'empresa'):
            return obj.empresa == request.user.empresa_ativa
        
        # If the object doesn't have an 'empresa' attribute, it might be a global resource
        # or a resource directly related to the user, in which case default to True
        return True
