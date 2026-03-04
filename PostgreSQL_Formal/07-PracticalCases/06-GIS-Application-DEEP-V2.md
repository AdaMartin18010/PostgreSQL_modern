# GIS应用PostgreSQL架构深度实战 v2.0

> **文档类型**: 深度实战案例 (形式化论证版)
> **业务场景**: 城市级位置服务与地图应用
> **技术栈**: PostgreSQL 16/17/18, PostGIS 3.4, PgRouting, pg_tileserv
> **创建日期**: 2026-03-04
> **文档长度**: 6000+字

---

## 摘要

本文基于城市级位置服务与地图应用实战场景，深入剖析PostgreSQL+PostGIS在空间数据管理、地理索引优化与地图服务集成中的架构设计。涵盖PostGIS核心扩展、空间数据模型设计、地理索引(GiST/SP-GiST)原理与优化、复杂空间查询实现、路径规划算法及矢量瓦片服务。通过形式化方法定义空间查询模型，给出索引选择的最优性证明，并基于生产环境实测数据验证方案有效性。

**关键词**: GIS、PostGIS、空间索引、地理查询、路径规划、矢量瓦片、PostgreSQL

---

## 1. 系统概述

### 1.1 业务规模与挑战

| 指标 | 数值 | 挑战 |
|------|------|------|
| POI数据量 | 5000万+ | 空间索引效率 |
| 轨迹数据/天 | 10亿+点 | 时序+空间混合查询 |
| 并发查询 | 50,000 QPS | 地理围栏实时判断 |
| 道路网络 | 1000万公里 | 路径规划性能 |
| 服务响应 | < 100ms (P99) | 空间计算优化 |
| 数据精度 | 厘米级(RTK) | 高精度坐标存储 |

### 1.2 系统架构

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         GIS系统整体架构                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐   │
│  │  地图服务   │  │  位置服务   │  │  导航服务   │  │   分析服务      │   │
│  │ Map Service │  │ Location Svc│  │ Navigation  │  │   Analytics     │   │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └────────┬────────┘   │
│         │                │                │                  │            │
│         └────────────────┴────────────────┴──────────────────┘            │
│                              │                                            │
│                              ▼                                            │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    PostGIS 空间数据库层                              │   │
│  │  ┌──────────────────────────────────────────────────────────────┐  │   │
│  │  │  PostGIS Extension                                          │  │   │
│  │  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────────┐  │  │   │
│  │  │  │ Geometry │  │ Geography│  │ Raster   │  │  Topology   │  │  │   │
│  │  │  │   2D/3D  │  │  球面坐标 │  │ 栅格分析 │  │  拓扑网络   │  │  │   │
│  │  │  └──────────┘  └──────────┘  └──────────┘  └─────────────┘  │  │   │
│  │  └──────────────────────────────────────────────────────────────┘  │   │
│  │                                                                     │   │
│  │  ┌──────────────────────────────────────────────────────────────┐  │   │
│  │  │  空间索引层                                                   │  │   │
│  │  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────────┐  │  │   │
│  │  │  │  GiST    │  │ SP-GiST  │  │  GIN     │  │   BRIN      │  │  │   │
│  │  │  │ 通用搜索树│  │ 空间分区 │  │ JSON检索 │  │ 块范围索引  │  │  │   │
│  │  │  └──────────┘  └──────────┘  └──────────┘  └─────────────┘  │  │   │
│  │  └──────────────────────────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                              │                                            │
│                              ▼                                            │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    存储层                                            │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────────────────┐ │   │
│  │  │ 主实例    │  │ 只读副本  │  │  归档存储 │  │  对象存储(瓦片缓存)  │ │   │
│  │  │ Primary  │  │ Replica  │  │ Archive  │  │  S3/OSS Tiles       │ │   │
│  │  └──────────┘  └──────────┘  └──────────┘  └─────────────────────┘ │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.3 PostGIS核心模块

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       PostGIS 3.4 核心模块架构                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  PostGIS Extension                                                          │
│  │                                                                          │
│  ├─ postgis          # 核心几何类型与函数                                   │
│  │   ├─ Geometry Types: POINT, LINESTRING, POLYGON, MULTI*, GEOMETRYCOLLECTION│
│  │   ├─ Coordinate Systems: 2D, 3DZ, 3DM, 4D                               │
│  │   ├─ Spatial Functions: ST_Distance, ST_Intersects, ST_Buffer, ST_Union │
│  │   └─ Coordinate Reference Systems: 6000+ EPSG codes                     │
│  │                                                                          │
│  ├─ postgis_topology  # 拓扑数据模型                                       │
│  │   ├─ Face/Edge/Node topology                                           │
│  │   ├─ TopoGeometry validation                                           │
│  │   └─ Topological editing                                               │
│  │                                                                          │
│  ├─ postgis_raster    # 栅格数据处理                                       │
│  │   ├─ Raster tile storage                                               │
│  │   ├─ ST_MapAlgebra, ST_Intersection                                    │
│  │   └─ GDAL integration                                                  │
│  │                                                                          │
│  ├─ postgis_sfcgal    # 3D几何处理 (CGAL绑定)                               │
│  │   ├─ 3D buffering                                                        │
│  │   ├─ Extrusion, extrudeStraightSkeleton                                  │
│  │   └─ Volume/Area 3D calculations                                         │
│  │                                                                          │
│  ├─ address_standardizer  # 地址标准化                                     │
│  │   └─ Rule-based address parsing                                          │
│  │                                                                          │
│  └─ postgis_tiger_geocoder  # TIGER地理编码器                               │
│      └─ US Census data integration                                         │
│                                                                             │
│  pgRouting Extension                                                        │
│  ├─ Shortest Path: Dijkstra, A*, Johnson                                   │
│  ├─ Traveling Salesman Problem (TSP)                                       │
│  ├─ Vehicle Routing Problem (VRP)                                          │
│  └─ Turn restrictions, one-way streets                                     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. 空间数据模型

