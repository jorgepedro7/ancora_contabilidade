# ObrigacaoGuiaView — Design Spec

**Data:** 2026-04-14
**Módulo:** `apps/obrigacoes/`
**Arquivo alvo:** `frontend/src/views/obrigacoes/ObrigacaoGuiaView.vue`

---

## Objetivo

Substituir o placeholder da view de Guias por uma visão de calendário mensal das obrigações fiscais. O escritório usa esta tela para acompanhar o que vence em cada mês e registrar pagamentos rapidamente.

---

## Escopo

- **Apenas frontend.** Nenhuma mudança de backend, model ou migration necessária.
- A API existente (`/api/obrigacoes/obrigacoes/`) provê todos os dados.
- O service `obrigacoes.service.js` já tem `getObrigacoes` e `updateObrigacao`.

---

## Comportamento

### Carregamento

- `onMounted`: busca todas as obrigações da empresa ativa via `getObrigacoes()` (sem filtro de data — o backend já restringe por empresa_ativa).
- O agrupamento por mês é feito **no frontend** a partir de `data_vencimento`.
- São exibidos **7 meses**: 3 meses anteriores ao mês atual + mês atual + 3 meses seguintes. Meses sem obrigações aparecem com mensagem "Nenhuma obrigação neste mês."

### Filtro de tipo

- Select no topo com opções: Todos + cada `tipo_obrigacao` do model.
- Filtra reativamente no frontend (não faz nova chamada à API).

### Grupos de mês (colapsáveis)

- Cabeçalho clicável: `"Abril 2026"` + contador `"5 obrigações — 2 abertas — R$ 1.250,00 a pagar"`.
  - "a pagar" = soma dos `valor` onde `status in ['ABERTO', 'ATRASADO']`.
- **Mês atual:** aberto por padrão.
- **Demais meses:** fechados por padrão.
- Toggle via `v-show` + ícone de chevron que rotaciona.

### Linha por obrigação

Colunas: Tipo | Descrição | Vencimento | Valor | Status | Ações

- **Tipo:** label legível (ex: "DARF", "PGDAS-D")
- **Descrição:** `obrigacao.descricao` ou `—` se vazio
- **Vencimento:** data formatada `dd/mm/yyyy`; sublinhado vermelho se `esta_vencida` (calculado localmente: `data_vencimento < hoje && status not in ['PAGO','ENVIADO','CONCLUIDO']`)
- **Valor:** `R$ X.XXX,XX` ou `—` se nulo
- **Badge de status:**
  - ABERTO → `bg-blue-500`
  - ATRASADO → `bg-red-500`
  - PAGO / ENVIADO / CONCLUÍDO → `bg-green-500`
  - CANCELADO → `bg-gray-500`
- **Ações:** botão "Registrar Pagamento" visível apenas se `status in ['ABERTO', 'ATRASADO']`

### Modal de pagamento

Campos:
- `data_envio_pagamento` (date, obrigatório)
- `link_documento` (text/URL, opcional — link do comprovante)
- `observacoes` (textarea, opcional)

Ao confirmar: chama `updateObrigacao(id, { status: 'PAGO', data_envio_pagamento, link_documento, observacoes })`. Sucesso → `uiStore.showNotification('Pagamento registrado!', 'success')` + reload da lista.

---

## Identidade visual

Segue os padrões do sistema:
- Fundo: `bg-ancora-black/40`, bordas: `border-ancora-gold/20`
- Cabeçalho de mês: `bg-ancora-navy` com texto `text-ancora-gold`
- Linhas: `hover:bg-ancora-navy/30`
- Botão primário: `bg-ancora-gold text-ancora-black font-bold`
- Fonte display: `font-display` nos títulos

---

## Tratamento de erros

- Falha no `getObrigacoes`: `uiStore.showNotification('Erro ao carregar guias.', 'error')`
- Falha no `updateObrigacao`: `uiStore.showNotification('Erro ao registrar pagamento.', 'error')`
- Nenhum estado de carregamento global — apenas `loading` local por operação

---

## Arquivo alterado

| Arquivo | Ação |
|---|---|
| `frontend/src/views/obrigacoes/ObrigacaoGuiaView.vue` | Substituir placeholder pela implementação completa |

Nenhum outro arquivo alterado.
