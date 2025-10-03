# 地理围栏实战案例 — Geofencing with PostGIS

> **版本对标**：PostgreSQL 17 + PostGIS 3.4（更新于 2025-10）  
> **难度等级**：⭐⭐⭐⭐ 高级  
> **预计时间**：60-90分钟  
> **适合场景**：外卖配送、共享出行、物流跟踪、LBS营销

---

## 📋 案例目标

构建一个生产级的地理围栏系统，包括：

1. ✅ 点在多边形内判断（Point-in-Polygon）
2. ✅ 实时位置追踪与告警
3. ✅ 高性能空间索引（GiST索引）
4. ✅ 多围栏管理与优先级
5. ✅ 地理围栏进出事件触发

---

## 🎯 业务场景

**场景描述**：外卖骑手位置监控与配送区域管理

- **业务需求**：
  - 监控骑手是否在配送区域内
  - 骑手进入/离开围栏时触发告警
  - 查询附近可用骑手
  - 计算配送路线距离
- **性能要求**：
  - 10万骑手实时位置更新
  - 查询响应时间<50ms
  - 支持复杂多边形围栏

---

## 🏗️ 架构设计

```text
骑手位置上报（经纬度）
    ↓
PostGIS空间查询（ST_Contains）
    ↓
围栏匹配（GiST索引加速）
    ↓
触发器检测进出事件
    ↓
告警系统（NOTIFY/消息队列）
```

---

## 📦 1. 环境准备

### 1.1 安装PostGIS扩展

```sql
-- 创建PostGIS扩展
CREATE EXTENSION IF NOT EXISTS postgis;

-- 验证安装
SELECT PostGIS_Version();
SELECT PostGIS_Full_Version();

-- 输出示例：
-- PostGIS_Version: 3.4 USE_GEOS=1 USE_PROJ=1 USE_STATS=1
```

### 1.2 创建数据库

```sql
-- 创建专用数据库（可选）
CREATE DATABASE geofencing_db;
\c geofencing_db

CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;  -- 可选：拓扑功能
```

---

## 🗺️ 2. 数据模型设计

### 2.1 创建围栏表

```sql
-- 创建地理围栏表
CREATE TABLE geofences (
    id bigserial PRIMARY KEY,
    name text NOT NULL,
    description text,
    fence_type text NOT NULL,  -- 'delivery_zone', 'service_area', 'restricted_area'
    priority int DEFAULT 0,    -- 优先级（数值越大越高）
    geometry geometry(Polygon, 4326) NOT NULL,  -- 多边形，使用WGS84坐标系
    metadata jsonb,            -- 扩展信息（如营业时间、配送费等）
    is_active boolean DEFAULT true,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now()
);

-- 创建空间索引（GiST索引，加速空间查询）
CREATE INDEX idx_geofences_geometry ON geofences USING gist(geometry);

-- 创建其他索引
CREATE INDEX idx_geofences_type ON geofences(fence_type) WHERE is_active = true;
CREATE INDEX idx_geofences_priority ON geofences(priority DESC);

-- 添加约束
ALTER TABLE geofences
    ADD CONSTRAINT geofences_valid_geometry CHECK (ST_IsValid(geometry));

-- 添加注释
COMMENT ON TABLE geofences IS '地理围栏表：存储配送区域、服务区等多边形';
COMMENT ON COLUMN geofences.geometry IS 'PostGIS几何类型，SRID=4326（WGS84）';
```

### 2.2 创建位置追踪表

