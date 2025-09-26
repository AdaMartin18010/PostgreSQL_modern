# rag_minimal

目标：最小可运行的 RAG 检索样例（pgvector + HNSW）。

使用步骤：

1) psql -f schema.sql
2) 生成/导入 embedding（占位：外部脚本生成 384 维向量）
3) psql -f load.sql（建议批量导入后再建索引或分批重建；随后 ANALYZE）
4) 参数化查询：
   - 在 psql 中：
     - `\set q '(0.01,0.02,0.03, ... ,0.04)'`
     - `\i query.sql`（或直接执行示例查询）
   - 在应用层：将数组转换为 `vector` 类型再参与 `<->` 距离计算

注意：批量导入后再建索引或分批重建；ANALYZE 更新统计。
