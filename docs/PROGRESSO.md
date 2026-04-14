# Âncora Contabilidade — Progresso de Implementação

Documento de rastreamento do estado de cada módulo. Atualizado a cada sessão de desenvolvimento.

**Última atualização:** 2026-04-13 (Módulos 9 e 10 auditados)

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
**Status: ✅ Completo** — *Auditado e corrigido em 2026-04-13*

**Fixes aplicados:**
- `BalancoPatrimonialView`: `models.Q` não estava importado → `NameError` em runtime. Corrigido adicionando `Q` ao import e substituindo todas as 6 ocorrências de `models.Q(...)` por `Q(...)`

**Frontend verificado:**
- `LancamentoContabilListView.vue` ✅ (241 linhas, real)
- `DREView.vue` ✅ (filtro por período, formatação BRL)
- `BalancoPatrimonialView.vue` ✅ (filtro por data base)
- `contabil.service.js` ✅ (todos os métodos presentes)
- Rotas registradas: `/contabil/lancamentos`, `/contabil/dre`, `/contabil/balanco` ✅

**Commits:** `fix(contabil): importa Q e corrige models.Q — NameError em BalancoPatrimonialView`

---

### Módulo 9 — Obrigações Acessórias (`apps/obrigacoes/`)
**Status: ✅ Completo** — *Auditado em 2026-04-13*

**Fixes aplicados:**
- `filterset_fields`: removido `'empresa'` do filtro exposto — get_queryset já restringe ao empresa_ativa; expor o campo era redundante e potencialmente confuso
- ObrigacaoGuiaView.vue: implementado calendário mensal com grupos colapsáveis por mês, filtro por tipo e modal de registro de pagamento

**Frontend verificado:**
- `ObrigacaoFiscalListView.vue` ✅ (CRUD completo com modal, filtro por descrição)
- `ObrigacaoGuiaView.vue` ✅ (calendário mensal com colapsáveis, filtro por tipo, modal de registro de pagamento)
- `obrigacoes.service.js` ✅ (todos os métodos: getObrigacoes, create, update, delete, vencendo_hoje, vencendo_proximos_dias)
- Rotas registradas: `/obrigacoes/calendario`, `/obrigacoes/guias` ✅

---

### Módulo 10 — Relatórios (`apps/relatorios/`)
**Status: ✅ Completo** — *Auditado em 2026-04-13*

**Estrutura:**
- Sem `models.py` ou `serializers.py` — apenas views de agregação
- Usa `garantir_empresa_padrao(request.user)` (função válida em `core/utils.py:146`)

**Backend verificado:**
- `DashboardView` ✅ (KPIs: NF-e do mês, contas vencendo, saldo bancário)
- `DREView` ✅ (receitas/despesas por período com breakdown por conta)
- `LivroFiscalView` ✅ (NF-e autorizadas por período com totais)
- `PosicaoEstoqueView` ✅ (produtos com controla_estoque=True + alerta_minimo)
- `FolhaCompetenciaView` ✅ (totais de holerites por competência YYYY-MM)

**Frontend verificado:**
- `RelatorioView.vue` ✅ (implementação real — não é placeholder; 5 seções: DRE, Livro Fiscal, Estoque, Folha, links Contábil)
- `relatorios.service.js` ✅ (getDashboard, getDRE, getLivroFiscal, getPosicaoEstoque, getFolhaCompetencia)
- Rota registrada: `/relatorios` ✅

---

### Módulo 11 — Intake / Portal do Cliente (`apps/intake/`)
**Status: ⚠️ Planejado**
- Plano em `intake-plan.md`
- Models: PortalCliente, DocumentoRecebido, ChecklistCompetencia, Pendencia
- Integração Questor

---

## Próximos passos sugeridos

1. Implementar Módulo 11 (Intake/Portal)

---

## Padrões de bugs recorrentes encontrados

| Bug | Módulo(s) | Correção |
|---|---|---|
| `float()` em vez de `Decimal()` para campos numéricos | Estoque | `Decimal(str(valor))` com `except InvalidOperation` |
| Bypass `is_superuser` em `get_queryset` | Folha | Remover bypass, filtrar sempre por `empresa_ativa` |
| Signal com `pass` (não implementado) | Estoque | Implementar lógica de delta |
| Método ausente no service frontend | Folha | Verificar métodos usados nas views x definidos no service |
| `models.Q` usado sem import de `models` | Contábil | Adicionar `Q` ao import e substituir `models.Q(...)` por `Q(...)` |
