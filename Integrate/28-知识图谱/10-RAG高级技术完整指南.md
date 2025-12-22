---
> **📋 文档来源**: 新增深化文档
> **📅 创建日期**: 2025-01
> **⚠️ 注意**: 本文档为深度补充，深化RAG技术栈

---

# RAG高级技术完整指南

## 元数据

- **文档版本**: v1.0
- **创建日期**: 2025-01
- **技术栈**: PostgreSQL 16+ | pgvector 0.7+ | LangChain 0.2+ | OpenAI/Anthropic API | Cross-Encoders
- **难度级别**: ⭐⭐⭐⭐⭐ (专家级)
- **预计阅读**: 150分钟
- **前置要求**: 熟悉基础RAG和KG增强RAG架构

---

## 📋 完整目录

- [RAG高级技术完整指南](#rag高级技术完整指南)
  - [元数据](#元数据)
  - [📋 完整目录](#-完整目录)
  - [1. 查询重写与扩展](#1-查询重写与扩展)
    - [1.1 查询重写策略](#11-查询重写策略)
      - [问题诊断式重写](#问题诊断式重写)
      - [多视角重写](#多视角重写)
    - [1.2 查询扩展技术](#12-查询扩展技术)
      - [基于知识图谱的查询扩展](#基于知识图谱的查询扩展)
      - [基于向量相似度的查询扩展](#基于向量相似度的查询扩展)
    - [1.3 LLM驱动的查询优化](#13-llm驱动的查询优化)
  - [2. 多阶段检索系统](#2-多阶段检索系统)
    - [2.1 粗排-精排架构](#21-粗排-精排架构)
    - [2.2 召回策略](#22-召回策略)
      - [混合召回](#混合召回)
    - [2.3 精排模型](#23-精排模型)
      - [Cross-Encoder精排](#cross-encoder精排)
  - [3. 重排序技术(Re-ranking)](#3-重排序技术re-ranking)
    - [3.1 Cross-Encoder重排序](#31-cross-encoder重排序)
      - [高级Cross-Encoder配置](#高级cross-encoder配置)
    - [3.2 混合重排序策略](#32-混合重排序策略)
    - [3.3 上下文感知重排序](#33-上下文感知重排序)
  - [4. Self-RAG架构](#4-self-rag架构)
    - [4.1 Self-RAG原理](#41-self-rag原理)
      - [Self-RAG核心组件](#self-rag核心组件)
  - [5. Agentic RAG](#5-agentic-rag)
    - [5.1 多Agent协作](#51-多agent协作)
      - [多Agent架构](#多agent架构)
      - [专门化Agent实现](#专门化agent实现)
    - [5.2 工具调用与规划](#52-工具调用与规划)
      - [工具系统](#工具系统)
    - [5.3 迭代优化](#53-迭代优化)
      - [迭代优化框架](#迭代优化框架)
  - [7. RAG评估体系](#7-rag评估体系)
    - [7.1 评估指标](#71-评估指标)
      - [检索质量指标](#检索质量指标)
      - [生成质量指标](#生成质量指标)
    - [7.2 基准测试](#72-基准测试)
      - [MTEB基准测试](#mteb基准测试)
      - [自定义评估框架](#自定义评估框架)
    - [7.3 持续优化](#73-持续优化)
      - [A/B测试框架](#ab测试框架)
      - [反馈循环优化](#反馈循环优化)
  - [📚 参考资源](#-参考资源)
  - [📝 更新日志](#-更新日志)

---

## 1. 查询重写与扩展

### 1.1 查询重写策略

查询重写是提升RAG系统检索质量的关键技术，通过改写原始查询来提高检索的准确性和召回率。

#### 问题诊断式重写

```python
class QueryRewriter:
    """查询重写器"""

    def __init__(self, llm):
        self.llm = llm

    def diagnose_and_rewrite(self, query: str) -> Dict[str, Any]:
        """
        诊断查询问题并重写

        Returns:
            {
                'original': 原始查询,
                'diagnosis': 问题诊断,
                'rewritten_queries': 重写后的查询列表,
                'strategy': 使用的策略
            }
        """

        diagnosis_prompt = f"""
        分析以下用户查询，识别潜在问题并重写：

        原始查询: {query}

        请分析：
        1. 查询是否过于简短或模糊？
        2. 是否包含专业术语需要展开？
        3. 是否隐含多个子问题？
        4. 是否需要添加领域上下文？

        请提供3-5个重写版本，每个版本针对不同的检索策略。
        """

        response = self.llm.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "你是一个查询优化专家。"},
                {"role": "user", "content": diagnosis_prompt}
            ],
            temperature=0.7
        )

        # 解析重写结果
        rewritten = self._parse_rewritten_queries(response.choices[0].message.content)

        return {
            'original': query,
            'rewritten_queries': rewritten,
            'strategy': 'diagnosis'
        }

    def _parse_rewritten_queries(self, content: str) -> List[str]:
        """解析LLM返回的重写查询"""
        import re
        # 提取编号的查询
        queries = re.findall(r'\d+[\.\)]\s*(.+)', content)
        return queries[:5]  # 返回前5个
```

#### 多视角重写

```python
class MultiPerspectiveRewriter:
    """多视角查询重写"""

    def __init__(self, llm):
        self.llm = llm
        self.perspectives = [
            'general',      # 通用视角
            'technical',    # 技术视角
            'practical',    # 实用视角
            'comparative',  # 对比视角
            'troubleshooting'  # 问题排查视角
        ]

    def rewrite_from_perspectives(self, query: str) -> Dict[str, str]:
        """
        从不同视角重写查询

        Returns:
            {perspective: rewritten_query}
        """
        rewritten = {}

        for perspective in self.perspectives:
            prompt = f"""
            从{perspective}视角重写以下查询，使其更适合检索相关文档：

            原始查询: {query}

            视角说明:
            - general: 通用、宽泛的表达
            - technical: 强调技术细节和术语
            - practical: 强调实际应用和操作
            - comparative: 强调对比和差异
            - troubleshooting: 强调问题解决和故障排查

            重写查询:
            """

            response = self.llm.chat.completions.create(
                model="gpt-4-turbo",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8
            )

            rewritten[perspective] = response.choices[0].message.content.strip()

        return rewritten
```

### 1.2 查询扩展技术

查询扩展通过添加相关术语、同义词和上下文信息来提升召回率。

#### 基于知识图谱的查询扩展

```python
class KGQueryExpander:
    """基于知识图谱的查询扩展"""

    def __init__(self, graph_conn, graph_name: str):
        self.graph_conn = graph_conn
        self.graph_name = graph_name
        self.cursor = graph_conn.cursor()

    def expand_with_related_entities(self, query: str, entities: List[str]) -> List[str]:
        """
        使用知识图谱扩展查询，添加相关实体

        Args:
            query: 原始查询
            entities: 识别出的实体列表

        Returns:
            扩展后的查询列表
        """
        expanded_queries = [query]  # 保留原始查询

        for entity in entities:
            # 查找实体的相关实体（1-2跳）
            related = self._get_related_entities(entity, max_hops=2)

            # 生成扩展查询
            for related_entity in related[:3]:  # 每个实体取前3个相关实体
                expanded = f"{query} {related_entity['label']}"
                expanded_queries.append(expanded)

        return expanded_queries

    def _get_related_entities(self, entity: str, max_hops: int = 2) -> List[Dict]:
        """获取实体的相关实体"""
        self.cursor.execute(f"""
            SELECT * FROM cypher('{self.graph_name}', $$
                MATCH (e:Entity {{name: '{entity}'}})
                MATCH path = (e)-[*1..{max_hops}]-(related:Entity)
                RETURN DISTINCT related.name as name, related.label as label
                ORDER BY length(path)
                LIMIT 10
            $$) AS (name text, label text);
        """)

        return [{'name': row[0], 'label': row[1]} for row in self.cursor.fetchall()]
```

#### 基于向量相似度的查询扩展

```python
class VectorQueryExpander:
    """基于向量相似度的查询扩展"""

    def __init__(self, embedding_model, vector_db):
        self.embedding_model = embedding_model
        self.vector_db = vector_db

    def expand_with_similar_terms(self, query: str, top_k: int = 5) -> List[str]:
        """
        使用向量相似度查找相似术语扩展查询

        Args:
            query: 原始查询
            top_k: 返回的相似术语数

        Returns:
            扩展后的查询列表
        """
        # 查询向量
        query_emb = self.embedding_model.encode(query)

        # 在术语库中查找相似术语
        similar_terms = self.vector_db.similarity_search_by_vector(
            query_emb,
            k=top_k
        )

        expanded_queries = [query]
        for term_doc in similar_terms:
            expanded = f"{query} {term_doc.page_content}"
            expanded_queries.append(expanded)

        return expanded_queries
```

### 1.3 LLM驱动的查询优化

使用LLM的推理能力进行智能查询优化。

```python
class LLMQueryOptimizer:
    """LLM驱动的查询优化器"""

    def __init__(self, llm, few_shot_examples: List[Dict] = None):
        self.llm = llm
        self.few_shot_examples = few_shot_examples or []

    def optimize_query(self, query: str, context: Dict = None) -> Dict[str, Any]:
        """
        优化查询，生成多个优化版本

        Args:
            query: 原始查询
            context: 上下文信息（如领域、历史查询等）

        Returns:
            {
                'original': 原始查询,
                'optimized': 优化后的主查询,
                'variants': 查询变体列表,
                'keywords': 提取的关键词,
                'intent': 意图识别
            }
        """

        # 构建Few-Shot示例
        examples_text = "\n\n".join([
            f"原始: {ex['original']}\n优化: {ex['optimized']}\n意图: {ex['intent']}"
            for ex in self.few_shot_examples[:3]
        ])

        context_info = ""
        if context:
            context_info = f"\n上下文: {context}"

        prompt = f"""
        优化以下用户查询，使其更适合检索相关文档：

        {examples_text}

        原始查询: {query}{context_info}

        请：
        1. 识别查询意图
        2. 提取关键信息
        3. 生成优化后的查询
        4. 提供2-3个查询变体

        格式：
        意图: <意图>
        关键词: <关键词列表>
        优化查询: <优化后的查询>
        变体1: <变体1>
        变体2: <变体2>
        """

        response = self.llm.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "你是查询优化专家，擅长将用户查询改写为最适合检索的形式。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )

        # 解析结果
        result = self._parse_optimization_result(response.choices[0].message.content)
        result['original'] = query

        return result

    def _parse_optimization_result(self, content: str) -> Dict[str, Any]:
        """解析优化结果"""
        import re

        intent_match = re.search(r'意图:\s*(.+)', content)
        keywords_match = re.search(r'关键词:\s*(.+)', content)
        optimized_match = re.search(r'优化查询:\s*(.+)', content)
        variants = re.findall(r'变体\d+:\s*(.+)', content)

        return {
            'intent': intent_match.group(1).strip() if intent_match else None,
            'keywords': keywords_match.group(1).strip().split(',') if keywords_match else [],
            'optimized': optimized_match.group(1).strip() if optimized_match else None,
            'variants': [v.strip() for v in variants]
        }
```

---

## 2. 多阶段检索系统

### 2.1 粗排-精排架构

多阶段检索通过粗排（召回大量候选）和精排（精确排序）两阶段提升检索质量。

```python
class TwoStageRetriever:
    """两阶段检索器"""

    def __init__(
        self,
        vector_store,      # 向量数据库（粗排）
        reranker=None,     # 重排序模型（精排）
        top_k_coarse=100,  # 粗排召回数
        top_k_final=10     # 最终返回数
    ):
        self.vector_store = vector_store
        self.reranker = reranker
        self.top_k_coarse = top_k_coarse
        self.top_k_final = top_k_final

    def retrieve(self, query: str, filters: Dict = None) -> List[Dict]:
        """
        两阶段检索

        Args:
            query: 查询文本
            filters: 元数据过滤条件

        Returns:
            排序后的文档列表
        """
        # 阶段1: 粗排 - 向量相似度检索
        coarse_results = self._coarse_retrieve(query, filters)

        if not self.reranker:
            # 无重排序模型，直接返回粗排结果
            return coarse_results[:self.top_k_final]

        # 阶段2: 精排 - 重排序
        reranked_results = self._fine_rerank(query, coarse_results)

        return reranked_results[:self.top_k_final]

    def _coarse_retrieve(self, query: str, filters: Dict = None) -> List[Dict]:
        """粗排：向量相似度检索"""
        # 向量检索
        docs = self.vector_store.similarity_search_with_score(
            query,
            k=self.top_k_coarse,
            filter=filters
        )

        results = []
        for doc, score in docs:
            results.append({
                'content': doc.page_content,
                'metadata': doc.metadata,
                'score': float(score),
                'source': 'vector'
            })

        return results

    def _fine_rerank(self, query: str, candidates: List[Dict]) -> List[Dict]:
        """精排：使用重排序模型"""
        if not self.reranker:
            return candidates

        # 准备重排序输入
        pairs = [(query, item['content']) for item in candidates]

        # 重排序得分
        rerank_scores = self.reranker.predict(pairs)

        # 合并分数并排序
        for i, item in enumerate(candidates):
            # 综合分数（可加权平均）
            item['rerank_score'] = float(rerank_scores[i])
            item['final_score'] = 0.3 * item['score'] + 0.7 * item['rerank_score']

        # 按最终分数排序
        return sorted(candidates, key=lambda x: x['final_score'], reverse=True)
```

### 2.2 召回策略

#### 混合召回

```python
class HybridRecallStrategy:
    """混合召回策略"""

    def __init__(self, vector_store, keyword_search=None, graph_search=None):
        self.vector_store = vector_store      # 向量检索
        self.keyword_search = keyword_search  # 关键词检索（如BM25）
        self.graph_search = graph_search      # 图检索

    def hybrid_recall(
        self,
        query: str,
        vector_weight=0.6,
        keyword_weight=0.3,
        graph_weight=0.1
    ) -> List[Dict]:
        """
        混合召回

        Args:
            query: 查询文本
            vector_weight: 向量检索权重
            keyword_weight: 关键词检索权重
            graph_weight: 图检索权重
        """
        all_results = {}

        # 1. 向量检索
        if self.vector_store:
            vector_results = self._vector_recall(query, top_k=50)
            for item in vector_results:
                doc_id = item['id']
                if doc_id not in all_results:
                    all_results[doc_id] = item
                    all_results[doc_id]['scores'] = {}
                all_results[doc_id]['scores']['vector'] = item['score'] * vector_weight

        # 2. 关键词检索
        if self.keyword_search:
            keyword_results = self._keyword_recall(query, top_k=50)
            for item in keyword_results:
                doc_id = item['id']
                if doc_id not in all_results:
                    all_results[doc_id] = item
                    all_results[doc_id]['scores'] = {}
                all_results[doc_id]['scores']['keyword'] = item['score'] * keyword_weight

        # 3. 图检索
        if self.graph_search:
            graph_results = self._graph_recall(query, top_k=30)
            for item in graph_results:
                doc_id = item['id']
                if doc_id not in all_results:
                    all_results[doc_id] = item
                    all_results[doc_id]['scores'] = {}
                all_results[doc_id]['scores']['graph'] = item['score'] * graph_weight

        # 融合分数
        for doc_id, item in all_results.items():
            item['final_score'] = sum(item['scores'].values())

        # 排序并返回
        sorted_results = sorted(
            all_results.values(),
            key=lambda x: x['final_score'],
            reverse=True
        )

        return sorted_results[:100]  # 返回Top 100用于精排

    def _vector_recall(self, query: str, top_k: int) -> List[Dict]:
        """向量检索召回"""
        docs = self.vector_store.similarity_search_with_score(query, k=top_k)
        return [
            {
                'id': f"vec_{i}",
                'content': doc.page_content,
                'metadata': doc.metadata,
                'score': float(score)
            }
            for i, (doc, score) in enumerate(docs)
        ]

    def _keyword_recall(self, query: str, top_k: int) -> List[Dict]:
        """关键词检索召回（BM25等）"""
        # 这里使用PostgreSQL全文搜索作为示例
        # 实际可以使用Elasticsearch、OpenSearch等
        if not self.keyword_search:
            return []

        results = self.keyword_search.search(query, top_k=top_k)
        return [
            {
                'id': f"kw_{i}",
                'content': result['content'],
                'metadata': result['metadata'],
                'score': float(result['score'])
            }
            for i, result in enumerate(results)
        ]

    def _graph_recall(self, query: str, top_k: int) -> List[Dict]:
        """图检索召回"""
        if not self.graph_search:
            return []

        # 实体识别
        entities = self.graph_search.extract_entities(query)

        # 子图检索
        subgraph_results = self.graph_search.retrieve_subgraph(entities, top_k=top_k)

        return [
            {
                'id': f"graph_{i}",
                'content': result['text'],
                'metadata': result['metadata'],
                'score': float(result['relevance'])
            }
            for i, result in enumerate(subgraph_results)
        ]
```

### 2.3 精排模型

#### Cross-Encoder精排

```python
from sentence_transformers import CrossEncoder

class CrossEncoderReranker:
    """Cross-Encoder重排序器"""

    def __init__(self, model_name: str = 'cross-encoder/ms-marco-MiniLM-L-12-v2'):
        """
        初始化Cross-Encoder

        Args:
            model_name: 预训练模型名称
                - cross-encoder/ms-marco-MiniLM-L-12-v2 (快速)
                - cross-encoder/ms-marco-MiniLM-L-6-v2 (更快)
                - cross-encoder/ms-marco-electra-base (更准确)
        """
        self.model = CrossEncoder(model_name, max_length=512)

    def rerank(self, query: str, candidates: List[Dict], top_k: int = 10) -> List[Dict]:
        """
        重排序候选文档

        Args:
            query: 查询文本
            candidates: 候选文档列表
            top_k: 返回Top K结果

        Returns:
            重排序后的文档列表
        """
        # 准备输入对
        pairs = [(query, item['content']) for item in candidates]

        # 批量预测
        scores = self.model.predict(pairs)

        # 添加重排序分数
        for i, item in enumerate(candidates):
            item['rerank_score'] = float(scores[i])

        # 按重排序分数排序
        reranked = sorted(candidates, key=lambda x: x['rerank_score'], reverse=True)

        return reranked[:top_k]
```

---

## 3. 重排序技术(Re-ranking)

### 3.1 Cross-Encoder重排序

Cross-Encoder是当前最常用的重排序技术，通过联合编码查询-文档对获得精确的相关性分数。

#### 高级Cross-Encoder配置

```python
class AdvancedCrossEncoderReranker:
    """高级Cross-Encoder重排序器"""

    def __init__(
        self,
        model_name: str = 'cross-encoder/ms-marco-MiniLM-L-12-v2',
        batch_size: int = 32,
        device: str = 'cuda'
    ):
        self.model = CrossEncoder(model_name, device=device)
        self.batch_size = batch_size

    def rerank_with_metadata(
        self,
        query: str,
        candidates: List[Dict],
        metadata_weight: float = 0.1
    ) -> List[Dict]:
        """
        结合元数据的重排序

        Args:
            query: 查询文本
            candidates: 候选文档
            metadata_weight: 元数据权重（用于最终分数融合）
        """
        # 构建查询-文档对
        pairs = []
        for item in candidates:
            # 可以将元数据信息融入文档文本
            enhanced_content = self._enhance_with_metadata(item)
            pairs.append((query, enhanced_content))

        # 批量预测
        scores = self.model.predict(
            pairs,
            batch_size=self.batch_size,
            show_progress_bar=True
        )

        # 融合分数
        for i, item in enumerate(candidates):
            rerank_score = float(scores[i])
            metadata_score = self._compute_metadata_score(item, query)

            # 加权融合
            item['rerank_score'] = rerank_score
            item['metadata_score'] = metadata_score
            item['final_score'] = (1 - metadata_weight) * rerank_score + metadata_weight * metadata_score

        # 排序
        return sorted(candidates, key=lambda x: x['final_score'], reverse=True)

    def _enhance_with_metadata(self, item: Dict) -> str:
        """使用元数据增强文档内容"""
        content = item['content']
        metadata = item.get('metadata', {})

        # 添加元数据信息（如类别、标签等）
        metadata_text = ""
        if 'category' in metadata:
            metadata_text += f"[类别: {metadata['category']}] "
        if 'tags' in metadata:
            tags = ', '.join(metadata['tags']) if isinstance(metadata['tags'], list) else metadata['tags']
            metadata_text += f"[标签: {tags}] "

        return f"{metadata_text}{content}"

    def _compute_metadata_score(self, item: Dict, query: str) -> float:
        """计算基于元数据的相关性分数"""
        metadata = item.get('metadata', {})

        # 简单的元数据匹配分数
        score = 0.0

        # 类别匹配
        if 'category' in metadata and metadata['category'].lower() in query.lower():
            score += 0.3

        # 标签匹配
        if 'tags' in metadata:
            tags = metadata['tags'] if isinstance(metadata['tags'], list) else [metadata['tags']]
            matched_tags = sum(1 for tag in tags if tag.lower() in query.lower())
            score += 0.2 * min(matched_tags / len(tags), 1.0)

        return min(score, 1.0)
```

### 3.2 混合重排序策略

结合多种重排序方法的混合策略。

```python
class HybridRerankingStrategy:
    """混合重排序策略"""

    def __init__(
        self,
        cross_encoder=None,
        llm_reranker=None,
        keyword_reranker=None
    ):
        self.cross_encoder = cross_encoder
        self.llm_reranker = llm_reranker
        self.keyword_reranker = keyword_reranker

    def hybrid_rerank(
        self,
        query: str,
        candidates: List[Dict],
        strategy: str = 'adaptive'
    ) -> List[Dict]:
        """
        混合重排序

        Args:
            query: 查询文本
            candidates: 候选文档
            strategy: 策略
                - 'adaptive': 自适应选择
                - 'ensemble': 集成所有方法
                - 'cascade': 级联（先用快速方法，再用精确方法）
        """
        if strategy == 'adaptive':
            return self._adaptive_rerank(query, candidates)
        elif strategy == 'ensemble':
            return self._ensemble_rerank(query, candidates)
        elif strategy == 'cascade':
            return self._cascade_rerank(query, candidates)
        else:
            raise ValueError(f"Unknown strategy: {strategy}")

    def _adaptive_rerank(self, query: str, candidates: List[Dict]) -> List[Dict]:
        """自适应重排序：根据查询特征选择方法"""
        # 查询长度
        query_length = len(query.split())

        # 候选数量
        num_candidates = len(candidates)

        if num_candidates <= 20 and query_length <= 20:
            # 少量候选且查询简单：使用Cross-Encoder
            if self.cross_encoder:
                return self.cross_encoder.rerank(query, candidates)
        elif num_candidates > 100:
            # 大量候选：先关键词过滤，再Cross-Encoder
            if self.keyword_reranker:
                filtered = self.keyword_reranker.filter(query, candidates, top_k=50)
                if self.cross_encoder:
                    return self.cross_encoder.rerank(query, filtered)
        else:
            # 中等规模：使用LLM重排序（如果可用）
            if self.llm_reranker:
                return self.llm_reranker.rerank(query, candidates)
            elif self.cross_encoder:
                return self.cross_encoder.rerank(query, candidates)

        # 默认：返回原顺序
        return candidates

    def _ensemble_rerank(self, query: str, candidates: List[Dict]) -> List[Dict]:
        """集成重排序：综合多种方法"""
        scores_dict = {}

        # Cross-Encoder分数
        if self.cross_encoder:
            ce_results = self.cross_encoder.rerank(query, candidates)
            for i, item in enumerate(ce_results):
                doc_id = item.get('id', i)
                scores_dict[doc_id] = scores_dict.get(doc_id, {})
                scores_dict[doc_id]['ce'] = item['rerank_score']

        # LLM重排序分数
        if self.llm_reranker:
            llm_results = self.llm_reranker.rerank(query, candidates)
            for i, item in enumerate(llm_results):
                doc_id = item.get('id', i)
                scores_dict[doc_id] = scores_dict.get(doc_id, {})
                scores_dict[doc_id]['llm'] = item['rerank_score']

        # 加权融合
        weights = {'ce': 0.7, 'llm': 0.3}
        for item in candidates:
            doc_id = item.get('id', candidates.index(item))
            final_score = sum(
                scores_dict.get(doc_id, {}).get(method, 0) * weight
                for method, weight in weights.items()
            )
            item['final_score'] = final_score

        # 排序
        return sorted(candidates, key=lambda x: x['final_score'], reverse=True)

    def _cascade_rerank(self, query: str, candidates: List[Dict]) -> List[Dict]:
        """级联重排序：先用快速方法筛选，再用精确方法"""
        # 第一层：关键词快速筛选
        if self.keyword_reranker:
            filtered = self.keyword_reranker.filter(query, candidates, top_k=50)
        else:
            filtered = candidates[:50]

        # 第二层：Cross-Encoder精确排序
        if self.cross_encoder:
            return self.cross_encoder.rerank(query, filtered)
        else:
            return filtered
```

### 3.3 上下文感知重排序

考虑用户上下文和历史的重排序。

```python
class ContextAwareReranker:
    """上下文感知重排序"""

    def __init__(self, base_reranker, context_encoder=None):
        self.base_reranker = base_reranker
        self.context_encoder = context_encoder

    def rerank_with_context(
        self,
        query: str,
        candidates: List[Dict],
        user_context: Dict = None,
        conversation_history: List[Dict] = None
    ) -> List[Dict]:
        """
        考虑上下文的重排序

        Args:
            query: 当前查询
            candidates: 候选文档
            user_context: 用户上下文（偏好、历史等）
            conversation_history: 对话历史
        """
        # 使用基础重排序获得初始分数
        reranked = self.base_reranker.rerank(query, candidates)

        # 上下文增强
        if user_context or conversation_history:
            for item in reranked:
                context_score = self._compute_context_score(
                    item,
                    query,
                    user_context,
                    conversation_history
                )
                # 融合上下文分数
                item['context_score'] = context_score
                item['final_score'] = 0.7 * item['rerank_score'] + 0.3 * context_score

            # 重新排序
            reranked = sorted(reranked, key=lambda x: x['final_score'], reverse=True)

        return reranked

    def _compute_context_score(
        self,
        item: Dict,
        query: str,
        user_context: Dict,
        conversation_history: List[Dict]
    ) -> float:
        """计算上下文相关分数"""
        score = 0.0

        # 用户偏好匹配
        if user_context:
            preferences = user_context.get('preferences', [])
            item_tags = item.get('metadata', {}).get('tags', [])
            if isinstance(item_tags, str):
                item_tags = [item_tags]

            # 标签匹配
            matched = sum(1 for pref in preferences if pref in item_tags)
            score += 0.3 * (matched / max(len(preferences), 1))

        # 对话历史相关性
        if conversation_history:
            # 计算与历史查询的相关性
            history_queries = [h['query'] for h in conversation_history[-3:]]
            history_embedding = self.context_encoder.encode(' '.join(history_queries))
            item_embedding = self.context_encoder.encode(item['content'])

            similarity = np.dot(history_embedding, item_embedding) / (
                np.linalg.norm(history_embedding) * np.linalg.norm(item_embedding)
            )
            score += 0.2 * similarity

        return min(score, 1.0)
```

---

## 4. Self-RAG架构

### 4.1 Self-RAG原理

Self-RAG通过自适应的检索和生成决策，动态决定是否需要检索、检索什么内容、如何生成答案。

#### Self-RAG核心组件

```python
class SelfRAG:
    """Self-RAG实现"""

    def __init__(
        self,
        llm,
        retriever,
        critique_llm=None
    ):
        self.llm = llm
        self.retriever = retriever
        self.critique_llm = critique_llm or llm

    def generate(self, query: str, max_iterations: int = 3) -> Dict[str, Any]:
        """
        Self-RAG生成流程

        Args:
            query: 用户查询
            max_iterations: 最大迭代次数
        """
        context = []
        retrieved_docs = []
        generation_history = []

        for iteration in range(max_iterations):
            # 1. 决定是否需要检索
            retrieve_decision = self._decide_retrieve(query, context, generation_history)

            if retrieve_decision['should_retrieve']:
                # 2. 决定检索什么
                retrieval_query = self._decide_retrieval_query(
                    query,
                    context,
                    generation_history
                )

                # 3. 执行检索
                docs = self.retriever.retrieve(retrieval_query, top_k=5)
                retrieved_docs.extend(docs)
                context.extend([doc['content'] for doc in docs])

            # 4. 生成答案片段
            generation_result = self._generate_with_critique(
                query,
                context,
                generation_history
            )

            generation_history.append(generation_result)

            # 5. 判断是否继续
            if generation_result['is_complete']:
                break

        # 6. 最终答案生成
        final_answer = self._finalize_answer(query, context, generation_history)

        return {
            'answer': final_answer,
            'retrieved_docs': retrieved_docs,
            'generation_history': generation_history,
            'iterations': len(generation_history)
        }

    def _decide_retrieve(
        self,
        query: str,
        context: List[str],
        history: List[Dict]
    ) -> Dict[str, Any]:
        """决定是否需要检索"""
        prompt = f"""
        判断是否需要检索外部文档来回答以下查询。

        查询: {query}
        已有上下文: {len(context)} 个文档片段

        如果查询需要：
        - 事实性信息
        - 最新数据
        - 特定领域知识
        则回答 YES

        如果已有上下文足够回答，回答 NO

        回答格式: YES/NO
        理由: <简短理由>
        """

        response = self.critique_llm.chat.completions.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        result_text = response.choices[0].message.content
        should_retrieve = "YES" in result_text.upper()

        return {
            'should_retrieve': should_retrieve,
            'reasoning': result_text
        }

    def _decide_retrieval_query(
        self,
        query: str,
        context: List[str],
        history: List[Dict]
    ) -> str:
        """决定检索查询（可能需要改写）"""
        # 如果有生成历史，可能需要基于历史生成新的检索查询
        if history:
            prompt = f"""
            基于原始查询和已生成的内容，决定下一步应该检索什么信息。

            原始查询: {query}
            已生成内容: {history[-1]['text']}

            生成一个优化后的检索查询:
            """

            response = self.llm.chat.completions.create(
                model="gpt-4-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )

            return response.choices[0].message.content.strip()
        else:
            return query

    def _generate_with_critique(
        self,
        query: str,
        context: List[str],
        history: List[Dict]
    ) -> Dict[str, Any]:
        """生成并自我批判"""
        # 生成
        context_text = "\n\n".join(context[-5:])  # 使用最近5个文档

        generation_prompt = f"""
        基于以下上下文回答查询。

        查询: {query}
        上下文:
        {context_text}

        回答:
        """

        generation_response = self.llm.chat.completions.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": generation_prompt}],
            temperature=0.7
        )

        generated_text = generation_response.choices[0].message.content

        # 自我批判
        critique = self._critique_generation(
            query,
            context_text,
            generated_text
        )

        return {
            'text': generated_text,
            'critique': critique,
            'is_complete': critique['is_sufficient'],
            'needs_revision': critique['needs_revision']
        }

    def _critique_generation(
        self,
        query: str,
        context: str,
        generated: str
    ) -> Dict[str, Any]:
        """批判生成的内容"""
        prompt = f"""
        批判以下生成的回答：

        查询: {query}
        上下文: {context[:500]}
        生成回答: {generated}

        评估：
        1. 回答是否充分？(YES/NO)
        2. 是否准确引用上下文？(YES/NO)
        3. 是否需要修正？(YES/NO)
        4. 是否需要更多信息？(YES/NO)
        """

        response = self.critique_llm.chat.completions.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        result_text = response.choices[0].message.content

        return {
            'is_sufficient': "YES" in result_text.upper() and "充分" in result_text or "sufficient" in result_text.lower(),
            'is_accurate': "YES" in result_text.upper() and "准确" in result_text or "accurate" in result_text.lower(),
            'needs_revision': "YES" in result_text.upper() and "修正" in result_text or "revision" in result_text.lower(),
            'needs_more_info': "YES" in result_text.upper() and "更多信息" in result_text or "more information" in result_text.lower(),
            'reasoning': result_text
        }

    def _finalize_answer(
        self,
        query: str,
        context: List[str],
        history: List[Dict]
    ) -> str:
        """最终答案生成"""
        # 整合所有生成片段
        all_texts = [h['text'] for h in history]

        prompt = f"""
        整合以下内容片段，生成一个完整、连贯的回答。

        查询: {query}

        内容片段:
        {chr(10).join([f"{i+1}. {text}" for i, text in enumerate(all_texts)])}

        生成最终回答:
        """

        response = self.llm.chat.completions.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )

        return response.choices[0].message.content
```

---

## 5. Agentic RAG

### 5.1 多Agent协作

Agentic RAG通过多个专门的Agent协作，实现更智能的检索和生成。每个Agent负责特定的任务，通过协作完成复杂的查询。

#### 多Agent架构

```python
from typing import List, Dict, Any
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.tools import Tool
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

class MultiAgentRAG:
    """多Agent协作RAG系统"""

    def __init__(
        self,
        llm,
        retriever_agent,
        query_agent,
        synthesis_agent,
        validator_agent
    ):
        self.llm = llm
        self.retriever_agent = retriever_agent
        self.query_agent = query_agent
        self.synthesis_agent = synthesis_agent
        self.validator_agent = validator_agent

    def process_query(self, query: str) -> Dict[str, Any]:
        """
        多Agent协作处理查询

        Args:
            query: 用户查询

        Returns:
            最终答案和中间结果
        """
        # 1. Query Agent: 分析查询，制定计划
        query_plan = self.query_agent.analyze(query)

        # 2. Retriever Agent: 执行检索
        retrieved_docs = []
        for sub_query in query_plan['sub_queries']:
            docs = self.retriever_agent.retrieve(sub_query)
            retrieved_docs.extend(docs)

        # 3. Synthesis Agent: 综合信息生成答案
        answer = self.synthesis_agent.synthesize(
            query,
            retrieved_docs,
            query_plan
        )

        # 4. Validator Agent: 验证答案
        validation = self.validator_agent.validate(
            query,
            answer,
            retrieved_docs
        )

        # 如果验证失败，重新检索和生成
        if not validation['is_valid']:
            # 使用反馈改进检索
            improved_docs = self.retriever_agent.retrieve_with_feedback(
                query,
                validation['feedback']
            )
            answer = self.synthesis_agent.synthesize(
                query,
                improved_docs,
                query_plan
            )

        return {
            'answer': answer,
            'query_plan': query_plan,
            'retrieved_docs': retrieved_docs,
            'validation': validation
        }
```

#### 专门化Agent实现

```python
class QueryAnalysisAgent:
    """查询分析Agent"""

    def __init__(self, llm):
        self.llm = llm

    def analyze(self, query: str) -> Dict[str, Any]:
        """分析查询，生成执行计划"""
        prompt = f"""
        分析以下查询，生成执行计划：

        查询: {query}

        请：
        1. 识别查询意图（信息检索、计算、对比等）
        2. 分解为子查询（如果需要）
        3. 确定检索策略
        4. 估计复杂度

        返回JSON格式：
        {{
            "intent": "查询意图",
            "sub_queries": ["子查询1", "子查询2"],
            "retrieval_strategy": "检索策略",
            "complexity": "复杂度"
        }}
        """

        response = self.llm.chat.completions.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )

        import json
        return json.loads(response.choices[0].message.content)

class RetrievalAgent:
    """检索Agent"""

    def __init__(self, vector_store, graph_store, keyword_search):
        self.vector_store = vector_store
        self.graph_store = graph_store
        self.keyword_search = keyword_search

    def retrieve(self, query: str, strategy: str = 'hybrid') -> List[Dict]:
        """执行检索"""
        results = []

        if strategy in ['hybrid', 'vector']:
            vector_results = self.vector_store.similarity_search(query, k=5)
            results.extend([
                {'content': doc.page_content, 'source': 'vector', 'score': 0.9}
                for doc in vector_results
            ])

        if strategy in ['hybrid', 'keyword']:
            keyword_results = self.keyword_search.search(query, k=5)
            results.extend([
                {'content': result['text'], 'source': 'keyword', 'score': 0.8}
                for result in keyword_results
            ])

        if strategy in ['hybrid', 'graph']:
            graph_results = self.graph_store.query(query)
            results.extend([
                {'content': result['text'], 'source': 'graph', 'score': 0.85}
                for result in graph_results
            ])

        # 去重和排序
        return self._deduplicate_and_rank(results)

    def _deduplicate_and_rank(self, results: List[Dict]) -> List[Dict]:
        """去重并排序"""
        seen = set()
        unique_results = []
        for result in results:
            content_hash = hash(result['content'][:100])  # 使用前100字符作为hash
            if content_hash not in seen:
                seen.add(content_hash)
                unique_results.append(result)

        # 按分数排序
        return sorted(unique_results, key=lambda x: x['score'], reverse=True)[:10]

class SynthesisAgent:
    """综合Agent"""

    def __init__(self, llm):
        self.llm = llm

    def synthesize(
        self,
        query: str,
        docs: List[Dict],
        plan: Dict[str, Any]
    ) -> str:
        """综合信息生成答案"""
        context = "\n\n".join([
            f"[来源: {doc['source']}]\n{doc['content']}"
            for doc in docs[:10]
        ])

        prompt = f"""
        基于以下上下文回答查询。

        查询: {query}
        执行计划: {plan}

        上下文:
        {context}

        请生成一个准确、完整的答案。
        """

        response = self.llm.chat.completions.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )

        return response.choices[0].message.content

class ValidatorAgent:
    """验证Agent"""

    def __init__(self, llm, fact_checker=None):
        self.llm = llm
        self.fact_checker = fact_checker

    def validate(
        self,
        query: str,
        answer: str,
        docs: List[Dict]
    ) -> Dict[str, Any]:
        """验证答案"""
        prompt = f"""
        验证以下答案是否正确、完整。

        查询: {query}
        答案: {answer}
        支持文档数: {len(docs)}

        请评估：
        1. 答案是否准确？
        2. 答案是否完整？
        3. 答案是否有事实依据？
        4. 是否需要更多信息？

        返回JSON格式：
        {{
            "is_valid": true/false,
            "confidence": 0.0-1.0,
            "issues": ["问题列表"],
            "feedback": "改进建议"
        }}
        """

        response = self.llm.chat.completions.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        import json
        return json.loads(response.choices[0].message.content)
```

### 5.2 工具调用与规划

Agentic RAG通过工具调用扩展能力，包括数据库查询、API调用、计算工具等。

#### 工具系统

```python
from langchain.tools import Tool
from langchain.agents import initialize_agent, AgentType

class ToolBasedRAG:
    """基于工具的RAG系统"""

    def __init__(self, llm, vector_store):
        self.llm = llm
        self.vector_store = vector_store
        self.tools = self._create_tools()
        self.agent = initialize_agent(
            self.tools,
            llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True
        )

    def _create_tools(self) -> List[Tool]:
        """创建工具集"""
        tools = [
            Tool(
                name="向量检索",
                func=self._vector_search,
                description="使用向量相似度检索相关文档。输入：查询文本"
            ),
            Tool(
                name="SQL查询",
                func=self._sql_query,
                description="执行SQL查询数据库。输入：SQL查询语句"
            ),
            Tool(
                name="图查询",
                func=self._graph_query,
                description="查询知识图谱。输入：Cypher查询语句"
            ),
            Tool(
                name="计算器",
                func=self._calculator,
                description="执行数学计算。输入：数学表达式"
            ),
            Tool(
                name="实体识别",
                func=self._entity_recognition,
                description="识别文本中的实体。输入：文本"
            )
        ]
        return tools

    def _vector_search(self, query: str) -> str:
        """向量检索工具"""
        docs = self.vector_store.similarity_search(query, k=5)
        return "\n".join([doc.page_content for doc in docs])

    def _sql_query(self, sql: str) -> str:
        """SQL查询工具"""
        # 执行SQL查询
        # 这里应该连接数据库执行查询
        try:
            # result = execute_sql(sql)
            return f"SQL查询结果: {sql}"
        except Exception as e:
            return f"SQL查询错误: {str(e)}"

    def _graph_query(self, cypher: str) -> str:
        """图查询工具"""
        # 执行Cypher查询
        try:
            # result = execute_cypher(cypher)
            return f"图查询结果: {cypher}"
        except Exception as e:
            return f"图查询错误: {str(e)}"

    def _calculator(self, expression: str) -> str:
        """计算器工具"""
        try:
            result = eval(expression)  # 注意：生产环境应使用更安全的eval替代
            return str(result)
        except Exception as e:
            return f"计算错误: {str(e)}"

    def _entity_recognition(self, text: str) -> str:
        """实体识别工具"""
        # 使用NER模型识别实体
        # entities = ner_model.predict(text)
        return f"识别到的实体: {text}"

    def query(self, question: str) -> str:
        """使用工具回答查询"""
        return self.agent.run(question)
```

### 5.3 迭代优化

Agentic RAG通过迭代优化不断提升答案质量。

#### 迭代优化框架

```python
class IterativeRAG:
    """迭代优化RAG"""

    def __init__(self, base_rag, max_iterations: int = 3):
        self.base_rag = base_rag
        self.max_iterations = max_iterations

    def iterative_improve(self, query: str) -> Dict[str, Any]:
        """迭代改进答案"""
        history = []
        current_answer = None

        for iteration in range(self.max_iterations):
            # 生成或改进答案
            if iteration == 0:
                # 第一次：基础检索和生成
                result = self.base_rag.query(query)
                current_answer = result['answer']
            else:
                # 后续迭代：基于反馈改进
                feedback = self._generate_feedback(query, current_answer, history)
                improved_result = self.base_rag.query_with_feedback(query, feedback)
                current_answer = improved_result['answer']

            # 评估答案质量
            quality_score = self._evaluate_answer(query, current_answer)

            history.append({
                'iteration': iteration,
                'answer': current_answer,
                'quality_score': quality_score
            })

            # 如果质量足够高，停止迭代
            if quality_score > 0.9:
                break

        return {
            'final_answer': current_answer,
            'iterations': len(history),
            'history': history
        }

    def _generate_feedback(
        self,
        query: str,
        current_answer: str,
        history: List[Dict]
    ) -> str:
        """生成改进反馈"""
        prompt = f"""
        分析当前答案，生成改进建议。

        查询: {query}
        当前答案: {current_answer}
        历史迭代: {len(history)}

        请指出：
        1. 答案的问题
        2. 需要改进的地方
        3. 应该检索哪些额外信息
        """

        response = self.base_rag.llm.chat.completions.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )

        return response.choices[0].message.content

    def _evaluate_answer(self, query: str, answer: str) -> float:
        """评估答案质量"""
        prompt = f"""
        评估答案质量（0-1分）。

        查询: {query}
        答案: {answer}

        请从以下维度评分：
        1. 准确性（0.3）
        2. 完整性（0.3）
        3. 相关性（0.2）
        4. 可读性（0.2）

        返回0-1之间的分数。
        """

        response = self.base_rag.llm.chat.completions.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        try:
            score = float(response.choices[0].message.content)
            return max(0.0, min(1.0, score))
        except:
            return 0.5
```

---

## 7. RAG评估体系

### 7.1 评估指标

RAG系统的评估需要从多个维度进行，包括检索质量、生成质量和整体效果。

#### 检索质量指标

```python
from typing import List, Dict, Set
import numpy as np

class RetrievalMetrics:
    """检索质量评估指标"""

    @staticmethod
    def precision_at_k(retrieved: List[str], relevant: Set[str], k: int) -> float:
        """
        Precision@K: 前K个结果中相关文档的比例

        Args:
            retrieved: 检索到的文档ID列表
            relevant: 相关文档ID集合
            k: 评估前K个结果

        Returns:
            Precision@K分数
        """
        retrieved_k = retrieved[:k]
        relevant_retrieved = len([doc for doc in retrieved_k if doc in relevant])
        return relevant_retrieved / k if k > 0 else 0.0

    @staticmethod
    def recall_at_k(retrieved: List[str], relevant: Set[str], k: int) -> float:
        """
        Recall@K: 前K个结果中相关文档占所有相关文档的比例

        Args:
            retrieved: 检索到的文档ID列表
            relevant: 相关文档ID集合
            k: 评估前K个结果

        Returns:
            Recall@K分数
        """
        if len(relevant) == 0:
            return 0.0

        retrieved_k = retrieved[:k]
        relevant_retrieved = len([doc for doc in retrieved_k if doc in relevant])
        return relevant_retrieved / len(relevant)

    @staticmethod
    def f1_at_k(retrieved: List[str], relevant: Set[str], k: int) -> float:
        """F1@K: Precision和Recall的调和平均"""
        precision = RetrievalMetrics.precision_at_k(retrieved, relevant, k)
        recall = RetrievalMetrics.recall_at_k(retrieved, relevant, k)

        if precision + recall == 0:
            return 0.0

        return 2 * precision * recall / (precision + recall)

    @staticmethod
    def mrr(retrieved_lists: List[List[str]], relevant_sets: List[Set[str]]) -> float:
        """
        MRR (Mean Reciprocal Rank): 平均倒数排名

        Args:
            retrieved_lists: 每个查询的检索结果列表
            relevant_sets: 每个查询的相关文档集合

        Returns:
            MRR分数
        """
        reciprocal_ranks = []

        for retrieved, relevant in zip(retrieved_lists, relevant_sets):
            if len(relevant) == 0:
                continue

            # 找到第一个相关文档的排名
            rank = None
            for i, doc in enumerate(retrieved, 1):
                if doc in relevant:
                    rank = i
                    break

            if rank is not None:
                reciprocal_ranks.append(1.0 / rank)
            else:
                reciprocal_ranks.append(0.0)

        return np.mean(reciprocal_ranks) if reciprocal_ranks else 0.0

    @staticmethod
    def ndcg_at_k(
        retrieved: List[str],
        relevant: Set[str],
        k: int,
        gains: Dict[str, float] = None
    ) -> float:
        """
        NDCG@K (Normalized Discounted Cumulative Gain)

        Args:
            retrieved: 检索到的文档ID列表
            relevant: 相关文档ID集合（或带分数的字典）
            k: 评估前K个结果
            gains: 文档的相关性分数（可选，默认1.0）

        Returns:
            NDCG@K分数
        """
        if gains is None:
            gains = {doc: 1.0 for doc in relevant}

        # 计算DCG@K
        dcg = 0.0
        for i, doc in enumerate(retrieved[:k], 1):
            if doc in gains:
                gain = gains[doc]
                dcg += gain / np.log2(i + 1)

        # 计算IDCG@K（理想情况下的DCG）
        ideal_gains = sorted(gains.values(), reverse=True)[:k]
        idcg = sum(gain / np.log2(i + 2) for i, gain in enumerate(ideal_gains))

        # NDCG = DCG / IDCG
        return dcg / idcg if idcg > 0 else 0.0

    @staticmethod
    def evaluate_all(
        retrieved_lists: List[List[str]],
        relevant_sets: List[Set[str]],
        k_values: List[int] = [1, 5, 10]
    ) -> Dict[str, float]:
        """评估所有指标"""
        results = {}

        # MRR
        results['MRR'] = RetrievalMetrics.mrr(retrieved_lists, relevant_sets)

        # Precision, Recall, F1, NDCG @ K
        for k in k_values:
            precisions = [
                RetrievalMetrics.precision_at_k(ret, rel, k)
                for ret, rel in zip(retrieved_lists, relevant_sets)
            ]
            recalls = [
                RetrievalMetrics.recall_at_k(ret, rel, k)
                for ret, rel in zip(retrieved_lists, relevant_sets)
            ]
            f1s = [
                RetrievalMetrics.f1_at_k(ret, rel, k)
                for ret, rel in zip(retrieved_lists, relevant_sets)
            ]
            ndcgs = [
                RetrievalMetrics.ndcg_at_k(ret, rel, k)
                for ret, rel in zip(retrieved_lists, relevant_sets)
            ]

            results[f'Precision@{k}'] = np.mean(precisions)
            results[f'Recall@{k}'] = np.mean(recalls)
            results[f'F1@{k}'] = np.mean(f1s)
            results[f'NDCG@{k}'] = np.mean(ndcgs)

        return results

# 使用示例
retrieved = [
    ['doc1', 'doc2', 'doc3', 'doc4', 'doc5'],  # 查询1的检索结果
    ['doc2', 'doc1', 'doc5', 'doc6', 'doc7']   # 查询2的检索结果
]
relevant = [
    {'doc1', 'doc3'},  # 查询1的相关文档
    {'doc2', 'doc5'}   # 查询2的相关文档
]

metrics = RetrievalMetrics.evaluate_all(retrieved, relevant, k_values=[1, 5, 10])
print(metrics)
```

#### 生成质量指标

```python
from rouge_score import rouge_scorer
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
import openai

class GenerationMetrics:
    """生成质量评估指标"""

    def __init__(self):
        self.rouge_scorer = rouge_scorer.RougeScorer(
            ['rouge1', 'rouge2', 'rougeL'],
            use_stemmer=True
        )
        self.smoothing = SmoothingFunction().method1

    def rouge_score(self, generated: str, reference: str) -> Dict[str, float]:
        """
        ROUGE分数：评估生成文本的摘要质量

        Args:
            generated: 生成的文本
            reference: 参考文本

        Returns:
            ROUGE-1, ROUGE-2, ROUGE-L分数
        """
        scores = self.rouge_scorer.score(reference, generated)
        return {
            'rouge1': scores['rouge1'].fmeasure,
            'rouge2': scores['rouge2'].fmeasure,
            'rougeL': scores['rougeL'].fmeasure
        }

    def bleu_score(self, generated: str, reference: str) -> float:
        """
        BLEU分数：评估生成文本与参考文本的相似度

        Args:
            generated: 生成的文本（分词后的列表）
            reference: 参考文本（分词后的列表）

        Returns:
            BLEU分数
        """
        # 简单示例，实际使用需要分词
        generated_tokens = generated.split()
        reference_tokens = [reference.split()]

        return sentence_bleu(
            reference_tokens,
            generated_tokens,
            smoothing_function=self.smoothing
        )

    def semantic_similarity(
        self,
        generated: str,
        reference: str,
        embedding_model
    ) -> float:
        """
        语义相似度：使用嵌入向量计算语义相似度

        Args:
            generated: 生成的文本
            reference: 参考文本
            embedding_model: 嵌入模型

        Returns:
            余弦相似度分数
        """
        gen_emb = embedding_model.encode(generated)
        ref_emb = embedding_model.encode(reference)

        similarity = np.dot(gen_emb, ref_emb) / (
            np.linalg.norm(gen_emb) * np.linalg.norm(ref_emb)
        )

        return float(similarity)

    def faithfulness_score(
        self,
        generated: str,
        source_docs: List[str],
        llm
    ) -> float:
        """
        忠实度分数：评估生成内容是否忠实于源文档

        Args:
            generated: 生成的文本
            source_docs: 源文档列表
            llm: LLM模型（用于验证）

        Returns:
            忠实度分数（0-1）
        """
        prompt = f"""
        评估以下生成的答案是否忠实于提供的源文档。

        源文档:
        {chr(10).join([f"{i+1}. {doc[:200]}" for i, doc in enumerate(source_docs[:3])])}

        生成的答案:
        {generated}

        请评估：
        1. 答案中的所有事实是否都在源文档中？
        2. 答案是否添加了源文档中没有的信息？
        3. 答案是否曲解了源文档的意思？

        返回0-1之间的分数（1表示完全忠实）：
        """

        response = llm.chat.completions.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        try:
            score = float(response.choices[0].message.content)
            return max(0.0, min(1.0, score))
        except:
            return 0.5

    def answer_relevancy(
        self,
        query: str,
        answer: str,
        embedding_model
    ) -> float:
        """
        答案相关性：评估答案与查询的相关性

        Args:
            query: 查询文本
            answer: 生成的答案
            embedding_model: 嵌入模型

        Returns:
            相关性分数（0-1）
        """
        query_emb = embedding_model.encode(query)
        answer_emb = embedding_model.encode(answer)

        similarity = np.dot(query_emb, answer_emb) / (
            np.linalg.norm(query_emb) * np.linalg.norm(answer_emb)
        )

        return float(similarity)
```

### 7.2 基准测试

使用标准基准测试评估RAG系统的性能。

#### MTEB基准测试

```python
from mteb import MTEB
from sentence_transformers import SentenceTransformer

class RAGEvaluator:
    """RAG系统评估器"""

    def __init__(self, embedding_model, retriever):
        self.embedding_model = embedding_model
        self.retriever = retriever

    def evaluate_on_mteb(self, task_name: str = "Retrieval"):
        """
        在MTEB基准上评估嵌入模型

        Args:
            task_name: 任务名称（如"Retrieval", "Clustering"等）
        """
        evaluation = MTEB(task_types=[task_name])

        results = evaluation.run(
            self.embedding_model,
            output_folder=f"results/{task_name}",
            eval_splits=["test"]
        )

        return results

    def evaluate_on_beir(
        self,
        dataset_name: str = "nfcorpus",
        split: str = "test"
    ) -> Dict[str, float]:
        """
        在BEIR基准上评估检索系统

        Args:
            dataset_name: BEIR数据集名称
            split: 数据集分割（train/test/dev）

        Returns:
            评估指标字典
        """
        from beir import util, dataset
        from beir.retrieval.evaluation import EvaluateRetrieval
        from beir.retrieval.search.dense import DenseRetrievalExactSearch

        # 下载数据集
        url = f"https://public.ukp.informatik.tu-darmstadt.de/thakur/BEIR/datasets/{dataset_name}.zip"
        data_path = util.download_and_unzip(url, "datasets")

        # 加载数据集
        corpus, queries, qrels = dataset.load_beir_data(data_path, split=split)

        # 创建检索器
        model = DenseRetrievalExactSearch(
            self.embedding_model,
            batch_size=128
        )

        # 执行检索
        retriever = EvaluateRetrieval(model, score_function="cos_sim")
        results = retriever.retrieve(corpus, queries)

        # 评估
        metrics = retriever.evaluate(qrels, results, k_values=[1, 3, 5, 10])

        return metrics
```

#### 自定义评估框架

```python
class CustomRAGEvaluator:
    """自定义RAG评估框架"""

    def __init__(self, rag_system):
        self.rag_system = rag_system

    def evaluate_dataset(
        self,
        test_set: List[Dict[str, Any]],
        metrics_config: Dict[str, bool] = None
    ) -> Dict[str, Any]:
        """
        评估RAG系统在测试集上的表现

        Args:
            test_set: 测试集，每个样本包含query, expected_answer, relevant_docs
            metrics_config: 评估指标配置

        Returns:
            评估结果
        """
        if metrics_config is None:
            metrics_config = {
                'retrieval': True,
                'generation': True,
                'end_to_end': True
            }

        results = {
            'retrieval_metrics': {},
            'generation_metrics': {},
            'end_to_end_metrics': {}
        }

        retrieval_results = []
        generation_results = []

        for sample in test_set:
            query = sample['query']
            expected_answer = sample['expected_answer']
            relevant_docs = set(sample['relevant_docs'])

            # 执行RAG查询
            rag_result = self.rag_system.query(query)

            # 评估检索质量
            if metrics_config['retrieval']:
                retrieved_docs = [doc['id'] for doc in rag_result['retrieved_docs']]
                retrieval_results.append({
                    'retrieved': retrieved_docs,
                    'relevant': relevant_docs
                })

            # 评估生成质量
            if metrics_config['generation']:
                gen_metrics = GenerationMetrics()
                rouge = gen_metrics.rouge_score(
                    rag_result['answer'],
                    expected_answer
                )
                generation_results.append({
                    'rouge1': rouge['rouge1'],
                    'rouge2': rouge['rouge2'],
                    'rougeL': rouge['rougeL']
                })

        # 计算平均指标
        if metrics_config['retrieval'] and retrieval_results:
            retrieved_lists = [r['retrieved'] for r in retrieval_results]
            relevant_sets = [r['relevant'] for r in retrieval_results]
            results['retrieval_metrics'] = RetrievalMetrics.evaluate_all(
                retrieved_lists,
                relevant_sets
            )

        if metrics_config['generation'] and generation_results:
            results['generation_metrics'] = {
                'rouge1': np.mean([r['rouge1'] for r in generation_results]),
                'rouge2': np.mean([r['rouge2'] for r in generation_results]),
                'rougeL': np.mean([r['rougeL'] for r in generation_results])
            }

        return results
```

### 7.3 持续优化

建立持续优化机制，不断提升RAG系统性能。

#### A/B测试框架

```python
class RAGABTest:
    """RAG系统A/B测试框架"""

    def __init__(self, system_a, system_b, traffic_split: float = 0.5):
        self.system_a = system_a
        self.system_b = system_b
        self.traffic_split = traffic_split  # A组流量比例
        self.results_a = []
        self.results_b = []

    def query(self, query: str, user_id: str) -> Dict[str, Any]:
        """
        根据用户ID分配流量，执行查询

        Args:
            query: 用户查询
            user_id: 用户ID（用于流量分配）

        Returns:
            查询结果和实验组信息
        """
        # 基于用户ID的哈希分配流量
        import hashlib
        user_hash = int(hashlib.md5(user_id.encode()).hexdigest(), 16)
        is_group_a = (user_hash % 100) < (self.traffic_split * 100)

        if is_group_a:
            result = self.system_a.query(query)
            result['experiment_group'] = 'A'
            self.results_a.append({
                'query': query,
                'user_id': user_id,
                'result': result
            })
        else:
            result = self.system_b.query(query)
            result['experiment_group'] = 'B'
            self.results_b.append({
                'query': query,
                'user_id': user_id,
                'result': result
            })

        return result

    def compare_results(self) -> Dict[str, Any]:
        """比较A/B两组的结果"""
        # 这里可以计算各种指标
        # 例如：响应时间、用户满意度、点击率等

        return {
            'group_a_count': len(self.results_a),
            'group_b_count': len(self.results_b),
            'metrics': {
                # 可以添加具体的比较指标
            }
        }
```

#### 反馈循环优化

```python
class FeedbackLoop:
    """反馈循环优化机制"""

    def __init__(self, rag_system, feedback_store):
        self.rag_system = rag_system
        self.feedback_store = feedback_store  # 反馈存储（如数据库）

    def collect_feedback(
        self,
        query: str,
        answer: str,
        retrieved_docs: List[Dict],
        user_feedback: Dict[str, Any]
    ):
        """
        收集用户反馈

        Args:
            query: 查询
            answer: 生成的答案
            retrieved_docs: 检索到的文档
            user_feedback: 用户反馈（如评分、相关性标注等）
        """
        feedback_record = {
            'query': query,
            'answer': answer,
            'retrieved_docs': retrieved_docs,
            'user_rating': user_feedback.get('rating'),
            'is_relevant': user_feedback.get('is_relevant'),
            'timestamp': datetime.now()
        }

        self.feedback_store.save(feedback_record)

    def analyze_feedback(self, time_window: int = 7) -> Dict[str, Any]:
        """
        分析反馈数据，识别改进点

        Args:
            time_window: 分析时间窗口（天）
        """
        # 获取时间窗口内的反馈
        feedbacks = self.feedback_store.get_recent(time_window)

        # 分析低评分查询
        low_rated = [f for f in feedbacks if f.get('user_rating', 5) < 3]

        # 分析不相关文档
        irrelevant_docs = [
            f for f in feedbacks
            if not f.get('is_relevant', True)
        ]

        # 识别问题模式
        problems = {
            'low_rated_queries': low_rated[:10],  # Top 10问题查询
            'irrelevant_docs_count': len(irrelevant_docs),
            'average_rating': np.mean([f.get('user_rating', 5) for f in feedbacks])
        }

        return problems

    def optimize_based_on_feedback(self, problems: Dict[str, Any]):
        """
        基于反馈优化系统

        Args:
            problems: 分析出的问题
        """
        # 根据问题调整检索策略
        if problems['irrelevant_docs_count'] > 100:
            # 提高检索阈值
            self.rag_system.retriever.score_threshold *= 1.1

        # 优化查询重写
        if problems['average_rating'] < 3.5:
            # 启用更积极的查询重写
            self.rag_system.query_rewriter.enabled = True

        # 调整重排序权重
        # 根据反馈调整重排序模型的权重
        if problems['low_rated_queries']:
            # 分析低评分查询的模式，调整重排序策略
            pass
```

---

*[多模态RAG章节将在下一版本补充]*

---

## 📚 参考资源

1. **Self-RAG论文**: <https://arxiv.org/abs/2310.11511>
2. **RAG评估**: <https://github.com/langchain-ai/ragas>
3. **Cross-Encoder模型**: <https://www.sbert.net/docs/pretrained-cross-encoders.html>
4. **Query Expansion**: <https://arxiv.org/abs/2305.03653>

---

## 📝 更新日志

- **v1.0** (2025-01): 初始版本
  - 查询重写与扩展
  - 多阶段检索系统
  - Cross-Encoder重排序
  - Self-RAG架构

---

**下一步**: 补充Agentic RAG、多模态RAG和评估体系章节 | [返回目录](./README.md)
