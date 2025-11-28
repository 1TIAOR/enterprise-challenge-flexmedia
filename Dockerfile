FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY scripts/ ./scripts/
COPY examples/ ./examples/

RUN mkdir -p src/ml/models

EXPOSE 8000

CMD ["python", "-m", "src.data_collector"]

