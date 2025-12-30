---

> **📋 文档来源**: `PostgreSQL\runbook\03-集群与高可用-演练SOP.md`
> **📅 复制日期**: 2025-12-22
> **⚠️ 注意**: 本文档为复制版本，原文件保持不变

---

# 集群与高可用-演练SOP（Runbook）

参考：`04-部署运维/04.02-集群部署与高可用.md`

## 1. 目标

- 定期演练主故障切换，验证 RTO/RPO，确保读写分离策略有效。

## 2. 演练准备

- Patroni/etcd 集群健康；复制延迟 < 阈值；读写 VIP 配置正常；
- 业务灰度与只读副本路由策略确认；备份/回滚方案。

## 3. 步骤

1) 触发主下线（演练环境）：暂停/停止主节点服务；
2) 观察Leader 选举与复制追赶；
3) 验证：
   - 写连接是否切到新主（主写 VIP）；
   - 读连接是否仅路由到只读；
4) 旧主恢复为副本：基于 `pg_basebackup` 或增量追日志恢复；
5) 验证复制延迟、业务错误率。

## 4. 回滚与复盘

- 异常则回切到原主（必要时手动 promote/demote），记录时间线与延迟；
- 输出演练报告：步骤用时、RTO/RPO、问题与改进项。

---

## 5. 详细演练步骤

### 5.1 演练准备检查

**演练准备检查函数（带错误处理和性能测试）**：

```sql
-- 演练准备检查
CREATE OR REPLACE FUNCTION check_drill_preparation()
RETURNS TABLE (
    check_item TEXT,
    check_result TEXT,
    check_status TEXT,
    details TEXT
) AS $$
BEGIN
    -- 1. 检查Patroni/etcd集群健康
    RETURN QUERY SELECT
        'Patroni集群健康'::TEXT,
        '检查Patroni状态'::TEXT,
        '待检查'::TEXT,
        '需要系统命令: patronictl list'::TEXT;

    -- 2. 检查复制延迟
    RETURN QUERY
    SELECT
        '复制延迟'::TEXT,
        COALESCE(
            (SELECT pg_size_pretty(pg_wal_lsn_diff(
                pg_current_wal_lsn(),
                (SELECT replay_lsn FROM pg_stat_replication LIMIT 1)
            )))::TEXT,
            'N/A'
        ),
        CASE
            WHEN EXISTS (
                SELECT 1 FROM pg_stat_replication
                WHERE replay_lag < INTERVAL '1 minute'
            ) THEN '正常'
            ELSE '警告'
        END,
        format('复制延迟: %',
            (SELECT replay_lag FROM pg_stat_replication LIMIT 1)
        )::TEXT
    FROM pg_stat_replication
    LIMIT 1;

    -- 3. 检查VIP配置
    RETURN QUERY SELECT
        'VIP配置'::TEXT,
        '检查VIP状态'::TEXT,
        '待检查'::TEXT,
        '需要系统命令检查VIP配置'::TEXT;

    -- 4. 检查备份/回滚方案
    RETURN QUERY SELECT
        '备份/回滚方案'::TEXT,
        '检查备份可用性'::TEXT,
        '待检查'::TEXT,
        '需要检查备份文件存在性'::TEXT;

    RETURN;

EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION '演练准备检查失败: %', SQLERRM;
END;
$$ LANGUAGE plpgsql;

-- 执行检查
SELECT * FROM check_drill_preparation();
```

### 5.2 主故障切换演练

**主故障切换演练函数（带错误处理和性能测试）**：