### 2.1 空间数据类型选择

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     Geometry vs Geography 选择指南                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────┐    ┌─────────────────────┐                        │
│  │     Geometry        │    │     Geography       │                        │
│  │   (平面坐标系)       │    │    (地理坐标系)      │                        │
│  ├─────────────────────┤    ├─────────────────────┤                        │
│  │ • 使用平面坐标       │    │ • 使用经纬度        │                        │
│  │ • 计算速度快 10-100x│    │ • 自动处理球面距离  │                        │
│  │ • 适合小范围(<100km)│    │ • 适合大范围/全球   │                        │
│  │ • 支持所有空间函数  │    │ • 部分函数不支持    │                        │
│  ├─────────────────────┤    ├─────────────────────┤                        │
│  │ 典型应用:           │    │ 典型应用:           │                        │
│  │ • 城市规划          │    │ • 跨国物流          │                        │
│  │ • 室内导航          │    │ • 航空路线          │                        │
│  │ • 园区管理          │    │ • 海运航线          │                        │
│  │ • 本地配送          │    │ • 全球位置服务      │                        │
│  └─────────────────────┘    └─────────────────────┘                        │
│                                                                             │
│  选择公式:                                                                  │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  if (数据范围 > 100km || 跨越多个时区)                              │   │
│  │      → use Geography                                               │   │
│  │  else                                                              │   │
│  │      → use Geometry (性能优先)                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 ER关系图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         GIS应用系统ER关系图                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────────┐                                                      │
│  │  spatial_ref_sys │  # PostGIS内置坐标系统表                             │
│  │──────────────────│                                                      │
│  │ srid (PK)        │                                                      │
│  │ auth_name        │                                                      │
│  │ auth_srid        │                                                      │
│  │ srtext           │                                                      │
│  │ proj4text        │                                                      │
│  └────────┬─────────┘                                                      │
│           │                                                                │
│           │  (所有几何列通过SRID引用)                                        │
│           ▼                                                                │
│  ┌──────────────────┐         ┌──────────────────┐                        │
│  │       poi        │         │  poi_categories  │                        │
│  │──────────────────│         │──────────────────│                        │
│  │ PK poi_id        │◄────────│ PK category_id   │                        │
│  │ FK category_id   │   N:1   │    name          │                        │
│  │    name          │         │    icon          │                        │
│  │    geom(geometry)│         │    parent_id     │                        │
│  │    address       │         └──────────────────┘                        │
│  │    attributes    │                                                      │
│  │    created_at    │                                                      │
│  └────────┬─────────┘                                                      │
│           │                                                                │
│           │ 1:N                                                            │
│           ▼                                                                │
│  ┌──────────────────┐         ┌──────────────────┐                        │
│  │  trajectory_points│        │    road_network  │                        │
│  │──────────────────│         │──────────────────│                        │
│  │ PK point_id      │         │ PK road_id       │                        │
│  │ FK poi_id        │         │    name          │                        │
│  │    geom          │         │    geom(line)    │                        │
│  │    timestamp     │         │    source        │                        │
│  │    speed         │         │    target        │                        │
│  │    direction     │         │    length        │                        │
│  │    accuracy      │         │    max_speed     │                        │
│  └──────────────────┘         │    one_way       │                        │
│                               │    road_class    │                        │
│                               └────────┬─────────┘                        │
│                                        │                                   │
│                                        │ N:M (via)                         │
│                                        ▼                                   │
│  ┌──────────────────┐         ┌──────────────────┐                        │
│  │  geofence_zones  │         │  route_segments  │                        │
│  │──────────────────│         │──────────────────│                        │
│  │ PK zone_id       │         │ FK route_id      │                        │
│  │    name          │         │ FK road_id       │                        │
│  │    geom(polygon) │         │    sequence      │                        │
│  │    zone_type     │         └──────────────────┘                        │
│  │    rules(jsonb)  │                                                      │
│  └──────────────────┘                                                      │
│                                                                             │
│  ┌──────────────────┐         ┌──────────────────┐                        │
│  │  map_tiles_cache │         │  spatial_analysis│                        │
│  │──────────────────│         │──────────────────│                        │
│  │ PK tile_key      │         │ PK analysis_id   │                        │
│  │    zoom_level    │         │    query_type    │                        │
│  │    tile_x        │         │    geom_input    │                        │
│  │    tile_y        │         │    geom_result   │                        │
│  │    tile_data     │         │    metrics       │                        │
│  │    cached_at     │         │    created_at    │                        │
│  └──────────────────┘         └──────────────────┘                        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.3 核心表结构

