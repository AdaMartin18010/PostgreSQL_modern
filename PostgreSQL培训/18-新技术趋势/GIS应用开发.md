# PostgreSQL GIS 应用开发

> **更新时间**: 2025 年 1 月
> **技术版本**: PostgreSQL 18+ with PostGIS 3.4+
> **文档编号**: 03-03-TREND-14

## 📑 概述

PostgreSQL 结合 PostGIS 扩展提供了强大的地理信息系统（GIS）开发能力，支持空间数据类型、空间索引、空间函数和空间分析，广泛应用于地图应用、位置服务、地理分析等场景。

## 🎯 核心价值

- **空间数据类型**：支持点、线、面等空间数据类型
- **空间索引**：高效的 GIST 和 SP-GiST 空间索引
- **空间函数**：丰富的空间计算和分析函数
- **坐标系统**：支持多种坐标系统和投影
- **高性能查询**：优化的空间查询性能

## 📚 目录

- [PostgreSQL GIS 应用开发](#postgresql-gis-应用开发)
  - [📑 概述](#-概述)
  - [🎯 核心价值](#-核心价值)
  - [📚 目录](#-目录)
  - [1. GIS 基础](#1-gis-基础)
    - [1.1 PostGIS 安装](#11-postgis-安装)
    - [1.2 空间数据类型](#12-空间数据类型)
    - [1.3 坐标系统](#13-坐标系统)
  - [2. 空间数据存储](#2-空间数据存储)
    - [2.1 创建空间表](#21-创建空间表)
    - [2.2 插入空间数据](#22-插入空间数据)
    - [2.3 空间数据导入](#23-空间数据导入)
  - [3. 空间索引](#3-空间索引)
    - [3.1 GIST 索引](#31-gist-索引)
    - [3.2 SP-GiST 索引](#32-sp-gist-索引)
    - [3.3 索引优化](#33-索引优化)
  - [4. 空间查询](#4-空间查询)
    - [4.1 空间关系查询](#41-空间关系查询)
    - [4.2 空间距离查询](#42-空间距离查询)
    - [4.3 空间聚合查询](#43-空间聚合查询)
  - [5. 空间分析](#5-空间分析)
    - [5.1 缓冲区分析](#51-缓冲区分析)
    - [5.2 叠加分析](#52-叠加分析)
    - [5.3 网络分析](#53-网络分析)
  - [6. 地图可视化](#6-地图可视化)
    - [6.1 GeoJSON 输出](#61-geojson-输出)
    - [6.2 KML 输出](#62-kml-输出)
    - [6.3 地图服务集成](#63-地图服务集成)
  - [7. 性能优化](#7-性能优化)
    - [7.1 索引优化](#71-索引优化)
    - [7.2 查询优化](#72-查询优化)
    - [7.3 存储优化](#73-存储优化)
  - [8. 最佳实践](#8-最佳实践)
    - [8.1 设计建议](#81-设计建议)
    - [8.2 查询建议](#82-查询建议)
    - [8.3 性能优化建议](#83-性能优化建议)
  - [9. 实际案例](#9-实际案例)
    - [9.1 案例：地图应用开发](#91-案例地图应用开发)
    - [9.2 案例：地理分析系统](#92-案例地理分析系统)
  - [📊 总结](#-总结)

---

## 1. GIS 基础

### 1.1 PostGIS 安装

```sql
-- PostGIS 安装
-- 1. 安装 PostGIS 扩展
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;
CREATE EXTENSION IF NOT EXISTS postgis_raster;

-- 2. 验证安装
SELECT PostGIS_Version();
SELECT PostGIS_Full_Version();

-- 3. 查看 PostGIS 函数
SELECT proname, prosrc
FROM pg_proc
WHERE proname LIKE 'ST_%'
LIMIT 10;
```

### 1.2 空间数据类型

```sql
-- PostGIS 空间数据类型
-- 1. 点（Point）
SELECT ST_GeomFromText('POINT(116.3974 39.9093)', 4326) AS beijing_point;

-- 2. 线（LineString）
SELECT ST_GeomFromText('LINESTRING(116.3974 39.9093, 116.4074 39.9193)', 4326) AS line;

-- 3. 面（Polygon）
SELECT ST_GeomFromText('POLYGON((116.3974 39.9093, 116.4074 39.9093, 116.4074 39.9193, 116.3974 39.9193, 116.3974 39.9093))', 4326) AS polygon;

-- 4. 多点（MultiPoint）
SELECT ST_GeomFromText('MULTIPOINT(116.3974 39.9093, 116.4074 39.9193)', 4326) AS multipoint;

-- 5. 多线（MultiLineString）
SELECT ST_GeomFromText('MULTILINESTRING((116.3974 39.9093, 116.4074 39.9193))', 4326) AS multilinestring;

-- 6. 多面（MultiPolygon）
SELECT ST_GeomFromText('MULTIPOLYGON(((116.3974 39.9093, 116.4074 39.9093, 116.4074 39.9193, 116.3974 39.9193, 116.3974 39.9093)))', 4326) AS multipolygon;
```

### 1.3 坐标系统

```sql
-- PostGIS 坐标系统
-- 1. 查看坐标系统
SELECT srid, auth_name, auth_srid, proj4text
FROM spatial_ref_sys
WHERE srid = 4326;  -- WGS84

-- 2. 坐标转换
SELECT ST_Transform(
    ST_GeomFromText('POINT(116.3974 39.9093)', 4326),
    3857  -- Web Mercator
) AS transformed_point;

-- 3. 常用坐标系统
-- 4326: WGS84 (GPS 坐标)
-- 3857: Web Mercator (Web 地图)
-- 4490: CGCS2000 (中国国家坐标系)
-- 2154: RGF93 / Lambert-93 (法国)
```

---

## 2. 空间数据存储

### 2.1 创建空间表

```sql
-- 创建空间表
-- 1. 创建点表
CREATE TABLE locations (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    geom GEOMETRY(POINT, 4326)  -- 点类型，WGS84 坐标系
);

-- 2. 创建线表
CREATE TABLE roads (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    geom GEOMETRY(LINESTRING, 4326)  -- 线类型
);

-- 3. 创建面表
CREATE TABLE regions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    geom GEOMETRY(POLYGON, 4326)  -- 面类型
);

-- 4. 创建通用几何表
CREATE TABLE geometries (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    geom GEOMETRY(GEOMETRY, 4326)  -- 通用几何类型
);
```

### 2.2 插入空间数据

```sql
-- 插入空间数据
-- 1. 使用 WKT（Well-Known Text）插入
INSERT INTO locations (name, geom)
VALUES (
    'Beijing',
    ST_GeomFromText('POINT(116.3974 39.9093)', 4326)
);

-- 2. 使用 WKB（Well-Known Binary）插入
INSERT INTO locations (name, geom)
VALUES (
    'Shanghai',
    ST_GeomFromWKB(
        ST_AsBinary(ST_GeomFromText('POINT(121.4737 31.2304)', 4326)),
        4326
    )
);

-- 3. 使用经纬度直接插入
INSERT INTO locations (name, geom)
VALUES (
    'Guangzhou',
    ST_SetSRID(ST_MakePoint(113.2644, 23.1291), 4326)
);

-- 4. 批量插入
INSERT INTO locations (name, geom)
VALUES
    ('Shenzhen', ST_SetSRID(ST_MakePoint(114.0579, 22.5431), 4326)),
    ('Hangzhou', ST_SetSRID(ST_MakePoint(120.1551, 30.2741), 4326)),
    ('Chengdu', ST_SetSRID(ST_MakePoint(104.0668, 30.5728), 4326));
```

### 2.3 空间数据导入

```sql
-- 空间数据导入
-- 1. 使用 shp2pgsql 导入 Shapefile
-- shp2pgsql -s 4326 -I cities.shp public.cities | psql -d mydb

-- 2. 使用 ogr2ogr 导入
-- ogr2ogr -f "PostgreSQL" PG:"dbname=mydb user=postgres" cities.shp -nln cities -lco GEOMETRY_NAME=geom

-- 3. 使用 COPY 导入 GeoJSON
-- 需要先转换为 PostGIS 格式

-- 4. 使用 PostGIS 函数导入
INSERT INTO locations (name, geom)
SELECT
    properties->>'name' AS name,
    ST_GeomFromGeoJSON(geometry) AS geom
FROM jsonb_array_elements(
    '[
        {
            "type": "Feature",
            "properties": {"name": "Beijing"},
            "geometry": {
                "type": "Point",
                "coordinates": [116.3974, 39.9093]
            }
        }
    ]'::jsonb
) AS feature;
```

---

## 3. 空间索引

### 3.1 GIST 索引

```sql
-- GIST 索引（推荐用于空间数据）
-- 1. 创建 GIST 索引
CREATE INDEX idx_locations_geom ON locations USING GIST (geom);

-- 2. 创建空间索引（自动使用 GIST）
CREATE SPATIAL INDEX idx_locations_geom ON locations (geom);

-- 3. 查看索引信息
SELECT
    indexname,
    indexdef
FROM pg_indexes
WHERE tablename = 'locations';

-- 4. 分析索引使用情况
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM locations
WHERE ST_DWithin(
    geom,
    ST_GeomFromText('POINT(116.3974 39.9093)', 4326),
    0.1
);
```

### 3.2 SP-GiST 索引

```sql
-- SP-GiST 索引（适用于某些空间查询）
-- 1. 创建 SP-GiST 索引
CREATE INDEX idx_locations_geom_spgist ON locations USING SPGIST (geom);

-- 2. 查看索引使用情况
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM locations
WHERE geom && ST_MakeEnvelope(116.0, 39.0, 117.0, 40.0, 4326);
```

### 3.3 索引优化

```sql
-- 空间索引优化
-- 1. 使用覆盖索引
CREATE INDEX idx_locations_geom_name ON locations USING GIST (geom) INCLUDE (name);

-- 2. 部分索引（只索引特定区域）
CREATE INDEX idx_locations_geom_beijing ON locations USING GIST (geom)
WHERE ST_Within(geom, ST_MakeEnvelope(116.0, 39.0, 117.0, 40.0, 4326));

-- 3. 索引维护
VACUUM ANALYZE locations;
REINDEX INDEX idx_locations_geom;
```

---

## 4. 空间查询

### 4.1 空间关系查询

```sql
-- 空间关系查询
-- 1. 包含（Contains）
SELECT * FROM regions
WHERE ST_Contains(geom, ST_GeomFromText('POINT(116.3974 39.9093)', 4326));

-- 2. 相交（Intersects）
SELECT * FROM roads
WHERE ST_Intersects(geom, ST_GeomFromText('POLYGON((116.0 39.0, 117.0 39.0, 117.0 40.0, 116.0 40.0, 116.0 39.0))', 4326));

-- 3. 接触（Touches）
SELECT * FROM regions
WHERE ST_Touches(geom, ST_GeomFromText('POLYGON((116.0 39.0, 117.0 39.0, 117.0 40.0, 116.0 40.0, 116.0 39.0))', 4326));

-- 4. 重叠（Overlaps）
SELECT * FROM regions
WHERE ST_Overlaps(geom, ST_GeomFromText('POLYGON((116.0 39.0, 117.0 39.0, 117.0 40.0, 116.0 40.0, 116.0 39.0))', 4326));

-- 5. 在内部（Within）
SELECT * FROM locations
WHERE ST_Within(geom, ST_GeomFromText('POLYGON((116.0 39.0, 117.0 39.0, 117.0 40.0, 116.0 40.0, 116.0 39.0))', 4326));
```

### 4.2 空间距离查询

```sql
-- 空间距离查询
-- 1. 距离计算（度）
SELECT
    name,
    ST_Distance(
        geom,
        ST_GeomFromText('POINT(116.3974 39.9093)', 4326)
    ) AS distance_degrees
FROM locations
ORDER BY distance_degrees
LIMIT 10;

-- 2. 距离计算（米）
SELECT
    name,
    ST_Distance(
        ST_Transform(geom, 3857),  -- 转换为米制坐标系
        ST_Transform(ST_GeomFromText('POINT(116.3974 39.9093)', 4326), 3857)
    ) AS distance_meters
FROM locations
ORDER BY distance_meters
LIMIT 10;

-- 3. 最近邻查询
SELECT
    name,
    ST_Distance(
        ST_Transform(geom, 3857),
        ST_Transform(ST_GeomFromText('POINT(116.3974 39.9093)', 4326), 3857)
    ) AS distance_meters
FROM locations
ORDER BY geom <-> ST_GeomFromText('POINT(116.3974 39.9093)', 4326)
LIMIT 10;

-- 4. 范围内查询（DWithin）
SELECT * FROM locations
WHERE ST_DWithin(
    ST_Transform(geom, 3857),
    ST_Transform(ST_GeomFromText('POINT(116.3974 39.9093)', 4326), 3857),
    10000  -- 10 公里
);
```

### 4.3 空间聚合查询

```sql
-- 空间聚合查询
-- 1. 计算边界框（Bounding Box）
SELECT ST_Envelope(ST_Collect(geom)) AS bounding_box
FROM locations;

-- 2. 计算凸包（Convex Hull）
SELECT ST_ConvexHull(ST_Collect(geom)) AS convex_hull
FROM locations;

-- 3. 计算中心点
SELECT ST_Centroid(ST_Collect(geom)) AS center_point
FROM locations;

-- 4. 按区域聚合
SELECT
    region_id,
    COUNT(*) AS location_count,
    ST_Collect(geom) AS locations_geom
FROM locations
GROUP BY region_id;
```

---

## 5. 空间分析

### 5.1 缓冲区分析

```sql
-- 缓冲区分析
-- 1. 创建点缓冲区
SELECT ST_Buffer(
    ST_GeomFromText('POINT(116.3974 39.9093)', 4326),
    0.01  -- 缓冲区大小（度）
) AS buffer_geom;

-- 2. 创建线缓冲区
SELECT ST_Buffer(
    ST_GeomFromText('LINESTRING(116.3974 39.9093, 116.4074 39.9193)', 4326),
    0.01
) AS buffer_geom;

-- 3. 创建面缓冲区
SELECT ST_Buffer(
    ST_GeomFromText('POLYGON((116.3974 39.9093, 116.4074 39.9093, 116.4074 39.9193, 116.3974 39.9193, 116.3974 39.9093))', 4326),
    0.01
) AS buffer_geom;

-- 4. 使用米制单位创建缓冲区
SELECT ST_Transform(
    ST_Buffer(
        ST_Transform(ST_GeomFromText('POINT(116.3974 39.9093)', 4326), 3857),
        1000  -- 1 公里
    ),
    4326
) AS buffer_geom;
```

### 5.2 叠加分析

```sql
-- 叠加分析
-- 1. 交集（Intersection）
SELECT ST_Intersection(
    ST_GeomFromText('POLYGON((116.0 39.0, 117.0 39.0, 117.0 40.0, 116.0 40.0, 116.0 39.0))', 4326),
    ST_GeomFromText('POLYGON((116.5 39.5, 117.5 39.5, 117.5 40.5, 116.5 40.5, 116.5 39.5))', 4326)
) AS intersection_geom;

-- 2. 并集（Union）
SELECT ST_Union(
    ST_GeomFromText('POLYGON((116.0 39.0, 117.0 39.0, 117.0 40.0, 116.0 40.0, 116.0 39.0))', 4326),
    ST_GeomFromText('POLYGON((116.5 39.5, 117.5 39.5, 117.5 40.5, 116.5 40.5, 116.5 39.5))', 4326)
) AS union_geom;

-- 3. 差集（Difference）
SELECT ST_Difference(
    ST_GeomFromText('POLYGON((116.0 39.0, 117.0 39.0, 117.0 40.0, 116.0 40.0, 116.0 39.0))', 4326),
    ST_GeomFromText('POLYGON((116.5 39.5, 117.5 39.5, 117.5 40.5, 116.5 40.5, 116.5 39.5))', 4326)
) AS difference_geom;

-- 4. 对称差集（SymDifference）
SELECT ST_SymDifference(
    ST_GeomFromText('POLYGON((116.0 39.0, 117.0 39.0, 117.0 40.0, 116.0 40.0, 116.0 39.0))', 4326),
    ST_GeomFromText('POLYGON((116.5 39.5, 117.5 39.5, 117.5 40.5, 116.5 40.5, 116.5 39.5))', 4326)
) AS symdifference_geom;
```

### 5.3 网络分析

```sql
-- 网络分析（使用 pgRouting）
-- 1. 安装 pgRouting
CREATE EXTENSION IF NOT EXISTS pgrouting;

-- 2. 创建路网表
CREATE TABLE road_network (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    source INTEGER,
    target INTEGER,
    cost DOUBLE PRECISION,
    geom GEOMETRY(LINESTRING, 4326)
);

-- 3. 最短路径查询
SELECT * FROM pgr_dijkstra(
    'SELECT id, source, target, cost FROM road_network',
    1,  -- 起点
    10,  -- 终点
    directed := false
);
```

---

## 6. 地图可视化

### 6.1 GeoJSON 输出

```sql
-- GeoJSON 输出
-- 1. 单个几何对象转 GeoJSON
SELECT ST_AsGeoJSON(geom) AS geojson
FROM locations
WHERE id = 1;

-- 2. 多个几何对象转 GeoJSON FeatureCollection
SELECT json_build_object(
    'type', 'FeatureCollection',
    'features', json_agg(
        json_build_object(
            'type', 'Feature',
            'geometry', ST_AsGeoJSON(geom)::json,
            'properties', json_build_object(
                'id', id,
                'name', name
            )
        )
    )
) AS geojson
FROM locations
LIMIT 100;
```

### 6.2 KML 输出

```sql
-- KML 输出
-- 1. 几何对象转 KML
SELECT ST_AsKML(geom) AS kml
FROM locations
WHERE id = 1;

-- 2. 完整的 KML 文档
SELECT '<?xml version="1.0" encoding="UTF-8"?>' ||
       '<kml xmlns="http://www.opengis.net/kml/2.2">' ||
       '<Document>' ||
       '<Placemark>' ||
       '<name>' || name || '</name>' ||
       ST_AsKML(geom) ||
       '</Placemark>' ||
       '</Document>' ||
       '</kml>' AS kml
FROM locations
WHERE id = 1;
```

### 6.3 地图服务集成

```sql
-- 地图服务集成
-- 1. 生成地图瓦片（使用 PostGIS 和 Mapnik）
-- 需要配置 Mapnik 和渲染服务

-- 2. 提供 GeoJSON API
-- 使用 PostgreSQL 的 HTTP 扩展或应用层提供 API

-- 3. 提供 WMS/WFS 服务
-- 使用 GeoServer 或 MapServer 连接 PostgreSQL
```

---

## 7. 性能优化

### 7.1 索引优化

```sql
-- 索引优化
-- 1. 创建空间索引
CREATE INDEX idx_locations_geom ON locations USING GIST (geom);

-- 2. 使用覆盖索引
CREATE INDEX idx_locations_geom_name ON locations USING GIST (geom) INCLUDE (name);

-- 3. 部分索引
CREATE INDEX idx_locations_geom_active ON locations USING GIST (geom)
WHERE active = true;

-- 4. 索引维护
VACUUM ANALYZE locations;
```

### 7.2 查询优化

```sql
-- 查询优化
-- 1. 使用空间索引加速查询
SELECT * FROM locations
WHERE geom && ST_MakeEnvelope(116.0, 39.0, 117.0, 40.0, 4326)
AND ST_Within(geom, ST_MakeEnvelope(116.0, 39.0, 117.0, 40.0, 4326));

-- 2. 使用最近邻操作符
SELECT * FROM locations
ORDER BY geom <-> ST_GeomFromText('POINT(116.3974 39.9093)', 4326)
LIMIT 10;

-- 3. 使用空间连接优化
SELECT
    l.name,
    r.name AS region_name
FROM locations l
JOIN regions r ON ST_Within(l.geom, r.geom);
```

### 7.3 存储优化

```sql
-- 存储优化
-- 1. 使用合适的几何类型
-- 使用 POINT 而不是 GEOMETRY

-- 2. 简化几何对象
UPDATE locations
SET geom = ST_Simplify(geom, 0.001)
WHERE ST_NPoints(geom) > 1000;

-- 3. 压缩几何对象
UPDATE locations
SET geom = ST_Compress(geom);
```

---

## 8. 最佳实践

### 8.1 设计建议

```sql
-- 推荐：使用合适的几何类型
CREATE TABLE locations (
    geom GEOMETRY(POINT, 4326)  -- 明确指定类型
);

-- 推荐：创建空间索引
CREATE INDEX idx_locations_geom ON locations USING GIST (geom);

-- 推荐：使用合适的坐标系统
-- 4326: WGS84 (GPS 坐标)
-- 3857: Web Mercator (Web 地图)

-- 避免：使用通用 GEOMETRY 类型
-- 避免：不创建空间索引
```

### 8.2 查询建议

```sql
-- 推荐：使用空间索引加速查询
WHERE geom && ST_MakeEnvelope(...)

-- 推荐：使用最近邻操作符
ORDER BY geom <-> point

-- 推荐：使用空间连接
JOIN ... ON ST_Within(...)

-- 避免：不使用空间索引
-- 避免：复杂的空间计算
```

### 8.3 性能优化建议

```sql
-- 推荐：创建空间索引
CREATE INDEX idx_locations_geom ON locations USING GIST (geom);

-- 推荐：使用覆盖索引
CREATE INDEX idx_locations_geom_name ON locations USING GIST (geom) INCLUDE (name);

-- 推荐：简化几何对象
UPDATE locations SET geom = ST_Simplify(geom, 0.001);

-- 避免：过度复杂的几何对象
-- 避免：不维护索引
```

---

## 9. 实际案例

### 9.1 案例：地图应用开发

**场景**：基于 PostGIS 的地图应用

**实现**：

```sql
-- 1. 创建位置表
CREATE TABLE locations (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    geom GEOMETRY(POINT, 4326)
);

CREATE INDEX idx_locations_geom ON locations USING GIST (geom);

-- 2. 插入数据
INSERT INTO locations (name, geom)
VALUES
    ('Beijing', ST_SetSRID(ST_MakePoint(116.3974, 39.9093), 4326)),
    ('Shanghai', ST_SetSRID(ST_MakePoint(121.4737, 31.2304), 4326));

-- 3. 查询附近位置
SELECT
    name,
    ST_Distance(
        ST_Transform(geom, 3857),
        ST_Transform(ST_GeomFromText('POINT(116.3974 39.9093)', 4326), 3857)
    ) AS distance_meters
FROM locations
ORDER BY geom <-> ST_GeomFromText('POINT(116.3974 39.9093)', 4326)
LIMIT 10;

-- 4. 输出 GeoJSON
SELECT json_build_object(
    'type', 'FeatureCollection',
    'features', json_agg(
        json_build_object(
            'type', 'Feature',
            'geometry', ST_AsGeoJSON(geom)::json,
            'properties', json_build_object('name', name)
        )
    )
) AS geojson
FROM locations;
```

**效果**：

- 查询性能：< 50ms
- 支持实时地图显示
- 支持空间查询和分析

### 9.2 案例：地理分析系统

**场景**：地理数据分析系统

**实现**：

```sql
-- 1. 创建区域表
CREATE TABLE regions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    geom GEOMETRY(POLYGON, 4326)
);

CREATE INDEX idx_regions_geom ON regions USING GIST (geom);

-- 2. 空间聚合分析
SELECT
    r.name,
    COUNT(l.id) AS location_count,
    ST_Area(ST_Transform(r.geom, 3857)) AS area_m2
FROM regions r
LEFT JOIN locations l ON ST_Within(l.geom, r.geom)
GROUP BY r.id, r.name, r.geom;

-- 3. 缓冲区分析
SELECT
    l.name,
    ST_Buffer(ST_Transform(l.geom, 3857), 1000) AS buffer_geom
FROM locations l;
```

**效果**：

- 分析性能：< 200ms
- 支持复杂空间分析
- 支持大数据量处理

---

## 📊 总结

PostgreSQL 结合 PostGIS 提供了强大的 GIS 应用开发能力：

1. **空间数据类型**：支持点、线、面等空间数据类型
2. **空间索引**：高效的 GIST 和 SP-GiST 空间索引
3. **空间函数**：丰富的空间计算和分析函数
4. **坐标系统**：支持多种坐标系统和投影
5. **高性能查询**：优化的空间查询性能

**最佳实践**：

- 使用合适的几何类型
- 创建空间索引
- 使用合适的坐标系统
- 优化空间查询
- 简化复杂几何对象

---

**最后更新**: 2025 年 1 月
**维护者**: PostgreSQL Modern Team
