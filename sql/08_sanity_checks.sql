-- 1) Items sum equals order gross
WITH x AS (
  SELECT oi.order_id,
         SUM(oi.line_amount) AS item_sum,
         o.gross
  FROM fact_order_items oi
  JOIN fact_orders o USING(order_id)
  GROUP BY 1,3
)
SELECT * FROM x WHERE item_sum <> gross;

-- 2) Orphans
SELECT * FROM fact_orders WHERE customer_id NOT IN (SELECT customer_id FROM dim_customer);
SELECT * FROM fact_order_items WHERE product_id NOT IN (SELECT product_id FROM dim_product);

-- 3) Negative values
SELECT * FROM fact_orders WHERE gross < 0 OR discount < 0;
SELECT * FROM fact_marketing_spend WHERE spend < 0;
