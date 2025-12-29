---

> **📋 文档来源**: `PostgreSQL培训\07-安全\【深入】PostgreSQL安全深化-RLS与审计完整指南.md`
> **📅 复制日期**: 2025-12-22
> **⚠️ 注意**: 本文档为复制版本，原文件保持不变

---

# 【深入】PostgreSQL安全深化 - RLS与审计完整指南

> **创建时间**: 2025年1月
> **技术版本**: PostgreSQL 17+/18+
> **难度等级**: ⭐⭐⭐⭐ 高级
> **预计学习时间**: 1-2周

---

## 📑 目录

- [1.1 RLS基础概念](#11-rls基础概念)
- [1.2 RLS快速开始（15分钟）](#12-rls快速开始15分钟)
- [1.3 RLS策略类型](#13-rls策略类型)
- [1.4 RLS性能优化](#14-rls性能优化)
- [1.5 多租户RLS完整方案](#15-多租户rls完整方案)
- [2.1 使用pgAudit扩展](#21-使用pgaudit扩展)
- [2.2 自定义审计触发器](#22-自定义审计触发器)
- [2.3 审计日志查询和分析](#23-审计日志查询和分析)
- [2.4 不可篡改审计日志](#24-不可篡改审计日志)
- [3.1 静态脱敏（数据导出时）](#31-静态脱敏数据导出时)
- [3.2 动态脱敏（anon扩展）](#32-动态脱敏anon扩展)
- [3.3 差分隐私](#33-差分隐私)
- [4.1 SSL/TLS加密](#41-ssltls加密)
- [4.2 数据加密（pgcrypto）](#42-数据加密pgcrypto)
- [4.3 密钥轮换](#43-密钥轮换)
- [5.1 SQL注入测试](#51-sql注入测试)
- [5.2 权限提升测试](#52-权限提升测试)
- [5.3 DoS攻击测试](#53-dos攻击测试)
- [6.1 GDPR合规](#61-gdpr合规)
- [6.2 数据保留策略](#62-数据保留策略)
- [7.1 案例：多租户SaaS安全方案](#71-案例多租户saas安全方案)
- [7.2 案例：金融系统审计方案](#72-案例金融系统审计方案)
- [日常安全检查](#日常安全检查)
- [官方文档](#官方文档)
- [最佳实践](#最佳实践)
- [合规框架](#合规框架)
- [开源工具和扩展](#开源工具和扩展)
- [社区资源](#社区资源)
- [书籍推荐](#书籍推荐)
- [视频教程](#视频教程)
- [研究论文](#研究论文)
- [工具和脚本](#工具和脚本)
- [参考资源使用建议](#参考资源使用建议)
---

## 1. 行级安全（RLS）完整指南

### 1.1 RLS基础概念

**什么是RLS**：

行级安全（Row Level Security）允许在表级别定义安全策略，控制用户只能看到和修改特定的行。

**适用场景**：

- 多租户SaaS应用
- 基于角色的数据访问控制
- 数据隔离和权限管理
- 符合GDPR等法规要求

### 1.2 RLS快速开始（15分钟）

```sql
-- 1. 创建示例表（带错误处理）
DO $$
BEGIN
    BEGIN
        IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'documents') THEN
            RAISE NOTICE '表 documents 已存在';
        ELSE
            CREATE TABLE documents (
                id serial PRIMARY KEY,
                title text NOT NULL,
                content text,
                owner_id int NOT NULL,
                department text,
                classification text CHECK (classification IN ('public', 'internal', 'confidential', 'secret')),
                created_at timestamptz DEFAULT now()
            );
            RAISE NOTICE '表 documents 创建成功';
        END IF;
    EXCEPTION
        WHEN duplicate_table THEN
            RAISE WARNING '表 documents 已存在';
        WHEN OTHERS THEN
            RAISE WARNING '创建表失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 2. 插入测试数据（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'documents') THEN
            RAISE WARNING '表 documents 不存在，无法插入测试数据';
            RETURN;
        END IF;

        BEGIN
            INSERT INTO documents (title, content, owner_id, department, classification) VALUES
                ('Public Doc', 'Everyone can see', 1, 'marketing', 'public'),
                ('Team Doc', 'Team only', 2, 'engineering', 'internal'),
                ('Manager Doc', 'Managers only', 3, 'hr', 'confidential'),
                ('CEO Doc', 'CEO only', 4, 'executive', 'secret');
            RAISE NOTICE '测试数据插入成功';
        EXCEPTION
            WHEN unique_violation THEN
                RAISE WARNING '测试数据已存在，跳过插入';
            WHEN check_violation THEN
                RAISE WARNING '分类值不符合约束';
            WHEN OTHERS THEN
                RAISE WARNING '插入测试数据失败: %', SQLERRM;
                RAISE;
        END;
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '操作失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 3. 启用RLS（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'documents') THEN
            RAISE WARNING '表 documents 不存在，无法启用RLS';
            RETURN;
        END IF;

        ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
        RAISE NOTICE 'RLS已启用';
    EXCEPTION
        WHEN undefined_table THEN
            RAISE WARNING '表 documents 不存在';
        WHEN OTHERS THEN
            RAISE WARNING '启用RLS失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 4. 创建策略：用户只能看到自己的文档（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'documents') THEN
            RAISE WARNING '表 documents 不存在，无法创建策略';
            RETURN;
        END IF;

        IF EXISTS (SELECT 1 FROM pg_policies WHERE schemaname = 'public' AND tablename = 'documents' AND policyname = 'documents_owner_policy') THEN
            RAISE NOTICE '策略 documents_owner_policy 已存在';
        ELSE
            CREATE POLICY documents_owner_policy
                ON documents
                FOR SELECT
                USING (owner_id = current_setting('app.current_user_id')::int);
            RAISE NOTICE '策略 documents_owner_policy 创建成功';
        END IF;
    EXCEPTION
        WHEN duplicate_object THEN
            RAISE WARNING '策略 documents_owner_policy 已存在';
        WHEN syntax_error THEN
            RAISE WARNING '策略语法错误，请检查current_setting函数';
        WHEN OTHERS THEN
            RAISE WARNING '创建策略失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 5. 测试（带错误处理和性能测试）
-- 设置当前用户ID
DO $$
BEGIN
    BEGIN
        SET app.current_user_id = '1';
        RAISE NOTICE '当前用户ID设置为 1';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '设置用户ID失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 查询（只能看到owner_id=1的文档，带性能测试）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'documents') THEN
            RAISE WARNING '表 documents 不存在，无法执行查询';
            RETURN;
        END IF;
        RAISE NOTICE '开始查询文档（用户ID=1）';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '查询准备失败: %', SQLERRM;
            RAISE;
    END;
END $$;

EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM documents;
-- 结果：只返回 'Public Doc'

-- 切换用户
DO $$
BEGIN
    BEGIN
        SET app.current_user_id = '2';
        RAISE NOTICE '当前用户ID设置为 2';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '设置用户ID失败: %', SQLERRM;
            RAISE;
    END;
END $$;

EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM documents;
-- 结果：只返回 'Team Doc'
```

### 1.3 RLS策略类型

#### 1.3.1 SELECT策略（查询控制）

```sql
-- 策略1：用户只能看到自己的数据（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'documents') THEN
            RAISE WARNING '表 documents 不存在，无法创建策略';
            RETURN;
        END IF;

        IF EXISTS (SELECT 1 FROM pg_policies WHERE schemaname = 'public' AND tablename = 'documents' AND policyname = 'user_own_data') THEN
            RAISE NOTICE '策略 user_own_data 已存在';
        ELSE
            CREATE POLICY user_own_data
                ON documents
                FOR SELECT
                USING (owner_id = current_user_id());
            RAISE NOTICE '策略 user_own_data 创建成功';
        END IF;
    EXCEPTION
        WHEN duplicate_object THEN
            RAISE WARNING '策略 user_own_data 已存在';
        WHEN syntax_error THEN
            RAISE WARNING '策略语法错误，请检查current_user_id()函数是否存在';
        WHEN OTHERS THEN
            RAISE WARNING '创建策略失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 策略2：用户可以看到自己部门的数据（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'documents') THEN
            RAISE WARNING '表 documents 不存在，无法创建策略';
            RETURN;
        END IF;

        IF EXISTS (SELECT 1 FROM pg_policies WHERE schemaname = 'public' AND tablename = 'documents' AND policyname = 'department_data') THEN
            RAISE NOTICE '策略 department_data 已存在';
        ELSE
            CREATE POLICY department_data
                ON documents
                FOR SELECT
                USING (department = current_user_department());
            RAISE NOTICE '策略 department_data 创建成功';
        END IF;
    EXCEPTION
        WHEN duplicate_object THEN
            RAISE WARNING '策略 department_data 已存在';
        WHEN syntax_error THEN
            RAISE WARNING '策略语法错误，请检查current_user_department()函数是否存在';
        WHEN OTHERS THEN
            RAISE WARNING '创建策略失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 策略3：基于角色的访问（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'documents') THEN
            RAISE WARNING '表 documents 不存在，无法创建策略';
            RETURN;
        END IF;

        IF EXISTS (SELECT 1 FROM pg_policies WHERE schemaname = 'public' AND tablename = 'documents' AND policyname = 'role_based_access') THEN
            RAISE NOTICE '策略 role_based_access 已存在';
        ELSE
            CREATE POLICY role_based_access
                ON documents
                FOR SELECT
                USING (
                    CASE
                        WHEN current_user_role() = 'admin' THEN true
                        WHEN current_user_role() = 'manager' THEN classification IN ('public', 'internal', 'confidential')
                        WHEN current_user_role() = 'employee' THEN classification IN ('public', 'internal')
                        ELSE classification = 'public'
                    END
                );
            RAISE NOTICE '策略 role_based_access 创建成功';
        END IF;
    EXCEPTION
        WHEN duplicate_object THEN
            RAISE WARNING '策略 role_based_access 已存在';
        WHEN syntax_error THEN
            RAISE WARNING '策略语法错误，请检查current_user_role()函数是否存在';
        WHEN OTHERS THEN
            RAISE WARNING '创建策略失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 策略4：时间范围访问（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'documents') THEN
            RAISE WARNING '表 documents 不存在，无法创建策略';
            RETURN;
        END IF;

        IF EXISTS (SELECT 1 FROM pg_policies WHERE schemaname = 'public' AND tablename = 'documents' AND policyname = 'time_based_access') THEN
            RAISE NOTICE '策略 time_based_access 已存在';
        ELSE
            CREATE POLICY time_based_access
                ON documents
                FOR SELECT
                USING (
                    created_at >= now() - interval '1 year'
                    OR owner_id = current_user_id()
                );
            RAISE NOTICE '策略 time_based_access 创建成功';
        END IF;
    EXCEPTION
        WHEN duplicate_object THEN
            RAISE WARNING '策略 time_based_access 已存在';
        WHEN syntax_error THEN
            RAISE WARNING '策略语法错误';
        WHEN OTHERS THEN
            RAISE WARNING '创建策略失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 策略5：地理位置限制（结合PostGIS，带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'locations') THEN
            RAISE WARNING '表 locations 不存在，无法创建策略';
            RETURN;
        END IF;

        IF NOT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'postgis') THEN
            RAISE WARNING '扩展 postgis 未安装，无法使用地理位置功能';
            RETURN;
        END IF;

        IF EXISTS (SELECT 1 FROM pg_policies WHERE schemaname = 'public' AND tablename = 'locations' AND policyname = 'geo_based_access') THEN
            RAISE NOTICE '策略 geo_based_access 已存在';
        ELSE
            CREATE POLICY geo_based_access
                ON locations
                FOR SELECT
                USING (
                    ST_DWithin(
                        location::geometry,
                        current_user_location()::geometry,
                        1000  -- 1km范围内
                    )
                );
            RAISE NOTICE '策略 geo_based_access 创建成功';
        END IF;
    EXCEPTION
        WHEN duplicate_object THEN
            RAISE WARNING '策略 geo_based_access 已存在';
        WHEN undefined_function THEN
            RAISE WARNING '函数不存在，请确保PostGIS扩展已安装';
        WHEN syntax_error THEN
            RAISE WARNING '策略语法错误，请检查ST_DWithin和current_user_location()函数';
        WHEN OTHERS THEN
            RAISE WARNING '创建策略失败: %', SQLERRM;
            RAISE;
    END;
END $$;
```

#### 1.3.2 INSERT策略（插入控制）

```sql
-- 策略：用户只能以自己的名义创建文档（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'documents') THEN
            RAISE WARNING '表 documents 不存在，无法创建策略';
            RETURN;
        END IF;

        IF EXISTS (SELECT 1 FROM pg_policies WHERE schemaname = 'public' AND tablename = 'documents' AND policyname = 'documents_insert_policy') THEN
            RAISE NOTICE '策略 documents_insert_policy 已存在';
        ELSE
            CREATE POLICY documents_insert_policy
                ON documents
                FOR INSERT
                WITH CHECK (owner_id = current_user_id());
            RAISE NOTICE '策略 documents_insert_policy 创建成功';
        END IF;
    EXCEPTION
        WHEN duplicate_object THEN
            RAISE WARNING '策略 documents_insert_policy 已存在';
        WHEN syntax_error THEN
            RAISE WARNING '策略语法错误，请检查current_user_id()函数是否存在';
        WHEN OTHERS THEN
            RAISE WARNING '创建策略失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 策略：限制classification（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'documents') THEN
            RAISE WARNING '表 documents 不存在，无法创建策略';
            RETURN;
        END IF;

        IF EXISTS (SELECT 1 FROM pg_policies WHERE schemaname = 'public' AND tablename = 'documents' AND policyname = 'classification_insert_policy') THEN
            RAISE NOTICE '策略 classification_insert_policy 已存在';
        ELSE
            CREATE POLICY classification_insert_policy
                ON documents
                FOR INSERT
                WITH CHECK (
                    classification IN ('public', 'internal')
                    OR current_user_role() = 'manager'
                );
            RAISE NOTICE '策略 classification_insert_policy 创建成功';
        END IF;
    EXCEPTION
        WHEN duplicate_object THEN
            RAISE WARNING '策略 classification_insert_policy 已存在';
        WHEN syntax_error THEN
            RAISE WARNING '策略语法错误，请检查current_user_role()函数是否存在';
        WHEN OTHERS THEN
            RAISE WARNING '创建策略失败: %', SQLERRM;
            RAISE;
    END;
END $$;
```

#### 1.3.3 UPDATE策略（更新控制）

```sql
-- 策略：只能更新自己的文档（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'documents') THEN
            RAISE WARNING '表 documents 不存在，无法创建策略';
            RETURN;
        END IF;

        IF EXISTS (SELECT 1 FROM pg_policies WHERE schemaname = 'public' AND tablename = 'documents' AND policyname = 'documents_update_policy') THEN
            RAISE NOTICE '策略 documents_update_policy 已存在';
        ELSE
            CREATE POLICY documents_update_policy
                ON documents
                FOR UPDATE
                USING (owner_id = current_user_id())
                WITH CHECK (owner_id = current_user_id());
            RAISE NOTICE '策略 documents_update_policy 创建成功';
        END IF;
    EXCEPTION
        WHEN duplicate_object THEN
            RAISE WARNING '策略 documents_update_policy 已存在';
        WHEN syntax_error THEN
            RAISE WARNING '策略语法错误，请检查current_user_id()函数是否存在';
        WHEN OTHERS THEN
            RAISE WARNING '创建策略失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 策略：不能降低classification（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'documents') THEN
            RAISE WARNING '表 documents 不存在，无法创建策略';
            RETURN;
        END IF;

        IF EXISTS (SELECT 1 FROM pg_policies WHERE schemaname = 'public' AND tablename = 'documents' AND policyname = 'classification_update_policy') THEN
            RAISE NOTICE '策略 classification_update_policy 已存在';
        ELSE
            CREATE POLICY classification_update_policy
                ON documents
                FOR UPDATE
                USING (true)
                WITH CHECK (
                    classification >= OLD.classification
                    OR current_user_role() = 'admin'
                );
            RAISE NOTICE '策略 classification_update_policy 创建成功';
        END IF;
    EXCEPTION
        WHEN duplicate_object THEN
            RAISE WARNING '策略 classification_update_policy 已存在';
        WHEN syntax_error THEN
            RAISE WARNING '策略语法错误，请检查current_user_role()函数是否存在';
        WHEN OTHERS THEN
            RAISE WARNING '创建策略失败: %', SQLERRM;
            RAISE;
    END;
END $$;
```

#### 1.3.4 DELETE策略（删除控制）

```sql
-- 策略：只能删除自己的文档（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'documents') THEN
            RAISE WARNING '表 documents 不存在，无法创建策略';
            RETURN;
        END IF;

        IF EXISTS (SELECT 1 FROM pg_policies WHERE schemaname = 'public' AND tablename = 'documents' AND policyname = 'documents_delete_policy') THEN
            RAISE NOTICE '策略 documents_delete_policy 已存在';
        ELSE
            CREATE POLICY documents_delete_policy
                ON documents
                FOR DELETE
                USING (
                    owner_id = current_user_id()
                    AND classification != 'secret'
                );
            RAISE NOTICE '策略 documents_delete_policy 创建成功';
        END IF;
    EXCEPTION
        WHEN duplicate_object THEN
            RAISE WARNING '策略 documents_delete_policy 已存在';
        WHEN syntax_error THEN
            RAISE WARNING '策略语法错误，请检查current_user_id()函数是否存在';
        WHEN OTHERS THEN
            RAISE WARNING '创建策略失败: %', SQLERRM;
            RAISE;
    END;
END $$;
```

### 1.4 RLS性能优化

#### 问题：RLS可能导致性能下降

```sql
-- 性能问题示例（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'large_table') THEN
            RAISE WARNING '表 large_table 不存在，无法创建策略';
            RETURN;
        END IF;
        RAISE WARNING '注意：此策略使用子查询，可能导致性能问题';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '操作准备失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- CREATE POLICY slow_policy
--     ON large_table
--     FOR SELECT
--     USING (
--         user_id IN (SELECT user_id FROM user_permissions WHERE ...)  -- 子查询可能很慢
--     );

#### 优化方案

**方案1：使用JOIN代替子查询**:

```sql
-- 优化策略（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'large_table') THEN
            RAISE WARNING '表 large_table 不存在，无法创建优化策略';
            RETURN;
        END IF;

        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'user_permissions') THEN
            RAISE WARNING '表 user_permissions 不存在，无法创建优化策略';
            RETURN;
        END IF;

        IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE schemaname = 'public' AND tablename = 'large_table' AND policyname = 'optimized_policy') THEN
            CREATE POLICY optimized_policy
            ON large_table
            FOR SELECT
            USING (
                EXISTS (
                    SELECT 1 FROM user_permissions up
                    WHERE up.user_id = large_table.user_id
                    AND up.resource_id = large_table.id
                )
            );
            RAISE NOTICE '优化策略 optimized_policy 创建成功';
        ELSE
            RAISE NOTICE '优化策略 optimized_policy 已存在';
        END IF;
    EXCEPTION
        WHEN undefined_table THEN
            RAISE WARNING '表不存在';
        WHEN duplicate_object THEN
            RAISE WARNING '策略已存在';
        WHEN OTHERS THEN
            RAISE WARNING '创建策略失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 确保索引（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'user_permissions') THEN
            RAISE WARNING '表 user_permissions 不存在，无法创建索引';
            RETURN;
        END IF;

        IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE schemaname = 'public' AND tablename = 'user_permissions' AND indexname = 'idx_user_permissions') THEN
            CREATE INDEX idx_user_permissions ON user_permissions(user_id, resource_id);
            RAISE NOTICE '索引 idx_user_permissions 创建成功';
        ELSE
            RAISE NOTICE '索引 idx_user_permissions 已存在';
        END IF;
    EXCEPTION
        WHEN undefined_table THEN
            RAISE WARNING '表 user_permissions 不存在';
        WHEN duplicate_table THEN
            RAISE WARNING '索引 idx_user_permissions 已存在';
        WHEN OTHERS THEN
            RAISE WARNING '创建索引失败: %', SQLERRM;
            RAISE;
    END;
END $$;

**方案2：使用物化视图缓存权限**:

```sql
-- 创建权限缓存（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'user_permissions') THEN
            RAISE WARNING '表 user_permissions 不存在，无法创建物化视图';
            RETURN;
        END IF;

        IF NOT EXISTS (SELECT 1 FROM pg_matviews WHERE schemaname = 'public' AND matviewname = 'user_accessible_documents') THEN
            CREATE MATERIALIZED VIEW user_accessible_documents AS
            SELECT user_id, document_id
            FROM user_permissions
            WHERE is_active = true;
            RAISE NOTICE '物化视图 user_accessible_documents 创建成功';
        ELSE
            RAISE NOTICE '物化视图 user_accessible_documents 已存在';
        END IF;
    EXCEPTION
        WHEN undefined_table THEN
            RAISE WARNING '表 user_permissions 不存在';
        WHEN duplicate_table THEN
            RAISE WARNING '物化视图 user_accessible_documents 已存在';
        WHEN OTHERS THEN
            RAISE WARNING '创建物化视图失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 创建索引（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_matviews WHERE schemaname = 'public' AND matviewname = 'user_accessible_documents') THEN
            RAISE WARNING '物化视图 user_accessible_documents 不存在，无法创建索引';
            RETURN;
        END IF;

        IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE schemaname = 'public' AND tablename = 'user_accessible_documents' AND indexname = 'user_accessible_documents_user_id_document_id_idx') THEN
            CREATE INDEX ON user_accessible_documents(user_id, document_id);
            RAISE NOTICE '索引创建成功';
        ELSE
            RAISE NOTICE '索引已存在';
        END IF;
    EXCEPTION
        WHEN undefined_table THEN
            RAISE WARNING '物化视图不存在';
        WHEN duplicate_table THEN
            RAISE WARNING '索引已存在';
        WHEN OTHERS THEN
            RAISE WARNING '创建索引失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 定期刷新（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_matviews WHERE schemaname = 'public' AND matviewname = 'user_accessible_documents') THEN
            RAISE WARNING '物化视图 user_accessible_documents 不存在，无法刷新';
            RETURN;
        END IF;
        RAISE NOTICE '开始刷新物化视图 user_accessible_documents';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '刷新准备失败: %', SQLERRM;
            RAISE;
    END;
END $$;

REFRESH MATERIALIZED VIEW CONCURRENTLY user_accessible_documents;

-- 使用缓存的策略（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'documents') THEN
            RAISE WARNING '表 documents 不存在，无法创建策略';
            RETURN;
        END IF;

        IF NOT EXISTS (SELECT 1 FROM pg_matviews WHERE schemaname = 'public' AND matviewname = 'user_accessible_documents') THEN
            RAISE WARNING '物化视图 user_accessible_documents 不存在，无法创建策略';
            RETURN;
        END IF;

        IF EXISTS (SELECT 1 FROM pg_policies WHERE schemaname = 'public' AND tablename = 'documents' AND policyname = 'cached_policy') THEN
            RAISE NOTICE '策略 cached_policy 已存在';
        ELSE
            CREATE POLICY cached_policy
                ON documents
                FOR SELECT
                USING (
                    id IN (
                        SELECT document_id
                        FROM user_accessible_documents
                        WHERE user_id = current_user_id()
                    )
                );
            RAISE NOTICE '策略 cached_policy 创建成功';
        END IF;
    EXCEPTION
        WHEN undefined_table THEN
            RAISE WARNING '表或物化视图不存在';
        WHEN duplicate_object THEN
            RAISE WARNING '策略 cached_policy 已存在';
        WHEN OTHERS THEN
            RAISE WARNING '创建策略失败: %', SQLERRM;
            RAISE;
    END;
END $$;
```

**方案3：使用Security Barrier Views**:

```sql
-- 创建Security Barrier视图（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'documents') THEN
            RAISE WARNING '表 documents 不存在，无法创建视图';
            RETURN;
        END IF;

        IF NOT EXISTS (SELECT 1 FROM information_schema.views WHERE table_schema = 'public' AND table_name = 'user_documents') THEN
            CREATE VIEW user_documents
            WITH (security_barrier = true) AS
            SELECT *
            FROM documents
            WHERE owner_id = current_user_id()
               OR department = current_user_department();
            RAISE NOTICE 'Security Barrier视图 user_documents 创建成功';
        ELSE
            RAISE NOTICE '视图 user_documents 已存在';
        END IF;
    EXCEPTION
        WHEN undefined_table THEN
            RAISE WARNING '表 documents 不存在';
        WHEN duplicate_table THEN
            RAISE WARNING '视图 user_documents 已存在';
        WHEN OTHERS THEN
            RAISE WARNING '创建视图失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 用户查询视图而不是表（带错误处理和性能测试）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.views WHERE table_schema = 'public' AND table_name = 'user_documents') THEN
            RAISE WARNING '视图 user_documents 不存在，无法执行查询';
            RETURN;
        END IF;
        RAISE NOTICE '开始查询Security Barrier视图 user_documents';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '查询准备失败: %', SQLERRM;
            RAISE;
    END;
END $$;

EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM user_documents;
```

### 1.5 多租户RLS完整方案

```sql
-- 多租户RLS完整方案（带错误处理）
-- 租户表（带错误处理）
DO $$
BEGIN
    BEGIN
        IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'tenants') THEN
            RAISE NOTICE '表 tenants 已存在';
        ELSE
            CREATE TABLE tenants (
                tenant_id serial PRIMARY KEY,
                tenant_name text UNIQUE NOT NULL,
                created_at timestamptz DEFAULT now()
            );
            RAISE NOTICE '表 tenants 创建成功';
        END IF;
    EXCEPTION
        WHEN duplicate_table THEN
            RAISE WARNING '表 tenants 已存在';
        WHEN OTHERS THEN
            RAISE WARNING '创建表失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 用户表（带错误处理）
DO $$
BEGIN
    BEGIN
        IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'users') THEN
            RAISE NOTICE '表 users 已存在';
        ELSE
            IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'tenants') THEN
                RAISE WARNING '表 tenants 不存在，无法创建外键约束';
            END IF;

            CREATE TABLE users (
                user_id serial PRIMARY KEY,
                username text UNIQUE NOT NULL,
                tenant_id int REFERENCES tenants(tenant_id),
                role text CHECK (role IN ('admin', 'user', 'readonly'))
            );
            RAISE NOTICE '表 users 创建成功';
        END IF;
    EXCEPTION
        WHEN duplicate_table THEN
            RAISE WARNING '表 users 已存在';
        WHEN foreign_key_violation THEN
            RAISE WARNING '外键约束失败，请确保表 tenants 存在';
        WHEN OTHERS THEN
            RAISE WARNING '创建表失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 业务表（多租户，带错误处理）
DO $$
BEGIN
    BEGIN
        IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'orders') THEN
            RAISE NOTICE '表 orders 已存在';
        ELSE
            IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'tenants') OR
               NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'users') THEN
                RAISE WARNING '表 tenants 或 users 不存在，无法创建外键约束';
            END IF;

            CREATE TABLE orders (
                order_id serial PRIMARY KEY,
                tenant_id int NOT NULL REFERENCES tenants(tenant_id),
                user_id int NOT NULL REFERENCES users(user_id),
                amount numeric(10,2),
                status text,
                created_at timestamptz DEFAULT now()
            );
            RAISE NOTICE '表 orders 创建成功';
        END IF;
    EXCEPTION
        WHEN duplicate_table THEN
            RAISE WARNING '表 orders 已存在';
        WHEN foreign_key_violation THEN
            RAISE WARNING '外键约束失败，请确保表 tenants 和 users 存在';
        WHEN OTHERS THEN
            RAISE WARNING '创建表失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 启用RLS（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'orders') THEN
            RAISE WARNING '表 orders 不存在，无法启用RLS';
        ELSE
            ALTER TABLE orders ENABLE ROW LEVEL SECURITY;
            RAISE NOTICE '表 orders 的RLS已启用';
        END IF;
    EXCEPTION
        WHEN undefined_table THEN
            RAISE WARNING '表 orders 不存在';
        WHEN OTHERS THEN
            RAISE WARNING '启用RLS失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 策略1：租户隔离（最重要，带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'orders') THEN
            RAISE WARNING '表 orders 不存在，无法创建策略';
            RETURN;
        END IF;

        IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE schemaname = 'public' AND tablename = 'orders' AND policyname = 'tenant_isolation') THEN
            CREATE POLICY tenant_isolation
            ON orders
            FOR ALL
            USING (tenant_id = current_setting('app.tenant_id')::int);
            RAISE NOTICE '策略 tenant_isolation 创建成功';
        ELSE
            RAISE NOTICE '策略 tenant_isolation 已存在';
        END IF;
    EXCEPTION
        WHEN undefined_table THEN
            RAISE WARNING '表 orders 不存在';
        WHEN duplicate_object THEN
            RAISE WARNING '策略 tenant_isolation 已存在';
        WHEN OTHERS THEN
            RAISE WARNING '创建策略失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 策略2：用户权限（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'orders') THEN
            RAISE WARNING '表 orders 不存在，无法创建策略';
            RETURN;
        END IF;

        IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE schemaname = 'public' AND tablename = 'orders' AND policyname = 'user_access') THEN
            CREATE POLICY user_access
            ON orders
            FOR SELECT
            USING (
                -- 管理员可以看所有
                current_user_role() = 'admin'
                -- 普通用户只能看自己的
                OR user_id = current_user_id()
            );
            RAISE NOTICE '策略 user_access 创建成功';
        ELSE
            RAISE NOTICE '策略 user_access 已存在';
        END IF;
    EXCEPTION
        WHEN undefined_table THEN
            RAISE WARNING '表 orders 不存在';
        WHEN duplicate_object THEN
            RAISE WARNING '策略 user_access 已存在';
        WHEN OTHERS THEN
            RAISE WARNING '创建策略失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 策略3：只读用户不能修改（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'orders') THEN
            RAISE WARNING '表 orders 不存在，无法创建策略';
            RETURN;
        END IF;

        IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE schemaname = 'public' AND tablename = 'orders' AND policyname = 'readonly_restriction') THEN
            CREATE POLICY readonly_restriction
            ON orders
            FOR UPDATE
            USING (current_user_role() != 'readonly');
            RAISE NOTICE '策略 readonly_restriction 创建成功';
        ELSE
            RAISE NOTICE '策略 readonly_restriction 已存在';
        END IF;

        IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE schemaname = 'public' AND tablename = 'orders' AND policyname = 'readonly_delete_restriction') THEN
            CREATE POLICY readonly_delete_restriction
            ON orders
            FOR DELETE
            USING (current_user_role() != 'readonly');
            RAISE NOTICE '策略 readonly_delete_restriction 创建成功';
        ELSE
            RAISE NOTICE '策略 readonly_delete_restriction 已存在';
        END IF;
    EXCEPTION
        WHEN undefined_table THEN
            RAISE WARNING '表 orders 不存在';
        WHEN duplicate_object THEN
            RAISE WARNING '部分策略已存在';
        WHEN OTHERS THEN
            RAISE WARNING '创建策略失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 辅助函数（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'current_user_id' AND pronamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public')) THEN
            CREATE FUNCTION current_user_id() RETURNS int AS $$
                SELECT current_setting('app.user_id')::int;
            $$ LANGUAGE SQL STABLE;
            RAISE NOTICE '函数 current_user_id 创建成功';
        ELSE
            RAISE NOTICE '函数 current_user_id 已存在';
        END IF;

        IF NOT EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'current_user_role' AND pronamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public')) THEN
            CREATE FUNCTION current_user_role() RETURNS text AS $$
                SELECT current_setting('app.user_role')::text;
            $$ LANGUAGE SQL STABLE;
            RAISE NOTICE '函数 current_user_role 创建成功';
        ELSE
            RAISE NOTICE '函数 current_user_role 已存在';
        END IF;
    EXCEPTION
        WHEN duplicate_function THEN
            RAISE WARNING '部分函数已存在';
        WHEN OTHERS THEN
            RAISE WARNING '创建函数失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 应用层设置（每个请求开始时，带错误处理）
DO $$
BEGIN
    BEGIN
        PERFORM set_config('app.tenant_id', '123', false);
        PERFORM set_config('app.user_id', '456', false);
        PERFORM set_config('app.user_role', 'user', false);
        RAISE NOTICE '应用层配置设置成功';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '设置配置失败: %', SQLERRM;
            RAISE;
    END;
END $$;

---

## 2. 审计日志系统

### 2.1 使用pgAudit扩展

**安装**：

```bash
# Ubuntu/Debian
sudo apt-get install postgresql-17-pgaudit

# 配置postgresql.conf
shared_preload_libraries = 'pgaudit'
pgaudit.log = 'all'  # 或者 'read, write, ddl'
pgaudit.log_catalog = off
pgaudit.log_level = 'log'
pgaudit.log_parameter = on
pgaudit.log_relation = on
pgaudit.log_statement_once = off
```

**使用**：

```sql
-- 创建扩展（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'pgaudit') THEN
            CREATE EXTENSION pgaudit;
            RAISE NOTICE '扩展 pgaudit 创建成功';
        ELSE
            RAISE NOTICE '扩展 pgaudit 已存在';
        END IF;
    EXCEPTION
        WHEN duplicate_object THEN
            RAISE WARNING '扩展 pgaudit 已存在';
        WHEN OTHERS THEN
            RAISE WARNING '创建扩展失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 配置审计（会话级别，带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'pgaudit') THEN
            RAISE WARNING '扩展 pgaudit 未安装，无法配置审计';
            RETURN;
        END IF;
        RAISE NOTICE '配置审计（会话级别）';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '配置准备失败: %', SQLERRM;
            RAISE;
    END;
END $$;

SET pgaudit.log = 'read, write';
SET pgaudit.log_relation = on;

-- 配置审计（数据库级别，带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'pgaudit') THEN
            RAISE WARNING '扩展 pgaudit 未安装，无法配置审计';
            RETURN;
        END IF;
        RAISE NOTICE '配置审计（数据库级别）';
        RAISE NOTICE 'ALTER DATABASE mydb SET pgaudit.log = ''ddl, role'';';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '配置准备失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- ALTER DATABASE mydb SET pgaudit.log = 'ddl, role';

-- 配置审计（用户级别，带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'pgaudit') THEN
            RAISE WARNING '扩展 pgaudit 未安装，无法配置审计';
            RETURN;
        END IF;

        IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'dba') THEN
            RAISE WARNING '角色 dba 不存在，无法配置审计';
        ELSE
            ALTER ROLE dba SET pgaudit.log = 'all';
            RAISE NOTICE '角色 dba 的审计配置完成';
        END IF;
    EXCEPTION
        WHEN undefined_object THEN
            RAISE WARNING '角色 dba 不存在';
        WHEN OTHERS THEN
            RAISE WARNING '配置审计失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 配置审计（表级别，带错误处理）
DO $$
BEGIN
    BEGIN
        IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'sensitive_data') THEN
            RAISE NOTICE '表 sensitive_data 已存在';
        ELSE
            CREATE TABLE sensitive_data (
                id serial PRIMARY KEY,
                ssn text,
                credit_card text
            );
            RAISE NOTICE '表 sensitive_data 创建成功';
        END IF;
    EXCEPTION
        WHEN duplicate_table THEN
            RAISE WARNING '表 sensitive_data 已存在';
        WHEN OTHERS THEN
            RAISE WARNING '创建表失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 为特定表启用审计（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'sensitive_data') THEN
            RAISE WARNING '表 sensitive_data 不存在，无法启用审计';
        ELSE
            ALTER TABLE sensitive_data SET (pgaudit.log = 'read, write');
            RAISE NOTICE '表 sensitive_data 的审计配置完成';
        END IF;
    EXCEPTION
        WHEN undefined_table THEN
            RAISE WARNING '表 sensitive_data 不存在';
        WHEN OTHERS THEN
            RAISE WARNING '配置审计失败: %', SQLERRM;
            RAISE;
    END;
END $$;

**审计日志示例**：

```text
2025-01-01 10:00:00 UTC [12345]: [1-1] user=alice,db=mydb LOG:  AUDIT: SESSION,1,1,READ,SELECT,,,
    "SELECT * FROM sensitive_data WHERE id = 1",<not logged>
2025-01-01 10:00:05 UTC [12346]: [1-1] user=bob,db=mydb LOG:  AUDIT: SESSION,2,1,WRITE,UPDATE,,,
    "UPDATE sensitive_data SET ssn = '***' WHERE id = 2",<not logged>
```

### 2.2 自定义审计触发器

**完整审计表设计**：

```sql
-- 审计日志表（带错误处理）
DO $$
BEGIN
    BEGIN
        IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'audit_log') THEN
            RAISE NOTICE '表 audit_log 已存在';
        ELSE
            CREATE TABLE audit_log (
                audit_id bigserial PRIMARY KEY,
                table_name text NOT NULL,
                operation text NOT NULL CHECK (operation IN ('INSERT', 'UPDATE', 'DELETE', 'TRUNCATE')),
                old_data jsonb,
                new_data jsonb,
                changed_fields text[],
                user_name text NOT NULL,
                user_ip inet,
                application_name text,
                transaction_id bigint,
                occurred_at timestamptz NOT NULL DEFAULT now(),
                query_text text
            ) PARTITION BY RANGE (occurred_at);
            RAISE NOTICE '表 audit_log 创建成功（分区表）';
        END IF;
    EXCEPTION
        WHEN duplicate_table THEN
            RAISE WARNING '表 audit_log 已存在';
        WHEN OTHERS THEN
            RAISE WARNING '创建表失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 索引（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'audit_log') THEN
            RAISE WARNING '表 audit_log 不存在，无法创建索引';
            RETURN;
        END IF;

        IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE schemaname = 'public' AND tablename = 'audit_log' AND indexname = 'idx_audit_log_table') THEN
            CREATE INDEX idx_audit_log_table ON audit_log(table_name);
            RAISE NOTICE '索引 idx_audit_log_table 创建成功';
        END IF;

        IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE schemaname = 'public' AND tablename = 'audit_log' AND indexname = 'idx_audit_log_user') THEN
            CREATE INDEX idx_audit_log_user ON audit_log(user_name);
            RAISE NOTICE '索引 idx_audit_log_user 创建成功';
        END IF;

        IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE schemaname = 'public' AND tablename = 'audit_log' AND indexname = 'idx_audit_log_time') THEN
            CREATE INDEX idx_audit_log_time ON audit_log(occurred_at);
            RAISE NOTICE '索引 idx_audit_log_time 创建成功';
        END IF;

        IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE schemaname = 'public' AND tablename = 'audit_log' AND indexname = 'idx_audit_log_operation') THEN
            CREATE INDEX idx_audit_log_operation ON audit_log(operation);
            RAISE NOTICE '索引 idx_audit_log_operation 创建成功';
        END IF;

        IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE schemaname = 'public' AND tablename = 'audit_log' AND indexname = 'idx_audit_log_data') THEN
            CREATE INDEX idx_audit_log_data ON audit_log USING gin(old_data, new_data);
            RAISE NOTICE 'GIN索引 idx_audit_log_data 创建成功';
        END IF;
    EXCEPTION
        WHEN undefined_table THEN
            RAISE WARNING '表 audit_log 不存在';
        WHEN duplicate_table THEN
            RAISE WARNING '部分索引已存在';
        WHEN OTHERS THEN
            RAISE WARNING '创建索引失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 分区（按月，带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'audit_log') THEN
            RAISE WARNING '表 audit_log 不存在，无法创建分区';
            RETURN;
        END IF;

        IF NOT EXISTS (SELECT 1 FROM pg_tables WHERE schemaname = 'public' AND tablename = 'audit_log_2025_01') THEN
            CREATE TABLE audit_log_2025_01 PARTITION OF audit_log
            FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');
            RAISE NOTICE '分区 audit_log_2025_01 创建成功';
        ELSE
            RAISE NOTICE '分区 audit_log_2025_01 已存在';
        END IF;
    EXCEPTION
        WHEN duplicate_table THEN
            RAISE WARNING '分区已存在';
        WHEN OTHERS THEN
            RAISE WARNING '创建分区失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 自动创建分区函数（带完整错误处理）
CREATE OR REPLACE FUNCTION create_audit_partition()
RETURNS void AS $$
DECLARE
    partition_date date;
    partition_name text;
    start_date date;
    end_date date;
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'audit_log') THEN
            RAISE EXCEPTION '表 audit_log 不存在，无法创建分区';
        END IF;

        partition_date := date_trunc('month', now() + interval '1 month');
        partition_name := 'audit_log_' || to_char(partition_date, 'YYYY_MM');
        start_date := partition_date;
        end_date := partition_date + interval '1 month';

        IF EXISTS (
            SELECT 1 FROM pg_tables
            WHERE schemaname = 'public'
            AND tablename = partition_name
        ) THEN
            RAISE NOTICE '分区 % 已存在，跳过创建', partition_name;
            RETURN;
        END IF;

        EXECUTE format(
            'CREATE TABLE IF NOT EXISTS %I PARTITION OF audit_log FOR VALUES FROM (%L) TO (%L)',
            partition_name, start_date, end_date
        );
        RAISE NOTICE '分区 % 创建成功', partition_name;
    EXCEPTION
        WHEN duplicate_table THEN
            RAISE NOTICE '分区 % 已存在', partition_name;
        WHEN OTHERS THEN
            RAISE EXCEPTION 'create_audit_partition执行失败: %', SQLERRM;
    END;
END;
$$ LANGUAGE plpgsql;

-- 定期任务（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'pg_cron') THEN
            RAISE WARNING '扩展 pg_cron 未安装，无法创建定期任务';
            RAISE NOTICE '需要先安装扩展: CREATE EXTENSION pg_cron;';
        ELSE
            BEGIN
                PERFORM cron.schedule('create_audit_partition', '0 0 25 * *', 'SELECT create_audit_partition()');
                RAISE NOTICE '定期任务 create_audit_partition 创建成功';
            EXCEPTION
                WHEN duplicate_object THEN
                    RAISE WARNING '定期任务 create_audit_partition 已存在';
                WHEN OTHERS THEN
                    RAISE WARNING '创建定期任务失败: %', SQLERRM;
                    RAISE;
            END;
        END IF;
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '操作失败: %', SQLERRM;
            RAISE;
    END;
END $$;

**通用审计触发器函数**：

```sql
-- 通用审计触发器函数（带完整错误处理）
CREATE OR REPLACE FUNCTION audit_trigger_function()
RETURNS trigger AS $$
DECLARE
    old_data jsonb;
    new_data jsonb;
    changed_fields text[];
    query_text text;
BEGIN
    BEGIN
        -- 检查audit_log表是否存在
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'audit_log') THEN
            RAISE WARNING '表 audit_log 不存在，无法记录审计日志';
            IF TG_OP = 'DELETE' THEN
                RETURN OLD;
            ELSE
                RETURN NEW;
            END IF;
        END IF;

        -- 获取查询文本
        BEGIN
            query_text := current_query();
        EXCEPTION
            WHEN OTHERS THEN
                query_text := NULL;
                RAISE NOTICE '无法获取查询文本: %', SQLERRM;
        END;

        -- 处理不同操作
        IF TG_OP = 'INSERT' THEN
            BEGIN
                new_data := to_jsonb(NEW);
                old_data := NULL;
                changed_fields := NULL;
            EXCEPTION
                WHEN OTHERS THEN
                    RAISE WARNING '处理INSERT操作失败: %', SQLERRM;
                    RAISE;
            END;

        ELSIF TG_OP = 'UPDATE' THEN
            BEGIN
                old_data := to_jsonb(OLD);
                new_data := to_jsonb(NEW);

                -- 找出变更的字段
                BEGIN
                    SELECT array_agg(key)
                    INTO changed_fields
                    FROM (
                        SELECT key
                        FROM jsonb_each(new_data)
                        WHERE new_data->key IS DISTINCT FROM old_data->key
                    ) t;
                EXCEPTION
                    WHEN OTHERS THEN
                        changed_fields := NULL;
                        RAISE NOTICE '计算变更字段失败: %', SQLERRM;
                END;
            EXCEPTION
                WHEN OTHERS THEN
                    RAISE WARNING '处理UPDATE操作失败: %', SQLERRM;
                    RAISE;
            END;

        ELSIF TG_OP = 'DELETE' THEN
            BEGIN
                old_data := to_jsonb(OLD);
                new_data := NULL;
                changed_fields := NULL;
            EXCEPTION
                WHEN OTHERS THEN
                    RAISE WARNING '处理DELETE操作失败: %', SQLERRM;
                    RAISE;
            END;
        END IF;

        -- 插入审计日志
        BEGIN
            INSERT INTO audit_log (
                table_name,
                operation,
                old_data,
                new_data,
                changed_fields,
                user_name,
                user_ip,
                application_name,
                transaction_id,
                query_text
            ) VALUES (
                TG_TABLE_NAME,
                TG_OP,
                old_data,
                new_data,
                changed_fields,
                current_user,
                inet_client_addr(),
                current_setting('application_name', true),
                txid_current(),
                query_text
            );
        EXCEPTION
            WHEN OTHERS THEN
                RAISE WARNING '插入审计日志失败: %', SQLERRM;
                -- 继续执行，不中断原操作
        END;

        -- 返回适当的值
        IF TG_OP = 'DELETE' THEN
            RETURN OLD;
        ELSE
            RETURN NEW;
        END IF;
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING 'audit_trigger_function执行失败: %', SQLERRM;
            -- 返回适当的值，不中断原操作
            IF TG_OP = 'DELETE' THEN
                RETURN OLD;
            ELSE
                RETURN NEW;
            END IF;
    END;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
```

**应用到表**：

```sql
-- 为敏感表创建审计触发器（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'sensitive_data') THEN
            RAISE WARNING '表 sensitive_data 不存在，无法创建审计触发器';
            RETURN;
        END IF;

        IF NOT EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'audit_trigger_function' AND pronamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public')) THEN
            RAISE WARNING '函数 audit_trigger_function 不存在，无法创建审计触发器';
            RETURN;
        END IF;

        IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'audit_sensitive_data') THEN
            CREATE TRIGGER audit_sensitive_data
            AFTER INSERT OR UPDATE OR DELETE
            ON sensitive_data
            FOR EACH ROW
            EXECUTE FUNCTION audit_trigger_function();
            RAISE NOTICE '审计触发器 audit_sensitive_data 创建成功';
        ELSE
            RAISE NOTICE '审计触发器 audit_sensitive_data 已存在';
        END IF;
    EXCEPTION
        WHEN undefined_table THEN
            RAISE WARNING '表 sensitive_data 不存在';
        WHEN undefined_function THEN
            RAISE WARNING '函数 audit_trigger_function 不存在';
        WHEN duplicate_object THEN
            RAISE WARNING '触发器 audit_sensitive_data 已存在';
        WHEN OTHERS THEN
            RAISE WARNING '创建触发器失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 批量应用到所有表（带完整错误处理）
DO $$
DECLARE
    table_record record;
    processed_count INTEGER := 0;
    error_count INTEGER := 0;
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'audit_trigger_function' AND pronamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public')) THEN
            RAISE EXCEPTION '函数 audit_trigger_function 不存在，无法批量创建触发器';
        END IF;

        RAISE NOTICE '开始批量创建审计触发器';

        FOR table_record IN
            SELECT schemaname, tablename
            FROM pg_tables
            WHERE schemaname = 'public'
              AND tablename != 'audit_log'
        LOOP
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM pg_trigger
                    WHERE tgname = 'audit_' || table_record.tablename
                ) THEN
                    EXECUTE format(
                        'CREATE TRIGGER audit_%I AFTER INSERT OR UPDATE OR DELETE ON %I.%I FOR EACH ROW EXECUTE FUNCTION audit_trigger_function()',
                        table_record.tablename,
                        table_record.schemaname,
                        table_record.tablename
                    );
                    processed_count := processed_count + 1;
                    RAISE NOTICE '表 % 的审计触发器创建成功', table_record.tablename;
                ELSE
                    RAISE NOTICE '表 % 的审计触发器已存在，跳过', table_record.tablename;
                END IF;
            EXCEPTION
                WHEN undefined_table THEN
                    RAISE WARNING '表 % 不存在，跳过', table_record.tablename;
                    error_count := error_count + 1;
                WHEN duplicate_object THEN
                    RAISE WARNING '表 % 的触发器已存在，跳过', table_record.tablename;
                WHEN OTHERS THEN
                    RAISE WARNING '为表 % 创建触发器失败: %', table_record.tablename, SQLERRM;
                    error_count := error_count + 1;
            END;
        END LOOP;

        RAISE NOTICE '批量创建完成：成功 % 个，失败 % 个', processed_count, error_count;
    EXCEPTION
        WHEN OTHERS THEN
            RAISE EXCEPTION '批量创建触发器失败: %', SQLERRM;
    END;
END $$;
```

### 2.3 审计日志查询和分析

```sql
-- 审计日志查询和分析（带错误处理和性能测试）
-- 查询1：查看某个用户的所有操作（带错误处理和性能测试）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'audit_log') THEN
            RAISE WARNING '表 audit_log 不存在，无法执行查询';
            RETURN;
        END IF;
        RAISE NOTICE '开始查询用户 alice 的所有操作';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '查询准备失败: %', SQLERRM;
            RAISE;
    END;
END $$;

EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    occurred_at,
    table_name,
    operation,
    changed_fields,
    query_text
FROM audit_log
WHERE user_name = 'alice'
ORDER BY occurred_at DESC
LIMIT 100;

-- 查询2：查看敏感数据访问（带错误处理和性能测试）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'audit_log') THEN
            RAISE WARNING '表 audit_log 不存在，无法执行查询';
            RETURN;
        END IF;
        RAISE NOTICE '开始查询敏感数据访问';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '查询准备失败: %', SQLERRM;
            RAISE;
    END;
END $$;

EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    user_name,
    user_ip,
    COUNT(*) AS access_count,
    array_agg(DISTINCT operation) AS operations
FROM audit_log
WHERE table_name = 'sensitive_data'
  AND occurred_at >= now() - interval '24 hours'
GROUP BY user_name, user_ip
ORDER BY access_count DESC;

-- 查询3：查找异常操作（大量删除，带错误处理和性能测试）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'audit_log') THEN
            RAISE WARNING '表 audit_log 不存在，无法执行查询';
            RETURN;
        END IF;
        RAISE NOTICE '开始查找异常操作（大量删除）';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '查询准备失败: %', SQLERRM;
            RAISE;
    END;
END $$;

EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    user_name,
    table_name,
    COUNT(*) AS delete_count,
    min(occurred_at) AS first_delete,
    max(occurred_at) AS last_delete
FROM audit_log
WHERE operation = 'DELETE'
  AND occurred_at >= now() - interval '1 hour'
GROUP BY user_name, table_name
HAVING COUNT(*) > 100  -- 1小时内删除超过100行
ORDER BY delete_count DESC;

-- 查询4：数据变更历史（带错误处理和性能测试）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'audit_log') THEN
            RAISE WARNING '表 audit_log 不存在，无法执行查询';
            RETURN;
        END IF;
        RAISE NOTICE '开始查询数据变更历史';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '查询准备失败: %', SQLERRM;
            RAISE;
    END;
END $$;

EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    audit_id,
    operation,
    occurred_at,
    user_name,
    old_data->>'title' AS old_title,
    new_data->>'title' AS new_title,
    changed_fields
FROM audit_log
WHERE table_name = 'documents'
  AND (old_data->>'id' = '123' OR new_data->>'id' = '123')
ORDER BY occurred_at;

-- 查询5：恢复删除的数据（带错误处理和性能测试）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'audit_log') THEN
            RAISE WARNING '表 audit_log 不存在，无法执行查询';
            RETURN;
        END IF;
        RAISE NOTICE '开始查询删除的数据（用于恢复）';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '查询准备失败: %', SQLERRM;
            RAISE;
    END;
END $$;

EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    old_data->>'id' AS id,
    old_data->>'title' AS title,
    old_data->>'content' AS content
FROM audit_log
WHERE table_name = 'documents'
  AND operation = 'DELETE'
  AND old_data->>'id' = '123';

-- 恢复数据（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'documents') THEN
            RAISE WARNING '表 documents 不存在，无法恢复数据';
            RETURN;
        END IF;

        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'audit_log') THEN
            RAISE WARNING '表 audit_log 不存在，无法恢复数据';
            RETURN;
        END IF;
        RAISE NOTICE '开始恢复删除的数据';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '恢复准备失败: %', SQLERRM;
            RAISE;
    END;
END $$;

BEGIN
    INSERT INTO documents (id, title, content)
    SELECT
        (old_data->>'id')::int,
        old_data->>'title',
        old_data->>'content'
    FROM audit_log
    WHERE table_name = 'documents'
      AND operation = 'DELETE'
      AND old_data->>'id' = '123'
    ORDER BY occurred_at DESC
    LIMIT 1;
EXCEPTION
    WHEN unique_violation THEN
        RAISE WARNING '数据已存在，无法恢复';
        RAISE;
    WHEN OTHERS THEN
        RAISE WARNING '恢复数据失败: %', SQLERRM;
        RAISE;
END;
```

### 2.4 不可篡改审计日志

```sql
-- 使用Ledger表（PostgreSQL 18+概念，当前可用hash链实现，带错误处理）
DO $$
BEGIN
    BEGIN
        IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'immutable_audit_log') THEN
            RAISE NOTICE '表 immutable_audit_log 已存在';
        ELSE
            CREATE TABLE immutable_audit_log (
                audit_id bigserial PRIMARY KEY,
                table_name text NOT NULL,
                operation text NOT NULL,
                data_hash text NOT NULL,  -- 数据哈希
                previous_hash text,        -- 前一条记录的哈希
                chain_hash text NOT NULL,  -- 链式哈希
                occurred_at timestamptz NOT NULL DEFAULT now()
            );
            RAISE NOTICE '表 immutable_audit_log 创建成功（Ledger表）';
        END IF;
    EXCEPTION
        WHEN duplicate_table THEN
            RAISE WARNING '表 immutable_audit_log 已存在';
        WHEN OTHERS THEN
            RAISE WARNING '创建表失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 审计插入函数（带哈希链，带完整错误处理）
CREATE OR REPLACE FUNCTION insert_immutable_audit()
RETURNS trigger AS $$
DECLARE
    data_text text;
    data_hash_val text;
    prev_hash_val text;
    chain_hash_val text;
BEGIN
    BEGIN
        -- 检查pgcrypto扩展
        IF NOT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'pgcrypto') THEN
            RAISE EXCEPTION '扩展 pgcrypto 未安装，无法计算哈希';
        END IF;

        -- 计算数据哈希
        BEGIN
            data_text := NEW.table_name || NEW.operation || coalesce(NEW.old_data::text, '') || coalesce(NEW.new_data::text, '');
            data_hash_val := encode(digest(data_text, 'sha256'), 'hex');
        EXCEPTION
            WHEN OTHERS THEN
                RAISE EXCEPTION '计算数据哈希失败: %', SQLERRM;
        END;

        -- 获取前一条记录的chain_hash
        BEGIN
            SELECT chain_hash INTO prev_hash_val
            FROM immutable_audit_log
            ORDER BY audit_id DESC
            LIMIT 1;
        EXCEPTION
            WHEN no_data_found THEN
                prev_hash_val := NULL;
            WHEN OTHERS THEN
                RAISE WARNING '获取前一条记录哈希失败: %', SQLERRM;
                prev_hash_val := NULL;
        END;

        -- 计算链式哈希
        BEGIN
            chain_hash_val := encode(
                digest(coalesce(prev_hash_val, '') || data_hash_val, 'sha256'),
                'hex'
            );
        EXCEPTION
            WHEN OTHERS THEN
                RAISE EXCEPTION '计算链式哈希失败: %', SQLERRM;
        END;

        -- 更新NEW记录
        NEW.data_hash := data_hash_val;
        NEW.previous_hash := prev_hash_val;
        NEW.chain_hash := chain_hash_val;

        RETURN NEW;
    EXCEPTION
        WHEN OTHERS THEN
            RAISE EXCEPTION 'insert_immutable_audit执行失败: %', SQLERRM;
    END;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 创建触发器（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'immutable_audit_log') THEN
            RAISE WARNING '表 immutable_audit_log 不存在，无法创建触发器';
            RETURN;
        END IF;

        IF NOT EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'insert_immutable_audit' AND pronamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public')) THEN
            RAISE WARNING '函数 insert_immutable_audit 不存在，无法创建触发器';
            RETURN;
        END IF;

        IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'immutable_audit_trigger') THEN
            CREATE TRIGGER immutable_audit_trigger
            BEFORE INSERT ON immutable_audit_log
            FOR EACH ROW
            EXECUTE FUNCTION insert_immutable_audit();
            RAISE NOTICE '触发器 immutable_audit_trigger 创建成功';
        ELSE
            RAISE NOTICE '触发器 immutable_audit_trigger 已存在';
        END IF;
    EXCEPTION
        WHEN undefined_table THEN
            RAISE WARNING '表 immutable_audit_log 不存在';
        WHEN undefined_function THEN
            RAISE WARNING '函数 insert_immutable_audit 不存在';
        WHEN duplicate_object THEN
            RAISE WARNING '触发器 immutable_audit_trigger 已存在';
        WHEN OTHERS THEN
            RAISE WARNING '创建触发器失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 验证审计链完整性
CREATE OR REPLACE FUNCTION verify_audit_chain()
RETURNS TABLE(audit_id bigint, is_valid boolean, error_message text) AS $$
DECLARE
    rec record;
    expected_chain_hash text;
BEGIN
    FOR rec IN
        SELECT a1.audit_id, a1.data_hash, a1.previous_hash, a1.chain_hash,
               lag(a1.chain_hash) OVER (ORDER BY a1.audit_id) AS prev_chain_hash
        FROM immutable_audit_log a1
        ORDER BY a1.audit_id
    LOOP
        -- 验证previous_hash
        IF rec.previous_hash IS DISTINCT FROM rec.prev_chain_hash THEN
            RETURN QUERY SELECT rec.audit_id, false, 'Previous hash mismatch';
            CONTINUE;
        END IF;

        -- 验证chain_hash
        expected_chain_hash := encode(
            digest(coalesce(rec.previous_hash, '') || rec.data_hash, 'sha256'),
            'hex'
        );

        IF rec.chain_hash != expected_chain_hash THEN
            RETURN QUERY SELECT rec.audit_id, false, 'Chain hash mismatch';
            CONTINUE;
        END IF;

        RETURN QUERY SELECT rec.audit_id, true, NULL::text;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- 定期验证
SELECT * FROM verify_audit_chain() WHERE NOT is_valid;
```

---

## 3. 数据脱敏

### 3.1 静态脱敏（数据导出时）

```sql
-- 创建脱敏函数（带错误处理）
DO $$
BEGIN
    BEGIN
        -- 创建mask_phone函数
        IF NOT EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'mask_phone' AND pronamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public')) THEN
            CREATE OR REPLACE FUNCTION mask_phone(phone text)
            RETURNS text AS $$
                SELECT regexp_replace(phone, '(\d{3})\d{4}(\d{4})', '\1****\2');
            $$ LANGUAGE SQL IMMUTABLE;
            RAISE NOTICE '函数 mask_phone 创建成功';
        ELSE
            RAISE NOTICE '函数 mask_phone 已存在';
        END IF;

        -- 创建mask_email函数
        IF NOT EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'mask_email' AND pronamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public')) THEN
            CREATE OR REPLACE FUNCTION mask_email(email text)
            RETURNS text AS $$
                SELECT regexp_replace(email, '(.{2})(.*)(@.*)', '\1***\3');
            $$ LANGUAGE SQL IMMUTABLE;
            RAISE NOTICE '函数 mask_email 创建成功';
        ELSE
            RAISE NOTICE '函数 mask_email 已存在';
        END IF;

        -- 创建mask_id_card函数
        IF NOT EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'mask_id_card' AND pronamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public')) THEN
            CREATE OR REPLACE FUNCTION mask_id_card(id_card text)
            RETURNS text AS $$
                SELECT regexp_replace(id_card, '(\d{6})\d{8}(\d{4})', '\1********\2');
            $$ LANGUAGE SQL IMMUTABLE;
            RAISE NOTICE '函数 mask_id_card 创建成功';
        ELSE
            RAISE NOTICE '函数 mask_id_card 已存在';
        END IF;

        -- 创建mask_credit_card函数
        IF NOT EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'mask_credit_card' AND pronamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public')) THEN
            CREATE OR REPLACE FUNCTION mask_credit_card(cc text)
            RETURNS text AS $$
                SELECT regexp_replace(cc, '(\d{4})\d{8}(\d{4})', '\1********\2');
            $$ LANGUAGE SQL IMMUTABLE;
            RAISE NOTICE '函数 mask_credit_card 创建成功';
        ELSE
            RAISE NOTICE '函数 mask_credit_card 已存在';
        END IF;
    EXCEPTION
        WHEN duplicate_function THEN
            RAISE WARNING '部分函数已存在';
        WHEN OTHERS THEN
            RAISE WARNING '创建脱敏函数失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 脱敏视图（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'users') THEN
            RAISE WARNING '表 users 不存在，无法创建脱敏视图';
            RETURN;
        END IF;

        IF NOT EXISTS (SELECT 1 FROM information_schema.views WHERE table_schema = 'public' AND table_name = 'users_masked') THEN
            CREATE VIEW users_masked AS
            SELECT
                id,
                username,
                mask_email(email) AS email,
                mask_phone(phone) AS phone,
                mask_id_card(id_card) AS id_card,
                department,
                created_at
            FROM users;
            RAISE NOTICE '脱敏视图 users_masked 创建成功';
        ELSE
            RAISE NOTICE '脱敏视图 users_masked 已存在';
        END IF;
    EXCEPTION
        WHEN undefined_table THEN
            RAISE WARNING '表 users 不存在';
        WHEN duplicate_table THEN
            RAISE WARNING '视图 users_masked 已存在';
        WHEN OTHERS THEN
            RAISE WARNING '创建视图失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 授权给开发/测试环境（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'dev_role') THEN
            RAISE WARNING '角色 dev_role 不存在，无法授权';
        ELSE
            BEGIN
                GRANT SELECT ON users_masked TO dev_role;
                RAISE NOTICE '已授权 dev_role 访问 users_masked 视图';
            EXCEPTION
                WHEN OTHERS THEN
                    RAISE WARNING '授权失败: %', SQLERRM;
            END;

            BEGIN
                REVOKE SELECT ON users FROM dev_role;
                RAISE NOTICE '已撤销 dev_role 对 users 表的访问权限';
            EXCEPTION
                WHEN OTHERS THEN
                    RAISE WARNING '撤销权限失败: %', SQLERRM;
            END;
        END IF;
    EXCEPTION
        WHEN undefined_object THEN
            RAISE WARNING '角色 dev_role 不存在';
        WHEN OTHERS THEN
            RAISE WARNING '操作失败: %', SQLERRM;
            RAISE;
    END;
END $$;

### 3.2 动态脱敏（anon扩展）

**安装postgresql_anonymizer**：

```bash
# Ubuntu/Debian
sudo apt-get install postgresql-17-anonymizer
```

**使用**：

```sql
-- 动态脱敏（anon扩展，带错误处理）
-- 创建扩展（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'anon') THEN
            CREATE EXTENSION IF NOT EXISTS anon CASCADE;
            RAISE NOTICE '扩展 anon 创建成功';
        ELSE
            RAISE NOTICE '扩展 anon 已存在';
        END IF;
    EXCEPTION
        WHEN duplicate_object THEN
            RAISE WARNING '扩展 anon 已存在';
        WHEN OTHERS THEN
            RAISE WARNING '创建扩展失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 初始化（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'anon') THEN
            RAISE WARNING '扩展 anon 未安装，无法初始化';
            RETURN;
        END IF;
        PERFORM anon.init();
        RAISE NOTICE 'anon扩展初始化成功';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '初始化失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 定义脱敏规则（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'users') THEN
            RAISE WARNING '表 users 不存在，无法定义脱敏规则';
            RETURN;
        END IF;

        IF NOT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'anon') THEN
            RAISE WARNING '扩展 anon 未安装，无法定义脱敏规则';
            RETURN;
        END IF;

        BEGIN
            SECURITY LABEL FOR anon ON COLUMN users.email
            IS 'MASKED WITH FUNCTION anon.fake_email()';
            RAISE NOTICE 'email列脱敏规则设置成功';
        EXCEPTION
            WHEN OTHERS THEN
                RAISE WARNING '设置email脱敏规则失败: %', SQLERRM;
        END;

        BEGIN
            SECURITY LABEL FOR anon ON COLUMN users.phone
            IS 'MASKED WITH FUNCTION anon.partial(phone, 2, $$****$$, 2)';
            RAISE NOTICE 'phone列脱敏规则设置成功';
        EXCEPTION
            WHEN OTHERS THEN
                RAISE WARNING '设置phone脱敏规则失败: %', SQLERRM;
        END;

        BEGIN
            SECURITY LABEL FOR anon ON COLUMN users.ssn
            IS 'MASKED WITH VALUE NULL';
            RAISE NOTICE 'ssn列脱敏规则设置成功';
        EXCEPTION
            WHEN OTHERS THEN
                RAISE WARNING '设置ssn脱敏规则失败: %', SQLERRM;
        END;

        BEGIN
            SECURITY LABEL FOR anon ON COLUMN users.salary
            IS 'MASKED WITH FUNCTION anon.random_int_between(30000, 150000)';
            RAISE NOTICE 'salary列脱敏规则设置成功';
        EXCEPTION
            WHEN OTHERS THEN
                RAISE WARNING '设置salary脱敏规则失败: %', SQLERRM;
        END;
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '定义脱敏规则失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 创建脱敏角色（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'masked_user') THEN
            CREATE ROLE masked_user;
            RAISE NOTICE '角色 masked_user 创建成功';
        ELSE
            RAISE NOTICE '角色 masked_user 已存在';
        END IF;

        IF NOT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'anon') THEN
            RAISE WARNING '扩展 anon 未安装，无法设置脱敏标签';
        ELSE
            BEGIN
                SECURITY LABEL FOR anon ON ROLE masked_user IS 'MASKED';
                RAISE NOTICE '角色 masked_user 的脱敏标签设置成功';
            EXCEPTION
                WHEN OTHERS THEN
                    RAISE WARNING '设置脱敏标签失败: %', SQLERRM;
            END;
        END IF;
    EXCEPTION
        WHEN duplicate_object THEN
            RAISE WARNING '角色 masked_user 已存在';
        WHEN OTHERS THEN
            RAISE WARNING '创建角色失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 测试（带错误处理和性能测试）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'users') THEN
            RAISE WARNING '表 users 不存在，无法测试';
            RETURN;
        END IF;

        IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'masked_user') THEN
            RAISE WARNING '角色 masked_user 不存在，无法测试';
            RETURN;
        END IF;

        RAISE NOTICE '开始测试脱敏功能';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '测试准备失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- SET ROLE masked_user;
-- EXPLAIN (ANALYZE, BUFFERS, TIMING)
-- SELECT email, phone, ssn, salary FROM users;
-- -- 结果：显示脱敏后的数据

-- RESET ROLE;
-- EXPLAIN (ANALYZE, BUFFERS, TIMING)
-- SELECT email, phone, ssn, salary FROM users;
-- -- 结果：显示真实数据
```

**批量脱敏导出**：

```sql
-- 批量脱敏导出（带错误处理）
-- 匿名化整个数据库（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'anon') THEN
            RAISE WARNING '扩展 anon 未安装，无法匿名化数据库';
            RETURN;
        END IF;
        RAISE NOTICE '开始匿名化整个数据库';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '操作准备失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- SELECT anon.anonymize_database();

-- 匿名化特定表（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'anon') THEN
            RAISE WARNING '扩展 anon 未安装，无法匿名化表';
            RETURN;
        END IF;

        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'users') THEN
            RAISE WARNING '表 users 不存在，无法匿名化';
            RETURN;
        END IF;
        RAISE NOTICE '开始匿名化表 users';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '操作准备失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- SELECT anon.anonymize_table('users');

-- 导出到CSV（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'anon') THEN
            RAISE WARNING '扩展 anon 未安装，无法导出';
            RETURN;
        END IF;

        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'users') THEN
            RAISE WARNING '表 users 不存在，无法导出';
            RETURN;
        END IF;
        RAISE NOTICE '导出命令: \copy (SELECT * FROM anon.anonymize_table_json(''users'')) TO ''users_masked.csv'' CSV HEADER;';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '操作准备失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- \copy (SELECT * FROM anon.anonymize_table_json('users')) TO 'users_masked.csv' CSV HEADER;
```

### 3.3 差分隐私

```sql
-- 添加噪声函数（满足epsilon-差分隐私，带完整错误处理）
CREATE OR REPLACE FUNCTION add_laplace_noise(value numeric, epsilon numeric DEFAULT 0.1)
RETURNS numeric AS $$
DECLARE
    sensitivity numeric := 1.0;
    scale numeric;
    u numeric;
    noise numeric;
BEGIN
    BEGIN
        -- 参数验证
        IF epsilon <= 0 OR epsilon > 1 THEN
            RAISE EXCEPTION 'epsilon必须在(0, 1]范围内，当前值: %', epsilon;
        END IF;

        IF value IS NULL THEN
            RETURN NULL;
        END IF;

        -- 计算scale
        BEGIN
            scale := sensitivity / epsilon;
        EXCEPTION
            WHEN division_by_zero THEN
                RAISE EXCEPTION 'epsilon不能为0';
            WHEN OTHERS THEN
                RAISE EXCEPTION '计算scale失败: %', SQLERRM;
        END;

        -- 生成Laplace噪声
        BEGIN
            u := random() - 0.5;
            noise := -scale * sign(u) * ln(1 - 2 * abs(u));
        EXCEPTION
            WHEN numeric_value_out_of_range THEN
                RAISE WARNING '噪声计算超出范围，使用默认值0';
                noise := 0;
            WHEN OTHERS THEN
                RAISE EXCEPTION '生成噪声失败: %', SQLERRM;
        END;

        -- 返回加噪后的值
        BEGIN
            RETURN value + noise;
        EXCEPTION
            WHEN numeric_value_out_of_range THEN
                RAISE WARNING '结果超出范围，返回原值';
                RETURN value;
            WHEN OTHERS THEN
                RAISE EXCEPTION '计算最终值失败: %', SQLERRM;
        END;
    EXCEPTION
        WHEN OTHERS THEN
            RAISE EXCEPTION 'add_laplace_noise执行失败: %', SQLERRM;
    END;
END;
$$ LANGUAGE plpgsql VOLATILE;

-- 使用示例：查询平均薪资（带隐私保护，带错误处理和性能测试）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'employees') THEN
            RAISE WARNING '表 employees 不存在，无法执行查询';
            RETURN;
        END IF;

        IF NOT EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'add_laplace_noise' AND pronamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public')) THEN
            RAISE WARNING '函数 add_laplace_noise 不存在，无法执行查询';
            RETURN;
        END IF;
        RAISE NOTICE '开始查询平均薪资（带差分隐私保护）';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '查询准备失败: %', SQLERRM;
            RAISE;
    END;
END $$;

EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT add_laplace_noise(AVG(salary)::numeric, 0.1) AS avg_salary_dp
FROM employees
WHERE department = 'engineering';
```

---

## 4. 安全加固实战

### 4.1 SSL/TLS加密

**配置服务器**（`postgresql.conf`）：

```conf
# SSL配置
ssl = on
ssl_cert_file = '/etc/postgresql/17/main/server.crt'
ssl_key_file = '/etc/postgresql/17/main/server.key'
ssl_ca_file = '/etc/postgresql/17/main/root.crt'

# 强制SSL
ssl_min_protocol_version = 'TLSv1.2'
ssl_ciphers = 'HIGH:MEDIUM:+3DES:!aNULL'
ssl_prefer_server_ciphers = on

# 客户端证书认证
ssl_ca_file = '/etc/postgresql/17/main/root.crt'
```

**配置pg_hba.conf**：

```conf
# 强制SSL连接
hostssl all all 0.0.0.0/0 scram-sha-256
hostssl all all ::/0 scram-sha-256

# 要求客户端证书
hostssl all all 0.0.0.0/0 cert clientcert=verify-full

# 特定用户必须使用SSL
hostssl admin all 0.0.0.0/0 scram-sha-256
host admin all 0.0.0.0/0 reject
```

**生成证书**：

```bash
# 1. 生成CA证书
openssl genrsa -out root.key 2048
openssl req -new -x509 -key root.key -out root.crt -days 3650

# 2. 生成服务器证书
openssl genrsa -out server.key 2048
openssl req -new -key server.key -out server.csr
openssl x509 -req -in server.csr -CA root.crt -CAkey root.key -CAcreateserial -out server.crt -days 365

# 3. 设置权限
chmod 600 server.key
chown postgres:postgres server.key server.crt root.crt

# 4. 测试连接
psql "host=localhost dbname=mydb sslmode=require"
```

### 4.2 数据加密（pgcrypto）

```sql
-- 数据加密（pgcrypto，带错误处理）
-- 创建扩展（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'pgcrypto') THEN
            CREATE EXTENSION pgcrypto;
            RAISE NOTICE '扩展 pgcrypto 创建成功';
        ELSE
            RAISE NOTICE '扩展 pgcrypto 已存在';
        END IF;
    EXCEPTION
        WHEN duplicate_object THEN
            RAISE WARNING '扩展 pgcrypto 已存在';
        WHEN OTHERS THEN
            RAISE WARNING '创建扩展失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 对称加密（AES，带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'pgcrypto') THEN
            RAISE WARNING '扩展 pgcrypto 未安装，无法使用加密功能';
            RETURN;
        END IF;

        IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'encrypted_data') THEN
            RAISE NOTICE '表 encrypted_data 已存在';
        ELSE
            CREATE TABLE encrypted_data (
                id serial PRIMARY KEY,
                data_encrypted bytea,
                key_id int NOT NULL
            );
            RAISE NOTICE '表 encrypted_data 创建成功';
        END IF;
    EXCEPTION
        WHEN duplicate_table THEN
            RAISE WARNING '表 encrypted_data 已存在';
        WHEN OTHERS THEN
            RAISE WARNING '创建表失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 加密插入（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'encrypted_data') THEN
            RAISE WARNING '表 encrypted_data 不存在，无法插入数据';
            RETURN;
        END IF;

        IF NOT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'pgcrypto') THEN
            RAISE WARNING '扩展 pgcrypto 未安装，无法加密';
            RETURN;
        END IF;
        RAISE NOTICE '开始插入加密数据';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '插入准备失败: %', SQLERRM;
            RAISE;
    END;
END $$;

BEGIN
    INSERT INTO encrypted_data (data_encrypted, key_id)
    VALUES (
        pgp_sym_encrypt('sensitive data', 'encryption-key'),
        1
    );
EXCEPTION
    WHEN OTHERS THEN
        RAISE WARNING '插入加密数据失败: %', SQLERRM;
        RAISE;
END;

-- 解密查询（带错误处理和性能测试）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'encrypted_data') THEN
            RAISE WARNING '表 encrypted_data 不存在，无法查询';
            RETURN;
        END IF;

        IF NOT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'pgcrypto') THEN
            RAISE WARNING '扩展 pgcrypto 未安装，无法解密';
            RETURN;
        END IF;
        RAISE NOTICE '开始查询并解密数据';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '查询准备失败: %', SQLERRM;
            RAISE;
    END;
END $$;

EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    id,
    pgp_sym_decrypt(data_encrypted, 'encryption-key') AS data_decrypted
FROM encrypted_data;

-- 非对称加密（RSA，带错误处理）
-- 生成密钥对（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'pgcrypto') THEN
            RAISE WARNING '扩展 pgcrypto 未安装，无法生成密钥';
            RETURN;
        END IF;
        RAISE NOTICE '开始生成密钥对';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '操作准备失败: %', SQLERRM;
            RAISE;
    END;
END $$;

EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    armor(gen_random_bytes(32)) AS encryption_key,
    armor(gen_random_bytes(32)) AS decryption_key;

-- 使用公钥加密（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'encrypted_data') THEN
            RAISE WARNING '表 encrypted_data 不存在，无法插入数据';
            RETURN;
        END IF;

        IF NOT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'pgcrypto') THEN
            RAISE WARNING '扩展 pgcrypto 未安装，无法加密';
            RETURN;
        END IF;
        RAISE NOTICE '使用公钥加密需要提供有效的PGP公钥';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '操作准备失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- INSERT INTO encrypted_data (data_encrypted, key_id)
-- VALUES (
--     pgp_pub_encrypt('sensitive data', dearmor('-----BEGIN PGP PUBLIC KEY BLOCK-----...')),
--     1
-- );

-- 使用私钥解密（带错误处理和性能测试）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'encrypted_data') THEN
            RAISE WARNING '表 encrypted_data 不存在，无法查询';
            RETURN;
        END IF;

        IF NOT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'pgcrypto') THEN
            RAISE WARNING '扩展 pgcrypto 未安装，无法解密';
            RETURN;
        END IF;
        RAISE NOTICE '使用私钥解密需要提供有效的PGP私钥';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '查询准备失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- EXPLAIN (ANALYZE, BUFFERS, TIMING)
-- SELECT
--     pgp_pub_decrypt(data_encrypted, dearmor('-----BEGIN PGP PRIVATE KEY BLOCK-----...'))
-- FROM encrypted_data;
```

**列级加密方案**：

```sql
-- 列级加密方案（带错误处理）
DO $$
BEGIN
    BEGIN
        IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'users_secure') THEN
            RAISE NOTICE '表 users_secure 已存在';
        ELSE
            CREATE TABLE users_secure (
                id serial PRIMARY KEY,
                username text NOT NULL,
                email_encrypted bytea,      -- 加密存储
                phone_encrypted bytea,       -- 加密存储
                ssn_encrypted bytea,         -- 加密存储
                key_id int NOT NULL,         -- 密钥标识
                created_at timestamptz DEFAULT now()
            );
            RAISE NOTICE '表 users_secure 创建成功';
        END IF;
    EXCEPTION
        WHEN duplicate_table THEN
            RAISE WARNING '表 users_secure 已存在';
        WHEN OTHERS THEN
            RAISE WARNING '创建表失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 加密辅助函数（带完整错误处理）
CREATE OR REPLACE FUNCTION encrypt_column(data text, key_id int)
RETURNS bytea AS $$
DECLARE
    encryption_key text;
BEGIN
    BEGIN
        -- 参数验证
        IF data IS NULL THEN
            RETURN NULL;
        END IF;

        IF key_id IS NULL OR key_id <= 0 THEN
            RAISE EXCEPTION 'key_id必须为正整数，当前值: %', key_id;
        END IF;

        -- 检查扩展
        IF NOT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'pgcrypto') THEN
            RAISE EXCEPTION '扩展 pgcrypto 未安装，无法加密';
        END IF;

        -- 从密钥管理表获取密钥（实际应该从KMS）
        BEGIN
            SELECT key_value INTO encryption_key
            FROM encryption_keys
            WHERE key_id = encrypt_column.key_id
              AND is_active = true;

            IF encryption_key IS NULL THEN
                RAISE EXCEPTION '密钥 ID % 不存在或未激活', encrypt_column.key_id;
            END IF;
        EXCEPTION
            WHEN no_data_found THEN
                RAISE EXCEPTION '密钥 ID % 不存在', encrypt_column.key_id;
            WHEN OTHERS THEN
                RAISE EXCEPTION '获取密钥失败: %', SQLERRM;
        END;

        -- 加密数据
        BEGIN
            RETURN pgp_sym_encrypt(data, encryption_key);
        EXCEPTION
            WHEN OTHERS THEN
                RAISE EXCEPTION '加密失败: %', SQLERRM;
        END;
    EXCEPTION
        WHEN OTHERS THEN
            RAISE EXCEPTION 'encrypt_column执行失败: %', SQLERRM;
    END;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 解密辅助函数（带完整错误处理）
CREATE OR REPLACE FUNCTION decrypt_column(data_encrypted bytea, key_id int)
RETURNS text AS $$
DECLARE
    decryption_key text;
BEGIN
    BEGIN
        -- 参数验证
        IF data_encrypted IS NULL THEN
            RETURN NULL;
        END IF;

        IF key_id IS NULL OR key_id <= 0 THEN
            RAISE EXCEPTION 'key_id必须为正整数，当前值: %', key_id;
        END IF;

        -- 检查扩展
        IF NOT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'pgcrypto') THEN
            RAISE EXCEPTION '扩展 pgcrypto 未安装，无法解密';
        END IF;

        -- 获取解密密钥
        BEGIN
            SELECT key_value INTO decryption_key
            FROM encryption_keys
            WHERE key_id = decrypt_column.key_id;

            IF decryption_key IS NULL THEN
                RAISE EXCEPTION '密钥 ID % 不存在', decrypt_column.key_id;
            END IF;
        EXCEPTION
            WHEN no_data_found THEN
                RAISE EXCEPTION '密钥 ID % 不存在', decrypt_column.key_id;
            WHEN OTHERS THEN
                RAISE EXCEPTION '获取密钥失败: %', SQLERRM;
        END;

        -- 解密数据
        BEGIN
            RETURN pgp_sym_decrypt(data_encrypted, decryption_key);
        EXCEPTION
            WHEN invalid_text_representation THEN
                RAISE EXCEPTION '解密失败：数据格式错误或密钥不正确';
            WHEN OTHERS THEN
                RAISE EXCEPTION '解密失败: %', SQLERRM;
        END;
    EXCEPTION
        WHEN OTHERS THEN
            RAISE EXCEPTION 'decrypt_column执行失败: %', SQLERRM;
    END;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 插入数据（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'users_secure') THEN
            RAISE WARNING '表 users_secure 不存在，无法插入数据';
            RETURN;
        END IF;

        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'encryption_keys') THEN
            RAISE WARNING '表 encryption_keys 不存在，无法插入数据';
            RETURN;
        END IF;

        IF NOT EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'encrypt_column' AND pronamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public')) THEN
            RAISE WARNING '函数 encrypt_column 不存在，无法插入数据';
            RETURN;
        END IF;
        RAISE NOTICE '开始插入加密数据';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '插入准备失败: %', SQLERRM;
            RAISE;
    END;
END $$;

BEGIN
    INSERT INTO users_secure (username, email_encrypted, phone_encrypted, key_id)
    VALUES (
        'alice',
        encrypt_column('alice@example.com', 1),
        encrypt_column('13800138000', 1),
        1
    );
EXCEPTION
    WHEN foreign_key_violation THEN
        RAISE WARNING '外键约束失败，请确保密钥ID存在';
        RAISE;
    WHEN OTHERS THEN
        RAISE WARNING '插入数据失败: %', SQLERRM;
        RAISE;
END;

-- 查询数据（带错误处理和性能测试）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'users_secure') THEN
            RAISE WARNING '表 users_secure 不存在，无法查询';
            RETURN;
        END IF;

        IF NOT EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'decrypt_column' AND pronamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public')) THEN
            RAISE WARNING '函数 decrypt_column 不存在，无法查询';
            RETURN;
        END IF;
        RAISE NOTICE '开始查询并解密数据';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '查询准备失败: %', SQLERRM;
            RAISE;
    END;
END $$;

EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    id,
    username,
    decrypt_column(email_encrypted, key_id) AS email,
    decrypt_column(phone_encrypted, key_id) AS phone
FROM users_secure;
```

### 4.3 密钥轮换

```sql
-- 密钥管理表（带错误处理）
DO $$
BEGIN
    BEGIN
        IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'encryption_keys') THEN
            RAISE NOTICE '表 encryption_keys 已存在';
        ELSE
            CREATE TABLE encryption_keys (
                key_id serial PRIMARY KEY,
                key_version int NOT NULL,
                key_value text NOT NULL,  -- 实际应该存在KMS中
                is_active boolean DEFAULT true,
                created_at timestamptz DEFAULT now(),
                expires_at timestamptz
            );
            RAISE NOTICE '表 encryption_keys 创建成功';
        END IF;
    EXCEPTION
        WHEN duplicate_table THEN
            RAISE WARNING '表 encryption_keys 已存在';
        WHEN OTHERS THEN
            RAISE WARNING '创建表失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 密钥轮换函数（带完整错误处理）
CREATE OR REPLACE FUNCTION rotate_encryption_key()
RETURNS void AS $$
DECLARE
    old_key_id int;
    new_key_id int;
    old_key text;
    new_key text;
    affected_rows int;
BEGIN
    BEGIN
        -- 检查扩展
        IF NOT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'pgcrypto') THEN
            RAISE EXCEPTION '扩展 pgcrypto 未安装，无法轮换密钥';
        END IF;

        -- 检查表是否存在
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'encryption_keys') THEN
            RAISE EXCEPTION '表 encryption_keys 不存在';
        END IF;

        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'users_secure') THEN
            RAISE EXCEPTION '表 users_secure 不存在';
        END IF;

        -- 获取当前活跃密钥
        BEGIN
            SELECT key_id, key_value INTO old_key_id, old_key
            FROM encryption_keys
            WHERE is_active = true
            ORDER BY key_id DESC
            LIMIT 1;

            IF old_key_id IS NULL THEN
                RAISE EXCEPTION '未找到活跃的密钥';
            END IF;
        EXCEPTION
            WHEN no_data_found THEN
                RAISE EXCEPTION '未找到活跃的密钥';
            WHEN OTHERS THEN
                RAISE EXCEPTION '获取当前密钥失败: %', SQLERRM;
        END;

        -- 生成新密钥
        BEGIN
            INSERT INTO encryption_keys (key_version, key_value, is_active)
            VALUES (
                COALESCE((SELECT max(key_version) FROM encryption_keys), 0) + 1,
                encode(gen_random_bytes(32), 'base64'),
                true
            )
            RETURNING key_id, key_value INTO new_key_id, new_key;

            IF new_key_id IS NULL THEN
                RAISE EXCEPTION '生成新密钥失败';
            END IF;
        EXCEPTION
            WHEN OTHERS THEN
                RAISE EXCEPTION '生成新密钥失败: %', SQLERRM;
        END;

        -- 重新加密所有数据
        BEGIN
            UPDATE users_secure
            SET
                email_encrypted = pgp_sym_encrypt(
                    pgp_sym_decrypt(email_encrypted, old_key),
                    new_key
                ),
                phone_encrypted = pgp_sym_encrypt(
                    pgp_sym_decrypt(phone_encrypted, old_key),
                    new_key
                ),
                key_id = new_key_id
            WHERE key_id = old_key_id;

            GET DIAGNOSTICS affected_rows = ROW_COUNT;
            RAISE NOTICE '重新加密了 % 行数据', affected_rows;
        EXCEPTION
            WHEN invalid_text_representation THEN
                RAISE EXCEPTION '解密失败：数据格式错误或密钥不正确';
            WHEN OTHERS THEN
                RAISE EXCEPTION '重新加密数据失败: %', SQLERRM;
        END;

        -- 停用旧密钥
        BEGIN
            UPDATE encryption_keys
            SET is_active = false
            WHERE key_id = old_key_id;
        EXCEPTION
            WHEN OTHERS THEN
                RAISE WARNING '停用旧密钥失败: %', SQLERRM;
                -- 继续执行，不中断
        END;

        RAISE NOTICE '密钥轮换完成: % -> %', old_key_id, new_key_id;
    EXCEPTION
        WHEN OTHERS THEN
            RAISE EXCEPTION 'rotate_encryption_key执行失败: %', SQLERRM;
    END;
END;
$$ LANGUAGE plpgsql;

-- 定期轮换（每季度，带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'pg_cron') THEN
            RAISE WARNING '扩展 pg_cron 未安装，无法创建定期任务';
            RAISE NOTICE '需要先安装扩展: CREATE EXTENSION pg_cron;';
        ELSE
            BEGIN
                PERFORM cron.schedule('rotate_key', '0 0 1 */3 *', 'SELECT rotate_encryption_key()');
                RAISE NOTICE '定期任务 rotate_key 创建成功（每季度轮换）';
            EXCEPTION
                WHEN duplicate_object THEN
                    RAISE WARNING '定期任务 rotate_key 已存在';
                WHEN OTHERS THEN
                    RAISE WARNING '创建定期任务失败: %', SQLERRM;
                    RAISE;
            END;
        END IF;
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '操作失败: %', SQLERRM;
            RAISE;
    END;
END $$;
```

---

## 5. 渗透测试

### 5.1 SQL注入测试

**测试用例**：

```sql
-- SQL注入测试（带完整错误处理）
-- 测试1：基础SQL注入（演示不安全做法，带错误处理）
DO $$
DECLARE
    malicious_input text := $$' OR '1'='1$$;
    result text;
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'users') THEN
            RAISE WARNING '表 users 不存在，无法执行SQL注入测试';
            RETURN;
        END IF;

        RAISE WARNING '警告：以下是不安全的查询示例，永远不要在生产环境中使用';
        RAISE NOTICE '开始SQL注入测试（不安全示例）';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '测试准备失败: %', SQLERRM;
            RAISE;
    END;

    BEGIN
        -- 不安全的查询（永远不要这样做）
        EXECUTE 'SELECT username FROM users WHERE username = ''' || malicious_input || '''';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE NOTICE 'SQL注入被阻止: %', SQLERRM;
    END;
END $$;

-- 测试2：使用参数化查询（安全，带错误处理）
DO $$
DECLARE
    malicious_input text := $$' OR '1'='1$$;
    result text;
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'users') THEN
            RAISE WARNING '表 users 不存在，无法执行参数化查询测试';
            RETURN;
        END IF;
        RAISE NOTICE '开始参数化查询测试（安全示例）';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '测试准备失败: %', SQLERRM;
            RAISE;
    END;

    BEGIN
        EXECUTE 'SELECT username FROM users WHERE username = $1'
        INTO result
        USING malicious_input;

        IF result IS NULL THEN
            RAISE NOTICE '结果: NULL（未找到匹配用户，SQL注入被阻止）';
        ELSE
            RAISE NOTICE '结果: %（正常查询结果，SQL注入被阻止）', result;
        END IF;
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '参数化查询执行失败: %', SQLERRM;
            RAISE;
    END;
END $$;
```

**SQL注入防护清单**：

```sql
-- SQL注入防护清单（带错误处理）
-- ✅ 安全：使用参数化查询（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'users') THEN
            RAISE WARNING '表 users 不存在，无法创建预编译语句';
            RETURN;
        END IF;

        BEGIN
            PREPARE get_user(text) AS
            SELECT * FROM users WHERE username = $1;
            RAISE NOTICE '预编译语句 get_user 创建成功';
        EXCEPTION
            WHEN duplicate_prepared_statement THEN
                RAISE NOTICE '预编译语句 get_user 已存在';
            WHEN OTHERS THEN
                RAISE WARNING '创建预编译语句失败: %', SQLERRM;
        END;
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '操作失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- EXECUTE get_user('alice');

-- ✅ 安全：使用quote_literal（带错误处理）
DO $$
DECLARE
    user_input text := 'alice';
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'users') THEN
            RAISE WARNING '表 users 不存在，无法执行查询';
            RETURN;
        END IF;
        RAISE NOTICE '使用quote_literal进行安全查询';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '操作准备失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- EXECUTE 'SELECT * FROM users WHERE username = ' || quote_literal(user_input);

-- ✅ 安全：使用quote_ident（标识符，带错误处理）
DO $$
DECLARE
    table_name text := 'users';
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = table_name) THEN
            RAISE WARNING '表 % 不存在，无法执行查询', table_name;
            RETURN;
        END IF;
        RAISE NOTICE '使用quote_ident进行安全查询';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '操作准备失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- EXECUTE 'SELECT * FROM ' || quote_ident(table_name);

-- ✅ 安全：使用format with %L (literal) 和 %I (identifier，带错误处理)
DO $$
DECLARE
    table_name text := 'users';
    user_input text := 'alice';
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = table_name) THEN
            RAISE WARNING '表 % 不存在，无法执行查询', table_name;
            RETURN;
        END IF;
        RAISE NOTICE '使用format进行安全查询';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '操作准备失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- EXECUTE format('SELECT * FROM %I WHERE username = %L', table_name, user_input);

-- ❌ 不安全：字符串拼接（演示，带警告）
DO $$
DECLARE
    user_input text := $$' OR '1'='1$$;
BEGIN
    BEGIN
        RAISE WARNING '警告：以下是不安全的字符串拼接示例，永远不要在生产环境中使用';
        RAISE NOTICE '演示不安全的查询（仅用于测试）';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '操作准备失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- EXECUTE 'SELECT * FROM users WHERE username = ''' || user_input || '''';
```

### 5.2 权限提升测试

```sql
-- 权限提升测试（带错误处理和性能测试）
-- 测试1：检查SECURITY DEFINER函数（带错误处理和性能测试）
DO $$
BEGIN
    BEGIN
        RAISE NOTICE '开始检查SECURITY DEFINER函数';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '检查准备失败: %', SQLERRM;
            RAISE;
    END;
END $$;

EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    n.nspname AS schema,
    p.proname AS function,
    pg_get_userbyid(p.proowner) AS owner,
    p.prosecdef AS security_definer
FROM pg_proc p
JOIN pg_namespace n ON p.pronamespace = n.oid
WHERE p.prosecdef = true
  AND n.nspname NOT IN ('pg_catalog', 'information_schema')
ORDER BY schema, function;

-- 测试2：检查危险的GRANT（带错误处理和性能测试）
DO $$
BEGIN
    BEGIN
        RAISE NOTICE '开始检查危险的GRANT权限';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '检查准备失败: %', SQLERRM;
            RAISE;
    END;
END $$;

EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    grantee,
    table_schema,
    table_name,
    privilege_type
FROM information_schema.table_privileges
WHERE grantee = 'PUBLIC'
   OR privilege_type IN ('INSERT', 'UPDATE', 'DELETE')
ORDER BY table_schema, table_name;

-- 测试3：检查超级用户（带错误处理和性能测试）
DO $$
BEGIN
    BEGIN
        RAISE NOTICE '开始检查超级用户';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '检查准备失败: %', SQLERRM;
            RAISE;
    END;
END $$;

EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    rolname,
    rolsuper,
    rolinherit,
    rolcreaterole,
    rolcreatedb
FROM pg_roles
WHERE rolsuper = true;
```

### 5.3 DoS攻击测试

```sql
-- DoS攻击测试（带错误处理）
-- 测试1：资源耗尽攻击（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'test_user') THEN
            RAISE WARNING '角色 test_user 不存在，无法设置资源限制';
        ELSE
            BEGIN
                ALTER ROLE test_user SET statement_timeout = '30s';
                ALTER ROLE test_user SET lock_timeout = '10s';
                ALTER ROLE test_user SET idle_in_transaction_session_timeout = '60s';
                RAISE NOTICE '角色 test_user 的资源限制设置成功';
            EXCEPTION
                WHEN OTHERS THEN
                    RAISE WARNING '设置资源限制失败: %', SQLERRM;
                    RAISE;
            END;
        END IF;
    EXCEPTION
        WHEN undefined_object THEN
            RAISE WARNING '角色 test_user 不存在';
        WHEN OTHERS THEN
            RAISE WARNING '操作失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 测试2：连接耗尽（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'test_user') THEN
            RAISE WARNING '角色 test_user 不存在，无法设置连接限制';
        ELSE
            BEGIN
                ALTER ROLE test_user CONNECTION LIMIT 10;
                RAISE NOTICE '角色 test_user 的连接限制设置成功（最多10个连接）';
            EXCEPTION
                WHEN OTHERS THEN
                    RAISE WARNING '设置连接限制失败: %', SQLERRM;
                    RAISE;
            END;
        END IF;
    EXCEPTION
        WHEN undefined_object THEN
            RAISE WARNING '角色 test_user 不存在';
        WHEN OTHERS THEN
            RAISE WARNING '操作失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 测试3：临时文件耗尽（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = 'testdb') THEN
            RAISE WARNING '数据库 testdb 不存在，无法设置临时文件限制';
        ELSE
            BEGIN
                ALTER DATABASE testdb SET temp_file_limit = '1GB';
                RAISE NOTICE '数据库 testdb 的临时文件限制设置成功（1GB）';
            EXCEPTION
                WHEN OTHERS THEN
                    RAISE WARNING '设置临时文件限制失败: %', SQLERRM;
                    RAISE;
            END;
        END IF;
    EXCEPTION
        WHEN undefined_object THEN
            RAISE WARNING '数据库 testdb 不存在';
        WHEN OTHERS THEN
            RAISE WARNING '操作失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 测试4：检查慢查询（带错误处理和性能测试）
DO $$
BEGIN
    BEGIN
        RAISE NOTICE '开始检查慢查询（执行时间超过10秒）';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '检查准备失败: %', SQLERRM;
            RAISE;
    END;
END $$;

EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    pid,
    usename,
    datname,
    state,
    query_start,
    now() - query_start AS duration,
    query
FROM pg_stat_activity
WHERE state != 'idle'
  AND now() - query_start > interval '10 seconds'
ORDER BY duration DESC;
```

---

## 6. 合规性检查

### 6.1 GDPR合规

```sql
-- 创建数据主体权限管理表（带错误处理）
DO $$
BEGIN
    BEGIN
        IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'data_subject_requests') THEN
            RAISE NOTICE '表 data_subject_requests 已存在';
        ELSE
            CREATE TABLE data_subject_requests (
                request_id serial PRIMARY KEY,
                user_id int NOT NULL,
                request_type text CHECK (request_type IN ('access', 'rectification', 'erasure', 'portability', 'restriction')),
                request_status text CHECK (request_status IN ('pending', 'processing', 'completed', 'rejected')),
                requested_at timestamptz DEFAULT now(),
                completed_at timestamptz,
                notes text
            );
            RAISE NOTICE '表 data_subject_requests 创建成功';
        END IF;
    EXCEPTION
        WHEN duplicate_table THEN
            RAISE WARNING '表 data_subject_requests 已存在';
        WHEN OTHERS THEN
            RAISE WARNING '创建表失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 数据导出（Right to Access，带完整错误处理）
CREATE OR REPLACE FUNCTION export_user_data(p_user_id int)
RETURNS jsonb AS $$
DECLARE
    result jsonb;
BEGIN
    BEGIN
        -- 参数验证
        IF p_user_id IS NULL OR p_user_id <= 0 THEN
            RAISE EXCEPTION 'user_id必须为正整数，当前值: %', p_user_id;
        END IF;

        -- 检查用户是否存在
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'users') THEN
            RAISE EXCEPTION '表 users 不存在';
        END IF;

        IF NOT EXISTS (SELECT 1 FROM users WHERE id = p_user_id) THEN
            RAISE EXCEPTION '用户 ID % 不存在', p_user_id;
        END IF;

        -- 构建导出数据
        BEGIN
            SELECT jsonb_build_object(
                'user_info', (SELECT row_to_json(u) FROM users u WHERE id = p_user_id),
                'orders', COALESCE((SELECT jsonb_agg(row_to_json(o)) FROM orders o WHERE user_id = p_user_id), '[]'::jsonb),
                'payments', COALESCE((SELECT jsonb_agg(row_to_json(p)) FROM payments p WHERE user_id = p_user_id), '[]'::jsonb),
                'audit_log', COALESCE((SELECT jsonb_agg(row_to_json(a)) FROM audit_log a WHERE user_name = (SELECT username FROM users WHERE id = p_user_id)), '[]'::jsonb)
            ) INTO result;

            IF result IS NULL THEN
                RAISE EXCEPTION '导出数据失败：结果为空';
            END IF;
        EXCEPTION
            WHEN OTHERS THEN
                RAISE EXCEPTION '构建导出数据失败: %', SQLERRM;
        END;

        RETURN result;
    EXCEPTION
        WHEN OTHERS THEN
            RAISE EXCEPTION 'export_user_data执行失败: %', SQLERRM;
    END;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 数据删除（Right to Erasure，带完整错误处理）
CREATE OR REPLACE FUNCTION erase_user_data(p_user_id int)
RETURNS void AS $$
DECLARE
    affected_rows INTEGER;
BEGIN
    BEGIN
        -- 参数验证
        IF p_user_id IS NULL OR p_user_id <= 0 THEN
            RAISE EXCEPTION 'user_id必须为正整数，当前值: %', p_user_id;
        END IF;

        -- 检查表是否存在
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'data_subject_requests') THEN
            RAISE EXCEPTION '表 data_subject_requests 不存在';
        END IF;

        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'users') THEN
            RAISE EXCEPTION '表 users 不存在';
        END IF;

        -- 检查用户是否存在
        IF NOT EXISTS (SELECT 1 FROM users WHERE id = p_user_id) THEN
            RAISE EXCEPTION '用户 ID % 不存在', p_user_id;
        END IF;

        -- 记录删除请求
        BEGIN
            INSERT INTO data_subject_requests (user_id, request_type, request_status)
            VALUES (p_user_id, 'erasure', 'processing');
        EXCEPTION
            WHEN OTHERS THEN
                RAISE WARNING '记录删除请求失败: %', SQLERRM;
                -- 继续执行，不中断
        END;

        -- 删除或匿名化数据
        BEGIN
            -- 删除可删除的数据
            IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'user_sessions') THEN
                DELETE FROM user_sessions WHERE user_id = p_user_id;
                GET DIAGNOSTICS affected_rows = ROW_COUNT;
                RAISE NOTICE '删除了 % 条 user_sessions 记录', affected_rows;
            END IF;

            IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'user_preferences') THEN
                DELETE FROM user_preferences WHERE user_id = p_user_id;
                GET DIAGNOSTICS affected_rows = ROW_COUNT;
                RAISE NOTICE '删除了 % 条 user_preferences 记录', affected_rows;
            END IF;

            -- 匿名化必须保留的数据（如订单记录）
            IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'orders') THEN
                UPDATE orders
                SET
                    user_email = 'deleted@example.com',
                    user_phone = NULL,
                    billing_address = 'DELETED'
                WHERE user_id = p_user_id;
                GET DIAGNOSTICS affected_rows = ROW_COUNT;
                RAISE NOTICE '匿名化了 % 条 orders 记录', affected_rows;
            END IF;

            -- 删除用户主记录
            DELETE FROM users WHERE id = p_user_id;
            GET DIAGNOSTICS affected_rows = ROW_COUNT;
            IF affected_rows = 0 THEN
                RAISE WARNING '未删除任何用户记录';
            ELSE
                RAISE NOTICE '删除了 % 条用户记录', affected_rows;
            END IF;

            -- 更新请求状态
            UPDATE data_subject_requests
            SET request_status = 'completed', completed_at = now()
            WHERE user_id = p_user_id AND request_type = 'erasure';
        EXCEPTION
            WHEN OTHERS THEN
                UPDATE data_subject_requests
                SET request_status = 'rejected', notes = SQLERRM
                WHERE user_id = p_user_id AND request_type = 'erasure';
                RAISE EXCEPTION '删除或匿名化数据失败: %', SQLERRM;
        END;
    EXCEPTION
        WHEN OTHERS THEN
            RAISE EXCEPTION 'erase_user_data执行失败: %', SQLERRM;
    END;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
```

### 6.2 数据保留策略

```sql
-- 数据保留策略表（带错误处理）
DO $$
BEGIN
    BEGIN
        IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'retention_policies') THEN
            RAISE NOTICE '表 retention_policies 已存在';
        ELSE
            CREATE TABLE retention_policies (
                policy_id serial PRIMARY KEY,
                table_name text NOT NULL,
                retention_period interval NOT NULL,
                action text CHECK (action IN ('delete', 'archive', 'anonymize')),
                is_active boolean DEFAULT true
            );
            RAISE NOTICE '表 retention_policies 创建成功';
        END IF;
    EXCEPTION
        WHEN duplicate_table THEN
            RAISE WARNING '表 retention_policies 已存在';
        WHEN OTHERS THEN
            RAISE WARNING '创建表失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 插入策略（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'retention_policies') THEN
            RAISE EXCEPTION '表 retention_policies 不存在';
        END IF;

        BEGIN
            INSERT INTO retention_policies (table_name, retention_period, action) VALUES
                ('audit_log', '7 years', 'archive'),
                ('user_sessions', '90 days', 'delete'),
                ('temp_data', '7 days', 'delete'),
                ('orders', '10 years', 'anonymize')
            ON CONFLICT DO NOTHING;
            RAISE NOTICE '保留策略插入成功';
        EXCEPTION
            WHEN OTHERS THEN
                RAISE WARNING '插入策略失败: %', SQLERRM;
                RAISE;
        END;
    EXCEPTION
        WHEN undefined_table THEN
            RAISE EXCEPTION '表 retention_policies 不存在';
        WHEN OTHERS THEN
            RAISE EXCEPTION '操作失败: %', SQLERRM;
    END;
END $$;

-- 执行保留策略函数（带完整错误处理）
CREATE OR REPLACE FUNCTION apply_retention_policy()
RETURNS TABLE(table_name text, action text, rows_affected bigint) AS $$
DECLARE
    policy record;
    cutoff_date timestamptz;
    rows_count bigint;
BEGIN
    BEGIN
        -- 检查表是否存在
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'retention_policies') THEN
            RAISE EXCEPTION '表 retention_policies 不存在';
        END IF;

        FOR policy IN
            SELECT * FROM retention_policies WHERE is_active = true
        LOOP
            BEGIN
                cutoff_date := now() - policy.retention_period;

                -- 检查目标表是否存在
                IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = policy.table_name) THEN
                    RAISE WARNING '表 % 不存在，跳过策略', policy.table_name;
                    CONTINUE;
                END IF;

                IF policy.action = 'delete' THEN
                    BEGIN
                        EXECUTE format(
                            'DELETE FROM %I WHERE created_at < $1',
                            policy.table_name
                        ) USING cutoff_date;
                        GET DIAGNOSTICS rows_count = ROW_COUNT;
                        RAISE NOTICE '表 %: 删除了 % 行', policy.table_name, rows_count;
                    EXCEPTION
                        WHEN OTHERS THEN
                            RAISE WARNING '删除表 % 的数据失败: %', policy.table_name, SQLERRM;
                            rows_count := 0;
                    END;

                ELSIF policy.action = 'archive' THEN
                    BEGIN
                        -- 检查归档表是否存在
                        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = policy.table_name || '_archive') THEN
                            RAISE WARNING '归档表 %_archive 不存在，跳过归档', policy.table_name;
                            CONTINUE;
                        END IF;

                        -- 移动到归档表
                        EXECUTE format(
                            'INSERT INTO %I_archive SELECT * FROM %I WHERE created_at < $1',
                            policy.table_name, policy.table_name
                        ) USING cutoff_date;

                        EXECUTE format(
                            'DELETE FROM %I WHERE created_at < $1',
                            policy.table_name
                        ) USING cutoff_date;
                        GET DIAGNOSTICS rows_count = ROW_COUNT;
                        RAISE NOTICE '表 %: 归档了 % 行', policy.table_name, rows_count;
                    EXCEPTION
                        WHEN OTHERS THEN
                            RAISE WARNING '归档表 % 的数据失败: %', policy.table_name, SQLERRM;
                            rows_count := 0;
                    END;

                ELSIF policy.action = 'anonymize' THEN
                    BEGIN
                        EXECUTE format(
                            'UPDATE %I SET email = ''deleted@example.com'', phone = NULL WHERE created_at < $1',
                            policy.table_name
                        ) USING cutoff_date;
                        GET DIAGNOSTICS rows_count = ROW_COUNT;
                        RAISE NOTICE '表 %: 匿名化了 % 行', policy.table_name, rows_count;
                    EXCEPTION
                        WHEN OTHERS THEN
                            RAISE WARNING '匿名化表 % 的数据失败: %', policy.table_name, SQLERRM;
                            rows_count := 0;
                    END;
                END IF;

                RETURN QUERY SELECT policy.table_name, policy.action, rows_count;
            EXCEPTION
                WHEN OTHERS THEN
                    RAISE WARNING '处理策略 % 失败: %', policy.table_name, SQLERRM;
                    RETURN QUERY SELECT policy.table_name, policy.action, 0::bigint;
            END;
        END LOOP;
    EXCEPTION
        WHEN OTHERS THEN
            RAISE EXCEPTION 'apply_retention_policy执行失败: %', SQLERRM;
    END;
END;
$$ LANGUAGE plpgsql;

-- 定期执行（每天凌晨3点，带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'pg_cron') THEN
            RAISE WARNING '扩展 pg_cron 未安装，无法创建定期任务';
            RAISE NOTICE '需要先安装扩展: CREATE EXTENSION pg_cron;';
        ELSE
            BEGIN
                PERFORM cron.schedule('apply_retention', '0 3 * * *', 'SELECT apply_retention_policy()');
                RAISE NOTICE '定期任务 apply_retention 创建成功（每天凌晨3点执行）';
            EXCEPTION
                WHEN duplicate_object THEN
                    RAISE WARNING '定期任务 apply_retention 已存在';
                WHEN OTHERS THEN
                    RAISE WARNING '创建定期任务失败: %', SQLERRM;
                    RAISE;
            END;
        END IF;
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '操作失败: %', SQLERRM;
            RAISE;
    END;
END $$;
```

---

## 7. 完整实战案例

### 7.1 案例：多租户SaaS安全方案

**需求**：

- 1000+租户，完全数据隔离
- 每个租户有自己的用户和权限
- 审计所有数据访问
- 支持数据导出和删除（GDPR）

**完整实现**：

```sql
-- 1. 租户和用户表（带错误处理）
DO $$
BEGIN
    BEGIN
        IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'tenants') THEN
            RAISE NOTICE '表 tenants 已存在';
        ELSE
            CREATE TABLE tenants (
                tenant_id serial PRIMARY KEY,
                tenant_name text UNIQUE NOT NULL,
                is_active boolean DEFAULT true,
                created_at timestamptz DEFAULT now()
            );
            RAISE NOTICE '表 tenants 创建成功';
        END IF;
    EXCEPTION
        WHEN duplicate_table THEN
            RAISE WARNING '表 tenants 已存在';
        WHEN OTHERS THEN
            RAISE WARNING '创建表失败: %', SQLERRM;
            RAISE;
    END;
END $$;

DO $$
BEGIN
    BEGIN
        IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'users') THEN
            RAISE NOTICE '表 users 已存在';
        ELSE
            IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'tenants') THEN
                RAISE EXCEPTION '表 tenants 不存在，无法创建外键约束';
            END IF;

            CREATE TABLE users (
                user_id serial PRIMARY KEY,
                tenant_id int NOT NULL REFERENCES tenants(tenant_id),
                username text NOT NULL,
                email text NOT NULL,
                role text CHECK (role IN ('admin', 'user', 'readonly')),
                is_active boolean DEFAULT true,
                created_at timestamptz DEFAULT now(),
                UNIQUE(tenant_id, username)
            );
            RAISE NOTICE '表 users 创建成功';
        END IF;
    EXCEPTION
        WHEN duplicate_table THEN
            RAISE WARNING '表 users 已存在';
        WHEN foreign_key_violation THEN
            RAISE WARNING '外键约束失败，请确保表 tenants 存在';
        WHEN OTHERS THEN
            RAISE WARNING '创建表失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 2. 业务表（所有表都有tenant_id，带错误处理）
DO $$
BEGIN
    BEGIN
        IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'projects') THEN
            RAISE NOTICE '表 projects 已存在';
        ELSE
            IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'tenants') OR
               NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'users') THEN
                RAISE EXCEPTION '表 tenants 或 users 不存在，无法创建外键约束';
            END IF;

            CREATE TABLE projects (
                project_id serial PRIMARY KEY,
                tenant_id int NOT NULL REFERENCES tenants(tenant_id),
                project_name text NOT NULL,
                owner_id int NOT NULL REFERENCES users(user_id),
                created_at timestamptz DEFAULT now()
            );
            RAISE NOTICE '表 projects 创建成功';
        END IF;
    EXCEPTION
        WHEN duplicate_table THEN
            RAISE WARNING '表 projects 已存在';
        WHEN foreign_key_violation THEN
            RAISE WARNING '外键约束失败，请确保表 tenants 和 users 存在';
        WHEN OTHERS THEN
            RAISE WARNING '创建表失败: %', SQLERRM;
            RAISE;
    END;
END $$;

DO $$
BEGIN
    BEGIN
        IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'tasks') THEN
            RAISE NOTICE '表 tasks 已存在';
        ELSE
            IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'projects') THEN
                RAISE EXCEPTION '表 projects 不存在，无法创建外键约束';
            END IF;

            CREATE TABLE tasks (
                task_id serial PRIMARY KEY,
                tenant_id int NOT NULL REFERENCES tenants(tenant_id),
                project_id int NOT NULL REFERENCES projects(project_id),
                assignee_id int REFERENCES users(user_id),
                task_title text NOT NULL,
                task_status text,
                created_at timestamptz DEFAULT now()
            );
            RAISE NOTICE '表 tasks 创建成功';
        END IF;
    EXCEPTION
        WHEN duplicate_table THEN
            RAISE WARNING '表 tasks 已存在';
        WHEN foreign_key_violation THEN
            RAISE WARNING '外键约束失败，请确保表 projects 存在';
        WHEN OTHERS THEN
            RAISE WARNING '创建表失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 3. 启用RLS（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'projects') THEN
            RAISE WARNING '表 projects 不存在，无法启用RLS';
        ELSE
            ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
            RAISE NOTICE '表 projects 的RLS已启用';
        END IF;

        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'tasks') THEN
            RAISE WARNING '表 tasks 不存在，无法启用RLS';
        ELSE
            ALTER TABLE tasks ENABLE ROW LEVEL SECURITY;
            RAISE NOTICE '表 tasks 的RLS已启用';
        END IF;
    EXCEPTION
        WHEN undefined_table THEN
            RAISE WARNING '表不存在';
        WHEN OTHERS THEN
            RAISE WARNING '启用RLS失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 4. RLS策略：租户隔离（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'projects') THEN
            RAISE WARNING '表 projects 不存在，无法创建策略';
        ELSE
            IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE schemaname = 'public' AND tablename = 'projects' AND policyname = 'tenant_isolation_projects') THEN
                CREATE POLICY tenant_isolation_projects
                    ON projects
                    FOR ALL
                    USING (tenant_id = current_setting('app.tenant_id')::int);
                RAISE NOTICE '策略 tenant_isolation_projects 创建成功';
            ELSE
                RAISE NOTICE '策略 tenant_isolation_projects 已存在';
            END IF;
        END IF;

        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'tasks') THEN
            RAISE WARNING '表 tasks 不存在，无法创建策略';
        ELSE
            IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE schemaname = 'public' AND tablename = 'tasks' AND policyname = 'tenant_isolation_tasks') THEN
                CREATE POLICY tenant_isolation_tasks
                    ON tasks
                    FOR ALL
                    USING (tenant_id = current_setting('app.tenant_id')::int);
                RAISE NOTICE '策略 tenant_isolation_tasks 创建成功';
            ELSE
                RAISE NOTICE '策略 tenant_isolation_tasks 已存在';
            END IF;
        END IF;
    EXCEPTION
        WHEN undefined_table THEN
            RAISE WARNING '表不存在';
        WHEN duplicate_object THEN
            RAISE WARNING '策略已存在';
        WHEN OTHERS THEN
            RAISE WARNING '创建策略失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 5. RLS策略：角色权限（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'projects') THEN
            RAISE WARNING '表 projects 不存在，无法创建策略';
        ELSE
            IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE schemaname = 'public' AND tablename = 'projects' AND policyname = 'project_owner_access') THEN
                CREATE POLICY project_owner_access
                    ON projects
                    FOR UPDATE
                    USING (
                        owner_id = current_setting('app.user_id')::int
                        OR current_setting('app.user_role') = 'admin'
                    );
                RAISE NOTICE '策略 project_owner_access 创建成功';
            ELSE
                RAISE NOTICE '策略 project_owner_access 已存在';
            END IF;
        END IF;

        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'tasks') THEN
            RAISE WARNING '表 tasks 不存在，无法创建策略';
        ELSE
            IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE schemaname = 'public' AND tablename = 'tasks' AND policyname = 'task_assignee_access') THEN
                CREATE POLICY task_assignee_access
                    ON tasks
                    FOR UPDATE
                    USING (
                        assignee_id = current_setting('app.user_id')::int
                        OR current_setting('app.user_role') = 'admin'
                    );
                RAISE NOTICE '策略 task_assignee_access 创建成功';
            ELSE
                RAISE NOTICE '策略 task_assignee_access 已存在';
            END IF;
        END IF;
    EXCEPTION
        WHEN undefined_table THEN
            RAISE WARNING '表不存在';
        WHEN duplicate_object THEN
            RAISE WARNING '策略已存在';
        WHEN OTHERS THEN
            RAISE WARNING '创建策略失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 6. 审计所有表（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'projects') THEN
            RAISE WARNING '表 projects 不存在，无法创建审计触发器';
        ELSE
            IF NOT EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'audit_trigger_function' AND pronamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public')) THEN
                RAISE WARNING '函数 audit_trigger_function 不存在，无法创建审计触发器';
            ELSE
                IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'audit_projects') THEN
                    CREATE TRIGGER audit_projects
                        AFTER INSERT OR UPDATE OR DELETE ON projects
                        FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();
                    RAISE NOTICE '审计触发器 audit_projects 创建成功';
                ELSE
                    RAISE NOTICE '审计触发器 audit_projects 已存在';
                END IF;
            END IF;
        END IF;

        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'tasks') THEN
            RAISE WARNING '表 tasks 不存在，无法创建审计触发器';
        ELSE
            IF NOT EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'audit_trigger_function' AND pronamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public')) THEN
                RAISE WARNING '函数 audit_trigger_function 不存在，无法创建审计触发器';
            ELSE
                IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'audit_tasks') THEN
                    CREATE TRIGGER audit_tasks
                        AFTER INSERT OR UPDATE OR DELETE ON tasks
                        FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();
                    RAISE NOTICE '审计触发器 audit_tasks 创建成功';
                ELSE
                    RAISE NOTICE '审计触发器 audit_tasks 已存在';
                END IF;
            END IF;
        END IF;
    EXCEPTION
        WHEN undefined_table THEN
            RAISE WARNING '表不存在';
        WHEN undefined_function THEN
            RAISE WARNING '函数 audit_trigger_function 不存在';
        WHEN duplicate_object THEN
            RAISE WARNING '触发器已存在';
        WHEN OTHERS THEN
            RAISE WARNING '创建触发器失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 7. 应用层连接管理（带完整错误处理）
CREATE OR REPLACE FUNCTION set_tenant_context(p_tenant_id int, p_user_id int, p_role text)
RETURNS void AS $$
BEGIN
    BEGIN
        -- 参数验证
        IF p_tenant_id IS NULL OR p_tenant_id <= 0 THEN
            RAISE EXCEPTION 'tenant_id必须为正整数，当前值: %', p_tenant_id;
        END IF;

        IF p_user_id IS NULL OR p_user_id <= 0 THEN
            RAISE EXCEPTION 'user_id必须为正整数，当前值: %', p_user_id;
        END IF;

        IF p_role IS NULL OR p_role NOT IN ('admin', 'user', 'readonly') THEN
            RAISE EXCEPTION 'role必须是admin、user或readonly之一，当前值: %', p_role;
        END IF;

        -- 检查表是否存在
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'users') THEN
            RAISE EXCEPTION '表 users 不存在';
        END IF;

        -- 验证租户和用户关系
        IF NOT EXISTS (
            SELECT 1 FROM users
            WHERE user_id = p_user_id
              AND tenant_id = p_tenant_id
              AND is_active = true
        ) THEN
            RAISE EXCEPTION 'Invalid user or tenant: user_id=%, tenant_id=%', p_user_id, p_tenant_id;
        END IF;

        -- 设置会话变量
        BEGIN
            PERFORM set_config('app.tenant_id', p_tenant_id::text, false);
            PERFORM set_config('app.user_id', p_user_id::text, false);
            PERFORM set_config('app.user_role', p_role, false);
            RAISE NOTICE '租户上下文设置成功: tenant_id=%, user_id=%, role=%', p_tenant_id, p_user_id, p_role;
        EXCEPTION
            WHEN OTHERS THEN
                RAISE EXCEPTION '设置会话变量失败: %', SQLERRM;
        END;
    EXCEPTION
        WHEN OTHERS THEN
            RAISE EXCEPTION 'set_tenant_context执行失败: %', SQLERRM;
    END;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 8. 使用示例（应用层，带错误处理和性能测试）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'set_tenant_context' AND pronamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public')) THEN
            RAISE WARNING '函数 set_tenant_context 不存在，无法执行';
            RETURN;
        END IF;
        RAISE NOTICE '开始设置租户上下文';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '操作准备失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 每个请求开始时调用
SELECT set_tenant_context(123, 456, 'user');

-- 现在所有查询都自动应用RLS（带性能测试）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'projects') THEN
            RAISE WARNING '表 projects 不存在，无法执行查询';
            RETURN;
        END IF;
        RAISE NOTICE '开始查询projects表（自动应用RLS）';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '查询准备失败: %', SQLERRM;
            RAISE;
    END;
END $$;

EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM projects;  -- 只返回tenant_id=123的数据

DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'tasks') THEN
            RAISE WARNING '表 tasks 不存在，无法执行查询';
            RETURN;
        END IF;
        RAISE NOTICE '开始查询tasks表（自动应用RLS）';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '查询准备失败: %', SQLERRM;
            RAISE;
    END;
END $$;

EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM tasks;     -- 只返回tenant_id=123的数据
```

### 7.2 案例：金融系统审计方案

**需求**：

- 所有交易必须审计
- 审计日志不可篡改
- 支持审计日志查询和分析
- 符合SOC2、PCI-DSS要求

**完整实现**（参考上文不可篡改审计日志）

---

## 📊 安全检查清单

### 日常安全检查

```sql
-- 1. 检查弱密码
SELECT rolname
FROM pg_authid
WHERE rolpassword IS NULL
   OR rolpassword = ''
   OR rolcanlogin = true;

-- 2. 检查过期密码（需要自定义实现）
SELECT rolname, rolvaliduntil
FROM pg_authid
WHERE rolvaliduntil < now();

-- 3. 检查权限过大的角色
SELECT
    grantee,
    string_agg(privilege_type, ', ') AS privileges
FROM information_schema.table_privileges
WHERE grantee NOT IN ('postgres', 'pg_monitor')
GROUP BY grantee
HAVING count(*) > 100;  -- 拥有超过100个权限

-- 4. 检查未加密连接
SELECT
    datname,
    usename,
    client_addr,
    ssl,
    query
FROM pg_stat_ssl
JOIN pg_stat_activity USING (pid)
WHERE ssl = false
  AND client_addr IS NOT NULL;

-- 5. 检查长期未使用的账号
SELECT
    rolname,
    rolvaliduntil,
    '90 days' AS inactive_threshold
FROM pg_authid
WHERE rolcanlogin = true
  AND NOT EXISTS (
      SELECT 1 FROM pg_stat_activity
      WHERE usename = rolname
  );
```

---

## 📚 参考资源

### 官方文档

#### **PostgreSQL核心文档**

1. **Row Security Policies（行级安全策略）**
   - 链接: [https://www.postgresql.org/docs/current/ddl-rowsecurity.html](https://www.postgresql.org/docs/current/ddl-rowsecurity.html)
   - 内容: RLS策略的完整文档和示例

2. **Security and Authentication（安全与认证）**
   - 链接: [https://www.postgresql.org/docs/current/auth.html](https://www.postgresql.org/docs/current/auth.html)
   - 内容: PostgreSQL认证和授权机制

3. **Role Management（角色管理）**
   - 链接: [https://www.postgresql.org/docs/current/user-manag.html](https://www.postgresql.org/docs/current/user-manag.html)
   - 内容: 用户和角色管理

4. **Privileges（权限）**
   - 链接: [https://www.postgresql.org/docs/current/ddl-priv.html](https://www.postgresql.org/docs/current/ddl-priv.html)
   - 内容: 对象权限管理

#### **PostgreSQL扩展文档**

1. **pgAudit（审计扩展）**
   - GitHub: [https://github.com/pgaudit/pgaudit](https://github.com/pgaudit/pgaudit)
   - 文档: [https://github.com/pgaudit/pgaudit/blob/master/README.md](https://github.com/pgaudit/pgaudit/blob/master/README.md)
   - 功能: 详细的SQL审计日志

2. **pgcrypto（加密扩展）**
   - 文档: [https://www.postgresql.org/docs/current/pgcrypto.html](https://www.postgresql.org/docs/current/pgcrypto.html)
   - 功能: 加密函数和哈希函数

3. **postgresql_anonymizer（数据脱敏）**
   - 文档: [https://postgresql-anonymizer.readthedocs.io/](https://postgresql-anonymizer.readthedocs.io/)
   - GitHub: [https://github.com/postgresql-anonymizer/postgresql_anonymizer](https://github.com/postgresql-anonymizer/postgresql_anonymizer)
   - 功能: 数据脱敏和匿名化

4. **pg_stat_statements（性能监控）**
   - 文档: [https://www.postgresql.org/docs/current/pgstatstatements.html](https://www.postgresql.org/docs/current/pgstatstatements.html)
   - 功能: SQL语句性能统计

### 最佳实践

#### **安全最佳实践**

1. **OWASP PostgreSQL Security Cheat Sheet**
   - 链接: [https://cheatsheetseries.owasp.org/cheatsheets/PostgreSQL_Cheat_Sheet.html](https://cheatsheetseries.owasp.org/cheatsheets/PostgreSQL_Cheat_Sheet.html)
   - 内容: OWASP提供的PostgreSQL安全清单

2. **CIS PostgreSQL Benchmark**
   - 链接: [https://www.cisecurity.org/benchmark/postgresql](https://www.cisecurity.org/benchmark/postgresql)
   - 内容: CIS PostgreSQL安全基准测试

3. **PostgreSQL Security Best Practices**
   - 链接: [https://www.postgresql.org/docs/current/security.html](https://www.postgresql.org/docs/current/security.html)
   - 内容: PostgreSQL官方安全最佳实践

4. **NIST Cybersecurity Framework**
   - 链接: [https://www.nist.gov/cyberframework](https://www.nist.gov/cyberframework)
   - 内容: NIST网络安全框架

#### **RLS最佳实践**

1. **RLS Performance Optimization**
   - 内容: RLS性能优化技巧
   - 要点:
     - 使用索引优化策略函数
     - 避免复杂的策略表达式
     - 使用SECURITY DEFINER函数

2. **Multi-Tenant RLS Patterns**
   - 内容: 多租户RLS设计模式
   - 要点:
     - 租户ID隔离
     - 层次化权限
     - 性能考虑

### 合规框架

#### **数据保护法规**

1. **GDPR（通用数据保护条例）**
   - 全称: General Data Protection Regulation
   - 适用范围: 欧盟
   - 关键要求:
     - 数据最小化
     - 数据可移植性
     - 被遗忘权
     - 数据泄露通知
   - PostgreSQL实现:
     - RLS实现数据访问控制
     - 审计日志记录数据访问
     - 数据脱敏保护隐私

2. **CCPA（加州消费者隐私法）**
   - 全称: California Consumer Privacy Act
   - 适用范围: 美国加州
   - 关键要求:
     - 数据访问权
     - 数据删除权
     - 数据不出售权
   - PostgreSQL实现:
     - 审计日志追踪数据使用
     - RLS控制数据访问

3. **PIPEDA（个人信息保护和电子文档法）**
   - 全称: Personal Information Protection and Electronic Documents Act
   - 适用范围: 加拿大
   - 关键要求: 个人信息保护

#### **行业标准**

1. **SOC 2（服务组织控制）**
   - 类型: Type I / Type II
   - 关键控制:
     - 访问控制
     - 加密
     - 审计日志
     - 变更管理
   - PostgreSQL实现:
     - RLS实现访问控制
     - pgAudit实现审计
     - SSL/TLS加密传输

2. **PCI-DSS（支付卡行业数据安全标准）**
   - 版本: PCI DSS 4.0
   - 关键要求:
     - 加密存储和传输
     - 访问控制
     - 审计日志
     - 漏洞管理
   - PostgreSQL实现:
     - pgcrypto加密敏感数据
     - RLS限制访问
     - 完整审计日志

3. **HIPAA（健康保险便携性和责任法案）**
   - 全称: Health Insurance Portability and Accountability Act
   - 适用范围: 美国医疗行业
   - 关键要求:
     - PHI（受保护健康信息）保护
     - 访问控制
     - 审计日志
     - 加密要求
   - PostgreSQL实现:
     - RLS保护PHI
     - 加密存储
     - 完整审计

4. **ISO/IEC 27001（信息安全管理）**
   - 标准: ISO/IEC 27001:2022
   - 关键要求:
     - 信息安全管理体系
     - 风险评估
     - 访问控制
     - 审计和监控
   - PostgreSQL实现:
     - 全面的安全控制
     - 审计和监控
     - 访问控制

### 开源工具和扩展

#### **审计工具**

1. **pgAudit**
   - GitHub: [https://github.com/pgaudit/pgaudit](https://github.com/pgaudit/pgaudit)
   - 功能: 详细的SQL审计日志
   - 支持: PostgreSQL 9.5+

2. **pgAudit Extension**
   - 功能: 增强的审计功能
   - 特点: 可配置的审计策略

#### **安全工具**

1. **pgcrypto**
   - 功能: 加密函数库
   - 支持: AES、RSA、哈希等

2. **postgresql_anonymizer**
   - 功能: 数据脱敏和匿名化
   - 支持: 多种脱敏策略

3. **pg_partman**
   - 功能: 分区管理
   - 用途: 审计日志分区

#### **监控工具**

1. **pg_stat_statements**
   - 功能: SQL性能统计
   - 用途: 性能监控和优化

2. **pgBadger**
   - 功能: PostgreSQL日志分析器
   - 用途: 日志分析和报告

### 社区资源

#### **论坛和社区**

1. **PostgreSQL官方论坛**
   - 链接: [https://www.postgresql.org/list/](https://www.postgresql.org/list/)
   - 内容: PostgreSQL邮件列表和论坛

2. **Stack Overflow**
   - 标签: [postgresql](https://stackoverflow.com/questions/tagged/postgresql), [row-level-security](https://stackoverflow.com/questions/tagged/row-level-security)
   - 内容: 技术问答

3. **Reddit - r/PostgreSQL**
   - 链接: [https://www.reddit.com/r/PostgreSQL/](https://www.reddit.com/r/PostgreSQL/)
   - 内容: PostgreSQL社区讨论

4. **PostgreSQL中文社区**
   - 内容: 中文技术交流

#### **博客和文章**

1. **PostgreSQL官方博客**
   - 链接: [https://www.postgresql.org/about/newsarchive/](https://www.postgresql.org/about/newsarchive/)
   - 内容: PostgreSQL新闻和更新

2. **2ndQuadrant博客**
   - 内容: PostgreSQL最佳实践和教程

3. **Percona博客**
   - 内容: PostgreSQL性能和安全文章

### 书籍推荐

1. **《PostgreSQL即学即用》**
   - 作者: 多位作者
   - 内容: PostgreSQL基础和实践

2. **《PostgreSQL High Performance》**
   - 作者: Gregory Smith
   - 内容: PostgreSQL性能优化

3. **《Mastering PostgreSQL in Application Development》**
   - 作者: Dimitri Fontaine
   - 内容: PostgreSQL应用开发

4. **《PostgreSQL Security》**
   - 内容: PostgreSQL安全实践

### 视频教程

1. **PostgreSQL官方YouTube频道**
   - 内容: PostgreSQL教程和会议视频

2. **Coursera - PostgreSQL课程**
   - 内容: PostgreSQL数据库课程

3. **Udemy - PostgreSQL安全课程**
   - 内容: PostgreSQL安全实践课程

### 研究论文

1. **Row-Level Security in PostgreSQL**
   - 内容: RLS实现原理和性能分析

2. **Database Auditing Best Practices**
   - 内容: 数据库审计最佳实践研究

3. **Multi-Tenant Database Security**
   - 内容: 多租户数据库安全研究

### 工具和脚本

1. **RLS策略生成器**
   - 功能: 自动生成RLS策略脚本

2. **审计日志分析工具**
   - 功能: 分析审计日志，生成报告

3. **安全配置检查脚本**
   - 功能: 检查PostgreSQL安全配置

### 参考资源使用建议

- 📚 **初学者**: 从官方文档和最佳实践开始
- 🔧 **开发者**: 参考开源工具和扩展
- 🏢 **企业用户**: 关注合规框架和行业标准
- 🔬 **研究者**: 阅读研究论文了解最新进展

---

**创建时间**: 2025年1月
**最后更新**: 2025年1月
**维护者**: PostgreSQL Modern Team
**难度等级**: ⭐⭐⭐⭐ 高级

🔒 **构建安全可信的PostgreSQL系统！**
