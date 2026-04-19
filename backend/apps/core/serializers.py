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


class UsuarioGestaoSerializer(serializers.ModelSerializer):
    perfil = serializers.CharField(write_only=True)
    senha_temporaria = serializers.CharField(write_only=True, required=False)
    perfil_empresa = serializers.SerializerMethodField()
    pode_emitir_nf = serializers.SerializerMethodField()
    pode_cancelar_nf = serializers.SerializerMethodField()
    pode_ver_folha = serializers.SerializerMethodField()

    PERFIS_VALIDOS = {code for code, _ in PerfilPermissao.PERFIS_CHOICES}

    class Meta:
        model = Usuario
        fields = [
            'id', 'email', 'nome', 'telefone',
            'perfil', 'senha_temporaria',
            'perfil_empresa', 'pode_emitir_nf', 'pode_cancelar_nf', 'pode_ver_folha',
            'is_active', 'date_joined',
        ]
        read_only_fields = ['id', 'email', 'date_joined', 'is_active', 'perfil_empresa', 'pode_emitir_nf', 'pode_cancelar_nf', 'pode_ver_folha']

    def _get_perfil_obj(self, obj):
        cache_attr = f'_perfil_cache_{obj.pk}'
        if not hasattr(self, cache_attr):
            request = self.context.get('request')
            empresa = getattr(request.user, 'empresa_ativa', None) if request else None
            if request and empresa:
                try:
                    result = PerfilPermissao.objects.get(usuario=obj, empresa=empresa, ativo=True)
                except PerfilPermissao.DoesNotExist:
                    result = None
            else:
                result = None
            setattr(self, cache_attr, result)
        return getattr(self, cache_attr)

    def get_perfil_empresa(self, obj):
        p = self._get_perfil_obj(obj)
        return p.perfil if p else None

    def get_pode_emitir_nf(self, obj):
        p = self._get_perfil_obj(obj)
        return p.pode_emitir_nf if p else False

    def get_pode_cancelar_nf(self, obj):
        p = self._get_perfil_obj(obj)
        return p.pode_cancelar_nf if p else False

    def get_pode_ver_folha(self, obj):
        p = self._get_perfil_obj(obj)
        return p.pode_ver_folha if p else False

    def validate_perfil(self, value):
        if value not in self.PERFIS_VALIDOS:
            raise serializers.ValidationError(f'Perfil inválido. Escolha entre: {", ".join(sorted(self.PERFIS_VALIDOS))}')
        return value
