-- Cohort label = first order month
CREATE OR REPLACE VIEW v_customer_firsts AS
SELECT customer_id,
       MIN(DATE_TRUNC('month', order_ts))::date AS cohort_month,
       MIN(DATE(order_ts)) AS first_day
FROM fact_orders
GROUP BY 1;

-- Revenue by customer by month
CREATE OR REPLACE VIEW v_cust_monthly_rev AS
SELECT customer_id,
       DATE_TRUNC('month', order_ts)::date AS month,
       SUM(net) AS revenue
FROM fact_orders
GROUP BY 1,2;

-- LTV by cohort (cumulative)
CREATE OR REPLACE VIEW v_ltv_cohort AS
WITH base AS (
  SELECT f.customer_id, cf.cohort_month, cm.month, cm.revenue,
         (EXTRACT(YEAR FROM age(cm.month, cf.cohort_month)) * 12 +
          EXTRACT(MONTH FROM age(cm.month, cf.cohort_month)))::int AS m_offset
  FROM v_customer_firsts cf
  JOIN v_cust_monthly_rev cm USING(customer_id)
  JOIN fact_orders f ON f.customer_id = cf.customer_id
  GROUP BY f.customer_id, cf.cohort_month, cm.month, cm.revenue
)
SELECT cohort_month,
       m_offset,
       SUM(revenue) AS cohort_revenue,
       SUM(SUM(revenue)) OVER (PARTITION BY cohort_month ORDER BY m_offset) AS cohort_ltv
FROM base
GROUP BY 1,2
ORDER BY 1,2;

-- Retention (active customers per m_offset)
CREATE OR REPLACE VIEW v_retention_matrix AS
WITH active AS (
  SELECT DISTINCT cf.cohort_month, cf.customer_id,
         (EXTRACT(YEAR FROM age(DATE_TRUNC('month', o.order_ts), cf.cohort_month)) * 12 +
          EXTRACT(MONTH FROM age(DATE_TRUNC('month', o.order_ts), cf.cohort_month)))::int AS m_offset
  FROM v_customer_firsts cf
  JOIN fact_orders o ON o.customer_id = cf.customer_id
)
SELECT cohort_month,
       m_offset,
       COUNT(DISTINCT customer_id) AS active_customers
FROM active
GROUP BY 1,2
ORDER BY 1,2;