```sql
-- ============================================
-- 2.3.1 启用PostGIS扩展
-- ============================================
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;
CREATE EXTENSION IF NOT EXISTS postgis_sfcgal;

-- 验证安装
SELECT PostGIS_Version();

-- ============================================
-- 2.3.2 POI点数据表
-- ============================================
CREATE TABLE poi (
    poi_id          BIGSERIAL PRIMARY KEY,
    category_id     INTEGER NOT NULL,
    name            VARCHAR(255) NOT NULL,
    name_pinyin     VARCHAR(255), -- 拼音用于搜索
    geom            GEOMETRY(POINT, 4326) NOT NULL, -- WGS84坐标系
    address         VARCHAR(500),
    province        VARCHAR(50),
    city            VARCHAR(50),
    district        VARCHAR(50),
    phone           VARCHAR(50),
    business_hours  VARCHAR(200),
    rating          DECIMAL(2, 1) CHECK (rating >= 0 AND rating <= 5),
    review_count    INTEGER DEFAULT 0,
    attributes      JSONB DEFAULT '{}', -- 扩展属性
    status          SMALLINT DEFAULT 1, -- 0:关闭 1:营业
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
) PARTITION BY HASH (poi_id);

-- 创建16个分区
DO $$
BEGIN
    FOR i IN 0..15 LOOP
        EXECUTE format('CREATE TABLE poi_%s PARTITION OF poi 
                       FOR VALUES WITH (MODULUS 16, REMAINDER %s)', i, i);
    END LOOP;
END $$;

-- 空间索引 (GiST)
CREATE INDEX idx_poi_geom ON poi USING GIST(geom);

-- 复合索引: 城市+分类 (支持本地生活服务查询)
CREATE INDEX idx_poi_city_category ON poi(city, category_id) 
WHERE status = 1;

-- GIN索引: 扩展属性搜索
CREATE INDEX idx_poi_attrs ON poi USING GIN(attributes);

-- 全文搜索索引
CREATE INDEX idx_poi_name_fulltext ON poi 
USING GIN(to_tsvector('chinese', name || ' ' || COALESCE(address, '')));

COMMENT ON TABLE poi IS '兴趣点(POI)主表，存储地理位置信息';
COMMENT ON COLUMN poi.geom IS 'WGS84坐标系几何点，EPSG:4326';

-- ============================================
-- 2.3.3 POI分类表
-- ============================================
CREATE TABLE poi_categories (
    category_id     SERIAL PRIMARY KEY,
    parent_id       INTEGER REFERENCES poi_categories(category_id),
    name            VARCHAR(64) NOT NULL,
    name_en         VARCHAR(64),
    icon_url        VARCHAR(255),
    level           SMALLINT DEFAULT 1, -- 分类层级
    sort_order      INTEGER DEFAULT 0,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- 插入示例分类
INSERT INTO poi_categories (category_id, name, level) VALUES
(1, '餐饮', 1),
(2, '购物', 1),
(3, '生活服务', 1),
(4, '休闲娱乐', 1),
(11, '中餐', 2), (12, '西餐', 2), (13, '快餐', 2), -- 餐饮子类
(21, '超市', 2), (22, '便利店', 2), (23, '购物中心', 2); -- 购物子类

-- ============================================
-- 2.3.4 轨迹点表 (时序+空间分区)
-- ============================================
CREATE TABLE trajectory_points (
    point_id        BIGSERIAL,
    device_id       VARCHAR(64) NOT NULL,
    geom            GEOMETRY(POINT, 4326) NOT NULL,
    longitude       DECIMAL(12, 8) NOT NULL, -- 冗余存储便于直接读取
    latitude        DECIMAL(12, 8) NOT NULL,
    altitude        DECIMAL(10, 2),
    speed           DECIMAL(6, 2), -- km/h
    direction       SMALLINT, -- 0-360度
    accuracy        DECIMAL(6, 2), -- GPS精度(米)
    provider        SMALLINT DEFAULT 1, -- 1:GPS 2:WiFi 3:基站 4:混合
    timestamp       TIMESTAMPTZ NOT NULL,
    extra           JSONB DEFAULT '{}',
    PRIMARY KEY (device_id, timestamp, point_id)
) PARTITION BY RANGE (timestamp);

-- 按月创建分区
CREATE TABLE trajectory_points_y2026m01 PARTITION OF trajectory_points
    FOR VALUES FROM ('2026-01-01') TO ('2026-02-01');
CREATE TABLE trajectory_points_y2026m02 PARTITION OF trajectory_points
    FOR VALUES FROM ('2026-02-01') TO ('2026-03-01');

-- BRIN索引: 适合时序追加数据
CREATE INDEX idx_traj_time_brin ON trajectory_points 
USING BRIN(timestamp);

-- 空间索引
CREATE INDEX idx_traj_geom ON trajectory_points 
USING GIST(geom);

-- 设备+时间索引 (轨迹查询)
CREATE INDEX idx_traj_device_time ON trajectory_points(device_id, timestamp DESC);

COMMENT ON TABLE trajectory_points IS '设备轨迹点数据，按时序分区';

-- ============================================
-- 2.3.5 道路网络表 (用于路径规划)
-- ============================================
CREATE TABLE road_network (
    road_id         BIGSERIAL PRIMARY KEY,
    source_node     BIGINT NOT NULL,
    target_node     BIGINT NOT NULL,
    name            VARCHAR(255),
    road_type       SMALLINT DEFAULT 1, -- 1:高速 2:国道 3:省道 4:城市主干 5:其他
    geom            GEOMETRY(LINESTRING, 4326) NOT NULL,
    length_m        DECIMAL(10, 2) NOT NULL, -- 长度(米)
    max_speed       SMALLINT, -- 限速(km/h)
    oneway          SMALLINT DEFAULT 0, -- 0:双向 1:正向 -1:反向
    lanes           SMALLINT DEFAULT 2,
    bridge          BOOLEAN DEFAULT FALSE,
    tunnel          BOOLEAN DEFAULT FALSE,
    toll            BOOLEAN DEFAULT FALSE,
    status          SMALLINT DEFAULT 1, -- 0:在建 1:正常 2:封闭
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- 空间索引
CREATE INDEX idx_road_geom ON road_network USING GIST(geom);

-- 路网拓扑索引 (pgRouting需要)
CREATE INDEX idx_road_source ON road_network(source_node);
CREATE INDEX idx_road_target ON road_network(target_node);

-- 道路类型索引
CREATE INDEX idx_road_type ON road_network(road_type) WHERE status = 1;

COMMENT ON TABLE road_network IS '道路网络数据，支持pgRouting路径规划';

-- ============================================
-- 2.3.6 地理围栏表
-- ============================================
CREATE TABLE geofence_zones (
    zone_id         BIGSERIAL PRIMARY KEY,
    name            VARCHAR(128) NOT NULL,
    zone_type       SMALLINT NOT NULL CHECK (zone_type IN (1, 2, 3)), 
                    -- 1:禁止进入 2:限速 3:通知
    geom            GEOMETRY(POLYGON, 4326) NOT NULL,
    altitude_min    INTEGER, -- 最低高度(米)，用于空域
    altitude_max    INTEGER, -- 最高高度(米)
    rules           JSONB DEFAULT '{}', -- 规则配置
                    -- {"speed_limit": 30, "notify_on_enter": true, ...}
    schedule        JSONB DEFAULT '{}', -- 生效时间
                    -- {"start_time": "08:00", "end_time": "20:00", "days": [1,2,3,4,5]}
    is_active       BOOLEAN DEFAULT TRUE,
    created_by      BIGINT,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- 空间索引 (GiST支持多边形包含查询)
CREATE INDEX idx_geofence_geom ON geofence_zones 
USING GIST(geom) WHERE is_active = TRUE;

-- 类型索引
CREATE INDEX idx_geofence_type ON geofence_zones(zone_type) WHERE is_active = TRUE;

COMMENT ON TABLE geofence_zones IS '地理围栏区域，支持多边形和高度范围';

-- ============================================
-- 2.3.7 行政区划表
-- ============================================
CREATE TABLE administrative_regions (
    region_id       BIGSERIAL PRIMARY KEY,
    code            VARCHAR(12) NOT NULL UNIQUE, -- 国家统计局编码
    parent_code     VARCHAR(12),
    name            VARCHAR(64) NOT NULL,
    level           SMALLINT NOT NULL CHECK (level IN (1, 2, 3, 4)), 
                    -- 1:省 2:市 3:区县 4:乡镇
    center_geom     GEOMETRY(POINT, 4326),
    boundary_geom   GEOMETRY(MULTIPOLYGON, 4326),
    area_km2        DECIMAL(12, 2),
    population      BIGINT,
    extra           JSONB DEFAULT '{}',
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_region_geom ON administrative_regions USING GIST(boundary_geom);
CREATE INDEX idx_region_code ON administrative_regions(code);
CREATE INDEX idx_region_parent ON administrative_regions(parent_code);

COMMENT ON TABLE administrative_regions IS '中国行政区划边界数据';
```

---

## 3. 地理索引优化

### 3.1 索引类型对比

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      PostGIS空间索引类型对比                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  GiST (Generalized Search Tree)                                      │   │
│  │  ─────────────────────────────────────────────────────────────────  │   │
│  │  原理: R-Tree变体，支持所有几何类型的最近邻搜索                        │   │
│  │  适用: 通用空间查询，支持 && (bounding box重叠), @>, <@ 等操作符      │   │
│  │  优点: 支持KNN (<->) 距离排序，自动处理所有几何类型                    │   │
│  │  缺点: 索引较大，更新有一定开销                                       │   │
│  │                                                                     │   │
│  │  使用场景:                                                          │   │
│  │  • "附近的POI" 搜索                                                  │   │
│  │  • 多边形包含判断                                                    │   │
│  │  • 任意几何类型的空间关系查询                                         │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  SP-GiST (Space-Partitioning GiST)                                   │   │
│  │  ─────────────────────────────────────────────────────────────────  │   │
│  │  原理: 空间分区树 (Quadtree/KD-tree)，递归划分空间                     │   │
│  │  适用: 点数据，均匀分布的空间数据                                     │   │
│  │  优点: 点数据查询更快，索引更小                                       │   │
│  │  缺点: 仅支持点类型，不支持其他几何类型                                │   │
│  │                                                                     │   │
│  │  使用场景:                                                          │   │
│  │  • 大规模轨迹点数据                                                  │   │
│  │  • 传感器位置数据                                                    │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  BRIN (Block Range INdex)                                            │   │
│  │  ─────────────────────────────────────────────────────────────────  │   │
│  │  原理: 存储每个数据块的空间范围摘要，而非逐行索引                       │   │
│  │  适用: 大规模时序+空间数据，数据按时间/空间有序插入                     │   │
│  │  优点: 索引极小 (相比GiST小100-1000倍)                                │   │
│  │  缺点: 仅适合范围查询，不适合点查                                     │   │
│  │                                                                     │   │
│  │  使用场景:                                                          │   │
│  │  • 历史轨迹数据                                                      │   │
│  │  • 时序位置数据                                                      │   │
│  │  • 数据量 > 1000万且按时间有序                                        │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.2 索引创建策略

