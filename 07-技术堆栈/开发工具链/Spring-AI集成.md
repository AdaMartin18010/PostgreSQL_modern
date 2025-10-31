# 7.1.1 Spring AI 集成

> **更新时间**: 2025 年 11 月 1 日  
> **文档编号**: 07-01-01  
> **技术版本**: Spring AI 1.0+, Spring Boot 3.2+

## 📑 目录

- [7.1.1 Spring AI 集成](#711-spring-ai-集成)
  - [📑 目录](#-目录)
  - [1. 概述](#1-概述)
    - [1.1 文档目标](#11-文档目标)
    - [1.2 Spring AI 简介](#12-spring-ai-简介)
    - [1.3 集成价值](#13-集成价值)
  - [2. 核心功能](#2-核心功能)
    - [2.1 向量存储集成](#21-向量存储集成)
      - [2.1.1 PGVectorStore 特性](#211-pgvectorstore-特性)
      - [2.1.2 自动模式创建](#212-自动模式创建)
      - [2.1.3 批量操作支持](#213-批量操作支持)
    - [2.2 RAG 应用支持](#22-rag-应用支持)
      - [2.2.1 文档加载](#221-文档加载)
      - [2.2.2 向量化处理](#222-向量化处理)
      - [2.2.3 检索增强生成](#223-检索增强生成)
  - [3. 快速开始](#3-快速开始)
    - [3.1 项目初始化](#31-项目初始化)
      - [3.1.1 添加依赖](#311-添加依赖)
      - [3.1.2 项目结构](#312-项目结构)
    - [3.2 配置数据库](#32-配置数据库)
      - [3.2.1 数据源配置](#321-数据源配置)
      - [3.2.2 Spring AI 配置](#322-spring-ai-配置)
    - [3.3 创建向量存储](#33-创建向量存储)
      - [3.3.1 基础配置](#331-基础配置)
      - [3.3.2 高级配置](#332-高级配置)
    - [3.4 使用向量存储](#34-使用向量存储)
      - [3.4.1 添加文档](#341-添加文档)
      - [3.4.2 相似度搜索](#342-相似度搜索)
      - [3.4.3 元数据过滤](#343-元数据过滤)
  - [4. RAG 应用开发](#4-rag-应用开发)
    - [4.1 RAG 服务实现](#41-rag-服务实现)
      - [4.1.1 基础 RAG](#411-基础-rag)
      - [4.1.2 高级 RAG](#412-高级-rag)
    - [4.2 REST API 开发](#42-rest-api-开发)
      - [4.2.1 控制器实现](#421-控制器实现)
      - [4.2.2 请求响应模型](#422-请求响应模型)
    - [4.3 流式响应](#43-流式响应)
      - [4.3.1 流式聊天](#431-流式聊天)
      - [4.3.2 Server-Sent Events](#432-server-sent-events)
  - [5. 高级特性](#5-高级特性)
    - [5.1 混合搜索](#51-混合搜索)
      - [5.1.1 向量 + 全文搜索](#511-向量--全文搜索)
      - [5.1.2 RRF 算法融合](#512-rrf-算法融合)
    - [5.2 批量操作](#52-批量操作)
      - [5.2.1 批量添加文档](#521-批量添加文档)
      - [5.2.2 批量删除文档](#522-批量删除文档)
    - [5.3 性能优化](#53-性能优化)
      - [5.3.1 索引优化](#531-索引优化)
      - [5.3.2 查询优化](#532-查询优化)
  - [6. 最佳实践](#6-最佳实践)
    - [6.1 配置最佳实践](#61-配置最佳实践)
    - [6.2 性能最佳实践](#62-性能最佳实践)
    - [6.3 安全最佳实践](#63-安全最佳实践)
  - [7. 常见问题](#7-常见问题)
    - [7.1 依赖问题](#71-依赖问题)
    - [7.2 配置问题](#72-配置问题)
    - [7.3 性能问题](#73-性能问题)
  - [8. 参考资料](#8-参考资料)
    - [8.1 官方文档](#81-官方文档)
    - [8.2 技术文档](#82-技术文档)
    - [8.3 相关资源](#83-相关资源)

---

## 1. 概述

### 1.1 文档目标

**核心目标**:

本文档提供 Spring AI 与 PostgreSQL + pgvector 的集成指南，帮助开发者快速构建基于向量搜索的 RAG 应用
。

**文档价值**:

| 价值项       | 说明               | 影响             |
| ------------ | ------------------ | ---------------- |
| **快速集成** | 提供完整的集成步骤 | 减少开发时间     |
| **RAG 应用** | 支持检索增强生成   | 提升 AI 应用能力 |
| **性能优化** | 提供性能优化建议   | 提高应用性能     |

### 1.2 Spring AI 简介

**Spring AI 概述**:

Spring AI 是 Spring 生态系统中的 AI 框架，提供了与各种 AI 服务（OpenAI、Azure OpenAI、Anthropic 等）
的集成，以及向量存储、RAG 应用等能力。

**核心特性**:

| 特性            | 说明                   | 优势             |
| --------------- | ---------------------- | ---------------- |
| **向量存储**    | 支持多种向量存储       | 灵活选择存储方案 |
| **RAG 支持**    | 内置 RAG 应用支持      | 简化 RAG 开发    |
| **流式响应**    | 支持流式聊天响应       | 提升用户体验     |
| **Spring 集成** | 与 Spring 生态无缝集成 | 易于使用和维护   |

### 1.3 集成价值

**集成优势**:

| 优势          | 说明                           | 影响               |
| ------------- | ------------------------------ | ------------------ |
| **向量搜索**  | PostgreSQL + pgvector 向量搜索 | **高性能向量检索** |
| **统一存储**  | 业务数据与向量数据统一存储     | **简化架构**       |
| **ACID 事务** | 支持事务一致性                 | **数据一致性**     |
| **SQL 支持**  | 可使用 SQL 进行复杂查询        | **灵活查询**       |

## 2. 核心功能

### 2.1 向量存储集成

#### 2.1.1 PGVectorStore 特性

**PGVectorStore 核心特性**:

| 特性           | 说明                      | 优势       |
| -------------- | ------------------------- | ---------- |
| **自动建表**   | 自动创建向量存储表        | 简化初始化 |
| **索引支持**   | 支持 HNSW 和 IVFFlat 索引 | 高性能查询 |
| **元数据支持** | 支持文档元数据存储和过滤  | 灵活查询   |
| **批量操作**   | 支持批量添加和查询        | 提高性能   |

**支持的索引类型**:

```java
// HNSW 索引（高精度，推荐）
PgVectorStore.PgIndexType.HNSW

// IVFFlat 索引（大规模数据）
PgVectorStore.PgIndexType.IVFFLAT
```

**支持的距离类型**:

```java
// 余弦距离（推荐用于文本向量）
PgVectorStore.PgDistanceType.COSINE_DISTANCE

// 欧氏距离
PgVectorStore.PgDistanceType.EUCLIDEAN_DISTANCE

// 内积
PgVectorStore.PgDistanceType.INNER_PRODUCT
```

#### 2.1.2 自动模式创建

**自动模式创建配置**:

```yaml
spring:
  ai:
    vectorstore:
      pgvector:
        # 自动初始化表结构
        initialize-schema: true

        # 索引类型
        index-type: HNSW

        # 距离类型
        distance-type: COSINE_DISTANCE

        # 向量维度
        dimensions: 1536
```

**自动创建的表结构**:

```sql
-- Spring AI 自动创建的表
CREATE TABLE vector_store (
    id VARCHAR(255) PRIMARY KEY,
    content TEXT,
    embedding vector(1536),
    metadata JSONB
);

-- 自动创建的索引
CREATE INDEX vector_store_embedding_idx
ON vector_store
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);
```

#### 2.1.3 批量操作支持

**批量操作 API**:

```java
@Service
public class DocumentService {

    private final VectorStore vectorStore;

    public DocumentService(VectorStore vectorStore) {
        this.vectorStore = vectorStore;
    }

    // 批量添加文档
    public void addDocuments(List<String> contents,
                           List<Map<String, Object>> metadataList) {
        List<Document> documents = new ArrayList<>();
        for (int i = 0; i < contents.size(); i++) {
            Document doc = new Document(
                contents.get(i),
                metadataList.get(i)
            );
            documents.add(doc);
        }

        // 批量添加
        vectorStore.add(documents);
    }

    // 批量相似度搜索
    public List<List<Document>> batchSearch(List<String> queries, int topK) {
        List<List<Document>> results = new ArrayList<>();
        for (String query : queries) {
            List<Document> docs = vectorStore.similaritySearch(
                SearchRequest.builder()
                    .query(query)
                    .topK(topK)
                    .build()
            );
            results.add(docs);
        }
        return results;
    }
}
```

### 2.2 RAG 应用支持

#### 2.2.1 文档加载

**支持的文档格式**:

| 格式         | 说明          | 使用场景       |
| ------------ | ------------- | -------------- |
| **PDF**      | PDF 文档      | 技术文档、报告 |
| **Word**     | DOC/DOCX 文档 | 办公文档       |
| **Markdown** | Markdown 文档 | 技术文档       |
| **TXT**      | 纯文本文件    | 简单文档       |
| **Web**      | HTML/网页内容 | 网页爬取       |

**文档加载示例**:

```java
@Service
public class DocumentLoaderService {

    private final TikaDocumentReader tikaReader;
    private final VectorStore vectorStore;
    private final EmbeddingClient embeddingClient;

    // 加载 PDF 文档
    public void loadPdfDocument(String filePath) {
        Resource resource = new FileSystemResource(filePath);

        // 读取文档内容
        Document doc = tikaReader.read(resource);

        // 添加元数据
        Map<String, Object> metadata = new HashMap<>();
        metadata.put("source", filePath);
        metadata.put("type", "PDF");
        doc.getMetadata().putAll(metadata);

        // 存储到向量数据库
        vectorStore.add(List.of(doc));
    }

    // 加载多个文档
    public void loadDocuments(List<String> filePaths) {
        List<Document> documents = new ArrayList<>();

        for (String filePath : filePaths) {
            Resource resource = new FileSystemResource(filePath);
            Document doc = tikaReader.read(resource);
            documents.add(doc);
        }

        // 批量添加
        vectorStore.add(documents);
    }
}
```

#### 2.2.2 向量化处理

**向量化流程**:

```java
@Service
public class EmbeddingService {

    private final EmbeddingClient embeddingClient;

    public EmbeddingService(EmbeddingClient embeddingClient) {
        this.embeddingClient = embeddingClient;
    }

    // 文本向量化
    public List<Double> embed(String text) {
        EmbeddingResponse response = embeddingClient.embedForResponse(
            List.of(text)
        );
        return response.getResult().getOutput();
    }

    // 批量向量化
    public List<List<Double>> embedBatch(List<String> texts) {
        EmbeddingResponse response = embeddingClient.embedForResponse(texts);
        return response.getResults().stream()
            .map(Embedding::getOutput)
            .collect(Collectors.toList());
    }
}
```

**支持的 Embedding 模型**:

| 模型                                | 提供商 | 维度 | 说明               |
| ----------------------------------- | ------ | ---- | ------------------ |
| **text-embedding-3-small**          | OpenAI | 1536 | 推荐用于大多数场景 |
| **text-embedding-3-large**          | OpenAI | 3072 | 高精度场景         |
| **text-embedding-ada-002**          | OpenAI | 1536 | 旧版本，已废弃     |
| **text-multilingual-embedding-002** | OpenAI | 1536 | 多语言支持         |

#### 2.2.3 检索增强生成

**RAG 实现**:

```java
@Service
public class RAGService {

    private final VectorStore vectorStore;
    private final ChatClient chatClient;
    private final EmbeddingClient embeddingClient;

    public RAGService(VectorStore vectorStore,
                      ChatClient chatClient,
                      EmbeddingClient embeddingClient) {
        this.vectorStore = vectorStore;
        this.chatClient = chatClient;
        this.embeddingClient = embeddingClient;
    }

    // 基础 RAG
    public String chat(String userMessage) {
        // 1. 向量搜索相关文档
        List<Document> relevantDocs = vectorStore.similaritySearch(
            SearchRequest.builder()
                .query(userMessage)
                .topK(5)
                .build()
        );

        // 2. 构建上下文
        String context = relevantDocs.stream()
            .map(Document::getContent)
            .collect(Collectors.joining("\n\n"));

        // 3. 构建提示词
        String prompt = String.format(
            "基于以下上下文回答问题：\n\n%s\n\n问题：%s\n\n答案：",
            context,
            userMessage
        );

        // 4. 调用 LLM
        return chatClient.call(prompt);
    }

    // 高级 RAG（带元数据过滤）
    public String chatWithFilter(String userMessage,
                                 Map<String, Object> metadataFilter) {
        // 1. 带元数据过滤的搜索
        List<Document> relevantDocs = vectorStore.similaritySearch(
            SearchRequest.builder()
                .query(userMessage)
                .topK(5)
                .similarityThreshold(0.7)  // 相似度阈值
                .filter(metadataFilter)     // 元数据过滤
                .build()
        );

        // 2. 构建上下文（只使用高相关性文档）
        String context = relevantDocs.stream()
            .filter(doc -> doc.getMetadata().containsKey("score") &&
                          (Double) doc.getMetadata().get("score") > 0.7)
            .map(Document::getContent)
            .collect(Collectors.joining("\n\n"));

        // 3. 构建提示词
        String prompt = String.format(
            "基于以下上下文回答问题，如果上下文中没有相关信息，请说明：\n\n%s\n\n问题：%s\n\n答案：",
            context,
            userMessage
        );

        // 4. 调用 LLM
        return chatClient.call(prompt);
    }
}
```

## 3. 快速开始

### 3.1 项目初始化

#### 3.1.1 添加依赖

**Maven 依赖**:

```xml
<dependencies>
    <!-- Spring Boot -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter</artifactId>
    </dependency>

    <!-- Spring Boot Web -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-web</artifactId>
    </dependency>

    <!-- Spring AI PostgreSQL PGVector Store -->
    <dependency>
        <groupId>org.springframework.ai</groupId>
        <artifactId>spring-ai-postgresql-pgvector-store</artifactId>
        <version>1.0.0</version>
    </dependency>

    <!-- Spring Data JPA -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-data-jpa</artifactId>
    </dependency>

    <!-- PostgreSQL Driver -->
    <dependency>
        <groupId>org.postgresql</groupId>
        <artifactId>postgresql</artifactId>
        <scope>runtime</scope>
    </dependency>

    <!-- Spring AI OpenAI -->
    <dependency>
        <groupId>org.springframework.ai</groupId>
        <artifactId>spring-ai-openai-spring-boot-starter</artifactId>
        <version>1.0.0</version>
    </dependency>

    <!-- Spring AI Tika (文档读取) -->
    <dependency>
        <groupId>org.springframework.ai</groupId>
        <artifactId>spring-ai-tika-document-reader</artifactId>
        <version>1.0.0</version>
    </dependency>
</dependencies>
```

**Gradle 依赖**:

```gradle
dependencies {
    implementation 'org.springframework.boot:spring-boot-starter'
    implementation 'org.springframework.boot:spring-boot-starter-web'
    implementation 'org.springframework.ai:spring-ai-postgresql-pgvector-store:1.0.0'
    implementation 'org.springframework.boot:spring-boot-starter-data-jpa'
    runtimeOnly 'org.postgresql:postgresql'
    implementation 'org.springframework.ai:spring-ai-openai-spring-boot-starter:1.0.0'
    implementation 'org.springframework.ai:spring-ai-tika-document-reader:1.0.0'
}
```

#### 3.1.2 项目结构

**推荐项目结构**:

```
src/
├── main/
│   ├── java/
│   │   └── com/
│   │       └── example/
│   │           └── ai/
│   │               ├── Application.java
│   │               ├── config/
│   │               │   └── VectorStoreConfig.java
│   │               ├── service/
│   │               │   ├── DocumentService.java
│   │               │   ├── RAGService.java
│   │               │   └── EmbeddingService.java
│   │               ├── controller/
│   │               │   └── RAGController.java
│   │               └── model/
│   │                   ├── ChatRequest.java
│   │                   └── ChatResponse.java
│   └── resources/
│       └── application.yml
```

### 3.2 配置数据库

#### 3.2.1 数据源配置

**application.yml 配置**:

```yaml
spring:
  datasource:
    url: jdbc:postgresql://localhost:5432/ai_demo
    username: postgres
    password: postgres
    driver-class-name: org.postgresql.Driver

    # 连接池配置
    hikari:
      maximum-pool-size: 20
      minimum-idle: 5
      connection-timeout: 30000
      idle-timeout: 600000
      max-lifetime: 1800000

  jpa:
    hibernate:
      ddl-auto: none # 使用 Spring AI 自动建表
    properties:
      hibernate:
        dialect: org.hibernate.dialect.PostgreSQLDialect
        format_sql: true
        show_sql: false # 生产环境关闭
    show-sql: false
```

#### 3.2.2 Spring AI 配置

**Spring AI 配置**:

```yaml
spring:
  ai:
    # 向量存储配置
    vectorstore:
      pgvector:
        # 自动初始化表结构
        initialize-schema: true

        # 索引类型：HNSW 或 IVFFLAT
        index-type: HNSW

        # 距离类型：COSINE_DISTANCE, EUCLIDEAN_DISTANCE, INNER_PRODUCT
        distance-type: COSINE_DISTANCE

        # 向量维度（根据 Embedding 模型调整）
        dimensions: 1536

        # HNSW 索引参数
        hnsw:
          m: 16 # 每层最大连接数
          ef-construction: 64 # 构建时搜索范围

    # OpenAI 配置
    openai:
      api-key: ${OPENAI_API_KEY}
      chat:
        options:
          model: gpt-4-turbo-preview
          temperature: 0.7
          max-tokens: 2000

      embedding:
        options:
          model: text-embedding-3-small
          dimensions: 1536
```

### 3.3 创建向量存储

#### 3.3.1 基础配置

**基础配置示例**:

```java
@Configuration
public class VectorStoreConfig {

    @Bean
    public PgVectorStore vectorStore(
            DataSource dataSource,
            EmbeddingClient embeddingClient
    ) {
        return new PgVectorStore.Builder(dataSource, embeddingClient)
                .withIndexType(PgVectorStore.PgIndexType.HNSW)
                .withDistanceType(PgVectorStore.PgDistanceType.COSINE_DISTANCE)
                .withDimensions(1536)
                .withRemoveExisting(true)  // 开发环境使用
                .build();
    }
}
```

#### 3.3.2 高级配置

**高级配置示例**:

```java
@Configuration
public class VectorStoreConfig {

    @Bean
    @Primary
    public VectorStore vectorStore(
            DataSource dataSource,
            EmbeddingClient embeddingClient
    ) {
        return new PgVectorStore.Builder(dataSource, embeddingClient)
                .withIndexType(PgVectorStore.PgIndexType.HNSW)
                .withDistanceType(PgVectorStore.PgDistanceType.COSINE_DISTANCE)
                .withDimensions(1536)

                // HNSW 参数优化
                .withHnswM(32)              // 提高精度
                .withHnswEfConstruction(200)  // 提高构建质量

                // 表名自定义
                .withTableName("custom_vector_store")

                // 距离函数自定义
                .withDistanceFunction("cosine")

                .build();
    }

    // 大规模数据配置（使用 IVFFlat）
    @Bean
    @Qualifier("largeScaleVectorStore")
    public VectorStore largeScaleVectorStore(
            DataSource dataSource,
            EmbeddingClient embeddingClient
    ) {
        return new PgVectorStore.Builder(dataSource, embeddingClient)
                .withIndexType(PgVectorStore.PgIndexType.IVFFLAT)
                .withDistanceType(PgVectorStore.PgDistanceType.COSINE_DISTANCE)
                .withDimensions(1536)
                .withIvfLists(1000)  // IVFFlat 聚类数
                .build();
    }
}
```

### 3.4 使用向量存储

#### 3.4.1 添加文档

**添加文档示例**:

```java
@Service
public class DocumentService {

    private final VectorStore vectorStore;

    public DocumentService(VectorStore vectorStore) {
        this.vectorStore = vectorStore;
    }

    // 添加单个文档
    public void addDocument(String content, Map<String, Object> metadata) {
        Document document = new Document(content, metadata);
        vectorStore.add(List.of(document));
    }

    // 批量添加文档
    public void addDocuments(List<String> contents,
                             List<Map<String, Object>> metadataList) {
        List<Document> documents = new ArrayList<>();
        for (int i = 0; i < contents.size(); i++) {
            Map<String, Object> metadata = metadataList.get(i);
            Document doc = new Document(contents.get(i), metadata);
            documents.add(doc);
        }
        vectorStore.add(documents);
    }

    // 从文件添加文档
    public void addDocumentFromFile(String filePath) {
        Resource resource = new FileSystemResource(filePath);
        TikaDocumentReader reader = new TikaDocumentReader();
        Document doc = reader.read(resource);

        // 添加文件元数据
        Map<String, Object> metadata = new HashMap<>();
        metadata.put("source", filePath);
        metadata.put("type", "FILE");
        metadata.put("timestamp", System.currentTimeMillis());
        doc.getMetadata().putAll(metadata);

        vectorStore.add(List.of(doc));
    }
}
```

#### 3.4.2 相似度搜索

**相似度搜索示例**:

```java
@Service
public class DocumentService {

    private final VectorStore vectorStore;

    // 基础相似度搜索
    public List<Document> search(String query, int topK) {
        return vectorStore.similaritySearch(
            SearchRequest.builder()
                .query(query)
                .topK(topK)
                .build()
        );
    }

    // 带相似度阈值的搜索
    public List<Document> searchWithThreshold(String query,
                                             int topK,
                                             double threshold) {
        return vectorStore.similaritySearch(
            SearchRequest.builder()
                .query(query)
                .topK(topK)
                .similarityThreshold(threshold)
                .build()
        );
    }

    // 带元数据过滤的搜索
    public List<Document> searchWithFilter(String query,
                                          int topK,
                                          Map<String, Object> metadataFilter) {
        return vectorStore.similaritySearch(
            SearchRequest.builder()
                .query(query)
                .topK(topK)
                .filter(metadataFilter)
                .build()
        );
    }
}
```

#### 3.4.3 元数据过滤

**元数据过滤示例**:

```java
@Service
public class DocumentService {

    // 按类别过滤
    public List<Document> searchByCategory(String query,
                                         String category,
                                         int topK) {
        Map<String, Object> filter = new HashMap<>();
        filter.put("category", category);

        return vectorStore.similaritySearch(
            SearchRequest.builder()
                .query(query)
                .topK(topK)
                .filter(filter)
                .build()
        );
    }

    // 按日期范围过滤
    public List<Document> searchByDateRange(String query,
                                           LocalDate startDate,
                                           LocalDate endDate,
                                           int topK) {
        Map<String, Object> filter = new HashMap<>();
        filter.put("date >= ", startDate.toString());
        filter.put("date <= ", endDate.toString());

        return vectorStore.similaritySearch(
            SearchRequest.builder()
                .query(query)
                .topK(topK)
                .filter(filter)
                .build()
        );
    }

    // 组合过滤条件
    public List<Document> searchWithMultipleFilters(String query,
                                                   Map<String, Object> filters,
                                                   int topK) {
        return vectorStore.similaritySearch(
            SearchRequest.builder()
                .query(query)
                .topK(topK)
                .filter(filters)
                .build()
        );
    }
}
```

## 4. RAG 应用开发

### 4.1 RAG 服务实现

#### 4.1.1 基础 RAG

**基础 RAG 实现**:

```java
@Service
public class RAGService {

    private final VectorStore vectorStore;
    private final ChatClient chatClient;

    public RAGService(VectorStore vectorStore, ChatClient chatClient) {
        this.vectorStore = vectorStore;
        this.chatClient = chatClient;
    }

    public String chat(String userMessage) {
        // 1. 向量搜索相关文档
        List<Document> relevantDocs = vectorStore.similaritySearch(
            SearchRequest.builder()
                .query(userMessage)
                .topK(5)
                .build()
        );

        // 2. 构建上下文
        String context = relevantDocs.stream()
            .map(Document::getContent)
            .collect(Collectors.joining("\n\n"));

        // 3. 构建提示词
        String prompt = String.format(
            "基于以下上下文回答问题：\n\n%s\n\n问题：%s\n\n答案：",
            context,
            userMessage
        );

        // 4. 调用 LLM
        return chatClient.call(prompt);
    }
}
```

#### 4.1.2 高级 RAG

**高级 RAG 实现（带对话历史）**:

```java
@Service
public class AdvancedRAGService {

    private final VectorStore vectorStore;
    private final ChatClient chatClient;
    private final Map<String, List<Message>> conversationHistory = new ConcurrentHashMap<>();

    public String chat(String sessionId, String userMessage) {
        // 1. 获取对话历史
        List<Message> history = conversationHistory.getOrDefault(sessionId, new ArrayList<>());

        // 2. 向量搜索相关文档
        List<Document> relevantDocs = vectorStore.similaritySearch(
            SearchRequest.builder()
                .query(userMessage)
                .topK(5)
                .similarityThreshold(0.7)
                .build()
        );

        // 3. 构建上下文
        String context = relevantDocs.stream()
            .map(doc -> String.format("【文档 %d】\n%s",
                doc.getMetadata().get("id"),
                doc.getContent()))
            .collect(Collectors.joining("\n\n"));

        // 4. 构建提示词
        StringBuilder promptBuilder = new StringBuilder();
        promptBuilder.append("基于以下上下文回答问题，如果上下文中没有相关信息，请说明：\n\n");
        promptBuilder.append(context);
        promptBuilder.append("\n\n");

        // 添加对话历史
        if (!history.isEmpty()) {
            promptBuilder.append("之前的对话：\n");
            history.forEach(msg -> {
                promptBuilder.append(msg.getContent());
                promptBuilder.append("\n");
            });
            promptBuilder.append("\n");
        }

        promptBuilder.append("当前问题：").append(userMessage).append("\n\n答案：");

        // 5. 调用 LLM
        String response = chatClient.call(promptBuilder.toString());

        // 6. 保存对话历史
        history.add(new Message("user", userMessage));
        history.add(new Message("assistant", response));

        // 限制历史长度
        if (history.size() > 20) {
            history.remove(0);
            history.remove(0);
        }

        conversationHistory.put(sessionId, history);

        return response;
    }
}
```

### 4.2 REST API 开发

#### 4.2.1 控制器实现

**REST Controller 示例**:

```java
@RestController
@RequestMapping("/api/rag")
public class RAGController {

    private final RAGService ragService;

    @Autowired
    public RAGController(RAGService ragService) {
        this.ragService = ragService;
    }

    @PostMapping("/chat")
    public ResponseEntity<ChatResponse> chat(@RequestBody ChatRequest request) {
        String response = ragService.chat(request.getMessage());
        return ResponseEntity.ok(new ChatResponse(response));
    }

    @PostMapping("/chat/stream")
    public ResponseEntity<StreamingResponseBody> chatStream(@RequestBody ChatRequest request) {
        StreamingResponseBody stream = outputStream -> {
            // 流式响应实现
            ragService.chatStream(request.getMessage(), outputStream);
        };

        return ResponseEntity.ok()
            .contentType(MediaType.TEXT_PLAIN)
            .body(stream);
    }

    @PostMapping("/documents")
    public ResponseEntity<String> addDocument(@RequestBody DocumentRequest request) {
        ragService.addDocument(request.getContent(), request.getMetadata());
        return ResponseEntity.ok("Document added successfully");
    }

    @GetMapping("/search")
    public ResponseEntity<List<DocumentResponse>> search(
            @RequestParam String query,
            @RequestParam(defaultValue = "5") int topK) {
        List<Document> docs = ragService.search(query, topK);
        List<DocumentResponse> responses = docs.stream()
            .map(DocumentResponse::fromDocument)
            .collect(Collectors.toList());
        return ResponseEntity.ok(responses);
    }
}
```

#### 4.2.2 请求响应模型

**请求响应模型**:

```java
// ChatRequest.java
public class ChatRequest {
    private String message;
    private String sessionId;
    private Map<String, Object> metadata;

    // Getters and Setters
}

// ChatResponse.java
public class ChatResponse {
    private String answer;
    private List<DocumentReference> sources;
    private long timestamp;

    // Getters and Setters
}

// DocumentRequest.java
public class DocumentRequest {
    private String content;
    private Map<String, Object> metadata;

    // Getters and Setters
}

// DocumentResponse.java
public class DocumentResponse {
    private String id;
    private String content;
    private Map<String, Object> metadata;
    private double similarity;

    public static DocumentResponse fromDocument(Document doc) {
        DocumentResponse response = new DocumentResponse();
        response.setId((String) doc.getMetadata().get("id"));
        response.setContent(doc.getContent());
        response.setMetadata(doc.getMetadata());
        response.setSimilarity((Double) doc.getMetadata().getOrDefault("score", 0.0));
        return response;
    }
}
```

### 4.3 流式响应

#### 4.3.1 流式聊天

**流式聊天实现**:

```java
@Service
public class StreamingRAGService {

    private final VectorStore vectorStore;
    private final ChatClient chatClient;

    public void chatStream(String userMessage, OutputStream outputStream) {
        try {
            // 1. 向量搜索
            List<Document> relevantDocs = vectorStore.similaritySearch(
                SearchRequest.builder()
                    .query(userMessage)
                    .topK(5)
                    .build()
            );

            // 2. 构建上下文
            String context = relevantDocs.stream()
                .map(Document::getContent)
                .collect(Collectors.joining("\n\n"));

            // 3. 构建提示词
            String prompt = String.format(
                "基于以下上下文回答问题：\n\n%s\n\n问题：%s\n\n答案：",
                context,
                userMessage
            );

            // 4. 流式调用 LLM
            chatClient.stream(prompt)
                .doOnNext(chunk -> {
                    try {
                        outputStream.write(chunk.getResult().getOutput().getContent().getBytes());
                        outputStream.flush();
                    } catch (IOException e) {
                        throw new RuntimeException(e);
                    }
                })
                .blockLast();

            outputStream.close();
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }
}
```

#### 4.3.2 Server-Sent Events

**Server-Sent Events 实现**:

```java
@RestController
@RequestMapping("/api/rag")
public class StreamingRAGController {

    private final RAGService ragService;
    private final VectorStore vectorStore;
    private final ChatClient chatClient;

    @GetMapping(value = "/chat/stream", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public Flux<ServerSentEvent<String>> chatStream(@RequestParam String message) {
        // 1. 向量搜索
        List<Document> relevantDocs = vectorStore.similaritySearch(
            SearchRequest.builder()
                .query(message)
                .topK(5)
                .build()
        );

        // 2. 构建上下文
        String context = relevantDocs.stream()
            .map(Document::getContent)
            .collect(Collectors.joining("\n\n"));

        // 3. 构建提示词
        String prompt = String.format(
            "基于以下上下文回答问题：\n\n%s\n\n问题：%s\n\n答案：",
            context,
            message
        );

        // 4. 流式返回
        return chatClient.stream(prompt)
            .map(chunk -> ServerSentEvent.<String>builder()
                .data(chunk.getResult().getOutput().getContent())
                .build());
    }
}
```

## 5. 高级特性

### 5.1 混合搜索

#### 5.1.1 向量 + 全文搜索

**混合搜索实现**:

```java
@Service
public class HybridSearchService {

    private final VectorStore vectorStore;
    private final JdbcTemplate jdbcTemplate;

    public List<Document> hybridSearch(String query, int topK) {
        // 1. 向量搜索
        List<Document> vectorResults = vectorStore.similaritySearch(
            SearchRequest.builder()
                .query(query)
                .topK(topK * 2)
                .build()
        );

        // 2. 全文搜索（PostgreSQL tsvector）
        List<Document> textResults = jdbcTemplate.query(
            "SELECT id, content, metadata " +
            "FROM vector_store " +
            "WHERE to_tsvector('english', content) @@ to_tsquery('english', ?) " +
            "ORDER BY ts_rank(to_tsvector('english', content), to_tsquery('english', ?)) DESC " +
            "LIMIT ?",
            (rs, rowNum) -> {
                Document doc = new Document(
                    rs.getString("content"),
                    parseMetadata(rs.getString("metadata"))
                );
                doc.getMetadata().put("id", rs.getString("id"));
                doc.getMetadata().put("score", 1.0);  // 全文搜索分数
                return doc;
            },
            query, query, topK * 2
        );

        // 3. 融合结果（RRF 算法）
        return fuseResults(vectorResults, textResults, topK);
    }

    private List<Document> fuseResults(List<Document> vectorResults,
                                      List<Document> textResults,
                                      int topK) {
        Map<String, Document> docMap = new HashMap<>();
        Map<String, Double> scores = new HashMap<>();

        // 合并向量搜索结果
        for (int i = 0; i < vectorResults.size(); i++) {
            Document doc = vectorResults.get(i);
            String id = (String) doc.getMetadata().get("id");
            if (id == null) id = doc.getContent().substring(0, Math.min(50, doc.getContent().length()));

            docMap.put(id, doc);
            // RRF 分数：1 / (k + rank)
            scores.put(id, 1.0 / (60 + i + 1));
        }

        // 合并全文搜索结果
        for (int i = 0; i < textResults.size(); i++) {
            Document doc = textResults.get(i);
            String id = (String) doc.getMetadata().get("id");
            if (id == null) id = doc.getContent().substring(0, Math.min(50, doc.getContent().length()));

            docMap.putIfAbsent(id, doc);
            // RRF 分数：1 / (k + rank)
            scores.put(id, scores.getOrDefault(id, 0.0) + 1.0 / (60 + i + 1));
        }

        // 按分数排序
        return docMap.values().stream()
            .sorted((a, b) -> {
                String idA = (String) a.getMetadata().get("id");
                String idB = (String) b.getMetadata().get("id");
                return Double.compare(scores.getOrDefault(idB, 0.0),
                                    scores.getOrDefault(idA, 0.0));
            })
            .limit(topK)
            .collect(Collectors.toList());
    }
}
```

#### 5.1.2 RRF 算法融合

**RRF 算法实现**:

```java
@Service
public class RRFService {

    private final VectorStore vectorStore;

    public List<Document> rrfFusion(String query, int topK) {
        // 1. 向量搜索（多个配置）
        List<Document> vectorResults1 = vectorStore.similaritySearch(
            SearchRequest.builder()
                .query(query)
                .topK(topK)
                .similarityThreshold(0.7)
                .build()
        );

        List<Document> vectorResults2 = vectorStore.similaritySearch(
            SearchRequest.builder()
                .query(query)
                .topK(topK)
                .similarityThreshold(0.5)
                .build()
        );

        // 2. RRF 融合（k = 60）
        int k = 60;
        Map<String, Double> rrfScores = new HashMap<>();
        Map<String, Document> docMap = new HashMap<>();

        // 处理向量结果 1
        for (int i = 0; i < vectorResults1.size(); i++) {
            Document doc = vectorResults1.get(i);
            String id = getDocumentId(doc);
            double score = 1.0 / (k + i + 1);
            rrfScores.put(id, rrfScores.getOrDefault(id, 0.0) + score);
            docMap.putIfAbsent(id, doc);
        }

        // 处理向量结果 2
        for (int i = 0; i < vectorResults2.size(); i++) {
            Document doc = vectorResults2.get(i);
            String id = getDocumentId(doc);
            double score = 1.0 / (k + i + 1);
            rrfScores.put(id, rrfScores.getOrDefault(id, 0.0) + score);
            docMap.putIfAbsent(id, doc);
        }

        // 3. 按 RRF 分数排序
        return docMap.values().stream()
            .sorted((a, b) -> {
                String idA = getDocumentId(a);
                String idB = getDocumentId(b);
                return Double.compare(rrfScores.getOrDefault(idB, 0.0),
                                    rrfScores.getOrDefault(idA, 0.0));
            })
            .limit(topK)
            .collect(Collectors.toList());
    }

    private String getDocumentId(Document doc) {
        String id = (String) doc.getMetadata().get("id");
        if (id == null) {
            id = doc.getContent().substring(0, Math.min(50, doc.getContent().length()));
        }
        return id;
    }
}
```

### 5.2 批量操作

#### 5.2.1 批量添加文档

**批量添加优化**:

```java
@Service
public class BatchDocumentService {

    private final VectorStore vectorStore;

    // 分批添加（避免内存溢出）
    public void addDocumentsInBatches(List<Document> documents, int batchSize) {
        for (int i = 0; i < documents.size(); i += batchSize) {
            int end = Math.min(i + batchSize, documents.size());
            List<Document> batch = documents.subList(i, end);
            vectorStore.add(batch);

            // 添加进度日志
            System.out.printf("已添加 %d/%d 个文档\n", end, documents.size());
        }
    }

    // 异步批量添加
    @Async
    public CompletableFuture<Void> addDocumentsAsync(List<Document> documents) {
        return CompletableFuture.runAsync(() -> {
            addDocumentsInBatches(documents, 100);
        });
    }
}
```

#### 5.2.2 批量删除文档

**批量删除实现**:

```java
@Service
public class DocumentManagementService {

    private final JdbcTemplate jdbcTemplate;

    // 按 ID 批量删除
    public void deleteDocumentsByIds(List<String> ids) {
        String sql = "DELETE FROM vector_store WHERE id = ANY(?)";
        jdbcTemplate.update(sql, ids.toArray(new String[0]));
    }

    // 按元数据过滤删除
    public void deleteDocumentsByMetadata(Map<String, Object> metadataFilter) {
        StringBuilder sql = new StringBuilder("DELETE FROM vector_store WHERE ");
        List<Object> params = new ArrayList<>();

        int index = 0;
        for (Map.Entry<String, Object> entry : metadataFilter.entrySet()) {
            if (index > 0) {
                sql.append(" AND ");
            }
            sql.append("metadata->>? = ?");
            params.add(entry.getKey());
            params.add(entry.getValue().toString());
            index++;
        }

        jdbcTemplate.update(sql.toString(), params.toArray());
    }
}
```

### 5.3 性能优化

#### 5.3.1 索引优化

**索引优化配置**:

```java
@Configuration
public class OptimizedVectorStoreConfig {

    @Bean
    public PgVectorStore optimizedVectorStore(
            DataSource dataSource,
            EmbeddingClient embeddingClient
    ) {
        return new PgVectorStore.Builder(dataSource, embeddingClient)
                .withIndexType(PgVectorStore.PgIndexType.HNSW)
                .withDistanceType(PgVectorStore.PgDistanceType.COSINE_DISTANCE)
                .withDimensions(1536)

                // 优化 HNSW 参数（高精度场景）
                .withHnswM(32)                  // 提高 m（默认 16）
                .withHnswEfConstruction(200)    // 提高 ef_construction（默认 64）

                .build();
    }
}
```

**索引性能对比**:

| 索引类型        | 构建时间 | 查询延迟  | 召回率    | 内存占用 |
| --------------- | -------- | --------- | --------- | -------- |
| **HNSW (m=16)** | 快       | **<10ms** | **98%**   | 高       |
| **HNSW (m=32)** | 中       | **<15ms** | **99.5%** | 很高     |
| **IVFFlat**     | 很快     | **<20ms** | **95%**   | 低       |

#### 5.3.2 查询优化

**查询优化技巧**:

```java
@Service
public class OptimizedSearchService {

    private final VectorStore vectorStore;

    // 1. 使用相似度阈值过滤低质量结果
    public List<Document> searchWithThreshold(String query, double threshold) {
        return vectorStore.similaritySearch(
            SearchRequest.builder()
                .query(query)
                .topK(100)  // 多取一些
                .similarityThreshold(threshold)  // 过滤低质量结果
                .build()
        );
    }

    // 2. 使用元数据过滤减少搜索范围
    public List<Document> searchWithMetadataFilter(String query,
                                                   Map<String, Object> filter) {
        return vectorStore.similaritySearch(
            SearchRequest.builder()
                .query(query)
                .topK(10)
                .filter(filter)  // 提前过滤
                .build()
        );
    }

    // 3. 批量查询优化
    public Map<String, List<Document>> batchSearch(List<String> queries, int topK) {
        Map<String, List<Document>> results = new HashMap<>();

        // 并行查询
        queries.parallelStream().forEach(query -> {
            List<Document> docs = vectorStore.similaritySearch(
                SearchRequest.builder()
                    .query(query)
                    .topK(topK)
                    .build()
            );
            results.put(query, docs);
        });

        return results;
    }
}
```

## 6. 最佳实践

### 6.1 配置最佳实践

**配置建议**:

1. **索引选择**:

   - **<100 万数据**: 使用 HNSW (m=16)
   - **>100 万数据**: 使用 IVFFlat

2. **向量维度**:

   - OpenAI text-embedding-3-small: **1536**
   - OpenAI text-embedding-3-large: **3072**

3. **连接池配置**:
   ```yaml
   spring:
     datasource:
       hikari:
         maximum-pool-size: 20
         minimum-idle: 5
   ```

### 6.2 性能最佳实践

**性能优化建议**:

1. **批量操作**: 使用批量添加而不是逐个添加
2. **索引优化**: 根据数据量选择合适的索引类型和参数
3. **查询优化**: 使用相似度阈值和元数据过滤
4. **异步处理**: 对于大量文档，使用异步处理

### 6.3 安全最佳实践

**安全建议**:

1. **API Key 管理**: 使用环境变量或密钥管理服务
2. **输入验证**: 验证用户输入，防止注入攻击
3. **访问控制**: 实施适当的访问控制机制
4. **日志记录**: 记录敏感操作的日志

## 7. 常见问题

### 7.1 依赖问题

**常见依赖问题**:

1. **版本冲突**:

   ```xml
   <!-- 确保使用兼容的版本 -->
   <spring-boot.version>3.2.0</spring-boot.version>
   <spring-ai.version>1.0.0</spring-ai.version>
   ```

2. **缺少依赖**:
   ```xml
   <!-- 确保添加了所有必需的依赖 -->
   <dependency>
       <groupId>org.springframework.ai</groupId>
       <artifactId>spring-ai-postgresql-pgvector-store</artifactId>
   </dependency>
   ```

### 7.2 配置问题

**常见配置问题**:

1. **维度不匹配**: 确保 `dimensions` 配置与 Embedding 模型维度一致
2. **索引类型错误**: 确保索引类型与数据量匹配
3. **连接字符串错误**: 检查数据库连接配置

### 7.3 性能问题

**性能问题排查**:

1. **查询慢**: 检查索引是否创建，优化查询参数
2. **内存不足**: 使用批量操作，减少批次大小
3. **连接池耗尽**: 增加连接池大小或使用连接池

## 8. 参考资料

### 8.1 官方文档

- [Spring AI 官方文档](https://docs.spring.io/spring-ai/reference/) - Spring AI Reference
- [PGVector Store 文档](https://docs.spring.io/spring-ai/reference/api/vectordb/pgvector.html) -
  PGVector Store API

### 8.2 技术文档

- [pgvector 核心原理](../../01-向量与混合搜索/技术原理/pgvector核心原理.md) - pgvector Core
  Principles
- [混合搜索 RRF 算法](../../01-向量与混合搜索/技术原理/混合搜索RRF算法.md) - RRF Algorithm

### 8.3 相关资源

- [Spring Boot 官方文档](https://docs.spring.io/spring-boot/reference/) - Spring Boot Reference
- [PostgreSQL 官方文档](https://www.postgresql.org/docs/) - PostgreSQL Documentation

---

**最后更新**: 2025 年 11 月 1 日  
**维护者**: PostgreSQL Modern Team  
**文档编号**: 07-01-01
