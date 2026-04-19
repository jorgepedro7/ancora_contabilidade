from rest_framework.response import Response
from rest_framework.views import exception_handler
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.shortcuts import get_object_or_404

from .serializers import CustomTokenObtainPairSerializer, UsuarioSerializer, UsuarioGestaoSerializer
from .models import Usuario, PerfilPermissao
from .utils import garantir_empresa_padrao, obter_perfil_empresa
from .permissions import IsBackofficeCompany

def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    if response is not None:
        custom_response_data = {
            'success': False,
            'status_code': response.status_code,
            'errors': [],
            'message': ''
        }

        if isinstance(response.data, dict):
            # Handle validation errors specifically
            if 'detail' in response.data:
                custom_response_data['message'] = response.data['detail']
            else:
                for key, value in response.data.items():
                    error_message = value[0] if isinstance(value, list) else value
                    custom_response_data['errors'].append({
                        'field': key,
                        'message': error_message
                    })
                custom_response_data['message'] = 'Erro de validação.'
        else:
            custom_response_data['message'] = response.data

        response.data = custom_response_data
    return response

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class PerfilUsuarioView(generics.RetrieveAPIView):
    serializer_class = UsuarioSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        garantir_empresa_padrao(self.request.user)
        return self.request.user

class HealthCheckView(generics.GenericAPIView):
    permission_classes = [] # No authentication needed for health check

    def get(self, request, *args, **kwargs):
        return Response({'status': 'ok', 'message': 'API is running smoothly'}, status=status.HTTP_200_OK)


class UsuarioViewSet(viewsets.ModelViewSet):
    serializer_class = UsuarioGestaoSerializer
    permission_classes = [IsBackofficeCompany]
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def _get_empresa(self):
        return garantir_empresa_padrao(self.request.user)

    def _exigir_admin(self, empresa):
        if getattr(self.request.user, 'is_superuser', False):
            return
        perfil = obter_perfil_empresa(self.request.user, empresa)
        if perfil is None or perfil.perfil != 'ADMIN':
            raise PermissionDenied('Apenas administradores podem gerenciar usuários.')

    def get_object(self):
        queryset = self.get_queryset()
        lookup = self.kwargs[self.lookup_field]
        obj = get_object_or_404(queryset, pk=lookup)
        # empresa isolation already enforced by get_queryset; skip generic object permission
        return obj

    def get_queryset(self):
        empresa = self._get_empresa()
        tipo = self.request.query_params.get('tipo', 'equipe')
        qs = PerfilPermissao.objects.filter(empresa=empresa, ativo=True)
        if tipo == 'cliente':
            qs = qs.filter(perfil='CLIENTE')
        else:
            qs = qs.exclude(perfil='CLIENTE')
        usuario_ids = qs.values_list('usuario_id', flat=True)
        return Usuario.objects.filter(id__in=usuario_ids).order_by('nome')

    def perform_create(self, serializer):
        empresa = self._get_empresa()
        self._exigir_admin(empresa)
        perfil = serializer.validated_data.pop('perfil')
        senha = serializer.validated_data.pop('senha_temporaria', None)

        with transaction.atomic():
            user = Usuario(
                email=self.request.data.get('email', ''),
                nome=serializer.validated_data['nome'],
                telefone=serializer.validated_data.get('telefone', ''),
                empresa_ativa=empresa,
            )
            if senha:
                user.set_password(senha)
            else:
                user.set_unusable_password()
            user.save()
            PerfilPermissao.objects.create(usuario=user, empresa=empresa, perfil=perfil)

        serializer.instance = user

    def perform_update(self, serializer):
        empresa = self._get_empresa()
        self._exigir_admin(empresa)
        user = serializer.instance

        if user == self.request.user:
            raise ValidationError({'detail': 'Você não pode alterar o próprio perfil.'})

        novo_perfil = serializer.validated_data.pop('perfil', None)
        serializer.validated_data.pop('senha_temporaria', None)
        serializer.save()

        if novo_perfil:
            PerfilPermissao.objects.filter(usuario=user, empresa=empresa).update(perfil=novo_perfil)

    def perform_destroy(self, instance):
        empresa = self._get_empresa()
        self._exigir_admin(empresa)
        if instance == self.request.user:
            raise ValidationError({'detail': 'Você não pode desativar a si mesmo.'})
        instance.is_active = False
        instance.save(update_fields=['is_active'])
        PerfilPermissao.objects.filter(usuario=instance, empresa=empresa).update(ativo=False)

    @action(detail=True, methods=['post'], url_path='reativar')
    def reativar(self, request, pk=None):
        empresa = self._get_empresa()
        self._exigir_admin(empresa)
        # Look up across all users linked to this empresa (including inactive)
        usuario_ids = PerfilPermissao.objects.filter(empresa=empresa).values_list('usuario_id', flat=True)
        instance = get_object_or_404(Usuario, pk=pk, id__in=usuario_ids)
        instance.is_active = True
        instance.save(update_fields=['is_active'])
        PerfilPermissao.objects.filter(usuario=instance, empresa=empresa).update(ativo=True)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
