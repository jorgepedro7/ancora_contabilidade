from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import PerfilPermissao, Usuario
from .utils import garantir_empresa_padrao


def montar_contexto_empresa_ativa(user):
    empresa = getattr(user, 'empresa_ativa', None)
    contexto = {
        'empresa_ativa_id': str(empresa.id) if empresa else None,
        'empresa_ativa_nome': empresa.nome_exibicao if empresa else None,
        'perfil_empresa': None,
        'permissoes': {},
    }

    if not empresa:
        return contexto

    try:
        perfil_empresa = PerfilPermissao.objects.get(usuario=user, empresa=empresa, ativo=True)
    except PerfilPermissao.DoesNotExist:
        return contexto

    contexto['perfil_empresa'] = perfil_empresa.perfil
    contexto['permissoes'] = {
        'pode_emitir_nf': perfil_empresa.pode_emitir_nf,
        'pode_cancelar_nf': perfil_empresa.pode_cancelar_nf,
        'pode_ver_folha': perfil_empresa.pode_ver_folha,
    }
    return contexto

class UsuarioSerializer(serializers.ModelSerializer):
    empresa_ativa_id = serializers.UUIDField(source='empresa_ativa.id', read_only=True)
    empresa_ativa_nome = serializers.CharField(source='empresa_ativa.nome_exibicao', read_only=True)
    perfil_empresa = serializers.SerializerMethodField()
    permissoes = serializers.SerializerMethodField()

    class Meta:
        model = Usuario
        fields = [
            'id', 'email', 'nome', 'telefone', 'avatar',
            'empresa_ativa_id', 'empresa_ativa_nome',
            'perfil_empresa', 'permissoes',
        ]
        read_only_fields = ['id', 'empresa_ativa_id', 'empresa_ativa_nome', 'perfil_empresa', 'permissoes']

    def get_perfil_empresa(self, obj):
        return montar_contexto_empresa_ativa(obj)['perfil_empresa']

    def get_permissoes(self, obj):
        return montar_contexto_empresa_ativa(obj)['permissoes']

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        garantir_empresa_padrao(user)
        contexto_empresa = montar_contexto_empresa_ativa(user)

        # Adicione informações customizadas ao token
        token['email'] = user.email
        token['nome'] = user.nome
        token['empresa_ativa_id'] = contexto_empresa['empresa_ativa_id']
        token['empresa_ativa_nome'] = contexto_empresa['empresa_ativa_nome']
        token['perfil_empresa'] = contexto_empresa['perfil_empresa']
        token['permissoes'] = contexto_empresa['permissoes']

        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        garantir_empresa_padrao(self.user)
        # Adiciona os dados do usuário ao payload de resposta do login
        data['user'] = UsuarioSerializer(self.user).data
        return data