```sql
-- 创建骑手位置表
CREATE TABLE rider_locations (
    id bigserial PRIMARY KEY,
    rider_id bigint NOT NULL,
    location geometry(Point, 4326) NOT NULL,  -- 点坐标
    speed real,                -- 速度（km/h）
    heading real,              -- 方向（0-360度）
    accuracy real,             -- GPS精度（米）
    recorded_at timestamptz DEFAULT now(),
    
    -- 冗余字段（减少JOIN查询）
    latitude double precision,
    longitude double precision
);

-- 创建空间索引
CREATE INDEX idx_rider_locations_location ON rider_locations USING gist(location);

-- 创建其他索引
CREATE INDEX idx_rider_locations_rider_id ON rider_locations(rider_id);
CREATE INDEX idx_rider_locations_recorded_at ON rider_locations(recorded_at DESC);

-- 创建分区表（按日期分区，提升性能）
CREATE TABLE rider_locations_partitioned (
    id bigserial,
    rider_id bigint NOT NULL,
    location geometry(Point, 4326) NOT NULL,
    speed real,
    heading real,
    accuracy real,
    recorded_at timestamptz DEFAULT now(),
    PRIMARY KEY (id, recorded_at)
) PARTITION BY RANGE (recorded_at);

-- 创建分区
CREATE TABLE rider_locations_2025_10_01 PARTITION OF rider_locations_partitioned
    FOR VALUES FROM ('2025-10-01') TO ('2025-10-02');
CREATE TABLE rider_locations_2025_10_02 PARTITION OF rider_locations_partitioned
    FOR VALUES FROM ('2025-10-02') TO ('2025-10-03');
```

### 2.3 创建围栏事件表

```sql
-- 创建围栏进出事件表
CREATE TABLE fence_events (
    id bigserial PRIMARY KEY,
    rider_id bigint NOT NULL,
    fence_id bigint NOT NULL REFERENCES geofences(id),
    event_type text NOT NULL CHECK (event_type IN ('enter', 'exit')),
    location geometry(Point, 4326) NOT NULL,
    event_time timestamptz DEFAULT now(),
    metadata jsonb
);

CREATE INDEX idx_fence_events_rider_id ON fence_events(rider_id);
CREATE INDEX idx_fence_events_fence_id ON fence_events(fence_id);
CREATE INDEX idx_fence_events_time ON fence_events(event_time DESC);
CREATE INDEX idx_fence_events_type ON fence_events(event_type);
```

---

## 📝 3. 插入测试数据

### 3.1 创建围栏（北京部分区域）

```sql
-- 插入配送区域围栏（示例：北京朝阳区某商圈）
INSERT INTO geofences (name, description, fence_type, priority, geometry, metadata) VALUES
(
    '朝阳大悦城配送区',
    '朝阳大悦城3公里配送范围',
    'delivery_zone',
    10,
    ST_GeomFromText('POLYGON((
        116.480 39.925,
        116.490 39.925,
        116.490 39.935,
        116.480 39.935,
        116.480 39.925
    ))', 4326),
    '{"delivery_fee": 5, "min_order": 20, "business_hours": "09:00-22:00"}'::jsonb
),
(
    '三里屯服务区',
    '三里屯核心商圈',
    'service_area',
    20,
    ST_GeomFromText('POLYGON((
        116.450 39.915,
        116.460 39.915,
        116.460 39.925,
        116.450 39.925,
        116.450 39.915
    ))', 4326),
    '{"vip_area": true, "priority_service": true}'::jsonb
),
(
    '国贸中心区',
    '国贸商圈配送区',
    'delivery_zone',
    15,
    ST_GeomFromText('POLYGON((
        116.450 39.905,
        116.465 39.905,
        116.465 39.915,
        116.450 39.915,
        116.450 39.905
    ))', 4326),
    '{"delivery_fee": 8, "min_order": 30}'::jsonb
);

-- 查看已创建的围栏
SELECT 
    id,
    name,
    fence_type,
    priority,
    ST_AsText(geometry) AS wkt,
    ST_Area(geography::geography) AS area_sqm,  -- 面积（平方米）
    metadata
FROM geofences
ORDER BY priority DESC;
```

### 3.2 模拟骑手位置

