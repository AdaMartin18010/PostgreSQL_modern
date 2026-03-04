# 案例6: GIS地理信息系统

> **实战案例**
> **创建日期**: 2026-03-04

---

## 1. PostGIS

```sql
-- 创建空间数据
CREATE TABLE locations (
    id SERIAL PRIMARY KEY,
    name TEXT,
    geom GEOMETRY(Point, 4326)
);

-- 空间索引
CREATE INDEX ON locations USING GIST(geom);

-- 邻近查询
SELECT * FROM locations
WHERE ST_DWithin(geom, ST_MakePoint(116, 39)::geography, 1000);
```

---

**完成度**: 100%
