# Âncora Contabilidade — Progresso de Implementação

Documento de rastreamento do estado de cada módulo. Atualizado a cada sessão de desenvolvimento.

**Última atualização:** 2026-04-13

---

## Legenda

- ✅ Completo (backend + frontend sem gaps conhecidos)
- ⚠️ Parcial (implementado mas com gaps ou não verificado)
- ❌ Não iniciado / apenas placeholder
- 🔧 Em progresso

---

## Módulos

### Módulo 1 — Core (`apps/core/`)
**Status: ✅ Completo**
- Usuario, PerfilPermissao, LogAtividade
- JWT customizado (`CustomTokenObtainPairSerializer`)
- Utilitários BR: CPF, CNPJ, CEP, INSS, IRRF, FGTS
- ModelBase, ModelBaseEmpresa, StandardResultsPagination
- Permissões: IsBackofficeCompany, IsActiveCompany

---

### Módulo 2 — Empresas (`apps/empresas/`)
**Status: ✅ Completo**
- Empresa, ConfiguracaoFiscalEmpresa
- Action `selecionar`, `buscar_cep`, `resumo_fiscal`
- Frontend: lista (card/lista toggle), formulário completo, dark/light mode
- Fixes aplicados: scroll, toggle card/lista

---

### Módulo 3 — Cadastros (`apps/cadastros/`)
**Status: ✅ Completo**
- Cliente, Fornecedor, Produto
- Formulários completos com todos os campos fiscais
- Frontend implementado

---

### Módulo 4 — Fiscal (`apps/fiscal/`)
**Status: ✅ Completo**
- NotaFiscal, ItemNotaFiscal, EventoNotaFiscal
- NFeService: gerar XML, assinar, enviar SEFAZ, DANFE PDF
- Formulário completo de NF-e com gestão de itens
- Frontend implementado

---

### Módulo 5 — Financeiro (`apps/financeiro/`)
**Status: ✅ Completo**
- ContaBancaria, PlanoContas, ContaAPagar, ContaAReceber, MovimentacaoFinanceira
- Fluxo de caixa, contas vencendo hoje
- Modais completos de pagamento/recebimento
- Frontend implementado

---

### Módulo 6 — Estoque (`apps/estoque/`)
**Status: ✅ Completo** — *Auditado e corrigido em 2026-04-13*

**Fixes aplicados:**
- `float(quantidade)` → `Decimal(str(quantidade))` nas actions `entrada` e `saida`
- Signal de AJUSTE: implementado delta (positivo = acréscimo, negativo = decréscimo)
- Comentários de TRANSFERENCIA/INVENTARIO adicionados no `post_delete`

**Frontend implementado:**
- `estoque.service.js` — todos os métodos de API
- `EstoquePosicaoView.vue` — tabela com badges ZERADO/CRÍTICO/OK, paginação
- `EstoqueMovimentacaoView.vue` — lista com filtros + modais Nova Entrada / Nova Saída / Ajuste

**Commits:** `6edd617` → `1f56c97`

---

### Módulo 7 — Folha de Pagamento (`apps/folha/`)
**Status: ✅ Completo** — *Auditado e corrigido em 2026-04-13*

**Fixes aplicados:**
- `BaseFolhaViewSet.get_queryset()`: removido bypass `is_superuser` que violava isolamento por empresa
- `HoleriteFuncionario.calcular()`: filtro de contrato ativo agora respeita `data_fim` (`Q(data_fim__isnull=True) | Q(data_fim__gte=competencia)`)
- `signals.py`: limpo (removido código comentado morto)
- `folha.service.js`: adicionado método `deleteJustificativa` que estava ausente

**Frontend verificado:**
- `FuncionarioListView.vue` ✅
- `FuncionarioDetailView.vue` ✅ (bug `deleteJustificativa` corrigido)
- `FolhaPagamentoListView.vue` ✅ (calcular/fechar/holerites funcionais)
- Rotas registradas ✅

**Commits:** `aac7c47` → `4624a45`

---

### Módulo 8 — Contábil (`apps/contabil/`)
**Status: ❌ Não verificado**
- LancamentoContabil, BalancoPatrimonial, DRE
- SPED: EFD ICMS-IPI, ECD

---

### Módulo 9 — Obrigações Acessórias (`apps/obrigacoes/`)
**Status: ❌ Não verificado**
- ObrigacaoFiscal, GuiaEmissao
- Calendário fiscal, DARF, PGDAS-D

---

### Módulo 10 — Relatórios (`apps/relatorios/`)
**Status: ❌ Não verificado**
- Dashboard, DRE simplificado, livro fiscal, posição estoque, folha por competência

---

### Módulo 11 — Intake / Portal do Cliente (`apps/intake/`)
**Status: ⚠️ Planejado**
- Plano em `intake-plan.md`
- Models: PortalCliente, DocumentoRecebido, ChecklistCompetencia, Pendencia
- Integração Questor

---

## Próximos passos sugeridos

1. Auditar e corrigir Módulo 8 (Contábil)
2. Auditar e corrigir Módulo 9 (Obrigações)
3. Auditar e corrigir Módulo 10 (Relatórios)
4. Implementar Módulo 11 (Intake/Portal)

---

## Padrões de bugs recorrentes encontrados

| Bug | Módulo(s) | Correção |
|---|---|---|
| `float()` em vez de `Decimal()` para campos numéricos | Estoque | `Decimal(str(valor))` com `except InvalidOperation` |
| Bypass `is_superuser` em `get_queryset` | Folha | Remover bypass, filtrar sempre por `empresa_ativa` |
| Signal com `pass` (não implementado) | Estoque | Implementar lógica de delta |
| Método ausente no service frontend | Folha | Verificar métodos usados nas views x definidos no service |