```sql
-- 插入骑手位置数据
INSERT INTO rider_locations (rider_id, location, latitude, longitude, speed, heading, accuracy) VALUES
(1, ST_SetSRID(ST_MakePoint(116.485, 39.930), 4326), 39.930, 116.485, 15.5, 90, 5),
(2, ST_SetSRID(ST_MakePoint(116.455, 39.920), 4326), 39.920, 116.455, 12.0, 180, 8),
(3, ST_SetSRID(ST_MakePoint(116.460, 39.910), 4326), 39.910, 116.460, 20.0, 45, 3),
(4, ST_SetSRID(ST_MakePoint(116.470, 39.900), 4326), 39.900, 116.470, 0, 0, 10),  -- 超出所有围栏
(5, ST_SetSRID(ST_MakePoint(116.487, 39.928), 4326), 39.928, 116.487, 18.0, 270, 4);

-- 查看位置数据
SELECT 
    id,
    rider_id,
    ST_AsText(location) AS point,
    latitude,
    longitude,
    speed,
    recorded_at
FROM rider_locations
ORDER BY id;
```

---

## 🔍 4. 地理围栏查询

### 4.1 点在多边形内判断（核心功能）

```sql
-- 查询骑手在哪些围栏内
SELECT 
    rl.rider_id,
    rl.latitude,
    rl.longitude,
    g.id AS fence_id,
    g.name AS fence_name,
    g.fence_type,
    g.priority
FROM 
    rider_locations rl
JOIN 
    geofences g ON ST_Contains(g.geometry, rl.location)
WHERE 
    g.is_active = true
ORDER BY 
    rl.rider_id, g.priority DESC;

-- 查询特定骑手当前在哪个围栏内（按优先级取最高）
SELECT DISTINCT ON (rider_id)
    rider_id,
    fence_id,
    fence_name,
    priority
FROM (
    SELECT 
        rl.rider_id,
        g.id AS fence_id,
        g.name AS fence_name,
        g.priority
    FROM 
        rider_locations rl
    JOIN 
        geofences g ON ST_Contains(g.geometry, rl.location)
    WHERE 
        g.is_active = true
        AND rl.rider_id = 1
    ORDER BY 
        rl.recorded_at DESC, g.priority DESC
    LIMIT 1
) sub
ORDER BY rider_id;
```

### 4.2 查询围栏内的所有骑手

```sql
-- 查询指定围栏内的所有骑手
SELECT 
    rl.rider_id,
    rl.latitude,
    rl.longitude,
    rl.speed,
    rl.recorded_at,
    ST_Distance(
        rl.location::geography,
        ST_Centroid(g.geometry)::geography
    ) AS distance_to_center_m  -- 到围栏中心的距离
FROM 
    rider_locations rl
JOIN 
    geofences g ON ST_Contains(g.geometry, rl.location)
WHERE 
    g.name = '朝阳大悦城配送区'
    AND g.is_active = true
ORDER BY 
    rl.recorded_at DESC;
```

### 4.3 附近骑手查询（半径搜索）

```sql
-- 查询指定点附近1000米内的骑手
SELECT 
    rider_id,
    latitude,
    longitude,
    ST_Distance(
        location::geography,
        ST_SetSRID(ST_MakePoint(116.485, 39.930), 4326)::geography
    ) AS distance_m,
    speed,
    recorded_at
FROM 
    rider_locations
WHERE 
    ST_DWithin(
        location::geography,
        ST_SetSRID(ST_MakePoint(116.485, 39.930), 4326)::geography,
        1000  -- 1000米
    )
ORDER BY 
    distance_m
LIMIT 10;
```

### 4.4 计算配送距离

```sql
-- 计算骑手到目标点的直线距离
SELECT 
    rider_id,
    ST_Distance(
        location::geography,
        ST_SetSRID(ST_MakePoint(116.480, 39.925), 4326)::geography
    ) AS straight_distance_m,
    ST_Distance(
        location::geography,
        ST_SetSRID(ST_MakePoint(116.480, 39.925), 4326)::geography
    ) / 1000 AS straight_distance_km
FROM 
    rider_locations
WHERE 
    rider_id = 1;

-- 计算围栏面积
SELECT 
    id,
    name,
    ST_Area(geometry::geography) AS area_sqm,
    ST_Area(geometry::geography) / 1000000 AS area_sqkm,
    ST_Perimeter(geometry::geography) AS perimeter_m
FROM 
    geofences
ORDER BY area_sqm DESC;
```

