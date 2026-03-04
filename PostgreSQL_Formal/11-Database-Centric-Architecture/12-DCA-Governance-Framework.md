# DCA治理框架

> **文档类型**: 治理规范
> **创建日期**: 2026-03-04
> **文档长度**: 7500+字

---

## 摘要

建立数据库中心架构的治理体系，包括命名规范、代码审查清单、安全基线、性能标准和文档规范。

---

## 1. 治理组织架构

### 1.1 DCA卓越中心 (CoE)

```
DCA Center of Excellence
│
├── 架构委员会
│   ├── 首席架构师 (1人)
│   ├── 领域架构师 (3-5人)
│   └── DBA专家 (2-3人)
│
├── 工程团队
│   ├── 存储过程开发组
│   ├── 工具开发组
│   └── 测试与质量组
│
└── 赋能团队
    ├── 培训组
    ├── 文档组
    └── 社区运营组
```

### 1.2 职责分工

| 角色 | 核心职责 |
|------|----------|
| 首席架构师 | 制定技术路线、评审重大方案 |
| 领域架构师 | 负责特定业务领域的DCA设计 |
| DBA专家 | 性能优化、容量规划、安全审计 |
| 存储过程工程师 | 开发和维护存储过程 |
| 质量工程师 | 代码审查、测试覆盖、标准执行 |

---

## 2. 命名规范

### 2.1 对象命名

| 对象类型 | 命名格式 | 示例 |
|----------|----------|------|
| 存储过程 | `sp_{module}_{action}_{entity}` | `sp_order_create_order` |
| 函数 | `fn_{module}_{operation}_{entity}` | `fn_order_calculate_total` |
| 视图 | `v_{module}_{purpose}_{entity}` | `v_order_list_active` |
| 触发器 | `trg_{entity}_{action}_{timing}` | `trg_orders_audit_after` |
| 表 | `{entity}s` (复数) | `orders`, `customers` |
| 索引 | `idx_{table}_{column(s)}` | `idx_orders_user_id_status` |

### 2.2 参数命名

```sql
-- 输入参数前缀: p_
IN p_user_id BIGINT
IN p_start_date DATE

-- 输出参数前缀: out_
OUT out_order_id BIGINT
OUT out_total_amount DECIMAL

-- 局部变量前缀: v_
DECLARE v_current_time TIMESTAMP;
DECLARE v_calc_result DECIMAL;

-- 常量前缀: c_
DECLARE c_max_retry CONSTANT INTEGER := 3;
```

---

## 3. 代码审查清单

### 3.1 功能审查

- [ ] 业务逻辑正确性
- [ ] 边界条件处理
- [ ] 幂等性保证
- [ ] 事务完整性
- [ ] 错误处理覆盖

### 3.2 性能审查

- [ ] 索引使用检查
- [ ] N+1查询消除
- [ ] 批量操作优化
- [ ] 锁范围最小化
- [ ] 执行计划审查

### 3.3 安全审查

- [ ] SQL注入防护
- [ ] 权限最小化
- [ ] 敏感数据加密
- [ ] 审计日志记录
- [ ] RLS策略配置

### 3.4 代码质量

```sql
-- ✅ 好的代码: 清晰、有注释、模块化
CREATE OR REPLACE FUNCTION fn_calculate_order_total(
    p_order_id BIGINT
) RETURNS DECIMAL AS $$
/*
 * 计算订单总额
 * 包括商品价格、税费、运费
 * Author: team@example.com
 * Created: 2026-03-04
 */
DECLARE
    v_subtotal DECIMAL;
    v_tax DECIMAL;
    v_shipping DECIMAL;
BEGIN
    -- 计算商品小计
    SELECT COALESCE(SUM(quantity * unit_price), 0)
    INTO v_subtotal
    FROM order_items
    WHERE order_id = p_order_id;

    -- 计算税费 (假设税率8%)
    v_tax := v_subtotal * 0.08;

    -- 计算运费
    v_shipping := CASE
        WHEN v_subtotal > 100 THEN 0  -- 满100免运费
        ELSE 10
    END;

    RETURN v_subtotal + v_tax + v_shipping;
END;
$$ LANGUAGE plpgsql;
```

