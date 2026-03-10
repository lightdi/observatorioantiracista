# Usar imagem oficial otimizada do Python
FROM python:3.11-slim

# Variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=run.py

# Criar e definir diretório de trabalho
WORKDIR /app

# Instalar dependências de sistema operacional necessárias para o psycopg2 (PostgreSQL)
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar os requerimentos e instalar
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copiar todo o código-fonte restante
COPY . .

# Expor a porta que a aplicação vai escutar
EXPOSE 5005

# Script de entrada para performar migrações do banco (se houverem pendentes) e rodar
CMD ["sh", "-c", "flask db upgrade && gunicorn --bind 0.0.0.0:5005 'app:create_app(\"production\")'"]
