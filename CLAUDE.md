# CLAUDE.md — Âncora Contabilidade

Guia de contexto para assistência de desenvolvimento neste projeto.

## O que é o sistema

Sistema de gestão contábil **single-tenant** para o escritório Âncora Contabilidade. Uma única instalação gerencia a carteira de empresas-clientes do escritório. Não é um SaaS multi-tenant — a "empresa" no código é sempre uma empresa-cliente do escritório, não um tenant separado.

## Convenções obrigatórias

### Models
- **Todos** os models herdam de `ModelBase` ou `ModelBaseEmpresa` (definidos em `backend/apps/core/models.py`)
- `ModelBase`: UUID como PK, `criado_em`, `atualizado_em`, `ativo`, método `soft_delete()`
- `ModelBaseEmpresa`: herda de `ModelBase` e adiciona FK obrigatória para `Empresa`
- **Nunca** fazer DELETE físico em clientes, notas fiscais, funcionários ou lançamentos — usar `soft_delete()`
- Campos monetários: sempre `DecimalField(max_digits=15, decimal_places=2)` — nunca `FloatField`

### Isolamento por empresa
- Toda query deve filtrar por `empresa`
- ViewSets sobrescrevem `get_queryset()` para retornar apenas dados da empresa ativa (`request.user.empresa_ativa`)
- `perform_create()` injeta `empresa=obter_empresa_ativa_ou_erro(request.user)`
- Header `X-Empresa-Id` define o contexto; a empresa ativa fica em `request.user.empresa_ativa`

### Permissões
- `IsBackofficeCompany`: usuários do escritório com empresa ativa (perfil != CLIENTE)
- `IsActiveCompany`: qualquer usuário autenticado com empresa ativa
- Importar de `backend.apps.core.permissions`

### APIs
- ViewSets usam `DefaultRouter` com padrão REST
- Paginação: `StandardResultsPagination` (10 itens, retorna `count`, `total_pages`, `current_page`, `next`, `previous`, `results`)
- Erros formatados por `custom_exception_handler`: `{success, status_code, errors[], message}`

### Frontend
- Stores Pinia em `frontend/src/stores/` (auth, empresa, ui)
- Services Axios em `frontend/src/services/` — um arquivo por módulo Django
- Instância base do Axios em `frontend/src/services/api.js` (já tem interceptors de JWT)
- Notificações via `uiStore.showNotification(mensagem, 'success'|'error')`
- Empresa ativa em `empresaStore.activeEmpresa`

### Identidade visual
```
--ancora-gold:  #C6A348   (dourado institucional)
--ancora-black: #111111   (fundo principal)
--ancora-navy:  #0F1E3A   (fundo secundário)
```
- Classe Tailwind: `text-ancora-gold`, `bg-ancora-navy`, `border-ancora-gold/20`
- Fonte display: `font-display` (Cinzel/Cormorant Garamond)
- Fonte corpo: Montserrat

## Estrutura dos apps Django

```
backend/apps/
  core/          — Usuario, PerfilPermissao, LogAtividade, utils BR, pagination
  empresas/      — Empresa, ConfiguracaoFiscalEmpresa (carteira de clientes)
  cadastros/     — Cliente, Fornecedor, Produto
  fiscal/        — NotaFiscal, ItemNotaFiscal, EventoNFe, NFeService
  financeiro/    — ContaBancaria, PlanoContas, ContaAPagar, ContaAReceber, MovimentacaoFinanceira
  estoque/       — LocalEstoque, MovimentacaoEstoque, LoteEstoque, InventarioEstoque
  folha/         — Funcionario, ContratoTrabalho, FolhaPagamento, HoleriteFuncionario
  contabil/      — LancamentoContabil, BalancoPatrimonial, DRE
  obrigacoes/    — ObrigacaoFiscal, GuiaEmissao
  intake/        — PortalCliente, DocumentoRecebido, ChecklistCompetencia, Pendencia (portal de clientes)
  relatorios/    — Views de agregação: DRE simplificado, livro fiscal, estoque, folha
```

## Campos importantes por model

| Model | Campos-chave |
|---|---|
| `NotaFiscal` | `valor_produtos`, `valor_icms`, `valor_ipi`, `valor_total_nf`, `data_emissao` (DateTimeField) |
| `MovimentacaoFinanceira` | `tipo_movimentacao` ('E'=Entrada, 'S'=Saída), `data_movimentacao` (DateField), `valor` |
| `ContaAPagar` / `ContaAReceber` | `valor_total`, `valor_pago`/`valor_recebido`; `valor_saldo` é property — não usar em aggregate |
| `HoleriteFuncionario` | `salario_bruto`, `desconto_inss`, `desconto_irrf`, `desconto_fgts`, `total_proventos`, `total_descontos`, `liquido_receber` |
| `FolhaPagamento` | `competencia` (DateField — filtrar por `__year` e `__month`) |
| `Produto` | `descricao` (não `nome`), `codigo_interno`, sem campo `unidade_medida` |

## Rotas da API

```
/api/auth/         — login, refresh
/api/core/         — perfil, health
/api/empresas/     — carteira de empresas-clientes
/api/cadastros/    — clientes, fornecedores, produtos
/api/fiscal/       — notas fiscais
/api/financeiro/   — contas, fluxo de caixa
/api/estoque/      — movimentações, posição
/api/folha/        — funcionários, folha, holerites
/api/contabil/     — lançamentos, DRE, balanço
/api/obrigacoes/   — calendário, guias
/api/intake/       — portal de documentos
/api/relatorios/   — dashboard, dre, livro-fiscal, posicao-estoque, folha-competencia
```
