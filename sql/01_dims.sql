-- dim_date (date backbone)
CREATE TABLE IF NOT EXISTS dim_date (
  date_id date PRIMARY KEY,
  year int NOT NULL,
  quarter int NOT NULL CHECK (quarter between 1 and 4),
  month int NOT NULL CHECK (month between 1 and 12),
  day int NOT NULL CHECK (day between 1 and 31),
  week int NOT NULL CHECK (week between 1 and 53),
  is_weekend boolean NOT NULL
);

-- dim_customer
CREATE TABLE IF NOT EXISTS dim_customer (
  customer_id bigint PRIMARY KEY,
  email_hash text,
  country text,
  signup_date date
);

-- dim_product
CREATE TABLE IF NOT EXISTS dim_product (
  product_id bigint PRIMARY KEY,
  product_name text,
  category text,
  base_price numeric(12,2)
);

-- dim_channel
CREATE TABLE IF NOT EXISTS dim_channel (
  channel_id bigserial PRIMARY KEY,
  channel_name text UNIQUE NOT NULL
);

--Populate dim_date (10‑year horizon)
WITH RECURSIVE d AS (
  SELECT date '2020-01-01' AS d
  UNION ALL
  SELECT d + 1 FROM d WHERE d < date '2030-12-31'
)
INSERT INTO dim_date(date_id, year, quarter, month, day, week, is_weekend)
SELECT d,
       EXTRACT(YEAR FROM d)::int,
       EXTRACT(QUARTER FROM d)::int,
       EXTRACT(MONTH FROM d)::int,
       EXTRACT(DAY FROM d)::int,
       EXTRACT(WEEK FROM d)::int,
       EXTRACT(ISODOW FROM d) IN (6,7)
FROM d
ON CONFLICT (date_id) DO NOTHING;
