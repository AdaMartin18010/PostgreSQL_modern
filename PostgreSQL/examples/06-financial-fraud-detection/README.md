# 金融风控系统示例

> **PostgreSQL版本**: 18 ⭐ | 17
> **pgvector版本**: 2.0 ⭐ | 0.7+
> **最后更新**: 2025-11-11

---

## 📋 示例说明

本示例展示如何使用PostgreSQL 18 + pgvector构建金融风控系统，结合向量相似度检测和图关系分析，实现实时反欺诈检测。

**核心特性**：

- ✅ 向量相似度检测（识别相似欺诈模式）
- ✅ 账户关系图分析（检测可疑关联）
- ✅ 多因子风险评分
- ✅ 实时欺诈检测

**适用场景**：

- 银行反欺诈
- 支付风控
- 交易监控
- 账户风险评估

---

## 🚀 快速开始

### 1. 启动服务

```bash
docker-compose up -d
```

### 2. 连接到数据库

```bash
docker-compose exec postgres psql -U postgres -d fraud_detection
```

### 3. 检测单笔交易

```sql
-- 检测交易4是否为欺诈
SELECT * FROM detect_fraud(4, 0.3, 0.7);
```

### 4. 批量检测

```sql
-- 检测过去1小时内的所有交易
SELECT * FROM batch_detect_fraud('1 hour', 0.3, 0.7);
```

### 5. 查看欺诈交易

```sql
-- 查看所有标记为欺诈的交易
SELECT
    t.id,
    a1.account_number AS from_account,
    a2.account_number AS to_account,
    t.amount,
    t.fraud_score,
    t.created_at
FROM transactions t
JOIN accounts a1 ON t.from_account_id = a1.id
JOIN accounts a2 ON t.to_account_id = a2.id
WHERE t.is_fraud = true
ORDER BY t.fraud_score DESC;
```

### 6. 更新账户风险评分

```sql
-- 更新账户1的风险评分
SELECT update_account_risk_score(1);

-- 查看账户风险评分
SELECT account_number, account_type, risk_score
FROM accounts
ORDER BY risk_score DESC;
```

### 7. 停止服务

```bash
docker-compose down
```

---

## 📊 架构说明

```text
┌─────────────────────────────────────────┐
│        交易处理系统                       │
│  - 接收交易请求                           │
│  - 调用反欺诈检测                         │
│  - 决策（通过/拒绝/人工审核）              │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│      PostgreSQL 18 + pgvector           │
│  - 账户表（特征向量）                     │
│  - 交易表（交易向量）                     │
│  - 关系表（图结构）                       │
│  - 反欺诈检测函数                         │
└─────────────────────────────────────────┘
```

---

## 🔧 实际使用流程

### 1. 账户注册

```sql
-- 新账户注册
INSERT INTO accounts (account_number, account_type, transaction_pattern)
VALUES (
    'ACC005',
    'individual',
    '[生成的256维特征向量]'::vector(256)
);
```

### 2. 交易处理

```sql
-- 处理新交易
INSERT INTO transactions (
    from_account_id, to_account_id, amount, transaction_type, transaction_vector
)
VALUES (
    1, 2, 2000.00, 'transfer',
    '[生成的256维交易向量]'::vector(256)
)
RETURNING id;

-- 立即检测欺诈（假设返回的id是5）
SELECT * FROM detect_fraud(5, 0.3, 0.7);
```

### 3. 实时监控

```python
# Python示例：实时交易监控
import psycopg2

def process_transaction(from_account, to_account, amount, transaction_vector):
    conn = psycopg2.connect("dbname=fraud_detection user=postgres")
    cur = conn.cursor()

    # 插入交易
    cur.execute("""
        INSERT INTO transactions (from_account_id, to_account_id, amount, transaction_vector)
        VALUES (%s, %s, %s, %s)
        RETURNING id
    """, (from_account, to_account, amount, transaction_vector))

    transaction_id = cur.fetchone()[0]

    # 检测欺诈
    cur.execute("SELECT * FROM detect_fraud(%s, 0.3, 0.7)", (transaction_id,))
    result = cur.fetchone()

    is_fraud = result[5]  # is_fraud字段

    if is_fraud:
        # 拒绝交易或标记为人工审核
        handle_fraud_transaction(transaction_id, result)
    else:
        # 批准交易
        approve_transaction(transaction_id)

    conn.commit()
    cur.close()
    conn.close()
```

---

## 📈 风险因子说明

反欺诈检测函数考虑以下风险因子：

1. **向量相似度**（30%权重）
   - 查找与已知欺诈交易相似的交易模式
   - 使用pgvector进行快速相似度搜索

2. **发送方账户风险**（25%权重）
   - 基于账户历史欺诈率
   - 高风险账户的交易更可疑

3. **接收方账户风险**（15%权重）
   - 接收方账户的风险评分

4. **账户关系强度**（20%权重）
   - 弱关系的交易更可疑
   - 首次交易的账户对风险更高

5. **交易金额异常**（10%权重）
   - 大额交易需要额外关注

---

## 📚 相关文档

- [AI 时代专题 - 多模一体化](../../05-前沿技术/AI-时代/04-多模一体化-JSONB时序图向量.md)
- [落地案例 - 金融实时反欺诈](../../05-前沿技术/AI-时代/06-落地案例-2025精选.md#案例-2金融实时反欺诈apache-age--pgvector)
- [向量检索性能调优指南](../../05-前沿技术/05.05-向量检索性能调优指南.md)

---

## 🔧 扩展建议

### 1. 集成Apache AGE

对于更复杂的图分析，可以集成Apache AGE：

```sql
-- Apache AGE示例（需要安装AGE扩展）
SELECT * FROM cypher('fraud_graph', $$
    MATCH (a:Account)-[r:TRANSFER]->(b:Account)
    WHERE r.amount > 10000
    RETURN a, r, b
$$) AS (a agtype, r agtype, b agtype);
```

### 2. 实时流处理

使用PostgreSQL的流处理功能实时检测：

```sql
-- 创建流处理视图
CREATE VIEW fraud_stream AS
SELECT
    t.*,
    detect_fraud(t.id, 0.3, 0.7).*
FROM transactions t
WHERE t.created_at >= now() - INTERVAL '1 minute';
```

### 3. 机器学习集成

使用PostgreSQL的ML扩展进行更智能的检测：

```python
# 使用pg_ai或外部ML服务
from sklearn.ensemble import IsolationForest

# 训练异常检测模型
model = IsolationForest(contamination=0.1)
model.fit(transaction_vectors)

# 预测异常
predictions = model.predict(new_transaction_vectors)
```

---

**最后更新**：2025-11-11
