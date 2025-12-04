# 【深入】PostGIS空间数据库完整实战指南

> **文档版本**: v1.0 | **创建日期**: 2025-01 | **适用版本**: PostgreSQL 12+, PostGIS 3.0+
> **难度等级**: ⭐⭐⭐⭐ 高级 | **预计学习时间**: 10-12小时

---

## 📋 目录

- [【深入】PostGIS空间数据库完整实战指南](#深入postgis空间数据库完整实战指南)
  - [📋 目录](#-目录)
  - [1. 课程概述](#1-课程概述)
    - [1.1 什么是PostGIS？](#11-什么是postgis)
      - [核心特性](#核心特性)
      - [适用场景](#适用场景)
    - [1.2 为什么选择PostGIS？](#12-为什么选择postgis)
  - [2. GIS基础理论](#2-gis基础理论)
    - [2.1 空间数据模型](#21-空间数据模型)
      - [矢量数据模型](#矢量数据模型)
      - [栅格数据模型](#栅格数据模型)
    - [2.2 坐标参考系统 (CRS)](#22-坐标参考系统-crs)
      - [常用坐标系](#常用坐标系)
      - [地理坐标 vs 投影坐标](#地理坐标-vs-投影坐标)
    - [2.3 空间关系](#23-空间关系)
      - [DE-9IM模型（9交集模型）](#de-9im模型9交集模型)
  - [3. PostGIS架构与安装](#3-postgis架构与安装)
    - [3.1 系统架构](#31-系统架构)
    - [3.2 安装配置](#32-安装配置)
      - [安装PostGIS](#安装postgis)
      - [初始化数据库](#初始化数据库)
    - [3.3 快速验证](#33-快速验证)
  - [4. 空间数据类型](#4-空间数据类型)
    - [4.1 GEOMETRY vs GEOGRAPHY](#41-geometry-vs-geography)
      - [区别对比](#区别对比)
      - [使用示例](#使用示例)
    - [4.2 几何类型详解](#42-几何类型详解)
      - [POINT（点）](#point点)
      - [LINESTRING（线）](#linestring线)
      - [POLYGON（多边形）](#polygon多边形)
    - [4.3 复杂几何类型](#43-复杂几何类型)
      - [MULTIPOINT/MULTILINESTRING/MULTIPOLYGON](#multipointmultilinestringmultipolygon)
      - [GEOMETRYCOLLECTION](#geometrycollection)
  - [5. 空间索引](#5-空间索引)
    - [5.1 GiST索引](#51-gist索引)
      - [创建和使用](#创建和使用)
      - [GiST vs BRIN](#gist-vs-brin)
    - [5.2 SP-GiST索引](#52-sp-gist索引)
    - [5.3 空间索引优化](#53-空间索引优化)
      - [索引覆盖优化](#索引覆盖优化)
      - [分区表空间索引](#分区表空间索引)
  - [6. 空间查询与分析](#6-空间查询与分析)
    - [6.1 距离查询](#61-距离查询)
      - [点到点距离](#点到点距离)
      - [范围查询（DWithin）](#范围查询dwithin)
      - [K近邻查询](#k近邻查询)
    - [6.2 空间关系查询](#62-空间关系查询)
      - [Contains/Within](#containswithin)
      - [Intersects/Overlaps](#intersectsoverlaps)
      - [Touches/Crosses](#touchescrosses)
    - [6.3 空间聚合](#63-空间聚合)
      - [空间Union](#空间union)
      - [聚合几何](#聚合几何)
  - [7. 坐标系统与投影](#7-坐标系统与投影)
    - [7.1 坐标转换](#71-坐标转换)
      - [SRID转换](#srid转换)
      - [中国坐标系](#中国坐标系)
    - [7.2 自定义投影](#72-自定义投影)
  - [8. 空间关系与拓扑](#8-空间关系与拓扑)
    - [8.1 拓扑数据模型](#81-拓扑数据模型)
      - [创建拓扑](#创建拓扑)
      - [拓扑优势](#拓扑优势)
    - [8.2 拓扑查询](#82-拓扑查询)
  - [9. 高级空间分析](#9-高级空间分析)
    - [9.1 缓冲区分析](#91-缓冲区分析)
    - [9.2 Voronoi图/泰森多边形](#92-voronoi图泰森多边形)
    - [9.3 凹包与凸包](#93-凹包与凸包)
    - [9.4 热力图分析](#94-热力图分析)
    - [9.5 路径分析](#95-路径分析)
      - [路径简化](#路径简化)
      - [路径插值](#路径插值)
  - [10. 性能优化](#10-性能优化)
    - [10.1 查询优化](#101-查询优化)
      - [使用边界框预过滤](#使用边界框预过滤)
      - [边界框操作符](#边界框操作符)
    - [10.2 几何简化](#102-几何简化)
    - [10.3 空间聚类](#103-空间聚类)
    - [10.4 物化视图加速](#104-物化视图加速)
  - [11. 生产实战案例](#11-生产实战案例)
    - [11.1 案例1：O2O配送系统](#111-案例1o2o配送系统)
      - [需求](#需求)
      - [实现](#实现)
    - [11.2 案例2：房产推荐系统](#112-案例2房产推荐系统)
    - [11.3 案例3：灾害应急响应](#113-案例3灾害应急响应)
  - [12. 最佳实践](#12-最佳实践)
    - [12.1 数据设计原则](#121-数据设计原则)
      - [✅ 推荐做法](#-推荐做法)
      - [❌ 避免的做法](#-避免的做法)
    - [12.2 性能最佳实践](#122-性能最佳实践)
      - [查询优化检查清单](#查询优化检查清单)
      - [监控查询](#监控查询)
    - [12.3 数据质量保证](#123-数据质量保证)
  - [13. FAQ与疑难解答](#13-faq与疑难解答)
    - [Q1: GEOMETRY和GEOGRAPHY该如何选择？](#q1-geometry和geography该如何选择)
    - [Q2: 为什么空间查询很慢？](#q2-为什么空间查询很慢)
    - [Q3: 如何处理跨180度经线的几何？](#q3-如何处理跨180度经线的几何)
    - [Q4: 如何批量导入GeoJSON/Shapefile数据？](#q4-如何批量导入geojsonshapefile数据)
    - [Q5: PostGIS可以做路径导航吗？](#q5-postgis可以做路径导航吗)
  - [📚 延伸阅读](#-延伸阅读)
    - [官方资源](#官方资源)
    - [工具生态](#工具生态)
    - [推荐书籍](#推荐书籍)
  - [✅ 学习检查清单](#-学习检查清单)
  - [💡 下一步学习](#-下一步学习)

1. [GIS基础理论](#2-gis基础理论)
2. [PostGIS架构与安装](#3-postgis架构与安装)
3. [空间数据类型](#4-空间数据类型)
4. [空间索引](#5-空间索引)
5. [空间查询与分析](#6-空间查询与分析)
6. [坐标系统与投影](#7-坐标系统与投影)
7. [空间关系与拓扑](#8-空间关系与拓扑)
8. [高级空间分析](#9-高级空间分析)
9. [性能优化](#10-性能优化)
10. [生产实战案例](#11-生产实战案例)
11. [最佳实践](#12-最佳实践)
12. [FAQ与疑难解答](#13-faq与疑难解答)

---

## 1. 课程概述

### 1.1 什么是PostGIS？

**PostGIS** 是PostgreSQL的空间数据库扩展，为PostgreSQL提供地理空间对象支持，使其成为功能强大的GIS数据库。

#### 核心特性

| 特性 | 说明 | 应用 |
|------|------|------|
| **几何类型** | 点、线、面、多边形等 | 存储地理实体 |
| **空间索引** | R-Tree, GiST, SP-GiST | 高效空间查询 |
| **空间函数** | 2000+ 函数 | 距离、面积、缓冲区等 |
| **坐标转换** | 支持6000+坐标系 | WGS84, Web Mercator等 |
| **拓扑支持** | 拓扑数据模型 | 复杂空间关系 |
| **栅格支持** | 栅格数据类型 | 卫星影像、DEM |
| **3D支持** | 三维几何 | 建筑建模、地形分析 |

#### 适用场景

- **位置服务**: 地图应用、导航、配送路径优化
- **城市规划**: 土地利用、交通规划、设施选址
- **环境监测**: 气象分析、污染扩散、生态保护
- **商业智能**: 门店选址、市场分析、物流优化
- **智慧农业**: 精准农业、土地管理
- **应急响应**: 灾害评估、救援路径规划

### 1.2 为什么选择PostGIS？

```text
对比其他GIS解决方案：

PostGIS vs Oracle Spatial:
✅ 开源免费 vs 高昂许可费
✅ 活跃社区 vs 封闭生态
✅ 标准兼容 vs 专有技术

PostGIS vs MySQL Spatial:
✅ 功能丰富（2000+ 函数）
✅ 高性能空间索引
✅ 完整的拓扑支持
✅ 3D/栅格/点云支持

PostGIS vs MongoDB GeoJSON:
✅ ACID保证
✅ 复杂空间分析
✅ 精确的坐标转换
✅ 成熟的生态系统
```

---

## 2. GIS基础理论

### 2.1 空间数据模型

#### 矢量数据模型

```text
几何对象层次：

GEOMETRY (基类)
├── POINT (点)
│   └── MULTIPOINT (多点)
├── LINESTRING (线)
│   └── MULTILINESTRING (多线)
├── POLYGON (面)
│   └── MULTIPOLYGON (多面)
└── GEOMETRYCOLLECTION (几何集合)

空间维度：
- 2D: X, Y
- 3D: X, Y, Z (高程)
- 4D: X, Y, Z, M (测量值，如时间)
```

#### 栅格数据模型

```text
栅格 = 规则网格 + 每个单元的值

示例：卫星影像
┌─────┬─────┬─────┐
│ 120 │ 125 │ 130 │  每个单元存储
├─────┼─────┼─────┤  像素值（如温度、
│ 115 │ 122 │ 128 │  高程、反射率）
├─────┼─────┼─────┤
│ 110 │ 118 │ 125 │
└─────┴─────┴─────┘
```

### 2.2 坐标参考系统 (CRS)

#### 常用坐标系

| SRID | 名称 | 类型 | 应用 |
|------|------|------|------|
| **4326** | WGS84 | 地理坐标系 | GPS、国际标准 |
| **3857** | Web Mercator | 投影坐标系 | 网络地图（Google/OSM） |
| **2000** | CGCS2000 | 地理坐标系 | 中国国家标准 |
| **32650** | UTM Zone 50N | 投影坐标系 | 局部高精度测量 |

#### 地理坐标 vs 投影坐标

```text
地理坐标系 (SRID 4326):
- 单位：度 (经度, 纬度)
- 范围：经度 -180~180, 纬度 -90~90
- 特点：不等距，球面距离计算
- 示例：(116.4074, 39.9042) - 北京天安门

投影坐标系 (SRID 3857):
- 单位：米
- 范围：X ±20037508.34, Y ±20037508.34
- 特点：平面坐标，直角距离计算
- 示例：(12958938, 4825777) - 北京天安门投影坐标
```

### 2.3 空间关系

#### DE-9IM模型（9交集模型）

```text
两个几何对象A和B的关系：

    内部(I)  边界(B)  外部(E)
A内部  T/F     T/F     T/F
A边界  T/F     T/F     T/F
A外部  T/F     T/F     T/F

基本关系谓词：
- Contains (包含)
- Within (在内部)
- Overlaps (重叠)
- Crosses (穿过)
- Touches (接触)
- Disjoint (分离)
- Equals (相等)
```

---

## 3. PostGIS架构与安装

### 3.1 系统架构

```text
┌─────────────────────────────────────────┐
│         应用层 (Application)             │
│  QGIS / GeoServer / Web APIs            │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│         PostGIS Extension               │
├─────────────────────────────────────────┤
│ ┌───────────┐  ┌──────────────────┐    │
│ │ Geometry  │  │ Geography        │    │
│ │ Functions │  │ Functions        │    │
│ └───────────┘  └──────────────────┘    │
│ ┌───────────┐  ┌──────────────────┐    │
│ │ Raster    │  │ Topology         │    │
│ │ Support   │  │ Support          │    │
│ └───────────┘  └──────────────────┘    │
│ ┌───────────────────────────────────┐  │
│ │ GEOS (几何引擎)                    │  │
│ │ PROJ (坐标转换)                    │  │
│ │ GDAL (栅格/矢量驱动)               │  │
│ └───────────────────────────────────┘  │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│         PostgreSQL Core                 │
│  Storage / Index / Query Optimizer      │
└─────────────────────────────────────────┘
```

### 3.2 安装配置

#### 安装PostGIS

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y postgresql-14 postgresql-14-postgis-3

# CentOS/RHEL
sudo yum install -y epel-release
sudo yum install -y postgis33_14

# macOS (Homebrew)
brew install postgresql postgis

# Docker
docker run --name postgis -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 -d postgis/postgis:14-3.3
```

#### 初始化数据库

```sql
-- 1. 创建扩展
CREATE EXTENSION postgis;
CREATE EXTENSION postgis_topology;  -- 可选：拓扑支持
CREATE EXTENSION postgis_raster;    -- 可选：栅格支持
CREATE EXTENSION fuzzystrmatch;     -- 可选：模糊匹配
CREATE EXTENSION postgis_tiger_geocoder;  -- 可选：地理编码

-- 2. 验证安装
SELECT PostGIS_Full_Version();

-- 预期输出类似：
-- POSTGIS="3.3.2" [EXTENSION] PGSQL="140" GEOS="3.11.0"
-- PROJ="9.1.0" LIBXML="2.9.10" LIBJSON="0.15"

-- 3. 查看可用函数
SELECT COUNT(*) FROM pg_proc
WHERE pronamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public')
  AND prokind = 'f'
  AND proname LIKE 'ST_%';
-- 应该有 1000+ 函数
```

### 3.3 快速验证

```sql
-- 创建测试表
CREATE TABLE cities (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    location GEOMETRY(Point, 4326)
);

-- 插入数据
INSERT INTO cities (name, location) VALUES
('Beijing', ST_SetSRID(ST_MakePoint(116.4074, 39.9042), 4326)),
('Shanghai', ST_SetSRID(ST_MakePoint(121.4737, 31.2304), 4326)),
('Guangzhou', ST_SetSRID(ST_MakePoint(113.2644, 23.1291), 4326));

-- 测试查询
SELECT
    name,
    ST_AsText(location) AS wkt,
    ST_X(location) AS longitude,
    ST_Y(location) AS latitude
FROM cities;

-- 计算距离
SELECT
    a.name AS city1,
    b.name AS city2,
    ST_Distance(a.location::geography, b.location::geography) / 1000 AS distance_km
FROM cities a, cities b
WHERE a.id < b.id;

-- 预期输出：
-- Beijing <-> Shanghai: ~1068 km
-- Beijing <-> Guangzhou: ~1891 km
-- Shanghai <-> Guangzhou: ~1213 km
```

---

## 4. 空间数据类型

### 4.1 GEOMETRY vs GEOGRAPHY

#### 区别对比

| 特性 | GEOMETRY | GEOGRAPHY |
|------|----------|-----------|
| **坐标系统** | 笛卡尔平面 | 椭球面（地球表面） |
| **距离单位** | 坐标单位（度/米） | 米 |
| **精度** | 取决于投影 | 高精度（真实地球） |
| **性能** | 快 | 较慢（球面计算） |
| **函数支持** | 全部（2000+） | 部分（核心函数） |
| **适用场景** | 小范围、投影坐标 | 全球范围、长距离 |

#### 使用示例

```sql
-- GEOMETRY示例（平面计算）
CREATE TABLE parks_geometry (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    boundary GEOMETRY(Polygon, 4326)
);

INSERT INTO parks_geometry (name, boundary) VALUES
('Central Park', ST_GeomFromText('POLYGON((
    116.39 39.91, 116.40 39.91, 116.40 39.90, 116.39 39.90, 116.39 39.91
))', 4326));

-- 面积计算（度的平方，不准确）
SELECT name, ST_Area(boundary) AS area_deg2
FROM parks_geometry;
-- 结果约0.0001（度²，无实际意义）

-- GEOGRAPHY示例（球面计算）
CREATE TABLE parks_geography (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    boundary GEOGRAPHY(Polygon, 4326)
);

INSERT INTO parks_geography (name, boundary) VALUES
('Central Park', ST_GeogFromText('POLYGON((
    116.39 39.91, 116.40 39.91, 116.40 39.90, 116.39 39.90, 116.39 39.91
))'));

-- 面积计算（平方米，准确）
SELECT name, ST_Area(boundary) / 10000 AS area_hectares
FROM parks_geography;
-- 结果约121公顷（准确）
```

### 4.2 几何类型详解

#### POINT（点）

```sql
-- 创建点
SELECT ST_SetSRID(ST_MakePoint(116.4074, 39.9042), 4326) AS tiananmen;

-- 从WKT创建
SELECT ST_GeomFromText('POINT(116.4074 39.9042)', 4326);

-- 从GeoJSON创建
SELECT ST_GeomFromGeoJSON('{"type":"Point","coordinates":[116.4074,39.9042]}');

-- 提取坐标
SELECT
    ST_X(location) AS longitude,
    ST_Y(location) AS latitude,
    ST_Z(location) AS elevation  -- 如果是3D点
FROM cities WHERE name = 'Beijing';
```

#### LINESTRING（线）

```sql
-- 创建线（道路）
CREATE TABLE roads (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    path GEOMETRY(LineString, 4326)
);

INSERT INTO roads (name, path) VALUES
('Chang''an Avenue', ST_GeomFromText(
    'LINESTRING(116.39 39.91, 116.40 39.91, 116.41 39.91)', 4326
));

-- 线性分析
SELECT
    name,
    ST_Length(path::geography) / 1000 AS length_km,
    ST_NumPoints(path) AS vertex_count,
    ST_AsText(ST_StartPoint(path)) AS start_point,
    ST_AsText(ST_EndPoint(path)) AS end_point
FROM roads;

-- 提取线上的点
SELECT
    name,
    ST_AsText(ST_PointN(path, generate_series(1, ST_NumPoints(path))))
FROM roads;
```

#### POLYGON（多边形）

```sql
-- 创建多边形（带空洞）
CREATE TABLE districts (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    boundary GEOMETRY(Polygon, 4326)
);

-- 外环（逆时针）+ 内环-空洞（顺时针）
INSERT INTO districts (name, boundary) VALUES
('District A', ST_GeomFromText('POLYGON((
    0 0, 10 0, 10 10, 0 10, 0 0
), (
    2 2, 2 8, 8 8, 8 2, 2 2
))', 4326));

-- 多边形分析
SELECT
    name,
    ST_Area(boundary::geography) / 1000000 AS area_km2,
    ST_Perimeter(boundary::geography) / 1000 AS perimeter_km,
    ST_NumInteriorRings(boundary) AS hole_count,
    ST_AsText(ST_Centroid(boundary)) AS centroid
FROM districts;

-- 简化多边形（减少顶点）
SELECT
    name,
    ST_NPoints(boundary) AS original_points,
    ST_NPoints(ST_Simplify(boundary, 0.001)) AS simplified_points
FROM districts;
```

### 4.3 复杂几何类型

#### MULTIPOINT/MULTILINESTRING/MULTIPOLYGON

```sql
-- 多点（连锁店位置）
CREATE TABLE store_chains (
    id SERIAL PRIMARY KEY,
    brand VARCHAR(100),
    locations GEOMETRY(MultiPoint, 4326)
);

INSERT INTO store_chains (brand, locations) VALUES
('Starbucks Beijing', ST_GeomFromText('MULTIPOINT(
    116.40 39.91, 116.41 39.92, 116.39 39.90
)', 4326));

-- 多线（公交线路）
CREATE TABLE bus_routes (
    id SERIAL PRIMARY KEY,
    route_number VARCHAR(10),
    paths GEOMETRY(MultiLineString, 4326)
);

-- 多面（国家领土，含岛屿）
CREATE TABLE countries (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    territory GEOMETRY(MultiPolygon, 4326)
);

INSERT INTO countries (name, territory) VALUES
('Example Country', ST_GeomFromText('MULTIPOLYGON(((
    0 0, 10 0, 10 10, 0 10, 0 0
)), ((
    20 20, 30 20, 30 30, 20 30, 20 20
)))', 4326));
```

#### GEOMETRYCOLLECTION

```sql
-- 混合几何集合（城市规划）
CREATE TABLE city_features (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    features GEOMETRY(GeometryCollection, 4326)
);

INSERT INTO city_features (name, features) VALUES
('Urban Complex', ST_GeomFromText('GEOMETRYCOLLECTION(
    POINT(116.40 39.91),
    LINESTRING(116.39 39.90, 116.41 39.92),
    POLYGON((116.38 39.88, 116.42 39.88, 116.42 39.92, 116.38 39.92, 116.38 39.88))
)', 4326));

-- 分解几何集合
SELECT
    name,
    ST_GeometryType(ST_GeometryN(features, generate_series(1, ST_NumGeometries(features)))) AS geom_type,
    ST_AsText(ST_GeometryN(features, generate_series(1, ST_NumGeometries(features)))) AS geom_wkt
FROM city_features;
```

---

## 5. 空间索引

### 5.1 GiST索引

#### 创建和使用

```sql
-- 创建空间索引
CREATE INDEX cities_location_gist_idx
ON cities USING GIST (location);

-- 空间索引会自动用于以下查询
EXPLAIN ANALYZE
SELECT name FROM cities
WHERE ST_DWithin(location, ST_MakePoint(116.4, 39.9)::geography, 50000);

-- 查看索引使用情况
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan AS times_used,
    idx_tup_read AS tuples_read,
    idx_tup_fetch AS tuples_fetched
FROM pg_stat_user_indexes
WHERE indexname LIKE '%gist%'
ORDER BY idx_scan DESC;
```

#### GiST vs BRIN

| 特性 | GiST | BRIN |
|------|------|------|
| **结构** | R-Tree | 块级索引 |
| **大小** | 较大 | 极小 |
| **精度** | 高 | 粗略 |
| **适用场景** | 小到中等表 | 超大表，数据有序 |
| **维护成本** | 高 | 低 |

```sql
-- BRIN索引（适用于有序的大数据集）
CREATE INDEX cities_location_brin_idx
ON cities USING BRIN (location) WITH (pages_per_range = 128);

-- 对比索引大小
SELECT
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) AS index_size
FROM pg_stat_user_indexes
WHERE tablename = 'cities';
```

### 5.2 SP-GiST索引

```sql
-- SP-GiST索引（空间分区索引）
-- 适用于：点数据、四叉树分区
CREATE INDEX cities_location_spgist_idx
ON cities USING SPGIST (location);

-- 特点：
-- ✅ 点数据性能优秀
-- ✅ 内存效率高
-- ❌ 不支持所有几何类型
-- ❌ 更新较慢
```

### 5.3 空间索引优化

#### 索引覆盖优化

```sql
-- 问题：只需要距离，但触发全表扫描
EXPLAIN ANALYZE
SELECT name, ST_Distance(location::geography,
    ST_MakePoint(116.4, 39.9)::geography) AS dist
FROM cities
ORDER BY dist
LIMIT 10;

-- 优化：使用索引排序（KNN操作符）
EXPLAIN ANALYZE
SELECT name, ST_Distance(location::geography,
    ST_MakePoint(116.4, 39.9)::geography) AS dist
FROM cities
ORDER BY location <-> ST_MakePoint(116.4, 39.9)::geometry
LIMIT 10;
-- <-> 操作符触发索引排序，显著提升性能
```

#### 分区表空间索引

```sql
-- 按地理区域分区
CREATE TABLE events (
    id BIGSERIAL,
    name VARCHAR(100),
    location GEOMETRY(Point, 4326),
    event_time TIMESTAMPTZ
) PARTITION BY RANGE (ST_X(location));

CREATE TABLE events_east PARTITION OF events
    FOR VALUES FROM (100) TO (130);  -- 东部经度

CREATE TABLE events_west PARTITION OF events
    FOR VALUES FROM (70) TO (100);   -- 西部经度

-- 为每个分区创建索引
CREATE INDEX events_east_location_idx ON events_east USING GIST (location);
CREATE INDEX events_west_location_idx ON events_west USING GIST (location);
```

---

## 6. 空间查询与分析

### 6.1 距离查询

#### 点到点距离

```sql
-- Geography（精确，单位米）
SELECT
    ST_Distance(
        ST_MakePoint(116.4074, 39.9042)::geography,  -- 北京
        ST_MakePoint(121.4737, 31.2304)::geography   -- 上海
    ) / 1000 AS distance_km;
-- 结果：1068 km

-- Geometry（平面，单位度）
SELECT
    ST_Distance(
        ST_MakePoint(116.4074, 39.9042)::geometry,
        ST_MakePoint(121.4737, 31.2304)::geometry
    ) AS distance_degrees;
-- 结果：约9.37度（无实际意义）
```

#### 范围查询（DWithin）

```sql
-- 查找附近5公里内的餐厅
CREATE TABLE restaurants (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    location GEOMETRY(Point, 4326)
);

-- 查询
SELECT
    name,
    ST_Distance(location::geography,
        ST_MakePoint(116.4074, 39.9042)::geography) AS distance_m
FROM restaurants
WHERE ST_DWithin(
    location::geography,
    ST_MakePoint(116.4074, 39.9042)::geography,
    5000  -- 5公里
)
ORDER BY distance_m;
```

#### K近邻查询

```sql
-- 最近的10个加油站
SELECT
    name,
    ST_Distance(location::geography,
        ST_MakePoint(116.4, 39.9)::geography) / 1000 AS distance_km
FROM gas_stations
ORDER BY location <-> ST_MakePoint(116.4, 39.9)::geometry
LIMIT 10;
-- 使用 <-> 操作符触发KNN索引
```

### 6.2 空间关系查询

#### Contains/Within

```sql
-- 查找区域内的所有POI
SELECT p.name, p.category
FROM points_of_interest p
JOIN districts d ON d.name = 'Haidian District'
WHERE ST_Contains(d.boundary, p.location);

-- 查找点所在的区域
SELECT d.name AS district_name
FROM districts d
WHERE ST_Contains(d.boundary, ST_MakePoint(116.31, 40.00));

-- 等价于
SELECT d.name
FROM districts d
WHERE ST_Within(ST_MakePoint(116.31, 40.00), d.boundary);
```

#### Intersects/Overlaps

```sql
-- 查找与某区域相交的道路
SELECT r.name, r.road_class
FROM roads r
JOIN districts d ON d.name = 'Downtown'
WHERE ST_Intersects(r.path, d.boundary);

-- 查找重叠的保护区
SELECT
    a.name AS area1,
    b.name AS area2,
    ST_Area(ST_Intersection(a.boundary::geography, b.boundary::geography)) / 10000 AS overlap_hectares
FROM protected_areas a
JOIN protected_areas b ON a.id < b.id
WHERE ST_Overlaps(a.boundary, b.boundary);
```

#### Touches/Crosses

```sql
-- 查找接壤的行政区
SELECT
    a.name AS district1,
    b.name AS district2
FROM districts a
JOIN districts b ON a.id < b.id
WHERE ST_Touches(a.boundary, b.boundary);

-- 查找穿过区域的高速公路
SELECT h.name, d.name AS district_name
FROM highways h
JOIN districts d ON ST_Crosses(h.path, d.boundary);
```

### 6.3 空间聚合

#### 空间Union

```sql
-- 合并相邻区域
SELECT
    region,
    ST_Union(boundary) AS merged_boundary,
    SUM(ST_Area(boundary::geography)) / 1000000 AS total_area_km2
FROM districts
GROUP BY region;
```

#### 聚合几何

```sql
-- 收集所有商店位置为多点
SELECT
    brand,
    ST_Collect(location) AS all_locations,
    COUNT(*) AS store_count
FROM stores
GROUP BY brand;

-- 计算最小凸包（Convex Hull）
SELECT
    brand,
    ST_ConvexHull(ST_Collect(location)) AS service_area
FROM stores
GROUP BY brand;
```

---

## 7. 坐标系统与投影

### 7.1 坐标转换

#### SRID转换

```sql
-- WGS84 (4326) → Web Mercator (3857)
SELECT
    ST_AsText(location) AS wgs84,
    ST_AsText(ST_Transform(location, 3857)) AS web_mercator
FROM cities
WHERE name = 'Beijing';

-- 输出：
-- wgs84: POINT(116.4074 39.9042)
-- web_mercator: POINT(12958938 4825777)

-- 批量转换表
UPDATE cities
SET location_web_mercator = ST_Transform(location, 3857);
```

#### 中国坐标系

```sql
-- WGS84 (4326) → CGCS2000 (4490)
SELECT
    name,
    ST_AsText(location) AS wgs84,
    ST_AsText(ST_Transform(location, 4490)) AS cgcs2000
FROM cities;

-- WGS84 → 高斯-克吕格投影（用于大比例尺地图）
-- 北京：东经116°，使用6度带，中央经线117°
SELECT ST_Transform(
    ST_SetSRID(ST_MakePoint(116.4074, 39.9042), 4326),
    2435  -- CGCS2000 / Gauss-Kruger CM 117E
) AS gauss_kruger;
```

### 7.2 自定义投影

```sql
-- 添加自定义坐标系
INSERT INTO spatial_ref_sys (srid, auth_name, auth_srid, proj4text, srtext)
VALUES (
    999999,
    'CUSTOM',
    999999,
    '+proj=aeqd +lat_0=39.9042 +lon_0=116.4074 +x_0=0 +y_0=0 +ellps=WGS84 +units=m +no_defs',
    'LOCAL_CS["Beijing Centered",LOCAL_DATUM["Beijing",0],UNIT["meter",1]]'
);

-- 使用自定义投影（以北京为中心的等距离投影）
SELECT ST_Transform(
    ST_SetSRID(ST_MakePoint(121.4737, 31.2304), 4326),  -- 上海
    999999
) AS shanghai_from_beijing;
```

---

## 8. 空间关系与拓扑

### 8.1 拓扑数据模型

#### 创建拓扑

```sql
-- 启用拓扑扩展
CREATE EXTENSION postgis_topology;

-- 创建拓扑架构
SELECT topology.CreateTopology('city_topo', 4326, 0.0001);

-- 添加拓扑层
SELECT topology.AddTopoGeometryColumn(
    'city_topo', 'public', 'districts', 'topo_boundary', 'POLYGON'
);

-- 将几何转换为拓扑
UPDATE districts
SET topo_boundary = topology.toTopoGeom(boundary, 'city_topo', 1, 0.0001);

-- 验证拓扑
SELECT topology.ValidateTopology('city_topo');
```

#### 拓扑优势

```text
传统几何 vs 拓扑：

几何存储：
区A: POLYGON((0 0, 10 0, 10 10, 0 10, 0 0))
区B: POLYGON((10 0, 20 0, 20 10, 10 10, 10 0))
共享边界存储两次！→ 冗余、不一致风险

拓扑存储：
节点: N1(10,0), N2(10,10)
边: E1(N1→N2)
面: 区A使用E1，区B使用E1
共享边界只存储一次！→ 无冗余、保证一致性
```

### 8.2 拓扑查询

```sql
-- 查找相邻面
SELECT
    a.name AS district1,
    b.name AS district2
FROM districts a, districts b
WHERE a.id < b.id
  AND topology.ST_Equals(
      topology.GetTopoGeomElements(a.topo_boundary),
      topology.GetTopoGeomElements(b.topo_boundary)
  );

-- 查找孤立边（拓扑错误）
SELECT edge_id, ST_AsText(geom)
FROM city_topo.edge_data
WHERE left_face = 0 AND right_face = 0;
```

---

## 9. 高级空间分析

### 9.1 缓冲区分析

```sql
-- 创建缓冲区（噪音污染区）
SELECT
    name,
    ST_Buffer(location::geography, 500) AS buffer_500m
FROM airports;

-- 分级缓冲区
SELECT
    name,
    ST_Buffer(location::geography, 200) AS high_impact,
    ST_Buffer(location::geography, 500) AS medium_impact,
    ST_Buffer(location::geography, 1000) AS low_impact
FROM factories;

-- 计算缓冲区内的人口
SELECT
    f.name AS factory_name,
    SUM(c.population) AS affected_population
FROM factories f
JOIN communities c ON ST_Within(
    c.boundary::geography,
    ST_Buffer(f.location::geography, 1000)
);
```

### 9.2 Voronoi图/泰森多边形

```sql
-- 生成服务区（最近设施）
WITH hospital_points AS (
    SELECT ST_Collect(location) AS all_hospitals
    FROM hospitals
)
SELECT
    h.name,
    ST_VoronoiPolygons(hp.all_hospitals) AS service_area
FROM hospitals h, hospital_points hp;

-- 限定范围的Voronoi图
SELECT
    h.name,
    ST_Intersection(
        ST_VoronoiPolygons(ST_Collect(h2.location)),
        city.boundary
    ) AS service_area
FROM hospitals h
CROSS JOIN hospitals h2
JOIN city_boundary city ON TRUE
GROUP BY h.name, city.boundary;
```

### 9.3 凹包与凸包

```sql
-- 凸包（最小包围多边形）
SELECT
    brand,
    ST_ConvexHull(ST_Collect(location)) AS coverage_area
FROM stores
GROUP BY brand;

-- 凹包（更贴合的服务区域）
SELECT
    brand,
    ST_ConcaveHull(ST_Collect(location), 0.8) AS service_area
FROM stores
GROUP BY brand;
-- 参数0.8表示"紧密度"，0=凸包，1=最紧密
```

### 9.4 热力图分析

```sql
-- 基于密度的热力值计算
WITH grid AS (
    -- 创建网格
    SELECT
        i, j,
        ST_MakeEnvelope(
            116.0 + i * 0.01,
            39.0 + j * 0.01,
            116.0 + (i+1) * 0.01,
            39.0 + (j+1) * 0.01,
            4326
        ) AS cell
    FROM generate_series(0, 99) i,
         generate_series(0, 99) j
)
SELECT
    g.i, g.j,
    COUNT(e.id) AS event_count,
    ST_AsGeoJSON(g.cell) AS cell_geojson
FROM grid g
LEFT JOIN events e ON ST_Within(e.location, g.cell)
GROUP BY g.i, g.j, g.cell
HAVING COUNT(e.id) > 0;
```

### 9.5 路径分析

#### 路径简化

```sql
-- Douglas-Peucker算法简化路径
SELECT
    route_name,
    ST_NPoints(path) AS original_points,
    ST_NPoints(ST_Simplify(path, 0.0001)) AS simplified_points,
    ST_AsText(ST_Simplify(path, 0.0001)) AS simplified_path
FROM routes;
```

#### 路径插值

```sql
-- 沿路径生成等间距点
SELECT
    route_name,
    ST_AsText(ST_LineInterpolatePoint(path, fraction)) AS point,
    fraction * ST_Length(path::geography) AS distance_from_start
FROM routes,
     generate_series(0, 1, 0.1) AS fraction;  -- 每10%生成一个点
```

---

## 10. 性能优化

### 10.1 查询优化

#### 使用边界框预过滤

```sql
-- ❌ 慢查询：直接使用精确空间函数
SELECT COUNT(*)
FROM points p, polygons pg
WHERE ST_Contains(pg.geom, p.geom);

-- ✅ 快查询：先用边界框过滤
SELECT COUNT(*)
FROM points p, polygons pg
WHERE pg.geom && p.geom  -- 边界框操作符（使用索引）
  AND ST_Contains(pg.geom, p.geom);  -- 精确检查
```

#### 边界框操作符

| 操作符 | 含义 | 示例 |
|--------|------|------|
| `&&` | 边界框重叠 | `geom1 && geom2` |
| `&<` | 左侧重叠 | `geom1 &< geom2` |
| `&>` | 右侧重叠 | `geom1 &> geom2` |
| `<<` | 严格左侧 | `geom1 << geom2` |
| `>>` | 严格右侧 | `geom1 >> geom2` |

### 10.2 几何简化

```sql
-- 根据缩放级别简化几何
CREATE TABLE districts_simplified AS
SELECT
    id,
    name,
    boundary AS geom_full,  -- 原始精度
    ST_Simplify(boundary, 0.001) AS geom_z10,  -- 缩放级别10
    ST_Simplify(boundary, 0.01) AS geom_z5,    -- 缩放级别5
    ST_Simplify(boundary, 0.1) AS geom_z1      -- 缩放级别1
FROM districts;

-- 查询时选择合适的精度
SELECT
    name,
    CASE
        WHEN zoom_level >= 10 THEN geom_full
        WHEN zoom_level >= 5 THEN geom_z10
        WHEN zoom_level >= 1 THEN geom_z5
        ELSE geom_z1
    END AS geom
FROM districts_simplified;
```

### 10.3 空间聚类

```sql
-- ST_ClusterKMeans: 将点分组到K个簇
WITH clustered AS (
    SELECT
        name,
        location,
        ST_ClusterKMeans(location, 5) OVER () AS cluster_id
    FROM stores
)
SELECT
    cluster_id,
    COUNT(*) AS store_count,
    ST_AsText(ST_Centroid(ST_Collect(location))) AS cluster_center
FROM clustered
GROUP BY cluster_id;

-- ST_ClusterDBSCAN: 基于密度的聚类
WITH clustered AS (
    SELECT
        name,
        location,
        ST_ClusterDBSCAN(location, eps := 0.01, minpoints := 5) OVER () AS cluster_id
    FROM stores
)
SELECT
    cluster_id,
    COUNT(*) AS store_count,
    CASE
        WHEN cluster_id IS NULL THEN 'Outlier'
        ELSE 'Cluster ' || cluster_id::text
    END AS cluster_label
FROM clustered
GROUP BY cluster_id;
```

### 10.4 物化视图加速

```sql
-- 创建物化视图缓存复杂查询
CREATE MATERIALIZED VIEW mv_district_stats AS
SELECT
    d.name AS district_name,
    d.boundary,
    COUNT(p.id) AS poi_count,
    SUM(CASE WHEN p.category = 'Restaurant' THEN 1 ELSE 0 END) AS restaurant_count,
    ST_Area(d.boundary::geography) / 1000000 AS area_km2
FROM districts d
LEFT JOIN points_of_interest p ON ST_Contains(d.boundary, p.location)
GROUP BY d.id, d.name, d.boundary;

-- 创建空间索引
CREATE INDEX mv_district_stats_boundary_idx
ON mv_district_stats USING GIST (boundary);

-- 定期刷新
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_district_stats;
```

---

## 11. 生产实战案例

### 11.1 案例1：O2O配送系统

#### 需求

- 实时查找用户附近的商家
- 智能派单（距离+运力）
- 配送路径优化

#### 实现

```sql
-- 1. 商家表
CREATE TABLE merchants (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    location GEOMETRY(Point, 4326),
    category VARCHAR(50),
    rating DECIMAL(2,1),
    delivery_range INT DEFAULT 3000  -- 配送半径（米）
);

CREATE INDEX merchants_location_gist_idx ON merchants USING GIST (location);

-- 2. 骑手表
CREATE TABLE couriers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    current_location GEOMETRY(Point, 4326),
    status VARCHAR(20),  -- available, delivering
    last_update TIMESTAMPTZ
);

CREATE INDEX couriers_location_gist_idx ON couriers USING GIST (current_location);

-- 3. 查找可配送的商家
CREATE OR REPLACE FUNCTION find_available_merchants(
    user_lon DOUBLE PRECISION,
    user_lat DOUBLE PRECISION,
    max_distance INT DEFAULT 5000
)
RETURNS TABLE (
    merchant_id INT,
    merchant_name VARCHAR,
    distance_m DOUBLE PRECISION,
    estimated_time_min INT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        m.id,
        m.name,
        ST_Distance(
            m.location::geography,
            ST_SetSRID(ST_MakePoint(user_lon, user_lat), 4326)::geography
        ) AS distance_m,
        (ST_Distance(
            m.location::geography,
            ST_SetSRID(ST_MakePoint(user_lon, user_lat), 4326)::geography
        ) / 1000 * 3 + 20)::INT AS estimated_time_min  -- 假设时速20km/h + 准备时间
    FROM merchants m
    WHERE ST_DWithin(
        m.location::geography,
        ST_SetSRID(ST_MakePoint(user_lon, user_lat), 4326)::geography,
        LEAST(max_distance, m.delivery_range)
    )
      AND m.status = 'open'
    ORDER BY distance_m
    LIMIT 20;
END;
$$ LANGUAGE plpgsql;

-- 4. 智能派单
CREATE OR REPLACE FUNCTION assign_courier(
    pickup_lon DOUBLE PRECISION,
    pickup_lat DOUBLE PRECISION,
    delivery_lon DOUBLE PRECISION,
    delivery_lat DOUBLE PRECISION
)
RETURNS TABLE (
    courier_id INT,
    courier_name VARCHAR,
    distance_to_pickup_m DOUBLE PRECISION,
    total_delivery_distance_m DOUBLE PRECISION
) AS $$
BEGIN
    RETURN QUERY
    WITH pickup_point AS (
        SELECT ST_SetSRID(ST_MakePoint(pickup_lon, pickup_lat), 4326)::geography AS geog
    ),
    delivery_point AS (
        SELECT ST_SetSRID(ST_MakePoint(delivery_lon, delivery_lat), 4326)::geography AS geog
    )
    SELECT
        c.id,
        c.name,
        ST_Distance(c.current_location::geography, p.geog) AS dist_pickup,
        ST_Distance(p.geog, d.geog) AS dist_delivery
    FROM couriers c, pickup_point p, delivery_point d
    WHERE c.status = 'available'
      AND c.last_update > NOW() - INTERVAL '5 minutes'
    ORDER BY
        ST_Distance(c.current_location::geography, p.geog)  -- 优先最近的骑手
    LIMIT 10;
END;
$$ LANGUAGE plpgsql;

-- 5. 使用示例
-- 用户在 (116.40, 39.91)
SELECT * FROM find_available_merchants(116.40, 39.91, 5000);

-- 派单
SELECT * FROM assign_courier(
    116.41, 39.92,  -- 商家位置
    116.40, 39.91   -- 用户位置
);
```

### 11.2 案例2：房产推荐系统

```sql
-- 房产表
CREATE TABLE properties (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200),
    location GEOMETRY(Point, 4326),
    price DECIMAL(12,2),
    area DECIMAL(8,2),
    bedrooms INT,
    property_type VARCHAR(50)
);

-- POI权重表
CREATE TABLE poi_types (
    type VARCHAR(50) PRIMARY KEY,
    weight DECIMAL(3,2),  -- 权重系数
    max_distance INT      -- 最大考虑距离（米）
);

INSERT INTO poi_types VALUES
('Subway', 1.5, 1000),
('School', 1.2, 2000),
('Hospital', 1.0, 3000),
('Park', 0.8, 1000),
('Mall', 0.7, 2000);

-- POI表
CREATE TABLE pois (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    type VARCHAR(50) REFERENCES poi_types(type),
    location GEOMETRY(Point, 4326)
);

CREATE INDEX pois_location_gist_idx ON pois USING GIST (location);

-- 房产评分函数
CREATE OR REPLACE FUNCTION calculate_property_score(property_id INT)
RETURNS DECIMAL(8,2) AS $$
DECLARE
    prop_location GEOMETRY;
    base_score DECIMAL(8,2) := 50.0;
    poi_score DECIMAL(8,2) := 0.0;
BEGIN
    -- 获取房产位置
    SELECT location INTO prop_location
    FROM properties WHERE id = property_id;

    -- 计算POI加分
    SELECT SUM(
        pt.weight * (1 - LEAST(
            ST_Distance(prop_location::geography, p.location::geography) / pt.max_distance,
            1.0
        ))
    ) INTO poi_score
    FROM pois p
    JOIN poi_types pt ON p.type = pt.type
    WHERE ST_DWithin(
        prop_location::geography,
        p.location::geography,
        pt.max_distance
    );

    RETURN base_score + COALESCE(poi_score, 0);
END;
$$ LANGUAGE plpgsql;

-- 推荐查询
SELECT
    p.id,
    p.title,
    p.price,
    p.area,
    calculate_property_score(p.id) AS score,
    ST_AsText(p.location) AS location
FROM properties p
WHERE p.price BETWEEN 2000000 AND 3000000
  AND p.bedrooms >= 2
  AND ST_DWithin(
      p.location::geography,
      ST_MakePoint(116.40, 39.91)::geography,
      5000  -- 用户指定的范围
  )
ORDER BY calculate_property_score(p.id) DESC
LIMIT 20;
```

### 11.3 案例3：灾害应急响应

```sql
-- 灾害区域表
CREATE TABLE disaster_zones (
    id SERIAL PRIMARY KEY,
    disaster_type VARCHAR(50),
    affected_area GEOMETRY(Polygon, 4326),
    severity VARCHAR(20),  -- low, medium, high, critical
    reported_time TIMESTAMPTZ
);

-- 应急资源表
CREATE TABLE emergency_resources (
    id SERIAL PRIMARY KEY,
    resource_type VARCHAR(50),  -- ambulance, fire_truck, rescue_team
    location GEOMETRY(Point, 4326),
    status VARCHAR(20),  -- available, deployed
    capacity INT
);

-- 受影响人口评估
CREATE OR REPLACE FUNCTION assess_affected_population(disaster_id INT)
RETURNS TABLE (
    total_population BIGINT,
    affected_buildings INT,
    critical_facilities INT
) AS $$
BEGIN
    RETURN QUERY
    WITH disaster AS (
        SELECT affected_area FROM disaster_zones WHERE id = disaster_id
    )
    SELECT
        COALESCE(SUM(c.population), 0)::BIGINT AS total_pop,
        COUNT(DISTINCT b.id)::INT AS buildings,
        COUNT(DISTINCT f.id)::INT AS critical_fac
    FROM disaster d
    LEFT JOIN communities c ON ST_Intersects(d.affected_area, c.boundary)
    LEFT JOIN buildings b ON ST_Within(b.location, d.affected_area)
    LEFT JOIN critical_facilities f ON ST_Within(f.location, d.affected_area);
END;
$$ LANGUAGE plpgsql;

-- 资源调度
CREATE OR REPLACE FUNCTION dispatch_resources(
    disaster_id INT,
    resource_type VARCHAR,
    required_count INT
)
RETURNS TABLE (
    resource_id INT,
    distance_km DECIMAL(8,2),
    eta_minutes INT
) AS $$
BEGIN
    RETURN QUERY
    WITH disaster AS (
        SELECT ST_Centroid(affected_area) AS center
        FROM disaster_zones WHERE id = disaster_id
    )
    SELECT
        r.id,
        (ST_Distance(r.location::geography, d.center::geography) / 1000)::DECIMAL(8,2),
        (ST_Distance(r.location::geography, d.center::geography) / 1000 / 60)::INT  -- 假设60km/h
    FROM emergency_resources r, disaster d
    WHERE r.resource_type = dispatch_resources.resource_type
      AND r.status = 'available'
    ORDER BY ST_Distance(r.location, d.center)
    LIMIT required_count;
END;
$$ LANGUAGE plpgsql;

-- 使用示例
-- 1. 评估影响
SELECT * FROM assess_affected_population(1);

-- 2. 调度资源
SELECT * FROM dispatch_resources(1, 'ambulance', 10);
```

---

## 12. 最佳实践

### 12.1 数据设计原则

#### ✅ 推荐做法

```sql
-- 1. 始终指定SRID
CREATE TABLE locations (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    geom GEOMETRY(Point, 4326)  -- ✅ 明确指定类型和SRID
);

-- 2. 为空间列创建索引
CREATE INDEX locations_geom_gist_idx ON locations USING GIST (geom);

-- 3. 为高频查询创建部分索引
CREATE INDEX active_locations_geom_idx ON locations USING GIST (geom)
WHERE status = 'active';

-- 4. 使用CHECK约束验证SRID
ALTER TABLE locations ADD CONSTRAINT enforce_srid_geom
CHECK (ST_SRID(geom) = 4326);

-- 5. 使用Geography类型进行长距离查询
CREATE TABLE global_locations (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    geog GEOGRAPHY(Point, 4326)  -- ✅ Geography自动球面计算
);
```

#### ❌ 避免的做法

```sql
-- ❌ 不指定SRID
CREATE TABLE bad_locations (
    geom GEOMETRY  -- 没有指定类型和SRID
);

-- ❌ 混用不同SRID（导致错误结果）
INSERT INTO locations (geom) VALUES
(ST_MakePoint(116.40, 39.91)),  -- 没有设置SRID，默认0
(ST_SetSRID(ST_MakePoint(116.40, 39.91), 4326));

-- ❌ 在Geography上使用不支持的函数
SELECT ST_Buffer(geog, 100) FROM global_locations;  -- 错误！
-- ✅ 应该先转换为Geometry
SELECT ST_Buffer(geog::geometry, 100) FROM global_locations;
```

### 12.2 性能最佳实践

#### 查询优化检查清单

- [ ] 空间列已创建索引（GiST/SP-GiST/BRIN）
- [ ] 使用`&&`边界框预过滤
- [ ] WHERE子句先过滤非空间条件
- [ ] 避免在SELECT中使用复杂空间函数
- [ ] 大表使用分区
- [ ] 复杂查询使用物化视图
- [ ] 监控`pg_stat_statements`识别慢查询

#### 监控查询

```sql
-- 查看空间查询性能
SELECT
    query,
    calls,
    mean_exec_time,
    total_exec_time
FROM pg_stat_statements
WHERE query LIKE '%ST_%' OR query LIKE '%geography%'
ORDER BY total_exec_time DESC
LIMIT 20;

-- 查看索引使用情况
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch,
    pg_size_pretty(pg_relation_size(indexrelid)) AS index_size
FROM pg_stat_user_indexes
WHERE indexname LIKE '%gist%'
ORDER BY idx_scan DESC;
```

### 12.3 数据质量保证

```sql
-- 1. 检测无效几何
SELECT id, ST_IsValid(geom), ST_IsValidReason(geom)
FROM polygons
WHERE NOT ST_IsValid(geom);

-- 2. 修复无效几何
UPDATE polygons
SET geom = ST_MakeValid(geom)
WHERE NOT ST_IsValid(geom);

-- 3. 检测重复顶点
SELECT id, ST_NPoints(geom) AS original,
       ST_NPoints(ST_RemoveRepeatedPoints(geom)) AS cleaned
FROM linestrings
WHERE ST_NPoints(geom) != ST_NPoints(ST_RemoveRepeatedPoints(geom));

-- 4. 检测自相交多边形
SELECT id, ST_IsSimple(geom)
FROM polygons
WHERE NOT ST_IsSimple(geom);
```

---

## 13. FAQ与疑难解答

### Q1: GEOMETRY和GEOGRAPHY该如何选择？

**A**:

| 场景 | 推荐类型 | 原因 |
|------|----------|------|
| 全球范围 | GEOGRAPHY | 精确的球面距离 |
| 长距离（>50km） | GEOGRAPHY | 避免投影失真 |
| 小范围、局部 | GEOMETRY | 性能更好 |
| 需要复杂空间函数 | GEOMETRY | 函数支持更全 |
| 缓冲区/面积计算 | GEOGRAPHY | 结果更准确 |

### Q2: 为什么空间查询很慢？

**诊断步骤**:

```sql
-- 1. 检查是否使用了索引
EXPLAIN ANALYZE
SELECT * FROM locations
WHERE ST_DWithin(geom, ST_MakePoint(116.40, 39.91)::geometry, 0.1);

-- 如果看到 "Seq Scan"，说明没用索引

-- 2. 检查索引是否存在
SELECT indexname, indexdef
FROM pg_indexes
WHERE tablename = 'locations';

-- 3. 检查统计信息是否过期
ANALYZE locations;

-- 4. 强制使用索引（测试）
SET enable_seqscan = OFF;
-- 测试查询
SET enable_seqscan = ON;

-- 5. 检查是否需要VACUUM
SELECT relname, n_dead_tup, last_vacuum, last_autovacuum
FROM pg_stat_user_tables
WHERE relname = 'locations';

VACUUM ANALYZE locations;
```

### Q3: 如何处理跨180度经线的几何？

```sql
-- 问题：跨越日期变更线的多边形
-- 错误示例：
SELECT ST_GeomFromText('POLYGON((170 10, -170 10, -170 -10, 170 -10, 170 10))', 4326);
-- 这会创建一个"错误"的多边形

-- 解决方案1：分割成两个多边形
SELECT ST_Union(
    ST_GeomFromText('POLYGON((170 10, 180 10, 180 -10, 170 -10, 170 10))', 4326),
    ST_GeomFromText('POLYGON((-180 10, -170 10, -170 -10, -180 -10, -180 10))', 4326)
);

-- 解决方案2：使用Web Mercator投影（如果适用）
SELECT ST_Transform(
    ST_GeomFromText('POLYGON((170 10, 190 10, 190 -10, 170 -10, 170 10))', 4326),
    3857
);
```

### Q4: 如何批量导入GeoJSON/Shapefile数据？

**导入GeoJSON**:

```bash
# 使用ogr2ogr
ogr2ogr -f "PostgreSQL" \
  PG:"dbname=mydb user=postgres" \
  data.geojson \
  -nln my_table \
  -append

# 或在SQL中
CREATE TABLE geojson_import AS
SELECT
    properties->>'name' AS name,
    properties->>'type' AS type,
    ST_SetSRID(ST_GeomFromGeoJSON(geometry), 4326) AS geom
FROM json_to_recordset(
    pg_read_file('/path/to/data.geojson')::json#>'{features}'
) AS features(properties json, geometry json);
```

**导入Shapefile**:

```bash
# 使用shp2pgsql
shp2pgsql -I -s 4326 data.shp my_table | psql -d mydb

# 参数说明：
# -I: 创建空间索引
# -s 4326: 指定SRID
# -a: 追加到现有表
# -d: 删除表后重建
# -c: 创建新表
```

### Q5: PostGIS可以做路径导航吗？

**A**: PostGIS本身不提供路径算法，但可以配合**pgRouting**扩展：

```sql
-- 安装pgRouting
CREATE EXTENSION pgrouting;

-- 准备道路网络数据（需要拓扑结构）
SELECT pgr_createTopology('roads', 0.0001, 'geom', 'id');

-- Dijkstra最短路径
SELECT * FROM pgr_dijkstra(
    'SELECT id, source, target, ST_Length(geom::geography) AS cost FROM roads',
    1,  -- 起点节点ID
    10, -- 终点节点ID
    directed := false
);

-- A*算法（更快，需要坐标）
SELECT * FROM pgr_astar(
    'SELECT id, source, target,
            ST_Length(geom::geography) AS cost,
            ST_X(ST_StartPoint(geom)) AS x1,
            ST_Y(ST_StartPoint(geom)) AS y1,
            ST_X(ST_EndPoint(geom)) AS x2,
            ST_Y(ST_EndPoint(geom)) AS y2
     FROM roads',
    1, 10, directed := false
);
```

---

## 📚 延伸阅读

### 官方资源

- [PostGIS Documentation](https://postgis.net/documentation/)
- [PostGIS Reference](https://postgis.net/docs/reference.html)
- [OGC Simple Features Specification](https://www.ogc.org/standard/sfs/)

### 工具生态

- **QGIS**: 开源GIS桌面软件
- **GeoServer**: 地图服务器
- **Leaflet/OpenLayers**: Web地图库
- **ogr2ogr/shp2pgsql**: 数据导入工具

### 推荐书籍

- 《PostGIS in Action》(3rd Edition)
- 《Mastering PostGIS》by Dominik Mikiewicz
- 《Introduction to PostGIS》by Boundless

---

## ✅ 学习检查清单

- [ ] 理解矢量/栅格数据模型
- [ ] 掌握GEOMETRY和GEOGRAPHY的区别
- [ ] 能够创建和管理空间索引
- [ ] 熟练使用空间查询函数
- [ ] 理解坐标系统和投影转换
- [ ] 能够进行空间拓扑分析
- [ ] 掌握性能优化技巧
- [ ] 能够设计和实现生产级GIS应用

---

## 💡 下一步学习

1. **进阶主题**:
   - 栅格数据处理（PostGIS Raster）
   - 点云数据（PDAL + PostGIS）
   - 3D建筑建模
   - 时空数据分析

2. **相关扩展**:
   - pgRouting: 路径规划
   - pg_tileserv: 矢量切片服务
   - pg_featureserv: OGC API服务

3. **相关课程**:
   - [分布式PostgreSQL-Citus](../05-部署架构/)
   - [PostgreSQL性能调优](../11-性能调优/)

---

**文档维护**: 本文档持续更新以反映PostGIS最新特性。
**反馈**: 如发现错误或有改进建议，请提交issue。

**版本历史**:

- v1.0 (2025-01): 初始版本，覆盖PostGIS 3.0+核心特性
