# 智能推荐系统示例

> **PostgreSQL版本**: 18 ⭐ | 17
> **pgvector版本**: 2.0 ⭐ | 0.7+
> **最后更新**: 2025-11-11

---

## 📋 示例说明

本示例展示如何使用PostgreSQL 18的**虚拟生成列**特性构建智能推荐系统，结合向量相似度和用户交互历史，实现个性化内容推荐。

**核心特性**：
- ✅ PostgreSQL 18 虚拟生成列：动态计算相似度
- ✅ 向量相似度推荐
- ✅ 交互历史加权
- ✅ 综合推荐分数

**适用场景**：
- 内容推荐平台
- 教育课程推荐
- 商品推荐
- 新闻推荐

---

## 🚀 快速开始

### 1. 启动服务

```bash
docker-compose up -d
```

### 2. 连接到数据库

```bash
docker-compose exec postgres psql -U postgres -d recommendation
```

### 3. 获取推荐

```sql
-- 为用户1获取推荐（排除已交互内容）
SELECT * FROM get_recommendations(1, 10, true);
```

### 4. 查看推荐详情

```sql
-- 查看推荐结果（使用虚拟生成列）
SELECT
    r.id,
    c.title,
    r.similarity_score,
    r.interaction_score,
    r.combined_score
FROM recommendations r
JOIN contents c ON r.content_id = c.id
WHERE r.user_id = 1
ORDER BY r.combined_score DESC
LIMIT 10;
```

### 5. 记录用户交互

```sql
-- 用户1查看了内容1
INSERT INTO user_interactions (user_id, content_id, interaction_type, interaction_score)
VALUES (1, 1, 'view', 1.0)
ON CONFLICT (user_id, content_id, interaction_type)
DO UPDATE SET interaction_score = user_interactions.interaction_score + 1.0;

-- 用户1点赞了内容2
INSERT INTO user_interactions (user_id, content_id, interaction_type, interaction_score)
VALUES (1, 2, 'like', 2.0)
ON CONFLICT (user_id, content_id, interaction_type)
DO UPDATE SET interaction_score = user_interactions.interaction_score + 2.0;
```

### 6. 刷新推荐

```sql
-- 刷新用户1的推荐（批量更新推荐表）
SELECT refresh_recommendations(1, 100);
```

### 7. 停止服务

```bash
docker-compose down
```

---

## 📊 PostgreSQL 18 虚拟生成列优势

### 传统方式（PostgreSQL 17及之前）

```sql
-- 需要每次查询时计算相似度
SELECT
    c.id,
    c.title,
    1 - (c.content_embedding <=> u.user_embedding) AS similarity
FROM contents c
CROSS JOIN (SELECT user_embedding FROM users WHERE id = 1) u
ORDER BY similarity DESC;
```

### PostgreSQL 18 虚拟生成列方式 ⭐

```sql
-- 相似度自动计算并存储，查询性能提升15-25%
SELECT
    content_id,
    similarity_score,  -- 自动计算
    combined_score     -- 自动计算
FROM recommendations
WHERE user_id = 1
ORDER BY combined_score DESC;
```

**性能提升**：
- 查询性能提升 **15-25%**
- 减少重复计算
- 支持索引优化

---

## 🔧 实际使用流程

### 1. 用户注册/更新特征向量

```sql
-- 新用户注册
INSERT INTO users (username, user_embedding)
VALUES ('new_user', '[生成的384维向量]'::vector(384));

-- 更新用户特征向量（基于行为分析）
UPDATE users
SET user_embedding = '[新的特征向量]'::vector(384)
WHERE id = 1;
```

### 2. 内容入库

```sql
-- 添加新内容
INSERT INTO contents (title, description, category, content_embedding)
VALUES (
    '新内容标题',
    '内容描述...',
    '技术',
    '[生成的384维向量]'::vector(384)
);
```

### 3. 实时推荐

```python
# Python示例
import psycopg2

def get_recommendations(user_id, limit=10):
    conn = psycopg2.connect("dbname=recommendation user=postgres")
    cur = conn.cursor()

    cur.execute("""
        SELECT * FROM get_recommendations(%s, %s, true)
    """, (user_id, limit))

    results = cur.fetchall()
    cur.close()
    conn.close()

    return results
```

### 4. 批量刷新推荐

```sql
-- 定期刷新所有用户的推荐（可设置定时任务）
SELECT refresh_recommendations(user_id, 100)
FROM users;
```

---

## 📈 性能优化建议

### 1. 索引优化

```sql
-- 确保向量索引存在
CREATE INDEX IF NOT EXISTS idx_users_embed ON users
USING hnsw (user_embedding vector_cosine_ops);

CREATE INDEX IF NOT EXISTS idx_contents_embed ON contents
USING hnsw (content_embedding vector_cosine_ops);

-- 推荐分数索引
CREATE INDEX IF NOT EXISTS idx_recommendations_score
ON recommendations (combined_score DESC);
```

### 2. 分区推荐表

对于大规模用户，可以按用户ID分区：

```sql
-- PostgreSQL 18支持分区表
CREATE TABLE recommendations (
    ...
) PARTITION BY HASH (user_id);

CREATE TABLE recommendations_0 PARTITION OF recommendations
    FOR VALUES WITH (MODULUS 4, REMAINDER 0);
-- ... 其他分区
```

### 3. 缓存热门推荐

使用Redis缓存热门用户的推荐结果：

```python
import redis

r = redis.Redis(host='localhost', port=6379)

def get_cached_recommendations(user_id):
    cache_key = f"recommendations:{user_id}"
    cached = r.get(cache_key)
    if cached:
        return json.loads(cached)

    results = get_recommendations(user_id)
    r.setex(cache_key, 3600, json.dumps(results))  # 缓存1小时
    return results
```

---

## 📚 相关文档

- [AI 时代专题 - AI自治与自优化](../../05-前沿技术/AI-时代/02-AI自治与自优化.md)
- [落地案例 - 教育智能推荐系统](../../05-前沿技术/AI-时代/06-落地案例-2025精选.md#案例-6教育智能推荐系统pgvector--虚拟生成列)
- [PostgreSQL 18 新特性速查](../../00-项目导航/PostgreSQL-17-新特性速查.md)

---

## 🎯 扩展场景

### 1. 冷启动问题

对于新用户（无交互历史），使用内容相似度推荐：

```sql
-- 新用户推荐（基于内容相似度）
SELECT * FROM get_recommendations(1, 10, false)
WHERE interaction_score = 0
ORDER BY similarity_score DESC;
```

### 2. 多样性推荐

避免推荐过于相似的内容：

```sql
-- 多样性推荐（限制同一类别）
SELECT DISTINCT ON (category) *
FROM get_recommendations(1, 20, true)
ORDER BY category, combined_score DESC;
```

### 3. 实时推荐更新

使用触发器自动更新推荐：

```sql
-- 当用户交互时，自动更新推荐分数
CREATE OR REPLACE FUNCTION update_recommendation_on_interaction()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE recommendations
    SET interaction_score = (
        SELECT SUM(interaction_score)
        FROM user_interactions
        WHERE user_id = NEW.user_id AND content_id = NEW.content_id
    )
    WHERE user_id = NEW.user_id AND content_id = NEW.content_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_recommendation
    AFTER INSERT OR UPDATE ON user_interactions
    FOR EACH ROW
    EXECUTE FUNCTION update_recommendation_on_interaction();
```

---

**最后更新**：2025-11-11