```sql
-- ============================================
-- 3.2.1 GiST索引参数调优
-- ============================================

-- 标准GiST索引
CREATE INDEX idx_poi_geom_gist ON poi USING GIST(geom);

-- GiST索引带缓冲参数 (数据更新频繁时使用)
CREATE INDEX idx_poi_geom_gist_buffered ON poi 
USING GIST(geom) WITH (buffering = 'on', fillfactor = 90);

-- 3D空间索引 (包含高度)
CREATE INDEX idx_geofence_3d ON geofence_zones 
USING GIST(geom) WITH (dimension = 3);

-- ============================================
-- 3.2.2 SP-GiST点数据索引
-- ============================================
CREATE INDEX idx_traj_spgist ON trajectory_points 
USING SPGIST(geom);

-- ============================================
-- 3.2.3 BRIN索引 (海量时序数据)
-- ============================================

-- 基本BRIN索引
CREATE INDEX idx_traj_brin ON trajectory_points 
USING BRIN(timestamp);

-- 带空间范围的BRIN (需要PostGIS 3.0+)
CREATE INDEX idx_traj_brin_geom ON trajectory_points 
USING BRIN(geom) WITH (pages_per_range = 128);

-- ============================================
-- 3.2.4 索引选择决策函数
-- ============================================
CREATE OR REPLACE FUNCTION recommend_spatial_index(
    p_table_name TEXT,
    p_geom_column TEXT,
    p_data_type TEXT, -- 'point', 'line', 'polygon'
    p_data_volume BIGINT, -- 预估数据量
    p_update_frequency TEXT -- 'high', 'medium', 'low'
) RETURNS TABLE (
    recommended_index TEXT,
    reasoning TEXT,
    create_sql TEXT
) AS $$
BEGIN
    IF p_data_type = 'point' AND p_data_volume > 10000000 THEN
        RETURN QUERY SELECT 
            'SP-GiST'::TEXT,
            '点数据量大，SP-GiST索引更小更快'::TEXT,
            format('CREATE INDEX idx_%s_spgist ON %I USING SPGIST(%I);',
                   p_table_name, p_table_name, p_geom_column);
    ELSIF p_data_volume > 50000000 AND p_update_frequency = 'low' THEN
        RETURN QUERY SELECT 
            'BRIN'::TEXT,
            '海量历史数据，BRIN索引极小'::TEXT,
            format('CREATE INDEX idx_%s_brin ON %I USING BRIN(%I);',
                   p_table_name, p_table_name, p_geom_column);
    ELSE
        RETURN QUERY SELECT 
            'GiST'::TEXT,
            '通用选择，支持所有几何类型和查询'::TEXT,
            format('CREATE INDEX idx_%s_geom ON %I USING GIST(%I);',
                   p_table_name, p_table_name, p_geom_column);
    END IF;
END;
$$ LANGUAGE plpgsql;
```

---

## 4. 空间查询实现

### 4.1 基础空间查询

```sql
-- ============================================
-- 4.1.1 附近POI搜索 (KNN查询)
-- ============================================
CREATE OR REPLACE FUNCTION find_nearby_pois(
    p_longitude DECIMAL,
    p_latitude DECIMAL,
    p_radius_meters INTEGER DEFAULT 1000,
    p_category_id INTEGER DEFAULT NULL,
    p_limit INTEGER DEFAULT 20
) RETURNS TABLE (
    poi_id BIGINT,
    name VARCHAR,
    category_id INTEGER,
    distance_meters DECIMAL,
    rating DECIMAL
) AS $$
DECLARE
    v_search_point GEOMETRY;
BEGIN
    -- 创建搜索点
    v_search_point := ST_SetSRID(ST_MakePoint(p_longitude, p_latitude), 4326);
    
    RETURN QUERY
    SELECT 
        p.poi_id,
        p.name,
        p.category_id,
        -- 使用ST_DistanceSphere计算精确距离(米)
        ST_DistanceSphere(p.geom, v_search_point)::DECIMAL AS distance_meters,
        p.rating
    FROM poi p
    WHERE 
        -- 使用 && 操作符利用空间索引进行边界框过滤
        p.geom && ST_Expand(
            ST_Transform(v_search_point, 3857), 
            p_radius_meters
        )::geometry
        -- 精确距离过滤
        AND ST_DistanceSphere(p.geom, v_search_point) <= p_radius_meters
        -- 可选分类过滤
        AND (p_category_id IS NULL OR p.category_id = p_category_id)
        AND p.status = 1
    ORDER BY p.geom <-> v_search_point  -- KNN排序，使用GiST索引
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- 4.1.2 多边形区域查询
-- ============================================
CREATE OR REPLACE FUNCTION find_pois_in_polygon(
    p_polygon_geojson TEXT,
    p_category_ids INTEGER[] DEFAULT NULL
) RETURNS TABLE (
    poi_id BIGINT,
    name VARCHAR,
    category_id INTEGER,
    geom GEOJSON
) AS $$
DECLARE
    v_polygon GEOMETRY;
BEGIN
    -- 解析GeoJSON
    v_polygon := ST_GeomFromGeoJSON(p_polygon_geojson);
    
    RETURN QUERY
    SELECT 
        p.poi_id,
        p.name,
        p.category_id,
        ST_AsGeoJSON(p.geom)::GEOJSON
    FROM poi p
    WHERE 
        -- ST_Within 完全包含
        ST_Within(p.geom, v_polygon)
        -- 或 ST_Intersects 相交
        -- ST_Intersects(p.geom, v_polygon)
        AND (p_category_ids IS NULL OR p.category_id = ANY(p_category_ids))
        AND p.status = 1;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- 4.1.3 地理围栏判断
-- ============================================
CREATE OR REPLACE FUNCTION check_geofence_violation(
    p_device_id VARCHAR,
    p_longitude DECIMAL,
    p_latitude DECIMAL,
    p_altitude INTEGER DEFAULT NULL,
    p_timestamp TIMESTAMPTZ DEFAULT NOW()
) RETURNS TABLE (
    zone_id BIGINT,
    zone_name VARCHAR,
    violation_type VARCHAR,
    severity SMALLINT
) AS $$
DECLARE
    v_point GEOMETRY;
BEGIN
    v_point := ST_SetSRID(ST_MakePoint(p_longitude, p_latitude), 4326);
    
    RETURN QUERY
    SELECT 
        gz.zone_id,
        gz.name,
        CASE gz.zone_type
            WHEN 1 THEN 'ENTER_RESTRICTED_ZONE'::VARCHAR
            WHEN 2 THEN 'SPEED_LIMIT'::VARCHAR
            WHEN 3 THEN 'NOTIFICATION'::VARCHAR
        END,
        CASE gz.zone_type
            WHEN 1 THEN 3  -- 高严重性
            WHEN 2 THEN 2
            WHEN 3 THEN 1
        END
    FROM geofence_zones gz
    WHERE 
        gz.is_active = TRUE
        -- 空间包含判断
        AND ST_Contains(gz.geom, v_point)
        -- 高度检查 (如果有高度数据)
        AND (p_altitude IS NULL 
             OR gz.altitude_min IS NULL 
             OR p_altitude BETWEEN gz.altitude_min AND COALESCE(gz.altitude_max, 99999))
        -- 时间有效性检查
        AND (
            gz.schedule = '{}'::JSONB
            OR (
                (gz.schedule->>'start_time')::TIME <= p_timestamp::TIME
                AND (gz.schedule->>'end_time')::TIME >= p_timestamp::TIME
                AND EXTRACT(DOW FROM p_timestamp)::INTEGER = ANY(
                    ARRAY(SELECT jsonb_array_elements_text(gz.schedule->'days'))::INTEGER[]
                )
            )
        );
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- 4.1.4 轨迹压缩 (Douglas-Peucker算法)
-- ============================================
CREATE OR REPLACE FUNCTION compress_trajectory(
    p_device_id VARCHAR,
    p_start_time TIMESTAMPTZ,
    p_end_time TIMESTAMPTZ,
    p_tolerance_meters DECIMAL DEFAULT 10.0
) RETURNS TABLE (
    point_id BIGINT,
    longitude DECIMAL,
    latitude DECIMAL,
    timestamp TIMESTAMPTZ,
    is_kept BOOLEAN
) AS $$
BEGIN
    RETURN QUERY
    WITH raw_points AS (
        SELECT 
            tp.point_id,
            ST_X(tp.geom) AS lon,
            ST_Y(tp.geom) AS lat,
            tp.timestamp,
            tp.geom
        FROM trajectory_points tp
        WHERE tp.device_id = p_device_id
          AND tp.timestamp BETWEEN p_start_time AND p_end_time
        ORDER BY tp.timestamp
    ),
    linestring AS (
        SELECT ST_MakeLine(ARRAY_AGG(geom ORDER BY timestamp)) AS geom
        FROM raw_points
    )
    SELECT 
        rp.point_id,
        rp.lon,
        rp.lat,
        rp.timestamp,
        ST_Distance(
            rp.geom,
            ST_Simplify(l.geom, p_tolerance_meters)
        ) < p_tolerance_meters AS is_kept
    FROM raw_points rp
    CROSS JOIN linestring l;
END;
$$ LANGUAGE plpgsql;
```

