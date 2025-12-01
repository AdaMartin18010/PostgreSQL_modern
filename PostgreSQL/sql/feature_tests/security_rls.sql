-- RLS Feature Test (1.1.17)
CREATE SCHEMA IF NOT EXISTS ft_sec;
SET search_path TO ft_sec, public;

DROP TABLE IF EXISTS rls_docs CASCADE;
CREATE TABLE rls_docs(
  id BIGSERIAL PRIMARY KEY,
  owner_name TEXT NOT NULL,
  content TEXT NOT NULL
);

ALTER TABLE rls_docs ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS p_owner_only ON rls_docs;
CREATE POLICY p_owner_only ON rls_docs FOR ALL USING (owner_name = current_user);

-- 示例数据
INSERT INTO rls_docs(owner_name, content) VALUES
  ('alice', 'alice note'),
  ('bob', 'bob note');

-- 使用不同用户验证可见性（需要事先创建角色 alice/bob 并切换）
-- SET ROLE alice; SELECT * FROM rls_docs; -- 仅见 alice 行
-- SET ROLE bob;   SELECT * FROM rls_docs; -- 仅见 bob 行

