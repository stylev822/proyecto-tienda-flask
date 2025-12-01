import os
import psycopg2
from psycopg2.extras import DictCursor
from flask import g

# Configuración de la BD (Cloud-Ready)
# os.getenv busca la variable en el servidor. Si no existe, usa el segundo valor (tu local).
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "mi_base")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "12345") 
DB_PORT = os.getenv("DB_PORT", "5432")

def get_db():
    if 'db' not in g:
        g.db = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT,
            cursor_factory=DictCursor
        )
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()