---

> **📋 文档来源**: `docs\03-KnowledgeGraph\07-LLM与知识图谱深度集成.md`
> **📅 复制日期**: 2025-12-22
> **⚠️ 注意**: 本文档为复制版本，原文件保持不变

---

# LLM与知识图谱深度集成完整指南

## 元数据

- **文档版本**: v1.0
- **创建日期**: 2025-12-04
- **适用技术栈**: PostgreSQL 16+ | Apache AGE 1.5+ | pgvector 0.7+ | OpenAI/Anthropic API
- **难度级别**: ⭐⭐⭐⭐⭐ (专家级)
- **预计阅读**: 150分钟
- **配套资源**: [完整代码](./examples/llm-kg/) | [Jupyter Notebooks](./notebooks/)

---

## 📋 完整目录

- [LLM与知识图谱深度集成完整指南](#llm与知识图谱深度集成完整指南)
  - [元数据](#元数据)
  - [📋 完整目录](#-完整目录)
  - [1. LLM+知识图谱融合架构](#1-llm知识图谱融合架构)
    - [1.1 为什么需要融合](#11-为什么需要融合)
      - [LLM的局限性](#llm的局限性)
      - [知识图谱的局限性](#知识图谱的局限性)
      - [融合的价值](#融合的价值)
    - [1.2 融合模式](#12-融合模式)
      - [模式1: LLM增强知识图谱](#模式1-llm增强知识图谱)
      - [模式2: 知识图谱增强LLM](#模式2-知识图谱增强llm)
      - [模式3: 双向增强 (推荐)](#模式3-双向增强-推荐)
    - [1.3 技术挑战](#13-技术挑战)
  - [2. Text-to-Cypher生成系统](#2-text-to-cypher生成系统)
    - [2.1 Prompt工程](#21-prompt工程)
      - [高质量Prompt模板](#高质量prompt模板)
    - [2.2 Few-Shot学习](#22-few-shot学习)
      - [动态示例选择](#动态示例选择)
    - [2.3 错误修复机制](#23-错误修复机制)
      - [自动Cypher修复](#自动cypher修复)
      - [使用示例](#使用示例)
    - [2.4 性能优化](#24-性能优化)
      - [查询缓存](#查询缓存)
  - [3. KBQA系统完整实现](#3-kbqa系统完整实现)
    - [3.1 问题理解](#31-问题理解)
      - [意图识别](#意图识别)
    - [3.2 实体识别与链接](#32-实体识别与链接)
      - [高级实体链接](#高级实体链接)
    - [3.3 子图检索](#33-子图检索)
      - [多跳子图检索](#多跳子图检索)
    - [3.4 答案生成](#34-答案生成)
      - [答案生成策略](#答案生成策略)
    - [3.5 多跳推理](#35-多跳推理)
      - [路径推理](#路径推理)
  - [4. RAG+KG混合架构](#4-ragkg混合架构)
    - [4.1 混合检索](#41-混合检索)
    - [4.2 结果融合](#42-结果融合)
  - [5. LLM驱动的知识抽取](#5-llm驱动的知识抽取)
    - [5.1 实体抽取](#51-实体抽取)
    - [5.2 关系抽取](#52-关系抽取)
  - [6. 企业级生产架构](#6-企业级生产架构)
    - [6.1 系统架构](#61-系统架构)
    - [6.2 性能优化](#62-性能优化)
    - [6.3 监控告警](#63-监控告警)
  - [📚 参考资源](#-参考资源)
  - [📝 更新日志](#-更新日志)
  - [🎯 快速开始](#-快速开始)
    - [安装依赖](#安装依赖)
    - [基础使用](#基础使用)

---

## 1. LLM+知识图谱融合架构

### 1.1 为什么需要融合

#### LLM的局限性

| 局限 | 描述 | 知识图谱如何解决 |
|------|------|------------------|
| **幻觉问题** | 生成不真实的信息 | 提供可验证的事实依据 |
| **时效性差** | 训练数据截止日期 | 实时更新的知识库 |
| **可解释性弱** | 黑盒推理过程 | 明确的推理路径 |
| **知识更新难** | 需要重新训练 | 动态添加/修改知识 |
| **领域知识不足** | 通用模型缺乏专业性 | 存储领域专家知识 |

#### 知识图谱的局限性

| 局限 | 描述 | LLM如何解决 |
|------|------|-------------|
| **构建成本高** | 需要人工标注 | 自动化知识抽取 |
| **查询困难** | 需要学习Cypher | 自然语言接口 |
| **泛化能力弱** | 只能回答已知知识 | 常识推理与创造性回答 |
| **冷启动问题** | 初期知识稀疏 | 预训练知识补充 |

#### 融合的价值

```text
LLM + KG融合系统 = 1 + 1 > 2

优势：
✅ 准确性: KG提供事实验证
✅ 时效性: KG实时更新
✅ 可解释性: 明确的推理链
✅ 领域专业性: KG专业知识 + LLM理解
✅ 用户体验: 自然语言交互
```

### 1.2 融合模式

#### 模式1: LLM增强知识图谱

```text
用户问题 → LLM理解 → 生成Cypher → KG查询 → 返回结果
```

**适用场景**: 结构化查询、精确问答

#### 模式2: 知识图谱增强LLM

```text
用户问题 → KG检索相关知识 → 注入LLM上下文 → LLM生成答案
```

**适用场景**: 需要创造性、解释性回答

#### 模式3: 双向增强 (推荐)

```text
用户问题
   ├─→ LLM理解 + 实体识别
   ├─→ KG子图检索
   ├─→ 向量相似度搜索
   └─→ LLM综合生成答案
```

**适用场景**: 复杂场景、企业级应用

### 1.3 技术挑战

```python
# 技术挑战清单
class LLMKGChallenges:
    """LLM+KG融合的技术挑战"""

    challenges = {
        "准确性": {
            "Text-to-Cypher精度": "需要>=90%准确率",
            "实体链接准确性": "消歧困难",
            "幻觉控制": "防止LLM编造事实"
        },
        "性能": {
            "延迟": "端到端<2秒",
            "并发": "支持1000+ QPS",
            "成本": "LLM API调用成本控制"
        },
        "工程化": {
            "错误处理": "Cypher语法错误自动修复",
            "缓存策略": "减少重复调用",
            "监控": "全链路可观测"
        },
        "数据质量": {
            "KG完整性": "知识覆盖率",
            "Schema进化": "适应变化",
            "数据一致性": "多源融合"
        }
    }

    @classmethod
    def print_challenges(cls):
        for category, items in cls.challenges.items():
            print(f"\n【{category}】")
            for challenge, description in items.items():
                print(f"  - {challenge}: {description}")

# 输出挑战清单
LLMKGChallenges.print_challenges()
```

---

## 2. Text-to-Cypher生成系统

### 2.1 Prompt工程

#### 高质量Prompt模板

```python
import json
from typing import Dict, List, Optional
from openai import OpenAI

class CypherPromptTemplate:
    """Text-to-Cypher Prompt模板"""

    @staticmethod
    def get_system_prompt(schema: Dict) -> str:
        """系统提示词"""
        return f"""你是一个Cypher查询专家，专门为Apache AGE图数据库生成查询。

## 图Schema

### 节点类型 (Node Labels)
{json.dumps(schema['node_labels'], indent=2, ensure_ascii=False)}

### 关系类型 (Relationship Types)
{json.dumps(schema['relationship_types'], indent=2, ensure_ascii=False)}

### 关系连接模式 (Connection Patterns)
{json.dumps(schema.get('patterns', {}), indent=2, ensure_ascii=False)}

## Cypher语法规则

1. **基本模式匹配**

    ```cypher
    MATCH (n:Label {{property: 'value'}})
    RETURN n
    ```

2. **关系匹配**

    ```cypher
    MATCH (a:Person)-[r:KNOWS]->(b:Person)
    WHERE r.since > 2020
    RETURN a.name, b.name
    ```

3. **路径查询**

    ```cypher
    MATCH path = (a)-[:KNOWS*1..3]->(b)
    RETURN path
    ```

4. **聚合查询**

    ```cypher
    MATCH (p:Person)-[:WORKS_FOR]->(c:Company)
    RETURN c.name, COUNT(p) AS employee_count
    ORDER BY employee_count DESC
    ```

## 重要约束

✅ DO:

- 始终使用标签和关系类型 (区分大小写)
- 使用参数化查询防止注入
- 添加LIMIT限制结果数量
- 使用明确的方向 `-[r:TYPE]->` 而不是 `-[r:TYPE]-`
- 属性访问使用点号: `n.property`

❌ DON'T:

- 不要使用未在schema中定义的标签/关系
- 不要生成破坏性查询 (CREATE/DELETE/SET) 除非明确要求
- 不要使用复杂的路径模式 (长度>5)
- 不要忘记WHERE过滤条件

## 输出格式

只返回Cypher查询，不要包含任何解释或代码块标记。
"""

    @staticmethod
    def get_few_shot_examples() -> List[Dict]:
        """Few-Shot示例"""
        return [
            {
                "question": "有多少个用户?",
                "cypher": "MATCH (u:User) RETURN COUNT(u) AS user_count"
            },
            {
                "question": "找出年龄超过30岁的用户",
                "cypher": """MATCH (u:User)
WHERE u.age > 30
RETURN u.name, u.age
ORDER BY u.age DESC
LIMIT 100"""
            },
            {
                "question": "Alice的朋友有哪些?",
                "cypher": """MATCH (a:User {name: 'Alice'})-[:FRIEND]->(friend)
RETURN friend.name, friend.age
ORDER BY friend.name"""
            },
            {
                "question": "找出共同朋友最多的用户对",
                "cypher": """MATCH (u1:User)-[:FRIEND]->(common)<-[:FRIEND]-(u2:User)
WHERE id(u1) < id(u2)
RETURN u1.name, u2.name, COUNT(common) AS common_friends
ORDER BY common_friends DESC
LIMIT 10"""
            },
            {
                "question": "从北京到上海的最短路径",
                "cypher": """MATCH path = shortestPath(
  (a:City {name: '北京'})-[:CONNECTED_TO*]-(b:City {name: '上海'})
)
RETURN path, length(path) AS distance"""
            },
            {
                "question": "每个公司有多少员工?",
                "cypher": """MATCH (p:Person)-[:WORKS_FOR]->(c:Company)
RETURN c.name AS company, COUNT(p) AS employee_count
ORDER BY employee_count DESC"""
            },
            {
                "question": "推荐与Bob兴趣相似的用户",
                "cypher": """MATCH (bob:User {name: 'Bob'})
MATCH (other:User)
WHERE other <> bob
  AND SIZE([i IN bob.interests WHERE i IN other.interests]) > 0
RETURN other.name,
       SIZE([i IN bob.interests WHERE i IN other.interests]) AS common_interests
ORDER BY common_interests DESC
LIMIT 10"""
            }
        ]

    @staticmethod
    def format_user_prompt(question: str, examples: List[Dict] = None) -> str:
        """用户提示词"""
        prompt = "将以下问题转换为Cypher查询:\n\n"

        # 添加Few-Shot示例
        if examples:
            prompt += "## 参考示例\n\n"
            for ex in examples:
                prompt += f"问题: {ex['question']}\n"
                prompt += f"Cypher:\n```cypher\n{ex['cypher']}\n```\n\n"

        prompt += f"## 当前问题\n\n问题: {question}\n\nCypher:\n"

        return prompt

# 使用示例

schema = {
    "node_labels": {
        "User": ["name", "age", "email", "interests"],
        "Company": ["name", "industry", "founded"],
        "City": ["name", "country", "population"]
    },
    "relationship_types": {
        "FRIEND": ["since", "strength"],
        "WORKS_FOR": ["position", "since"],
        "LOCATED_IN": []
    },
    "patterns": [
        "(User)-[:FRIEND]->(User)",
        "(User)-[:WORKS_FOR]->(Company)",
        "(Company)-[:LOCATED_IN]->(City)"
    ]
}

template = CypherPromptTemplate()
system_prompt = template.get_system_prompt(schema)
user_prompt = template.format_user_prompt(
    "找出在科技公司工作的30岁以上用户",
    examples=template.get_few_shot_examples()[:3]
)

print(system_prompt)
print("\n" + "="*80 + "\n")
print(user_prompt)

```

### 2.2 Few-Shot学习

#### 动态示例选择

```python
from typing import List, Dict
from sentence_transformers import SentenceTransformer
import numpy as np

class DynamicFewShotSelector:
    """动态选择最相关的Few-Shot示例"""

    def __init__(self, example_bank: List[Dict]):
        self.example_bank = example_bank
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

        # 预计算示例的向量
        self.example_embeddings = self.embedding_model.encode(
            [ex['question'] for ex in example_bank]
        )

    def select_examples(self, question: str, top_k: int = 3) -> List[Dict]:
        """选择最相关的K个示例"""
        # 生成问题向量
        question_emb = self.embedding_model.encode(question)

        # 计算相似度
        similarities = np.dot(self.example_embeddings, question_emb) / (
            np.linalg.norm(self.example_embeddings, axis=1) * np.linalg.norm(question_emb)
        )

        # 选择Top-K
        top_indices = np.argsort(similarities)[-top_k:][::-1]

        return [self.example_bank[i] for i in top_indices]

# 构建示例库
example_bank = [
    {"question": "有多少个用户?", "cypher": "MATCH (u:User) RETURN COUNT(u)"},
    {"question": "年龄最大的10个用户", "cypher": "MATCH (u:User) RETURN u.name, u.age ORDER BY u.age DESC LIMIT 10"},
    {"question": "Alice的朋友", "cypher": "MATCH (a:User {name: 'Alice'})-[:FRIEND]->(f) RETURN f.name"},
    {"question": "在北京的公司", "cypher": "MATCH (c:Company)-[:LOCATED_IN]->(city:City {name: '北京'}) RETURN c.name"},
    {"question": "每个公司的员工数", "cypher": "MATCH (p:Person)-[:WORKS_FOR]->(c:Company) RETURN c.name, COUNT(p) AS count"},
    # ... 更多示例
]

selector = DynamicFewShotSelector(example_bank)

# 为新问题选择示例
question = "找出在科技公司工作的员工人数"
selected_examples = selector.select_examples(question, top_k=3)

print(f"问题: {question}\n")
print("选中的示例:")
for ex in selected_examples:
    print(f"  - {ex['question']}")
```

### 2.3 错误修复机制

#### 自动Cypher修复

```python
import re
import json
import psycopg2
from typing import Optional, List, Dict, Tuple
from openai import OpenAI

class CypherErrorFixer:
    """Cypher查询错误自动修复"""

    def __init__(self, conn, graph_name: str):
        self.conn = conn
        self.graph_name = graph_name
        self.cursor = conn.cursor()

    def execute_with_retry(
        self,
        cypher: str,
        max_retries: int = 3,
        llm_client: Optional[OpenAI] = None
    ) -> tuple:
        """带重试的执行"""

        for attempt in range(max_retries):
            try:
                # 尝试执行
                result = self._execute_cypher(cypher)
                return (True, result, cypher)

            except Exception as e:
                error_msg = str(e)
                print(f"❌ 执行失败 (尝试 {attempt + 1}/{max_retries}): {error_msg}")

                # 尝试自动修复
                fixed_cypher = self._auto_fix(cypher, error_msg)

                if fixed_cypher and fixed_cypher != cypher:
                    print(f"🔧 自动修复后的查询:\n{fixed_cypher}")
                    cypher = fixed_cypher
                    continue

                # 如果有LLM，尝试LLM修复
                if llm_client and attempt < max_retries - 1:
                    print("🤖 尝试LLM修复...")
                    cypher = self._llm_fix(cypher, error_msg, llm_client)
                    continue

                # 最后一次尝试失败
                if attempt == max_retries - 1:
                    return (False, None, error_msg)

        return (False, None, "Max retries exceeded")

    def _execute_cypher(self, cypher: str) -> List[Dict]:
        """执行Cypher查询"""
        # 提取RETURN列
        return_cols = self._extract_return_columns(cypher)

        self.cursor.execute(f"""
            SELECT * FROM cypher('{self.graph_name}', $$
                {cypher}
            $$) AS ({', '.join([f'{col} agtype' for col in return_cols])});
        """)

        results = []
        for row in self.cursor.fetchall():
            result = {}
            for i, col in enumerate(return_cols):
                try:
                    result[col] = json.loads(row[i]) if row[i] else None
                except:
                    result[col] = str(row[i])
            results.append(result)

        return results

    def _auto_fix(self, cypher: str, error_msg: str) -> Optional[str]:
        """基于规则的自动修复"""

        # 规则1: 缺少RETURN语句
        if "RETURN" not in cypher.upper():
            cypher += "\nRETURN *"

        # 规则2: 属性访问错误 (n['name'] -> n.name)
        cypher = re.sub(r"(\w+)\['(\w+)'\]", r"\1.\2", cypher)

        # 规则3: 关系方向错误 (双向改单向)
        if "undirected" in error_msg.lower():
            cypher = cypher.replace("--", "-->")

        # 规则4: 缺少标签
        if "label" in error_msg.lower():
            # 尝试添加通用标签
            cypher = re.sub(r"MATCH \((\w+)\)", r"MATCH (\1:Entity)", cypher)

        # 规则5: 属性名错误 (常见拼写错误)
        typo_fixes = {
            'nmae': 'name',
            'eamil': 'email',
            'comapny': 'company'
        }
        for typo, correct in typo_fixes.items():
            cypher = cypher.replace(typo, correct)

        return cypher

    def _llm_fix(self, cypher: str, error_msg: str, llm_client: OpenAI) -> str:
        """使用LLM修复错误"""
        prompt = f"""你是Cypher专家。以下查询执行失败，请修复它。

原始查询:
```cypher
{cypher}
```

```text
错误信息:
{error_msg}

请返回修复后的Cypher查询，只返回查询本身，不要解释。
"""
        response = llm_client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "你是Cypher查询修复专家。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1
        )
        fixed_cypher = response.choices[0].message.content.strip()
        fixed_cypher = fixed_cypher.replace("```cypher", "").replace("```", "").strip()
        return fixed_cypher

    def _extract_return_columns(self, cypher: str) -> List[str]:
        """提取RETURN列名"""
        match = re.search(r'RETURN\s+(.*?)(?:ORDER BY|LIMIT|$)', cypher, re.IGNORECASE | re.DOTALL)
        if not match:
            return ['result']

        return_clause = match.group(1).strip()

        if return_clause == '*':
            return ['result']

        columns = []
        for part in return_clause.split(','):
            part = part.strip()
            if ' AS ' in part.upper():
                alias = part.split(' AS ')[-1].strip()
                columns.append(alias)
            else:
                columns.append(part.split('.')[-1].strip('()'))

        return columns
```

#### 使用示例

```python
from openai import OpenAI

conn = psycopg2.connect("dbname=test_db user=postgres")
fixer = CypherErrorFixer(conn, 'test_graph')
llm_client = OpenAI(api_key='your-key')

# 测试有错误的查询

bad_cypher = """
MATCH (u:User)
WHERE u.nmae = 'Alice'  -- 拼写错误
RETURN u.eamil  -- 拼写错误
"""

success, result, final_cypher = fixer.execute_with_retry(
    bad_cypher,
    max_retries=3,
    llm_client=llm_client
)

if success:
    print(f"✅ 执行成功!")
    print(f"最终查询:\n{final_cypher}")
    print(f"结果: {result}")
else:
    print(f"❌ 执行失败: {final_cypher}")
```

### 2.4 性能优化

#### 查询缓存

```python
import hashlib
import json
from typing import Optional
from functools import lru_cache
import redis

class CypherQueryCache:
    """Cypher查询缓存"""

    def __init__(self, redis_client: redis.Redis, ttl: int = 3600):
        self.redis = redis_client
        self.ttl = ttl

    def get_cache_key(self, question: str, schema_version: str) -> str:
        """生成缓存键"""
        content = f"{question}|{schema_version}"
        return f"cypher_cache:{hashlib.md5(content.encode()).hexdigest()}"

    def get(self, question: str, schema_version: str) -> Optional[str]:
        """获取缓存的Cypher"""
        key = self.get_cache_key(question, schema_version)
        cached = self.redis.get(key)
        return cached.decode() if cached else None

    def set(self, question: str, schema_version: str, cypher: str):
        """设置缓存"""
        key = self.get_cache_key(question, schema_version)
        self.redis.setex(key, self.ttl, cypher)

    def invalidate_all(self):
        """清空所有缓存"""
        keys = self.redis.keys("cypher_cache:*")
        if keys:
            self.redis.delete(*keys)

# 集成到Text-to-Cypher生成器
class CachedText2CypherGenerator:
    """带缓存的Text-to-Cypher生成器"""

    def __init__(self, generator: Text2CypherGenerator, cache: CypherQueryCache):
        self.generator = generator
        self.cache = cache
        self.schema_version = self._compute_schema_version()

    def _compute_schema_version(self) -> str:
        """计算schema版本号"""
        schema = self.generator.schema
        schema_str = json.dumps(schema, sort_keys=True)
        return hashlib.md5(schema_str.encode()).hexdigest()[:8]

    def generate_cypher(self, question: str) -> str:
        """生成Cypher (带缓存)"""
        # 尝试从缓存获取
        cached = self.cache.get(question, self.schema_version)
        if cached:
            print(f"✅ 缓存命中: {question}")
            return cached

        # 缓存未命中,生成新查询
        print(f"🔄 生成新查询: {question}")
        cypher = self.generator.generate_cypher(question)

        # 保存到缓存
        self.cache.set(question, self.schema_version, cypher)

        return cypher

# 使用示例
redis_client = redis.Redis(host='localhost', port=6379, db=0)
cache = CypherQueryCache(redis_client, ttl=3600)

generator = Text2CypherGenerator(conn, 'knowledge_graph', 'openai-key')
cached_generator = CachedText2CypherGenerator(generator, cache)

# 第一次调用 (生成)
cypher1 = cached_generator.generate_cypher("有多少个用户?")

# 第二次调用 (缓存)
cypher2 = cached_generator.generate_cypher("有多少个用户?")

assert cypher1 == cypher2
```

---

## 3. KBQA系统完整实现

### 3.1 问题理解

#### 意图识别

```python
from enum import Enum
from typing import Dict, List

class QueryIntent(Enum):
    """查询意图"""
    COUNT = "count"  # 统计查询
    FIND = "find"  # 查找查询
    COMPARE = "compare"  # 比较查询
    RECOMMEND = "recommend"  # 推荐查询
    REASON = "reason"  # 推理查询
    AGGREGATE = "aggregate"  # 聚合查询

class QuestionUnderstanding:
    """问题理解模块"""

    def __init__(self, llm_client: OpenAI):
        self.llm = llm_client

    def analyze(self, question: str) -> Dict:
        """分析问题"""
        result = {
            'intent': self._classify_intent(question),
            'entities': self._extract_entities(question),
            'constraints': self._extract_constraints(question),
            'expected_answer_type': self._determine_answer_type(question)
        }

        return result

    def _classify_intent(self, question: str) -> QueryIntent:
        """分类查询意图"""
        prompt = f"""分析以下问题的查询意图，从以下类别中选择一个:
- count: 统计数量 (如"有多少...")
- find: 查找实体 (如"找出...","谁...")
- compare: 比较对比 (如"...和...的区别")
- recommend: 推荐 (如"推荐...","建议...")
- reason: 推理解释 (如"为什么...","原因...")
- aggregate: 聚合分析 (如"每个...的...")

问题: {question}

只返回意图类别,不要解释。
"""

        response = self.llm.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        intent_str = response.choices[0].message.content.strip().lower()

        try:
            return QueryIntent(intent_str)
        except ValueError:
            return QueryIntent.FIND  # 默认

    def _extract_entities(self, question: str) -> List[Dict]:
        """提取问题中的实体"""
        prompt = f"""从以下问题中提取关键实体。

问题: {question}

以JSON格式返回实体列表,每个实体包含:
- mention: 实体在问题中的原文
- type: 实体类型 (Person/Company/Product/Location/Date/Number等)

只返回JSON,不要其他内容。
"""

        response = self.llm.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0
        )

        try:
            result = json.loads(response.choices[0].message.content)
            return result.get('entities', [])
        except:
            return []

    def _extract_constraints(self, question: str) -> List[Dict]:
        """提取查询约束条件"""
        prompt = f"""从以下问题中提取约束条件。

问题: {question}

以JSON格式返回约束列表,每个约束包含:
- type: 约束类型 (age/location/date/category等)
- operator: 操作符 (>/</=/contains等)
- value: 约束值

只返回JSON,不要其他内容。
"""

        response = self.llm.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0
        )

        try:
            result = json.loads(response.choices[0].message.content)
            return result.get('constraints', [])
        except:
            return []

    def _determine_answer_type(self, question: str) -> str:
        """确定期望的答案类型"""
        if any(word in question.lower() for word in ['多少', 'how many', 'count']):
            return 'number'
        elif any(word in question.lower() for word in ['是否', 'whether', 'is']):
            return 'boolean'
        elif any(word in question.lower() for word in ['列出', 'list', 'find']):
            return 'list'
        else:
            return 'text'

# 使用示例
client = OpenAI(api_key='your-key')
understanding = QuestionUnderstanding(client)

question = "找出在北京工作的30岁以上的软件工程师"
analysis = understanding.analyze(question)

print(f"意图: {analysis['intent'].value}")
print(f"实体: {analysis['entities']}")
print(f"约束: {analysis['constraints']}")
print(f"答案类型: {analysis['expected_answer_type']}")
```

### 3.2 实体识别与链接

#### 高级实体链接

```python
import json
import psycopg2
import numpy as np
from typing import List, Dict, Optional
from sentence_transformers import SentenceTransformer

class AdvancedEntityLinker:
    """高级实体链接"""

    def __init__(self, conn, graph_name: str, embedding_model: SentenceTransformer):
        self.conn = conn
        self.graph_name = graph_name
        self.cursor = conn.cursor()
        self.embedding_model = embedding_model

    def link_entities(self, entities: List[Dict]) -> List[Dict]:
        """链接实体到知识图谱"""
        linked = []

        for entity in entities:
            mention = entity['mention']
            entity_type = entity.get('type')

            # 步骤1: 精确匹配
            exact_match = self._exact_match(mention, entity_type)
            if exact_match:
                linked.append({
                    'mention': mention,
                    'linked_to': exact_match,
                    'method': 'exact',
                    'confidence': 1.0
                })
                continue

            # 步骤2: 模糊匹配
            fuzzy_matches = self._fuzzy_match(mention, entity_type)
            if fuzzy_matches:
                linked.append({
                    'mention': mention,
                    'linked_to': fuzzy_matches[0],
                    'method': 'fuzzy',
                    'confidence': fuzzy_matches[0]['score']
                })
                continue

            # 步骤3: 语义匹配
            semantic_match = self._semantic_match(mention, entity_type)
            if semantic_match:
                linked.append({
                    'mention': mention,
                    'linked_to': semantic_match,
                    'method': 'semantic',
                    'confidence': semantic_match['score']
                })
            else:
                # 未链接
                linked.append({
                    'mention': mention,
                    'linked_to': None,
                    'method': 'none',
                    'confidence': 0.0
                })

        return linked

    def _exact_match(self, mention: str, entity_type: Optional[str]) -> Optional[Dict]:
        """精确匹配"""
        type_filter = f"AND '{entity_type}' IN labels(n)" if entity_type else ""

        self.cursor.execute(f"""
            SELECT * FROM cypher('{self.graph_name}', $$
                MATCH (n)
                WHERE n.name = '{mention}' {type_filter}
                RETURN id(n) AS node_id, n.name AS name, labels(n) AS types
                LIMIT 1
            $$) AS (node_id agtype, name agtype, types agtype);
        """)

        result = self.cursor.fetchone()
        if result:
            return {
                'node_id': int(json.loads(result[0])),
                'name': json.loads(result[1]),
                'types': json.loads(result[2])
            }
        return None

    def _fuzzy_match(self, mention: str, entity_type: Optional[str], threshold: float = 0.8) -> List[Dict]:
        """模糊匹配 (Levenshtein距离)"""
        type_filter = f"AND '{entity_type}' IN labels(n)" if entity_type else ""

        self.cursor.execute(f"""
            SELECT * FROM cypher('{self.graph_name}', $$
                MATCH (n)
                WHERE 1=1 {type_filter}
                RETURN id(n) AS node_id, n.name AS name, labels(n) AS types
            $$) AS (node_id agtype, name agtype, types agtype);
        """)

        import Levenshtein

        candidates = []
        for node_id, name, types in self.cursor.fetchall():
            name_str = json.loads(name)
            distance = Levenshtein.distance(mention.lower(), name_str.lower())
            max_len = max(len(mention), len(name_str))
            similarity = 1 - (distance / max_len)

            if similarity >= threshold:
                candidates.append({
                    'node_id': int(json.loads(node_id)),
                    'name': name_str,
                    'types': json.loads(types),
                    'score': similarity
                })

        candidates.sort(key=lambda x: x['score'], reverse=True)
        return candidates

    def _semantic_match(self, mention: str, entity_type: Optional[str]) -> Optional[Dict]:
        """语义匹配 (向量相似度)"""
        # 生成mention的向量
        mention_emb = self.embedding_model.encode(mention)

        # 查询向量存储表
        type_filter = ""
        if entity_type:
            self.cursor.execute(f"""
                SELECT node_id, name, types, embedding
                FROM {self.graph_name}_entity_embeddings
                WHERE '{entity_type}' = ANY(types)
                ORDER BY embedding <=> %s::vector
                LIMIT 1;
            """, (mention_emb.tolist(),))
        else:
            self.cursor.execute(f"""
                SELECT node_id, name, types, embedding
                FROM {self.graph_name}_entity_embeddings
                ORDER BY embedding <=> %s::vector
                LIMIT 1;
            """, (mention_emb.tolist(),))

        result = self.cursor.fetchone()
        if result:
            node_id, name, types, embedding = result

            # 计算相似度
            similarity = np.dot(mention_emb, np.array(embedding)) / (
                np.linalg.norm(mention_emb) * np.linalg.norm(embedding)
            )

            if similarity > 0.7:  # 阈值
                return {
                    'node_id': node_id,
                    'name': name,
                    'types': types,
                    'score': float(similarity)
                }

        return None

# 使用示例
conn = psycopg2.connect("dbname=knowledge_db user=postgres")
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
linker = AdvancedEntityLinker(conn, 'company_kg', embedding_model)

entities = [
    {'mention': 'Apple', 'type': 'Company'},
    {'mention': 'Steve Jobs', 'type': 'Person'},
    {'mention': 'iPhone', 'type': 'Product'}
]

linked_entities = linker.link_entities(entities)
for le in linked_entities:
    print(f"{le['mention']} -> {le['linked_to']} ({le['method']}, {le['confidence']:.2f})")
```

### 3.3 子图检索

#### 多跳子图检索

```python
import json
import psycopg2
from typing import List, Dict

class SubgraphRetriever:
    """子图检索器"""

    def __init__(self, conn, graph_name: str):
        self.conn = conn
        self.graph_name = graph_name
        self.cursor = conn.cursor()

    def retrieve(
        self,
        seed_entities: List[int],
        max_hops: int = 2,
        max_nodes: int = 100
    ) -> Dict:
        """检索子图"""

        nodes = set()
        edges = []

        for seed_id in seed_entities:
            # K-hop邻居检索
            self.cursor.execute(f"""
                SELECT * FROM cypher('{self.graph_name}', $$
                    MATCH path = (seed)-[*1..{max_hops}]-(neighbor)
                    WHERE id(seed) = {seed_id}
                    RETURN DISTINCT
                        [n IN nodes(path) | {{id: id(n), properties: properties(n), labels: labels(n)}}] AS path_nodes,
                        [r IN relationships(path) | {{id: id(r), type: type(r), properties: properties(r), start_id: startNode(r).id, end_id: endNode(r).id}}] AS path_edges
                    LIMIT {max_nodes}
                $$) AS (path_nodes agtype, path_edges agtype);
            """)

            for path_nodes, path_edges in self.cursor.fetchall():
                # 解析节点
                for node in json.loads(path_nodes):
                    nodes.add(node['id'])

                # 解析边
                for edge in json.loads(path_edges):
                    edges.append(edge)

        return {
            'nodes': list(nodes),
            'edges': edges,
            'node_count': len(nodes),
            'edge_count': len(edges)
        }

    def retrieve_with_constraints(
        self,
        seed_entities: List[int],
        constraints: List[Dict],
        max_hops: int = 2
    ) -> Dict:
        """带约束的子图检索"""

        # 构建WHERE子句
        where_clauses = []
        for constraint in constraints:
            prop = constraint['type']
            op = constraint['operator']
            value = constraint['value']

            if op == '>':
                where_clauses.append(f"neighbor.{prop} > {value}")
            elif op == '<':
                where_clauses.append(f"neighbor.{prop} < {value}")
            elif op == '=':
                where_clauses.append(f"neighbor.{prop} = '{value}'")
            elif op == 'contains':
                where_clauses.append(f"neighbor.{prop} CONTAINS '{value}'")

        where_clause = " AND ".join(where_clauses) if where_clauses else "1=1"

        nodes = set()
        edges = []

        for seed_id in seed_entities:
            self.cursor.execute(f"""
                SELECT * FROM cypher('{self.graph_name}', $$
                    MATCH path = (seed)-[*1..{max_hops}]-(neighbor)
                    WHERE id(seed) = {seed_id} AND {where_clause}
                    RETURN DISTINCT
                        nodes(path) AS path_nodes,
                        relationships(path) AS path_edges
                    LIMIT 50
                $$) AS (path_nodes agtype, path_edges agtype);
            """)

            for path_nodes, path_edges in self.cursor.fetchall():
                nodes.update(json.loads(path_nodes))
                edges.extend(json.loads(path_edges))

        return {
            'nodes': list(nodes),
            'edges': edges
        }

# 使用示例
conn = psycopg2.connect("dbname=knowledge_db user=postgres")
retriever = SubgraphRetriever(conn, 'company_kg')

seed_entities = [123, 456]  # Apple Inc., Steve Jobs
constraints = [
    {'type': 'age', 'operator': '>', 'value': 30},
    {'type': 'location', 'operator': '=', 'value': 'San Francisco'}
]

subgraph = retriever.retrieve_with_constraints(
    seed_entities,
    constraints,
    max_hops=2
)

print(f"检索到 {subgraph['node_count']} 个节点, {subgraph['edge_count']} 条边")
```

---

### 3.4 答案生成

#### 答案生成策略

```python
from typing import Dict, List, Optional
from openai import OpenAI

class AnswerGenerator:
    """答案生成器"""

    def __init__(self, llm_client: OpenAI):
        self.llm = llm_client

    def generate_answer(
        self,
        question: str,
        subgraph: Dict,
        query_intent: str,
        answer_type: str
    ) -> Dict:
        """生成答案"""

        # 构建上下文
        context = self._build_context(subgraph)

        # 根据答案类型选择策略
        if answer_type == 'number':
            return self._generate_numeric_answer(question, context)
        elif answer_type == 'list':
            return self._generate_list_answer(question, context)
        elif answer_type == 'boolean':
            return self._generate_boolean_answer(question, context)
        else:
            return self._generate_text_answer(question, context)

    def _build_context(self, subgraph: Dict) -> str:
        """构建上下文"""
        context_parts = []

        # 添加节点信息
        if 'nodes' in subgraph:
            for node in subgraph['nodes']:
                context_parts.append(f"实体: {node.get('name', 'Unknown')}")

        # 添加关系信息
        if 'edges' in subgraph:
            for edge in subgraph['edges']:
                context_parts.append(
                    f"关系: {edge.get('start', 'Unknown')} -[{edge.get('type', 'RELATED')}]-> {edge.get('end', 'Unknown')}"
                )

        return "\n".join(context_parts)

    def _generate_text_answer(self, question: str, context: str) -> Dict:
        """生成文本答案"""
        prompt = f"""基于以下知识图谱信息回答问题。

知识图谱信息:
{context}

问题: {question}

请提供准确、简洁的答案。如果信息不足，请说明。
"""

        response = self.llm.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "你是一个知识图谱问答专家。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1
        )

        answer = response.choices[0].message.content.strip()

        return {
            'answer': answer,
            'type': 'text',
            'confidence': 0.85
        }

    def _generate_numeric_answer(self, question: str, context: str) -> Dict:
        """生成数值答案"""
        # 类似实现，但要求返回数字
        return self._generate_text_answer(question, context)

    def _generate_list_answer(self, question: str, context: str) -> Dict:
        """生成列表答案"""
        # 类似实现，但要求返回列表
        return self._generate_text_answer(question, context)

    def _generate_boolean_answer(self, question: str, context: str) -> Dict:
        """生成布尔答案"""
        # 类似实现，但要求返回是/否
        return self._generate_text_answer(question, context)

# 使用示例
client = OpenAI(api_key='your-key')
generator = AnswerGenerator(client)

subgraph = {
    'nodes': [
        {'name': 'Apple Inc.', 'type': 'Company'},
        {'name': 'Steve Jobs', 'type': 'Person'}
    ],
    'edges': [
        {'start': 'Steve Jobs', 'type': 'FOUNDED', 'end': 'Apple Inc.'}
    ]
}

result = generator.generate_answer(
    "谁创立了Apple?",
    subgraph,
    query_intent='find',
    answer_type='text'
)

print(result['answer'])
```

---

### 3.5 多跳推理

#### 路径推理

```python
class MultiHopReasoner:
    """多跳推理器"""

    def __init__(self, conn, graph_name: str):
        self.conn = conn
        self.graph_name = graph_name
        self.cursor = conn.cursor()

    def reason(self, start_entity: int, end_entity: int, max_hops: int = 3) -> List[Dict]:
        """多跳推理"""
        self.cursor.execute(f"""
            SELECT * FROM cypher('{self.graph_name}', $$
                MATCH path = shortestPath(
                    (start)-[*1..{max_hops}]-(end)
                )
                WHERE id(start) = {start_entity} AND id(end) = {end_entity}
                RETURN path, length(path) AS hop_count
            $$) AS (path agtype, hop_count agtype);
        """)

        results = []
        for row in self.cursor.fetchall():
            path_data = json.loads(row[0])
            hop_count = json.loads(row[1])

            results.append({
                'path': path_data,
                'hop_count': int(hop_count),
                'confidence': self._calculate_confidence(int(hop_count))
            })

        return results

    def _calculate_confidence(self, hop_count: int) -> float:
        """计算置信度"""
        # 跳数越少，置信度越高
        if hop_count == 1:
            return 1.0
        elif hop_count == 2:
            return 0.8
        elif hop_count == 3:
            return 0.6
        else:
            return 0.4

# 使用示例
conn = psycopg2.connect("dbname=knowledge_db user=postgres")
reasoner = MultiHopReasoner(conn, 'company_kg')

paths = reasoner.reason(
    start_entity=123,  # Apple Inc.
    end_entity=456,    # iPhone
    max_hops=3
)

for path in paths:
    print(f"路径: {path['path']}, 跳数: {path['hop_count']}, 置信度: {path['confidence']}")
```

---

## 4. RAG+KG混合架构

### 4.1 混合检索

```python
from typing import List, Dict
import numpy as np

class HybridRetriever:
    """混合检索器（向量+图）"""

    def __init__(self, vector_retriever, graph_retriever):
        self.vector_retriever = vector_retriever
        self.graph_retriever = graph_retriever

    def retrieve(self, query: str, top_k: int = 10) -> Dict:
        """混合检索"""
        # 向量检索
        vector_results = self.vector_retriever.search(query, top_k=top_k)

        # 图检索
        graph_results = self.graph_retriever.retrieve(query, max_nodes=top_k)

        # 融合结果
        fused_results = self._fuse_results(vector_results, graph_results)

        return fused_results

    def _fuse_results(self, vector_results: List[Dict], graph_results: Dict) -> Dict:
        """融合检索结果"""
        # 使用Reciprocal Rank Fusion (RRF)
        rrf_scores = {}

        # 向量结果RRF分数
        for i, result in enumerate(vector_results):
            doc_id = result.get('id')
            rrf_scores[doc_id] = rrf_scores.get(doc_id, 0) + 1 / (60 + i + 1)

        # 图结果RRF分数
        if 'nodes' in graph_results:
            for i, node in enumerate(graph_results['nodes']):
                node_id = node.get('id')
                rrf_scores[node_id] = rrf_scores.get(node_id, 0) + 1 / (60 + i + 1)

        # 排序
        sorted_results = sorted(
            rrf_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )

        return {
            'results': sorted_results[:10],
            'vector_count': len(vector_results),
            'graph_count': len(graph_results.get('nodes', []))
        }
```

### 4.2 结果融合

```python
class ResultFusion:
    """结果融合策略"""

    @staticmethod
    def weighted_fusion(
        vector_results: List[Dict],
        graph_results: Dict,
        vector_weight: float = 0.6,
        graph_weight: float = 0.4
    ) -> List[Dict]:
        """加权融合"""
        fused = []

        # 归一化分数
        vector_scores = [r.get('score', 0) for r in vector_results]
        graph_scores = [n.get('score', 0) for n in graph_results.get('nodes', [])]

        max_vector = max(vector_scores) if vector_scores else 1.0
        max_graph = max(graph_scores) if graph_scores else 1.0

        # 融合
        for result in vector_results:
            normalized_score = (result.get('score', 0) / max_vector) * vector_weight
            fused.append({
                **result,
                'fused_score': normalized_score,
                'source': 'vector'
            })

        for node in graph_results.get('nodes', []):
            normalized_score = (node.get('score', 0) / max_graph) * graph_weight
            fused.append({
                **node,
                'fused_score': normalized_score,
                'source': 'graph'
            })

        # 按融合分数排序
        fused.sort(key=lambda x: x['fused_score'], reverse=True)

        return fused
```

---

## 5. LLM驱动的知识抽取

### 5.1 实体抽取

```python
class EntityExtractor:
    """LLM驱动的实体抽取"""

    def __init__(self, llm_client: OpenAI):
        self.llm = llm_client

    def extract_entities(self, text: str) -> List[Dict]:
        """抽取实体"""
        prompt = f"""从以下文本中抽取实体。

文本:
{text}

以JSON格式返回实体列表，每个实体包含:
- name: 实体名称
- type: 实体类型 (Person/Organization/Location/Product等)
- start_pos: 起始位置
- end_pos: 结束位置

只返回JSON，不要其他内容。
"""

        response = self.llm.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "你是实体抽取专家。"},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0
        )

        try:
            result = json.loads(response.choices[0].message.content)
            return result.get('entities', [])
        except:
            return []

# 使用示例
client = OpenAI(api_key='your-key')
extractor = EntityExtractor(client)

text = "Apple Inc. was founded by Steve Jobs in Cupertino, California."
entities = extractor.extract_entities(text)

for entity in entities:
    print(f"{entity['name']} ({entity['type']})")
```

### 5.2 关系抽取

```python
class RelationExtractor:
    """LLM驱动的关系抽取"""

    def __init__(self, llm_client: OpenAI):
        self.llm = llm_client

    def extract_relations(self, text: str, entities: List[Dict]) -> List[Dict]:
        """抽取关系"""
        entities_str = json.dumps(entities, ensure_ascii=False, indent=2)

        prompt = f"""从以下文本和实体中抽取关系。

文本:
{text}

实体:
{entities_str}

以JSON格式返回关系列表，每个关系包含:
- subject: 主体实体
- predicate: 关系类型
- object: 客体实体
- confidence: 置信度

只返回JSON，不要其他内容。
"""

        response = self.llm.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "你是关系抽取专家。"},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0
        )

        try:
            result = json.loads(response.choices[0].message.content)
            return result.get('relations', [])
        except:
            return []

# 使用示例
client = OpenAI(api_key='your-key')
extractor = RelationExtractor(client)

text = "Apple Inc. was founded by Steve Jobs in Cupertino."
entities = [
    {'name': 'Apple Inc.', 'type': 'Organization'},
    {'name': 'Steve Jobs', 'type': 'Person'},
    {'name': 'Cupertino', 'type': 'Location'}
]

relations = extractor.extract_relations(text, entities)

for rel in relations:
    print(f"{rel['subject']} -[{rel['predicate']}]-> {rel['object']}")
```

---

## 6. 企业级生产架构

### 6.1 系统架构

```text
┌─────────────────────────────────────────────────┐
│            LLM+KG融合系统架构                    │
├─────────────────────────────────────────────────┤
│                                                 │
│  [API Gateway]                                  │
│       │                                         │
│  [LLM Service] ──┐                              │
│       │          │                              │
│  [KG Service] ───┼──→ [PostgreSQL + AGE]       │
│       │          │                              │
│  [Vector Service]─┘                              │
│       │                                         │
│  [Cache Layer (Redis)]                          │
│       │                                         │
│  [Monitoring & Logging]                         │
│                                                 │
└─────────────────────────────────────────────────┘
```

### 6.2 性能优化

```python
class PerformanceOptimizer:
    """性能优化器"""

    def __init__(self):
        self.cache = {}
        self.metrics = {
            'total_queries': 0,
            'cache_hits': 0,
            'avg_latency': 0.0
        }

    def optimize_query(self, query: str) -> str:
        """优化查询"""
        # 查询缓存
        if query in self.cache:
            self.metrics['cache_hits'] += 1
            return self.cache[query]

        # 执行查询
        start_time = time.time()
        result = self._execute_query(query)
        latency = time.time() - start_time

        # 更新指标
        self.metrics['total_queries'] += 1
        self.metrics['avg_latency'] = (
            (self.metrics['avg_latency'] * (self.metrics['total_queries'] - 1) + latency) /
            self.metrics['total_queries']
        )

        # 缓存结果
        self.cache[query] = result

        return result

    def _execute_query(self, query: str) -> str:
        """执行查询"""
        # 实现查询逻辑
        return "result"
```

### 6.3 监控告警

```python
import logging
from typing import Dict
import time

class MonitoringSystem:
    """监控系统"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.metrics = {
            'query_count': 0,
            'error_count': 0,
            'avg_latency': 0.0,
            'cache_hit_rate': 0.0
        }

    def log_query(self, query: str, latency: float, success: bool):
        """记录查询"""
        self.metrics['query_count'] += 1
        self.metrics['avg_latency'] = (
            (self.metrics['avg_latency'] * (self.metrics['query_count'] - 1) + latency) /
            self.metrics['query_count']
        )

        if not success:
            self.metrics['error_count'] += 1

        # 告警检查
        if latency > 2.0:
            self._alert(f"高延迟查询: {latency:.2f}s")

        if self.metrics['error_count'] / self.metrics['query_count'] > 0.1:
            self._alert("错误率过高")

    def _alert(self, message: str):
        """发送告警"""
        self.logger.warning(f"⚠️ 告警: {message}")
        # 可以集成到告警系统（如PagerDuty、Slack等）

# 使用示例
monitor = MonitoringSystem()

# 记录查询
monitor.log_query("查询示例", latency=1.5, success=True)
monitor.log_query("查询示例2", latency=2.5, success=False)

print(f"指标: {monitor.metrics}")
```

---

## 📚 参考资源

1. **OpenAI API文档**: <https://platform.openai.com/docs>
2. **Anthropic Claude API**: <https://docs.anthropic.com/>
3. **LangChain文档**: <https://python.langchain.com/docs/get_started/introduction>
4. **Apache AGE**: <https://age.apache.org/>
5. **KBQA综述论文**: <https://arxiv.org/abs/2108.06688>

---

## 📝 更新日志

- **v1.1** (2025-01-XX): 全面修复版本
  - ✅ 修复代码块格式问题
  - ✅ 补充缺失的导入语句
  - ✅ 完善目录结构
  - ✅ 补充答案生成章节
  - ✅ 补充多跳推理章节
  - ✅ 补充RAG+KG混合架构章节
  - ✅ 补充LLM驱动的知识抽取章节
  - ✅ 补充企业级生产架构章节
  - ✅ 统一代码格式和风格

- **v1.0** (2025-12-04): 初始版本
  - Text-to-Cypher生成
  - KBQA系统完整实现
  - RAG+KG混合架构（框架）
  - LLM驱动的知识抽取（框架）
  - 企业级生产架构（框架）

---

## 🎯 快速开始

### 安装依赖

```bash
pip install openai psycopg2-binary sentence-transformers numpy redis
```

### 基础使用

```python
from openai import OpenAI
import psycopg2

# 初始化
client = OpenAI(api_key='your-key')
conn = psycopg2.connect("dbname=test_db user=postgres")

# Text-to-Cypher生成
from cypher_generator import Text2CypherGenerator
generator = Text2CypherGenerator(conn, 'knowledge_graph', 'your-key')
cypher = generator.generate("有多少个用户?")

# KBQA系统
from kbqa import KBQASystem
kbqa = KBQASystem(conn, 'knowledge_graph', client)
answer = kbqa.answer("Apple的创始人是谁?")
print(answer)
```

---

**下一步**: [08-知识抽取与NER完整指南](./08-知识抽取与NER完整指南.md) | [返回目录](./README.md)
