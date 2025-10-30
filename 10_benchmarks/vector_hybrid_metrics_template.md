# 向量/混合搜索指标模板（PG18 对齐）

## 目的
统一评测语义检索与混合检索（pgvector + 全文/RRF）的关键指标，确保不同数据集与参数可对比。

## 指标定义
- 延迟：P50/P95/P99（ms）
- 吞吐：QPS（稳定区间）
- 召回：Recall@K（K ∈ {10, 50, 100}）
- 排序质量：NDCG@K（K ∈ {10, 50, 100}）
- 资源：CPU/内存/IO 峰值与均值
- 索引成本：构建耗时、峰值内存、索引大小
- 维护成本：增量更新耗时、重建窗口

## 评测维度
- 索引类型：HNSW / IVFFlat
- 距离度量：L2 / Cosine / Inner Product
- 参数：`ef_search`、`M`（HNSW）、`lists`、`probes`（IVFFlat）
- 融合策略：纯向量 / 向量+全文（RRF: w_vec, w_ft, K）

## 报告模板

| 数据集 | 模式 | 指标 | P50 | P95 | P99 | Recall@10 | NDCG@10 | QPS | 备注 |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| ds1 | HNSW | baseline |  |  |  |  |  |  |  |
| ds1 | HNSW+RRF | fusion |  |  |  |  |  |  |  |
| ds1 | IVFFlat | baseline |  |  |  |  |  |  |  |
| ds1 | IVFFlat+RRF | fusion |  |  |  |  |  |  |  |

## 参考入口
- 论证：`13_ai_alignment/01_向量与混合搜索.md`
- 总览：`13_ai_alignment/00_论证总览_AI_View_对齐_PG18.md`

