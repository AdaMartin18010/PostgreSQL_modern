# JPA/Hibernate 集成 PostgreSQL 向量搜索

> **更新时间**: 2025 年 11 月 1 日
> **技术版本**: PostgreSQL 14+, pgvector 0.7.0+, Hibernate 6.0+
> **文档编号**: 07-03-02

## 📑 目录

- [JPA/Hibernate 集成 PostgreSQL 向量搜索](#jpahibernate-集成-postgresql-向量搜索)
  - [📑 目录](#-目录)
  - [1. 概述](#1-概述)
    - [1.1 集成优势](#11-集成优势)
    - [1.2 技术栈](#12-技术栈)
  - [2. 依赖配置](#2-依赖配置)
    - [2.1 Maven 配置](#21-maven-配置)
    - [2.2 Gradle 配置](#22-gradle-配置)
    - [2.3 数据库配置](#23-数据库配置)
  - [3. 实体映射](#3-实体映射)
    - [3.1 向量类型映射](#31-向量类型映射)
    - [3.2 Repository 接口](#32-repository-接口)
  - [4. 查询实现](#4-查询实现)
    - [4.1 向量搜索服务](#41-向量搜索服务)
    - [4.2 自定义查询方法](#42-自定义查询方法)
  - [5. 实践案例](#5-实践案例)
    - [5.1 完整的 RAG 应用](#51-完整的-rag-应用)
  - [6. 参考资料](#6-参考资料)

---

## 1. 概述

### 1.1 集成优势

- **ORM 支持**: 使用 JPA/Hibernate 管理实体
- **类型安全**: 类型安全的查询
- **事务管理**: 自动事务管理
- **缓存支持**: 二级缓存支持

### 1.2 技术栈

- **Spring Boot**: 2.7+ 或 3.0+
- **Hibernate**: 6.0+
- **PostgreSQL Driver**: 42.5+
- **pgvector**: 通过自定义类型支持

## 2. 依赖配置

### 2.1 Maven 配置

```xml
<dependencies>
    <!-- Spring Boot Starter -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-data-jpa</artifactId>
    </dependency>

    <!-- PostgreSQL Driver -->
    <dependency>
        <groupId>org.postgresql</groupId>
        <artifactId>postgresql</artifactId>
    </dependency>

    <!-- pgvector-java (向量类型支持) -->
    <dependency>
        <groupId>com.pgvector</groupId>
        <artifactId>pgvector</artifactId>
        <version>0.1.4</version>
    </dependency>
</dependencies>
```

### 2.2 Gradle 配置

```gradle
dependencies {
    implementation 'org.springframework.boot:spring-boot-starter-data-jpa'
    implementation 'org.postgresql:postgresql'
    implementation 'com.pgvector:pgvector:0.1.4'
}
```

### 2.3 数据库配置

```yaml
# application.yml
spring:
  datasource:
    url: jdbc:postgresql://localhost:5432/vectordb
    username: postgres
    password: password
    driver-class-name: org.postgresql.Driver

  jpa:
    database-platform: org.hibernate.dialect.PostgreSQLDialect
    hibernate:
      ddl-auto: update
    properties:
      hibernate:
        dialect: org.hibernate.dialect.PostgreSQLDialect
```

## 3. 实体映射

### 3.1 向量类型映射

```java
// Vector 类型包装类
package com.example.model;

import com.pgvector.PGvector;
import jakarta.persistence.AttributeConverter;
import jakarta.persistence.Converter;

@Converter
public class VectorConverter implements AttributeConverter<double[], PGvector> {
    @Override
    public PGvector convertToDatabaseColumn(double[] attribute) {
        if (attribute == null) {
            return null;
        }
        return new PGvector(attribute);
    }

    @Override
    public double[] convertToEntityAttribute(PGvector dbData) {
        if (dbData == null) {
            return null;
        }
        return dbData.toArray();
    }
}

// 实体类
package com.example.model;

import jakarta.persistence.*;
import lombok.Data;

@Entity
@Table(name = "documents")
@Data
public class Document {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "content")
    private String content;

    @Column(name = "embedding", columnDefinition = "vector(1536)")
    @Convert(converter = VectorConverter.class)
    private double[] embedding;

    @Column(name = "metadata", columnDefinition = "jsonb")
    private String metadata;
}
```

### 3.2 Repository 接口

```java
package com.example.repository;

import com.example.model.Document;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface DocumentRepository extends JpaRepository<Document, Long> {

    @Query(value = """
        SELECT * FROM documents
        ORDER BY embedding <=> CAST(:queryVector AS vector)
        LIMIT :limit
        """, nativeQuery = true)
    List<Document> findSimilar(
        @Param("queryVector") String queryVector,
        @Param("limit") int limit
    );
}
```

## 4. 查询实现

### 4.1 向量搜索服务

```java
package com.example.service;

import com.example.model.Document;
import com.example.repository.DocumentRepository;
import com.pgvector.PGvector;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class VectorSearchService {

    @Autowired
    private DocumentRepository documentRepository;

    public List<Document> search(double[] queryVector, int limit) {
        // 转换为 PostgreSQL 向量格式
        PGvector pgVector = new PGvector(queryVector);
        String vectorString = pgVector.toString();

        return documentRepository.findSimilar(vectorString, limit);
    }
}
```

### 4.2 自定义查询方法

```java
// Repository 中添加自定义方法
@Query(value = """
    SELECT id, content, metadata,
           1 - (embedding <=> CAST(:queryVector AS vector)) AS similarity
    FROM documents
    WHERE 1 - (embedding <=> CAST(:queryVector AS vector)) > :threshold
    ORDER BY embedding <=> CAST(:queryVector AS vector)
    LIMIT :limit
    """, nativeQuery = true)
List<Object[]> findSimilarWithThreshold(
    @Param("queryVector") String queryVector,
    @Param("threshold") double threshold,
    @Param("limit") int limit
);
```

## 5. 实践案例

### 5.1 完整的 RAG 应用

```java
// Controller
package com.example.controller;

import com.example.model.Document;
import com.example.service.VectorSearchService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/search")
public class SearchController {

    @Autowired
    private VectorSearchService vectorSearchService;

    @PostMapping("/vector")
    public List<Document> vectorSearch(
        @RequestBody double[] queryVector,
        @RequestParam(defaultValue = "10") int limit
    ) {
        return vectorSearchService.search(queryVector, limit);
    }
}

// Service
package com.example.service;

import com.example.model.Document;
import com.example.repository.DocumentRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@Transactional
public class DocumentService {

    @Autowired
    private DocumentRepository documentRepository;

    public Document save(Document document) {
        return documentRepository.save(document);
    }

    public List<Document> findAll() {
        return documentRepository.findAll();
    }
}
```

## 6. 参考资料

- [Spring Data JPA 文档](https://spring.io/projects/spring-data-jpa)
- [Hibernate 文档](https://hibernate.org/orm/documentation/)
- [pgvector-java](https://github.com/pgvector/pgvector-java)

---

**最后更新**: 2025 年 11 月 1 日
**维护者**: PostgreSQL Modern Team
**文档编号**: 07-03-02