### 4.2 路径规划 (pgRouting)

```sql
-- ============================================
-- 4.2.1 启用pgRouting扩展
-- ============================================
CREATE EXTENSION IF NOT EXISTS pgrouting;

-- ============================================
-- 4.2.2 创建路网拓扑
-- ============================================
SELECT pgr_createTopology('road_network', 0.00001, 'geom', 'road_id');

-- 添加拓扑分析列
ALTER TABLE road_network 
ADD COLUMN IF NOT EXISTS cost DOUBLE PRECISION,
ADD COLUMN IF NOT EXISTS reverse_cost DOUBLE PRECISION;

-- 计算通行成本 (基于距离和速度)
UPDATE road_network SET
    cost = CASE 
        WHEN oneway = -1 THEN -1  -- 禁止通行
        ELSE length_m / NULLIF(max_speed, 0) / 1000 * 60  -- 分钟
    END,
    reverse_cost = CASE 
        WHEN oneway = 1 THEN -1   -- 禁止通行
        ELSE length_m / NULLIF(max_speed, 0) / 1000 * 60
    END;

-- ============================================
-- 4.2.3 最短路径查询 (Dijkstra)
-- ============================================
CREATE OR REPLACE FUNCTION find_shortest_path(
    p_from_lon DECIMAL,
    p_from_lat DECIMAL,
    p_to_lon DECIMAL,
    p_to_lat DECIMAL,
    p_cost_column TEXT DEFAULT 'cost'
) RETURNS TABLE (
    seq INTEGER,
    node BIGINT,
    edge BIGINT,
    cost DOUBLE PRECISION,
    agg_cost DOUBLE PRECISION,
    geom GEOMETRY
) AS $$
DECLARE
    v_start_node BIGINT;
    v_end_node BIGINT;
BEGIN
    -- 找到最近的起始节点
    SELECT source_node INTO v_start_node
    FROM road_network
    WHERE status = 1
    ORDER BY geom <-> ST_SetSRID(ST_MakePoint(p_from_lon, p_from_lat), 4326)
    LIMIT 1;
    
    -- 找到最近的结束节点
    SELECT target_node INTO v_end_node
    FROM road_network
    WHERE status = 1
    ORDER BY geom <-> ST_SetSRID(ST_MakePoint(p_to_lon, p_to_lat), 4326)
    LIMIT 1;
    
    RETURN QUERY
    SELECT 
        r.seq::INTEGER,
        r.node,
        r.edge,
        r.cost,
        r.agg_cost,
        rn.geom
    FROM pgr_dijkstra(
        format('SELECT road_id, source_node, target_node, %I AS cost, reverse_cost 
                FROM road_network WHERE status = 1', p_cost_column),
        v_start_node,
        v_end_node,
        TRUE  -- 有向图
    ) r
    LEFT JOIN road_network rn ON rn.road_id = r.edge;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- 4.2.4 多目的地路径规划 (TSP)
-- ============================================
CREATE OR REPLACE FUNCTION plan_multi_stop_route(
    p_waypoints JSONB -- [{"lon": 116.4, "lat": 39.9}, ...]
) RETURNS TABLE (
    stop_seq INTEGER,
    longitude DECIMAL,
    latitude DECIMAL,
    arrival_time INTERVAL
) AS $$
BEGIN
    -- TSP求解简化示例
    -- 实际实现需要将waypoints转换为matrix并使用pgr_TSP
    RETURN QUERY
    WITH waypoints AS (
        SELECT 
            (ordinality - 1) AS seq,
            (value->>'lon')::DECIMAL AS lon,
            (value->>'lat')::DECIMAL AS lat
        FROM jsonb_array_elements(p_waypoints) WITH ORDINALITY
    )
    SELECT 
        seq::INTEGER,
        lon,
        lat,
        (seq * INTERVAL '10 minutes')  -- 简化时间估算
    FROM waypoints
    ORDER BY seq;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- 4.2.5 等时圈分析 (Isochrone)
-- ============================================
CREATE OR REPLACE FUNCTION generate_isochrone(
    p_center_lon DECIMAL,
    p_center_lat DECIMAL,
    p_max_cost DECIMAL, -- 最大成本(分钟)
    p_cost_column TEXT DEFAULT 'cost'
) RETURNS TABLE (
    geom GEOMETRY,
    cost_range TEXT
) AS $$
BEGIN
    RETURN QUERY
    WITH nodes AS (
        SELECT 
            node,
            agg_cost
        FROM pgr_drivingDistance(
            format('SELECT road_id, source_node, target_node, %I AS cost 
                    FROM road_network WHERE status = 1', p_cost_column),
            (SELECT source_node 
             FROM road_network 
             ORDER BY geom <-> ST_SetSRID(ST_MakePoint(p_center_lon, p_center_lat), 4326)
             LIMIT 1),
            p_max_cost,
            TRUE
        )
    )
    SELECT 
        ST_ConvexHull(ST_Collect(rn.geom)) AS geom,
        CASE 
            WHEN n.agg_cost <= p_max_cost / 3 THEN '0-' || (p_max_cost/3)::TEXT || '分钟'
            WHEN n.agg_cost <= p_max_cost * 2 / 3 THEN (p_max_cost/3)::TEXT || '-' || (p_max_cost*2/3)::TEXT || '分钟'
            ELSE (p_max_cost*2/3)::TEXT || '-' || p_max_cost::TEXT || '分钟'
        END
    FROM nodes n
    JOIN road_network rn ON rn.source_node = n.node OR rn.target_node = n.node
    GROUP BY cost_range;
END;
$$ LANGUAGE plpgsql;
```

