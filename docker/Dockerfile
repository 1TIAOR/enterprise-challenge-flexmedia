# Dockerfile para aplicação Python - Totem Flexmedia
FROM python:3.11-slim

# Define diretório de trabalho
WORKDIR /app

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copia arquivo de dependências
COPY requirements.txt .

# Instala dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia código da aplicação
COPY src/ ./src/
COPY scripts/ ./scripts/
COPY examples/ ./examples/

# Cria diretório para modelos ML
RUN mkdir -p src/ml/models

# Expõe porta (se necessário para API futura)
EXPOSE 8000

# Comando padrão (pode ser sobrescrito no docker-compose)
CMD ["python", "-m", "src.data_collector"]

