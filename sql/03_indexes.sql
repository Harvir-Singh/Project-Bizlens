CREATE INDEX IF NOT EXISTS idx_orders_ts ON fact_orders(order_ts);
CREATE INDEX IF NOT EXISTS idx_orders_customer_ts ON fact_orders(customer_id, order_ts);
CREATE INDEX IF NOT EXISTS idx_items_product ON fact_order_items(product_id);
CREATE INDEX IF NOT EXISTS idx_spend_day_channel ON fact_marketing_spend(day, channel_id);
