# Gemini CLI (forma mais confiável — passa o arquivo direto)
gemini --file PROMPT_ANCORA_CLI.md

# Ou embutindo o conteúdo na linha de comando
gemini "$(cat PROMPT_ANCORA_CLI.md)"

# Se quiser modo interativo com contexto do projeto
gemini chat --file PROMPT_ANCORA_CLI.md

# Dentro de um diretório de projeto (o Gemini CLI lê o contexto dos arquivos)
cd ancora_contabilidade
gemini "$(cat ../PROMPT_ANCORA_CLI.md)"
---

## CONTEXTO DO PROJETO

Você vai construir o **Âncora Contabilidade System**, um sistema web completo de gestão contábil para o escritório de contabilidade **Âncora Contabilidade**. O sistema gerencia múltiplos clientes (empresas), emite documentos fiscais, calcula folha de pagamento, controla estoque, gera obrigações acessórias e produz relatórios contábeis.

---

## IDENTIDADE VISUAL — ÂNCORA CONTABILIDADE

### Paleta de Cores (use exatamente estes valores)
| Nome                  | HEX     | RGB           | CMYK              |
|-----------------------|---------|---------------|-------------------|
| Dourado Institucional | #C6A348 | 198, 163, 72  | 0, 35, 85, 10     |
| Preto Institucional   | #111111 | 17, 17, 17    | 0, 0, 0, 93       |
| Branco Oficial        | #FFFFFF | 255, 255, 255 | 0, 0, 0, 0        |
| Azul Marinho (Apoio)  | #0F1E3A | 15, 30, 58    | 74, 48, 0, 77     |

### Tipografia
- **Primária (Logo/Títulos):** Cinzel Bold ou Cormorant Garamond Semibold — caixa alta com leve letter-spacing
- **Secundária (UI/Subtítulos):** Montserrat Medium
- **Interface (Corpo de texto):** Montserrat Regular, 14px base