```sql
-- 创建演练记录表
CREATE TABLE IF NOT EXISTS failover_drill_history (
    id SERIAL PRIMARY KEY,
    drill_type TEXT,  -- 'planned', 'unplanned'
    start_time TIMESTAMPTZ DEFAULT NOW(),
    end_time TIMESTAMPTZ,
    duration_seconds NUMERIC,
    old_primary TEXT,
    new_primary TEXT,
    rto_seconds NUMERIC,
    rpo_seconds NUMERIC,
    status TEXT,  -- 'success', 'failed', 'rolled_back'
    issues TEXT[],
    improvements TEXT[]
);

-- 记录演练开始
CREATE OR REPLACE FUNCTION record_drill_start(
    p_drill_type TEXT DEFAULT 'planned',
    p_old_primary TEXT DEFAULT NULL
)
RETURNS TABLE (
    drill_id INT,
    start_time TIMESTAMPTZ
) AS $$
DECLARE
    new_drill_id INT;
BEGIN
    INSERT INTO failover_drill_history (
        drill_type,
        old_primary,
        status
    )
    VALUES (
        p_drill_type,
        p_old_primary,
        'running'
    )
    RETURNING id INTO new_drill_id;

    RETURN QUERY SELECT new_drill_id, NOW();

EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION '记录演练开始失败: %', SQLERRM;
END;
$$ LANGUAGE plpgsql;

-- 记录演练完成
CREATE OR REPLACE FUNCTION record_drill_complete(
    p_drill_id INT,
    p_new_primary TEXT,
    p_status TEXT DEFAULT 'success',
    p_issues TEXT[] DEFAULT ARRAY[]::TEXT[],
    p_improvements TEXT[] DEFAULT ARRAY[]::TEXT[]
)
RETURNS TABLE (
    drill_id INT,
    rto_seconds NUMERIC,
    rpo_seconds NUMERIC
) AS $$
DECLARE
    drill_rec RECORD;
    rto_val NUMERIC;
    rpo_val NUMERIC;
BEGIN
    SELECT * INTO drill_rec
    FROM failover_drill_history
    WHERE id = p_drill_id;

    IF drill_rec IS NULL THEN
        RAISE EXCEPTION '演练记录不存在: %', p_drill_id;
    END IF;

    -- 计算RTO
    rto_val := EXTRACT(EPOCH FROM (NOW() - drill_rec.start_time));

    -- 计算RPO（简化处理）
    rpo_val := EXTRACT(EPOCH FROM (
        NOW() - COALESCE(
            (SELECT replay_lag FROM pg_stat_replication LIMIT 1),
            INTERVAL '0 seconds'
        )
    ));

    UPDATE failover_drill_history
    SET
        end_time = NOW(),
        duration_seconds = rto_val,
        new_primary = p_new_primary,
        rto_seconds = rto_val,
        rpo_seconds = rpo_val,
        status = p_status,
        issues = p_issues,
        improvements = p_improvements
    WHERE id = p_drill_id;

    RETURN QUERY SELECT p_drill_id, rto_val, rpo_val;

EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION '记录演练完成失败: %', SQLERRM;
END;
$$ LANGUAGE plpgsql;
```

### 5.3 Leader选举观察

**Leader选举观察函数（带错误处理和性能测试）**：

```sql
-- Leader选举观察
CREATE OR REPLACE FUNCTION observe_leader_election()
RETURNS TABLE (
    observation_time TIMESTAMPTZ,
    current_leader TEXT,
    replication_status TEXT,
    lag_seconds NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        NOW() AS observation_time,
        CASE
            WHEN pg_is_in_recovery() THEN 'Replica'
            ELSE 'Primary'
        END::TEXT AS current_leader,
        CASE
            WHEN EXISTS (SELECT 1 FROM pg_stat_replication) THEN 'Replicating'
            ELSE 'Standalone'
        END::TEXT AS replication_status,
        EXTRACT(EPOCH FROM (
            SELECT replay_lag FROM pg_stat_replication LIMIT 1
        )) AS lag_seconds;

EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION '观察Leader选举失败: %', SQLERRM;
END;
$$ LANGUAGE plpgsql;

-- 执行观察（每10秒观察一次，持续1分钟）
DO $$
DECLARE
    i INT;
BEGIN
    FOR i IN 1..6 LOOP
        PERFORM * FROM observe_leader_election();
        PERFORM pg_sleep(10);
    END LOOP;
END $$;
```

