# Folha de Pagamento — Bug Fixes Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Corrigir 3 bugs no backend do módulo de Folha de Pagamento e verificar integridade do frontend.

**Architecture:** Fixes cirúrgicos — sem alteração de models ou migrations. Apenas lógica de negócio e verificação de código existente.

**Tech Stack:** Django 4.2, DRF, Vue 3.

---

## Mapa de Arquivos

| Arquivo | Ação | Responsabilidade |
|---|---|---|
| `backend/apps/folha/views.py` | Modificar | Remover bypass de is_superuser em get_queryset |
| `backend/apps/folha/models.py` | Modificar | Adicionar filtro data_fim na query de contrato ativo |
| `backend/apps/folha/signals.py` | Modificar | Limpar arquivo (remover código comentado sem valor) |
| `frontend/src/views/folha/*.vue` | Verificar | Confirmar ausência de placeholders e consistência de serviço |
| `frontend/src/services/folha.service.js` | Verificar | Confirmar todos os métodos necessários existem |

---

## Task 1: Remover bypass de is_superuser em get_queryset

**Files:**
- Modify: `backend/apps/folha/views.py`

- [ ] **Step 1: Substituir get_queryset em BaseFolhaViewSet**

Localizar o método `get_queryset` (linhas 24-34) e substituir por:

```python
    def get_queryset(self):
        if self.request.user.is_authenticated and self.request.user.empresa_ativa:
            return self.queryset.filter(empresa=self.request.user.empresa_ativa, ativo=True)
        return self.queryset.none()
```

A lógica é idêntica ao padrão de todos os outros módulos (estoque, financeiro, fiscal). O bypass `is_superuser` viola o isolamento por empresa definido em CLAUDE.md.

- [ ] **Step 2: Verificar sintaxe**

```bash
cd /home/jorge/Projetos/ancora_contabilidade
python3 -c "import ast; ast.parse(open('backend/apps/folha/views.py').read()); print('OK')"
```

Esperado: `OK`

- [ ] **Step 3: Commit**

```bash
git add backend/apps/folha/views.py
git commit -m "fix(folha): remove bypass is_superuser em get_queryset — isolamento por empresa"
```

---

## Task 2: Corrigir filtro de contrato ativo para respeitar data_fim

**Files:**
- Modify: `backend/apps/folha/models.py`

- [ ] **Step 1: Localizar a query problemática**

Em `HoleriteFuncionario.calcular()` (em torno da linha 200), a query de contrato ativo é:

```python
contrato_ativo = self.funcionario.contratos.filter(
    ativo=True,
    data_inicio__lte=self.folha_pagamento.competencia
).order_by('-data_inicio').first()
```

Isso retorna contratos que iniciaram antes da competência mas que podem ter expirado (`data_fim` anterior à competência). Substituir pela query corrigida:

```python
contrato_ativo = self.funcionario.contratos.filter(
    ativo=True,
    data_inicio__lte=self.folha_pagamento.competencia
).filter(
    models.Q(data_fim__isnull=True) | models.Q(data_fim__gte=self.folha_pagamento.competencia)
).order_by('-data_inicio').first()
```

Isso garante que apenas contratos sem data_fim (indeterminado) ou com data_fim maior ou igual à competência sejam considerados.

- [ ] **Step 2: Verificar que `models.Q` já está importado no arquivo**

```bash
grep -n "^from django.db import\|^import models\|models.Q" backend/apps/folha/models.py | head -5
```

Se `Q` não estiver importado, adicionar no import: `from django.db.models import Q` e usar `Q(...)` em vez de `models.Q(...)`.

- [ ] **Step 3: Verificar sintaxe**

```bash
python3 -c "import ast; ast.parse(open('backend/apps/folha/models.py').read()); print('OK')"
```

Esperado: `OK`

- [ ] **Step 4: Commit**

```bash
git add backend/apps/folha/models.py
git commit -m "fix(folha): filtro de contrato ativo respeita data_fim na competência"
```

---

## Task 3: Limpar signals.py

**Files:**
- Modify: `backend/apps/folha/signals.py`

- [ ] **Step 1: Substituir o arquivo por versão limpa**

O arquivo atual contém apenas código comentado sem valor. Substituir por:

```python
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import FolhaPagamento

# Signals do módulo de Folha de Pagamento
# Atualmente sem signals ativos — lógica de cálculo é acionada explicitamente
# via action POST /api/folha/folha-pagamento/{id}/calcular/
```

- [ ] **Step 2: Verificar sintaxe**

```bash
python3 -c "import ast; ast.parse(open('backend/apps/folha/signals.py').read()); print('OK')"
```

Esperado: `OK`

- [ ] **Step 3: Commit**

```bash
git add backend/apps/folha/signals.py
git commit -m "chore(folha): limpa signals.py — remove código comentado sem valor"
```

---

## Task 4: Verificar frontend do módulo de Folha

**Files:**
- Read: `frontend/src/views/folha/FuncionarioListView.vue`
- Read: `frontend/src/views/folha/FuncionarioDetailView.vue`
- Read: `frontend/src/views/folha/FolhaPagamentoListView.vue`
- Read: `frontend/src/services/folha.service.js`

- [ ] **Step 1: Verificar ausência de placeholders**

```bash
grep -rn "em desenvolvimento\|Em breve\|placeholder_content\|TODO\|FIXME" frontend/src/views/folha/
```

Esperado: nenhuma ocorrência (ou só atributos `placeholder=` de inputs HTML).

- [ ] **Step 2: Verificar que o service tem todos os métodos usados nas views**

Listar métodos chamados nas views:
```bash
grep -h "FolhaService\.\|folhaService\." frontend/src/views/folha/*.vue | grep -oP '\.(get|create|update|delete|calcular|fechar|download|pdf)\w*' | sort -u
```

Listar métodos definidos no service:
```bash
grep -n "async " frontend/src/services/folha.service.js
```

Confirmar que todos os métodos usados nas views existem no service.

- [ ] **Step 3: Verificar importações nas views**

```bash
grep -n "import\|from " frontend/src/views/folha/*.vue | grep -v "//\|<!--"
```

Confirmar que todas as views importam de `@/stores/` e `@/services/` corretamente (não caminhos relativos quebrando).

- [ ] **Step 4: Verificar rotas no router**

```bash
grep -n "folha" frontend/src/router/index.js
```

Confirmar que as 3 views têm rotas registradas.

- [ ] **Step 5: Reportar resultado**

Se tudo OK: commit de encerramento.
Se encontrar problema: descrever exatamente o que está errado.

```bash
git add .
git status
```

Se não houver nada novo para commitar, apenas reportar "frontend verificado, sem problemas".

- [ ] **Step 6: Commit final**

```bash
git commit -m "fix(folha): módulo 7 auditado — 3 bugs corrigidos + frontend verificado" --allow-empty
```
