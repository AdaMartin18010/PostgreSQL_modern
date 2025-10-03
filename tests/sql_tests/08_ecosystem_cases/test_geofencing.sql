-- TEST: PostGIS地理围栏测试
-- DESCRIPTION: 测试PostGIS空间查询和地理围栏功能
-- EXPECTED: 所有空间查询和围栏判断正确
-- TAGS: postgis, geofencing, spatial-index
-- NOTE: 需要安装PostGIS扩展

-- SETUP
-- 检查并创建PostGIS扩展
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'postgis') THEN
        CREATE EXTENSION postgis;
    END IF;
END $$;

-- 创建围栏表
CREATE TABLE test_geofences (
    id serial PRIMARY KEY,
    name text NOT NULL,
    geometry geometry(Polygon, 4326) NOT NULL
);

-- 创建位置表
CREATE TABLE test_locations (
    id serial PRIMARY KEY,
    name text NOT NULL,
    location geometry(Point, 4326) NOT NULL
);

-- 创建空间索引
CREATE INDEX idx_test_geofences_geometry ON test_geofences USING gist(geometry);
CREATE INDEX idx_test_locations_location ON test_locations USING gist(location);

-- TEST_BODY
-- 测试1：创建围栏（正方形区域）
INSERT INTO test_geofences (name, geometry) VALUES
    ('Zone A', ST_GeomFromText('POLYGON((0 0, 10 0, 10 10, 0 10, 0 0))', 4326)),
    ('Zone B', ST_GeomFromText('POLYGON((20 20, 30 20, 30 30, 20 30, 20 20))', 4326));

SELECT COUNT(*) FROM test_geofences;  -- EXPECT_VALUE: 2

-- 测试2：验证几何对象有效性
SELECT COUNT(*) FROM test_geofences 
WHERE ST_IsValid(geometry);  -- EXPECT_VALUE: 2

-- 测试3：创建位置点
INSERT INTO test_locations (name, location) VALUES
    ('Point 1', ST_SetSRID(ST_MakePoint(5, 5), 4326)),      -- 在Zone A内
    ('Point 2', ST_SetSRID(ST_MakePoint(25, 25), 4326)),    -- 在Zone B内
    ('Point 3', ST_SetSRID(ST_MakePoint(15, 15), 4326)),    -- 不在任何围栏内
    ('Point 4', ST_SetSRID(ST_MakePoint(2, 2), 4326));      -- 在Zone A内

SELECT COUNT(*) FROM test_locations;  -- EXPECT_VALUE: 4

-- 测试4：点在多边形内判断（ST_Contains）
SELECT COUNT(*) 
FROM test_locations l
JOIN test_geofences g ON ST_Contains(g.geometry, l.location)
WHERE g.name = 'Zone A';  -- EXPECT_VALUE: 2

-- 测试5：查找不在任何围栏内的点
SELECT COUNT(*)
FROM test_locations l
WHERE NOT EXISTS (
    SELECT 1 FROM test_geofences g
    WHERE ST_Contains(g.geometry, l.location)
);  -- EXPECT_VALUE: 1

-- 测试6：距离计算
SELECT 
    ST_Distance(
        ST_SetSRID(ST_MakePoint(0, 0), 4326)::geography,
        ST_SetSRID(ST_MakePoint(10, 0), 4326)::geography
    ) AS distance_meters;  -- 应该返回约1113195米（地球表面距离）

-- 测试7：附近搜索（半径查询）
SELECT COUNT(*)
FROM test_locations
WHERE ST_DWithin(
    location::geography,
    ST_SetSRID(ST_MakePoint(5, 5), 4326)::geography,
    500000  -- 500km半径
);  -- EXPECT_VALUE: 3

-- 测试8：面积计算
SELECT 
    name,
    ST_Area(geometry::geography) / 1000000 AS area_sqkm
FROM test_geofences
WHERE name = 'Zone A';  -- EXPECT_ROWS: 1

-- 测试9：围栏相交检测
SELECT COUNT(*)
FROM test_geofences g1
JOIN test_geofences g2 ON g1.id < g2.id
WHERE ST_Intersects(g1.geometry, g2.geometry);  -- EXPECT_VALUE: 0 (不相交)

-- 测试10：空间索引使用验证
EXPLAIN (COSTS OFF)
SELECT l.name
FROM test_locations l
JOIN test_geofences g ON ST_Contains(g.geometry, l.location);
-- 应该看到 "Index Scan using idx_test_geofences_geometry"

-- 测试11：最近点查询
SELECT 
    l.name,
    ST_Distance(
        l.location::geography,
        ST_SetSRID(ST_MakePoint(0, 0), 4326)::geography
    ) AS distance
FROM test_locations l
ORDER BY l.location::geography <-> ST_SetSRID(ST_MakePoint(0, 0), 4326)::geography
LIMIT 1;  -- EXPECT_ROWS: 1

-- TEARDOWN
-- 清理测试数据
DROP TABLE IF EXISTS test_locations;
DROP TABLE IF EXISTS test_geofences;

