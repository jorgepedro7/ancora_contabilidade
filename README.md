# Âncora Contabilidade

Sistema de Gestão Contábil moderno focado em robustez, automação e conformidade (eSocial/Fiscal).

## 🚀 Funcionalidades Atuais

- **Módulo de Folha de Pagamento**:
  - Cadastro completo de funcionários e contratos.
  - Motor de cálculo automático (INSS, IRRF, FGTS, Horas Extras, DSR).
  - Gestão de cartões de ponto e ocorrências (atestados, faltas).
  - Emissão de holerites em PDF.
- **Gestão Multi-Empresa**: Arquitetura pronta para múltiplos tenants com separação total de dados.
- **GED (Gestão Eletrônica de Documentos)**: Prontuário digital de funcionários.
- **Integrações**: Pronto para integração com sistemas fiscais e bancários.

## 🛠️ Tecnologias

- **Backend**: Django 4.2 + Django REST Framework.
- **Frontend**: Vue.js 3 + Vite + Tailwind CSS / Vanilla CSS.
- **Banco de Dados**: PostgreSQL.
- **Fila de Tarefas**: Celery + Redis.
- **Infraestrutura**: Docker & Docker Compose.
- **PDF**: ReportLab.

## 📦 Como rodar o projeto

### Pré-requisitos
- Docker e Docker Compose instalados.

### Passos
1. Clone o repositório.
2. Crie um arquivo `.env` na raiz (use o `.env.example` como base).
3. Suba os containers:
   ```bash
   docker-compose up -d --build
   ```
4. Execute as migrações do banco:
   ```bash
   docker-compose exec backend python manage.py migrate
   ```
5. Crie um superusuário:
   ```bash
   docker-compose exec backend python manage.py createsuperuser
   ```
6. (Opcional) Popule o sistema com dados de teste para a Folha:
   ```bash
   docker-compose exec backend python manage.py seed_payroll
   ```

Acesse o sistema em: `http://localhost`

## 📄 Licença
Este projeto é para uso interno da Âncora Contabilidade.
