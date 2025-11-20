# PostGIS 空间数据

> **更新时间**: 2025 年 11 月 1 日  
> **技术版本**: PostGIS 3.4+, PostgreSQL 15+  
> **文档编号**: 07-02-01

## 📑 目录

- [PostGIS 空间数据](#postgis-空间数据)
  - [📑 目录](#-目录)
  - [1. 概述](#1-概述)
    - [1.1 技术背景](#11-技术背景)
    - [1.2 技术定位](#12-技术定位)
    - [1.3 核心价值](#13-核心价值)
  - [2. 空间数据类型](#2-空间数据类型)
    - [2.1 几何类型](#21-几何类型)
    - [2.2 地理类型](#22-地理类型)
    - [2.3 栅格类型](#23-栅格类型)
  - [3. 空间索引](#3-空间索引)
    - [3.1 GIST 索引](#31-gist-索引)
    - [3.2 SP-GiST 索引](#32-sp-gist-索引)
    - [3.3 索引优化](#33-索引优化)
  - [4. 空间查询](#4-空间查询)
    - [4.1 空间关系查询](#41-空间关系查询)
    - [4.2 空间分析查询](#42-空间分析查询)
    - [4.3 空间聚合查询](#43-空间聚合查询)
  - [5. 最佳实践](#5-最佳实践)
    - [5.1 数据类型选择](#51-数据类型选择)
    - [5.2 索引策略](#52-索引策略)
    - [5.3 性能优化](#53-性能优化)
  - [6. 参考资料](#6-参考资料)

---

## 1. 概述

### 1.1 技术背景

**问题需求**:

PostGIS 是 PostgreSQL 的空间数据扩展，提供空间数据类型、空间索引和空间查询功能，广泛应用于地理信息系
统（GIS）、位置服务（LBS）等场景。

**技术演进**:

1. **2001 年**: PostGIS 1.0 发布
2. **2015 年**: PostGIS 2.2 支持 3D 几何
3. **2020 年**: PostGIS 3.0 重构架构
4. **2025 年**: PostGIS 3.4 优化性能

### 1.2 技术定位

PostGIS 空间数据集成提供 PostgreSQL 与空间数据的集成方案，支持几何、地理和栅格数据类型。

### 1.3 核心价值

- **空间数据类型**: 完整的空间数据类型支持
- **空间索引**: 高效的 GIST 和 SP-GiST 索引
- **空间查询**: 丰富的空间查询和分析功能
- **标准兼容**: 符合 OGC 标准

---

## 2. 空间数据类型

### 2.1 几何类型

**几何类型**:

```sql
-- 创建空间表
CREATE TABLE locations (
    id SERIAL PRIMARY KEY,
    name TEXT,
    geom GEOMETRY(POINT, 4326)  -- 点类型，WGS84 坐标系
);

-- 插入点数据
INSERT INTO locations (name, geom)
VALUES (
    'Beijing',
    ST_GeomFromText('POINT(116.4074 39.9042)', 4326)
);

-- 插入线数据
CREATE TABLE roads (
    id SERIAL PRIMARY KEY,
    name TEXT,
    geom GEOMETRY(LINESTRING, 4326)
);

-- 插入面数据
CREATE TABLE regions (
    id SERIAL PRIMARY KEY,
    name TEXT,
    geom GEOMETRY(POLYGON, 4326)
);
```

### 2.2 地理类型

**地理类型**:

```sql
-- 使用地理类型（基于球面计算）
CREATE TABLE cities (
    id SERIAL PRIMARY KEY,
    name TEXT,
    geog GEOGRAPHY(POINT, 4326)
);

-- 插入地理数据
INSERT INTO cities (name, geog)
VALUES (
    'Shanghai',
    ST_GeogFromText('POINT(121.4737 31.2304)')
);

-- 地理类型自动处理坐标系统
SELECT ST_Distance(
    ST_GeogFromText('POINT(116.4074 39.9042)'),
    ST_GeogFromText('POINT(121.4737 31.2304)')
) / 1000 as distance_km;  -- 返回千米
```

### 2.3 栅格类型

**栅格类型**:

```sql
-- 创建栅格表
CREATE TABLE elevation (
    id SERIAL PRIMARY KEY,
    name TEXT,
    rast RASTER
);

-- 导入栅格数据
INSERT INTO elevation (name, rast)
VALUES (
    'dem',
    ST_FromGDALRaster('/path/to/dem.tif')
);

-- 栅格查询
SELECT ST_Value(rast, ST_GeomFromText('POINT(116.4074 39.9042)', 4326))
FROM elevation
WHERE name = 'dem';
```

---

## 3. 空间索引

### 3.1 GIST 索引

**GIST 索引**:

```sql
-- 创建 GIST 索引
CREATE INDEX idx_locations_geom ON locations USING GIST (geom);

-- 空间查询使用索引
EXPLAIN ANALYZE
SELECT * FROM locations
WHERE ST_DWithin(
    geom,
    ST_GeomFromText('POINT(116.4074 39.9042)', 4326),
    1000  -- 1000 米范围内
);
```

### 3.2 SP-GiST 索引

**SP-GiST 索引**:

```sql
-- 创建 SP-GiST 索引（适用于点数据）
CREATE INDEX idx_cities_geog ON cities USING SPGIST (geog);

-- 查询优化
EXPLAIN ANALYZE
SELECT * FROM cities
WHERE ST_DWithin(
    geog,
    ST_GeogFromText('POINT(116.4074 39.9042)'),
    50000  -- 50 千米范围内
);
```

### 3.3 索引优化

**索引优化技巧**:

```sql
-- 1. 使用覆盖索引
CREATE INDEX idx_locations_geom_name ON locations
USING GIST (geom) INCLUDE (name);

-- 2. 部分索引（只索引特定区域）
CREATE INDEX idx_locations_beijing ON locations
USING GIST (geom)
WHERE ST_Within(geom, ST_MakeEnvelope(116.0, 39.0, 117.0, 40.0, 4326));

-- 3. 并行索引构建
SET max_parallel_maintenance_workers = 4;
CREATE INDEX CONCURRENTLY idx_locations_geom ON locations USING GIST (geom);
```

---

## 4. 空间查询

### 4.1 空间关系查询

**空间关系查询**:

```sql
-- 1. 包含关系
SELECT * FROM regions
WHERE ST_Contains(geom, ST_GeomFromText('POINT(116.4074 39.9042)', 4326));

-- 2. 相交关系
SELECT * FROM roads
WHERE ST_Intersects(geom, ST_MakeEnvelope(116.0, 39.0, 117.0, 40.0, 4326));

-- 3. 距离查询
SELECT name, ST_Distance(geom, ST_GeomFromText('POINT(116.4074 39.9042)', 4326)) as distance
FROM locations
ORDER BY distance
LIMIT 10;

-- 4. 缓冲区查询
SELECT * FROM locations
WHERE ST_Within(
    geom,
    ST_Buffer(ST_GeomFromText('POINT(116.4074 39.9042)', 4326), 1000)
);
```

### 4.2 空间分析查询

**空间分析查询**:

```sql
-- 1. 计算面积
SELECT name, ST_Area(geom) as area_m2
FROM regions;

-- 2. 计算长度
SELECT name, ST_Length(geom) as length_m
FROM roads;

-- 3. 计算质心
SELECT name, ST_AsText(ST_Centroid(geom)) as centroid
FROM regions;

-- 4. 简化几何
SELECT name, ST_Simplify(geom, 0.001) as simplified_geom
FROM regions;
```

### 4.3 空间聚合查询

**空间聚合查询**:

```sql
-- 1. 空间聚合
SELECT
    region_id,
    ST_Union(geom) as union_geom,
    COUNT(*) as point_count
FROM locations
GROUP BY region_id;

-- 2. 空间聚类
SELECT
    ST_ClusterKMeans(geom, 5) OVER () as cluster_id,
    name,
    geom
FROM locations;

-- 3. 最近邻聚合
SELECT
    a.name,
    COUNT(*) as nearby_count,
    AVG(ST_Distance(a.geom, b.geom)) as avg_distance
FROM locations a
JOIN locations b ON ST_DWithin(a.geom, b.geom, 1000)
WHERE a.id != b.id
GROUP BY a.id, a.name;
```

---

## 5. 最佳实践

### 5.1 数据类型选择

- **几何类型**: 适用于平面投影坐标系，计算速度快
- **地理类型**: 适用于全球坐标系，自动处理球面计算
- **栅格类型**: 适用于连续数据（如高程、温度）

### 5.2 索引策略

- **GIST 索引**: 适用于所有几何类型，通用性强
- **SP-GiST 索引**: 适用于点数据，查询性能更好
- **覆盖索引**: 减少回表查询，提升性能

### 5.3 性能优化

- **坐标系统**: 选择合适的坐标系统
- **几何简化**: 简化复杂几何，减少存储和计算
- **分区策略**: 按空间范围分区，提升查询性能

---

## 6. 参考资料

- [PostGIS 官方文档](https://postgis.net/documentation/)
- [OGC 标准](https://www.ogc.org/standards/)

---

**最后更新**: 2025 年 11 月 1 日  
**维护者**: PostgreSQL Modern Team