---

## 🚀 5. 高级特性

### 5.1 实时围栏进出检测（触发器）

```sql
-- 创建触发器函数：检测围栏进出事件
CREATE OR REPLACE FUNCTION detect_fence_events()
RETURNS trigger AS $$
DECLARE
    current_fences bigint[];
    previous_fences bigint[];
    entered_fences bigint[];
    exited_fences bigint[];
    fence_id bigint;
BEGIN
    -- 获取当前位置所在的围栏
    SELECT ARRAY_AGG(g.id)
    INTO current_fences
    FROM geofences g
    WHERE ST_Contains(g.geometry, NEW.location)
      AND g.is_active = true;
    
    -- 获取上一次位置所在的围栏
    SELECT ARRAY_AGG(g.id)
    INTO previous_fences
    FROM rider_locations rl
    JOIN geofences g ON ST_Contains(g.geometry, rl.location)
    WHERE rl.rider_id = NEW.rider_id
      AND rl.id < NEW.id
      AND g.is_active = true
    ORDER BY rl.id DESC
    LIMIT 1;
    
    -- 处理NULL情况
    current_fences := COALESCE(current_fences, ARRAY[]::bigint[]);
    previous_fences := COALESCE(previous_fences, ARRAY[]::bigint[]);
    
    -- 计算进入的围栏
    entered_fences := ARRAY(
        SELECT unnest(current_fences)
        EXCEPT
        SELECT unnest(previous_fences)
    );
    
    -- 计算离开的围栏
    exited_fences := ARRAY(
        SELECT unnest(previous_fences)
        EXCEPT
        SELECT unnest(current_fences)
    );
    
    -- 记录进入事件
    FOREACH fence_id IN ARRAY entered_fences
    LOOP
        INSERT INTO fence_events (rider_id, fence_id, event_type, location, event_time)
        VALUES (NEW.rider_id, fence_id, 'enter', NEW.location, NEW.recorded_at);
        
        -- 发送通知
        PERFORM pg_notify('fence_event', json_build_object(
            'rider_id', NEW.rider_id,
            'fence_id', fence_id,
            'event_type', 'enter',
            'timestamp', extract(epoch from NEW.recorded_at)
        )::text);
    END LOOP;
    
    -- 记录离开事件
    FOREACH fence_id IN ARRAY exited_fences
    LOOP
        INSERT INTO fence_events (rider_id, fence_id, event_type, location, event_time)
        VALUES (NEW.rider_id, fence_id, 'exit', NEW.location, NEW.recorded_at);
        
        -- 发送通知
        PERFORM pg_notify('fence_event', json_build_object(
            'rider_id', NEW.rider_id,
            'fence_id', fence_id,
            'event_type', 'exit',
            'timestamp', extract(epoch from NEW.recorded_at)
        )::text);
    END LOOP;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 创建触发器
CREATE TRIGGER rider_location_fence_trigger
    AFTER INSERT ON rider_locations
    FOR EACH ROW
    EXECUTE FUNCTION detect_fence_events();
```

### 5.2 测试围栏进出事件

```sql
-- 测试：骑手移动进入围栏
INSERT INTO rider_locations (rider_id, location, latitude, longitude)
VALUES (10, ST_SetSRID(ST_MakePoint(116.485, 39.930), 4326), 39.930, 116.485);

-- 测试：骑手移动离开围栏
INSERT INTO rider_locations (rider_id, location, latitude, longitude)
VALUES (10, ST_SetSRID(ST_MakePoint(116.500, 39.940), 4326), 39.940, 116.500);

-- 查看事件记录
SELECT 
    fe.id,
    fe.rider_id,
    g.name AS fence_name,
    fe.event_type,
    ST_AsText(fe.location) AS location,
    fe.event_time
FROM 
    fence_events fe
JOIN 
    geofences g ON fe.fence_id = g.id
WHERE 
    fe.rider_id = 10
ORDER BY 
    fe.event_time DESC;
```

