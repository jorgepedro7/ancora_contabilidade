from rest_framework.response import Response
from rest_framework.views import exception_handler
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated

from .serializers import CustomTokenObtainPairSerializer, UsuarioSerializer
from .models import Usuario
from .utils import garantir_empresa_padrao

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
