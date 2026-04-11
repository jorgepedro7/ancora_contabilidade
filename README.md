# Âncora Contabilidade

Sistema de gestão contábil do escritório **Âncora Contabilidade**. Instalação única (single-tenant) que gerencia a carteira de empresas-clientes do escritório, integrando fiscal, financeiro, folha, contábil, estoque e portal de recebimento de documentos.

## Módulos

| Módulo | Funcionalidades |
|---|---|
| **Empresas** | Cadastro da carteira de clientes, regime tributário, certificado digital, configuração SEFAZ |
| **Fiscal** | NF-e / NFC-e — emissão, autorização SEFAZ, cancelamento, CC-e, DANFE em PDF |
| **Financeiro** | Contas a pagar/receber, fluxo de caixa, contas bancárias, plano de contas |
| **Estoque** | Movimentações, posição por produto, lotes, inventário |
| **Folha de Pagamento** | Funcionários, contratos, cálculo de INSS/IRRF/FGTS, holerite PDF, registro de ponto |
| **Contábil** | Lançamentos, DRE, Balanço Patrimonial, SPED |
| **Obrigações** | Calendário fiscal, DARF, PGDAS-D, alertas de vencimento |
| **Central de Recebimentos (Intake)** | Portal para clientes enviarem documentos, checklist por competência, exportação para Questor |
| **Relatórios** | DRE simplificado, livro fiscal, posição de estoque, folha por competência |

## Stack

- **Backend**: Django 4.2 + Django REST Framework + JWT (simplejwt)
- **Frontend**: Vue.js 3 + Vite + Pinia + Tailwind CSS
- **Banco**: PostgreSQL 15
- **Tarefas assíncronas**: Celery + Redis
- **Infraestrutura**: Docker Compose + Nginx + Gunicorn
- **PDF**: ReportLab

## Como rodar

### Pré-requisitos
- Docker e Docker Compose instalados

### Passos

```bash
# 1. Clone e configure o ambiente
cp .env.example .env

# 2. Suba os containers
docker-compose up -d --build

# 3. Execute as migrações
docker-compose exec backend python manage.py migrate

# 4. Crie um superusuário
docker-compose exec backend python manage.py createsuperuser

# 5. (Opcional) Popule com dados de teste
docker-compose exec backend python manage.py seed_payroll
```

Acesse em: `http://localhost`

## Arquitetura

O sistema é **single-tenant** — uma instalação por escritório de contabilidade. A separação de dados é por **empresa-cliente** (campo `empresa` em todos os models). Usuários do backoffice (contadores) têm perfil `ADMIN`, `CONTADOR`, `AUXILIAR`, `FINANCEIRO` ou `CONSULTA` por empresa. Clientes do escritório têm perfil `CLIENTE` e acesso restrito ao portal de intake.

O header `X-Empresa-Id` define o contexto da empresa ativa em cada requisição à API.

## Licença

Uso interno — Âncora Contabilidade.
