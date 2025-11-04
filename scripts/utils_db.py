import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

PG_USER = os.getenv('PG_USER')
PG_PASSWORD = os.getenv('PG_PASSWORD')
PG_HOST = os.getenv('PG_HOST', 'localhost')
PG_PORT = os.getenv('PG_PORT', '5432')
PG_DATABASE = os.getenv('PG_DATABASE')

DB_URL = f"postgresql+psycopg2://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DATABASE}"
engine = create_engine(DB_URL, future=True)

def exec_sql_file(path: str):
    with engine.begin() as conn:
        with open(path, 'r', encoding='utf-8') as f:
            conn.execute(text(f.read()))
