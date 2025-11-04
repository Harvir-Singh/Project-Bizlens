# scripts/build_cohorts_ltv.py
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

print("🚀 Building cohort retention and LTV analytics...")

with engine.begin() as conn:

    # --- 1️⃣ Cohort assignments (each customer's first order month)
    conn.execute(text("""
        CREATE OR REPLACE VIEW v_customer_cohort AS
        SELECT
            customer_id,
            MIN(DATE_TRUNC('month', order_ts)) AS cohort_month
        FROM fact_orders
        GROUP BY customer_id;
    """))
    print("✅ v_customer_cohort view created.")

    # --- 2️⃣ Monthly activity table (customer orders per month)
    conn.execute(text("""
        CREATE OR REPLACE VIEW v_customer_activity AS
        SELECT
            o.customer_id,
            DATE_TRUNC('month', o.order_ts) AS activity_month,
            COUNT(DISTINCT o.order_id) AS orders,
            SUM(o.net) AS revenue
        FROM fact_orders o
        GROUP BY o.customer_id, DATE_TRUNC('month', o.order_ts);
    """))
    print("✅ v_customer_activity view created.")

    # --- 3️⃣ Retention matrix: how many customers stayed active
    conn.execute(text("""
        CREATE OR REPLACE VIEW v_retention_matrix AS
        SELECT
            c.cohort_month,
            EXTRACT(MONTH FROM AGE(a.activity_month, c.cohort_month))::INT AS m_offset,
            COUNT(DISTINCT a.customer_id) AS active_customers
        FROM v_customer_cohort c
        JOIN v_customer_activity a
            ON c.customer_id = a.customer_id
        WHERE a.activity_month >= c.cohort_month
        GROUP BY c.cohort_month, m_offset
        ORDER BY c.cohort_month, m_offset;
    """))
    print("✅ v_retention_matrix view created.")

    # --- 4️⃣ LTV per cohort
    conn.execute(text("""
        CREATE OR REPLACE VIEW v_ltv_cohort AS
        SELECT
            c.cohort_month,
            ROUND(SUM(a.revenue), 2) AS total_revenue,
            COUNT(DISTINCT c.customer_id) AS total_customers,
            ROUND(SUM(a.revenue) / NULLIF(COUNT(DISTINCT c.customer_id), 0), 2) AS avg_ltv
        FROM v_customer_cohort c
        JOIN v_customer_activity a
            ON c.customer_id = a.customer_id
        GROUP BY c.cohort_month
        ORDER BY c.cohort_month;
    """))
    print("✅ v_ltv_cohort view created.")

    # --- 5️⃣ Materialized view for Power BI
    conn.execute(text("""
        CREATE MATERIALIZED VIEW IF NOT EXISTS mv_cohort_summary AS
        SELECT
            c.cohort_month,
            r.m_offset,
            r.active_customers,
            l.total_revenue,
            l.total_customers,
            l.avg_ltv
        FROM v_retention_matrix r
        JOIN v_ltv_cohort l USING (cohort_month)
        JOIN v_customer_cohort c USING (cohort_month)
        ORDER BY cohort_month, m_offset;
    """))
    conn.execute(text("REFRESH MATERIALIZED VIEW mv_cohort_summary;"))
    print("✅ mv_cohort_summary refreshed.")

print("🎯 Cohort and LTV build complete.")