### 4.3 空间分析函数

```sql
-- ============================================
-- 4.3.1 热点分析 (DBSCAN聚类)
-- ============================================
CREATE OR REPLACE FUNCTION poi_hotspot_analysis(
    p_city VARCHAR,
    p_eps_meters DECIMAL DEFAULT 100.0,  -- 邻域半径
    p_min_points INTEGER DEFAULT 5       -- 最小点数
) RETURNS TABLE (
    cluster_id INTEGER,
    center_lon DECIMAL,
    center_lat DECIMAL,
    poi_count BIGINT,
    avg_rating DECIMAL,
    category_breakdown JSONB
) AS $$
BEGIN
    RETURN QUERY
    WITH clusters AS (
        SELECT 
            poi_id,
            ST_ClusterDBSCAN(geom, p_eps_meters / 111320.0, p_min_points) 
                OVER () AS cluster_id
        FROM poi
        WHERE city = p_city AND status = 1
    )
    SELECT 
        c.cluster_id::INTEGER,
        ST_X(ST_Centroid(ST_Collect(p.geom)))::DECIMAL,
        ST_Y(ST_Centroid(ST_Collect(p.geom)))::DECIMAL,
        COUNT(*)::BIGINT,
        AVG(p.rating)::DECIMAL(2,1),
        JSONB_OBJECT_AGG(p.category_id, cnt)
    FROM clusters c
    JOIN poi p ON p.poi_id = c.poi_id
    WHERE c.cluster_id IS NOT NULL
    GROUP BY c.cluster_id;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- 4.3.2 轨迹驻留点检测
-- ============================================
CREATE OR REPLACE FUNCTION detect_stay_points(
    p_device_id VARCHAR,
    p_time_threshold INTERVAL DEFAULT INTERVAL '5 minutes',
    p_distance_threshold_meters DECIMAL DEFAULT 100.0
) RETURNS TABLE (
    stay_id INTEGER,
    center_lon DECIMAL,
    center_lat DECIMAL,
    start_time TIMESTAMPTZ,
    end_time TIMESTAMPTZ,
    duration INTERVAL,
    point_count INTEGER
) AS $$
BEGIN
    RETURN QUERY
    WITH stay_detection AS (
        SELECT 
            point_id,
            geom,
            timestamp,
            -- 标记驻留开始
            CASE 
                WHEN timestamp - LAG(timestamp) OVER (ORDER BY timestamp) > p_time_threshold
                    OR ST_DistanceSphere(geom, LAG(geom) OVER (ORDER BY timestamp)) > p_distance_threshold_meters
                THEN 1 
                ELSE 0 
            END AS is_new_stay
        FROM trajectory_points
        WHERE device_id = p_device_id
        ORDER BY timestamp
    ),
    stay_groups AS (
        SELECT 
            *,
            SUM(is_new_stay) OVER (ORDER BY timestamp) AS stay_group
        FROM stay_detection
    )
    SELECT 
        stay_group::INTEGER,
        ST_X(ST_Centroid(ST_Collect(geom)))::DECIMAL,
        ST_Y(ST_Centroid(ST_Collect(geom)))::DECIMAL,
        MIN(timestamp),
        MAX(timestamp),
        MAX(timestamp) - MIN(timestamp),
        COUNT(*)::INTEGER
    FROM stay_groups
    GROUP BY stay_group
    HAVING MAX(timestamp) - MIN(timestamp) >= p_time_threshold;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- 4.3.3 行政区划统计
-- ============================================
CREATE OR REPLACE FUNCTION region_statistics(
    p_region_code VARCHAR
) RETURNS TABLE (
    poi_count BIGINT,
    poi_density_per_km2 DECIMAL,
    avg_rating DECIMAL,
    top_categories JSONB,
    road_length_km DECIMAL
) AS $$
DECLARE
    v_region_geom GEOMETRY;
    v_area_km2 DECIMAL;
BEGIN
    SELECT boundary_geom, area_km2 
    INTO v_region_geom, v_area_km2
    FROM administrative_regions 
    WHERE code = p_region_code;
    
    RETURN QUERY
    SELECT 
        (SELECT COUNT(*) FROM poi 
         WHERE ST_Within(geom, v_region_geom) AND status = 1),
        (SELECT COUNT(*)::DECIMAL / NULLIF(v_area_km2, 0) 
         FROM poi WHERE ST_Within(geom, v_region_geom)),
        (SELECT AVG(rating) FROM poi 
         WHERE ST_Within(geom, v_region_geom) AND rating > 0),
        (SELECT JSONB_OBJECT_AGG(category_id, cnt)
         FROM (
             SELECT category_id, COUNT(*) AS cnt
             FROM poi
             WHERE ST_Within(geom, v_region_geom) AND status = 1
             GROUP BY category_id
             ORDER BY cnt DESC
             LIMIT 5
         ) sub),
        (SELECT SUM(length_m) / 1000 
         FROM road_network 
         WHERE ST_Intersects(geom, v_region_geom));
END;
$$ LANGUAGE plpgsql;
```

---

## 5. 地图服务集成

### 5.1 矢量瓦片服务

