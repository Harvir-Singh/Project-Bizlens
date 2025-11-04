-- Materialized daily aggregation for fast BI
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_daily_summary AS
SELECT k.day, k.orders, k.customers, k.revenue, k.aov,
       c.spend, c.new_customers, c.cac
FROM v_kpi_daily k
LEFT JOIN v_cac_daily c USING(day);

CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_daily_summary_day ON mv_daily_summary(day);

-- Refresh helper
CREATE OR REPLACE FUNCTION refresh_mv_daily_summary() RETURNS void AS $$
BEGIN
  REFRESH MATERIALIZED VIEW CONCURRENTLY mv_daily_summary;
END; $$ LANGUAGE plpgsql;
