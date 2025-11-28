"""
Script de Inicialização do Banco de Dados
Cria o banco e executa o schema
"""

import sys
import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Lê o schema SQL
schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')

def init_database():
    """Inicializa o banco de dados"""
    
    # Conecta ao PostgreSQL (sem especificar database para criar se não existir)
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=int(os.getenv('DB_PORT', 5432)),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', 'postgres')
    )
    
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()
    
    # Cria database se não existir
    db_name = os.getenv('DB_NAME', 'flexmedia_totem')
    
    try:
        cursor.execute(f"CREATE DATABASE {db_name}")
        print(f"Database '{db_name}' criado com sucesso!")
    except psycopg2.errors.DuplicateDatabase:
        print(f"Database '{db_name}' já existe.")
    
    cursor.close()
    conn.close()
    
    # Conecta ao database criado e executa schema
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=int(os.getenv('DB_PORT', 5432)),
        database=db_name,
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', 'postgres')
    )
    
    cursor = conn.cursor()
    
    # Lê e executa schema
    with open(schema_path, 'r') as f:
        schema_sql = f.read()
    
    cursor.execute(schema_sql)
    conn.commit()
    
    print("Schema executado com sucesso!")
    
    cursor.close()
    conn.close()
    
    print("✅ Banco de dados inicializado!")


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    init_database()

