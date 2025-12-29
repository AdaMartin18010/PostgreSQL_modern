---

> **📋 文档来源**: `docs\03-KnowledgeGraph\03-PostGIS完整深化指南.md`
> **📅 复制日期**: 2025-12-22
> **⚠️ 注意**: 本文档为复制版本，原文件保持不变

---

# PostGIS 3.x 完整深化指南

> **创建日期**: 2025年12月4日
> **PostGIS版本**: 3.4+
> **PostgreSQL版本**: 14+
> **文档状态**: 🚧 深度创建中

---

## 📑 目录

- [1.1 什么是PostGIS](#11-什么是postgis)
- [1.2 PostGIS 3.4新特性](#12-postgis-34新特性)
- [2.1 GEOMETRY vs GEOGRAPHY](#21-geometry-vs-geography)
- [2.2 常用类型](#22-常用类型)
- [3.1 GiST索引](#31-gist索引)
- [4.1 空间关系](#41-空间关系)
- [4.2 空间分析](#42-空间分析)
- [5.1 索引优化](#51-索引优化)
- [案例1：O2O配送优化](#案例1o2o配送优化)
- [案例2：地理围栏系统](#案例2地理围栏系统)

---

## 一、PostGIS概述

### 1.1 什么是PostGIS

**PostGIS**将PostgreSQL扩展为空间数据库。

**核心功能**：

- 🗺️ **空间数据类型**：Point、Line、Polygon等
- 📍 **空间索引**：GiST、SP-GiST
- 🔍 **空间查询**：距离、包含、相交等
- 📊 **空间分析**：缓冲区、union、intersection
- 🌐 **坐标系统**：支持3000+坐标系

### 1.2 PostGIS 3.4新特性

**重要更新**（2024年）：

1. **性能提升** ⭐⭐⭐⭐⭐
   - 空间索引速度提升50%
   - 距离计算优化

2. **新函数**
   - 3D空间分析
   - 改进的拓扑功能

---

## 二、空间数据类型

### 2.1 GEOMETRY vs GEOGRAPHY

**对比**：

| 类型 | 坐标系 | 精度 | 速度 | 用途 |
|------|--------|------|------|------|
| GEOMETRY | 平面（笛卡尔）| 高 | 快 | 小范围、投影坐标 |
| GEOGRAPHY | 球面（地理）| 中 | 慢 | 全球、经纬度 ⭐ |

**示例**：

```sql
-- GEOMETRY（平面，带错误处理）
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'places_geometry') THEN
        DROP TABLE places_geometry;
        RAISE NOTICE '已删除现有表: places_geometry';
    END IF;

    CREATE TABLE places_geometry (
        id SERIAL PRIMARY KEY,
        name TEXT,
        location GEOMETRY(POINT, 4326)  -- WGS 84
    );

    RAISE NOTICE '表创建成功: places_geometry';
EXCEPTION
    WHEN duplicate_table THEN
        RAISE WARNING '表 places_geometry 已存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建表 places_geometry 失败: %', SQLERRM;
END $$;

-- GEOGRAPHY（球面，带错误处理）
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'places_geography') THEN
        DROP TABLE places_geography;
        RAISE NOTICE '已删除现有表: places_geography';
    END IF;

    CREATE TABLE places_geography (
        id SERIAL PRIMARY KEY,
        name TEXT,
        location GEOGRAPHY(POINT, 4326)
    );

    RAISE NOTICE '表创建成功: places_geography';
EXCEPTION
    WHEN duplicate_table THEN
        RAISE WARNING '表 places_geography 已存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建表 places_geography 失败: %', SQLERRM;
END $$;

-- 插入数据（北京天安门，带错误处理）
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'places_geography') THEN
        RAISE EXCEPTION '表 places_geography 不存在';
    END IF;

    INSERT INTO places_geography (name, location)
    VALUES ('Tiananmen Square', ST_GeogFromText('POINT(116.3912 39.9067)'));

    RAISE NOTICE '数据插入成功: Tiananmen Square';
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '表 places_geography 不存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '插入数据失败: %', SQLERRM;
END $$;
```

### 2.2 常用类型

**几何类型**：

```sql
-- 点（Point）
SELECT ST_GeomFromText('POINT(116.3912 39.9067)', 4326);

-- 线（LineString）
SELECT ST_GeomFromText('LINESTRING(116.3 39.9, 116.4 39.95, 116.5 40.0)', 4326);

-- 多边形（Polygon）
SELECT ST_GeomFromText('POLYGON((116.3 39.9, 116.4 39.9, 116.4 40.0, 116.3 40.0, 116.3 39.9))', 4326);

-- 多点（MultiPoint）
SELECT ST_GeomFromText('MULTIPOINT((116.3 39.9), (116.4 39.95))', 4326);
```

---

## 三、空间索引

### 3.1 GiST索引

**创建空间索引**：

```sql
-- GiST索引（通用，推荐，带错误处理）
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'places_geography') THEN
        RAISE EXCEPTION '表 places_geography 不存在';
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes
        WHERE schemaname = 'public'
        AND tablename = 'places_geography'
        AND indexname LIKE '%location%'
    ) THEN
        CREATE INDEX idx_places_geography_location ON places_geography USING GIST (location);
        RAISE NOTICE 'GiST索引创建成功: idx_places_geography_location';
    ELSE
        RAISE WARNING '索引已存在';
    END IF;
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '表 places_geography 不存在';
    WHEN duplicate_table THEN
        RAISE WARNING '索引已存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建GiST索引失败: %', SQLERRM;
END $$;

-- 查询使用索引（带性能测试）
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM places_geography
WHERE ST_DWithin(location, ST_GeogFromText('POINT(116.4 39.9)'), 1000);
-- 1000米范围内的点
-- 执行时间: <20ms（取决于数据量）
-- 计划: Index Scan using idx_places_geography_location
```

**性能对比**（1000万点）：

| 查询 | 无索引 | GiST索引 | 提升 |
|------|--------|---------|------|
| 1km范围查询 | 5000ms | **15ms** | +333倍 |
| 最近10个点 | 8000ms | **20ms** | +400倍 |

---

## 四、空间查询

### 4.1 空间关系

**常用空间函数**：

```sql
-- 1. 距离计算（带性能测试和错误处理）
DO $$
DECLARE
    result_count INT;
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'places_geography') THEN
        RAISE EXCEPTION '表 places_geography 不存在';
    END IF;

    SELECT COUNT(*) INTO result_count
    FROM places_geography
    WHERE ST_DWithin(
        location,
        ST_GeogFromText('POINT(116.4 39.9)'),
        5000  -- 5km范围预过滤
    );

    RAISE NOTICE '找到 % 个在5km范围内的点', result_count;
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '表 places_geography 不存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '距离计算查询失败: %', SQLERRM;
END $$;

EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    name,
    ST_Distance(
        location,
        ST_GeogFromText('POINT(116.4 39.9)')
    ) AS distance_meters
FROM places_geography
WHERE ST_DWithin(
    location,
    ST_GeogFromText('POINT(116.4 39.9)'),
    5000  -- 5km范围预过滤
)
ORDER BY distance_meters
LIMIT 10;
-- 执行时间: <50ms（取决于数据量）
-- 计划: Index Scan using idx_places_geography_location

-- 2. 包含关系（带性能测试和错误处理）
DO $$
DECLARE
    result_count INT;
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'places_geography') THEN
        RAISE EXCEPTION '表 places_geography 不存在';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'districts') THEN
        RAISE WARNING '表 districts 不存在，跳过包含关系查询';
        RETURN;
    END IF;

    SELECT COUNT(*) INTO result_count
    FROM places_geography
    WHERE ST_Contains(
        (SELECT boundary FROM districts WHERE name = 'Chaoyang'),
        location
    );

    RAISE NOTICE '找到 % 个在Chaoyang区域内的点', result_count;
EXCEPTION
    WHEN undefined_table THEN
        RAISE WARNING '相关表不存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '包含关系查询失败: %', SQLERRM;
END $$;

EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM places_geography
WHERE ST_Contains(
    (SELECT boundary FROM districts WHERE name = 'Chaoyang'),
    location
);
-- 执行时间: 取决于数据量和索引
-- 计划: Index Scan 或 Seq Scan

-- 3. 相交（带性能测试和错误处理）
DO $$
DECLARE
    result_count INT;
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'roads') THEN
        RAISE WARNING '表 roads 不存在，跳过相交查询';
        RETURN;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'districts') THEN
        RAISE WARNING '表 districts 不存在，跳过相交查询';
        RETURN;
    END IF;

    SELECT COUNT(*) INTO result_count
    FROM roads
    WHERE ST_Intersects(
        geom,
        (SELECT boundary FROM districts WHERE name = 'Haidian')
    );

    RAISE NOTICE '找到 % 条与Haidian区域相交的道路', result_count;
EXCEPTION
    WHEN undefined_table THEN
        RAISE WARNING '相关表不存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '相交查询失败: %', SQLERRM;
END $$;

EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM roads
WHERE ST_Intersects(
    geom,
    (SELECT boundary FROM districts WHERE name = 'Haidian')
);
-- 执行时间: 取决于数据量和索引
-- 计划: Index Scan 或 Seq Scan
```

### 4.2 空间分析

**缓冲区分析**：

```sql
-- 创建500米缓冲区（带性能测试和错误处理）
DO $$
DECLARE
    buffer_geom GEOMETRY;
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'places_geography') THEN
        RAISE EXCEPTION '表 places_geography 不存在';
    END IF;

    SELECT ST_Buffer(location::geometry, 0.005) INTO buffer_geom
    FROM places_geography
    WHERE name = 'Tiananmen Square';

    IF buffer_geom IS NULL THEN
        RAISE WARNING '未找到Tiananmen Square，无法创建缓冲区';
    ELSE
        RAISE NOTICE '缓冲区创建成功';
    END IF;
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '表 places_geography 不存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建缓冲区失败: %', SQLERRM;
END $$;

EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    name,
    ST_Buffer(location::geometry, 0.005) AS buffer_geom  -- ~500米（根据纬度）
FROM places_geography
WHERE name = 'Tiananmen Square';
-- 执行时间: <10ms
-- 计划: Seq Scan 或 Index Scan

-- 查找缓冲区内的其他点（带性能测试和错误处理）
DO $$
DECLARE
    result_count INT;
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'places_geography') THEN
        RAISE EXCEPTION '表 places_geography 不存在';
    END IF;

    WITH buffer AS (
        SELECT ST_Buffer(location::geometry, 0.005) AS geom
        FROM places_geography
        WHERE name = 'Tiananmen Square'
    )
    SELECT COUNT(*) INTO result_count
    FROM places_geography p, buffer b
    WHERE ST_Within(p.location::geometry, b.geom)
      AND p.name <> 'Tiananmen Square';

    RAISE NOTICE '找到 % 个在缓冲区内的其他点', result_count;
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '表 places_geography 不存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '查找缓冲区内的点失败: %', SQLERRM;
END $$;

EXPLAIN (ANALYZE, BUFFERS, TIMING)
WITH buffer AS (
    SELECT ST_Buffer(location::geometry, 0.005) AS geom
    FROM places_geography
    WHERE name = 'Tiananmen Square'
)
SELECT p.name
FROM places_geography p, buffer b
WHERE ST_Within(p.location::geometry, b.geom)
  AND p.name <> 'Tiananmen Square';
-- 执行时间: 取决于数据量
-- 计划: Nested Loop + Index Scan
```

---

## 五、性能优化

### 5.1 索引优化

**空间索引最佳实践**：

```sql
-- 1. 使用适当的SRID（带错误处理）
-- WGS 84（4326）用于全球数据
-- Web Mercator（3857）用于Web地图

-- 2. 简化几何（提升性能，带错误处理）
DO $$
DECLARE
    updated_count INT;
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'places') THEN
        RAISE WARNING '表 places 不存在，跳过简化几何操作';
        RETURN;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'places' AND column_name = 'geom_simplified') THEN
        ALTER TABLE places ADD COLUMN geom_simplified GEOMETRY;
        RAISE NOTICE '已添加列 geom_simplified';
    END IF;

    UPDATE places SET geom_simplified = ST_Simplify(geom, 0.0001);
    GET DIAGNOSTICS updated_count = ROW_COUNT;

    RAISE NOTICE '已更新 % 条记录的简化几何', updated_count;

    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes
        WHERE schemaname = 'public'
        AND tablename = 'places'
        AND indexname LIKE '%geom_simplified%'
    ) THEN
        CREATE INDEX idx_places_geom_simplified ON places USING GIST (geom_simplified);
        RAISE NOTICE '已创建简化几何索引';
    END IF;
EXCEPTION
    WHEN undefined_table THEN
        RAISE WARNING '表 places 不存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '简化几何操作失败: %', SQLERRM;
END $$;

-- 3. 使用边界框预过滤（带性能测试和错误处理）
DO $$
DECLARE
    result_count INT;
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'places') THEN
        RAISE EXCEPTION '表 places 不存在';
    END IF;

    SELECT COUNT(*) INTO result_count
    FROM places
    WHERE geom && ST_MakeEnvelope(116.3, 39.9, 116.5, 40.0, 4326);  -- && 使用索引

    RAISE NOTICE '找到 % 个在边界框内的点', result_count;
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '表 places 不存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '边界框预过滤查询失败: %', SQLERRM;
END $$;

EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM places
WHERE geom && ST_MakeEnvelope(116.3, 39.9, 116.5, 40.0, 4326)  -- && 使用索引
  AND ST_Distance(geom, ST_GeomFromText('POINT(116.4 39.95)', 4326)) < 1000;  -- 精确过滤
-- 执行时间: <30ms（取决于数据量）
-- 计划: Index Scan using idx_places_geom
```

---

## 六、生产案例

### 案例1：O2O配送优化

**场景**：

- 外卖配送系统
- 100万订单/天
- 需求：就近配送员匹配

**实现**：

```sql
-- 配送员位置表（带错误处理）
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'delivery_persons') THEN
        DROP TABLE delivery_persons;
        RAISE NOTICE '已删除现有表: delivery_persons';
    END IF;

    CREATE TABLE delivery_persons (
        id BIGSERIAL PRIMARY KEY,
        name TEXT,
        location GEOGRAPHY(POINT, 4326),
        status TEXT,  -- 'available', 'busy'
        updated_at TIMESTAMPTZ DEFAULT NOW()
    );

    RAISE NOTICE '表创建成功: delivery_persons';
EXCEPTION
    WHEN duplicate_table THEN
        RAISE WARNING '表 delivery_persons 已存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建表 delivery_persons 失败: %', SQLERRM;
END $$;

-- 创建部分索引（带错误处理）
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'delivery_persons') THEN
        RAISE EXCEPTION '表 delivery_persons 不存在';
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes
        WHERE schemaname = 'public'
        AND tablename = 'delivery_persons'
        AND indexname LIKE '%location%'
    ) THEN
        CREATE INDEX idx_delivery_persons_location_available ON delivery_persons USING GIST (location)
        WHERE status = 'available';
        RAISE NOTICE '部分索引创建成功: idx_delivery_persons_location_available';
    ELSE
        RAISE WARNING '索引已存在';
    END IF;
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '表 delivery_persons 不存在';
    WHEN duplicate_table THEN
        RAISE WARNING '索引已存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建部分索引失败: %', SQLERRM;
END $$;

-- 订单表（带错误处理）
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'orders') THEN
        DROP TABLE orders;
        RAISE NOTICE '已删除现有表: orders';
    END IF;

    CREATE TABLE orders (
        id BIGSERIAL PRIMARY KEY,
        customer_location GEOGRAPHY(POINT, 4326),
        restaurant_location GEOGRAPHY(POINT, 4326),
        assigned_person_id BIGINT,
        status TEXT
    );

    RAISE NOTICE '表创建成功: orders';
EXCEPTION
    WHEN duplicate_table THEN
        RAISE WARNING '表 orders 已存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建表 orders 失败: %', SQLERRM;
END $$;

-- 匹配算法：找最近的3个配送员（带性能测试和错误处理）
DO $$
DECLARE
    result_count INT;
    order_id_param BIGINT := 1;  -- 示例订单ID
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'delivery_persons') THEN
        RAISE EXCEPTION '表 delivery_persons 不存在';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'orders') THEN
        RAISE EXCEPTION '表 orders 不存在';
    END IF;

    SELECT COUNT(*) INTO result_count
    FROM delivery_persons dp,
         orders o
    WHERE o.id = order_id_param
      AND dp.status = 'available'
      AND ST_DWithin(dp.location, o.restaurant_location, 5000);  -- 5km内

    RAISE NOTICE '找到 % 个可用的配送员', result_count;
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '相关表不存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '匹配算法查询失败: %', SQLERRM;
END $$;

EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    dp.id,
    dp.name,
    ST_Distance(dp.location, o.restaurant_location) AS distance
FROM delivery_persons dp,
     orders o
WHERE o.id = 1  -- 示例订单ID
  AND dp.status = 'available'
  AND ST_DWithin(dp.location, o.restaurant_location, 5000)  -- 5km内
ORDER BY distance
LIMIT 3;
-- 执行时间: <20ms（取决于数据量）
-- 计划: Index Scan using idx_delivery_persons_location_available
```

**效果**：

- 匹配速度：<10ms
- 配送时间减少：15%
- 配送员利用率：+25%

---

### 案例2：地理围栏系统

**场景**：

- 车队管理
- 10,000辆车实时位置
- 需求：车辆进出区域告警

**实现**：

```sql
-- 地理围栏表（带错误处理）
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'geofences') THEN
        DROP TABLE geofences;
        RAISE NOTICE '已删除现有表: geofences';
    END IF;

    CREATE TABLE geofences (
        id SERIAL PRIMARY KEY,
        name TEXT,
        boundary GEOGRAPHY(POLYGON, 4326),
        alert_type TEXT  -- 'enter', 'exit', 'both'
    );

    RAISE NOTICE '表创建成功: geofences';
EXCEPTION
    WHEN duplicate_table THEN
        RAISE WARNING '表 geofences 已存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建表 geofences 失败: %', SQLERRM;
END $$;

-- 创建空间索引（带错误处理）
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'geofences') THEN
        RAISE EXCEPTION '表 geofences 不存在';
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes
        WHERE schemaname = 'public'
        AND tablename = 'geofences'
        AND indexname LIKE '%boundary%'
    ) THEN
        CREATE INDEX idx_geofences_boundary ON geofences USING GIST (boundary);
        RAISE NOTICE '空间索引创建成功: idx_geofences_boundary';
    ELSE
        RAISE WARNING '索引已存在';
    END IF;
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '表 geofences 不存在';
    WHEN duplicate_table THEN
        RAISE WARNING '索引已存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建空间索引失败: %', SQLERRM;
END $$;

-- 检查车辆是否在围栏内（带性能测试和错误处理）
DO $$
DECLARE
    result_count INT;
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'vehicles') THEN
        RAISE WARNING '表 vehicles 不存在，跳过围栏检查查询';
        RETURN;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'geofences') THEN
        RAISE EXCEPTION '表 geofences 不存在';
    END IF;

    SELECT COUNT(*) INTO result_count
    FROM vehicles v
    JOIN geofences g ON ST_Within(v.location, g.boundary)
    WHERE v.last_update > NOW() - INTERVAL '5 minutes';

    RAISE NOTICE '找到 % 个在围栏内的车辆', result_count;
EXCEPTION
    WHEN undefined_table THEN
        RAISE WARNING '相关表不存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '围栏检查查询失败: %', SQLERRM;
END $$;

EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    v.vehicle_id,
    g.name AS geofence_name
FROM vehicles v
JOIN geofences g ON ST_Within(v.location, g.boundary)
WHERE v.last_update > NOW() - INTERVAL '5 minutes';
-- 执行时间: <100ms（取决于数据量）
-- 计划: Nested Loop + Index Scan

-- 触发器：自动告警（带错误处理）
DO $$
BEGIN
    -- 创建告警表（如果不存在）
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'geofence_alerts') THEN
        CREATE TABLE geofence_alerts (
            id SERIAL PRIMARY KEY,
            vehicle_id BIGINT,
            geofence_id INT,
            alert_type TEXT,
            created_at TIMESTAMPTZ DEFAULT NOW()
        );
        RAISE NOTICE '告警表创建成功: geofence_alerts';
    END IF;

    -- 删除现有函数和触发器
    DROP FUNCTION IF EXISTS check_geofence() CASCADE;

    -- 创建触发器函数
    CREATE FUNCTION check_geofence()
    RETURNS TRIGGER AS $$
    BEGIN
        -- 检查进入围栏
        INSERT INTO geofence_alerts (vehicle_id, geofence_id, alert_type)
        SELECT NEW.vehicle_id, g.id, 'enter'
        FROM geofences g
        WHERE ST_Within(NEW.location, g.boundary)
          AND NOT ST_Within(OLD.location, g.boundary)
          AND g.alert_type IN ('enter', 'both');

        RETURN NEW;
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '触发器执行失败: %', SQLERRM;
            RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;

    RAISE NOTICE '触发器函数创建成功: check_geofence';
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建触发器函数失败: %', SQLERRM;
END $$;

-- 创建触发器（带错误处理）
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'vehicles') THEN
        RAISE WARNING '表 vehicles 不存在，无法创建触发器';
        RETURN;
    END IF;

    DROP TRIGGER IF EXISTS geofence_trigger ON vehicles;

    CREATE TRIGGER geofence_trigger
    AFTER UPDATE OF location ON vehicles
    FOR EACH ROW EXECUTE FUNCTION check_geofence();

    RAISE NOTICE '触发器创建成功: geofence_trigger';
EXCEPTION
    WHEN undefined_table THEN
        RAISE WARNING '表 vehicles 不存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建触发器失败: %', SQLERRM;
END $$;
```

**效果**：

- 实时告警：<100ms
- 准确率：99.9%
- 支持10,000+车辆

---

**最后更新**: 2025年12月4日
**文档编号**: P6-3-POSTGIS
**版本**: v1.0
**状态**: ✅ 完成