### Tom Visual
- Elegante, sóbrio e profissional
- Fundo escuro (#111111 ou #0F1E3A) com acentos dourados (#C6A348)
- Cards com borda dourada sutil, sombras suaves em azul-marinho
- Ícones minimalistas, sem excessos decorativos

---

## STACK TECNOLÓGICA OBRIGATÓRIA

### Backend
- **Python 3.11+** com **Django 4.2**
- **Django REST Framework 3.14** (API REST)
- **djangorestframework-simplejwt 5.3** (autenticação JWT)
- **django-cors-headers** (CORS para Vue.js)
- **django-filter** (filtros avançados na API)
- **psycopg2-binary** (driver PostgreSQL)
- **PostgreSQL 15+** (banco de dados principal)
- **Celery + Redis** (tarefas assíncronas: envio SEFAZ, eSocial, relatórios)
- **lxml + signxml + cryptography** (assinatura digital XML NF-e)

### Frontend
- **Vue.js 3** com Composition API
- **Vite** (build tool)
- **Pinia** (gerenciamento de estado)
- **Vue Router 4** (roteamento)
- **Axios** (chamadas HTTP à API)
- **Tailwind CSS** (estilização — customizado com as cores da Âncora)
- **Chart.js ou Recharts** (gráficos no dashboard)
- **@vueuse/core** (utilitários reativos)

### Infraestrutura
- **Docker + Docker Compose** (todos os serviços containerizados)
- **Nginx** (reverse proxy — redireciona /api/ para Django e / para Vue.js)
- **Gunicorn** (WSGI para produção)

---

## ESTRUTURA DE PASTAS EXATA

```
ancora_contabilidade/
├── backend/
│   ├── manage.py
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── config/
│   │   ├── __init__.py          # import celery app (com try/except)
│   │   ├── settings.py          # settings com fallback para ambiente local
│   │   ├── urls.py              # URLs principais da API
│   │   ├── wsgi.py
│   │   └── celery.py
│   └── apps/
│       ├── core/                # Usuário customizado, logs, utils BR
│       ├── empresas/            # Cadastro de empresas clientes
│       ├── cadastros/           # Clientes, Fornecedores, Produtos
│       ├── fiscal/              # NF-e, NFS-e, NFC-e, integração SEFAZ
│       ├── financeiro/          # Contas a pagar/receber, fluxo de caixa
│       ├── estoque/             # Entradas, saídas, inventário
│       ├── folha/               # Folha de pagamento, eSocial
│       ├── contabil/            # Lançamentos, DRE, Balanço, SPED
│       ├── obrigacoes/          # DARF, DIRF, calendário fiscal
│       └── relatorios/          # Dashboards e exportações
├── frontend/
│   ├── index.html
│   ├── vite.config.js
│   ├── tailwind.config.js       # com as cores da Âncora
│   ├── src/
│   │   ├── main.js
│   │   ├── App.vue
│   │   ├── router/index.js
│   │   ├── stores/              # Pinia stores
│   │   │   ├── auth.js
│   │   │   ├── empresa.js
│   │   │   └── ui.js
│   │   ├── services/            # Axios services por módulo
│   │   │   ├── api.js           # instância base do axios com interceptors
│   │   │   ├── auth.service.js
│   │   │   ├── empresas.service.js
│   │   │   ├── fiscal.service.js
│   │   │   └── ...
│   │   ├── views/               # Páginas (uma por rota)
│   │   │   ├── LoginView.vue
│   │   │   ├── DashboardView.vue
│   │   │   ├── empresas/
│   │   │   ├── fiscal/
│   │   │   ├── financeiro/
│   │   │   ├── folha/
│   │   │   └── ...
│   │   └── components/          # Componentes reutilizáveis
│   │       ├── layout/
│   │       │   ├── AppHeader.vue
│   │       │   ├── AppSidebar.vue
│   │       │   └── AppFooter.vue
│   │       ├── ui/              # Botões, Inputs, Cards, Modais, Tabelas
│   │       └── charts/
├── nginx/nginx.conf
├── docker-compose.yml
├── .env.example
└── setup_local.sh               # script de setup para desenvolvimento
```

---

## MÓDULOS E FUNCIONALIDADES DETALHADAS

### MÓDULO 1 — CORE (apps/core/)
**Usuário customizado:**
- Login por e-mail (não username)
- Model: `Usuario(AbstractBaseUser)` com campos: id (UUID), email, nome, telefone, avatar, empresa_ativa (FK), is_active, is_staff
- Manager: `UsuarioManager` com `create_user` e `create_superuser`

**Permissões por empresa (multi-tenancy):**
- Model: `PerfilPermissao` — um usuário pode ter perfis diferentes em empresas diferentes
- Perfis: ADMIN, CONTADOR, AUXILIAR, FINANCEIRO, CONSULTA
- Permissões granulares: pode_emitir_nf, pode_cancelar_nf, pode_ver_folha, etc.

**Auditoria:**
- Model: `LogAtividade` — registra TODAS as ações (CREATE, UPDATE, DELETE, VIEW, EXPORT, LOGIN)
- Campos: usuario, empresa, acao, modulo, objeto_tipo, objeto_id, dados_anteriores (JSON), dados_novos (JSON), ip_address

**Utilitários brasileiros (utils.py):**
- `validar_cpf(cpf)` — algoritmo oficial Receita Federal
- `validar_cnpj(cnpj)` — algoritmo oficial Receita Federal
- `formatar_cpf(cpf)` — 12345678900 → 123.456.789-00
- `formatar_cnpj(cnpj)` — 12345678000195 → 12.345.678/0001-95
- `buscar_cep(cep)` — consulta ViaCEP e retorna endereço completo
- `calcular_inss(salario)` — tabela progressiva 2024
- `calcular_irrf(base, dependentes)` — tabela progressiva 2024
- `calcular_fgts(salario)` — 8% do salário
- `gerar_chave_acesso_nfe(...)` — gera chave de acesso 44 dígitos com DV

**Classes base (pagination.py):**
- `ModelBase` — model abstrato com: id (UUID), criado_em, atualizado_em, ativo + método `soft_delete()`
- `ModelBaseEmpresa(ModelBase)` — adiciona FK obrigatória para Empresa (multi-tenancy)
- `StandardResultsPagination` — paginação com: count, total_pages, current_page, next, previous, results
- `custom_exception_handler` — formata erros em: {success, status_code, errors[], message}

**JWT customizado:**
- `CustomTokenObtainPairSerializer` — retorna access, refresh + dados do usuário no login
- Endpoint POST /api/auth/login/ retorna: {access, refresh, user: {id, nome, email, empresa_ativa}}

---

### MÓDULO 2 — EMPRESAS (apps/empresas/)
**Model Empresa:**
- Identificação: razao_social, nome_fantasia, cnpj (validado), inscricao_estadual, inscricao_municipal, cnae_principal, cnae_secundarios (JSON)
- Tributação: regime_tributario (SN, SNEI, LP, LR, LA, MEI, ENTE), porte (MEI, ME, EPP, MEDIO, GRANDE)
- Endereço completo com código IBGE do município
- Certificado digital: arquivo .pfx, senha (criptografada), data_validade
- Property `certificado_vencido` que compara data_validade com hoje
- Property `nome_exibicao` → nome_fantasia ou razao_social
- Property `endereco_completo` → string formatada

**Model ConfiguracaoFiscalEmpresa:**
- Séries e próximos números de NF-e, NFS-e, NFC-e
- Ambiente SEFAZ (1=Produção, 2=Homologação) por empresa
- CSC ID e CSC Token para NFC-e
- Método `proximo_numero_nfe()` com SELECT FOR UPDATE (thread-safe)

**ViewSet EmpresaViewSet:**
- Actions extras: `selecionar` (define empresa_ativa no usuário), `buscar_cep`, `resumo_fiscal`
- Filtros: regime_tributario, uf, ativo, porte
- Busca: razao_social, nome_fantasia, cnpj
- Soft delete (apenas desativa, não remove)

---

### MÓDULO 3 — CADASTROS (apps/cadastros/)
**Clientes e Fornecedores (herdam de PessoaBase):**
- Suporte a PF, PJ e Exterior
- Todos os campos fiscais: indicador_ie, CNPJ/CPF validados
- Endereço completo com código IBGE
- Dados bancários do fornecedor (para pagamentos via PIX/TED)

**Produtos:**
- Código interno, EAN/código de barras
- Classificação fiscal completa: NCM, CEST, CFOP padrão, origem
- Tributação completa: ICMS (CST/CSOSN, alíquota, MVA-ST), IPI (CST, alíquota), PIS/COFINS (CST, alíquota)
- Preços: custo, venda, margem de lucro
- Estoque: mínimo, máximo, atual, controla_estoque (boolean)
- Peso e dimensões (para campos de transporte na NF-e)

**Tabelas de Preço:**
- Múltiplas tabelas por empresa
- Preço e desconto específico por produto em cada tabela
- Vínculo com cadastro de clientes

---

### MÓDULO 4 — FISCAL (apps/fiscal/)
**Model NotaFiscal (NF-e Modelo 55 e NFC-e Modelo 65):**
Status: RASCUNHO → PENDENTE → PROCESSANDO → AUTORIZADA / REJEITADA / CANCELADA / DENEGADA

Campos obrigatórios conforme layout SEFAZ 4.0:
- Identificação: chave_acesso (44 dígitos), protocolo, número, série, modelo, tipo_nf, finalidade
- Destinatário completo com endereço
- Totais: produtos, desconto, frete, seguro, outras_despesas, ICMS, ICMS-ST, IPI, PIS, COFINS, total_nf
- Transporte: modalidade_frete, transportadora (FK)
- Arquivos: xml_autorizado, xml_cancelamento, pdf_danfe (FileField)
- Retorno SEFAZ: codigo_retorno, mensagem_retorno

**Model ItemNotaFiscal:**
- Produto com todos os campos fiscais por item
- Tributação completa: ICMS, ICMS-ST, IPI, PIS, COFINS (base, alíquota, valor)
- Método `save()` calcula valor_total automaticamente

**Model EventoNotaFiscal:**
- Tipos: Cancelamento (110110), Carta de Correção (110114), EPEC (110115)
- Armazena XML do evento e protocolo de retorno

**Service NFeService (services.py):**
- `gerar_xml(nota_fiscal)` — gera XML conforme layout 4.0
- `assinar_xml(xml, certificado_pfx, senha)` — assina com signxml + cryptography
- `enviar_sefaz(xml_assinado, uf, ambiente)` — envia via requests para webservice SOAP
- `processar_retorno(xml_retorno)` — parseia resposta e atualiza status da nota
- `gerar_danfe(nota_fiscal)` — gera PDF do DANFE com ReportLab
- `cancelar_nota(nota_fiscal, justificativa)` — envia evento de cancelamento
- `carta_correcao(nota_fiscal, texto)` — envia CC-e

**Task Celery (tasks.py):**
- `autorizar_nota.delay(nota_id)` — envia para SEFAZ de forma assíncrona
- `sincronizar_notas_pendentes()` — verifica notas em processamento a cada 30 min

---

### MÓDULO 5 — FINANCEIRO (apps/financeiro/)
**ContaBancaria:** CC, CP, Aplicação, Caixa — com saldo_atual atualizado a cada movimentação

**PlanoContas:** Hierárquico, com tipos RC/DS/AT/PA/PL — base para DRE e Balanço

**ContaAPagar e ContaAReceber:**
- Status: ABERTA → PARCIAL → PAGA/RECEBIDA
- Suporte a parcelas (parcela_atual / total_parcelas)
- Juros, multa e desconto
- Geração automática de MovimentacaoFinanceira ao pagar/receber
- Property `esta_vencida` e `valor_saldo`

**MovimentacaoFinanceira:**
- Tipo: E (Entrada), S (Saída), T (Transferência)
- Sempre vinculada a uma ContaBancaria
- Atualiza `saldo_atual` da conta automaticamente via signal Django

**Endpoints da API:**
- `GET /api/financeiro/fluxo-caixa/?data_inicio=&data_fim=` → DRE simplificado do período
- `GET /api/financeiro/contas-pagar/?vencimento=hoje&status=ABERTA` → contas vencendo hoje
- `POST /api/financeiro/contas-receber/{id}/receber/` → registra recebimento

---

### MÓDULO 6 — ESTOQUE (apps/estoque/)
**Models:**
- `LocalEstoque` — prateleiras, galpões, centros de distribuição
- `MovimentacaoEstoque` — entrada, saída, transferência, ajuste, inventário
- `LoteEstoque` — controle por lote e validade
- `InventarioEstoque` — inventário periódico com divergências

**Regras:**
- Toda movimentação atualiza `Produto.estoque_atual` via signal
- Entrada de NF-e gera `MovimentacaoEstoque` automaticamente
- Alerta quando estoque_atual < estoque_minimo

---

### MÓDULO 7 — FOLHA DE PAGAMENTO (apps/folha/)
**Models:**
- `Cargo` com CBO
- `Departamento` com centro_custo
- `Funcionario` — dados pessoais completos, PIS, CTPS, dados bancários
- `ContratoTrabalho` — CLT, PJ, Aprendiz, Estágio; salário, benefícios, categoria eSocial
- `FolhaPagamento` — competência, tipo (Mensal, 13º, Férias, Rescisão)
- `HoleriteFuncionario` — proventos e descontos individuais

**Cálculos automáticos em HoleriteFuncionario.calcular():**
- INSS pela tabela progressiva 2024 (faixas: 7,5% / 9% / 12% / 14%)
- IRRF pela tabela progressiva 2024 com dedução por dependente de R$189,59
- FGTS = 8% do salário bruto
- INSS patronal = 20% do salário bruto
- Horas extras 50% e 100%

**Geração de holerite PDF** via ReportLab com logo da Âncora Contabilidade

**eSocial (fase futura):**
- S-2200: Cadastramento inicial do vínculo
- S-1200: Remuneração do trabalhador
- S-2299: Desligamento

---

### MÓDULO 8 — CONTÁBIL (apps/contabil/)
**Models:**
- `LancamentoContabil` — débito/crédito com conta do plano de contas
- `PartidaLancamento` — débitos e créditos de cada lançamento
- Lançamentos automáticos gerados por NF-e, folha e movimentações financeiras

**Relatórios contábeis:**
- DRE (Demonstração do Resultado do Exercício)
- Balancete de Verificação
- Balanço Patrimonial
- Razão por conta

**SPED:**
- Geração do arquivo EFD ICMS-IPI (SPED Fiscal)
- Geração do arquivo ECD (SPED Contábil)

---

### MÓDULO 9 — OBRIGAÇÕES ACESSÓRIAS (apps/obrigacoes/)
**Calendário Fiscal:**
- Model `ObrigacaoFiscal` — tipo, data_vencimento, empresa, status
- Tipos: DARF, PGDAS-D, DAE, DAS-MEI, DIRF, DCTF, DEFIS, GIA, DeSTDA, eSocial, EFD
- Task Celery `verificar_vencimentos()` diária → envia alertas por e-mail

**Guias:**
- Geração de DARF com código de receita
- Cálculo automático de DAS (Simples Nacional) via PGDAS-D
- Integração com SINTEGRA

---

### MÓDULO 10 — RELATÓRIOS (apps/relatorios/)
**Dashboard principal:**
- Total de NF-e emitidas no mês
- Contas a pagar vencendo em 5 dias
- Contas a receber vencendo em 5 dias
- Saldo total por conta bancária
- Gráfico de faturamento (últimos 12 meses)
- Gráfico de despesas por categoria

**Relatórios exportáveis (PDF e Excel):**
- Livro de Entradas e Saídas
- Apuração de ICMS
- Apuração de PIS/COFINS
- Relatório de Folha por competência
- Posição de Estoque

---

## CONFIGURAÇÕES DE SETTINGS (backend/config/settings.py)

O settings.py DEVE funcionar localmente sem Redis instalado. Use este padrão:

```python
# Carrega .env sem dependência obrigatória de django-environ
def load_env():
    env_path = BASE_DIR.parent / '.env'
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, _, value = line.partition('=')
                    os.environ.setdefault(key.strip(), value.strip())
load_env()

# config/__init__.py — import do Celery SEMPRE com try/except
try:
    from .celery import app as celery_app
    __all__ = ('celery_app',)
except ImportError:
    pass

# Celery síncrono em desenvolvimento
CELERY_TASK_ALWAYS_EAGER = True  # executa tasks inline em dev
```

---

## CONFIGURAÇÃO DO VUE.JS (tailwind.config.js)

```javascript
// tailwind.config.js — cores da Âncora Contabilidade
module.exports = {
  content: ['./src/**/*.{vue,js,ts}'],
  theme: {
    extend: {
      colors: {
        ancora: {
          gold:    '#C6A348',  // Dourado Institucional
          black:   '#111111',  // Preto Institucional
          white:   '#FFFFFF',  // Branco Oficial
          navy:    '#0F1E3A',  // Azul Marinho
        }
      },
      fontFamily: {
        display: ['"Cinzel"', '"Cormorant Garamond"', 'serif'],
        body:    ['"Montserrat"', 'sans-serif'],
      }
    }
  }
}
```

**Layout do frontend:**
- Sidebar escura (#111111 ou #0F1E3A) com itens de menu dourados ao hover
- Header com logo "ÂNCORA" em Cinzel Bold com cor dourada
- Cards com borda `border-ancora-gold/30` e fundo `bg-ancora-black/50`
- Botão primário: `bg-ancora-gold text-ancora-black font-bold`
- Botão secundário: `border border-ancora-gold text-ancora-gold`
- Tabelas com header `bg-ancora-navy` e linhas alternadas em cinza escuro
- Badges de status: AUTORIZADA=verde, REJEITADA=vermelho, PENDENTE=amarelo-dourado

---

## ROTAS DA API (config/urls.py)

```
POST   /api/auth/login/                    → JWT com dados do usuário
POST   /api/auth/refresh/                  → renovar token
GET    /api/core/health/                   → health check
GET    /api/core/perfil/                   → dados do usuário logado

GET    /api/empresas/                      → listar empresas do usuário
POST   /api/empresas/                      → cadastrar empresa
GET    /api/empresas/{id}/                 → detalhe
PUT    /api/empresas/{id}/                 → editar
POST   /api/empresas/{id}/selecionar/      → define empresa ativa na sessão
POST   /api/empresas/{id}/resumo-fiscal/   → dados fiscais da empresa
POST   /api/empresas/buscar-cep/           → consulta ViaCEP

GET    /api/cadastros/clientes/            → listar com filtro/busca/paginação
POST   /api/cadastros/clientes/
GET    /api/cadastros/fornecedores/
POST   /api/cadastros/fornecedores/
GET    /api/cadastros/produtos/
POST   /api/cadastros/produtos/

GET    /api/fiscal/notas-fiscais/          → listar NF-e
POST   /api/fiscal/notas-fiscais/          → criar NF-e em rascunho
GET    /api/fiscal/notas-fiscais/{id}/
POST   /api/fiscal/notas-fiscais/{id}/autorizar/   → envia para SEFAZ
POST   /api/fiscal/notas-fiscais/{id}/cancelar/    → cancela nota autorizada
GET    /api/fiscal/notas-fiscais/{id}/danfe/        → baixa PDF DANFE
POST   /api/fiscal/notas-fiscais/{id}/email/        → envia por e-mail

GET    /api/financeiro/contas-pagar/
POST   /api/financeiro/contas-pagar/
POST   /api/financeiro/contas-pagar/{id}/pagar/
GET    /api/financeiro/contas-receber/
POST   /api/financeiro/contas-receber/
POST   /api/financeiro/contas-receber/{id}/receber/
GET    /api/financeiro/fluxo-caixa/

GET    /api/estoque/movimentacoes/
POST   /api/estoque/entrada/
POST   /api/estoque/saida/
GET    /api/estoque/posicao/

GET    /api/folha/funcionarios/
POST   /api/folha/funcionarios/
GET    /api/folha/folha-pagamento/
POST   /api/folha/folha-pagamento/
POST   /api/folha/folha-pagamento/{id}/calcular/
GET    /api/folha/folha-pagamento/{id}/holerites/

GET    /api/obrigacoes/calendario/
GET    /api/obrigacoes/vencendo-hoje/

GET    /api/relatorios/dashboard/
GET    /api/relatorios/dre/?data_inicio=&data_fim=
```

---

## REGRAS DE DESENVOLVIMENTO

1. **TODOS os models** devem herdar de `ModelBase` ou `ModelBaseEmpresa` (UUID como PK, criado_em, atualizado_em, ativo, soft_delete)

2. **Multi-tenancy obrigatório:** toda query deve filtrar por `empresa`. Os ViewSets devem sobrescrever `get_queryset()` para retornar apenas dados da empresa ativa do usuário (lida do header `X-Empresa-Id` ou de `request.user.empresa_ativa`)

3. **Soft delete em vez de DELETE:** nunca remover registros físicos de clientes, notas fiscais, funcionários ou lançamentos contábeis

4. **Validações brasileiras:** CPF, CNPJ, CEP, PIS, CTPS devem ser validados com algoritmos corretos

5. **Internacionalização:** LANGUAGE_CODE = 'pt-br', TIME_ZONE = 'America/Sao_Paulo', USE_TZ = True

6. **Campos monetários:** sempre `DecimalField(max_digits=15, decimal_places=2)` — NUNCA FloatField para valores financeiros

7. **Índices obrigatórios:** todo model com queries frequentes deve ter `Meta.indexes` definido

8. **Transações atômicas:** operações que tocam múltiplas tabelas (ex: pagar conta + gerar movimentação + atualizar saldo) devem usar `@transaction.atomic`

9. **Logs:** toda ação relevante (emissão de NF-e, pagamento, alteração de cadastro) deve gerar um `LogAtividade`

10. **Testes:** criar testes para validadores brasileiros, cálculos de folha e geração de chave NF-e

---

## PRIORIDADE DE IMPLEMENTAÇÃO

Implemente nesta ordem:

**Fase 1 — Base (obrigatório primeiro):**
1. `config/` — settings, urls, wsgi, celery (com try/except)
2. `apps/core/` — Usuario, PerfilPermissao, LogAtividade, utils.py, pagination.py, views.py (JWT custom)
3. `apps/empresas/` — Empresa, ConfiguracaoFiscalEmpresa, ViewSet completo
4. `apps/cadastros/` — Cliente, Fornecedor, Produto (models + serializers + views)

**Fase 2 — Operacional:**
5. `apps/fiscal/` — NotaFiscal, ItemNotaFiscal, EventoNotaFiscal + NFeService
6. `apps/financeiro/` — ContaBancaria, PlanoContas, ContaAPagar, ContaAReceber, fluxo de caixa
7. `apps/estoque/` — MovimentacaoEstoque, controle de saldo

**Fase 3 — RH e Contabilidade:**
8. `apps/folha/` — Funcionario, ContratoTrabalho, FolhaPagamento com cálculos
9. `apps/contabil/` — LancamentoContabil, DRE, Balanço
10. `apps/obrigacoes/` — calendário fiscal, alertas

**Fase 4 — Frontend Vue.js:**
11. Configuração Vite + Tailwind com cores da Âncora
12. Layout principal: Sidebar + Header + Router
13. Telas: Login, Dashboard, Empresas, Clientes, NF-e, Financeiro, Folha
14. Integração com a API Django via Axios com interceptors JWT

---

## COMANDO INICIAL

Comece criando a estrutura completa de pastas e os arquivos da Fase 1. Para cada arquivo criado, verifique se os imports estão corretos e se `python manage.py check` passa sem erros antes de avançar para o próximo módulo.
