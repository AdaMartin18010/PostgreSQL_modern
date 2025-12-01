# PostgreSQL AI集成 - 30分钟快速开始

**最后更新**: 2025-11-11
**难度**: 🟢 入门
**预计时间**: 30分钟
**版本覆盖**: PostgreSQL 17+ | PostgreSQL 18
**相关文档**: [AI 时代专题主文档](../ai_view.md) | [AI 时代专题导航](../07-前沿技术/AI-时代/00-导航.md)

---

## 📋 学习目标

完成本指南后，你将能够：

- ✅ 在PostgreSQL中安装pgvector扩展
- ✅ 创建包含向量列的表
- ✅ 使用Python生成文本嵌入
- ✅ 执行向量相似度搜索
- ✅ 理解基本的向量检索原理

---

## 🎯 前置要求

### 必需

- PostgreSQL 17+ 或 18+（推荐 PostgreSQL 18）
- 基础SQL知识
- Python 3.8+（用于生成嵌入）

### 可选

- Docker（用于快速环境搭建）
- 文本编辑器或IDE

---

## 🚀 步骤1: 环境准备 (5分钟)

### 方式A: Docker快速启动（推荐）

如果你还没有PostgreSQL环境，使用Docker是最快的方式：

```bash
# 拉取包含pgvector的PostgreSQL镜像
docker run -d \
  --name postgres-ai \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=vectordb \
  -p 5432:5432 \
  ankane/pgvector:latest

# 等待几秒钟让数据库启动
sleep 5

# 连接到数据库
docker exec -it postgres-ai psql -U postgres -d vectordb
```

### 方式B: 现有PostgreSQL安装扩展

如果你已经有PostgreSQL，需要安装pgvector扩展：

**Ubuntu/Debian**:

```bash
# 安装编译工具
sudo apt-get update
sudo apt-get install -y postgresql-server-dev-16 build-essential git

# 下载并编译pgvector
cd /tmp
git clone --branch v0.7.0 https://github.com/pgvector/pgvector.git
cd pgvector
make
sudo make install
```

**macOS (Homebrew)**:

```bash
brew install pgvector
```

**验证安装**:

```sql
-- 连接到数据库
psql -U postgres -d your_database

-- 安装扩展
CREATE EXTENSION IF NOT EXISTS vector;

-- 验证
SELECT * FROM pg_extension WHERE extname = 'vector';
-- 应该看到一行结果
```

---

## 📦 步骤2: 创建表和数据 (10分钟)

### 2.1 创建文档表

```sql
-- 创建存储文档和向量的表
CREATE TABLE documents (
    id BIGSERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    embedding vector(384), -- 使用384维向量（all-MiniLM-L6-v2模型）
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 创建向量索引（HNSW算法，余弦相似度）
CREATE INDEX ON documents
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- 查看表结构
\d documents
```

### 2.2 插入示例数据（手动测试用）

```sql
-- 插入几条带有虚拟向量的测试数据
-- 注意：这些向量是随机的，仅用于测试语法

INSERT INTO documents (title, content, embedding) VALUES
('PostgreSQL简介',
 'PostgreSQL是一个强大的开源关系型数据库管理系统，支持SQL查询和ACID事务。',
 -- 384维随机向量（实际使用时应该由模型生成）
 array_fill(0.1, ARRAY[384])::vector(384)
),
('向量数据库',
 '向量数据库用于存储和检索高维向量数据，广泛应用于AI和机器学习领域。',
 array_fill(0.2, ARRAY[384])::vector(384)
),
('机器学习基础',
 '机器学习是人工智能的一个分支，通过算法让计算机从数据中学习规律。',
 array_fill(0.15, ARRAY[384])::vector(384)
);

-- 验证插入
SELECT id, title, substring(content, 1, 50) as content_preview
FROM documents;
```

---

## 🔍 步骤3: 执行向量搜索 (5分钟)

### 3.1 基本相似度搜索

```sql
-- 定义查询向量（实际应该由模型生成）
WITH query AS (
    SELECT array_fill(0.12, ARRAY[384])::vector(384) AS q_vec
)
-- 查找最相似的3个文档
SELECT
    d.id,
    d.title,
    d.content,
    1 - (d.embedding <=> query.q_vec) AS similarity,
    d.embedding <=> query.q_vec AS distance
FROM documents d, query
ORDER BY d.embedding <=> query.q_vec  -- <=> 是余弦距离操作符
LIMIT 3;
```

