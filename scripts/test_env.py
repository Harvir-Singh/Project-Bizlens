from dotenv import load_dotenv
import os

load_dotenv()
for k in ("PG_USER","PG_PASSWORD","PG_DATABASE"):
    print(k, "→", os.getenv(k))
