-- fact_orders
CREATE TABLE IF NOT EXISTS fact_orders (
  order_id bigint PRIMARY KEY,
  customer_id bigint NOT NULL REFERENCES dim_customer(customer_id),
  order_ts timestamp NOT NULL,
  gross numeric(12,2) NOT NULL CHECK (gross >= 0),
  discount numeric(12,2) NOT NULL DEFAULT 0 CHECK (discount >= 0),
  net numeric(12,2) GENERATED ALWAYS AS (gross - discount) STORED
);

-- fact_order_items
CREATE TABLE IF NOT EXISTS fact_order_items (
  order_id bigint NOT NULL REFERENCES fact_orders(order_id) ON DELETE CASCADE,
  product_id bigint NOT NULL REFERENCES dim_product(product_id),
  qty int NOT NULL CHECK (qty > 0),
  price numeric(12,2) NOT NULL CHECK (price >= 0),
  line_amount numeric(12,2) GENERATED ALWAYS AS (qty * price) STORED,
  PRIMARY KEY(order_id, product_id)
);

-- fact_marketing_spend
CREATE TABLE IF NOT EXISTS fact_marketing_spend (
  day date NOT NULL REFERENCES dim_date(date_id),
  channel_id bigint NOT NULL REFERENCES dim_channel(channel_id),
  spend numeric(12,2) NOT NULL CHECK (spend >= 0),
  PRIMARY KEY(day, channel_id)
);