### 3.2 理解距离操作符

pgvector提供三种距离操作符：

```sql
-- <-> : L2 距离（欧几里得距离）
-- <#> : 内积距离（负内积）
-- <=> : 余弦距离

-- 示例：比较不同距离度量
WITH query AS (
    SELECT array_fill(0.12, ARRAY[384])::vector(384) AS q_vec
)
SELECT
    id,
    title,
    embedding <-> query.q_vec AS l2_distance,
    embedding <#> query.q_vec AS inner_product,
    embedding <=> query.q_vec AS cosine_distance,
    1 - (embedding <=> query.q_vec) AS cosine_similarity
FROM documents, query
ORDER BY embedding <=> query.q_vec
LIMIT 3;
```

---

## 🐍 步骤4: Python集成 - 生成真实嵌入 (10分钟)

### 4.1 安装Python依赖

```bash
# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装必要的包
pip install psycopg2-binary sentence-transformers numpy
```

### 4.2 完整的Python示例

创建文件 `vector_search_demo.py`:

```python
#!/usr/bin/env python3
"""
PostgreSQL向量搜索演示
使用sentence-transformers生成文本嵌入
"""

from sentence_transformers import SentenceTransformer
import psycopg2
import numpy as np

# 1. 加载嵌入模型（第一次运行会下载模型）
print("加载嵌入模型...")
model = SentenceTransformer('all-MiniLM-L6-v2')
print(f"模型维度: {model.get_sentence_embedding_dimension()}")  # 应该是384

# 2. 连接数据库
print("连接数据库...")
conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="vectordb",  # 根据你的数据库名修改
    user="postgres",
    password="postgres"   # 根据你的密码修改
)

# 3. 定义辅助函数

def add_document(title, content):
    """添加文档并自动生成嵌入"""
    # 生成嵌入向量
    embedding = model.encode(content).tolist()

    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO documents (title, content, embedding)
            VALUES (%s, %s, %s)
            RETURNING id
        """, (title, content, embedding))

        doc_id = cur.fetchone()[0]
        conn.commit()
        print(f"✅ 添加文档 ID={doc_id}: {title}")
        return doc_id

def search(query_text, top_k=5):
    """语义搜索"""
    # 生成查询向量
    query_embedding = model.encode(query_text).tolist()

    with conn.cursor() as cur:
        cur.execute("""
            SELECT
                id,
                title,
                content,
                1 - (embedding <=> %s::vector) AS similarity
            FROM documents
            ORDER BY embedding <=> %s::vector
            LIMIT %s
        """, (query_embedding, query_embedding, top_k))

        results = cur.fetchall()
        return results

# 4. 添加一些真实文档

print("\n--- 添加示例文档 ---")

documents = [
    ("Python编程", "Python是一门简单易学的编程语言，广泛应用于数据科学和Web开发。"),
    ("数据库技术", "数据库用于持久化存储和管理数据，支持复杂的查询和事务处理。"),
    ("人工智能发展", "人工智能正在改变各行各业，从自动驾驶到医疗诊断。"),
    ("云计算平台", "云计算提供按需的计算资源，企业可以根据需要灵活扩展。"),
    ("向量检索原理", "向量检索通过计算向量之间的距离或相似度，快速找到相关内容。"),
]

for title, content in documents:
    add_document(title, content)

# 5. 执行搜索

print("\n--- 执行搜索 ---\n")

queries = [
    "如何学习编程",
    "数据存储方案",
    "AI相关技术"
]

for query in queries:
    print(f"🔍 搜索: '{query}'")
    results = search(query, top_k=3)

    for idx, (doc_id, title, content, similarity) in enumerate(results, 1):
        print(f"  {idx}. [{similarity:.3f}] {title}")
        print(f"     {content[:60]}...")
    print()

# 6. 清理
conn.close()
print("✅ 完成！")
```

### 4.3 运行演示

