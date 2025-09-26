\set hot_ratio 0.5
\set hot_key_min 1
\set hot_key_max 10
\set cold_key_min 11
\set cold_key_max 1000

\setcustom customer_id random(1,1000)
\set ckey :customer_id

-- 热键命中：按照 hot_ratio 的概率选择热区键
\if :random(1,100) <= :int(:hot_ratio*100)
  \set ckey random(:hot_key_min, :hot_key_max)
\else
  \set ckey random(:cold_key_min, :cold_key_max)
\endif

-- 单键路由写
INSERT INTO orders(order_id, customer_id, order_date, amount)
VALUES (CAST(1000000000 + :random(1,100000000) AS BIGINT), :ckey, now(), CAST(:random(1,10000) AS NUMERIC));

-- 单键查询
SELECT count(*) FROM orders WHERE customer_id = :ckey;

