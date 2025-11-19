# PostGIS 空间数据集成

> **更新时间**: 2025 年 11 月 1 日
> **技术版本**: PostgreSQL 14+, PostGIS 3.3+
> **文档编号**: 07-03-01

## 📑 目录

- [PostGIS 空间数据集成](#postgis-空间数据集成)
  - [📑 目录](#-目录)
  - [1. 概述](#1-概述)
    - [1.1 PostGIS 简介](#11-postgis-简介)
    - [1.2 应用场景](#12-应用场景)
  - [2. PostGIS 安装配置](#2-postgis-安装配置)
    - [2.1 安装 PostGIS](#21-安装-postgis)
    - [2.2 启用扩展](#22-启用扩展)
  - [3. 空间数据类型](#3-空间数据类型)
    - [3.1 几何类型](#31-几何类型)
    - [3.2 地理类型](#32-地理类型)
  - [4. 空间查询](#4-空间查询)
    - [4.1 距离查询](#41-距离查询)
    - [4.2 空间索引](#42-空间索引)
  - [5. 与向量搜索结合](#5-与向量搜索结合)
    - [5.1 混合查询](#51-混合查询)
  - [6. 实践案例](#6-实践案例)
    - [6.1 附近商家推荐](#61-附近商家推荐)
  - [7. 参考资料](#7-参考资料)

---

## 1. 概述

### 1.1 PostGIS 简介

PostGIS 是 PostgreSQL 的空间数据扩展，支持：

- **几何数据类型**: POINT、LINESTRING、POLYGON 等
- **地理数据类型**: 经纬度坐标
- **空间索引**: GiST 索引
- **空间函数**: 距离计算、相交判断等

### 1.2 应用场景

- **地理位置搜索**: 附近的人、附近的商家
- **地理围栏**: 区域判断
- **路径规划**: 最短路径计算
- **空间分析**: 地理数据分析

## 2. PostGIS 安装配置

### 2.1 安装 PostGIS

```bash
# Ubuntu/Debian
sudo apt-get install postgresql-14-postgis

# macOS
brew install postgis

# Docker
docker run -d \
  --name postgres-postgis \
  -e POSTGRES_PASSWORD=password \
  postgis/postgis:14-3.3
```

### 2.2 启用扩展

```sql
-- 创建数据库
CREATE DATABASE geodb;

-- 连接到数据库
\c geodb

-- 启用 PostGIS 扩展
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;
```

## 3. 空间数据类型

### 3.1 几何类型

```sql
-- 创建包含空间数据的表
CREATE TABLE locations (
    id SERIAL PRIMARY KEY,
    name TEXT,
    geom GEOMETRY(POINT, 4326),  -- 点类型，WGS84坐标系
    address TEXT
);

-- 插入空间数据
INSERT INTO locations (name, geom, address) VALUES (
    'Beijing',
    ST_SetSRID(ST_MakePoint(116.4074, 39.9042), 4326),
    '北京市'
);
```

### 3.2 地理类型

```sql
-- 使用地理类型（更适合距离计算）
CREATE TABLE locations_geog (
    id SERIAL PRIMARY KEY,
    name TEXT,
    geog GEOGRAPHY(POINT, 4326)
);

-- 插入地理数据
INSERT INTO locations_geog (name, geog) VALUES (
    'Shanghai',
    ST_SetSRID(ST_MakePoint(121.4737, 31.2304), 4326)::GEOGRAPHY
);
```

## 4. 空间查询

### 4.1 距离查询

```sql
-- 查询附近的点（使用几何类型）
SELECT name, ST_Distance(geom, ST_MakePoint(116.4074, 39.9042)) AS distance
FROM locations
ORDER BY geom <-> ST_MakePoint(116.4074, 39.9042)
LIMIT 10;

-- 查询附近的点（使用地理类型，更准确）
SELECT name, ST_Distance(geog, ST_MakePoint(121.4737, 31.2304)::GEOGRAPHY) AS distance
FROM locations_geog
WHERE ST_DWithin(
    geog,
    ST_MakePoint(121.4737, 31.2304)::GEOGRAPHY,
    10000  -- 10公里
)
ORDER BY geog <-> ST_MakePoint(121.4737, 31.2304)::GEOGRAPHY;
```

### 4.2 空间索引

```sql
-- 创建空间索引
CREATE INDEX idx_locations_geom ON locations USING GIST(geom);
CREATE INDEX idx_locations_geog ON locations_geog USING GIST(geog);

-- 使用索引查询
SELECT * FROM locations
WHERE ST_DWithin(
    geom,
    ST_MakePoint(116.4074, 39.9042),
    0.1  -- 约10公里（度单位）
);
```

## 5. 与向量搜索结合

### 5.1 混合查询

```sql
-- 结合空间搜索和向量搜索
CREATE TABLE places (
    id SERIAL PRIMARY KEY,
    name TEXT,
    description TEXT,
    location GEOGRAPHY(POINT, 4326),
    embedding vector(1536)
);

-- 创建索引
CREATE INDEX idx_places_location ON places USING GIST(location);
CREATE INDEX idx_places_embedding ON places USING hnsw (embedding vector_cosine_ops);

-- 混合查询：语义相似 + 地理位置
WITH semantic_search AS (
    SELECT id, embedding <=> query_vector AS semantic_distance
    FROM places
    ORDER BY embedding <=> query_vector
    LIMIT 100
),
spatial_search AS (
    SELECT id, location <-> user_location::GEOGRAPHY AS spatial_distance
    FROM places
    WHERE ST_DWithin(location, user_location::GEOGRAPHY, 5000)
)
SELECT
    p.id,
    p.name,
    ss.semantic_distance,
    sp.spatial_distance,
    (1.0 / (60 + ROW_NUMBER() OVER (ORDER BY ss.semantic_distance))) +
    (1.0 / (60 + ROW_NUMBER() OVER (ORDER BY sp.spatial_distance))) AS combined_score
FROM places p
JOIN semantic_search ss ON p.id = ss.id
JOIN spatial_search sp ON p.id = sp.id
ORDER BY combined_score DESC
LIMIT 10;
```

## 6. 实践案例

### 6.1 附近商家推荐

```python
# 附近商家推荐（语义 + 地理位置）
class NearbyBusinessRecommendation:
    async def recommend(self, query_text, user_location, radius=5000):
        # 1. 生成查询向量
        query_vector = await self.embedder.embed(query_text)

        # 2. 执行混合查询
        results = await self.db.fetch("""
            WITH semantic_results AS (
                SELECT id, embedding <=> $1::vector AS semantic_score
                FROM businesses
                ORDER BY embedding <=> $1::vector
                LIMIT 50
            ),
            spatial_results AS (
                SELECT id,
                       location <-> $2::GEOGRAPHY AS spatial_distance
                FROM businesses
                WHERE ST_DWithin(location, $2::GEOGRAPHY, $3)
            )
            SELECT
                b.id,
                b.name,
                b.description,
                sr.semantic_score,
                sp.spatial_distance,
                (1.0 / (60 + sr.semantic_score * 1000)) +
                (1.0 / (60 + sp.spatial_distance / 1000)) AS combined_score
            FROM businesses b
            JOIN semantic_results sr ON b.id = sr.id
            JOIN spatial_results sp ON b.id = sp.id
            ORDER BY combined_score DESC
            LIMIT 10
        """, query_vector, user_location, radius)

        return results
```

## 7. 参考资料

- [PostGIS 官方文档](https://postgis.net/documentation/)
- [PostgreSQL 空间数据](https://www.postgresql.org/docs/current/datatype-geometric.html)

---

**最后更新**: 2025 年 11 月 1 日
**维护者**: PostgreSQL Modern Team
**文档编号**: 07-03-01
