# scripts/etl_load_products.py
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

load_dotenv()

engine = create_engine(
    f"postgresql+psycopg2://{os.getenv('PG_USER')}:{os.getenv('PG_PASSWORD')}"
    f"@{os.getenv('PG_HOST')}:{os.getenv('PG_PORT')}/{os.getenv('PG_DATABASE')}"
)

print("Loading dim_product...")

# Create product dimension from order_items.csv
try:
    df_items = pd.read_csv("data/order_items.csv")
    unique_products = df_items["product_id"].drop_duplicates().sort_values().reset_index(drop=True)
    df_products = pd.DataFrame({
        "product_id": unique_products,
        "product_name": [f"Product_{pid}" for pid in unique_products],
        "category": ["General"] * len(unique_products)
    })
    df_products.to_sql("dim_product", engine, if_exists="append", index=False, method="multi", chunksize=1000)
    print(f"Loaded {len(df_products)} products into dim_product")
except Exception as e:
    print("Error loading dim_product:", e)

print("dim_product load complete.")
