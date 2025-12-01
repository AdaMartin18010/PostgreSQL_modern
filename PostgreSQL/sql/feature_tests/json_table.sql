-- PostgreSQL 17.x SQL/JSON: JSON_TABLE 功能测试
-- 版本：PostgreSQL 17+
-- 用途：测试JSON_TABLE函数和SQL/JSON标准功能
-- 执行环境：PostgreSQL 17+ 或兼容版本

-- =====================
-- 1. 环境准备
-- =====================

-- 1.1 检查PostgreSQL版本和JSON支持
SELECT version();
SELECT extname, extversion FROM pg_extension WHERE extname = 'jsonb';

-- 1.2 创建测试数据
CREATE SCHEMA IF NOT EXISTS ft_json;
SET search_path TO ft_json, public;

-- 创建测试表
DROP TABLE IF EXISTS json_test_data CASCADE;
CREATE TABLE json_test_data (
    id bigserial PRIMARY KEY,
    document_name text NOT NULL,
    json_data jsonb NOT NULL,
    created_at timestamptz DEFAULT now()
);

-- 插入复杂的JSON测试数据
INSERT INTO json_test_data (document_name, json_data) VALUES
-- 订单数据
('order_001', '{
    "order_id": "ORD-001",
    "customer": {
        "id": 12345,
        "name": "John Doe",
        "email": "john.doe@example.com",
        "address": {
            "street": "123 Main St",
            "city": "New York",
            "state": "NY",
            "zip": "10001"
        }
    },
    "items": [
        {"sku": "LAPTOP-001", "name": "Gaming Laptop", "qty": 1, "price": 1299.99, "category": "Electronics"},
        {"sku": "MOUSE-001", "name": "Wireless Mouse", "qty": 2, "price": 29.99, "category": "Electronics"}
    ],
    "total": 1359.97,
    "status": "completed",
    "order_date": "2023-12-01T10:30:00Z"
}'),

-- 产品目录数据
('product_catalog', '{
    "catalog_id": "CAT-2023",
    "categories": [
        {
            "id": "electronics",
            "name": "Electronics",
            "products": [
                {"id": "LAPTOP-001", "name": "Gaming Laptop", "price": 1299.99, "in_stock": true},
                {"id": "PHONE-001", "name": "Smartphone", "price": 699.99, "in_stock": false}
            ]
        },
        {
            "id": "books",
            "name": "Books",
            "products": [
                {"id": "BOOK-001", "name": "PostgreSQL Guide", "price": 49.99, "in_stock": true},
                {"id": "BOOK-002", "name": "SQL Reference", "price": 39.99, "in_stock": true}
            ]
        }
    ]
}'),

-- 用户活动数据
('user_activity', '{
    "user_id": 12345,
    "session_id": "sess_abc123",
    "activities": [
        {
            "type": "page_view",
            "page": "/products/laptop",
            "timestamp": "2023-12-01T10:15:00Z",
            "duration": 45
        },
        {
            "type": "click",
            "element": "add_to_cart",
            "timestamp": "2023-12-01T10:16:00Z",
            "product_id": "LAPTOP-001"
        },
        {
            "type": "purchase",
            "order_id": "ORD-001",
            "timestamp": "2023-12-01T10:30:00Z",
            "amount": 1359.97
        }
    ]
}');

-- =====================
-- 2. 基础JSON_TABLE测试
-- =====================

-- 2.1 测试JSON_TABLE支持（如果可用）
DO $$
BEGIN
    -- 尝试使用JSON_TABLE
    BEGIN
        EXECUTE 'SELECT * FROM JSON_TABLE(''{"items":[{"sku":"A","qty":2}]}'', ''$.items[*]'' 
                 COLUMNS (sku text PATH ''$.sku'', qty int PATH ''$.qty''))';
        RAISE NOTICE 'JSON_TABLE is supported in this version';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE NOTICE 'JSON_TABLE not supported: %', SQLERRM;
    END;
END $$;

-- 2.2 兼容性回退方案 - 使用jsonb_array_elements
-- 提取订单项目
SELECT 
    id,
    document_name,
    (item->>'sku') AS sku,
    (item->>'name') AS name,
    (item->>'qty')::int AS quantity,
    (item->>'price')::numeric AS price,
    (item->>'category') AS category
FROM json_test_data,
     jsonb_array_elements(json_data->'items') AS item
