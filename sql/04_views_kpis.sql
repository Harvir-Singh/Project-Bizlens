-- Orders, customers, revenue, AOV by day
CREATE OR REPLACE VIEW v_kpi_daily AS
SELECT
  DATE(order_ts) AS day,
  COUNT(DISTINCT order_id) AS orders,
  COUNT(DISTINCT customer_id) AS customers,
  SUM(net) AS revenue,
  AVG(net) AS aov
FROM fact_orders
GROUP BY 1;

-- CAC = spend / new_customers (first order on day)
CREATE OR REPLACE VIEW v_cac_daily AS
WITH first_orders AS (
  SELECT customer_id, MIN(DATE(order_ts)) AS first_day
  FROM fact_orders
  GROUP BY 1
)
SELECT m.day,
       SUM(m.spend) AS spend,
       COUNT(f.customer_id) AS new_customers,
       CASE WHEN COUNT(f.customer_id) = 0 THEN NULL
            ELSE SUM(m.spend)::numeric / COUNT(f.customer_id) END AS cac
FROM fact_marketing_spend m
LEFT JOIN first_orders f ON f.first_day = m.day
GROUP BY 1;

-- Combine KPI + CAC
CREATE OR REPLACE VIEW v_kpi_cac_daily AS
SELECT k.day, k.orders, k.customers, k.revenue, k.aov,
       c.spend, c.new_customers, c.cac
FROM v_kpi_daily k
LEFT JOIN v_cac_daily c USING(day);
