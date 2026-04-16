# Gestão de Usuários — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Criar telas de gestão de usuários (Equipe e Clientes do Portal) para ADMINs gerenciarem equipe e clientes sem usar Django Admin.

**Architecture:** Endpoint REST unificado `UsuarioViewSet` em `core` com filtro `?tipo=equipe|cliente`. Frontend com duas views sob `/configuracoes/`, service dedicado, e nova seção "Configurações" no sidebar visível apenas para ADMIN.

**Tech Stack:** Django REST Framework + ViewSets + `transaction.atomic()`, Vue 3 + Pinia, Tailwind CSS.

---

## File Map

| File | Action | Responsibility |
|---|---|---|
| `backend/apps/core/serializers.py` | Modify | Add `UsuarioGestaoSerializer` |
| `backend/apps/core/views.py` | Modify | Add `UsuarioViewSet` |
| `backend/apps/core/urls.py` | Modify | Register router with `UsuarioViewSet` |
| `backend/apps/core/tests_usuarios.py` | Create | Tests for `UsuarioViewSet` |
| `frontend/src/services/usuarios.service.js` | Create | API calls for user management |
| `frontend/src/views/configuracoes/EquipeView.vue` | Create | Team management screen |
| `frontend/src/views/configuracoes/ClientesPortalView.vue` | Create | Portal clients management screen |
| `frontend/src/router/index.js` | Modify | Add two new routes |
| `frontend/src/components/layout/AppSidebar.vue` | Modify | Add "Configurações" section |

---

### Task 1: UsuarioGestaoSerializer

**Files:**
- Modify: `backend/apps/core/serializers.py`

- [ ] **Step 1: Write the failing test**

Create `backend/apps/core/tests_usuarios.py`:

```python
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from backend.apps.core.models import PerfilPermissao
from backend.apps.empresas.models import Empresa

User = get_user_model()


def _make_empresa():
    return Empresa.objects.create(
        razao_social='Empresa Teste',
        nome_fantasia='Teste',
        cnpj='12345678000195',
        regime_tributario='SN',
        cnae_principal='1234567',
        cep='01001000',
        logradouro='Rua A',
        numero='1',
        bairro='Centro',
        municipio='São Paulo',
        uf='SP',
    )


def _make_user(email, nome, empresa, perfil, password='senha123'):
    user = User.objects.create_user(email=email, nome=nome, password=password)
    user.empresa_ativa = empresa
    user.save(update_fields=['empresa_ativa'])
    PerfilPermissao.objects.create(usuario=user, empresa=empresa, perfil=perfil)
    return user


def _token(client, email, password='senha123'):
    resp = client.post(reverse('token_obtain_pair'), {'email': email, 'password': password}, format='json')
    return resp.data['access']


class UsuarioGestaoSerializerTest(APITestCase):
    def setUp(self):
        self.empresa = _make_empresa()
        self.admin = _make_user('admin@t.test', 'Admin', self.empresa, 'ADMIN')
        token = _token(self.client, 'admin@t.test')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    def test_cria_usuario_equipe(self):
        url = reverse('usuarios-list')
        payload = {
            'email': 'novo@t.test',
            'nome': 'Novo Membro',
            'perfil': 'CONTADOR',
            'senha_temporaria': 'temp1234',
        }
        resp = self.client.post(url, payload, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED, resp.data)
        self.assertEqual(resp.data['email'], 'novo@t.test')
        self.assertEqual(resp.data['perfil_empresa'], 'CONTADOR')
        self.assertTrue(User.objects.filter(email='novo@t.test').exists())
        self.assertTrue(PerfilPermissao.objects.filter(usuario__email='novo@t.test', perfil='CONTADOR').exists())
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd /home/jorge/Projetos/ancora_contabilidade
docker compose exec backend python manage.py test backend.apps.core.tests_usuarios.UsuarioGestaoSerializerTest.test_cria_usuario_equipe --verbosity=2
```

Expected: FAIL with `NoReverseMatch` or `ImportError`.

- [ ] **Step 3: Add `UsuarioGestaoSerializer` to `backend/apps/core/serializers.py`**

Append at the end of the file (after the `CustomTokenObtainPairSerializer` class):

