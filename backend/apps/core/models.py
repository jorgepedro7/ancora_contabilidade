from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone
import uuid

# Base Models
class ModelBase(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    ativo = models.BooleanField(default=True)

    class Meta:
        abstract = True

    def soft_delete(self):
        self.ativo = False
        self.save()

class ModelBaseEmpresa(ModelBase):
    empresa = models.ForeignKey('empresas.Empresa', on_delete=models.PROTECT, related_name='%(class)s_set')

    class Meta:
        abstract = True


# User Models
class UsuarioManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('O e-mail é obrigatório.')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class Usuario(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    nome = models.CharField(max_length=255)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    empresa_ativa = models.ForeignKey('empresas.Empresa', on_delete=models.SET_NULL, blank=True, null=True, related_name='usuarios_ativos')

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = UsuarioManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nome']

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'

    def __str__(self):
        return self.email

class PerfilPermissao(ModelBaseEmpresa):
    PERFIS_CHOICES = [
        ('ADMIN', 'Administrador'),
        ('CONTADOR', 'Contador'),
        ('AUXILIAR', 'Auxiliar Contábil'),
        ('FINANCEIRO', 'Financeiro'),
        ('CONSULTA', 'Consulta'),
        ('CLIENTE', 'Cliente do Portal'),
    ]
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='perfis_permissoes')
    perfil = models.CharField(max_length=20, choices=PERFIS_CHOICES, default='CONSULTA')

    # Permissões granulares (exemplo)
    pode_emitir_nf = models.BooleanField(default=False)
    pode_cancelar_nf = models.BooleanField(default=False)
    pode_ver_folha = models.BooleanField(default=False)
    # Adicione mais permissões conforme necessário

    class Meta:
        verbose_name = 'Perfil de Permissão'
        verbose_name_plural = 'Perfis de Permissão'
        unique_together = ('usuario', 'empresa') # Um usuário pode ter apenas um perfil por empresa

    def __str__(self):
        return f'{self.usuario.email} - {self.get_perfil_display()} ({self.empresa.nome_fantasia})'

class LogAtividade(ModelBase):
    ACAO_CHOICES = [
        ('CREATE', 'Criação'),
        ('UPDATE', 'Atualização'),
        ('DELETE', 'Exclusão'),
        ('VIEW', 'Visualização'),
        ('EXPORT', 'Exportação'),
        ('LOGIN', 'Login'),
    ]
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True)
    empresa = models.ForeignKey('empresas.Empresa', on_delete=models.SET_NULL, null=True, blank=True)
    acao = models.CharField(max_length=10, choices=ACAO_CHOICES)
    modulo = models.CharField(max_length=50)
    objeto_tipo = models.CharField(max_length=100, blank=True, null=True)
    objeto_id = models.UUIDField(blank=True, null=True)
    dados_anteriores = models.JSONField(blank=True, null=True)
    dados_novos = models.JSONField(blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    descricao = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Log de Atividade'
        verbose_name_plural = 'Logs de Atividade'
        ordering = ['-criado_em']

    def __str__(self):
        return f'{self.criado_em.strftime("%Y-%m-%d %H:%M")} - {self.usuario.email if self.usuario else "Sistema"} - {self.get_acao_display()} em {self.modulo}'