### 5.3 复杂围栏查询

```sql
-- 查询重叠的围栏
SELECT 
    a.id AS fence_a_id,
    a.name AS fence_a_name,
    b.id AS fence_b_id,
    b.name AS fence_b_name,
    ST_Area(ST_Intersection(a.geometry, b.geometry)::geography) AS overlap_area_sqm
FROM 
    geofences a
JOIN 
    geofences b ON a.id < b.id
WHERE 
    ST_Intersects(a.geometry, b.geometry)
    AND a.is_active = true
    AND b.is_active = true;

-- 查询某点所在的所有围栏（按优先级排序）
SELECT 
    g.id,
    g.name,
    g.fence_type,
    g.priority,
    g.metadata
FROM 
    geofences g
WHERE 
    ST_Contains(
        g.geometry,
        ST_SetSRID(ST_MakePoint(116.485, 39.930), 4326)
    )
    AND g.is_active = true
ORDER BY 
    g.priority DESC;
```

---

## 📊 6. 性能优化

### 6.1 空间索引优化

```sql
-- 查看空间索引使用情况
EXPLAIN (ANALYZE, BUFFERS)
SELECT COUNT(*)
FROM rider_locations rl
JOIN geofences g ON ST_Contains(g.geometry, rl.location)
WHERE g.is_active = true;

-- 期望看到：
-- Index Scan using idx_geofences_geometry on geofences

-- 强制使用空间索引
SET enable_seqscan = off;

-- 分析空间索引效率
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
WHERE tablename IN ('geofences', 'rider_locations')
ORDER BY idx_scan DESC;
```

### 6.2 简化几何对象

```sql
-- 简化复杂多边形（减少顶点数，提升性能）
UPDATE geofences
SET geometry = ST_SimplifyPreserveTopology(geometry, 0.0001)
WHERE ST_NPoints(geometry) > 100;

-- 查看简化效果
SELECT 
    id,
    name,
    ST_NPoints(geometry) AS num_points,
    ST_IsValid(geometry) AS is_valid,
    pg_size_pretty(pg_column_size(geometry)) AS geometry_size
FROM geofences
ORDER BY num_points DESC;
```

### 6.3 批量位置更新

```sql
-- 使用COPY批量导入位置数据（性能最优）
COPY rider_locations (rider_id, latitude, longitude, location, speed, heading, recorded_at)
FROM STDIN WITH (FORMAT csv);
1,39.930,116.485,ST_SetSRID(ST_MakePoint(116.485, 39.930), 4326),15.5,90,2025-10-03 12:00:00
2,39.920,116.455,ST_SetSRID(ST_MakePoint(116.455, 39.920), 4326),12.0,180,2025-10-03 12:00:05
\.

-- 或使用批量INSERT
INSERT INTO rider_locations (rider_id, location, latitude, longitude)
SELECT
    (random() * 1000)::int AS rider_id,
    ST_SetSRID(
        ST_MakePoint(
            116.45 + random() * 0.05,  -- 经度
            39.90 + random() * 0.05    -- 纬度
        ),
        4326
    ) AS location,
    39.90 + random() * 0.05 AS latitude,
    116.45 + random() * 0.05 AS longitude
FROM generate_series(1, 10000);
```

---

## 🎨 7. 可视化与监控

### 7.1 导出GeoJSON（供前端地图展示）

