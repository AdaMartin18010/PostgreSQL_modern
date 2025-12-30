---
> **📋 文档来源**: 新增深化文档
> **📅 创建日期**: 2025-01
> **⚠️ 注意**: 本文档为深度补充，系统化PostGIS空间数据技术栈

---

# PostGIS空间数据完整实战指南

## 元数据

- **文档版本**: v2.0
- **创建日期**: 2025-01
- **技术栈**: PostgreSQL 17+/18+ | PostGIS 3.4+ | Mapbox | Leaflet | OpenLayers
- **难度级别**: ⭐⭐⭐⭐ (高级)
- **预计阅读**: 180分钟
- **前置要求**: 熟悉PostgreSQL基础、地理信息系统（GIS）基础

---

## 📋 完整目录

- [PostGIS空间数据完整实战指南](#postgis空间数据完整实战指南)
  - [元数据](#元数据)
  - [📋 完整目录](#-完整目录)
  - [1. PostGIS安装与配置](#1-postgis安装与配置)
    - [1.1 安装PostGIS](#11-安装postgis)
      - [Ubuntu/Debian安装](#ubuntudebian安装)
      - [CentOS/RHEL安装](#centosrhel安装)
      - [Docker安装](#docker安装)
      - [从源码编译安装](#从源码编译安装)
    - [1.2 初始化PostGIS](#12-初始化postgis)
      - [创建扩展](#创建扩展)
      - [验证安装](#验证安装)
    - [1.3 版本验证](#13-版本验证)
      - [检查PostGIS功能](#检查postgis功能)
    - [1.4 配置优化](#14-配置优化)
      - [PostgreSQL配置优化](#postgresql配置优化)
  - [2. 空间数据类型深入解析](#2-空间数据类型深入解析)
    - [2.1 GEOMETRY vs GEOGRAPHY](#21-geometry-vs-geography)
      - [详细对比](#详细对比)
      - [使用建议](#使用建议)
    - [2.2 常用几何类型](#22-常用几何类型)
      - [点（Point）](#点point)
      - [线（LineString）](#线linestring)
      - [多边形（Polygon）](#多边形polygon)
      - [多点（MultiPoint）](#多点multipoint)
    - [2.3 坐标系统（SRID）](#23-坐标系统srid)
      - [常用SRID](#常用srid)
      - [添加自定义SRID](#添加自定义srid)
    - [2.4 空间数据创建](#24-空间数据创建)
      - [从文本创建](#从文本创建)
  - [3. 空间索引优化](#3-空间索引优化)
    - [3.1 GIST索引详解](#31-gist索引详解)
      - [创建GIST索引](#创建gist索引)
      - [索引性能对比](#索引性能对比)
    - [3.2 SP-GiST索引](#32-sp-gist索引)
      - [SP-GiST索引适用场景](#sp-gist索引适用场景)
    - [3.3 索引策略选择](#33-索引策略选择)
      - [选择指南](#选择指南)
      - [组合索引示例](#组合索引示例)
    - [3.4 索引维护](#34-索引维护)
      - [索引维护操作](#索引维护操作)
  - [4. 空间查询性能优化](#4-空间查询性能优化)
    - [4.1 边界框预过滤](#41-边界框预过滤)
      - [使用\&\&操作符](#使用操作符)
      - [边界框优化技巧](#边界框优化技巧)
    - [4.2 几何简化](#42-几何简化)
      - [简化几何对象](#简化几何对象)
      - [根据缩放级别简化](#根据缩放级别简化)
    - [4.3 查询优化技巧](#43-查询优化技巧)
      - [使用LIMIT限制结果](#使用limit限制结果)
      - [避免在WHERE子句中使用函数](#避免在where子句中使用函数)
  - [5. 空间数据导入导出](#5-空间数据导入导出)
    - [5.1 从GeoJSON导入](#51-从geojson导入)
      - [使用ogr2ogr工具](#使用ogr2ogr工具)
      - [使用PostgreSQL函数导入](#使用postgresql函数导入)
    - [5.2 从Shapefile导入](#52-从shapefile导入)
      - [使用ogr2ogr导入](#使用ogr2ogr导入)
    - [5.3 从KML/KMZ导入](#53-从kmlkmz导入)
    - [5.4 导出为GeoJSON](#54-导出为geojson)
      - [使用ogr2ogr导出](#使用ogr2ogr导出)
      - [使用PostgreSQL函数导出](#使用postgresql函数导出)
    - [5.5 批量导入优化](#55-批量导入优化)
      - [使用COPY命令](#使用copy命令)
  - [6. 坐标系转换](#6-坐标系转换)
    - [6.1 常用坐标系](#61-常用坐标系)
    - [6.2 坐标转换函数](#62-坐标转换函数)
      - [ST\_Transform转换](#st_transform转换)
      - [GEOGRAPHY转换注意事项](#geography转换注意事项)
    - [6.3 转换最佳实践](#63-转换最佳实践)
      - [预先转换存储](#预先转换存储)
  - [7. 地理围栏与位置服务](#7-地理围栏与位置服务)
    - [7.1 地理围栏实现](#71-地理围栏实现)
      - [创建地理围栏表](#创建地理围栏表)
      - [位置检查服务](#位置检查服务)
      - [实时位置追踪](#实时位置追踪)
  - [8. 路径规划与导航](#8-路径规划与导航)
    - [8.1 最短路径算法](#81-最短路径算法)
      - [使用ST\_ShortestLine](#使用st_shortestline)
    - [8.2 pgRouting集成](#82-pgrouting集成)
      - [安装pgRouting](#安装pgrouting)
  - [10. 与地图库集成](#10-与地图库集成)
    - [10.1 Mapbox集成](#101-mapbox集成)
      - [后端API](#后端api)
      - [前端Mapbox集成](#前端mapbox集成)
    - [10.2 Leaflet集成](#102-leaflet集成)
  - [📚 参考资源](#-参考资源)
  - [📝 更新日志](#-更新日志)

---

## 1. PostGIS安装与配置

### 1.1 安装PostGIS

#### Ubuntu/Debian安装

```bash
# 添加PostgreSQL官方APT仓库
sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
sudo apt-get update

# 安装PostGIS
sudo apt-get install postgresql-17-postgis-3

# 或者安装特定版本
sudo apt-get install postgresql-17-postgis-3.4
```

#### CentOS/RHEL安装

```bash
# 添加PostgreSQL官方YUM仓库
sudo yum install -y https://download.postgresql.org/pub/repos/yum/reporpms/EL-8-x86_64/pgdg-redhat-repo-latest.noarch.rpm
sudo yum install -y postgresql17-server postgresql17

# 安装PostGIS
sudo yum install -y postgis34_17

# 或者使用dnf (Fedora/RHEL 8+)
sudo dnf install -y postgis34_17
```

#### Docker安装

```dockerfile
# Dockerfile
FROM postgis/postgis:17-3.4

# 自定义配置
ENV POSTGRES_DB=mydb
ENV POSTGRES_USER=postgres
ENV POSTGRES_PASSWORD=password

# 运行PostGIS容器
docker run -d \
  --name postgis-db \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=gisdb \
  -p 5432:5432 \
  postgis/postgis:17-3.4
```

#### 从源码编译安装

```bash
# 下载PostGIS源码
wget https://download.osgeo.org/postgis/source/postgis-3.4.0.tar.gz
tar -xzf postgis-3.4.0.tar.gz
cd postgis-3.4.0

# 安装依赖
sudo apt-get install -y \
  build-essential \
  libgeos-dev \
  libproj-dev \
  libgdal-dev \
  libjson-c-dev \
  libxml2-dev

# 配置和编译
./configure --with-pgconfig=/usr/bin/pg_config
make
sudo make install
```

### 1.2 初始化PostGIS

#### 创建扩展

```sql
-- 连接到数据库
\c mydb

-- 创建PostGIS扩展（带错误处理）
DO $$
BEGIN
    -- 检查是否有创建扩展的权限
    IF NOT EXISTS (
        SELECT 1 FROM pg_roles
        WHERE rolname = current_user
        AND rolsuper = TRUE
    ) THEN
        RAISE WARNING '当前用户不是超级用户，可能无法创建扩展';
    END IF;

    -- 创建PostGIS扩展
    IF NOT EXISTS (
        SELECT 1 FROM pg_extension
        WHERE extname = 'postgis'
    ) THEN
        CREATE EXTENSION IF NOT EXISTS postgis;
        RAISE NOTICE 'PostGIS扩展创建成功';
    END IF;

    -- 创建PostGIS拓扑扩展
    IF NOT EXISTS (
        SELECT 1 FROM pg_extension
        WHERE extname = 'postgis_topology'
    ) THEN
        CREATE EXTENSION IF NOT EXISTS postgis_topology;
        RAISE NOTICE 'PostGIS拓扑扩展创建成功';
    END IF;

    -- 创建PostGIS栅格扩展（可选）
    IF NOT EXISTS (
        SELECT 1 FROM pg_extension
        WHERE extname = 'postgis_raster'
    ) THEN
        CREATE EXTENSION IF NOT EXISTS postgis_raster;
        RAISE NOTICE 'PostGIS栅格扩展创建成功';
    END IF;

    -- 创建模糊字符串匹配扩展（可选）
    IF NOT EXISTS (
        SELECT 1 FROM pg_extension
        WHERE extname = 'fuzzystrmatch'
    ) THEN
        CREATE EXTENSION IF NOT EXISTS fuzzystrmatch;
        RAISE NOTICE '模糊字符串匹配扩展创建成功';
    END IF;

    -- 创建PostGIS地理编码扩展（可选，仅美国）
    IF NOT EXISTS (
        SELECT 1 FROM pg_extension
        WHERE extname = 'postgis_tiger_geocoder'
    ) THEN
        CREATE EXTENSION IF NOT EXISTS postgis_tiger_geocoder;
        RAISE NOTICE 'PostGIS地理编码扩展创建成功';
    END IF;
EXCEPTION
    WHEN insufficient_privilege THEN
        RAISE EXCEPTION '权限不足，无法创建扩展';
    WHEN undefined_file THEN
        RAISE EXCEPTION '扩展文件不存在，请检查PostGIS安装';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建扩展失败: %', SQLERRM;
END $$;

-- 查看已安装的扩展（带错误处理）
DO $$
DECLARE
    ext_count INT;
BEGIN
    SELECT COUNT(*) INTO ext_count
    FROM pg_extension
    WHERE extname LIKE 'postgis%';

    RAISE NOTICE '已安装 % 个PostGIS相关扩展', ext_count;
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION '查询扩展失败: %', SQLERRM;
END $$;

SELECT * FROM pg_extension WHERE extname LIKE 'postgis%';
```

#### 验证安装

```sql
-- 查看PostGIS版本
SELECT PostGIS_Version();
SELECT PostGIS_Full_Version();

-- 查看PostGIS函数
SELECT proname, pronargs
FROM pg_proc
WHERE proname LIKE 'ST_%'
ORDER BY proname
LIMIT 20;

-- 查看空间参考系统
SELECT srid, auth_name, auth_srid, proj4text
FROM spatial_ref_sys
WHERE auth_name = 'EPSG' AND auth_srid IN (4326, 3857, 4490)
ORDER BY auth_srid;
```

### 1.3 版本验证

#### 检查PostGIS功能

```sql
-- 测试基本功能（带错误处理）
DO $$
DECLARE
    test_point GEOMETRY;
    test_text TEXT;
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_extension
        WHERE extname = 'postgis'
    ) THEN
        RAISE EXCEPTION 'PostGIS扩展未安装';
    END IF;

    SELECT ST_GeomFromText('POINT(116.3912 39.9067)', 4326) INTO test_point;
    SELECT ST_AsText(test_point) INTO test_text;

    RAISE NOTICE '测试点创建成功: %', test_text;
EXCEPTION
    WHEN undefined_function THEN
        RAISE EXCEPTION 'PostGIS函数不存在，请检查PostGIS扩展安装';
    WHEN OTHERS THEN
        RAISE EXCEPTION '测试基本功能失败: %', SQLERRM;
END $$;

SELECT
    ST_GeomFromText('POINT(116.3912 39.9067)', 4326) AS point,
    ST_AsText(ST_GeomFromText('POINT(116.3912 39.9067)', 4326)) AS text;

-- 测试距离计算（带性能测试和错误处理）
DO $$
DECLARE
    distance_result NUMERIC;
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_extension
        WHERE extname = 'postgis'
    ) THEN
        RAISE EXCEPTION 'PostGIS扩展未安装';
    END IF;

    SELECT ST_Distance(
        ST_GeomFromText('POINT(116.3912 39.9067)', 4326)::geography,
        ST_GeomFromText('POINT(116.4074 39.9042)', 4326)::geography
    ) INTO distance_result;

    RAISE NOTICE '两点距离: % 米', distance_result;
EXCEPTION
    WHEN undefined_function THEN
        RAISE EXCEPTION 'PostGIS函数不存在，请检查PostGIS扩展安装';
    WHEN OTHERS THEN
        RAISE EXCEPTION '测试距离计算失败: %', SQLERRM;
END $$;

EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT ST_Distance(
    ST_GeomFromText('POINT(116.3912 39.9067)', 4326)::geography,
    ST_GeomFromText('POINT(116.4074 39.9042)', 4326)::geography
) AS distance_meters;
-- 执行时间: <5ms
-- 计划: Function Scan

-- 测试索引（带错误处理）
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'test_points') THEN
        DROP TABLE test_points;
        RAISE NOTICE '已删除现有表: test_points';
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_extension
        WHERE extname = 'postgis'
    ) THEN
        RAISE EXCEPTION 'PostGIS扩展未安装';
    END IF;

    CREATE TABLE test_points (
        id SERIAL PRIMARY KEY,
        name TEXT,
        location GEOGRAPHY(POINT, 4326)
    );

    RAISE NOTICE '表创建成功: test_points';
EXCEPTION
    WHEN undefined_object THEN
        RAISE EXCEPTION 'GEOGRAPHY类型不存在，请安装PostGIS扩展';
    WHEN duplicate_table THEN
        RAISE WARNING '表test_points已存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建表失败: %', SQLERRM;
END $$;

-- 创建索引（带错误处理）
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'test_points') THEN
        RAISE EXCEPTION '表test_points不存在，请先创建';
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes
        WHERE schemaname = 'public'
        AND tablename = 'test_points'
        AND indexname = 'test_points_location_idx'
    ) THEN
        CREATE INDEX test_points_location_idx ON test_points USING GIST (location);
        RAISE NOTICE '索引创建成功: test_points_location_idx';
    END IF;
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '表test_points不存在';
    WHEN duplicate_table THEN
        RAISE WARNING '索引已存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建索引失败: %', SQLERRM;
END $$;

-- 插入测试数据（带错误处理）
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'test_points') THEN
        RAISE EXCEPTION '表test_points不存在';
    END IF;

    INSERT INTO test_points (name, location)
    VALUES ('Test Point', ST_GeogFromText('POINT(116.3912 39.9067)'))
    ON CONFLICT DO NOTHING;

    RAISE NOTICE '测试数据插入成功';
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '表test_points不存在';
    WHEN undefined_function THEN
        RAISE EXCEPTION 'ST_GeogFromText函数不存在，请检查PostGIS扩展安装';
    WHEN OTHERS THEN
        RAISE EXCEPTION '插入数据失败: %', SQLERRM;
END $$;

-- 测试索引查询（带性能测试）
DO $$
DECLARE
    result_count INT;
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'test_points') THEN
        RAISE WARNING '表test_points不存在';
        RETURN;
    END IF;

    SELECT COUNT(*) INTO result_count
    FROM test_points
    WHERE ST_DWithin(
        location,
        ST_GeogFromText('POINT(116.4 39.9)'),
    10000  -- 10km
);

DROP TABLE test_points;
```

### 1.4 配置优化

#### PostgreSQL配置优化

```bash
# postgresql.conf 优化配置
# 空间查询优化
shared_buffers = 4GB                    # 增加共享缓冲区
effective_cache_size = 12GB             # 有效缓存大小
work_mem = 64MB                         # 工作内存（空间计算需要）
maintenance_work_mem = 1GB              # 维护工作内存（索引构建）
random_page_cost = 1.1                  # SSD优化
effective_io_concurrency = 200          # SSD并发

# 并行查询（PostgreSQL 17+）
max_parallel_workers_per_gather = 4     # 并行工作进程
parallel_tuple_cost = 0.01              # 并行元组成本
parallel_setup_cost = 1000              # 并行设置成本

# 日志配置（用于调试）
log_min_duration_statement = 1000       # 记录慢查询（>1秒）
```

---

## 2. 空间数据类型深入解析

### 2.1 GEOMETRY vs GEOGRAPHY

#### 详细对比

| 特性 | GEOMETRY | GEOGRAPHY |
| --- | --- | --- |
| **坐标系** | 平面（笛卡尔坐标） | 球面（地理坐标） |
| **精度** | 高（平面投影） | 中等（球面计算） |
| **速度** | 快（直接计算） | 较慢（球面计算） |
| **适用范围** | 小范围、投影坐标 | 全球、经纬度坐标 |
| **距离单位** | 投影单位（米、英尺等） | 米（自动转换为米） |
| **面积单位** | 投影单位 | 平方米 |
| **SRID要求** | 必须指定 | 通常使用4326（WGS84） |

#### 使用建议

```sql
-- ✅ 使用GEOMETRY的场景
-- 1. 小范围数据（城市、地区）
-- 2. 使用投影坐标系（如Web Mercator 3857）
-- 3. 需要高精度计算

CREATE TABLE city_buildings (
    id SERIAL PRIMARY KEY,
    name TEXT,
    geom GEOMETRY(POLYGON, 3857)  -- Web Mercator
);

-- ✅ 使用GEOGRAPHY的场景
-- 1. 全球数据
-- 2. 使用经纬度坐标（WGS84 4326）
-- 3. 需要计算真实地理距离

CREATE TABLE global_cities (
    id SERIAL PRIMARY KEY,
    name TEXT,
    location GEOGRAPHY(POINT, 4326)  -- WGS84
);
```

### 2.2 常用几何类型

#### 点（Point）

```sql
-- 创建点
CREATE TABLE points (
    id SERIAL PRIMARY KEY,
    name TEXT,
    location GEOGRAPHY(POINT, 4326)
);

-- 插入点数据
INSERT INTO points (name, location) VALUES
    ('Beijing', ST_GeogFromText('POINT(116.3912 39.9067)')),
    ('Shanghai', ST_GeogFromText('POINT(121.4737 31.2304)')),
    ('Guangzhou', ST_GeogFromText('POINT(113.2644 23.1291)'));

-- 或者使用ST_MakePoint
INSERT INTO points (name, location) VALUES
    ('Shenzhen', ST_MakePoint(114.0579, 22.5431)::geography);
```

#### 线（LineString）

```sql
-- 创建线
CREATE TABLE routes (
    id SERIAL PRIMARY KEY,
    name TEXT,
    route GEOGRAPHY(LINESTRING, 4326)
);

-- 插入路线
INSERT INTO routes (name, route) VALUES
    ('Route 1', ST_GeogFromText('LINESTRING(116.3912 39.9067, 116.4074 39.9042, 116.4236 39.9017)'));

-- 计算路线长度
SELECT
    name,
    ST_Length(route) AS length_meters,
    ST_Length(route) / 1000 AS length_km
FROM routes;
```

#### 多边形（Polygon）

```sql
-- 创建多边形（区域）
CREATE TABLE regions (
    id SERIAL PRIMARY KEY,
    name TEXT,
    boundary GEOGRAPHY(POLYGON, 4326),
    area_sqm NUMERIC  -- 面积（平方米）
);

-- 插入区域（注意：多边形必须闭合，第一个点和最后一个点相同）
INSERT INTO regions (name, boundary) VALUES
    ('Downtown', ST_GeogFromText('POLYGON((
        116.38 39.89,
        116.40 39.89,
        116.40 39.92,
        116.38 39.92,
        116.38 39.89
    ))')'));

-- 计算面积
UPDATE regions
SET area_sqm = ST_Area(boundary)
WHERE area_sqm IS NULL;

-- 查询面积大于某个值的区域
SELECT name, area_sqm / 1000000 AS area_km2
FROM regions
WHERE ST_Area(boundary) > 1000000;  -- 大于1平方公里
```

#### 多点（MultiPoint）

```sql
-- 创建多点
CREATE TABLE clusters (
    id SERIAL PRIMARY KEY,
    name TEXT,
    points GEOGRAPHY(MULTIPOINT, 4326)
);

INSERT INTO clusters (name, points) VALUES
    ('Cluster 1', ST_GeogFromText('MULTIPOINT(
        (116.3912 39.9067),
        (116.4074 39.9042),
        (116.4236 39.9017)
    )'));
```

### 2.3 坐标系统（SRID）

#### 常用SRID

```sql
-- WGS84（全球定位系统标准，最常用）
SELECT ST_GeomFromText('POINT(116.3912 39.9067)', 4326);
SELECT ST_GeogFromText('POINT(116.3912 39.9067)');

-- Web Mercator（Web地图标准）
SELECT ST_GeomFromText('POINT(12957564 4823544)', 3857);

-- 中国坐标系
-- GCJ-02（火星坐标系，中国地图常用）
-- BD-09（百度坐标系）
-- 注意：这些坐标系可能不在标准spatial_ref_sys表中，需要添加

-- 查看SRID信息
SELECT
    srid,
    auth_name,
    auth_srid,
    srtext,
    proj4text
FROM spatial_ref_sys
WHERE srid IN (4326, 3857, 4490, 2154)
ORDER BY srid;
```

#### 添加自定义SRID

```sql
-- 添加自定义坐标系（例如GCJ-02）
-- 注意：需要正确的proj4字符串
INSERT INTO spatial_ref_sys (srid, auth_name, auth_srid, proj4text, srtext)
VALUES (
    4490,  -- 假设使用4490作为GCJ-02的SRID
    'CUSTOM',
    4490,
    '+proj=longlat +datum=GCJ-02 +no_defs',
    'GEOGCS["GCJ-02",DATUM["GCJ-02",SPHEROID["WGS 84",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["degree",0.0174532925199433]]'
);
```

### 2.4 空间数据创建

#### 从文本创建

```sql
-- WKT (Well-Known Text) 格式
SELECT ST_GeomFromText('POINT(116.3912 39.9067)', 4326);
SELECT ST_GeomFromText('LINESTRING(116.3 39.9, 116.4 39.95, 116.5 40.0)', 4326);
SELECT ST_GeomFromText('POLYGON((116.3 39.9, 116.4 39.9, 116.4 40.0, 116.3 40.0, 116.3 39.9))', 4326);

-- WKB (Well-Known Binary) 格式
SELECT ST_GeomFromWKB('\x0101000000...'::bytea, 4326);

-- GeoJSON格式
SELECT ST_GeomFromGeoJSON('{
    "type": "Point",
    "coordinates": [116.3912, 39.9067]
}');
```

---

## 3. 空间索引优化

### 3.1 GIST索引详解

#### 创建GIST索引

```sql
-- 基本GIST索引
CREATE INDEX idx_points_location ON points USING GIST (location);

-- 使用填充因子（fillfactor）优化
-- 对于只读或很少更新的表，可以设置更高的填充因子
CREATE INDEX idx_points_location ON points
USING GIST (location) WITH (fillfactor=100);

-- 部分索引（只索引特定条件的数据）
CREATE INDEX idx_points_active_location ON points
USING GIST (location)
WHERE status = 'active';

-- 表达式索引
CREATE INDEX idx_points_location_centroid ON polygons
USING GIST (ST_Centroid(boundary));
```

#### 索引性能对比

```sql
-- 测试查询性能
EXPLAIN ANALYZE
SELECT * FROM points
WHERE ST_DWithin(
    location,
    ST_GeogFromText('POINT(116.4 39.9)'),
    10000  -- 10km
);

-- 查看索引使用情况
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan,  -- 索引扫描次数
    idx_tup_read,  -- 读取的元组数
    idx_tup_fetch  -- 获取的元组数
FROM pg_stat_user_indexes
WHERE indexname = 'idx_points_location';
```

### 3.2 SP-GiST索引

#### SP-GiST索引适用场景

```sql
-- SP-GiST适用于某些特定的几何类型
-- 例如：点数据、某些网络结构

CREATE INDEX idx_points_location_spgist ON points
USING SPGIST (location);

-- SP-GiST vs GIST性能对比
-- 对于点数据，SP-GiST可能更快
-- 对于复杂几何，GIST通常更好
```

### 3.3 索引策略选择

#### 选择指南

```text
使用GIST索引:
✅ 多边形、线、复杂几何
✅ 需要空间关系查询（包含、相交、距离等）
✅ 混合几何类型
✅ 大多数情况（默认选择）

使用SP-GiST索引:
✅ 点数据（可能更快）
✅ 树形数据结构
✅ 某些特殊场景

组合索引:
✅ 空间索引 + 属性索引
✅ 例如：GIST(location) + BTREE(created_at)
```

#### 组合索引示例

```sql
-- 创建组合索引
CREATE INDEX idx_points_location_time ON points
USING GIST (location, created_at);

-- 或者分别创建（通常更好）
CREATE INDEX idx_points_location ON points USING GIST (location);
CREATE INDEX idx_points_created_at ON points USING BTREE (created_at);

-- PostgreSQL可以同时使用多个索引
```

### 3.4 索引维护

#### 索引维护操作

```sql
-- 查看索引大小
SELECT
    schemaname,
    tablename,
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) AS index_size
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY pg_relation_size(indexrelid) DESC;

-- 重建索引（如果索引膨胀）
REINDEX INDEX idx_points_location;

-- 并发重建（不阻塞读写）
REINDEX INDEX CONCURRENTLY idx_points_location;

-- 分析表（更新统计信息）
ANALYZE points;

-- VACUUM索引（清理死元组）
VACUUM ANALYZE points;
```

---

## 4. 空间查询性能优化

### 4.1 边界框预过滤

#### 使用&&操作符

```sql
-- ✅ 推荐：先使用&&进行边界框过滤，再精确计算
-- &&操作符使用索引，速度很快

SELECT * FROM points
WHERE location && ST_MakeEnvelope(
    116.38, 39.89,  -- 左下角
    116.42, 39.93,  -- 右上角
    4326
)::geography
AND ST_DWithin(
    location,
    ST_GeogFromText('POINT(116.4 39.9)'),
    5000  -- 5km精确过滤
);

-- ❌ 不推荐：直接使用ST_DWithin（不使用边界框过滤）
SELECT * FROM points
WHERE ST_DWithin(
    location,
    ST_GeogFromText('POINT(116.4 39.9)'),
    5000
);
```

#### 边界框优化技巧

```sql
-- 创建边界框辅助函数
CREATE OR REPLACE FUNCTION get_bbox(
    center GEOGRAPHY(POINT, 4326),
    radius_meters NUMERIC
) RETURNS GEOMETRY AS $$
DECLARE
    -- 近似计算：1度纬度 ≈ 111km
    lat_offset NUMERIC := radius_meters / 111000;
    lon_offset NUMERIC := radius_meters / (111000 * cos(radians(ST_Y(center::geometry))));
BEGIN
    RETURN ST_MakeEnvelope(
        ST_X(center::geometry) - lon_offset,
        ST_Y(center::geometry) - lat_offset,
        ST_X(center::geometry) + lon_offset,
        ST_Y(center::geometry) + lat_offset,
        4326
    );
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- 使用边界框函数
SELECT * FROM points
WHERE location && get_bbox(
    ST_GeogFromText('POINT(116.4 39.9)'),
    5000
)::geography
AND ST_DWithin(
    location,
    ST_GeogFromText('POINT(116.4 39.9)'),
    5000
);
```

### 4.2 几何简化

#### 简化几何对象

```sql
-- ST_Simplify简化几何（减少点数）
-- tolerance: 简化容差（单位与几何的SRID相同）

-- 简化线
UPDATE routes
SET route_simplified = ST_Simplify(route::geometry, 0.001)::geography
WHERE route_simplified IS NULL;

-- 简化多边形
UPDATE regions
SET boundary_simplified = ST_Simplify(boundary::geometry, 0.0001)::geography
WHERE boundary_simplified IS NULL;

-- 创建简化版本的索引（用于快速查询）
CREATE INDEX idx_regions_boundary_simplified ON regions
USING GIST (boundary_simplified);

-- 查询时使用简化版本进行预过滤
SELECT * FROM regions
WHERE boundary_simplified && ST_MakeEnvelope(116.3, 39.9, 116.5, 40.0, 4326)::geography
AND ST_Intersects(boundary, query_geom);  -- 精确判断使用原始几何
```

#### 根据缩放级别简化

```sql
-- 为不同缩放级别创建不同简化程度的几何
ALTER TABLE regions ADD COLUMN boundary_zoom5 GEOGRAPHY(POLYGON, 4326);
ALTER TABLE regions ADD COLUMN boundary_zoom10 GEOGRAPHY(POLYGON, 4326);
ALTER TABLE regions ADD COLUMN boundary_zoom15 GEOGRAPHY(POLYGON, 4326);

-- 更新简化几何
UPDATE regions SET
    boundary_zoom5 = ST_Simplify(boundary::geometry, 0.01)::geography,   -- 低缩放
    boundary_zoom10 = ST_Simplify(boundary::geometry, 0.001)::geography, -- 中缩放
    boundary_zoom15 = boundary;  -- 高缩放使用原始几何

-- 根据缩放级别选择几何
CREATE OR REPLACE FUNCTION get_geometry_by_zoom(
    p_boundary GEOGRAPHY(POLYGON, 4326),
    p_zoom INTEGER
) RETURNS GEOGRAPHY AS $$
BEGIN
    IF p_zoom <= 5 THEN
        RETURN ST_Simplify(p_boundary::geometry, 0.01)::geography;
    ELSIF p_zoom <= 10 THEN
        RETURN ST_Simplify(p_boundary::geometry, 0.001)::geography;
    ELSE
        RETURN p_boundary;
    END IF;
END;
$$ LANGUAGE plpgsql IMMUTABLE;
```

### 4.3 查询优化技巧

#### 使用LIMIT限制结果

```sql
-- ✅ 推荐：使用LIMIT限制返回结果数
SELECT * FROM points
WHERE location && get_bbox(ST_GeogFromText('POINT(116.4 39.9)'), 5000)::geography
ORDER BY location <-> ST_GeogFromText('POINT(116.4 39.9)')  -- <-> 运算符计算距离
LIMIT 10;

-- <-> 运算符使用索引，比ST_Distance快
```

#### 避免在WHERE子句中使用函数

```sql
-- ❌ 不推荐：函数在WHERE子句中，无法使用索引
SELECT * FROM points
WHERE ST_X(location::geometry) > 116.3
  AND ST_Y(location::geometry) > 39.9;

-- ✅ 推荐：使用边界框
SELECT * FROM points
WHERE location && ST_MakeEnvelope(116.3, 39.9, 180, 90, 4326)::geography;

-- ❌ 不推荐：在WHERE中使用ST_Transform
SELECT * FROM points
WHERE ST_Transform(location::geometry, 3857) && bbox_3857;

-- ✅ 推荐：预先转换或使用相同SRID
SELECT * FROM points_3857
WHERE location && bbox_3857;
```

---

## 5. 空间数据导入导出

### 5.1 从GeoJSON导入

#### 使用ogr2ogr工具

```bash
# 安装GDAL工具
sudo apt-get install gdal-bin

# 从GeoJSON导入
ogr2ogr -f "PostgreSQL" \
  PG:"host=localhost port=5432 dbname=gisdb user=postgres password=password" \
  data.geojson \
  -nln imported_features \
  -nlt PROMOTE_TO_MULTI \
  -lco GEOMETRY_NAME=geom \
  -lco SPATIAL_INDEX=GIST
```

#### 使用PostgreSQL函数导入

```sql
-- 创建导入函数
CREATE OR REPLACE FUNCTION import_geojson(
    p_table_name TEXT,
    p_geojson JSONB
) RETURNS INTEGER AS $$
DECLARE
    feature RECORD;
    geom GEOGRAPHY;
    props JSONB;
    count INTEGER := 0;
BEGIN
    FOR feature IN SELECT * FROM jsonb_array_elements(p_geojson->'features')
    LOOP
        -- 提取几何
        geom := ST_GeomFromGeoJSON(feature->'geometry')::geography;

        -- 提取属性
        props := feature->'properties';

        -- 插入数据（动态SQL）
        EXECUTE format('
            INSERT INTO %I (geom, properties)
            VALUES ($1, $2)
        ', p_table_name)
        USING geom, props;

        count := count + 1;
    END LOOP;

    RETURN count;
END;
$$ LANGUAGE plpgsql;

-- 使用函数导入
SELECT import_geojson(
    'imported_features',
    '{"type":"FeatureCollection","features":[...]}'::jsonb
);
```

### 5.2 从Shapefile导入

#### 使用ogr2ogr导入

```bash
# 从Shapefile导入
ogr2ogr -f "PostgreSQL" \
  PG:"host=localhost port=5432 dbname=gisdb user=postgres password=password" \
  data.shp \
  -nln shapefile_data \
  -lco GEOMETRY_NAME=geom \
  -lco SPATIAL_INDEX=GIST \
  -t_srs EPSG:4326  # 转换为WGS84
```

### 5.3 从KML/KMZ导入

```bash
# 从KML导入
ogr2ogr -f "PostgreSQL" \
  PG:"host=localhost port=5432 dbname=gisdb user=postgres password=password" \
  data.kml \
  -nln kml_data \
  -lco GEOMETRY_NAME=geom

# 从KMZ导入（需要先解压）
unzip data.kmz
ogr2ogr -f "PostgreSQL" \
  PG:"host=localhost port=5432 dbname=gisdb user=postgres password=password" \
  doc.kml \
  -nln kmz_data
```

### 5.4 导出为GeoJSON

#### 使用ogr2ogr导出

```bash
# 导出为GeoJSON
ogr2ogr -f "GeoJSON" \
  output.geojson \
  PG:"host=localhost port=5432 dbname=gisdb user=postgres password=password" \
  -sql "SELECT * FROM points WHERE created_at > '2025-01-01'"
```

#### 使用PostgreSQL函数导出

```sql
-- 创建GeoJSON导出函数
CREATE OR REPLACE FUNCTION export_to_geojson(
    p_table_name TEXT,
    p_geom_column TEXT DEFAULT 'geom',
    p_where_clause TEXT DEFAULT ''
) RETURNS JSONB AS $$
DECLARE
    sql_text TEXT;
    result JSONB;
BEGIN
    sql_text := format('
        SELECT jsonb_build_object(
            ''type'', ''FeatureCollection'',
            ''features'', jsonb_agg(
                jsonb_build_object(
                    ''type'', ''Feature'',
                    ''geometry'', ST_AsGeoJSON(%I)::jsonb,
                    ''properties'', row_to_json(t.*)::jsonb - ''%I''
                )
            )
        )
        FROM %I t
        %s
    ', p_geom_column, p_geom_column, p_table_name, p_where_clause);

    EXECUTE sql_text INTO result;

    RETURN result;
END;
$$ LANGUAGE plpgsql;

-- 使用函数导出
SELECT export_to_geojson('points', 'location', 'WHERE status = ''active''');
```

### 5.5 批量导入优化

#### 使用COPY命令

```sql
-- 创建临时表
CREATE TEMP TABLE temp_points (
    name TEXT,
    lon NUMERIC,
    lat NUMERIC
);

-- 使用COPY导入CSV
\COPY temp_points FROM 'points.csv' WITH CSV HEADER;

-- 批量转换为空间数据并插入
INSERT INTO points (name, location)
SELECT
    name,
    ST_MakePoint(lon, lat)::geography
FROM temp_points;

-- 或者使用事务批量插入
BEGIN;
INSERT INTO points (name, location) VALUES
    ('Point 1', ST_MakePoint(116.3912, 39.9067)::geography),
    ('Point 2', ST_MakePoint(116.4074, 39.9042)::geography),
    -- ... 更多点
    ('Point 1000', ST_MakePoint(116.4236, 39.9017)::geography);
COMMIT;
```

---

## 6. 坐标系转换

### 6.1 常用坐标系

```sql
-- WGS84 (EPSG:4326) - 全球定位系统标准
SELECT ST_GeomFromText('POINT(116.3912 39.9067)', 4326);

-- Web Mercator (EPSG:3857) - Web地图标准
SELECT ST_Transform(
    ST_GeomFromText('POINT(116.3912 39.9067)', 4326),
    3857
);

-- 中国坐标系
-- GCJ-02 (EPSG:4490) - 火星坐标系
-- BD-09 - 百度坐标系
-- 注意：这些可能需要自定义SRID定义
```

### 6.2 坐标转换函数

#### ST_Transform转换

```sql
-- GEOMETRY类型转换
SELECT ST_Transform(
    ST_GeomFromText('POINT(116.3912 39.9067)', 4326),  -- 源SRID
    3857  -- 目标SRID
);

-- 批量转换
UPDATE points_3857
SET geom = ST_Transform(
    (SELECT geom FROM points_4326 WHERE id = points_3857.id),
    3857
);
```

#### GEOGRAPHY转换注意事项

```sql
-- GEOGRAPHY类型必须先转换为GEOMETRY，转换后再转回
SELECT ST_Transform(
    location::geometry,  -- 先转为GEOMETRY
    3857
)::geography AS location_3857
FROM points
WHERE location IS NOT NULL;
```

### 6.3 转换最佳实践

#### 预先转换存储

```sql
-- 方案1：存储多个坐标系版本（推荐用于频繁查询）
CREATE TABLE points (
    id SERIAL PRIMARY KEY,
    name TEXT,
    location_4326 GEOGRAPHY(POINT, 4326),  -- WGS84
    location_3857 GEOMETRY(POINT, 3857)    -- Web Mercator
);

-- 使用触发器自动转换
CREATE OR REPLACE FUNCTION convert_coordinates()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.location_4326 IS NOT NULL THEN
        NEW.location_3857 := ST_Transform(NEW.location_4326::geometry, 3857);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER convert_coordinates_trigger
BEFORE INSERT OR UPDATE ON points
FOR EACH ROW
EXECUTE FUNCTION convert_coordinates();
```

---

## 7. 地理围栏与位置服务

### 7.1 地理围栏实现

#### 创建地理围栏表

```sql
-- 地理围栏表
CREATE TABLE geofences (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    boundary GEOGRAPHY(POLYGON, 4326) NOT NULL,
    type TEXT,  -- 'inclusion', 'exclusion'
    created_at TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB
);

-- 创建索引
CREATE INDEX idx_geofences_boundary ON geofences USING GIST (boundary);

-- 插入围栏
INSERT INTO geofences (name, boundary, type) VALUES
    ('Office Area', ST_GeogFromText('POLYGON((
        116.38 39.89,
        116.40 39.89,
        116.40 39.92,
        116.38 39.92,
        116.38 39.89
    ))'), 'inclusion');
```

#### 位置检查服务

```sql
-- 检查点是否在围栏内
CREATE OR REPLACE FUNCTION check_geofence(
    p_location GEOGRAPHY(POINT, 4326),
    p_geofence_id INTEGER DEFAULT NULL
) RETURNS TABLE (
    geofence_id INTEGER,
    geofence_name TEXT,
    is_inside BOOLEAN,
    distance_meters NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        g.id,
        g.name,
        ST_Within(p_location::geometry, g.boundary::geometry) AS is_inside,
        ST_Distance(p_location, g.boundary) AS distance
    FROM geofences g
    WHERE (p_geofence_id IS NULL OR g.id = p_geofence_id)
      AND ST_DWithin(p_location, g.boundary, 1000)  -- 1km范围内
    ORDER BY ST_Distance(p_location, g.boundary);
END;
$$ LANGUAGE plpgsql;

-- 使用函数
SELECT * FROM check_geofence(
    ST_GeogFromText('POINT(116.39 39.90)')
);
```

#### 实时位置追踪

```sql
-- 位置追踪表
CREATE TABLE location_tracks (
    id BIGSERIAL PRIMARY KEY,
    device_id TEXT NOT NULL,
    location GEOGRAPHY(POINT, 4326) NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    speed NUMERIC,  -- 速度（m/s）
    heading NUMERIC,  -- 方向（度）
    accuracy NUMERIC,  -- 精度（米）
    geofence_id INTEGER REFERENCES geofences(id)
);

-- 创建索引
CREATE INDEX idx_tracks_device_time ON location_tracks (device_id, timestamp DESC);
CREATE INDEX idx_tracks_location ON location_tracks USING GIST (location);
CREATE INDEX idx_tracks_geofence ON location_tracks (geofence_id) WHERE geofence_id IS NOT NULL;

-- 插入位置时自动检查围栏
CREATE OR REPLACE FUNCTION update_geofence_on_insert()
RETURNS TRIGGER AS $$
DECLARE
    fence_id INTEGER;
BEGIN
    -- 查找包含该点的围栏
    SELECT id INTO fence_id
    FROM geofences
    WHERE ST_Within(NEW.location::geometry, boundary::geometry)
    ORDER BY ST_Area(boundary)
    LIMIT 1;

    NEW.geofence_id := fence_id;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_geofence_trigger
BEFORE INSERT ON location_tracks
FOR EACH ROW
EXECUTE FUNCTION update_geofence_on_insert();
```

---

## 8. 路径规划与导航

### 8.1 最短路径算法

#### 使用ST_ShortestLine

```sql
-- 计算两点之间的最短线
SELECT ST_ShortestLine(
    ST_GeomFromText('POINT(116.3912 39.9067)', 4326),
    ST_GeomFromText('POINT(116.4074 39.9042)', 4326)
);
```

### 8.2 pgRouting集成

#### 安装pgRouting

```bash
# Ubuntu/Debian
sudo apt-get install postgresql-17-pgrouting

# 或在数据库中创建扩展
```

```sql
-- 创建pgRouting扩展
CREATE EXTENSION IF NOT EXISTS pgrouting;

-- 创建路网表
CREATE TABLE roads (
    id SERIAL PRIMARY KEY,
    name TEXT,
    geom GEOMETRY(LINESTRING, 4326),
    length_m NUMERIC,
    speed_kmh NUMERIC,
    cost NUMERIC,  -- 通行成本
    reverse_cost NUMERIC  -- 反向通行成本
);

-- 创建拓扑
SELECT pgr_createTopology('roads', 0.0001, 'geom', 'id');

-- 最短路径查询
SELECT * FROM pgr_dijkstra(
    'SELECT id, source, target, cost, reverse_cost FROM roads',
    1,  -- 起点节点ID
    10,  -- 终点节点ID
    directed := true
);
```

---

## 10. 与地图库集成

### 10.1 Mapbox集成

#### 后端API

```python
# Flask API示例
from flask import Flask, jsonify, request
import psycopg2
from psycopg2.extras import RealDictCursor
import json

app = Flask(__name__)

def get_db_connection():
    return psycopg2.connect(
        host='localhost',
        database='gisdb',
        user='postgres',
        password='password'
    )

@app.route('/api/points', methods=['GET'])
def get_points():
    """获取GeoJSON格式的点数据"""
    bbox = request.args.get('bbox')  # "minLon,minLat,maxLon,maxLat"

    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    if bbox:
        coords = [float(x) for x in bbox.split(',')]
        cursor.execute("""
            SELECT jsonb_build_object(
                'type', 'FeatureCollection',
                'features', jsonb_agg(
                    jsonb_build_object(
                        'type', 'Feature',
                        'geometry', ST_AsGeoJSON(location)::jsonb,
                        'properties', jsonb_build_object(
                            'id', id,
                            'name', name
                        )
                    )
                )
            ) AS geojson
            FROM points
            WHERE location && ST_MakeEnvelope(%s, %s, %s, %s, 4326)::geography
        """, (coords[0], coords[1], coords[2], coords[3]))
    else:
        cursor.execute("""
            SELECT jsonb_build_object(
                'type', 'FeatureCollection',
                'features', jsonb_agg(
                    jsonb_build_object(
                        'type', 'Feature',
                        'geometry', ST_AsGeoJSON(location)::jsonb,
                        'properties', jsonb_build_object('id', id, 'name', name)
                    )
                )
            ) AS geojson
            FROM points
        """)

    result = cursor.fetchone()
    cursor.close()
    conn.close()

    return jsonify(result['geojson'])

if __name__ == '__main__':
    app.run(debug=True)
```

#### 前端Mapbox集成

```javascript
// Mapbox GL JS示例
mapboxgl.accessToken = 'YOUR_MAPBOX_ACCESS_TOKEN';

const map = new mapboxgl.Map({
    container: 'map',
    style: 'mapbox://styles/mapbox/streets-v11',
    center: [116.3912, 39.9067],
    zoom: 12
});

// 加载GeoJSON数据
map.on('load', () => {
    // 从API获取数据
    fetch('/api/points?bbox=116.38,39.89,116.42,39.93')
        .then(response => response.json())
        .then(data => {
            map.addSource('points', {
                'type': 'geojson',
                'data': data
            });

            map.addLayer({
                'id': 'points',
                'type': 'circle',
                'source': 'points',
                'paint': {
                    'circle-radius': 6,
                    'circle-color': '#ff0000'
                }
            });
        });
});
```

### 10.2 Leaflet集成

```javascript
// Leaflet示例
const map = L.map('map').setView([39.9067, 116.3912], 12);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors'
}).addTo(map);

// 从API加载GeoJSON
fetch('/api/points')
    .then(response => response.json())
    .then(data => {
        L.geoJSON(data, {
            pointToLayer: (feature, latlng) => {
                return L.circleMarker(latlng, {
                    radius: 8,
                    fillColor: '#ff7800',
                    color: '#000',
                    weight: 1,
                    opacity: 1,
                    fillOpacity: 0.8
                });
            }
        }).addTo(map);
    });
```

---

## 📚 参考资源

1. **PostGIS官方文档**: <https://postgis.net/documentation/>
2. **GDAL/OGR工具**: <https://gdal.org/>
3. **Mapbox文档**: <https://docs.mapbox.com/>
4. **Leaflet文档**: <https://leafletjs.com/>
5. **pgRouting文档**: <https://pgrouting.org/>

---

## 📝 更新日志

- **v2.0** (2025-01): 完整实战指南
  - 添加完整的安装配置
  - 补充空间数据类型深入解析
  - 添加空间索引优化
  - 补充空间查询性能优化
  - 添加数据导入导出
  - 补充坐标系转换
  - 添加地理围栏与位置服务
  - 补充路径规划
  - 添加地理大数据处理
  - 补充地图库集成

---

**状态**: ✅ **文档完成** | [返回目录](../README.md)
