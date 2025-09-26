CREATE EXTENSION IF NOT EXISTS vector;
CREATE SCHEMA IF NOT EXISTS rag;
CREATE TABLE IF NOT EXISTS rag.docs (
  id bigserial PRIMARY KEY,
  meta jsonb,
  embedding vector(384)
);
CREATE INDEX IF NOT EXISTS idx_docs_hnsw ON rag.docs USING hnsw (embedding vector_l2_ops) WITH (m=16, ef_construction=200);
