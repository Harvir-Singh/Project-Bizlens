# scripts/etl_load_facts.py
import os
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# -------------------- CONFIG & CONNECTION --------------------
load_dotenv()

PG_USER = os.getenv("PG_USER")
PG_PASSWORD = os.getenv("PG_PASSWORD")
PG_HOST = os.getenv("PG_HOST")
PG_PORT = os.getenv("PG_PORT")
PG_DATABASE = os.getenv("PG_DATABASE")

engine = create_engine(
    f"postgresql+psycopg2://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DATABASE}"
)

# -------------------- LOAD MODE --------------------
# Choose: "reset" to clear tables each run, or "upsert" to keep and update existing data
MODE = "reset"   # change to "upsert" for incremental loads

print("Starting fact data load...")

# -------------------- RESET (optional) --------------------
if MODE == "reset":
    with engine.begin() as conn:
        conn.execute(text("""
            TRUNCATE TABLE fact_order_items, fact_orders, fact_marketing_spend
            RESTART IDENTITY CASCADE;
        """))
    print("Tables truncated — fresh reload.")

# -------------------- 1. fact_orders --------------------
try:
    df_orders = pd.read_csv("data/orders.csv")[["order_id", "customer_id", "order_ts", "gross", "discount"]]

    if MODE == "upsert":
        # Upsert logic
        with engine.begin() as conn:
            df_orders.to_sql("_tmp_orders", conn, if_exists="replace", index=False)
            conn.execute(text("""
                INSERT INTO fact_orders (order_id, customer_id, order_ts, gross, discount)
                SELECT order_id, customer_id, order_ts, gross, discount FROM _tmp_orders
                ON CONFLICT (order_id)
                DO UPDATE SET
                    customer_id = EXCLUDED.customer_id,
                    order_ts   = EXCLUDED.order_ts,
                    gross      = EXCLUDED.gross,
                    discount   = EXCLUDED.discount;
                DROP TABLE _tmp_orders;
            """))
        print(f"Upserted {len(df_orders)} rows into fact_orders")
    else:
        df_orders.to_sql("fact_orders", engine, if_exists="append", index=False, method="multi", chunksize=2000)
        print(f"Loaded {len(df_orders)} rows into fact_orders")
except Exception as e:
    print("Error loading orders.csv:", e)

# -------------------- 2. fact_order_items --------------------
try:
    df_items = pd.read_csv("data/order_items.csv")[["order_id", "product_id", "qty", "price"]]
    df_items.to_sql("fact_order_items", engine, if_exists="append", index=False, method="multi", chunksize=2000)
    print(f"Loaded {len(df_items)} rows into fact_order_items")
except Exception as e:
    print("Error loading order_items.csv:", e)

# -------------------- 3. fact_marketing_spend --------------------
try:
    df_spend = pd.read_csv("data/marketing_spend.csv")
    with engine.connect() as conn:
        dim_channels = pd.read_sql("SELECT channel_id, channel_name FROM dim_channel", conn)
    df_spend = df_spend.merge(dim_channels, on="channel_name", how="left")
    df_spend = df_spend[["day", "channel_id", "spend"]]
    df_spend.to_sql("fact_marketing_spend", engine, if_exists="append", index=False, method="multi", chunksize=2000)
    print(f"Loaded {len(df_spend)} rows into fact_marketing_spend")
except Exception as e:
    print("Error loading marketing_spend.csv:", e)

print("Fact data load complete.")
