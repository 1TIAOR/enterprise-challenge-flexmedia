# Docker - Totem Flexmedia

## Arquivos Docker

- `Dockerfile` - Imagem para aplicação Python/API
- `Dockerfile.dashboard` - Imagem para Dashboard Streamlit

## Uso

### Desenvolvimento Local

```bash
# Iniciar todos os serviços
docker-compose up -d

# Ver logs
docker-compose logs -f

# Parar serviços
docker-compose down

# Parar e remover volumes (limpar dados)
docker-compose down -v
```

### Serviços Disponíveis

- **PostgreSQL**: `localhost:5432`
- **API/Coletor**: `localhost:8000` (quando implementado)
- **Dashboard**: `localhost:8501`

### Variáveis de Ambiente

Copie `env.example` para `.env` e ajuste conforme necessário:

```bash
cp env.example .env
```

### Volumes

- `postgres_data`: Dados persistentes do PostgreSQL
- `./src/ml/models`: Modelos ML treinados
- `./src`: Código-fonte (montado para desenvolvimento)

### Healthchecks

O PostgreSQL possui healthcheck configurado. Os serviços dependentes aguardam o banco estar saudável antes de iniciar.

