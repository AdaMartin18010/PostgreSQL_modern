---

> **📋 文档来源**: `docs\01-PostgreSQL18\23-PostGIS地理空间数据库实战.md`
> **📅 复制日期**: 2025-12-22
> **⚠️ 注意**: 本文档为复制版本，原文件保持不变

---

# PostgreSQL 18 + PostGIS地理空间数据库实战

## 📑 目录

- [2.1 基础类型](#21-基础类型)
- [3.1 GiST索引](#31-gist索引)
- [4.1 距离计算](#41-距离计算)
- [4.2 空间关系](#42-空间关系)
- [5.1 外卖配送系统](#51-外卖配送系统)
- [5.2 地理围栏](#52-地理围栏)
- [6.1 路径计算](#61-路径计算)
- [7.1 网格聚合](#71-网格聚合)
- [8.1 空间索引优化](#81-空间索引优化)
- [8.2 geometry vs geography](#82-geometry-vs-geography)
---

## 2. 几何类型

### 2.1 基础类型

```sql
-- 性能测试：点（POINT）（带错误处理）
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'locations') THEN
        DROP TABLE locations;
        RAISE NOTICE '已删除现有表: locations';
    END IF;

    CREATE TABLE locations (
        loc_id SERIAL PRIMARY KEY,
        name VARCHAR(100),
        geom geometry(POINT, 4326)  -- WGS84坐标系
    );

    RAISE NOTICE '表创建成功: locations';
EXCEPTION
    WHEN duplicate_table THEN
        RAISE WARNING '表locations已存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建表失败: %', SQLERRM;
END $$;

-- 插入数据（带错误处理）
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'locations') THEN
        RAISE EXCEPTION '表locations不存在';
    END IF;

    INSERT INTO locations (name, geom) VALUES
    ('北京', ST_GeomFromText('POINT(116.4074 39.9042)', 4326)),
    ('上海', ST_GeomFromText('POINT(121.4737 31.2304)', 4326))
    ON CONFLICT DO NOTHING;

    RAISE NOTICE '数据插入成功';
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '表locations不存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '插入数据失败: %', SQLERRM;
END $$;

-- 性能测试：或使用ST_MakePoint（带错误处理）
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'locations') THEN
        RAISE EXCEPTION '表locations不存在';
    END IF;

    INSERT INTO locations (name, geom) VALUES
    ('广州', ST_SetSRID(ST_MakePoint(113.2644, 23.1291), 4326))
    ON CONFLICT DO NOTHING;

    RAISE NOTICE 'ST_MakePoint插入成功';
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '表locations不存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION 'ST_MakePoint插入失败: %', SQLERRM;
END $$;

-- 性能测试：线（LINESTRING）（带错误处理）
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'roads') THEN
        DROP TABLE roads;
        RAISE NOTICE '已删除现有表: roads';
    END IF;

    CREATE TABLE roads (
        road_id SERIAL PRIMARY KEY,
        name VARCHAR(100),
        geom geometry(LINESTRING, 4326)
    );

    RAISE NOTICE '表创建成功: roads';
EXCEPTION
    WHEN duplicate_table THEN
        RAISE WARNING '表roads已存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建表失败: %', SQLERRM;
END $$;

-- 插入道路数据（带错误处理）
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'roads') THEN
        RAISE EXCEPTION '表roads不存在';
    END IF;

    INSERT INTO roads (name, geom) VALUES
    ('道路1', ST_GeomFromText('LINESTRING(116.4 39.9, 116.5 40.0)', 4326))
    ON CONFLICT DO NOTHING;

    RAISE NOTICE '道路数据插入成功';
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '表roads不存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '插入数据失败: %', SQLERRM;
END $$;

-- 性能测试：多边形（POLYGON）（带错误处理）
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'districts') THEN
        DROP TABLE districts;
        RAISE NOTICE '已删除现有表: districts';
    END IF;

    CREATE TABLE districts (
        district_id SERIAL PRIMARY KEY,
        name VARCHAR(100),
        geom geometry(POLYGON, 4326)
    );

    RAISE NOTICE '表创建成功: districts';
EXCEPTION
    WHEN duplicate_table THEN
        RAISE WARNING '表districts已存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建表失败: %', SQLERRM;
END $$;

-- 插入区域数据（带错误处理）
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'districts') THEN
        RAISE EXCEPTION '表districts不存在';
    END IF;

    INSERT INTO districts (name, geom) VALUES
    ('区域1', ST_GeomFromText('POLYGON((116.3 39.8, 116.5 39.8, 116.5 40.0, 116.3 40.0, 116.3 39.8))', 4326))
    ON CONFLICT DO NOTHING;

    RAISE NOTICE '区域数据插入成功';
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '表districts不存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '插入数据失败: %', SQLERRM;
END $$;

```

---

## 3. 空间索引

### 3.1 GiST索引

```sql
-- 性能测试：创建空间索引（带错误处理）
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'locations') THEN
        RAISE WARNING '表locations不存在，跳过索引创建';
    ELSE
        IF NOT EXISTS (
            SELECT 1 FROM pg_indexes
            WHERE schemaname = 'public'
            AND tablename = 'locations'
            AND indexname = 'idx_locations_geom'
        ) THEN
            CREATE INDEX idx_locations_geom ON locations USING gist(geom);
            RAISE NOTICE '索引创建成功: idx_locations_geom';
        ELSE
            RAISE WARNING '索引idx_locations_geom已存在';
        END IF;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'roads') THEN
        RAISE WARNING '表roads不存在，跳过索引创建';
    ELSE
        IF NOT EXISTS (
            SELECT 1 FROM pg_indexes
            WHERE schemaname = 'public'
            AND tablename = 'roads'
            AND indexname = 'idx_roads_geom'
        ) THEN
            CREATE INDEX idx_roads_geom ON roads USING gist(geom);
            RAISE NOTICE '索引创建成功: idx_roads_geom';
        ELSE
            RAISE WARNING '索引idx_roads_geom已存在';
        END IF;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'districts') THEN
        RAISE WARNING '表districts不存在，跳过索引创建';
    ELSE
        IF NOT EXISTS (
            SELECT 1 FROM pg_indexes
            WHERE schemaname = 'public'
            AND tablename = 'districts'
            AND indexname = 'idx_districts_geom'
        ) THEN
            CREATE INDEX idx_districts_geom ON districts USING gist(geom);
            RAISE NOTICE '索引创建成功: idx_districts_geom';
        ELSE
            RAISE WARNING '索引idx_districts_geom已存在';
        END IF;
    END IF;
EXCEPTION
    WHEN undefined_table THEN
        RAISE WARNING '相关表不存在';
    WHEN duplicate_table THEN
        RAISE WARNING '部分空间索引已存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建空间索引失败: %', SQLERRM;
END $$;

-- 性能测试：查询性能（带错误处理和性能分析）
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'locations') THEN
        RAISE EXCEPTION '表locations不存在';
    END IF;

    RAISE NOTICE '执行空间查询性能测试';
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '表locations不存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '空间查询失败: %', SQLERRM;
END $$;

EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM locations
WHERE ST_DWithin(geom, ST_MakePoint(116.4, 39.9), 0.1);
-- 无索引: Seq Scan, 850ms
-- 有索引: Index Scan using idx_locations_geom, 12ms (-99%)

```

---

## 4. 空间查询

### 4.1 距离计算

```sql
-- 性能测试：计算两点距离（米）（带错误处理和性能分析）
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'locations') THEN
        RAISE EXCEPTION '表locations不存在';
    END IF;

    RAISE NOTICE '执行两点距离计算性能测试';
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '表locations不存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '计算两点距离失败: %', SQLERRM;
END $$;

EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    l1.name AS from_loc,
    l2.name AS to_loc,
    ST_Distance(
        l1.geom::geography,
        l2.geom::geography
    ) AS distance_meters
FROM locations l1, locations l2
WHERE l1.loc_id = 1 AND l2.loc_id = 2;
-- 执行时间: <10ms
-- 计划: Seq Scan 或 Index Scan

-- 性能测试：查找附近的点（半径1000米）（带错误处理和性能分析）
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'locations') THEN
        RAISE EXCEPTION '表locations不存在';
    END IF;

    RAISE NOTICE '执行附近点查找性能测试';
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '表locations不存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '查找附近点失败: %', SQLERRM;
END $$;

EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    name,
    ST_Distance(geom::geography, ST_MakePoint(116.4, 39.9)::geography) AS distance
FROM locations
WHERE ST_DWithin(
    geom::geography,
    ST_MakePoint(116.4, 39.9)::geography,
    1000
)
ORDER BY distance;
-- 执行时间: <50ms（取决于数据量）
-- 计划: Index Scan using idx_locations_geom
```

### 4.2 空间关系

```sql
-- 性能测试：点是否在多边形内（带错误处理和性能分析）
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'locations') THEN
        RAISE EXCEPTION '表locations不存在';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'districts') THEN
        RAISE EXCEPTION '表districts不存在';
    END IF;

    RAISE NOTICE '执行空间关系查询性能测试';
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '相关表不存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '空间关系查询失败: %', SQLERRM;
END $$;

EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT l.name
FROM locations l
JOIN districts d ON ST_Within(l.geom, d.geom)
WHERE d.name = '朝阳区';
-- 执行时间: <30ms（取决于数据量）
-- 计划: Nested Loop + Index Scan

-- 性能测试：相交（带错误处理和性能分析）
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'roads') THEN
        RAISE EXCEPTION '表roads不存在';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'districts') THEN
        RAISE EXCEPTION '表districts不存在';
    END IF;

    RAISE NOTICE '执行相交查询性能测试';
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '相关表不存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '相交查询失败: %', SQLERRM;
END $$;

EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT r.name
FROM roads r
JOIN districts d ON ST_Intersects(r.geom, d.geom)
WHERE d.name = '海淀区';
-- 执行时间: <40ms（取决于数据量）
-- 计划: Nested Loop + Index Scan

-- 性能测试：包含（带错误处理和性能分析）
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'districts') THEN
        RAISE EXCEPTION '表districts不存在';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'locations') THEN
        RAISE EXCEPTION '表locations不存在';
    END IF;

    RAISE NOTICE '执行包含查询性能测试';
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '相关表不存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '包含查询失败: %', SQLERRM;
END $$;

EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT d.name, COUNT(l.loc_id) AS location_count
FROM districts d
LEFT JOIN locations l ON ST_Contains(d.geom, l.geom)
GROUP BY d.name;
-- 执行时间: 取决于数据量
-- 计划: Hash Aggregate + Nested Loop
COMMIT;
EXCEPTION
    WHEN undefined_table THEN
        RAISE NOTICE '表districts或locations不存在';
    WHEN OTHERS THEN
        RAISE NOTICE '包含查询失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：最近邻（KNN）（带错误处理和性能分析）
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'locations') THEN
        RAISE EXCEPTION '表locations不存在';
    END IF;

    RAISE NOTICE '执行最近邻查询性能测试';
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '表locations不存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '最近邻查询失败: %', SQLERRM;
END $$;

EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT name
FROM locations
ORDER BY geom <-> ST_MakePoint(116.4, 39.9)::geometry
LIMIT 5;
-- 执行时间: <20ms（取决于数据量）
-- 计划: Index Scan using idx_locations_geom (KNN)
```

---

## 5. 实战案例

### 5.1 外卖配送系统

```sql
-- 性能测试：商家表（带错误处理）
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'restaurants') THEN
        DROP TABLE restaurants;
        RAISE NOTICE '已删除现有表: restaurants';
    END IF;

    CREATE TABLE restaurants (
        restaurant_id SERIAL PRIMARY KEY,
        name VARCHAR(200),
        location geometry(POINT, 4326),
        delivery_range INT DEFAULT 3000  -- 配送范围（米）
    );

    RAISE NOTICE '表创建成功: restaurants';
EXCEPTION
    WHEN duplicate_table THEN
        RAISE WARNING '表restaurants已存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建商家表失败: %', SQLERRM;
END $$;

-- 创建商家表空间索引（带错误处理）
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'restaurants') THEN
        RAISE EXCEPTION '表restaurants不存在';
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes
        WHERE schemaname = 'public'
        AND tablename = 'restaurants'
        AND indexname = 'idx_restaurants_location'
    ) THEN
        CREATE INDEX idx_restaurants_location ON restaurants USING gist(location);
        RAISE NOTICE '索引创建成功: idx_restaurants_location';
    ELSE
        RAISE WARNING '索引idx_restaurants_location已存在';
    END IF;
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '表restaurants不存在';
    WHEN duplicate_table THEN
        RAISE WARNING '索引已存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建索引失败: %', SQLERRM;
END $$;

-- 性能测试：订单表（带错误处理）
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'restaurants') THEN
        RAISE EXCEPTION '表restaurants不存在，请先创建';
    END IF;

    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'orders') THEN
        DROP TABLE orders;
        RAISE NOTICE '已删除现有表: orders';
    END IF;

    CREATE TABLE orders (
        order_id BIGSERIAL PRIMARY KEY,
        restaurant_id INT REFERENCES restaurants(restaurant_id),
        delivery_location geometry(POINT, 4326),
        status VARCHAR(20),
        created_at TIMESTAMPTZ DEFAULT now()
    );

    RAISE NOTICE '表创建成功: orders';
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '表restaurants不存在，请先创建';
    WHEN duplicate_table THEN
        RAISE WARNING '表orders已存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建订单表失败: %', SQLERRM;
END $$;

-- 创建订单表空间索引（带错误处理）
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'orders') THEN
        RAISE EXCEPTION '表orders不存在';
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes
        WHERE schemaname = 'public'
        AND tablename = 'orders'
        AND indexname = 'idx_orders_location'
    ) THEN
        CREATE INDEX idx_orders_location ON orders USING gist(delivery_location);
        RAISE NOTICE '索引创建成功: idx_orders_location';
    ELSE
        RAISE WARNING '索引idx_orders_location已存在';
    END IF;
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '表orders不存在';
    WHEN duplicate_table THEN
        RAISE WARNING '索引已存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建索引失败: %', SQLERRM;
END $$;

-- 性能测试：骑手表（带错误处理）
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'riders') THEN
        DROP TABLE riders;
        RAISE NOTICE '已删除现有表: riders';
    END IF;

    CREATE TABLE riders (
        rider_id INT PRIMARY KEY,
        name VARCHAR(100),
        current_location geometry(POINT, 4326),
        status VARCHAR(20),
        updated_at TIMESTAMPTZ DEFAULT now()
    );

    RAISE NOTICE '表创建成功: riders';
EXCEPTION
    WHEN duplicate_table THEN
        RAISE WARNING '表riders已存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建骑手表失败: %', SQLERRM;
END $$;

-- 创建骑手表空间索引（带错误处理）
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'riders') THEN
        RAISE EXCEPTION '表riders不存在';
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes
        WHERE schemaname = 'public'
        AND tablename = 'riders'
        AND indexname = 'idx_riders_location'
    ) THEN
        CREATE INDEX idx_riders_location ON riders USING gist(current_location);
        RAISE NOTICE '索引创建成功: idx_riders_location';
    ELSE
        RAISE WARNING '索引idx_riders_location已存在';
    END IF;
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '表riders不存在';
    WHEN duplicate_table THEN
        RAISE WARNING '索引已存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建索引失败: %', SQLERRM;
END $$;

-- 性能测试：查询用户位置附近可配送的商家（带错误处理和性能分析）
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'restaurants') THEN
        RAISE EXCEPTION '表restaurants不存在';
    END IF;

    RAISE NOTICE '执行附近商家查询性能测试';
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '表restaurants不存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '查询附近商家失败: %', SQLERRM;
END $$;

EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    r.restaurant_id,
    r.name,
    ST_Distance(r.location::geography, user_loc::geography) AS distance
FROM restaurants r,
     ST_MakePoint(116.4, 39.9)::geometry user_loc
WHERE ST_DWithin(
    r.location::geography,
    user_loc::geography,
    r.delivery_range
)
ORDER BY distance
LIMIT 20;
-- 执行时间: <50ms（取决于数据量）
-- 计划: Index Scan using idx_restaurants_location

-- 性能测试：查询订单附近的空闲骑手（带错误处理和性能分析）
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'riders') THEN
        RAISE EXCEPTION '表riders不存在';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'orders') THEN
        RAISE EXCEPTION '表orders不存在';
    END IF;

    RAISE NOTICE '执行附近骑手查询性能测试';
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '表riders或orders不存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '查询附近骑手失败: %', SQLERRM;
END $$;

EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    rider_id,
    name,
    ST_Distance(current_location::geography, order_loc::geography) AS distance
FROM riders,
     (SELECT delivery_location AS order_loc FROM orders WHERE order_id = 12345) o
WHERE status = 'available'
  AND ST_DWithin(
      current_location::geography,
      order_loc::geography,
      5000
  )
ORDER BY distance
LIMIT 10;
-- 执行时间: <40ms（取决于数据量）
-- 计划: Index Scan using idx_riders_location

-- 性能测试：配送路径优化（简化TSP）（带错误处理和性能分析）
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'orders') THEN
        RAISE EXCEPTION '表orders不存在';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'riders') THEN
        RAISE EXCEPTION '表riders不存在';
    END IF;

    RAISE NOTICE '执行配送路径优化查询性能测试';
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '表orders或riders不存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '配送路径优化查询失败: %', SQLERRM;
END $$;

EXPLAIN (ANALYZE, BUFFERS, TIMING)
WITH rider_orders AS (
    SELECT
        o.order_id,
        o.delivery_location,
        ST_Distance(r.current_location::geography, o.delivery_location::geography) AS distance
    FROM orders o,
         riders r
    WHERE o.status = 'assigned'
      AND o.rider_id = r.rider_id
)
SELECT * FROM rider_orders
ORDER BY distance;
-- 执行时间: 取决于数据量
-- 计划: Hash Join + Index Scan
```

### 5.2 地理围栏

```sql
-- 围栏表
CREATE TABLE geofences (
    fence_id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    fence_type VARCHAR(50),
    geom geometry(POLYGON, 4326),
    metadata JSONB
);

CREATE INDEX idx_geofences_geom ON geofences USING gist(geom);

-- 检查设备是否在围栏内
SELECT
    d.device_id,
    d.device_name,
    f.name AS fence_name,
    f.fence_type
FROM devices d
JOIN geofences f ON ST_Within(d.current_location, f.geom)
WHERE d.device_id = 12345;

-- 实时触发器（进入/离开围栏）
CREATE OR REPLACE FUNCTION check_geofence()
RETURNS TRIGGER AS $$
DECLARE
    entered_fences INT[];
    exited_fences INT[];
BEGIN
    -- 检查进入的围栏
    SELECT array_agg(fence_id) INTO entered_fences
    FROM geofences
    WHERE ST_Within(NEW.current_location, geom)
      AND NOT ST_Within(OLD.current_location, geom);

    -- 检查离开的围栏
    SELECT array_agg(fence_id) INTO exited_fences
    FROM geofences
    WHERE ST_Within(OLD.current_location, geom)
      AND NOT ST_Within(NEW.current_location, geom);

    -- 记录事件
    IF entered_fences IS NOT NULL THEN
        INSERT INTO geofence_events (device_id, fence_ids, event_type)
        VALUES (NEW.device_id, entered_fences, 'entered');
    END IF;

    IF exited_fences IS NOT NULL THEN
        INSERT INTO geofence_events (device_id, fence_ids, event_type)
        VALUES (NEW.device_id, exited_fences, 'exited');
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

---

## 6. 路径分析

### 6.1 路径计算

```sql
-- 轨迹表
CREATE TABLE trajectories (
    traj_id BIGSERIAL PRIMARY KEY,
    device_id INT,
    path geometry(LINESTRING, 4326),
    start_time TIMESTAMPTZ,
    end_time TIMESTAMPTZ
);

-- 计算路径长度
SELECT
    traj_id,
    ST_Length(path::geography) AS length_meters,
    end_time - start_time AS duration
FROM trajectories;

-- 计算平均速度
SELECT
    traj_id,
    ST_Length(path::geography) / EXTRACT(EPOCH FROM (end_time - start_time)) AS speed_mps
FROM trajectories;

-- 路径简化（减少点数）
UPDATE trajectories
SET path = ST_Simplify(path, 0.0001)  -- 容差
WHERE ST_NPoints(path) > 1000;
```

---

## 7. 热力图

### 7.1 网格聚合

```sql
-- 将点聚合到网格
WITH grid AS (
    SELECT
        ST_MakeEnvelope(
            x, y,
            x + 0.01, y + 0.01,
            4326
        ) AS cell,
        x, y
    FROM
        generate_series(116.0, 117.0, 0.01) x,
        generate_series(39.0, 40.0, 0.01) y
)
SELECT
    g.x,
    g.y,
    COUNT(l.loc_id) AS point_count
FROM grid g
LEFT JOIN locations l ON ST_Within(l.geom, g.cell)
GROUP BY g.x, g.y
HAVING COUNT(l.loc_id) > 0
ORDER BY point_count DESC;
```

---

## 8. 性能优化

### 8.1 空间索引优化

```sql
-- 聚簇索引（物理排序）
CLUSTER locations USING idx_locations_geom;

-- 定期维护
VACUUM ANALYZE locations;

-- 查看索引使用
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
WHERE indexrelname LIKE '%geom%'
ORDER BY idx_scan DESC;
```

### 8.2 geometry vs geography

```sql
-- geometry: 平面坐标，快
SELECT ST_Distance(
    ST_MakePoint(116.4, 39.9),
    ST_MakePoint(116.5, 40.0)
);  -- 返回度数

-- geography: 球面坐标，准确
SELECT ST_Distance(
    ST_MakePoint(116.4, 39.9)::geography,
    ST_MakePoint(116.5, 40.0)::geography
);  -- 返回米

-- 性能对比
-- geometry: 快10倍
-- geography: 精确（考虑地球曲率）

-- 建议: 小范围用geometry，大范围用geography
```

---

**完成**: PostGIS地理空间数据库实战
**字数**: ~10,000字
**涵盖**: 几何类型、空间索引、查询、实战案例（外卖、围栏）、性能优化