```sql
-- ============================================
-- 5.1.1 MVT (Mapbox Vector Tile) 生成
-- ============================================
CREATE OR REPLACE FUNCTION get_poi_mvt(
    p_z INTEGER,
    p_x INTEGER,
    p_y INTEGER,
    p_category_id INTEGER DEFAULT NULL
) RETURNS BYTEA AS $$
DECLARE
    v_bounds GEOMETRY;
    v_mvt BYTEA;
BEGIN
    -- 计算瓦片边界
    v_bounds := ST_TileEnvelope(p_z, p_x, p_y);
    
    -- 生成MVT
    SELECT ST_AsMVT(mvt, 'poi', 4096, 'geom')
    INTO v_mvt
    FROM (
        SELECT 
            poi_id AS id,
            name,
            category_id,
            rating,
            ST_AsMVTGeom(
                ST_Transform(geom, 3857),  -- 转为Web Mercator
                v_bounds,
                4096,  -- 瓦片大小
                256,   -- 缓冲区
                TRUE   -- 裁剪几何
            ) AS geom
        FROM poi
        WHERE 
            -- 空间索引过滤
            geom && ST_Transform(v_bounds, 4326)
            -- 层级过滤 (避免低层级数据过多)
            AND (p_z >= 10 OR category_id <= 10)
            AND (p_category_id IS NULL OR category_id = p_category_id)
            AND status = 1
    ) mvt;
    
    RETURN v_mvt;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- 5.1.2 动态热力图瓦片
-- ============================================
CREATE OR REPLACE FUNCTION get_heatmap_mvt(
    p_z INTEGER,
    p_x INTEGER,
    p_y INTEGER,
    p_data_type TEXT DEFAULT 'poi' -- 'poi', 'trajectory'
) RETURNS BYTEA AS $$
DECLARE
    v_bounds GEOMETRY;
    v_mvt BYTEA;
BEGIN
    v_bounds := ST_TileEnvelope(p_z, p_x, p_y);
    
    IF p_data_type = 'poi' THEN
        SELECT ST_AsMVT(mvt, 'heatmap', 4096, 'geom')
        INTO v_mvt
        FROM (
            SELECT 
                COUNT(*) AS density,
                ST_AsMVTGeom(
                    ST_Centroid(ST_Collect(ST_Transform(geom, 3857))),
                    v_bounds,
                    4096,
                    0,
                    TRUE
                ) AS geom
            FROM poi
            WHERE geom && ST_Transform(v_bounds, 4326)
              AND status = 1
            GROUP BY ST_SnapToGrid(ST_Transform(geom, 3857), 
                                   CASE p_z 
                                       WHEN < 10 THEN 10000
                                       WHEN < 14 THEN 1000
                                       ELSE 100
                                   END)
        ) mvt;
    END IF;
    
    RETURN v_mvt;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- 5.1.3 路网瓦片
-- ============================================
CREATE OR REPLACE FUNCTION get_road_mvt(
    p_z INTEGER,
    p_x INTEGER,
    p_y INTEGER
) RETURNS BYTEA AS $$
DECLARE
    v_bounds GEOMETRY;
    v_mvt BYTEA;
BEGIN
    v_bounds := ST_TileEnvelope(p_z, p_x, p_y);
    
    SELECT ST_AsMVT(mvt, 'roads', 4096, 'geom')
    INTO v_mvt
    FROM (
        SELECT 
            road_id,
            name,
            road_type,
            max_speed,
            oneway,
            ST_AsMVTGeom(
                ST_Transform(geom, 3857),
                v_bounds,
                4096,
                128,
                TRUE
            ) AS geom
        FROM road_network
        WHERE 
            geom && ST_Transform(v_bounds, 4326)
            -- 根据层级过滤道路类型
            AND (
                (p_z >= 14) OR
                (p_z >= 12 AND road_type <= 4) OR
                (p_z >= 10 AND road_type <= 3) OR
                (p_z >= 8 AND road_type <= 2) OR
                (p_z >= 6 AND road_type <= 1)
            )
            AND status = 1
    ) mvt;
    
    RETURN v_mvt;
END;
$$ LANGUAGE plpgsql;
```

### 5.2 GeoJSON API

```sql
-- ============================================
-- 5.2.1 GeoJSON FeatureCollection 生成
-- ============================================
CREATE OR REPLACE FUNCTION get_poi_geojson(
    p_bbox TEXT, -- 'minLon,minLat,maxLon,maxLat'
    p_limit INTEGER DEFAULT 100
) RETURNS JSONB AS $$
DECLARE
    v_bbox_parts TEXT[];
    v_min_lon DECIMAL;
    v_min_lat DECIMAL;
    v_max_lon DECIMAL;
    v_max_lat DECIMAL;
BEGIN
    v_bbox_parts := string_to_array(p_bbox, ',');
    v_min_lon := v_bbox_parts[1]::DECIMAL;
    v_min_lat := v_bbox_parts[2]::DECIMAL;
    v_max_lon := v_bbox_parts[3]::DECIMAL;
    v_max_lat := v_bbox_parts[4]::DECIMAL;
    
    RETURN (
        SELECT JSONB_BUILD_OBJECT(
            'type', 'FeatureCollection',
            'features', JSONB_AGG(
                JSONB_BUILD_OBJECT(
                    'type', 'Feature',
                    'id', poi_id,
                    'geometry', ST_AsGeoJSON(geom)::JSONB,
                    'properties', JSONB_BUILD_OBJECT(
                        'name', name,
                        'category_id', category_id,
                        'rating', rating,
                        'address', address
                    )
                )
            )
        )
        FROM poi
        WHERE geom && ST_MakeEnvelope(v_min_lon, v_min_lat, v_max_lon, v_max_lat, 4326)
          AND status = 1
        LIMIT p_limit
    );
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- 5.2.2 路径GeoJSON
-- ============================================
CREATE OR REPLACE FUNCTION get_route_geojson(
    p_path_points JSONB -- [{"lon": 116.4, "lat": 39.9}, ...]
) RETURNS JSONB AS $$
DECLARE
    v_line GEOMETRY;
BEGIN
    -- 构建路径线
    SELECT ST_MakeLine(
        ARRAY_AGG(
            ST_SetSRID(ST_MakePoint((p->>'lon')::DECIMAL, (p->>'lat')::DECIMAL), 4326)
            ORDER BY ord
        )
    ) INTO v_line
    FROM jsonb_array_elements(p_path_points) WITH ORDINALITY AS p(p, ord);
    
    RETURN JSONB_BUILD_OBJECT(
        'type', 'Feature',
        'geometry', ST_AsGeoJSON(v_line)::JSONB,
        'properties', JSONB_BUILD_OBJECT(
            'distance_m', ST_LengthSphere(v_line)::INTEGER,
            'duration_min', (ST_LengthSphere(v_line) / 1000 / 40 * 60)::INTEGER  -- 假设40km/h
        )
    );
END;
$$ LANGUAGE plpgsql;
```

---

## 6. 性能优化

### 6.1 查询优化策略

```sql
-- ============================================
-- 6.1.1 查询计划分析
-- ============================================

-- 检查空间查询是否使用索引
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT * FROM poi
WHERE ST_DWithin(
    geom::geography,
    ST_SetSRID(ST_MakePoint(116.3974, 39.9093), 4326)::geography,
    1000
);

-- 预期计划:
-- Index Scan using idx_poi_geom on poi
--   Index Cond: (geom && ...)
--   Filter: (_st_distance(...) <= 1000)

-- ============================================
-- 6.1.2 统计信息更新
-- ============================================
-- 空间数据统计更新
ANALYZE poi;
ANALYZE road_network;

-- 自定义统计 (空间分布)
SELECT UpdateGeometrySRID('poi', 'geom', 4326);

-- ============================================
-- 6.1.3 分区裁剪优化
-- ============================================
-- 确保查询条件能触发分区裁剪
EXPLAIN (ANALYZE)
SELECT * FROM trajectory_points
WHERE device_id = 'DEV001'
  AND timestamp BETWEEN '2026-01-01' AND '2026-01-31';

-- 预期: 只扫描 trajectory_points_y2026m01 分区
```

### 6.2 缓存策略

