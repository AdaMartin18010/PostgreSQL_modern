-- 发布端（publisher）
CREATE PUBLICATION pub_demo FOR TABLE demo.events;

-- 订阅端（subscriber）
-- 注意在订阅端执行：
-- CREATE SUBSCRIPTION sub_demo CONNECTION 'host=PUB_HOST dbname=DB user=USER password=PASS' PUBLICATION pub_demo;

-- 订阅状态
SELECT * FROM pg_stat_subscription;