```bash
# 运行Python脚本
python vector_search_demo.py

# 预期输出：
# 加载嵌入模型...
# 模型维度: 384
# 连接数据库...
#
# --- 添加示例文档 ---
# ✅ 添加文档 ID=4: Python编程
# ✅ 添加文档 ID=5: 数据库技术
# ...
#
# --- 执行搜索 ---
# 🔍 搜索: '如何学习编程'
#   1. [0.723] Python编程
#   2. [0.512] 人工智能发展
#   ...
```

---

## 🎓 步骤5: 高级用法（可选）

### 5.1 混合搜索：向量 + 过滤条件

```sql
-- 结合向量搜索和传统条件过滤
WITH query AS (
    SELECT array_fill(0.12, ARRAY[384])::vector(384) AS q_vec
)
SELECT
    d.id,
    d.title,
    1 - (d.embedding <=> query.q_vec) AS similarity
FROM documents d, query
WHERE
    d.created_at >= NOW() - INTERVAL '7 days'  -- 只搜索最近7天
    AND 1 - (d.embedding <=> query.q_vec) > 0.5  -- 相似度阈值
ORDER BY d.embedding <=> query.q_vec
LIMIT 10;
```

### 5.2 批量向量化

```python
def batch_add_documents(documents_list, batch_size=32):
    """批量添加文档"""
    for i in range(0, len(documents_list), batch_size):
        batch = documents_list[i:i+batch_size]

        # 批量生成嵌入
        contents = [doc[1] for doc in batch]
        embeddings = model.encode(contents)

        # 批量插入
        with conn.cursor() as cur:
            for (title, content), embedding in zip(batch, embeddings):
                cur.execute(
                    "INSERT INTO documents (title, content, embedding) VALUES (%s, %s, %s)",
                    (title, content, embedding.tolist())
                )
        conn.commit()
        print(f"✅ 批量添加 {len(batch)} 个文档")
```

### 5.3 向量索引参数调优

```sql
-- 删除旧索引
DROP INDEX IF EXISTS documents_embedding_idx;

-- 创建优化的HNSW索引
-- m: 每层最大连接数（越大召回率越高，但索引越大）
-- ef_construction: 构建时的搜索深度（越大质量越高，但构建越慢）
CREATE INDEX documents_embedding_idx ON documents
USING hnsw (embedding vector_cosine_ops)
WITH (m = 32, ef_construction = 128);

-- 或使用IVFFlat索引（适合超大数据集）
CREATE INDEX documents_embedding_ivf_idx ON documents
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
```

---

## ✅ 完成检查清单

恭喜！如果你完成了以上步骤，请确认：

- [x] pgvector扩展已安装
- [x] 创建了包含vector列的表
- [x] 创建了向量索引
- [x] 执行了基本的相似度搜索
- [x] 使用Python生成了真实的文本嵌入
- [x] 理解了向量距离操作符的区别

---

## 🎯 下一步学习

### 推荐路径

1. **深入向量数据库** (30分钟)
   - 阅读：[03.05-向量数据库支持](../04-高级特性/03.05-向量数据库支持.md)
   - 学习HNSW vs IVFFlat索引选择

2. **性能调优** (1小时)
   - 阅读：[向量检索性能调优](../07-前沿技术/05.05-向量检索性能调优指南.md)
   - 学习参数调优和性能基准

3. **RAG架构** (2-3小时)
   - 阅读：[RAG架构实战](../07-前沿技术/05.04-RAG架构实战指南.md)
   - 构建完整的知识库问答系统

4. **完整案例项目** (1天)
   - 实践：[语义搜索系统案例](../cases/ai-applications/01-semantic-search/)（开发中）
   - 端到端可运行项目

---

## 🔧 常见问题

### Q1: 向量维度怎么选择？

**A**: 取决于你使用的嵌入模型：

| 模型 | 维度 | 适用场景 |
|-----|------|---------|
| all-MiniLM-L6-v2 | 384 | 快速、轻量级 |
| all-mpnet-base-v2 | 768 | 更好的质量 |
| text-embedding-ada-002 (OpenAI) | 1536 | 最高质量，但需API |
| BAAI/bge-large-en-v1.5 | 1024 | 中文支持好 |

```sql
-- 创建表时指定维度
CREATE TABLE docs (
    embedding vector(384)  -- 匹配模型维度
);
```

### Q2: HNSW vs IVFFlat如何选择？

**A**:

