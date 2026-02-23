from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Usuario, PerfilPermissao # Importe PerfilPermissao

class UsuarioSerializer(serializers.ModelSerializer):
    empresa_ativa_id = serializers.UUIDField(source='empresa_ativa.id', read_only=True)
    empresa_ativa_nome = serializers.CharField(source='empresa_ativa.nome_fantasia', read_only=True)

    class Meta:
        model = Usuario
        fields = ['id', 'email', 'nome', 'telefone', 'avatar', 'empresa_ativa_id', 'empresa_ativa_nome']
        read_only_fields = ['id', 'empresa_ativa_id', 'empresa_ativa_nome']

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Adicione informações customizadas ao token
        token['email'] = user.email
        token['nome'] = user.nome
        if user.empresa_ativa:
            token['empresa_ativa_id'] = str(user.empresa_ativa.id)
            token['empresa_ativa_nome'] = user.empresa_ativa.nome_fantasia
            # Adicionar perfis e permissões do usuário para a empresa ativa
            try:
                perfil_empresa = PerfilPermissao.objects.get(usuario=user, empresa=user.empresa_ativa)
                token['perfil_empresa'] = perfil_empresa.perfil
                # Adicione as permissões granulares aqui
                token['permissoes'] = {
                    'pode_emitir_nf': perfil_empresa.pode_emitir_nf,
                    'pode_cancelar_nf': perfil_empresa.pode_cancelar_nf,
                    'pode_ver_folha': perfil_empresa.pode_ver_folha,
                    # ... outras permissões
                }
            except PerfilPermissao.DoesNotExist:
                token['perfil_empresa'] = None
                token['permissoes'] = {}
        else:
            token['empresa_ativa_id'] = None
            token['empresa_ativa_nome'] = None
            token['perfil_empresa'] = None
            token['permissoes'] = {}

        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        # Adiciona os dados do usuário ao payload de resposta do login
        data['user'] = UsuarioSerializer(self.user).data
        return data
