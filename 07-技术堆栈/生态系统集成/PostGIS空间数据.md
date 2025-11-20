# 7.2.1 PostGIS 空间数据

> **更新时间**: 2025 年 11 月 1 日  
> **技术版本**: PostGIS 3.4+, PostgreSQL 18+  
> **文档编号**: 07-02-01

## 📑 目录

- [7.2.1 PostGIS 空间数据](#721-postgis-空间数据)
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
    - [3.1 GiST 索引](#31-gist-索引)
    - [3.2 SP-GiST 索引](#32-sp-gist-索引)
  - [4. 空间查询](#4-空间查询)
    - [4.1 空间关系查询](#41-空间关系查询)
    - [4.2 空间分析查询](#42-空间分析查询)
  - [5. 最佳实践](#5-最佳实践)
    - [5.1 数据模型建议](#51-数据模型建议)
    - [5.2 查询优化建议](#52-查询优化建议)
  - [6. 参考资料](#6-参考资料)

---

## 1. 概述

### 1.1 技术背景

**问题需求**:

PostGIS 为 PostgreSQL 添加空间数据支持，支持地理信息系统（GIS）应用，适用于位置服务、地图应用等场景
。

**技术演进**:

1. **2001 年**: PostGIS 项目启动
2. **2010 年**: PostGIS 2.0 发布
3. **2020 年**: PostGIS 3.0 发布
4. **2025 年**: PostGIS 3.4 优化性能

### 1.2 技术定位

PostGIS 空间数据提供完整的地理空间数据处理能力，扩展 PostgreSQL 的空间数据功能。

### 1.3 核心价值

- **空间数据**: 支持空间数据类型
- **空间查询**: 支持空间查询和分析
- **性能优化**: 优化空间查询性能

---

## 2. 空间数据类型

### 2.1 几何类型

**几何类型**:

```sql
-- 创建空间表
CREATE TABLE locations (
    id SERIAL PRIMARY KEY,
    name TEXT,
    geom GEOMETRY(POINT, 4326)
);

-- 插入空间数据
INSERT INTO locations (name, geom)
VALUES ('Beijing', ST_GeomFromText('POINT(116.4074 39.9042)', 4326));
```

### 2.2 地理类型

**地理类型**:

```sql
-- 使用地理类型
CREATE TABLE cities (
    id SERIAL PRIMARY KEY,
    name TEXT,
    location GEOGRAPHY(POINT, 4326)
);
```

### 2.3 栅格类型

**栅格类型**:

```sql
-- 栅格数据
CREATE TABLE rasters (
    id SERIAL PRIMARY KEY,
    name TEXT,
    rast RASTER
);
```

---

## 3. 空间索引

### 3.1 GiST 索引

**索引创建**:

```sql
-- 创建空间索引
CREATE INDEX idx_locations_geom ON locations USING GIST (geom);
```

### 3.2 SP-GiST 索引

**SP-GiST 索引**:

```sql
-- 创建 SP-GiST 索引
CREATE INDEX idx_locations_geom_spgist ON locations USING SPGIST (geom);
```

---

## 4. 空间查询

### 4.1 空间关系查询

**关系查询**:

```sql
-- 查找附近的点
SELECT name, ST_Distance(geom, ST_GeomFromText('POINT(116.4074 39.9042)', 4326)) AS distance
FROM locations
ORDER BY geom <-> ST_GeomFromText('POINT(116.4074 39.9042)', 4326)
LIMIT 10;

-- 查找包含的点
SELECT * FROM locations
WHERE ST_Contains(
    ST_GeomFromText('POLYGON(...)', 4326),
    geom
);
```

### 4.2 空间分析查询

**分析查询**:

```sql
-- 计算面积
SELECT name, ST_Area(geom) AS area
FROM polygons;

-- 计算距离
SELECT ST_Distance(
    ST_GeomFromText('POINT(116.4074 39.9042)', 4326),
    ST_GeomFromText('POINT(121.4737 31.2304)', 4326)
) AS distance;
```

---

## 5. 最佳实践

### 5.1 数据模型建议

- **坐标系选择**: 选择合适的坐标系
- **几何类型**: 选择合适的几何类型
- **索引创建**: 创建空间索引

### 5.2 查询优化建议

- **索引使用**: 使用空间索引
- **查询重写**: 优化查询语句
- **批量操作**: 使用批量操作

---

## 6. 参考资料

- [PostGIS 文档](https://postgis.net/documentation/)
- [空间数据教程](https://postgis.net/workshops/postgis-intro/)

---

**最后更新**: 2025 年 11 月 1 日  
**维护者**: PostgreSQL Modern Team
