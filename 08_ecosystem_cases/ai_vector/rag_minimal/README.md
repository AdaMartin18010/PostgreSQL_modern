# rag_minimal

目标：最小可运行的 RAG 检索样例（pgvector + HNSW）。

使用步骤：
1) psql -f schema.sql
2) 生成/导入 embedding（占位：外部脚本生成 384 维向量）
3) psql -f load.sql
4) psql -f query.sql（将 :query_embedding 替换为待检索向量）

注意：批量导入后再建索引或分批重建；ANALYZE 更新统计。