```python
from django.db import transaction


class UsuarioGestaoSerializer(serializers.ModelSerializer):
    perfil = serializers.CharField(write_only=True)
    senha_temporaria = serializers.CharField(write_only=True, required=False)
    perfil_empresa = serializers.SerializerMethodField()
    pode_emitir_nf = serializers.SerializerMethodField()
    pode_cancelar_nf = serializers.SerializerMethodField()
    pode_ver_folha = serializers.SerializerMethodField()

    class Meta:
        model = Usuario
        fields = [
            'id', 'email', 'nome', 'telefone',
            'perfil', 'senha_temporaria',
            'perfil_empresa', 'pode_emitir_nf', 'pode_cancelar_nf', 'pode_ver_folha',
            'is_active', 'date_joined',
        ]
        read_only_fields = ['id', 'date_joined', 'perfil_empresa', 'pode_emitir_nf', 'pode_cancelar_nf', 'pode_ver_folha']

    def _get_perfil_obj(self, obj):
        request = self.context.get('request')
        if not request:
            return None
        empresa = getattr(request.user, 'empresa_ativa', None)
        if not empresa:
            return None
        try:
            return PerfilPermissao.objects.get(usuario=obj, empresa=empresa, ativo=True)
        except PerfilPermissao.DoesNotExist:
            return None

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
```

**Note:** The `transaction` import and `create` / `update` methods will be added in Task 2 (ViewSet), because `perform_create` handles atomicity there. The serializer `validate_perfil` is also needed — add it here:

```python
    PERFIS_EQUIPE = {'ADMIN', 'CONTADOR', 'AUXILIAR', 'FINANCEIRO', 'CONSULTA'}
    PERFIS_VALIDOS = PERFIS_EQUIPE | {'CLIENTE'}

    def validate_perfil(self, value):
        if value not in self.PERFIS_VALIDOS:
            raise serializers.ValidationError(f'Perfil inválido. Escolha entre: {", ".join(sorted(self.PERFIS_VALIDOS))}')
        return value
```

- [ ] **Step 4: Run test again — still fails (ViewSet and URL not created yet)**

```bash
docker compose exec backend python manage.py test backend.apps.core.tests_usuarios.UsuarioGestaoSerializerTest.test_cria_usuario_equipe --verbosity=2
```

Expected: FAIL with `NoReverseMatch`. That's correct — proceed to Task 2.

- [ ] **Step 5: Commit**

```bash
git add backend/apps/core/serializers.py backend/apps/core/tests_usuarios.py
git commit -m "feat(core): add UsuarioGestaoSerializer and initial test"
```

---

### Task 2: UsuarioViewSet

**Files:**
- Modify: `backend/apps/core/views.py`

- [ ] **Step 1: Add `UsuarioViewSet` to `backend/apps/core/views.py`**

Add the following imports at the top of the file (after existing imports):

```python
from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied, ValidationError
from django.db import transaction

from .models import PerfilPermissao
from .serializers import UsuarioGestaoSerializer
from .permissions import IsBackofficeCompany
from .utils import garantir_empresa_padrao, obter_perfil_empresa
```

Then append this class at the end of `views.py`:

```python
class UsuarioViewSet(viewsets.ModelViewSet):
    serializer_class = UsuarioGestaoSerializer
    permission_classes = [IsBackofficeCompany]
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def _get_empresa(self):
        return garantir_empresa_padrao(self.request.user)

    def _exigir_admin(self):
        perfil = obter_perfil_empresa(self.request.user, self._get_empresa())
        if perfil is None or perfil.perfil != 'ADMIN':
            raise PermissionDenied('Apenas administradores podem gerenciar usuários.')

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
        self._exigir_admin()
        empresa = self._get_empresa()
        perfil = serializer.validated_data.pop('perfil')
        senha = serializer.validated_data.pop('senha_temporaria', None)

        with transaction.atomic():
            user = Usuario(
                email=serializer.validated_data['email'],
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

        # Rebind para que o serializer consiga serializar o objeto criado
        serializer.instance = user

    def perform_update(self, serializer):
        self._exigir_admin()
        empresa = self._get_empresa()
        user = serializer.instance

        # Não pode alterar o próprio perfil
        if user == self.request.user:
            raise ValidationError({'detail': 'Você não pode alterar o próprio perfil.'})

        novo_perfil = serializer.validated_data.pop('perfil', None)
        serializer.validated_data.pop('senha_temporaria', None)
        serializer.save()

        if novo_perfil:
            PerfilPermissao.objects.filter(usuario=user, empresa=empresa).update(perfil=novo_perfil)

    def perform_destroy(self, instance):
        self._exigir_admin()
        if instance == self.request.user:
            raise ValidationError({'detail': 'Você não pode desativar a si mesmo.'})
        instance.is_active = False
        instance.save(update_fields=['is_active'])
```

- [ ] **Step 2: Run test to verify it still fails (URL not registered yet)**

```bash
docker compose exec backend python manage.py test backend.apps.core.tests_usuarios.UsuarioGestaoSerializerTest.test_cria_usuario_equipe --verbosity=2
```

Expected: FAIL with `NoReverseMatch`. Proceed to Task 3.

- [ ] **Step 3: Commit**