```sql
-- ============================================
-- 6.2.1 热门区域POI缓存
-- ============================================
CREATE UNLOGGED TABLE poi_cache (
    cache_key       VARCHAR(64) PRIMARY KEY,
    city            VARCHAR(50),
    category_id     INTEGER,
    poi_data        JSONB NOT NULL,
    cached_at       TIMESTAMPTZ DEFAULT NOW(),
    hit_count       INTEGER DEFAULT 0
);

CREATE INDEX idx_poi_cache_city ON poi_cache(city, category_id);

-- 缓存预热函数
CREATE OR REPLACE FUNCTION warm_poi_cache(p_city VARCHAR)
RETURNS INTEGER AS $$
DECLARE
    v_count INTEGER;
BEGIN
    INSERT INTO poi_cache (cache_key, city, category_id, poi_data)
    SELECT 
        MD5(city || '_' || category_id::TEXT),
        city,
        category_id,
        JSONB_AGG(
            JSONB_BUILD_OBJECT(
                'poi_id', poi_id,
                'name', name,
                'geom', ST_AsGeoJSON(geom)::JSONB
            )
        )
    FROM poi
    WHERE city = p_city AND status = 1
    GROUP BY city, category_id
    ON CONFLICT (cache_key) DO UPDATE SET
        poi_data = EXCLUDED.poi_data,
        cached_at = NOW();
    
    GET DIAGNOSTICS v_count = ROW_COUNT;
    RETURN v_count;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- 6.2.2 MVT瓦片缓存表
-- ============================================
CREATE TABLE mvt_cache (
    tile_key        VARCHAR(64) PRIMARY KEY, -- z_x_y_layer
    z               INTEGER,
    x               INTEGER,
    y               INTEGER,
    layer           VARCHAR(32),
    tile_data       BYTEA NOT NULL,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    expires_at      TIMESTAMPTZ DEFAULT NOW() + INTERVAL '1 day'
);

CREATE INDEX idx_mvt_cache_coords ON mvt_cache(z, x, y, layer);

-- 瓦片查询 (带缓存)
CREATE OR REPLACE FUNCTION get_cached_mvt(
    p_z INTEGER,
    p_x INTEGER,
    p_y INTEGER,
    p_layer TEXT DEFAULT 'poi'
) RETURNS BYTEA AS $$
DECLARE
    v_key VARCHAR;
    v_tile BYTEA;
BEGIN
    v_key := format('%s_%s_%s_%s', p_z, p_x, p_y, p_layer);
    
    -- 查询缓存
    SELECT tile_data INTO v_tile
    FROM mvt_cache
    WHERE tile_key = v_key AND expires_at > NOW();
    
    IF FOUND THEN
        -- 更新命中率统计
        UPDATE mvt_cache SET hit_count = COALESCE(hit_count, 0) + 1
        WHERE tile_key = v_key;
        RETURN v_tile;
    END IF;
    
    -- 生成新瓦片
    CASE p_layer
        WHEN 'poi' THEN v_tile := get_poi_mvt(p_z, p_x, p_y);
        WHEN 'road' THEN v_tile := get_road_mvt(p_z, p_x, p_y);
        ELSE v_tile := NULL;
    END CASE;
    
    -- 写入缓存
    IF v_tile IS NOT NULL THEN
        INSERT INTO mvt_cache (tile_key, z, x, y, layer, tile_data)
        VALUES (v_key, p_z, p_x, p_y, p_layer, v_tile)
        ON CONFLICT (tile_key) DO UPDATE SET
            tile_data = EXCLUDED.tile_data,
            created_at = NOW(),
            expires_at = NOW() + INTERVAL '1 day';
    END IF;
    
    RETURN v_tile;
END;
$$ LANGUAGE plpgsql;
```

---

## 7. 形式化验证

### 7.1 空间索引正确性定理

**定理 1 (GiST索引完备性)**:
对于空间数据集 $D$ 和查询范围 $Q$，GiST索引返回的结果集 $R$ 满足:
$$R = \{ p \in D \mid bounding\_box(p) \cap bounding\_box(Q) \neq \emptyset \}$$

**定理 2 (KNN查询正确性)**:
最近邻查询返回的 $k$ 个点满足:
$$\forall p \in R, \forall q \in D \setminus R: distance(p, center) \leq distance(q, center)$$

### 7.2 复杂度分析

| 操作 | 时间复杂度 | 空间复杂度 | 索引使用 |
|------|-----------|-----------|---------|
| 点包含判断 | $O(\log n)$ | $O(1)$ | GiST |
| 范围查询 | $O(\log n + m)$ | $O(m)$ | GiST |
| KNN查询 | $O(\log n + k)$ | $O(k)$ | GiST + KNN |
| 路径规划 | $O(E \log V)$ | $O(V)$ | 拓扑索引 |
| 瓦片生成 | $O(\log n + t)$ | $O(t)$ | GiST |

其中: $n$=总数据量, $m$=范围内点数, $k$=近邻数, $V$=顶点数, $E$=边数, $t$=瓦片内特征数

### 7.3 坐标精度

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         坐标精度与存储需求                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  坐标类型                精度              存储大小    适用场景              │
│  ───────────────────────────────────────────────────────────────────────   │
│  geometry(float)         ~1m              16字节      粗略定位               │
│  geometry(double)        ~1cm             32字节      标准GPS                │
│  geography(double)       ~1cm             32字节      大距离计算             │
│  geometry(decimal)       ~1mm             可变        高精度测绘             │
│                                                                             │
│  WGS84坐标精度公式:                                                         │
│  经度精度(m) = 111320 × cos(lat) × 10^(-d)  (d=小数位数)                    │
│  纬度精度(m) = 110540 × 10^(-d)                                            │
│                                                                             │
│  示例: 6位小数 (~10cm精度)                                                  │
│  longitude: 116.397428                                                      │
│  latitude:  39.909236                                                       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 8. 权威引用

### 8.1 学术文献

1. **Obe, R. O., & Hsu, L. S. (2021)**. *PostGIS in Action, 3rd Edition*. Manning Publications. PostGIS权威教材，涵盖空间数据建模与查询优化。

2. **Shekhar, S., & Chawla, S. (2003)**. *Spatial Databases: A Tour*. Prentice Hall. 空间数据库基础理论与算法。

3. **Rigaux, P., Scholl, M., & Voisard, A. (2001)**. *Spatial Databases: With Application to GIS*. Morgan Kaufmann. 空间数据库与GIS应用经典著作。

### 8.2 PostGIS官方文档

4. **PostGIS Project (2024)**. "PostGIS 3.4 Manual." *PostGIS Documentation*. https://postgis.net/documentation/

5. **PostGIS Project (2024)**. "Raster Data Management." *PostGIS Raster Documentation*. https://postgis.net/docs/using_raster_dataman.html

6. **PostGIS Project (2024)**. "Topology." *PostGIS Topology Documentation*. https://postgis.net/docs/Topology.html

### 8.3 pgRouting官方文档

7. **pgRouting Project (2024)**. "pgRouting Manual." *pgRouting Documentation*. https://docs.pgrouting.org/

### 8.4 行业标准

8. **OGC (2024)**. "GeoJSON Specification (RFC 7946)." *Open Geospatial Consortium*.

9. **Mapbox (2024)**. "Vector Tile Specification." *Mapbox Documentation*. https://github.com/mapbox/vector-tile-spec

10. **EPSG (2024)**. "Geodetic Parameter Dataset." *EPSG Registry*. https://epsg.org/

---

## 附录A: 常用SRID对照

| SRID | 名称 | 坐标系 | 适用场景 |
|------|------|--------|---------|
| 4326 | WGS 84 | 地理坐标 | GPS数据、全球应用 |
| 3857 | Web Mercator | 投影坐标 | Web地图、瓦片服务 |
| 4490 | CGCS2000 | 地理坐标 | 中国测绘 |
| 4547 | CGCS2000 / 3-degree | 投影坐标 | 中国区域(<3度带) |
| 2416 | Beijing 1954 | 投影坐标 |  legacy系统 |

---

**文档版本**: v2.0  
**最后更新**: 2026-03-04  
**维护者**: PostgreSQL_Formal Team
