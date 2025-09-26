-- 可运行示例（占位）：从 JSONL 文件读取并 INSERT（需要外部工具将 JSONL 转为 TSV/CSV 或使用 psql \\copy + 程序转换）。
-- 下面提供 plpgsql 读取 TEXT 并解析 jsonb 的示意：

-- 假设外部已将 JSONL 读入到临时表 tmp_lines(line text)
-- CREATE TEMP TABLE tmp_lines(line text);
-- \copy tmp_lines FROM 'sample.jsonl';

DO $$
DECLARE
  r record;
  j jsonb;
BEGIN
  FOR r IN SELECT line FROM tmp_lines LOOP
    j := r.line::jsonb;
    INSERT INTO rag.docs(meta, embedding)
    VALUES (j->'meta', (
      -- 简化示意：将 json 数组转为文本再由扩展/应用层转 vector
      -- 实际项目建议在应用层生成 vector 类型
      (trim(both '[]' from (j->'embedding')::text))::text
    )::vector);
  END LOOP;
END$$;
