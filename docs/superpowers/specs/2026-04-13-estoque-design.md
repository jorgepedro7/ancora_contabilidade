# Design — Módulo 6: Estoque

**Data:** 2026-04-13  
**Escopo:** Correções de backend + frontend completo  
**Abordagem:** Sequential (backend → frontend)

---

## Estado Atual

### Backend (existe, com defeitos)
- Models: `LocalEstoque`, `MovimentacaoEstoque`, `LoteEstoque`, `InventarioEstoque` — schema OK
- ViewSets com filtros, actions `entrada`, `saida`, `finalizar_inventario`, `cancelar_inventario`
- Signal atualiza `estoque_atual` do produto, mas AJUSTE tem `pass` (não implementado)
- Migrations aplicadas (`0001_initial.py`)

### Frontend (placeholders)
- `EstoqueMovimentacaoView.vue` — só texto "em desenvolvimento"
- `EstoquePosicaoView.vue` — só texto "em desenvolvimento"
- Sem `estoque.service.js`

---

## Correções do Backend

### 1. float → Decimal (views.py)
- Actions `entrada` e `saida` usam `float(quantidade)` — viola regra de campos numéricos
- Substituir por `Decimal(quantidade)` com `try/except InvalidOperation`
- Import: `from decimal import Decimal, InvalidOperation`

### 2. Signal de AJUSTE (signals.py)
- Tipo `AJUSTE`: `quantidade` representa **delta** (positivo = acréscimo, negativo = decréscimo)
- Aplicar: `produto.estoque_atual += instance.quantidade`
- Remover o `pass` e implementar a lógica corretamente

### 3. finalizar_inventario (views.py)
- Escopo simples: apenas muda status para `FINALIZADO`
- Já funciona assim — manter sem alteração

---

## Frontend

### estoque.service.js
Arquivo novo em `frontend/src/services/estoque.service.js`.

Métodos:
| Método | Endpoint | Descrição |
|---|---|---|
| `listarLocais()` | `GET /api/estoque/locais/` | Lista locais de estoque |
| `listarMovimentacoes(params)` | `GET /api/estoque/movimentacoes/` | Lista com filtros |
| `registrarEntrada(data)` | `POST /api/estoque/movimentacoes/entrada/` | Registra entrada |
| `registrarSaida(data)` | `POST /api/estoque/movimentacoes/saida/` | Registra saída |
| `registrarAjuste(data)` | `POST /api/estoque/movimentacoes/` | Registra ajuste (delta) |
| `getPosicao(params)` | `GET /api/estoque/posicao/` | Posição atual de estoque |
| `listarInventarios(params)` | `GET /api/estoque/inventarios/` | Lista inventários |
| `abrirInventario(data)` | `POST /api/estoque/inventarios/` | Cria inventário |
| `finalizarInventario(id)` | `POST /api/estoque/inventarios/{id}/finalizar_inventario/` | Finaliza |
| `cancelarInventario(id)` | `POST /api/estoque/inventarios/{id}/cancelar_inventario/` | Cancela |

---

### EstoquePosicaoView.vue
Rota: `/estoque/posicao`

**Funcionalidades:**
- Tabela de produtos com colunas: Código, Descrição, Estoque Atual, Estoque Mínimo, Estoque Máximo, Status
- Alerta visual: linha/badge em vermelho quando `estoque_atual < estoque_minimo`
- Filtro por nome/código (campo de busca)
- Badge de status: OK (verde), CRÍTICO (vermelho), ZERADO (cinza)
- Sem paginação complexa — usa paginação padrão `StandardResultsPagination`

---

### EstoqueMovimentacaoView.vue
Rota: `/estoque/movimentacoes`

**Funcionalidades:**
- Lista de movimentações com colunas: Data, Tipo, Produto, Quantidade, Local Origem, Local Destino, Observações
- Filtros: Tipo de movimentação, Produto (busca)
- Badge colorido por tipo: ENTRADA (verde), SAIDA (vermelho), AJUSTE (amarelo), TRANSFERENCIA (azul), INVENTARIO (cinza)
- Botões de ação: "Nova Entrada", "Nova Saída", "Ajuste"
- Cada botão abre um **modal** com formulário específico:

**Modal Nova Entrada:**
- Produto (select com busca)
- Quantidade
- Local de Destino (select)
- Observações

**Modal Nova Saída:**
- Produto (select com busca)
- Quantidade
- Local de Origem (select)
- Observações
- Validação: bloqueia se quantidade > estoque_atual

**Modal Ajuste:**
- Produto (select com busca)
- Delta (número, positivo ou negativo)
- Observações

---

## Padrões a Seguir

- Identidade visual: `bg-ancora-navy`, `text-ancora-gold`, `border-ancora-gold/20`
- Notificações: `uiStore.showNotification(msg, 'success'|'error')`
- Empresa ativa: `empresaStore.activeEmpresa`
- Erros de API: tratar `error.response.data.message` ou `error.response.data.errors`
- Stores: importar `useAuthStore`, `useEmpresaStore`, `useUiStore` de `@/stores/`

---

## O que NÃO está no escopo

- `ItemInventario` (model de contagem por produto no inventário)
- Tela de gestão de inventários
- Tela de lotes
- Integração automática com NF-e
- Alerta automático por e-mail de estoque mínimo