```sql
-- 导出围栏为GeoJSON
SELECT 
    jsonb_build_object(
        'type', 'FeatureCollection',
        'features', jsonb_agg(
            jsonb_build_object(
                'type', 'Feature',
                'id', id,
                'geometry', ST_AsGeoJSON(geometry)::jsonb,
                'properties', jsonb_build_object(
                    'name', name,
                    'fence_type', fence_type,
                    'priority', priority,
                    'metadata', metadata
                )
            )
        )
    ) AS geojson
FROM geofences
WHERE is_active = true;

-- 导出骑手位置为GeoJSON
SELECT 
    jsonb_build_object(
        'type', 'FeatureCollection',
        'features', jsonb_agg(
            jsonb_build_object(
                'type', 'Feature',
                'id', rider_id,
                'geometry', ST_AsGeoJSON(location)::jsonb,
                'properties', jsonb_build_object(
                    'rider_id', rider_id,
                    'speed', speed,
                    'heading', heading,
                    'recorded_at', recorded_at
                )
            )
        )
    ) AS geojson
FROM rider_locations
WHERE recorded_at > now() - interval '5 minutes';
```

### 7.2 监控视图

```sql
-- 创建实时监控视图
CREATE OR REPLACE VIEW geofence_realtime_stats AS
SELECT 
    g.id AS fence_id,
    g.name AS fence_name,
    g.fence_type,
    COUNT(DISTINCT rl.rider_id) AS rider_count,
    AVG(rl.speed) AS avg_speed,
    MAX(rl.recorded_at) AS last_update_time
FROM 
    geofences g
LEFT JOIN 
    rider_locations rl ON ST_Contains(g.geometry, rl.location)
WHERE 
    g.is_active = true
    AND rl.recorded_at > now() - interval '5 minutes'
GROUP BY 
    g.id, g.name, g.fence_type
ORDER BY 
    rider_count DESC;

-- 查询统计
SELECT * FROM geofence_realtime_stats;
```

---

## ✅ 8. 完整示例

```sql
-- 综合查询：查找附近空闲骑手并分配订单
WITH target_location AS (
    SELECT ST_SetSRID(ST_MakePoint(116.485, 39.930), 4326) AS point
),
nearby_riders AS (
    SELECT 
        rl.rider_id,
        rl.location,
        rl.speed,
        ST_Distance(
            rl.location::geography,
            tl.point::geography
        ) AS distance_m
    FROM 
        rider_locations rl,
        target_location tl
    WHERE 
        rl.recorded_at > now() - interval '1 minute'
        AND ST_DWithin(
            rl.location::geography,
            tl.point::geography,
            3000  -- 3公里范围内
        )
),
riders_in_fence AS (
    SELECT 
        nr.rider_id,
        nr.distance_m,
        g.name AS fence_name,
        g.priority AS fence_priority
    FROM 
        nearby_riders nr
    JOIN 
        geofences g ON ST_Contains(g.geometry, nr.location)
    WHERE 
        g.fence_type = 'delivery_zone'
        AND g.is_active = true
)
SELECT 
    rider_id,
    round(distance_m::numeric, 2) AS distance_m,
    fence_name,
    fence_priority
FROM 
    riders_in_fence
ORDER BY 
    fence_priority DESC,
    distance_m ASC
LIMIT 5;
```

---

## 📚 9. 最佳实践

### 9.1 坐标系选择

- ✅ 使用SRID 4326（WGS84）存储经纬度
- ✅ 距离计算时转换为geography类型
- ✅ 避免混用不同坐标系

### 9.2 性能优化

- ✅ 创建GiST空间索引
- ✅ 简化复杂几何对象
- ✅ 使用分区表存储历史位置
- ✅ 定期VACUUM维护

### 9.3 业务设计

- ✅ 设置围栏优先级
- ✅ 支持围栏时间范围
- ✅ 记录进出事件
- ✅ 实现告警机制

---

## 🎯 10. 练习任务

1. **基础练习**：
   - 创建3个配送区域围栏
   - 插入10个骑手位置
   - 查询每个围栏内的骑手数量

2. **进阶练习**：
   - 实现围栏进出事件检测
   - 创建实时监控视图
   - 导出GeoJSON供前端展示

3. **挑战任务**：
   - 构建完整的LBS配送系统
   - 优化百万级位置更新性能
   - 实现复杂路径规划算法

---

**维护者**：PostgreSQL_modern Project Team  
**最后更新**：2025-10-03  
**下一步**：查看 [联邦查询案例](../federated_queries/README.md)