- **HNSW**:
  - ✅ 更高的召回率
  - ✅ 适合中小数据集 (<100万向量)
  - ❌ 内存占用较大

- **IVFFlat**:
  - ✅ 更快的索引构建
  - ✅ 适合大数据集 (>100万向量)
  - ❌ 需要调优`lists`和`probes`参数

### Q3: 为什么搜索结果不准确？

**可能原因**:

1. **向量未归一化** (余弦相似度需要)

   ```python
   from sklearn.preprocessing import normalize
   embedding = normalize(model.encode(text).reshape(1, -1))[0]
   ```

2. **索引参数不当**

   ```sql
   -- 增大ef_construction提升质量
   CREATE INDEX ... WITH (m = 16, ef_construction = 128);
   ```

3. **模型不匹配领域**
   - 选择领域专用模型（如法律、医疗）

### Q4: 如何查看向量？

```sql
-- 查看向量的前10个维度
SELECT id, title, embedding[1:10] FROM documents LIMIT 1;

-- 计算向量的模长
SELECT id, title, sqrt(sum(x^2)) as norm
FROM documents, unnest(embedding::real[]) AS x
GROUP BY id, title;
```

### Q5: 性能优化建议？

1. **合理的索引参数**
2. **使用物化视图缓存常用查询**
3. **分区大表**
4. **监控查询性能**

   ```sql
   EXPLAIN ANALYZE
   SELECT ... FROM documents
   ORDER BY embedding <=> query_vec
   LIMIT 10;
   ```

---

## 📚 参考资源

### 官方文档

- [pgvector GitHub](https://github.com/pgvector/pgvector)
- [PostgreSQL文档](https://www.postgresql.org/docs/)
- [Sentence Transformers](https://www.sbert.net/)

### 本项目文档

- [向量数据库支持](../04-高级特性/03.05-向量数据库支持.md)
- [机器学习集成](../04-高级特性/03.04-机器学习集成.md)
- [批判性评价报告](../PostgreSQL-AI集成批判性评价报告-2025-10.md)

### 外部资源

- [Hugging Face Model Hub](https://huggingface.co/models) - 查找嵌入模型
- [pgvector Examples](https://github.com/pgvector/pgvector-python) - Python示例
- [本地可运行示例](../examples/README.md) ⭐ - 8个完整的Docker Compose示例项目
- [Vector Database Comparison](https://benchmark.vectorview.ai/) - 向量数据库对比

---

## 💬 反馈和支持

### 遇到问题？

1. **检查环境**:

   ```bash
   psql --version  # PostgreSQL版本
   python --version  # Python版本
   ```

2. **查看扩展**:

   ```sql
   SELECT * FROM pg_available_extensions WHERE name = 'vector';
   ```

3. **查看日志**:

   ```bash
   # Docker
   docker logs postgres-ai

   # 本地
   tail -f /var/log/postgresql/postgresql-16-main.log
   ```

### 需要帮助？

- 📖 查看完整文档索引
- 💬 提交Issue或问题
- 🤝 贡献改进建议

---

---

## 📚 相关文档

### AI 时代专题（推荐阅读）

- **📖 [PostgreSQL 在 AI 时代的全面演进](../ai_view.md)** - 主文档（v3.0）⭐⭐⭐
- [AI 时代专题导航](../07-前沿技术/AI-时代/00-导航.md) - 专题导航
- [向量与混合搜索](../07-前沿技术/AI-时代/01-向量与混合搜索-pgvector与RRF.md) - pgvector 2.0 + RRF
- [实践指南](../07-前沿技术/AI-时代/07-实践指南-落地清单.md) - 企业落地清单
- [落地案例](../07-前沿技术/AI-时代/06-落地案例-2025精选.md) - 8 个行业案例

### 其他资源

- [AI集成改进行动计划](./AI集成改进行动计划.md) - 详细改进计划
- [PostgreSQL 知识库 README](../README.md) - 主入口

---

**最后更新**: 2025-11-11
**版本**: v1.1
**预计学习时间**: 30-45分钟
**难度**: 🟢 入门
**版本覆盖**: PostgreSQL 17+ | PostgreSQL 18（推荐）

---

[返回导航](./README-AI集成评价.md) | [查看改进计划](./AI集成改进行动计划.md) | [AI 时代专题](../ai_view.md)