```bash
git add backend/apps/core/views.py
git commit -m "feat(core): add UsuarioViewSet"
```

---

### Task 3: URLs — Register Router

**Files:**
- Modify: `backend/apps/core/urls.py`

- [ ] **Step 1: Replace `backend/apps/core/urls.py` with router-based config**

```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import PerfilUsuarioView, HealthCheckView, UsuarioViewSet

router = DefaultRouter()
router.register(r'usuarios', UsuarioViewSet, basename='usuarios')

urlpatterns = [
    path('perfil/', PerfilUsuarioView.as_view(), name='perfil_usuario'),
    path('health/', HealthCheckView.as_view(), name='health_check'),
    path('', include(router.urls)),
]
```

- [ ] **Step 2: Run tests**

```bash
docker compose exec backend python manage.py test backend.apps.core.tests_usuarios --verbosity=2
```

Expected: PASS for `test_cria_usuario_equipe`.

- [ ] **Step 3: Add remaining tests to `backend/apps/core/tests_usuarios.py`**

Append to the file, inside the class `UsuarioGestaoSerializerTest` (after `test_cria_usuario_equipe`):

```python
    def test_cria_cliente_portal(self):
        url = reverse('usuarios-list')
        payload = {
            'email': 'cliente@t.test',
            'nome': 'Cliente Portal',
            'perfil': 'CLIENTE',
            'senha_temporaria': 'temp1234',
        }
        resp = self.client.post(url, payload, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED, resp.data)
        self.assertEqual(resp.data['perfil_empresa'], 'CLIENTE')

    def test_lista_equipe_exclui_clientes(self):
        _make_user('equipe@t.test', 'Equipe', self.empresa, 'CONTADOR')
        _make_user('cliente@t.test', 'Cliente', self.empresa, 'CLIENTE')
        url = reverse('usuarios-list') + '?tipo=equipe'
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        emails = [u['email'] for u in resp.data['results']]
        self.assertIn('equipe@t.test', emails)
        self.assertNotIn('cliente@t.test', emails)

    def test_lista_clientes_inclui_so_clientes(self):
        _make_user('equipe@t.test', 'Equipe', self.empresa, 'CONTADOR')
        _make_user('cliente@t.test', 'Cliente', self.empresa, 'CLIENTE')
        url = reverse('usuarios-list') + '?tipo=cliente'
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        emails = [u['email'] for u in resp.data['results']]
        self.assertIn('cliente@t.test', emails)
        self.assertNotIn('equipe@t.test', emails)

    def test_edita_perfil(self):
        membro = _make_user('membro@t.test', 'Membro', self.empresa, 'AUXILIAR')
        url = reverse('usuarios-detail', args=[membro.id])
        resp = self.client.patch(url, {'perfil': 'FINANCEIRO'}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK, resp.data)
        self.assertEqual(
            PerfilPermissao.objects.get(usuario=membro, empresa=self.empresa).perfil,
            'FINANCEIRO',
        )

    def test_desativa_usuario(self):
        membro = _make_user('membro2@t.test', 'Membro2', self.empresa, 'CONSULTA')
        url = reverse('usuarios-detail', args=[membro.id])
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        membro.refresh_from_db()
        self.assertFalse(membro.is_active)

    def test_nao_pode_desativar_si_mesmo(self):
        url = reverse('usuarios-detail', args=[self.admin.id])
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_contador_nao_pode_criar_usuario(self):
        contador = _make_user('contador@t.test', 'Contador', self.empresa, 'CONTADOR')
        token = _token(self.client, 'contador@t.test')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        url = reverse('usuarios-list')
        resp = self.client.post(url, {'email': 'x@t.test', 'nome': 'X', 'perfil': 'CONSULTA', 'senha_temporaria': 'abc'}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_isolamento_empresa(self):
        """Admin de outra empresa não vê usuários desta empresa."""
        outra_empresa = _make_empresa.__wrapped__() if hasattr(_make_empresa, '__wrapped__') else Empresa.objects.create(
            razao_social='Outra Empresa',
            nome_fantasia='Outra',
            cnpj='98765432000199',
            regime_tributario='LP',
            cnae_principal='9999999',
            cep='01001000',
            logradouro='Av B',
            numero='2',
            bairro='Centro',
            municipio='SP',
            uf='SP',
        )
        outro_admin = _make_user('outro@t.test', 'Outro Admin', outra_empresa, 'ADMIN')
        token = _token(self.client, 'outro@t.test')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        url = reverse('usuarios-list') + '?tipo=equipe'
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        emails = [u['email'] for u in resp.data['results']]
        self.assertNotIn('admin@t.test', emails)
```

- [ ] **Step 4: Run all tests**

```bash
docker compose exec backend python manage.py test backend.apps.core.tests_usuarios --verbosity=2
```

