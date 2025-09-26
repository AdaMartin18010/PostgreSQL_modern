-- 初始化：扩展、节点检查、示例表与分片
CREATE EXTENSION IF NOT EXISTS citus;

-- 示例表
CREATE TABLE customers (
  customer_id BIGINT PRIMARY KEY,
  customer_name TEXT NOT NULL
);

CREATE TABLE orders (
  order_id BIGINT PRIMARY KEY,
  customer_id BIGINT NOT NULL REFERENCES customers(customer_id),
  order_date TIMESTAMPTZ NOT NULL DEFAULT now(),
  amount NUMERIC(12,2) NOT NULL
);

-- 分布与辅助表
SELECT create_distributed_table('orders', 'customer_id');
-- 将 customers 设为引用表，便于跨分片 JOIN
SELECT create_reference_table('customers');

-- 演示数据
INSERT INTO customers(customer_id, customer_name)
SELECT g, 'customer_'||g FROM generate_series(1, 1000) g;

INSERT INTO orders(order_id, customer_id, order_date, amount)
SELECT g, (random()*999+1)::bigint, now() - (random()*10||' days')::interval, (random()*1000)::numeric(12,2)
FROM generate_series(1, 100000) g;

-- 示例查询（单分片路由 vs 跨分片 JOIN）
EXPLAIN (ANALYZE, VERBOSE)
SELECT count(*) FROM orders WHERE customer_id = 42;

EXPLAIN (ANALYZE, VERBOSE)
SELECT c.customer_name, sum(o.amount)
FROM orders o JOIN customers c USING (customer_id)
GROUP BY c.customer_name
ORDER BY sum(o.amount) DESC
LIMIT 10;

