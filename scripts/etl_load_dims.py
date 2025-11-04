# scripts/etl_load_dims.py
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
import hashlib

# Load environment variables
load_dotenv()

engine = create_engine(
    f"postgresql+psycopg2://{os.getenv('PG_USER')}:{os.getenv('PG_PASSWORD')}"
    f"@{os.getenv('PG_HOST')}:{os.getenv('PG_PORT')}/{os.getenv('PG_DATABASE')}"
)

print("🚀 Starting dimension data load...")

# 1️ dim_customer
try:
    df_customers = pd.read_csv("data/customers.csv")

    # Convert column names and hash email for privacy
    df_customers = df_customers.rename(columns={
        "signup_ts": "signup_date"
    })
    df_customers["email_hash"] = df_customers["email"].apply(
        lambda x: hashlib.sha256(x.encode()).hexdigest()
    )
    df_customers = df_customers[["customer_id", "email_hash", "country", "signup_date"]]

    df_customers.to_sql("dim_customer", engine, if_exists="append", index=False, method="multi", chunksize=1000)
    print(f"Loaded {len(df_customers)} customers into dim_customer")
except Exception as e:
    print("Error loading customers.csv:", e)

# 2️ dim_channel
try:
    df_spend = pd.read_csv("data/marketing_spend.csv")
    df_channels = df_spend[["channel_name"]].drop_duplicates()
    df_channels.to_sql("dim_channel", engine, if_exists="append", index=False, method="multi")
    print(f"Loaded {len(df_channels)} channels into dim_channel")
except Exception as e:
    print("Error loading marketing_spend.csv:", e)

print("Dimension data load complete.")