Expected: All 9 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/apps/core/urls.py backend/apps/core/tests_usuarios.py
git commit -m "feat(core): register UsuarioViewSet router and full test suite"
```

---

### Task 4: Frontend Service

**Files:**
- Create: `frontend/src/services/usuarios.service.js`

- [ ] **Step 1: Create the service file**

```javascript
import api from './api'

const UsuariosService = {
  listEquipe() {
    return api.get('/core/usuarios/?tipo=equipe').then(r => r.data)
  },

  listClientes() {
    return api.get('/core/usuarios/?tipo=cliente').then(r => r.data)
  },

  createUsuario(data) {
    return api.post('/core/usuarios/', data).then(r => r.data)
  },

  updateUsuario(id, data) {
    return api.patch(`/core/usuarios/${id}/`, data).then(r => r.data)
  },

  deleteUsuario(id) {
    return api.delete(`/core/usuarios/${id}/`).then(r => r.data)
  },
}

export default UsuariosService
```

- [ ] **Step 2: Verify the API base path used by existing services**

```bash
grep -n "baseURL\|/api/" /home/jorge/Projetos/ancora_contabilidade/frontend/src/services/api.js | head -5
```

If `baseURL` already includes `/api/`, the paths above should be `/core/usuarios/` (no `/api/` prefix). Confirm this matches patterns in other services like `intake.service.js` or `empresas.service.js`.

- [ ] **Step 3: Commit**

```bash
git add frontend/src/services/usuarios.service.js
git commit -m "feat(frontend): add UsuariosService"
```

---

### Task 5: EquipeView

**Files:**
- Create: `frontend/src/views/configuracoes/EquipeView.vue`

- [ ] **Step 1: Create the directory and file**

```bash
mkdir -p /home/jorge/Projetos/ancora_contabilidade/frontend/src/views/configuracoes
```

Create `frontend/src/views/configuracoes/EquipeView.vue`:

```vue
<template>
  <div class="p-4 space-y-6 max-w-5xl mx-auto">
    <!-- Cabeçalho -->
    <section class="bg-ancora-black/30 border border-ancora-gold/20 rounded-lg p-6">
      <div class="flex items-start justify-between gap-4">
        <div>
          <p class="text-sm uppercase tracking-wide text-gray-500 mb-2">Configurações</p>
          <h1 class="text-3xl font-display text-ancora-gold mb-1">Equipe</h1>
          <p class="text-gray-400 text-sm">Gerencie os membros da equipe interna.</p>
        </div>
        <button
          type="button"
          @click="abrirModal()"
          class="px-4 py-2 bg-ancora-gold text-ancora-black rounded-md font-bold hover:bg-ancora-gold/80 text-sm"
        >
          + Adicionar membro
        </button>
      </div>
    </section>

    <!-- Filtros -->
    <div class="flex gap-2">
      <button
        v-for="f in filtros"
        :key="f.value"
        @click="filtroAtivo = f.value"
        :class="[
          'px-3 py-1 rounded-full text-sm border',
          filtroAtivo === f.value
            ? 'bg-ancora-gold text-ancora-black border-ancora-gold font-bold'
            : 'text-gray-400 border-gray-700 hover:border-ancora-gold/50 hover:text-ancora-gold',
        ]"
      >
        {{ f.label }}
      </button>
    </div>

    <!-- Tabela -->
    <section class="bg-ancora-black/40 border border-ancora-gold/20 rounded-lg overflow-hidden">
      <div v-if="loading" class="p-6 text-gray-500 text-sm">Carregando...</div>
      <table v-else class="w-full text-sm">
        <thead class="border-b border-ancora-gold/20">
          <tr class="text-gray-500 text-xs uppercase tracking-wide">
            <th class="text-left px-4 py-3">Nome</th>
            <th class="text-left px-4 py-3">E-mail</th>
            <th class="text-left px-4 py-3">Perfil</th>
            <th class="text-left px-4 py-3">Status</th>
            <th class="text-left px-4 py-3">Entrada</th>
            <th class="px-4 py-3"></th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="membro in listaFiltrada"
            :key="membro.id"
            class="border-b border-ancora-gold/10 hover:bg-ancora-navy/20"
          >
            <td class="px-4 py-3 text-white">{{ membro.nome }}</td>
            <td class="px-4 py-3 text-gray-400">{{ membro.email }}</td>
            <td class="px-4 py-3">
              <span :class="badgePerfil(membro.perfil_empresa)" class="text-xs font-bold px-2 py-1 rounded">
                {{ membro.perfil_empresa }}
              </span>
            </td>
            <td class="px-4 py-3">
              <span
                :class="membro.is_active ? 'text-green-400' : 'text-gray-500'"
                class="text-xs font-bold"
              >
                {{ membro.is_active ? 'Ativo' : 'Inativo' }}
              </span>
            </td>
            <td class="px-4 py-3 text-gray-500 text-xs">{{ formatData(membro.date_joined) }}</td>
            <td class="px-4 py-3 flex gap-2 justify-end">
              <button
                type="button"
                @click="abrirModal(membro)"
                class="text-xs text-ancora-gold hover:underline"
              >
                Editar
              </button>
              <button
                type="button"
                @click="toggleAtivo(membro)"
                class="text-xs text-gray-400 hover:text-red-400"
              >
                {{ membro.is_active ? 'Desativar' : 'Ativar' }}
              </button>
            </td>
          </tr>
          <tr v-if="!listaFiltrada.length">
            <td colspan="6" class="px-4 py-6 text-center text-gray-500 text-sm">Nenhum membro encontrado.</td>
          </tr>
        </tbody>
      </table>
    </section>

    <!-- Modal -->
    <div
      v-if="modalAberto"
      class="fixed inset-0 bg-black/70 flex items-center justify-center z-50"
      @click.self="fecharModal"
    >
      <div class="bg-ancora-black border border-ancora-gold/30 rounded-lg p-6 w-full max-w-md space-y-4">
        <h2 class="text-xl font-display text-ancora-gold">
          {{ editando ? 'Editar membro' : 'Adicionar membro' }}
        </h2>
        <form class="space-y-3" @submit.prevent="salvar">
          <div>
            <label class="block text-sm text-gray-300 mb-1">Nome *</label>
            <input
              v-model="form.nome"
              required
              type="text"
              class="w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white"
            />
          </div>
          <div>
            <label class="block text-sm text-gray-300 mb-1">E-mail *</label>
            <input
              v-model="form.email"
              required
              type="email"
              :disabled="!!editando"
              class="w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white disabled:opacity-50"
            />
          </div>
          <div v-if="!editando">
            <label class="block text-sm text-gray-300 mb-1">Senha temporária *</label>
            <input
              v-model="form.senha_temporaria"
              required
              type="password"
              class="w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white"
            />
          </div>
          <div>
            <label class="block text-sm text-gray-300 mb-1">Perfil *</label>
            <select
              v-model="form.perfil"
              required
              class="w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white"
            >
              <option value="ADMIN">Administrador</option>
              <option value="CONTADOR">Contador</option>
              <option value="AUXILIAR">Auxiliar Contábil</option>
              <option value="FINANCEIRO">Financeiro</option>
              <option value="CONSULTA">Consulta</option>
            </select>
          </div>
          <div class="flex gap-2 justify-end pt-2">
            <button type="button" @click="fecharModal" class="px-4 py-2 text-sm text-gray-400 hover:text-white">
              Cancelar
            </button>
            <button
              type="submit"
              :disabled="salvando"
              class="px-4 py-2 bg-ancora-gold text-ancora-black rounded-md font-bold text-sm hover:bg-ancora-gold/80 disabled:opacity-50"
            >
              {{ salvando ? 'Salvando...' : 'Salvar' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import UsuariosService from '@/services/usuarios.service'
import { useUiStore } from '@/stores/ui'

const uiStore = useUiStore()

const membros = ref([])
const loading = ref(false)
const filtroAtivo = ref('todos')
const modalAberto = ref(false)
const editando = ref(null)
const salvando = ref(false)

const filtros = [
  { label: 'Todos', value: 'todos' },
  { label: 'Ativos', value: 'ativos' },
  { label: 'Inativos', value: 'inativos' },
]

const form = ref(formVazio())

function formVazio() {
  return { nome: '', email: '', senha_temporaria: '', perfil: 'CONTADOR' }
}

const listaFiltrada = computed(() => {
  if (filtroAtivo.value === 'ativos') return membros.value.filter(m => m.is_active)
  if (filtroAtivo.value === 'inativos') return membros.value.filter(m => !m.is_active)
  return membros.value
})

onMounted(carregar)

async function carregar() {
  loading.value = true
  try {
    const resp = await UsuariosService.listEquipe()
    membros.value = resp.results || resp || []
  } catch {
    uiStore.showNotification('Erro ao carregar equipe.', 'error')
  } finally {
    loading.value = false
  }
}

function abrirModal(membro = null) {
  editando.value = membro
  form.value = membro
    ? { nome: membro.nome, email: membro.email, perfil: membro.perfil_empresa, senha_temporaria: '' }
    : formVazio()
  modalAberto.value = true
}

function fecharModal() {
  modalAberto.value = false
  editando.value = null
}

async function salvar() {
  salvando.value = true
  try {
    if (editando.value) {
      const updated = await UsuariosService.updateUsuario(editando.value.id, {
        nome: form.value.nome,
        perfil: form.value.perfil,
      })
      const idx = membros.value.findIndex(m => m.id === editando.value.id)
      if (idx !== -1) membros.value[idx] = updated
      uiStore.showNotification('Membro atualizado.', 'success')
    } else {
      const created = await UsuariosService.createUsuario(form.value)
      membros.value = [created, ...membros.value]
      uiStore.showNotification('Membro adicionado.', 'success')
    }
    fecharModal()
  } catch (error) {
    const msg =
      error?.response?.data?.errors?.[0]?.message ||
      error?.response?.data?.message ||
      'Erro ao salvar.'
    uiStore.showNotification(msg, 'error')
  } finally {
    salvando.value = false
  }
}

async function toggleAtivo(membro) {
  if (membro.is_active) {
    try {
      await UsuariosService.deleteUsuario(membro.id)
      membro.is_active = false
      uiStore.showNotification('Usuário desativado.', 'success')
    } catch (error) {
      const msg =
        error?.response?.data?.errors?.[0]?.message ||
        error?.response?.data?.message ||
        'Erro ao desativar.'
      uiStore.showNotification(msg, 'error')
    }
  } else {
    try {
      const updated = await UsuariosService.updateUsuario(membro.id, { is_active: true })
      membro.is_active = updated.is_active
      uiStore.showNotification('Usuário ativado.', 'success')
    } catch {
      uiStore.showNotification('Erro ao ativar usuário.', 'error')
    }
  }
}

function badgePerfil(perfil) {
  const map = {
    ADMIN: 'bg-ancora-gold/20 text-ancora-gold',
    CONTADOR: 'bg-blue-500/20 text-blue-300',
    AUXILIAR: 'bg-purple-500/20 text-purple-300',
    FINANCEIRO: 'bg-green-600/20 text-green-300',
    CONSULTA: 'bg-gray-500/20 text-gray-300',
  }
  return map[perfil] || 'bg-gray-500/20 text-gray-300'
}

function formatData(iso) {
  if (!iso) return ''
  return new Date(iso).toLocaleDateString('pt-BR')
}
</script>
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/views/configuracoes/EquipeView.vue
git commit -m "feat(frontend): add EquipeView"
```

---

### Task 6: ClientesPortalView

**Files:**
- Create: `frontend/src/views/configuracoes/ClientesPortalView.vue`

- [ ] **Step 1: Create the file**

```vue
<template>
  <div class="p-4 space-y-6 max-w-5xl mx-auto">
    <!-- Cabeçalho -->
    <section class="bg-ancora-black/30 border border-ancora-gold/20 rounded-lg p-6">
      <div class="flex items-start justify-between gap-4">
        <div>
          <p class="text-sm uppercase tracking-wide text-gray-500 mb-2">Configurações</p>
          <h1 class="text-3xl font-display text-ancora-gold mb-1">Clientes do Portal</h1>
          <p class="text-gray-400 text-sm">Gerencie os acessos dos clientes ao portal de envio de documentos.</p>
        </div>
        <button
          type="button"
          @click="abrirModal()"
          class="px-4 py-2 bg-ancora-gold text-ancora-black rounded-md font-bold hover:bg-ancora-gold/80 text-sm"
        >
          + Adicionar cliente
        </button>
      </div>
    </section>

    <!-- Tabela -->
    <section class="bg-ancora-black/40 border border-ancora-gold/20 rounded-lg overflow-hidden">
      <div v-if="loading" class="p-6 text-gray-500 text-sm">Carregando...</div>
      <table v-else class="w-full text-sm">
        <thead class="border-b border-ancora-gold/20">
          <tr class="text-gray-500 text-xs uppercase tracking-wide">
            <th class="text-left px-4 py-3">Nome</th>
            <th class="text-left px-4 py-3">E-mail</th>
            <th class="text-left px-4 py-3">Status</th>
            <th class="text-left px-4 py-3">Entrada</th>
            <th class="px-4 py-3"></th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="cliente in clientes"
            :key="cliente.id"
            class="border-b border-ancora-gold/10 hover:bg-ancora-navy/20"
          >
            <td class="px-4 py-3 text-white">{{ cliente.nome }}</td>
            <td class="px-4 py-3 text-gray-400">{{ cliente.email }}</td>
            <td class="px-4 py-3">
              <span
                :class="cliente.is_active ? 'text-green-400' : 'text-gray-500'"
                class="text-xs font-bold"
              >
                {{ cliente.is_active ? 'Ativo' : 'Inativo' }}
              </span>
            </td>
            <td class="px-4 py-3 text-gray-500 text-xs">{{ formatData(cliente.date_joined) }}</td>
            <td class="px-4 py-3 flex gap-2 justify-end">
              <button
                type="button"
                @click="toggleAtivo(cliente)"
                class="text-xs text-gray-400 hover:text-red-400"
              >
                {{ cliente.is_active ? 'Desativar' : 'Ativar' }}
              </button>
            </td>
          </tr>
          <tr v-if="!clientes.length">
            <td colspan="5" class="px-4 py-6 text-center text-gray-500 text-sm">Nenhum cliente encontrado.</td>
          </tr>
        </tbody>
      </table>
    </section>

    <!-- Modal -->
    <div
      v-if="modalAberto"
      class="fixed inset-0 bg-black/70 flex items-center justify-center z-50"
      @click.self="fecharModal"
    >
      <div class="bg-ancora-black border border-ancora-gold/30 rounded-lg p-6 w-full max-w-md space-y-4">
        <h2 class="text-xl font-display text-ancora-gold">Adicionar cliente</h2>
        <form class="space-y-3" @submit.prevent="salvar">
          <div>
            <label class="block text-sm text-gray-300 mb-1">Nome *</label>
            <input
              v-model="form.nome"
              required
              type="text"
              class="w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white"
            />
          </div>
          <div>
            <label class="block text-sm text-gray-300 mb-1">E-mail *</label>
            <input
              v-model="form.email"
              required
              type="email"
              class="w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white"
            />
          </div>
          <div>
            <label class="block text-sm text-gray-300 mb-1">Senha temporária *</label>
            <input
              v-model="form.senha_temporaria"
              required
              type="password"
              class="w-full px-3 py-2 bg-ancora-black/70 border border-ancora-gold/20 rounded-md text-white"
            />
          </div>
          <div class="flex gap-2 justify-end pt-2">
            <button type="button" @click="fecharModal" class="px-4 py-2 text-sm text-gray-400 hover:text-white">
              Cancelar
            </button>
            <button
              type="submit"
              :disabled="salvando"
              class="px-4 py-2 bg-ancora-gold text-ancora-black rounded-md font-bold text-sm hover:bg-ancora-gold/80 disabled:opacity-50"
            >
              {{ salvando ? 'Salvando...' : 'Salvar' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import UsuariosService from '@/services/usuarios.service'
import { useUiStore } from '@/stores/ui'

const uiStore = useUiStore()

const clientes = ref([])
const loading = ref(false)
const modalAberto = ref(false)
const salvando = ref(false)
const form = ref({ nome: '', email: '', senha_temporaria: '' })

onMounted(carregar)

async function carregar() {
  loading.value = true
  try {
    const resp = await UsuariosService.listClientes()
    clientes.value = resp.results || resp || []
  } catch {
    uiStore.showNotification('Erro ao carregar clientes.', 'error')
  } finally {
    loading.value = false
  }
}

function abrirModal() {
  form.value = { nome: '', email: '', senha_temporaria: '' }
  modalAberto.value = true
}

function fecharModal() {
  modalAberto.value = false
}

async function salvar() {
  salvando.value = true
  try {
    const created = await UsuariosService.createUsuario({ ...form.value, perfil: 'CLIENTE' })
    clientes.value = [created, ...clientes.value]
    uiStore.showNotification('Cliente adicionado.', 'success')
    fecharModal()
  } catch (error) {
    const msg =
      error?.response?.data?.errors?.[0]?.message ||
      error?.response?.data?.message ||
      'Erro ao salvar.'
    uiStore.showNotification(msg, 'error')
  } finally {
    salvando.value = false
  }
}

async function toggleAtivo(cliente) {
  if (cliente.is_active) {
    try {
      await UsuariosService.deleteUsuario(cliente.id)
      cliente.is_active = false
      uiStore.showNotification('Cliente desativado.', 'success')
    } catch (error) {
      const msg =
        error?.response?.data?.errors?.[0]?.message ||
        error?.response?.data?.message ||
        'Erro ao desativar.'
      uiStore.showNotification(msg, 'error')
    }
  } else {
    try {
      const updated = await UsuariosService.updateUsuario(cliente.id, { is_active: true })
      cliente.is_active = updated.is_active
      uiStore.showNotification('Cliente ativado.', 'success')
    } catch {
      uiStore.showNotification('Erro ao ativar cliente.', 'error')
    }
  }
}

function formatData(iso) {
  if (!iso) return ''
  return new Date(iso).toLocaleDateString('pt-BR')
}
</script>
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/views/configuracoes/ClientesPortalView.vue
git commit -m "feat(frontend): add ClientesPortalView"
```

---

### Task 7: Router + Sidebar

**Files:**
- Modify: `frontend/src/router/index.js`
- Modify: `frontend/src/components/layout/AppSidebar.vue`

- [ ] **Step 1: Add routes to `frontend/src/router/index.js`**

Add these two routes inside the `routes` array, before the closing `]` (after the last route):

```javascript
    {
      path: '/configuracoes/equipe',
      name: 'equipe-list',
      component: () => import('../views/configuracoes/EquipeView.vue'),
      meta: { requiresAuth: true, requiresBackoffice: true }
    },
    {
      path: '/configuracoes/clientes',
      name: 'clientes-portal-list',
      component: () => import('../views/configuracoes/ClientesPortalView.vue'),
      meta: { requiresAuth: true, requiresBackoffice: true }
    },
```

- [ ] **Step 2: Add "Configurações" section to `frontend/src/components/layout/AppSidebar.vue`**

In the `menuItems` array, append this new entry at the end (before the closing `]`):

```javascript
  { name: 'Configurações', icon: '⚙️', children: [
    { name: 'Equipe', icon: '👥', path: '/configuracoes/equipe' },
    { name: 'Clientes do Portal', icon: '🔑', path: '/configuracoes/clientes' },
  ], requiresEmpresa: true, requiresAdmin: true },
```

Then update the `isItemVisible` function to handle `requiresAdmin`:

```javascript
function isItemVisible(item) {
  if (item.requiresBackoffice && authStore.user?.perfil_empresa === 'CLIENTE') {
    return false
  }
  if (item.requiresAdmin && authStore.user?.perfil_empresa !== 'ADMIN') {
    return false
  }
  if (item.requiresEmpresa && !empresaStore.activeEmpresa) {
    return false
  }
  return true
}
```

- [ ] **Step 3: Verify frontend builds without errors**

```bash
cd /home/jorge/Projetos/ancora_contabilidade
docker compose exec frontend npm run build 2>&1 | tail -20
```

Expected: Build succeeds with no errors.

- [ ] **Step 4: Run backend tests one final time**

```bash
docker compose exec backend python manage.py test backend.apps.core.tests_usuarios --verbosity=2
```

Expected: All 9 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/router/index.js frontend/src/components/layout/AppSidebar.vue
git commit -m "feat(frontend): add Configurações section to sidebar and router routes"
```

---

## Self-Review

### Spec coverage

| Spec requirement | Covered in |
|---|---|
| `GET /api/core/usuarios/?tipo=equipe` → lista equipe (exclui CLIENTE) | Task 2 (`get_queryset`) + Task 3 tests |
| `GET /api/core/usuarios/?tipo=cliente` → lista clientes | Task 2 + Task 3 tests |
| `POST /api/core/usuarios/` → cria usuário + perfil (transação) | Task 2 (`perform_create`) + Task 3 tests |
| `PATCH /api/core/usuarios/{id}/` → edita nome, perfil | Task 2 (`perform_update`) + Task 3 tests |
| `DELETE /api/core/usuarios/{id}/` → desativa (is_active=False) | Task 2 (`perform_destroy`) + Task 3 tests |
| Permissão: `IsBackofficeCompany` + ADMIN inline | Task 2 (`_exigir_admin`) + Task 3 tests |
| Não pode desativar a si mesmo | Task 2 + Task 3 `test_nao_pode_desativar_si_mesmo` |
| CONTADOR tentando criar → 403 | Task 3 `test_contador_nao_pode_criar_usuario` |
| Isolamento por empresa | Task 3 `test_isolamento_empresa` |
| Serializer: id, email, nome, telefone, perfil_empresa, pode_emitir_nf, pode_cancelar_nf, pode_ver_folha, is_active, date_joined | Task 1 |
| Service: listEquipe, listClientes, createUsuario, updateUsuario, deleteUsuario | Task 4 |
| EquipeView: tabela, modal, filtro todos/ativos/inativos, badge de perfil | Task 5 |
| ClientesPortalView: tabela, modal, toggle ativo/inativo | Task 6 |
| Router: /configuracoes/equipe, /configuracoes/clientes | Task 7 |
| Sidebar: seção "Configurações" visível apenas para ADMIN | Task 7 |

All spec requirements are covered.

### Placeholder scan

No TBDs, TODOs, or incomplete sections found.

### Type consistency

- `UsuarioGestaoSerializer` defined in Task 1, used in Task 2 (`serializer_class = UsuarioGestaoSerializer`)
- `UsuarioViewSet` defined in Task 2, registered in Task 3
- `UsuariosService` created in Task 4, imported in Tasks 5 and 6
- `badgePerfil(perfil)` in Task 5 takes `membro.perfil_empresa` which is the serializer field `get_perfil_empresa` — consistent
- `requiresAdmin` flag in sidebar (Task 7) handled in `isItemVisible` in same task — consistent
