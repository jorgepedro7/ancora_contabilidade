# Gestão de Usuários — Design

> **For agentic workers:** Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Permitir que usuários ADMIN gerenciem a equipe interna e os clientes do portal dentro do próprio sistema, sem precisar do Django Admin ou shell.

**Architecture:** Endpoint unificado `POST /api/core/usuarios/` cria `Usuario` + `PerfilPermissao` atomicamente. Frontend tem duas telas separadas — Equipe e Clientes do Portal — acessíveis via seção "Configurações" no sidebar.

**Tech Stack:** Django REST Framework, Vue 3, Pinia, Tailwind CSS (padrão do projeto).

---

## Escopo

Dois perfis gerenciados:
- **Equipe**: perfis ADMIN, CONTADOR, AUXILIAR, FINANCEIRO, CONSULTA
- **Clientes do Portal**: perfil CLIENTE

Quem pode acessar: apenas usuários com perfil `ADMIN` na empresa ativa.

---

## Backend

### Novo arquivo: `backend/apps/core/serializers.py`

```python
class UsuarioGestaoSerializer(serializers.ModelSerializer):
    perfil = serializers.CharField(write_only=True)
    senha_temporaria = serializers.CharField(write_only=True, required=False)
    perfil_empresa = serializers.SerializerMethodField()
    pode_emitir_nf = serializers.SerializerMethodField()
    pode_cancelar_nf = serializers.SerializerMethodField()
    pode_ver_folha = serializers.SerializerMethodField()

    def get_perfil_empresa(self, obj): ...  # retorna perfil da empresa ativa
    def get_pode_emitir_nf(self, obj): ...
    # etc.
```

Campos retornados: `id, email, nome, telefone, perfil_empresa, pode_emitir_nf, pode_cancelar_nf, pode_ver_folha, is_active, date_joined`.

### ViewSet: `UsuarioViewSet` em `backend/apps/core/views.py`

```
GET    /api/core/usuarios/?tipo=equipe   → lista equipe (exclui CLIENTE)
GET    /api/core/usuarios/?tipo=cliente  → lista clientes do portal
POST   /api/core/usuarios/               → cria usuário + perfil (transação)
PATCH  /api/core/usuarios/{id}/          → edita nome, perfil, permissões, is_active
DELETE /api/core/usuarios/{id}/          → desativa (is_active=False, não deleta)
```

**Permissão:** `IsBackofficeCompany` + verificação inline de que `perfil_empresa == 'ADMIN'`.

**`perform_create`**: usa `transaction.atomic()`, cria `Usuario` com `set_password(senha_temporaria)`, cria `PerfilPermissao` vinculado à empresa ativa.

**`perform_destroy`**: seta `is_active=False` e salva — não deleta do banco.

**Filtro `?tipo=`**: `equipe` → exclui perfil CLIENTE; `cliente` → inclui só CLIENTE. Implementado via `get_queryset()` filtrando `PerfilPermissao` da empresa ativa.

### URLs: `backend/apps/core/urls.py`

```python
router.register(r'usuarios', UsuarioViewSet, basename='usuarios')
```

---

## Frontend

### Service: `frontend/src/services/usuarios.service.js`

```javascript
listEquipe()           → GET /core/usuarios/?tipo=equipe
listClientes()         → GET /core/usuarios/?tipo=cliente
createUsuario(data)    → POST /core/usuarios/
updateUsuario(id,data) → PATCH /core/usuarios/{id}/
deleteUsuario(id)      → DELETE /core/usuarios/{id}/
```

### Views

**`frontend/src/views/configuracoes/EquipeView.vue`**
- Tabela: Nome, E-mail, Perfil (badge colorido), Status (ativo/inativo), Data de entrada
- Botão "Adicionar membro" → modal com campos: nome, e-mail, senha temporária, perfil (select: ADMIN/CONTADOR/AUXILIAR/FINANCEIRO/CONSULTA)
- Ação por linha: chip de perfil clicável para editar, toggle ativo/inativo
- Filtro: todos / ativos / inativos

**`frontend/src/views/configuracoes/ClientesPortalView.vue`**
- Tabela: Nome, E-mail, Portal vinculado (`slug`), Status, Data de entrada
- Botão "Adicionar cliente" → modal com campos: nome, e-mail, senha temporária (perfil fixado em CLIENTE)
- Ação por linha: toggle ativo/inativo, copiar link do portal

### Router: `frontend/src/router/index.js`

```javascript
{ path: '/configuracoes/equipe',   name: 'equipe-list',   component: EquipeView,   meta: { requiresAuth: true } },
{ path: '/configuracoes/clientes', name: 'clientes-portal-list', component: ClientesPortalView, meta: { requiresAuth: true } },
```

### Sidebar: `frontend/src/components/layout/AppSidebar.vue`

Nova seção "Configurações" com dois itens:
- Equipe → `/configuracoes/equipe`
- Clientes do Portal → `/configuracoes/clientes`

Visível apenas para perfil ADMIN.

---

## Permissões e Segurança

- Backend rejeita qualquer operação se o usuário não for ADMIN (HTTP 403)
- Não é possível desativar a si mesmo (retorna erro 400)
- Não é possível alterar o próprio perfil
- `DELETE` nunca apaga do banco — apenas `is_active=False`

---

## Testes

- `UsuarioGestaoTest`: cria usuário equipe, cria cliente, lista por tipo, edita perfil, desativa
- Isolamento: ADMIN só vê usuários da própria empresa ativa
- Permissão: CONTADOR tentando criar usuário → 403