WHERE document_name = 'order_001'
ORDER BY (item->>'qty')::int DESC;

-- =====================
-- 3. 复杂JSON数据提取
-- =====================

-- 3.1 提取客户信息
SELECT 
    id,
    document_name,
    json_data->'customer'->>'name' AS customer_name,
    json_data->'customer'->>'email' AS customer_email,
    json_data->'customer'->'address'->>'city' AS city,
    json_data->'customer'->'address'->>'state' AS state,
    json_data->>'total' AS order_total
FROM json_test_data
WHERE document_name = 'order_001';

-- 3.2 提取产品目录信息
SELECT 
    id,
    document_name,
    category->>'id' AS category_id,
    category->>'name' AS category_name,
    product->>'id' AS product_id,
    product->>'name' AS product_name,
    (product->>'price')::numeric AS price,
    (product->>'in_stock')::boolean AS in_stock
FROM json_test_data,
     jsonb_array_elements(json_data->'categories') AS category,
     jsonb_array_elements(category->'products') AS product
WHERE document_name = 'product_catalog'
ORDER BY category_id, product_name;

-- 3.3 提取用户活动信息
SELECT 
    id,
    document_name,
    json_data->>'user_id' AS user_id,
    json_data->>'session_id' AS session_id,
    activity->>'type' AS activity_type,
    activity->>'timestamp' AS activity_timestamp,
    activity->>'duration' AS duration,
    activity->>'page' AS page,
    activity->>'element' AS element,
    activity->>'product_id' AS product_id,
    activity->>'order_id' AS order_id,
    (activity->>'amount')::numeric AS amount
FROM json_test_data,
     jsonb_array_elements(json_data->'activities') AS activity
WHERE document_name = 'user_activity'
ORDER BY activity->>'timestamp';

-- =====================
-- 4. JSON路径查询测试
-- =====================

-- 4.1 使用jsonb_path_query
SELECT 
    id,
    document_name,
    jsonb_path_query(json_data, '$.items[*].sku') AS sku_values,
    jsonb_path_query(json_data, '$.items[*].price') AS price_values
FROM json_test_data
WHERE document_name = 'order_001';

-- 4.2 使用jsonb_path_query_array
SELECT 
    id,
    document_name,
    jsonb_path_query_array(json_data, '$.items[*].sku') AS all_skus,
    jsonb_path_query_array(json_data, '$.items[*].price') AS all_prices
FROM json_test_data
WHERE document_name = 'order_001';

-- 4.3 条件路径查询
SELECT 
    id,
    document_name,
    jsonb_path_query_array(json_data, '$.items[*] ? (@.price > 100).sku') AS expensive_items
FROM json_test_data
WHERE document_name = 'order_001';

-- =====================
-- 5. JSON聚合和统计
-- =====================

-- 5.1 统计订单信息
SELECT 
    document_name,
    json_data->>'order_id' AS order_id,
    json_data->'customer'->>'name' AS customer_name,
    count(*) AS item_count,
    sum((item->>'qty')::int) AS total_quantity,
    sum((item->>'price')::numeric * (item->>'qty')::int) AS calculated_total,
    (json_data->>'total')::numeric AS stored_total
FROM json_test_data,
     jsonb_array_elements(json_data->'items') AS item
WHERE document_name = 'order_001'
GROUP BY document_name, json_data->>'order_id', json_data->'customer'->>'name', json_data->>'total';

-- 5.2 按类别统计产品
SELECT 
    category->>'id' AS category_id,
    category->>'name' AS category_name,
    count(*) AS product_count,
    avg((product->>'price')::numeric) AS avg_price,
    min((product->>'price')::numeric) AS min_price,
    max((product->>'price')::numeric) AS max_price,
    count(*) FILTER (WHERE (product->>'in_stock')::boolean) AS in_stock_count
FROM json_test_data,
     jsonb_array_elements(json_data->'categories') AS category,
     jsonb_array_elements(category->'products') AS product
WHERE document_name = 'product_catalog'
GROUP BY category->>'id', category->>'name'
ORDER BY avg_price DESC;

-- =====================
-- 6. JSON数据验证和错误处理
-- =====================

-- 6.1 验证JSON结构
SELECT 
    id,
    document_name,
    CASE 
        WHEN json_data ? 'order_id' THEN 'Order Document'
        WHEN json_data ? 'catalog_id' THEN 'Catalog Document'
        WHEN json_data ? 'user_id' THEN 'User Activity Document'
        ELSE 'Unknown Document Type'
    END AS document_type,
    jsonb_typeof(json_data) AS root_type
