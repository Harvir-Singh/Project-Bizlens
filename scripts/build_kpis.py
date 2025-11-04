# scripts/build_kpis.py
import os
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

print("🚀 Building KPI views and materialized summaries...")

with engine.begin() as conn:

    # --- v_kpi_daily: core daily metrics -------------------
    conn.execute(text("""
        CREATE OR REPLACE VIEW v_kpi_daily AS
        SELECT
            DATE(o.order_ts) AS day,
            COUNT(DISTINCT o.order_id)        AS orders,
            COUNT(DISTINCT o.customer_id)     AS customers,
            SUM(o.net)                        AS revenue,
            SUM(o.gross)                      AS gross,
            SUM(o.discount)                   AS discounts,
            AVG(o.net)                        AS aov
        FROM fact_orders o
        GROUP BY 1
        ORDER BY 1;
    """))
    print("✅ v_kpi_daily view created.")

    # --- CAC: join with marketing spend --------------------
    conn.execute(text("""
        CREATE OR REPLACE VIEW v_cac_daily AS
        SELECT
            k.day,
            k.revenue,
            k.orders,
            k.customers,
            COALESCE(SUM(m.spend),0) AS spend,
            CASE
                WHEN COUNT(DISTINCT k.customers) > 0 THEN
                    COALESCE(SUM(m.spend),0) / COUNT(DISTINCT k.customers)
                ELSE 0
            END AS cac
        FROM v_kpi_daily k
        LEFT JOIN fact_marketing_spend m ON k.day = m.day
        GROUP BY k.day, k.revenue, k.orders, k.customers
        ORDER BY k.day;
    """))
    print("✅ v_cac_daily view created.")

    # --- LTV by cohort month (optional derived table) ------
    conn.execute(text("""
        CREATE OR REPLACE VIEW v_ltv_monthly AS
        SELECT
            DATE_TRUNC('month', o.order_ts) AS cohort_month,
            o.customer_id,
            SUM(o.net) AS total_spend
        FROM fact_orders o
        GROUP BY 1, o.customer_id;
    """))
    print("✅ v_ltv_monthly view created.")

    # --- Materialized summary for Power BI -----------------
    conn.execute(text("""
        CREATE MATERIALIZED VIEW IF NOT EXISTS mv_daily_summary AS
        SELECT
            k.day,
            k.orders,
            k.customers,
            k.revenue,
            k.gross,
            k.discounts,
            k.aov,
            c.spend,
            c.cac
        FROM v_kpi_daily k
        LEFT JOIN v_cac_daily c ON k.day = c.day
        ORDER BY k.day;
    """))
    conn.execute(text("REFRESH MATERIALIZED VIEW mv_daily_summary;"))
    print("✅ mv_daily_summary refreshed.")

print("🎯 KPI build complete.")