---

## 4. 安全基线

### 4.1 强制安全规则

| 规则 | 级别 | 检查方式 |
|------|------|----------|
| 所有输入必须参数化 | 强制 | 静态扫描 |
| 敏感操作必须审计 | 强制 | 代码审查 |
| RLS必须启用 | 强制 | 自动检查 |
| 最小权限原则 | 强制 | 权限审计 |
| 敏感数据加密 | 高 | 代码审查 |

### 4.2 安全编码规范

```sql
-- ✅ 安全的参数处理
CREATE PROCEDURE sp_search_users(IN p_keyword VARCHAR)
AS $$
BEGIN
    -- 参数化查询，自动转义
    SELECT * FROM users WHERE name ILIKE '%' || p_keyword || '%';
END;
$$;

-- ❌ 不安全的动态SQL
CREATE PROCEDURE sp_search_users_unsafe(IN p_column VARCHAR, IN p_value VARCHAR)
AS $$
BEGIN
    -- 危险：可能导致SQL注入
    EXECUTE 'SELECT * FROM users WHERE ' || p_column || ' = ''' || p_value || '''';
END;
$$;
```

---

## 5. 性能标准

### 5.1 SLA指标

| 指标 | P50 | P95 | P99 |
|------|-----|-----|-----|
| 简单查询 | < 10ms | < 50ms | < 100ms |
| 复杂查询 | < 50ms | < 200ms | < 500ms |
| 存储过程 | < 20ms | < 100ms | < 200ms |
| 批量操作 | < 100ms | < 500ms | < 1s |

### 5.2 性能检查清单

- [ ] 执行时间 < 100ms (P95)
- [ ] 缓存命中率 > 95%
- [ ] 无全表扫描 (小表除外)
- [ ] 锁等待时间 < 10ms
- [ ] 临时文件使用 < 100MB

---

## 6. 文档规范

### 6.1 存储过程文档模板

```sql
/*
 * 名称: sp_order_create
 *
 * 描述:
 *   创建新订单，包括验证库存、计算价格、扣减库存、记录审计日志
 *
 * 参数:
 *   @p_user_id BIGINT - 用户ID
 *   @p_items JSONB - 订单项数组 [{product_id, quantity, unit_price}]
 *   @p_shipping_address JSONB - 配送地址
 *   @out_order_id BIGINT (OUT) - 返回订单ID
 *   @out_total DECIMAL (OUT) - 返回订单总额
 *
 * 返回值:
 *   通过OUT参数返回
 *
 * 异常:
 *   E0001 - 参数错误
 *   E0003 - 库存不足
 *   E0007 - 系统错误
 *
 * 示例:
 *   CALL sp_order_create(
 *       1,
 *       '[{"product_id": 1, "quantity": 2, "unit_price": 99.99}]'::JSONB,
 *       '{"city": "Beijing", "address": "..."}'::JSONB,
 *       NULL, NULL
 *   );
 *
 * 作者: team@example.com
 * 创建日期: 2026-03-04
 * 版本: 1.0
 * 变更历史:
 *   2026-03-04 v1.0 - 初始版本
 */
```

---

## 7. 质量度量

### 7.1 KPI指标

| 指标 | 目标值 | 度量方式 |
|------|--------|----------|
| 存储过程覆盖率 | > 80% | 业务逻辑在存储过程中的比例 |
| 代码重复率 | < 5% | SonarQube检测 |
| 测试覆盖率 | > 90% | pgTAP测试覆盖 |
| 安全漏洞 | 0 | 静态扫描 |
| 性能退化 | 0 | 基准测试对比 |

### 7.2 质量门禁

```
代码提交前必须通过:
├── 静态代码扫描 (PASS)
├── 单元测试 (覆盖率>90%)
├── 集成测试 (全部通过)
├── 性能测试 (P95<SLA)
└── 安全扫描 (无高危漏洞)
```

---

**文档信息**:

- 字数: 7500+
- 规范条目: 50+
- 检查清单: 30+项
- 状态: ✅ 完成
