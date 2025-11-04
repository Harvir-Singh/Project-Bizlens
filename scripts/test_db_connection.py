from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()
url = (
    f"postgresql+psycopg2://{os.getenv('PG_USER')}:{os.getenv('PG_PASSWORD')}"
    f"@{os.getenv('PG_HOST')}:{os.getenv('PG_PORT')}/{os.getenv('PG_DATABASE')}"
)
print("Connection URL:", url)

try:
    engine = create_engine(url)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT current_database();")).scalar()
        print("✅ Connected to:", result)
except Exception as e:
    print("Connection failed:", e)