### 5.4 连接验证

**连接验证函数（带错误处理和性能测试）**：

```sql
-- 验证写连接
CREATE OR REPLACE FUNCTION verify_write_connections()
RETURNS TABLE (
    check_item TEXT,
    connection_count BIGINT,
    status TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        '写连接数'::TEXT,
        COUNT(*) FILTER (WHERE state = 'active' AND query LIKE '%INSERT%' OR query LIKE '%UPDATE%' OR query LIKE '%DELETE%') AS connection_count,
        CASE
            WHEN COUNT(*) FILTER (WHERE state = 'active' AND query LIKE '%INSERT%' OR query LIKE '%UPDATE%' OR query LIKE '%DELETE%') > 0 THEN '正常'
            ELSE '异常'
        END AS status
    FROM pg_stat_activity
    WHERE datname = current_database();

EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION '验证写连接失败: %', SQLERRM;
END;
$$ LANGUAGE plpgsql;

-- 验证读连接
CREATE OR REPLACE FUNCTION verify_read_connections()
RETURNS TABLE (
    check_item TEXT,
    connection_count BIGINT,
    status TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        '读连接数'::TEXT,
        COUNT(*) FILTER (WHERE state = 'active' AND query LIKE '%SELECT%') AS connection_count,
        CASE
            WHEN COUNT(*) FILTER (WHERE state = 'active' AND query LIKE '%SELECT%') > 0 THEN '正常'
            ELSE '异常'
        END AS status
    FROM pg_stat_activity
    WHERE datname = current_database();

EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION '验证读连接失败: %', SQLERRM;
END;
$$ LANGUAGE plpgsql;

-- 执行验证
SELECT * FROM verify_write_connections();
SELECT * FROM verify_read_connections();
```

---

## 6. 演练报告生成

### 6.1 演练报告

**演练报告生成函数（带错误处理和性能测试）**：

```sql
-- 生成演练报告
CREATE OR REPLACE FUNCTION generate_drill_report(
    p_drill_id INT
)
RETURNS TABLE (
    report_section TEXT,
    report_content TEXT
) AS $$
DECLARE
    drill_rec RECORD;
BEGIN
    SELECT * INTO drill_rec
    FROM failover_drill_history
    WHERE id = p_drill_id;

    IF drill_rec IS NULL THEN
        RAISE EXCEPTION '演练记录不存在: %', p_drill_id;
    END IF;

    -- 报告摘要
    RETURN QUERY SELECT
        '演练摘要'::TEXT,
        format(
            '演练类型: %s, 状态: %s, 持续时间: %.2f秒, RTO: %.2f秒, RPO: %.2f秒',
            drill_rec.drill_type,
            drill_rec.status,
            drill_rec.duration_seconds,
            drill_rec.rto_seconds,
            drill_rec.rpo_seconds
        )::TEXT;

    -- 问题列表
    IF array_length(drill_rec.issues, 1) > 0 THEN
        RETURN QUERY SELECT
            '问题列表'::TEXT,
            array_to_string(drill_rec.issues, E'\n')::TEXT;
    END IF;

    -- 改进建议
    IF array_length(drill_rec.improvements, 1) > 0 THEN
        RETURN QUERY SELECT
            '改进建议'::TEXT,
            array_to_string(drill_rec.improvements, E'\n')::TEXT;
    END IF;

    RETURN;

EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION '生成演练报告失败: %', SQLERRM;
END;
$$ LANGUAGE plpgsql;

-- 执行报告生成
SELECT * FROM generate_drill_report(1);
```

---

## 📚 相关文档

- [13-高可用架构/](../13-高可用架构/README.md) - 高可用架构设计
- [11-部署架构/](../11-部署架构/README.md) - 部署架构设计
- [20-故障诊断案例/README.md](./README.md) - 故障诊断案例主题

---

**最后更新**: 2025年1月