FROM json_test_data;

-- 6.2 检查必需字段
SELECT 
    id,
    document_name,
    CASE 
        WHEN json_data ? 'items' AND jsonb_typeof(json_data->'items') = 'array' THEN 'Valid Items Array'
        WHEN json_data ? 'categories' AND jsonb_typeof(json_data->'categories') = 'array' THEN 'Valid Categories Array'
        WHEN json_data ? 'activities' AND jsonb_typeof(json_data->'activities') = 'array' THEN 'Valid Activities Array'
        ELSE 'Missing or Invalid Array Field'
    END AS validation_status
FROM json_test_data;

-- =====================
-- 7. 性能测试和优化
-- =====================

-- 7.1 创建JSON索引
CREATE INDEX idx_json_test_data_gin ON json_test_data USING gin (json_data);
CREATE INDEX idx_json_test_data_btree ON json_test_data ((json_data->>'order_id'));

-- 7.2 测试索引使用
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT * FROM json_test_data 
WHERE json_data @> '{"order_id": "ORD-001"}';

EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT * FROM json_test_data 
WHERE json_data->>'order_id' = 'ORD-001';

-- =====================
-- 8. 高级JSON操作
-- =====================

-- 8.1 JSON数据转换
SELECT 
    id,
    document_name,
    json_data,
    jsonb_pretty(json_data) AS formatted_json
FROM json_test_data
WHERE document_name = 'order_001';

-- 8.2 JSON数据修改
UPDATE json_test_data 
SET json_data = jsonb_set(json_data, '{status}', '"shipped"')
WHERE document_name = 'order_001';

-- 8.3 JSON数据合并
SELECT 
    jsonb_merge_agg(json_data) AS merged_data
FROM json_test_data
WHERE document_name IN ('order_001', 'product_catalog');

-- =====================
-- 9. 实际应用场景
-- =====================

-- 9.1 订单分析报表
SELECT 
    'Order Analysis' AS report_type,
    json_data->>'order_id' AS order_id,
    json_data->'customer'->>'name' AS customer_name,
    json_data->'customer'->'address'->>'city' AS customer_city,
    count(*) AS item_count,
    sum((item->>'qty')::int) AS total_quantity,
    (json_data->>'total')::numeric AS order_total,
    json_data->>'status' AS order_status
FROM json_test_data,
     jsonb_array_elements(json_data->'items') AS item
WHERE json_data ? 'order_id'
GROUP BY json_data->>'order_id', json_data->'customer'->>'name', 
         json_data->'customer'->'address'->>'city', json_data->>'total', json_data->>'status';

-- 9.2 产品库存报告
SELECT 
    'Inventory Report' AS report_type,
    category->>'name' AS category_name,
    product->>'name' AS product_name,
    (product->>'price')::numeric AS price,
    CASE 
        WHEN (product->>'in_stock')::boolean THEN 'In Stock'
        ELSE 'Out of Stock'
    END AS stock_status
FROM json_test_data,
     jsonb_array_elements(json_data->'categories') AS category,
     jsonb_array_elements(category->'products') AS product
WHERE json_data ? 'catalog_id'
ORDER BY category->>'name', product->>'name';

-- 9.3 用户行为分析
SELECT 
    'User Behavior Analysis' AS report_type,
    json_data->>'user_id' AS user_id,
    activity->>'type' AS activity_type,
    count(*) AS activity_count,
    min(activity->>'timestamp') AS first_activity,
    max(activity->>'timestamp') AS last_activity
FROM json_test_data,
     jsonb_array_elements(json_data->'activities') AS activity
WHERE json_data ? 'user_id'
GROUP BY json_data->>'user_id', activity->>'type'
ORDER BY user_id, activity_type;

-- =====================
-- 10. 清理和总结
-- =====================

-- 10.1 显示测试结果摘要
SELECT 
    'JSON_TABLE Test Summary' AS test_name,
    count(*) AS total_documents,
    count(DISTINCT document_name) AS unique_documents,
    avg(pg_column_size(json_data)) AS avg_json_size_bytes
FROM json_test_data;

-- 10.2 清理测试数据
-- DROP SCHEMA IF EXISTS ft_json CASCADE;


