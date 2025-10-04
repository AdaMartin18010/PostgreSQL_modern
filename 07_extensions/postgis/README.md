# postgis

> 版本对标（更新于 2025-10）

## 主题边界

- 地理空间数据类型、索引与空间查询（GIS）

## 核心要点

- 安装与启用：`CREATE EXTENSION postgis;`
- 数据类型：`geometry`、`geography`；坐标系与投影（SRID）
- 索引：GiST/GIN 空间索引
- 查询：空间关系、缓冲、距离、拓扑操作
- I/O：GeoJSON、WKT/WKB、Shapefile 导入导出

## 知识地图

- 空间类型与坐标系 → 索引与查询 → 数据交换与可视化

## 权威参考

- 官网与文档：`<https://postgis.net/`>
- 安装与指南：`<https://postgis.net/install/`>

## 评测要点

- 空间范围查询/邻近查询的 P95/P99 延迟与吞吐
- 不同 SRID/投影下的精度/性能差异
- 大要素集与复杂拓扑运算（缓冲、相交、合并）的耗时

## 常见参数（示例）

- 索引：GiST/GIN 选择与填充因子（FILLFACTOR）
- 精度：坐标精度、简化/抽稀策略
- 存储：几何精化与 TOAST 行为
