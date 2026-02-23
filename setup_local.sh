#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

echo "Iniciando setup do ambiente local..."

# Navega para o diretório raiz do projeto
cd "$(dirname "$0")"

# 1. Copiar .env.example para .env se não existir
if [ ! -f .env ]; then
  echo "Criando arquivo .env a partir de .env.example..."
  cp .env.example .env
else
  echo "Arquivo .env já existe, pulando criação."
fi

# 2. Construir e levantar os serviços Docker
echo "Construindo e levantando os serviços Docker-Compose..."
docker compose build
docker compose up -d db redis

echo "Aguardando o banco de dados iniciar..."
# Espera o PostgreSQL estar pronto para aceitar conexões
until docker compose exec db pg_isready -U ancora_user -d ancora_contabilidade; do
  echo -n "."
  sleep 1
done
echo "Banco de dados iniciado!"

# 3. Executar migrações do Django
echo "Executando migrações do Django..."
docker compose run --rm backend python manage.py makemigrations core empresas cadastros # Crie as migrações para os apps
docker compose run --rm backend python manage.py migrate

# 4. Criar superusuário Django (se não existir)
echo "Verificando/Criando superusuário Django..."
docker compose run --rm backend python manage.py createsuperuser --noinput || true # --noinput evita interação, || true ignora erro se já existir

# 5. Instalar dependências do frontend
echo "Instalando dependências do frontend..."
docker compose run --rm frontend npm install

# 6. Levantar todos os serviços Docker
echo "Levantando todos os serviços Docker-Compose (incluindo backend e frontend)..."
docker compose up -d

echo "Setup concluído! Acesse o frontend em http://localhost ou a API em http://localhost/api/"
echo "Para parar os serviços: docker compose down"
echo "Para acessar o shell do Django: docker compose exec backend python manage.py shell"
echo "Para rodar testes do Django: docker compose exec backend python manage.py test"
echo "Para ver logs: docker compose logs -f"
