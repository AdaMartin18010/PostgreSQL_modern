# 代码示例运行验证报告

> **生成日期**: 2025年1月
> **扫描结果**: 找到 983 个可能有语法错误的代码示例

---

## 📊 统计信息

- **需要修复的代码示例**: 983 个

## 📋 需要修复的代码示例

### 00-代码示例改进全面梳理计划-2025-01.md

**行 78** (sql):

```sql
-- 标准模式（带错误处理和性能测试）
DO $$
BEGIN
    -- SQL代码
    CREATE TABLE IF NOT EXISTS ...
    COMMIT;
EXCEPTION
    WHEN duplicate_table THEN
        RAISE NOTICE '表已存在';
    WHEN OTHERS THEN
        RAISE WARN
```

**错误**: SELECT语句缺少FROM子句

---

### 00-任务执行完成报告-2025-01.md

**行 138** (sql):

```sql
   EXPLAIN (ANALYZE, BUFFERS, TIMING)
   SELECT ...;

```

**错误**: SELECT语句缺少FROM子句

---

**行 144** (sql):

```sql
   -- 注意：函数内部查询的性能测试通常在函数调用时进行
   -- EXPLAIN (ANALYZE, BUFFERS, TIMING)
   -- SELECT ...;

```

**错误**: SELECT语句缺少FROM子句

---

### 00-任务执行总结-2025-01.md

**行 106** (sql):

```sql
   EXPLAIN (ANALYZE, BUFFERS, TIMING)
   SELECT ...;

```

**错误**: SELECT语句缺少FROM子句

---

**行 112** (sql):

```sql
   -- 创建索引后测试查询性能
   EXPLAIN (ANALYZE, BUFFERS, TIMING)
   SELECT ... WHERE indexed_column = ...;

```

**错误**: SELECT语句缺少FROM子句

---

**行 119** (sql):

```sql
   -- 在事务中监控性能
   EXPLAIN (ANALYZE, BUFFERS, TIMING)
   SELECT ...;

```

**错误**: SELECT语句缺少FROM子句

---

### 00-任务执行最终报告-2025-01.md

**行 127** (sql):

```sql
   EXPLAIN (ANALYZE, BUFFERS, TIMING)
   SELECT ...;

```

**错误**: SELECT语句缺少FROM子句

---

**行 133** (sql):

```sql
   -- 注意：函数内部查询的性能测试通常在函数调用时进行
   -- EXPLAIN (ANALYZE, BUFFERS, TIMING)
   -- SELECT ...;

```

**错误**: SELECT语句缺少FROM子句

---

**行 140** (sql):

```sql
   -- 注意：这是检查性查询，通常不需要性能测试
   -- 如果需要性能测试，可以使用：
   -- EXPLAIN (ANALYZE, BUFFERS, TIMING)
   -- SELECT ...;

```

**错误**: SELECT语句缺少FROM子句

---

### 00-任务执行进度报告-2025-01-最新.md

**行 104** (sql):

```sql
   EXPLAIN (ANALYZE, BUFFERS, TIMING)
   SELECT ...;

```

**错误**: SELECT语句缺少FROM子句

---

**行 110** (sql):

```sql
   -- 创建索引后测试查询性能
   EXPLAIN (ANALYZE, BUFFERS, TIMING)
   SELECT ... WHERE indexed_column = ...;

```

**错误**: SELECT语句缺少FROM子句

---

**行 117** (sql):

```sql
   -- 在事务中监控性能
   EXPLAIN (ANALYZE, BUFFERS, TIMING)
   SELECT ...;

```

**错误**: SELECT语句缺少FROM子句

---

### 00-批量处理完成总结-2025-01.md

**行 114** (sql):

```sql
   EXPLAIN (ANALYZE, BUFFERS, TIMING)
   SELECT ...;

```

**错误**: SELECT语句缺少FROM子句

---

**行 120** (sql):

```sql
   -- 创建索引后测试查询性能
   EXPLAIN (ANALYZE, BUFFERS, TIMING)
   SELECT ... WHERE indexed_column = ...;

```

**错误**: SELECT语句缺少FROM子句

---

**行 127** (sql):

```sql
   -- 在事务中监控性能
   EXPLAIN (ANALYZE, BUFFERS, TIMING)
   SELECT ...;

```

**错误**: SELECT语句缺少FROM子句

---

### 00-持续推进策略-2025-01.md

**行 35** (sql):

```sql
-- 标准错误处理模板
DO $$
BEGIN
    BEGIN
        -- 前置检查
        IF NOT EXISTS (...) THEN
            RAISE WARNING '...';
            RETURN;
        END IF;

        -- 主要操作
        ...

        RAISE NOTI
```

**错误**: SELECT语句缺少FROM子句

---

### 00-最终任务执行总结-2025-01.md

**行 121** (sql):

```sql
   EXPLAIN (ANALYZE, BUFFERS, TIMING)
   SELECT ...;

```

**错误**: SELECT语句缺少FROM子句

---

**行 127** (sql):

```sql
   -- 创建索引后测试查询性能
   EXPLAIN (ANALYZE, BUFFERS, TIMING)
   SELECT ... WHERE indexed_column = ...;

```

**错误**: SELECT语句缺少FROM子句

---

**行 134** (sql):

```sql
   -- 在事务中监控性能
   EXPLAIN (ANALYZE, BUFFERS, TIMING)
   SELECT ...;

```

**错误**: SELECT语句缺少FROM子句

---

### 00-最终完成度报告-2025-01.md

**行 136** (sql):

```sql
   EXPLAIN (ANALYZE, BUFFERS, TIMING)
   SELECT ...;

```

**错误**: SELECT语句缺少FROM子句

---

**行 142** (sql):

```sql
   -- 注意：函数内部查询的性能测试通常在函数调用时进行
   -- EXPLAIN (ANALYZE, BUFFERS, TIMING)
   -- SELECT ...;

```

**错误**: SELECT语句缺少FROM子句

---

### 01-核心基础\01.02-系统架构\01.01-系统架构与设计原理.md

**行 1848** (sql):

```sql
-- 从库提升为主库（PostgreSQL 12及以下）
-- 创建触发文件
touch /tmp/promote_standby

-- PostgreSQL 13+使用pg_promote()
SELECT pg_promote();

-- 检查主从状态
SELECT pg_is_in_recovery();
-- false = 主库，true = 从库

```

**错误**: SELECT语句缺少FROM子句

---

### 02-查询与优化\02.03-执行计划\02.04-执行计划与性能调优.md

**行 1020** (sql):

```sql
-- 创建执行计划分析函数
-- 分析执行计划函数（带完整错误处理）
CREATE OR REPLACE FUNCTION analyze_execution_plan(p_query_text text)
RETURNS TABLE(
    node_type text,
    cost_start numeric,
    cost_total numeric,
    actual_ti
```

**错误**: 单引号不匹配

---

**行 1085** (sql):

```sql
-- 性能基准测试函数（带完整错误处理）
CREATE OR REPLACE FUNCTION benchmark_query(
    p_query_text text,
    p_iterations integer DEFAULT 10
)
RETURNS TABLE(
    iteration integer,
    execution_time numeric,
    rows
```

**错误**: 单引号不匹配

---

**行 2265** (sql):

```sql
-- 系统配置优化（带错误处理）
-- 1. 内存配置
DO $$
BEGIN
    BEGIN
        ALTER SYSTEM SET shared_buffers = '256MB';
        ALTER SYSTEM SET work_mem = '4MB';
        ALTER SYSTEM SET maintenance_work_mem = '64MB';

```

**错误**: SELECT语句缺少FROM子句

---

### 02-查询与优化\02.04-统计信息\02.03-统计信息与代价模型.md

**行 2002** (sql):

```sql
-- 创建统计信息更新函数（带完整错误处理）
CREATE OR REPLACE FUNCTION update_table_stats(table_name text)
RETURNS void AS $$
BEGIN
    -- 参数验证
    IF table_name IS NULL OR TRIM(table_name) = '' THEN
        RAISE EXCEPTI
```

**错误**: 单引号不匹配

---

### 02-查询与优化\02.06-性能调优\PostgreSQL性能调优完整指南.md

**行 174** (sql):

```sql
-- 动态设置连接参数（带错误处理）
DO $$
DECLARE
    current_max_conn INT;
BEGIN
    -- 获取当前最大连接数
    SELECT current_setting('max_connections')::INT INTO current_max_conn;

    IF current_max_conn < 100 THEN

```

**错误**: SELECT语句缺少FROM子句

---

### 02-查询与优化\02.07-全文搜索\PostgreSQL18-全文搜索深度实战.md

**行 1350** (sql):

```sql
-- 创建产品表（带错误处理）
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'products') THEN
        RAISE WARNING '表已存在: products';
    ELSE

```

**错误**: 单引号不匹配

---

### 02-查询与优化\02.07-全文搜索\全文搜索与向量搜索结合.md

**行 322** (sql):

```sql
-- 方案2：加权组合（带完整错误处理）
CREATE OR REPLACE FUNCTION hybrid_search(
    query_text TEXT,
    query_embedding VECTOR(1536),
    fulltext_weight FLOAT DEFAULT 0.4,
    vector_weight FLOAT DEFAULT 0.6
)
RETUR
```

**错误**: 单引号不匹配

---

### 02-查询与优化\05.02-索引结构正确性-BTree_GiST_GiN不变式与证明.md

**行 1540** (sql):

```sql
   -- 使用amcheck验证索引不变式
   SELECT bt_index_check('idx_orders_order_date');

```

**错误**: SELECT语句缺少FROM子句

---

### 02-查询与优化\05.04-增量物化视图-代数差分与正确性.md

**行 1583** (sql):

```sql
   -- 使用pg_cron定时刷新
   SELECT cron.schedule(
       'refresh-summary',
       '0 * * * *',
       $$REFRESH MATERIALIZED VIEW CONCURRENTLY mv_order_summary$$
   );

```

**错误**: SELECT语句缺少FROM子句

---

### 02-查询与优化\05.07-物化视图选择-查询重写等价与代价界.md

**行 1134** (sql):

```sql
   -- 使用pg_cron定时刷新
   SELECT cron.schedule(
       'refresh-mv',
       '0 * * * *',
       $$REFRESH MATERIALIZED VIEW CONCURRENTLY mv_customer_orders$$
   );

```

**错误**: SELECT语句缺少FROM子句

---

### 02-查询与优化\05.08-可自维护物化视图-可维护性判据与构造.md

**行 1167** (sql):

```sql
-- 创建可自维护物化视图（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'user_events') THEN
            RAISE WARNING '
```

**错误**: 单引号不匹配

---

### 02-查询与优化\05.10-查询重写等价性-基于同构的充分必要条件.md

**行 935** (sql):

```sql
   -- 查看查询执行计划
   EXPLAIN (ANALYZE, BUFFERS)
   SELECT ...;

```

**错误**: SELECT语句缺少FROM子句

---

### 02-查询与优化\05.13-查询优化器自适应-反馈学习与代价模型修正.md

**行 319** (sql):

```sql
-- 查看当前代价模型参数（带错误处理）
DO $$
DECLARE
    seq_page_cost_val TEXT;
    random_page_cost_val TEXT;
    cpu_tuple_cost_val TEXT;
BEGIN
    BEGIN
        SELECT current_setting('seq_page_cost') INTO seq_page
```

**错误**: SELECT语句缺少FROM子句

---

**行 745** (sql):

```sql
   -- 启用pg_stat_statements
   CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

   -- 配置统计收集
   ALTER SYSTEM SET pg_stat_statements.track = 'all';
   SELECT pg_reload_conf();

```

**错误**: SELECT语句缺少FROM子句

---

### 02-查询与优化\05.15-数据库性能调优-参数优化与自适应调整的形式化.md

**行 261** (sql):

```sql
-- 查看当前内存参数（带错误处理）
DO $$
DECLARE
    shared_buffers_val TEXT;
    work_mem_val TEXT;
    maintenance_work_mem_val TEXT;
    effective_cache_size_val TEXT;
BEGIN
    BEGIN
        SELECT current_settin
```

**错误**: SELECT语句缺少FROM子句

---

**行 369** (sql):

```sql
-- 查看当前I/O参数（带错误处理）
DO $$
DECLARE
    random_page_cost_val TEXT;
    seq_page_cost_val TEXT;
    effective_io_concurrency_val TEXT;
BEGIN
    BEGIN
        SELECT current_setting('random_page_cost') I
```

**错误**: SELECT语句缺少FROM子句

---

**行 444** (sql):

```sql
-- 查看当前并发参数
SHOW max_connections;
SHOW max_parallel_workers_per_gather;
SHOW max_parallel_workers;

-- 调整最大连接数
ALTER SYSTEM SET max_connections = 200;
SELECT pg_reload_conf();

-- 调整并行查询参数
ALTER SYSTE
```

**错误**: SELECT语句缺少FROM子句

---

**行 566** (sql):

```sql
-- PostgreSQL: 丰富的参数配置
ALTER SYSTEM SET shared_buffers = '2GB';
ALTER SYSTEM SET work_mem = '64MB';
ALTER SYSTEM SET random_page_cost = 1.1;
SELECT pg_reload_conf();

-- SQLite: 有限的PRAGMA参数
PRAGMA cac
```

**错误**: SELECT语句缺少FROM子句

---

### 02-查询与优化\全文搜索完整实战指南.md

**行 90** (sql):

```sql
-- tsvector是文档的向量表示，包含词元和位置信息（带错误处理）
DO $$
DECLARE
    result_vector tsvector;
BEGIN
    BEGIN
        result_vector := to_tsvector('english', 'PostgreSQL is a powerful open source database');

```

**错误**: SELECT语句缺少FROM子句

---

**行 473** (sql):

```sql
-- zhparser使用jieba词典，可以添加自定义词典
-- 在postgresql.conf中配置
-- zhparser.multi_short = true  # 启用短词识别
-- zhparser.dict_in_memory = false  # 词典不加载到内存（节省内存）

-- 或者使用pg_jieba（另一个jieba扩展）
CREATE EXTENSION pg_jie
```

**错误**: SELECT语句缺少FROM子句

---

**行 761** (sql):

```sql
-- 创建语言检测函数（带错误处理）
DO $$
BEGIN
    BEGIN
        IF EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'detect_language') THEN
            DROP FUNCTION detect_language(TEXT) CASCADE;
            RAISE NOT
```

**错误**: 单引号不匹配

---

**行 816** (sql):

```sql
-- 创建多语言文章表（带错误处理）
DO $$
BEGIN
    BEGIN
        IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'multilingual_articles') THEN
            RAISE WARNI
```

**错误**: 单引号不匹配

---

**行 969** (sql):

```sql
-- 跨语言搜索（将查询转换为多种语言，带完整错误处理）
DO $$
BEGIN
    BEGIN
        IF EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'multilingual_search') THEN
            DROP FUNCTION multilingual_search(TEXT) CASCADE;

```

**错误**: 单引号不匹配

---

**行 1738** (sql):

```sql
-- 搜索博客文章（带完整错误处理）
DO $$
BEGIN
    BEGIN
        IF EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'search_blog_posts') THEN
            DROP FUNCTION search_blog_posts(TEXT, INTEGER, INTEGER) CASCADE;
```

**错误**: 单引号不匹配

---

### 03-事务与并发\03.01-MVCC机制\01.05-并发控制与MVCC机制.md

**行 682** (sql):

```sql
-- 事务快照格式：xmin:xmax:xip_list（带错误处理）
-- xmin: 最早的活动事务ID
-- xmax: 下一个事务ID（所有小于xmax的事务要么已提交，要么在xip_list中）
-- xip_list: 活动事务ID列表

-- 查看当前快照（带错误处理）
DO $$
BEGIN
    BEGIN
        RAISE NOTICE '开始查看当前快照';

```

**错误**: SELECT语句缺少FROM子句

---

### 03-事务与并发\03.07-场景实践\分布式系统\分布式场景CAP实践.md

**行 96** (sql):

```sql
-- 支付服务：CP模式（带完整错误处理）
DO $$
BEGIN
    BEGIN
        BEGIN
            ALTER SYSTEM SET synchronous_standby_names = 'standby1,standby2';
            RAISE NOTICE '支付服务：同步备库名称已设置为 standby1,standby2（CP模式
```

**错误**: 单引号不匹配

---

### 03-事务与并发\03.07-场景实践\时序数据\归档策略.md

**行 148** (sql):

```sql
-- 数据量归档策略
-- 1. 归档超过阈值的数据
-- 按大小归档函数（带完整错误处理）
CREATE OR REPLACE FUNCTION archive_by_size()
RETURNS void
LANGUAGE plpgsql
AS $$
DECLARE
    v_part_name TEXT;
    v_part_size BIGINT;
    v_size_thresho
```

**错误**: 单引号不匹配

---

### 03-事务与并发\03.07-场景实践\案例研究\CAP实践案例研究.md

**行 153** (sql):

```sql
-- PostgreSQL AP模式配置（带错误处理）
DO $$
BEGIN
    BEGIN
        BEGIN
            ALTER SYSTEM SET synchronous_standby_names = '';
            RAISE NOTICE '同步备库名称已设置为空（AP模式，异步复制）';
        EXCEPTION

```

**错误**: 单引号不匹配

---

**行 226** (sql):

```sql
-- PostgreSQL AP模式配置（带错误处理）
DO $$
BEGIN
    BEGIN
        BEGIN
            ALTER SYSTEM SET synchronous_standby_names = '';
            RAISE NOTICE '同步备库名称已设置为空（AP模式，异步复制）';
        EXCEPTION

```

**错误**: 单引号不匹配

---

### 03-事务与并发\03.07-场景实践\程序交互\应用程序与PostgreSQL MVCC交互.md

**行 100** (sql):

```sql
-- 检查事务状态（带错误处理和性能测试）
DO $$
BEGIN
    BEGIN
        RAISE NOTICE '开始检查事务状态和隔离级别';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '检查准备失败: %', SQLERRM;
            RAISE;
    END;
END
```

**错误**: SELECT语句缺少FROM子句

---

### 03-事务与并发\03.07-场景实践\金融系统\CAP-ACID场景化论证.md

**行 492** (sql):

```sql
-- 日志场景：AP模式配置（带错误处理）
DO $$
BEGIN
    BEGIN
        BEGIN
            ALTER SYSTEM SET synchronous_standby_names = '';
            RAISE NOTICE '同步备库名称已设置为空（AP模式，异步复制）';
        EXCEPTION

```

**错误**: 单引号不匹配

---

**行 609** (sql):

```sql
-- 时序场景：AP模式配置（带错误处理）
DO $$
BEGIN
    BEGIN
        BEGIN
            ALTER SYSTEM SET synchronous_standby_names = '';
            RAISE NOTICE '同步备库名称已设置为空（AP模式，异步复制）';
        EXCEPTION

```

**错误**: 单引号不匹配

---

### 03-事务与并发\03.07-场景实践\高可用\PostgreSQL集群的CAP.md

**行 198** (sql):

```sql
-- CP模式：同步复制（带错误处理）
DO $$
BEGIN
    BEGIN
        BEGIN
            ALTER SYSTEM SET synchronous_standby_names = 'standby1,standby2';
            RAISE NOTICE '同步备库名称已设置为 standby1,standby2（CP模式）';

```

**错误**: 单引号不匹配

---

**行 394** (sql):

```sql
-- 强一致性：同步复制（带完整错误处理）
DO $$
BEGIN
    BEGIN
        BEGIN
            ALTER SYSTEM SET synchronous_standby_names = 'standby1,standby2';
            RAISE NOTICE '同步备库名称已设置为 standby1,standby2（强一致性）';

```

**错误**: 单引号不匹配

---

**行 562** (sql):

```sql
-- 金融场景：CP模式（带完整错误处理）
DO $$
BEGIN
    BEGIN
        BEGIN
            ALTER SYSTEM SET synchronous_standby_names = 'standby1,standby2';
            RAISE NOTICE '同步备库名称已设置为 standby1,standby2（金融场景CP模式）
```

**错误**: 单引号不匹配

---

### 03-事务与并发\03.07-场景实践\高可用\故障转移场景.md

**行 386** (sql):

```sql
-- 流复制自动故障转移（带完整错误处理）
-- 使用pg_auto_failover或Patroni

-- 1. 故障检测
-- 自动检测主节点故障（由故障转移工具处理）

-- 2. 从节点提升（带错误处理）
DO $$
DECLARE
    v_promoted BOOLEAN;
BEGIN
    BEGIN
        -- 检查当前是否在恢复模式
        IF pg_i
```

**错误**: SELECT语句缺少FROM子句

---

**行 499** (sql):

```sql
-- 计划内故障转移流程（带完整错误处理）
-- 1. 停止主节点写操作（带错误处理）
DO $$
DECLARE
    v_paused BOOLEAN;
BEGIN
    BEGIN
        IF pg_is_in_recovery() THEN
            BEGIN
                SELECT pg_wal_replay_pause() INTO
```

**错误**: SELECT语句缺少FROM子句

---

**行 648** (sql):

```sql
-- 计划外故障转移流程（带完整错误处理）
-- 1. 检测主节点故障（带错误处理）
DO $$
DECLARE
    v_is_standby BOOLEAN;
BEGIN
    BEGIN
        SELECT pg_is_in_recovery() INTO v_is_standby;

        IF v_is_standby THEN
            RAISE
```

**错误**: SELECT语句缺少FROM子句

---

### 03-事务与并发\03.07-场景实践\高可用\流复制与CAP权衡.md

**行 532** (sql):

```sql
-- 异步流复制（AP模式，带完整错误处理）
DO $$
BEGIN
    BEGIN
        BEGIN
            ALTER SYSTEM SET synchronous_standby_names = '';
            RAISE NOTICE '同步备库名称已设置为空（AP模式，异步复制）';
        EXCEPTION

```

**错误**: 单引号不匹配

---

**行 570** (sql):

```sql
-- 动态切换到AP模式（带完整错误处理）
DO $$
DECLARE
    v_reloaded BOOLEAN;
BEGIN
    BEGIN
        BEGIN
            ALTER SYSTEM SET synchronous_standby_names = '';
            RAISE NOTICE '同步备库名称已设置为空（动态切换到AP模式）'
```

**错误**: 单引号不匹配; SELECT语句缺少FROM子句

---

### 03-事务与并发\03.07-场景实践\高可用\流复制与MVCC.md

**行 108** (sql):

```sql
-- 同步复制配置（postgresql.conf，带说明）
-- 注意：以下配置需要在postgresql.conf文件中设置，然后重启PostgreSQL
-- synchronous_standby_names = 'standby1,standby2'
-- synchronous_commit = on

-- 同步模式类型（带错误处理说明）：
DO $$
BEGIN
    BEGIN
```

**错误**: 单引号不匹配

---

**行 1027** (sql):

```sql
-- 从节点恢复（带错误处理）
-- 1. 检查WAL位置（带错误处理和性能测试）
DO $$
BEGIN
    BEGIN
        IF pg_is_in_recovery() THEN
            RAISE NOTICE '当前节点在恢复模式（从节点），开始检查WAL位置';
        ELSE
            RAISE WARNING '当前节点不在恢
```

**错误**: 单引号不匹配; SELECT语句缺少FROM子句

---

### 03-事务与并发\03.07-场景实践\高可用\逻辑复制与MVCC.md

**行 66** (sql):

```sql
-- 逻辑解码配置（带说明）
-- 注意：以下配置需要在postgresql.conf文件中设置，然后重启PostgreSQL
-- 发布端配置（postgresql.conf）
-- wal_level = logical;
-- max_replication_slots = 10;
-- max_wal_senders = 10;

-- 逻辑解码原理说明（带错误处理）
DO $$
BEGI
```

**错误**: 单引号不匹配

---

**行 168** (sql):

```sql
-- 创建订阅（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_publication WHERE pubname = 'my_publication') THEN
            RAISE WARNING '发布 my_publication 不存在，无法创建订阅';
            RE
```

**错误**: 单引号不匹配

---

### 03-事务与并发\03.07-场景实践\高可用\高可用最佳实践.md

**行 414** (sql):

```sql
-- 流复制性能优化配置（带完整错误处理）
-- 注意：这些配置需要在postgresql.conf中设置，或使用ALTER SYSTEM命令
-- 1. WAL优化（带错误处理）
DO $$
BEGIN
    BEGIN
        BEGIN
            ALTER SYSTEM SET wal_level = replica;
            RAISE NOTIC
```

**错误**: SELECT语句缺少FROM子句

---

### 03-事务与并发\03.10-锁升级与降级-安全性与死锁影响的形式证明.md

**行 507** (sql):

```sql
-- PostgreSQL 18：手动锁升级（从行锁到表锁，带错误处理）
DO $$
BEGIN
    BEGIN
        CREATE OR REPLACE FUNCTION upgrade_to_table_lock(
            table_name TEXT
        ) RETURNS VOID AS $$
        DECLARE

```

**错误**: 单引号不匹配

---

### 03-事务与并发\11-锁机制深度解析.md

**行 39** (sql):

```sql
-- 锁冲突矩阵
/*
                AS  RS  RE  SUE  S  SRE  E  AE
ACCESS SHARE     -   -   -   -   -   -   -   ✗
ROW SHARE        -   -   -   -   -   -   ✗   ✗
ROW EXCLUSIVE    -   -   -   -   ✗   ✗   ✗   ✗

```

**错误**: SELECT语句缺少FROM子句

---

**行 513** (sql):

```sql
-- 会话级锁
SELECT pg_advisory_lock(12345);
-- 执行临界区代码
SELECT pg_advisory_unlock(12345);

-- 事务级锁（自动释放）
BEGIN;
SELECT pg_advisory_xact_lock(12345);
-- 执行操作
COMMIT;  -- 自动释放

-- 尝试获取（非阻塞）
SELECT pg_try_adv
```

**错误**: SELECT语句缺少FROM子句

---

### 03-事务与并发\CAP理论\BASE理论详解.md

**行 176** (sql):

```sql
-- 异步复制（基本可用，带完整错误处理）
DO $$
BEGIN
    BEGIN
        BEGIN
            ALTER SYSTEM SET synchronous_standby_names = '';
            RAISE NOTICE '同步备库名称已设置为空（基本可用，异步复制）';
        EXCEPTION

```

**错误**: 单引号不匹配

---

**行 239** (sql):

```sql
-- 异步复制（软状态，带完整错误处理）
DO $$
BEGIN
    BEGIN
        BEGIN
            ALTER SYSTEM SET synchronous_standby_names = '';
            RAISE NOTICE '同步备库名称已设置为空（软状态，异步复制）';
        EXCEPTION
            WH
```

**错误**: 单引号不匹配

---

**行 300** (sql):

```sql
-- 异步复制（最终一致性，带完整错误处理）
DO $$
BEGIN
    BEGIN
        BEGIN
            ALTER SYSTEM SET synchronous_standby_names = '';
            RAISE NOTICE '同步备库名称已设置为空（最终一致性，异步复制）';
        EXCEPTION

```

**错误**: 单引号不匹配

---

**行 341** (sql):

```sql
-- BASE模式配置（带完整错误处理）
DO $$
BEGIN
    BEGIN
        BEGIN
            ALTER SYSTEM SET synchronous_standby_names = '';  -- 基本可用
            RAISE NOTICE '同步备库名称已设置为空（BASE模式：基本可用）';
        EXCEPTION

```

**错误**: 单引号不匹配

---

### 03-事务与并发\CAP理论\CAP与分布式系统设计.md

**行 157** (sql):

```sql
-- 支付服务：CP模式（带完整错误处理）
DO $$
BEGIN
    BEGIN
        BEGIN
            ALTER SYSTEM SET synchronous_standby_names = 'standby1,standby2';
            RAISE NOTICE '支付服务：同步备库名称已设置为 standby1,standby2（CP模式
```

**错误**: 单引号不匹配

---

**行 336** (sql):

```sql
-- AP模式配置（带完整错误处理）
DO $$
BEGIN
    BEGIN
        BEGIN
            ALTER SYSTEM SET synchronous_standby_names = '';
            RAISE NOTICE '同步备库名称已设置为空（AP模式，异步复制）';
        EXCEPTION
            WHE
```

**错误**: 单引号不匹配

---

### 03-事务与并发\CAP理论\CAP定理完整定义与证明.md

**行 291** (sql):

```sql
-- 异步复制配置（AP模式，带错误处理）
DO $$
BEGIN
    -- 检查是否为超级用户
    IF NOT current_setting('is_superuser')::boolean THEN
        RAISE EXCEPTION '需要超级用户权限才能修改系统配置';
    END IF;

    ALTER SYSTEM SET synchronous_st
```

**错误**: 单引号不匹配

---

**行 392** (sql):

```sql
-- 主库配置
synchronous_standby_names = ''
synchronous_commit = 'local'

-- AP模式特征：
-- ❌ 弱一致性：主库立即提交，备库可能延迟
-- ✅ 高可用性：分区时，主库继续服务
-- ✅ 分区容错：系统在网络分区时继续运行

```

**错误**: 单引号不匹配

---

**行 428** (sql):

```sql
-- 根据场景动态调整
-- 金融交易：使用CP模式
ALTER SYSTEM SET synchronous_standby_names = 'standby1,standby2';
ALTER SYSTEM SET synchronous_commit = 'remote_apply';

-- 日志写入：使用AP模式
ALTER SYSTEM SET synchronous_standby_
```

**错误**: 单引号不匹配

---

### 03-事务与并发\CAP理论\CAP权衡决策框架.md

**行 641** (sql):

```sql
-- AP模式配置（带完整错误处理）
DO $$
BEGIN
    BEGIN
        BEGIN
            ALTER SYSTEM SET synchronous_standby_names = '';
            RAISE NOTICE '同步备库名称已设置为空（AP模式，异步复制）';
        EXCEPTION
            WHE
```

**错误**: 单引号不匹配

---

**行 692** (sql):

```sql
-- AP模式配置（只读备库，带完整错误处理）
-- 主库：异步复制（带错误处理）
DO $$
BEGIN
    BEGIN
        BEGIN
            ALTER SYSTEM SET synchronous_standby_names = '';
            RAISE NOTICE '主库：同步备库名称已设置为空（AP模式，异步复制）';

```

**错误**: 单引号不匹配

---

**行 745** (sql):

```sql
-- AP模式配置（带完整错误处理）
DO $$
BEGIN
    BEGIN
        BEGIN
            ALTER SYSTEM SET synchronous_standby_names = '';
            RAISE NOTICE '同步备库名称已设置为空（AP模式，异步复制）';
        EXCEPTION
            WHE
```

**错误**: 单引号不匹配

---

**行 783** (sql):

```sql
-- 异步复制（AP模式，带完整错误处理）
DO $$
BEGIN
    BEGIN
        BEGIN
            ALTER SYSTEM SET synchronous_standby_names = '';
            RAISE NOTICE '同步备库名称已设置为空（AP模式，异步复制）';
        EXCEPTION

```

**错误**: 单引号不匹配

---

**行 960** (sql):

```sql
-- AP模式配置
ALTER SYSTEM SET synchronous_standby_names = '';
ALTER SYSTEM SET synchronous_commit = 'local';
ALTER SYSTEM SET default_transaction_isolation = 'read committed';

```

**错误**: 单引号不匹配

---

**行 995** (sql):

```sql
-- 动态切换到AP模式（提高可用性）
ALTER SYSTEM SET synchronous_standby_names = '';
SELECT pg_reload_conf();

-- 动态切换到CP模式（提高一致性）
ALTER SYSTEM SET synchronous_standby_names = 'standby1,standby2';
SELECT pg_reload_co
```

**错误**: 单引号不匹配; SELECT语句缺少FROM子句

---

### 03-事务与并发\CAP理论\PACELC定理详解.md

**行 356** (sql):

```sql
-- 配置异步复制（默认，带完整错误处理）
DO $$
BEGIN
    BEGIN
        BEGIN
            ALTER SYSTEM SET synchronous_standby_names = '';
            RAISE NOTICE '同步备库名称已设置为空（异步复制，AP/EL模式）';
        EXCEPTION

```

**错误**: 单引号不匹配

---

### 03-事务与并发\CAP理论\一致性模型详解.md

**行 298** (sql):

```sql
-- 异步复制实现最终一致性（带完整错误处理）
DO $$
BEGIN
    BEGIN
        BEGIN
            ALTER SYSTEM SET synchronous_standby_names = '';
            RAISE NOTICE '同步备库名称已设置为空（最终一致性，异步复制）';
        EXCEPTION

```

**错误**: 单引号不匹配

---

### 03-事务与并发\CAP理论\分区容错实现机制.md

**行 284** (sql):

```sql
-- AP模式：异步复制（带完整错误处理）
DO $$
BEGIN
    BEGIN
        BEGIN
            ALTER SYSTEM SET synchronous_standby_names = '';
            RAISE NOTICE '同步备库名称已设置为空（AP模式：异步复制）';
        EXCEPTION

```

**错误**: 单引号不匹配

---

**行 377** (sql):

```sql
-- AP模式：异步复制，最终一致性（带完整错误处理）
DO $$
BEGIN
    BEGIN
        BEGIN
            ALTER SYSTEM SET synchronous_standby_names = '';
            RAISE NOTICE '同步备库名称已设置为空（AP模式：异步复制，最终一致性）';
        EXCEPTION

```

**错误**: 单引号不匹配

---

### 03-事务与并发\CAP理论\可用性量化与测量.md

**行 210** (sql):

```sql
-- 健康检查查询（带完整错误处理和性能测试）
DO $$
DECLARE
    v_health_check INTEGER;
BEGIN
    BEGIN
        BEGIN
            EXPLAIN (ANALYZE, BUFFERS, TIMING)
            SELECT 1 INTO v_health_check;

            IF
```

**错误**: SELECT语句缺少FROM子句

---

### 03-事务与并发\PostgreSQL版本特性\pg17-vacuum-memory.md

**行 658** (sql):

```sql
-- 1. 设置autovacuum_work_mem
-- 建议：maintenance_work_mem的50-70%
ALTER SYSTEM SET autovacuum_work_mem = '2GB';

-- 2. 调整max_parallel_maintenance_workers
-- 根据新内存管理，可以适当增加
ALTER SYSTEM SET max_parallel_ma
```

**错误**: SELECT语句缺少FROM子句

---

### 03-事务与并发\PostgreSQL版本特性\pg18-virtual-columns.md

**行 350** (sql):

```sql
-- 测试场景：查询1000万行

-- 存储列：
-- SELECT time：10秒
-- 直接读取total_amount

-- 虚拟列：
-- SELECT time：12秒（20%下降）
-- 需要计算total_amount

-- 下降：20%
-- 原因：计算开销

-- 优化：如果total_amount有索引
-- 虚拟列：10秒（与存储列相同）
-- 原因：索引存储计算值

```

**错误**: SELECT语句缺少FROM子句

---

### 03-事务与并发\事务模型\两阶段提交深度分析.md

**行 698** (sql):

```sql
-- PostgreSQL跨数据库事务（使用dblink）

-- 创建dblink扩展
CREATE EXTENSION dblink;

-- 跨数据库事务
BEGIN;
-- 本地操作
UPDATE local_accounts SET balance = balance - 100 WHERE id = 1;

-- 远程操作
SELECT dblink_exec('remote_db',
```

**错误**: SELECT语句缺少FROM子句

---

### 04-存储与恢复\01.06-存储管理与数据持久化.md

**行 1173** (sql):

```sql
-- 查看恢复信息
SELECT
    pg_is_in_recovery(),
    pg_last_wal_receive_lsn(),
    pg_last_wal_replay_lsn(),
    pg_wal_lsn_diff(pg_last_wal_receive_lsn(), pg_last_wal_replay_lsn()) as replay_lag_bytes;

--
```

**错误**: SELECT语句缺少FROM子句

---

**行 2234** (sql):

```sql
-- 大表分区策略
CREATE TABLE log_entries (
    id BIGSERIAL,
    log_time TIMESTAMP,
    level VARCHAR(10),
    message TEXT,
    source VARCHAR(100)
) PARTITION BY RANGE (log_time);

-- 按月分区
CREATE TABLE l
```

**错误**: 单引号不匹配

---

**行 2335** (sql):

```sql
-- 1. 创建分区表（按月分区）
CREATE TABLE application_logs (
    id BIGSERIAL,
    log_time TIMESTAMP NOT NULL,
    level VARCHAR(10) NOT NULL,
    application VARCHAR(50),
    module VARCHAR(50),
    message TE
```

**错误**: 单引号不匹配

---

### 04-存储与恢复\06.03-ARIES日志恢复-正确性与不变式.md

**行 721** (sql):

```sql
-- PostgreSQL 18：分析阶段（自动执行）
-- 系统启动时自动执行，确定：
-- 1. 最后一个检查点位置
-- 2. 所有活跃事务

-- PostgreSQL 18：重做阶段（自动执行）
-- 从检查点开始，按LSN顺序重做所有日志记录
-- 使用PageLSN避免重复重做（幂等性）

-- PostgreSQL 18：撤销阶段（自动执行）
-- 撤销所有未提交事务的修改
--
```

**错误**: SELECT语句缺少FROM子句

---

### 04-存储与恢复\06.08-数据库容错与高可用-故障模型与恢复策略的形式化.md

**行 797** (sql):

```sql
-- 场景：电商系统高可用优化（带错误处理）
-- 1. 配置异步复制（性能优先，带错误处理）
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = current_user AND rolsuper = true) THEN
        RAISE EXCEPTION '需要超级用户权限来配置系统参数';

```

**错误**: 单引号不匹配

---

**行 928** (sql):

```sql
-- 1. 高可用方案选择（带错误处理）
-- 零数据丢失：同步复制 + pg_auto_failover
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = current_user AND rolsuper = true) THEN
        RAISE EXCEPTION '需要超级用户权限来配置系
```

**错误**: 单引号不匹配

---

### 04-存储与恢复\【深入】PostgreSQL备份恢复完善-PITR与灾备演练指南.md

**行 266** (sql):

```sql
-- 记录当前事务ID
SELECT txid_current();  -- 假设：1000

-- 执行一些操作
INSERT INTO test VALUES (1);
INSERT INTO test VALUES (2);  -- txid: 1001
INSERT INTO test VALUES (3);  -- txid: 1002

-- 恢复到txid 1001（包含id=1和i
```

**错误**: SELECT语句缺少FROM子句

---

**行 283** (sql):

```sql
-- 记录当前LSN（带错误处理）
DO $$
DECLARE
    current_lsn TEXT;
BEGIN
    SELECT pg_current_wal_lsn()::TEXT INTO current_lsn;
    RAISE NOTICE '当前LSN: %', current_lsn;
EXCEPTION
    WHEN OTHERS THEN
        RAI
```

**错误**: SELECT语句缺少FROM子句

---

**行 1474** (sql):

```sql
-- 创建校验和表（备份时，带错误处理）
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'backup_checksums') THEN
        DROP TABLE backup_checksums;

```

**错误**: 单引号不匹配

---

### 04-存储与恢复\备份与恢复.md

**行 685** (sql):

```sql
-- 创建恢复点（带错误处理）
DO $$
DECLARE
    restore_point_name TEXT := 'before_migration';
    lsn TEXT;
BEGIN
    BEGIN
        SELECT pg_create_restore_point(restore_point_name) INTO lsn;
        RAISE NOTICE
```

**错误**: SELECT语句缺少FROM子句

---

**行 1186** (sql):

```sql
   -- ✅ 好：使用pg_cron自动备份
   CREATE EXTENSION pg_cron;

   -- 每日备份
   SELECT cron.schedule(
       'daily-backup',
       '0 2 * * *',
       $$pg_dump -Fc -f /backup/daily_$(date +\%Y\%m\%d).dump mydb$
```

**错误**: SELECT语句缺少FROM子句

---

### 04-存储与恢复\备份恢复体系详解.md

**行 701** (sql):

```sql
-- recovery配置（PostgreSQL 12+，在postgresql.auto.conf中配置）
-- 注意：这些配置需要在恢复配置文件中设置，不能通过SQL直接设置

-- restore_command = 'cp /backup/wal/%f %p'
-- recovery_target_time = '2025-11-01 12:00:00'
-- recovery_targe
```

**错误**: SELECT语句缺少FROM子句

---

### 04-存储与恢复\存储与备份恢复场景分析指南.md

**行 448** (sql):

```sql
-- 创建自动分区函数（带错误处理）
-- 创建月度分区函数（带完整错误处理）
CREATE OR REPLACE FUNCTION create_monthly_partition(
    p_table_name TEXT,
    p_start_date DATE
)
RETURNS VOID
LANGUAGE plpgsql
AS $$
DECLARE
    v_partition_
```

**错误**: 单引号不匹配

---

**行 674** (sql):

```sql
-- 创建归档函数
-- 归档旧分区函数（带完整错误处理）
CREATE OR REPLACE FUNCTION archive_old_partitions()
RETURNS VOID
LANGUAGE plpgsql
AS $$
DECLARE
    v_partition_name TEXT;
    v_archive_date DATE;
    v_partition_count
```

**错误**: 单引号不匹配

---

**行 2033** (sql):

```sql
-- PostgreSQL 17+支持pg_read_csv函数，可以直接读取CSV文件
-- 创建归档数据查询函数（带错误处理）
CREATE OR REPLACE FUNCTION query_archive_csv(p_file_path TEXT)
RETURNS TABLE (
    id INTEGER,
    data TEXT,
    created_at TIMESTAMP
```

**错误**: 单引号不匹配

---

### 05-安全与合规\07.03-行级安全-RLS策略语义与不可逃逸性证明.md

**行 527** (sql):

```sql
-- 1. 简单策略（单条件）
CREATE POLICY simple_policy ON accounts
    FOR SELECT
    USING (user_id = 1);

-- 2. 组合策略（多条件OR）
CREATE POLICY manager_policy ON accounts
    FOR ALL
    USING (
        user_id = cu
```

**错误**: SELECT语句缺少FROM子句

---

### 05-安全与合规\07.04-数据库安全模型-访问控制与信息流安全的形式化.md

**行 575** (sql):

```sql
-- 测试1：令牌过期
SELECT verify_oauth2_token(
    '{"alg":"RS256","typ":"JWT"}',
    '{"sub":"user123","exp":1000000000,"scope":["read"]}'::JSON,  -- 已过期的时间戳
    'signature_here',
    'read'
); -- 应返回false

```

**错误**: SELECT语句缺少FROM子句

---

### 05-安全与合规\07.05-数据库审计与合规-完整性约束与审计轨迹的形式化.md

**行 814** (sql):

```sql
-- 场景：金融系统审计与合规（带错误处理）
-- 1. 启用pgAudit扩展（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'pgaudit') THEN
            CREATE EXTENSION pgaudit;

```

**错误**: 单引号不匹配

---

### 05-安全与合规\AI-Act合规\AI-Act要求解读.md

**行 483** (sql):

```sql
-- 数据分类表（带错误处理）
DO $$
BEGIN
    BEGIN
        -- 检查表是否已存在
        IF EXISTS (
            SELECT 1 FROM information_schema.tables
            WHERE table_schema = 'public' AND table_name = 'data_class
```

**错误**: 单引号不匹配

---

### 05-安全与合规\AI-Act合规\合规实施方案.md

**行 513** (sql):

```sql
-- 步骤 1: 创建审计日志表
CREATE TABLE IF NOT EXISTS audit_log (
    id BIGSERIAL PRIMARY KEY,
    table_name TEXT NOT NULL,
    operation TEXT NOT NULL,  -- 'INSERT', 'UPDATE', 'DELETE'
    old_data JSONB,

```

**错误**: 单引号不匹配

---

**行 644** (sql):

```sql
-- 步骤 1: 配置数据留存策略（带错误处理）
CREATE OR REPLACE FUNCTION configure_retention_policy(
    p_table_name TEXT,
    p_retention_period INTERVAL
)
RETURNS void AS $$
BEGIN
    -- 输入验证
    IF p_table_name IS NUL
```

**错误**: 单引号不匹配

---

**行 950** (sql):

```sql
   -- 检查PostgreSQL版本（需要18+）
   SELECT version();
   -- 应该显示PostgreSQL 18.x或更高版本

```

**错误**: SELECT语句缺少FROM子句

---

**行 1008** (sql):

```sql
   -- 配置扩展参数（可选）
   ALTER SYSTEM SET pg_dsr.enable_sovereignty = 'on';
   ALTER SYSTEM SET pg_dsr.enable_retention = 'on';
   ALTER SYSTEM SET pg_dsr.enable_audit = 'on';
   SELECT pg_reload_conf();

```

**错误**: SELECT语句缺少FROM子句

---

**行 1018** (sql):

```sql
-- 验证扩展功能
SELECT
    pg_dsr.version() AS extension_version,
    pg_dsr.is_compliance_enabled() AS compliance_enabled,
    pg_dsr.is_sovereignty_enabled() AS sovereignty_enabled,
    pg_dsr.is_retentio
```

**错误**: SELECT语句缺少FROM子句

---

**行 1567** (sql):

```sql
     -- 创建基于主权标签的RLS策略
     CREATE POLICY sovereignty_access_policy ON user_data
     FOR SELECT
     USING (
         data_sovereignty && ARRAY[current_setting('app.user_sovereignty', true)]
     );

```

**错误**: SELECT语句缺少FROM子句

---

**行 2002** (sql):

```sql
   -- 重新启用合规功能
   SELECT pg_dsr.enable_compliance();

```

**错误**: SELECT语句缺少FROM子句

---

### 05-安全与合规\AI-Act合规\合规检查清单.md

**行 195** (sql):

```sql
-- 检查数据留存策略配置函数（带完整错误处理）
CREATE OR REPLACE FUNCTION check_retention_policies()
RETURNS TABLE (
    table_name TEXT,
    has_policy BOOLEAN,
    policy_name TEXT,
    retention_period INTERVAL,
    sta
```

**错误**: 单引号不匹配

---

### 05-安全与合规\PostgreSQL-18.1-安全修复说明.md

**行 258** (sql):

```sql
   -- 攻击者控制的查询返回大量数据
   SELECT array_agg(generate_series(1, 999999999999));

```

**错误**: SELECT语句缺少FROM子句

---

### 05-安全与合规\【深入】PostgreSQL安全深化-RLS与审计完整指南.md

**行 2411** (sql):

```sql
-- 添加噪声函数（满足epsilon-差分隐私，带完整错误处理）
CREATE OR REPLACE FUNCTION add_laplace_noise(value numeric, epsilon numeric DEFAULT 0.1)
RETURNS numeric AS $$
DECLARE
    sensitivity numeric := 1.0;
    scale numer
```

**错误**: 括号不匹配

---

**行 3119** (sql):

```sql
-- SQL注入测试（带完整错误处理）
-- 测试1：基础SQL注入（演示不安全做法，带错误处理）
DO $$
DECLARE
    malicious_input text := $$' OR '1'='1$$;
    result text;
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.ta
```

**错误**: 单引号不匹配

---

**行 3188** (sql):

```sql
-- SQL注入防护清单（带错误处理）
-- ✅ 安全：使用参数化查询（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'users') THEN

```

**错误**: 单引号不匹配

---

**行 4256** (sql):

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
WHERE rolvalidu
```

**错误**: 单引号不匹配

---

### 05-安全与合规\【深入】数据溯源与血缘分析完整指南.md

**行 1219** (sql):

```sql
-- 正向追踪：从数据源追踪到数据目标
CREATE OR REPLACE FUNCTION forward_track_lineage(
    p_source_schema VARCHAR(100),
    p_source_table VARCHAR(100),
    p_source_column VARCHAR(100),
    p_max_depth INTEGER DEFAU
```

**错误**: 单引号不匹配

---

**行 1279** (sql):

```sql
-- 反向追踪：从数据目标追溯到数据源
CREATE OR REPLACE FUNCTION backward_track_lineage(
    p_target_schema VARCHAR(100),
    p_target_table VARCHAR(100),
    p_target_column VARCHAR(100),
    p_max_depth INTEGER DEFA
```

**错误**: 单引号不匹配

---

**行 1828** (sql):

```sql
-- 1. 启用溯源追踪
SET provsql.enable = on;

-- 2. 创建溯源表
CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    customer_id INTEGER,
    amount DECIMAL(10, 2),
    order_date DATE
);

-- 3. 插入数据（自动记录溯源）
```

**错误**: SELECT语句缺少FROM子句

---

**行 1856** (sql):

```sql
-- 将ProvSQL的溯源信息同步到自定义溯源表
CREATE OR REPLACE FUNCTION sync_provsql_lineage()
RETURNS TRIGGER AS $$
DECLARE
    v_provenance JSONB;
BEGIN
    -- 获取ProvSQL溯源信息
    SELECT provsql.provenance_of(TG_TABLE_N
```

**错误**: SELECT语句缺少FROM子句

---

### 05-安全与合规\【深入】联邦学习与隐私计算完整指南.md

**行 1949** (sql):

```sql
-- 医院A数据库配置
-- 1. 创建患者数据表
CREATE TABLE patients (
    id SERIAL PRIMARY KEY,
    age INTEGER,
    gender VARCHAR(10),
    symptoms TEXT,
    lab_results JSONB,
    diagnosis VARCHAR(100),
    created_
```

**错误**: SELECT语句缺少FROM子句

---

### 05-安全与合规\加密查询\加密查询性能测试.md

**行 713** (python):

```python
     from functools import lru_cache

     @lru_cache(maxsize=10000)
     def decrypt_cached(encrypted_value, key):
         return decrypt(encrypted_value, key)

```

**错误**: 语法错误: unexpected indent (行 1)

---

**行 726** (python):

```python
     def encrypt_batch(values, key):
         return [encrypt(v, key) for v in values]

```

**错误**: 语法错误: unexpected indent (行 1)

---

**行 738** (python):

```python
     def paillier_sum_batch(encrypted_values):
         result = encrypted_values[0]
         for val in encrypted_values[1:]:
             result = public_key.add(result, val)
         return result

```

**错误**: 语法错误: unexpected indent (行 1)

---

**行 751** (python):

```python
     import cupy as cp

     def paillier_gpu(encrypted_values):
         # GPU并行计算
         return cp.array([paillier_op(v) for v in encrypted_values])

```

**错误**: 语法错误: unexpected indent (行 1)

---

**行 832** (python):

```python
     def select_encryption_scheme(query):
         if 'SUM' in query or 'AVG' in query:
             return 'paillier'
         elif 'BETWEEN' in query or '>' in query:
             return 'ope'

```

**错误**: 语法错误: unexpected indent (行 1)

---

**行 849** (python):

```python
     def adjust_encryption_scheme(performance_requirement):
         if performance_requirement == 'high':
             return 'deterministic'  # 性能优先
         elif performance_requirement == 'balance
```

**错误**: 语法错误: unexpected indent (行 1)

---

### 05-安全与合规\加密查询\同态加密集成.md

**行 1075** (sql):

```sql
-- 创建密钥管理表（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'encryption_keys') THEN
            CREATE TABLE e
```

**错误**: 单引号不匹配

---

**行 1180** (sql):

```sql
-- 创建加密函数
CREATE OR REPLACE FUNCTION paillier_encrypt(
    plain_value INTEGER,
    public_key BYTEA
) RETURNS BYTEA AS $$
    -- 调用Python函数进行加密
    SELECT python_function('encrypt', plain_value, publ
```

**错误**: SELECT语句缺少FROM子句

---

### 05-安全与合规\加密查询\混合加密查询原理.md

**行 453** (sql):

```sql
-- 创建缓存表（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'decryption_cache') THEN
            CREATE TABLE de
```

**错误**: 单引号不匹配

---

**行 1105** (sql):

```sql
-- 创建密钥管理表（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'encryption_keys') THEN
            CREATE TABLE e
```

**错误**: 单引号不匹配

---

**行 1737** (sql):

```sql
-- 创建密钥访问控制表（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'key_access_control') THEN
            CREATE TA
```

**错误**: 单引号不匹配

---

### 05-安全与合规\安全与加密.md

**行 1693** (sql):

```sql
-- ✅ 好：使用pgAudit扩展进行细粒度审计
CREATE EXTENSION IF NOT EXISTS pgaudit;

-- 配置pgAudit
ALTER SYSTEM SET pgaudit.log = 'read,write,ddl';
ALTER SYSTEM SET pgaudit.log_catalog = off;
ALTER SYSTEM SET pgaudit.lo
```

**错误**: SELECT语句缺少FROM子句

---

### 05-安全与合规\安全体系详解.md

**行 1342** (sql):

```sql
     -- 创建只读角色
     CREATE ROLE readonly_role;
     GRANT CONNECT ON DATABASE mydb TO readonly_role;
     GRANT SELECT ON ALL TABLES IN SCHEMA public TO readonly_role;

     -- 创建读写角色
     CREATE ROLE
```

**错误**: SELECT语句缺少FROM子句

---

**行 1420** (sql):

```sql
     -- 配置密码加密方式
     ALTER SYSTEM SET password_encryption = 'scram-sha-256';
     SELECT pg_reload_conf();

     -- 创建用户时自动使用SCRAM-SHA-256
     CREATE USER app_user WITH PASSWORD 'secure_password_123
```

**错误**: SELECT语句缺少FROM子句

---

**行 1442** (sql):

```sql
     -- 启用SSL/TLS
     ALTER SYSTEM SET ssl = on;
     ALTER SYSTEM SET ssl_cert_file = '/etc/ssl/certs/server.crt';
     ALTER SYSTEM SET ssl_key_file = '/etc/ssl/private/server.key';
     SELECT pg_
```

**错误**: SELECT语句缺少FROM子句

---

**行 1500** (sql):

```sql
     -- 启用审计日志
     ALTER SYSTEM SET log_statement = 'all';
     ALTER SYSTEM SET log_connections = on;
     ALTER SYSTEM SET log_disconnections = on;
     ALTER SYSTEM SET log_duration = on;
     SEL
```

**错误**: SELECT语句缺少FROM子句

---

**行 1686** (sql):

```sql
-- 1. 列级权限
GRANT SELECT (id, name, email) ON users TO app_user;
-- 用户只能查询特定列

-- 2. 行级权限（RLS）
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;
CREATE POLICY orders_user_policy ON orders
    FOR SELECT

```

**错误**: SELECT语句缺少FROM子句

---

**行 1729** (sql):

```sql
   -- ✅ 好：只授予必要权限
   CREATE ROLE app_user;
   GRANT CONNECT ON DATABASE mydb TO app_user;
   GRANT SELECT, INSERT, UPDATE ON orders TO app_user;
   -- 不授予DELETE权限，除非必要

```

**错误**: SELECT语句缺少FROM子句

---

**行 1767** (sql):

```sql
   -- ❌ 不好：授予过多权限
   GRANT ALL ON DATABASE mydb TO app_user;

   -- ✅ 好：最小权限原则
   GRANT CONNECT ON DATABASE mydb TO app_user;
   GRANT SELECT, INSERT, UPDATE ON orders TO app_user;

```

**错误**: SELECT语句缺少FROM子句

---

### 05-安全与合规\安全加固\PostgreSQL安全加固完整指南.md

**行 198** (sql):

```sql
     ALTER SYSTEM SET password_encryption = 'scram-sha-256';
     SELECT pg_reload_conf();

```

**错误**: SELECT语句缺少FROM子句

---

### 05-安全与合规\安全加固\安全事件响应.md

**行 186** (sql):

```sql
-- 创建事件严重程度评估函数
CREATE OR REPLACE FUNCTION assess_event_severity(
    p_event_type TEXT,
    p_data_affected BIGINT,
    p_system_affected BOOLEAN,
    p_business_impact TEXT
) RETURNS TEXT AS $$
DECL
```

**错误**: SELECT语句缺少FROM子句

---

### 05-安全与合规\安全加固\漏洞管理.md

**行 205** (sql):

```sql
-- 如果无法立即修复，实施临时缓解措施（带错误处理，需要超级用户权限）
DO $$
DECLARE
    current_user_super BOOLEAN;
BEGIN
    BEGIN
        -- 检查是否有超级用户权限
        SELECT rolsuper INTO current_user_super
        FROM pg_roles

```

**错误**: 单引号不匹配

---

### 05-安全与合规\安全架构设计与场景分析指南.md

**行 2388** (sql):

```sql
-- 创建角色管理函数（带错误处理）
DO $$
BEGIN
    BEGIN
        CREATE OR REPLACE FUNCTION grant_role_permissions(
            p_role_name TEXT,
            p_schema_name TEXT,
            p_permissions TEXT[]

```

**错误**: SELECT语句缺少FROM子句

---

**行 3963** (sql):

```sql
-- 选型决策函数
CREATE OR REPLACE FUNCTION select_encryption_solution(
    encryption_scope VARCHAR,
    performance_req VARCHAR,
    db_admin_trust BOOLEAN,
    budget_constraint VARCHAR
) RETURNS VARCHAR
```

**错误**: SELECT语句缺少FROM子句

---

**行 5312** (sql):

```sql
-- 创建基础角色模板
CREATE ROLE tenant_admin_template NOLOGIN;
CREATE ROLE tenant_user_template NOLOGIN;
CREATE ROLE tenant_readonly_template NOLOGIN;

-- 租户管理员权限
GRANT USAGE ON SCHEMA public TO tenant_admin_
```

**错误**: SELECT语句缺少FROM子句

---

**行 5927** (sql):

```sql
-- 1. 配置SSL/TLS加密
ALTER SYSTEM SET ssl = on;
ALTER SYSTEM SET ssl_cert_file = '/etc/ssl/certs/server.crt';
ALTER SYSTEM SET ssl_key_file = '/etc/ssl/private/server.key';
SELECT pg_reload_conf();

-- 2
```

**错误**: SELECT语句缺少FROM子句

---

**行 5953** (sql):

```sql
-- 1. 设计角色层次结构
CREATE ROLE base_readonly;
CREATE ROLE base_readwrite;
CREATE ROLE base_admin;

-- 2. 实现角色继承
GRANT base_readonly TO base_readwrite;
GRANT base_readwrite TO base_admin;

-- 3. 授予数据库权限
GR
```

**错误**: SELECT语句缺少FROM子句

---

### 05-安全与合规\审计与脱敏\不可篡改审计日志.md

**行 455** (sql):

```sql
-- 创建备份表（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'user_data_ledger') THEN
            RAISE WARNING '
```

**错误**: 括号不匹配

---

### 05-安全与合规\审计与脱敏\动态数据脱敏.md

**行 490** (sql):

```sql
-- 优化脱敏函数（使用 C 语言扩展，带错误处理）
CREATE OR REPLACE FUNCTION mask_email_fast(email TEXT)
RETURNS TEXT AS $$
BEGIN
    -- 参数验证
    IF email IS NULL OR email = '' THEN
        RETURN email;
    END IF;

    BE
```

**错误**: 单引号不匹配

---

### 05-安全与合规\审计与脱敏\细粒度权限控制.md

**行 372** (sql):

```sql
-- 基于数据内容的列权限（带错误处理）
CREATE OR REPLACE FUNCTION has_column_permission_dynamic(
    p_table_name TEXT,
    p_column_name TEXT,
    p_record_data JSONB
)
RETURNS BOOLEAN AS $$
DECLARE
    v_role TEXT;

```

**错误**: SELECT语句缺少FROM子句

---

**行 804** (sql):

```sql
-- 为权限检查创建索引
CREATE INDEX idx_user_data_sovereignty ON user_data USING GIN (data_sovereignty);

-- 优化 RLS 策略（使用索引）
CREATE POLICY "optimized_sovereignty_access"
ON user_data FOR SELECT
USING (
    data
```

**错误**: SELECT语句缺少FROM子句

---

### 05-安全与合规\技术原理\审计日志机制.md

**行 390** (sql):

```sql
-- 创建审计触发器函数（带错误处理）
DO $$
BEGIN
    BEGIN
        CREATE OR REPLACE FUNCTION audit_trigger()
        RETURNS TRIGGER AS $$
        DECLARE
            prev_hash TEXT;
            curr_hash TEXT;

```

**错误**: 单引号不匹配

---

**行 929** (sql):

```sql
-- 1. 创建不可篡改审计日志表
CREATE TABLE audit_log (
    id SERIAL PRIMARY KEY,
    table_name TEXT NOT NULL,
    operation TEXT NOT NULL,
    old_data JSONB,
    new_data JSONB,
    user_name TEXT,
    ip_addr
```

**错误**: 单引号不匹配

---

### 05-安全与合规\技术原理\数据主权技术.md

**行 437** (sql):

```sql
-- 自动标签分配函数（带错误处理）
DO $$
BEGIN
    BEGIN
        CREATE OR REPLACE FUNCTION auto_assign_sovereignty_tags(
            p_table_name TEXT,
            p_column_name TEXT,
            p_condition TEXT

```

**错误**: 单引号不匹配

---

**行 563** (sql):

```sql
-- 标签更新函数（带错误处理）
DO $$
BEGIN
    BEGIN
        CREATE OR REPLACE FUNCTION update_sovereignty_tag(
            p_tag_id INTEGER,
            p_new_value TEXT,
            p_description TEXT DEFAULT NUL
```

**错误**: 单引号不匹配

---

**行 1276** (sql):

```sql
-- 1. 安装 pg_dsr 扩展
CREATE EXTENSION IF NOT EXISTS pg_dsr;

-- 2. 配置数据主权策略
ALTER SYSTEM SET pg_dsr.enable_row_labels = on;
ALTER SYSTEM SET pg_dsr.enable_cross_border_control = on;
ALTER SYSTEM SET pg_
```

**错误**: SELECT语句缺少FROM子句

---

### 05-安全与合规\技术原理\数据库合规架构.md

**行 390** (sql):

```sql
-- 基于标签的访问控制策略
CREATE POLICY sovereignty_policy ON user_data
FOR SELECT
USING (
    -- 检查数据主权标签
    CASE
        WHEN data_sovereignty = 'EU' THEN
            current_setting('pg_dsr.allowed_regions')
```

**错误**: SELECT语句缺少FROM子句

---

**行 926** (sql):

```sql
-- 启用 pg_dsr 插件
CREATE EXTENSION IF NOT EXISTS pg_dsr;

-- 配置合规策略
ALTER SYSTEM SET pg_dsr.enable_row_labels = ON;
ALTER SYSTEM SET pg_dsr.enable_cross_border_control = ON;
ALTER SYSTEM SET pg_dsr.enab
```

**错误**: SELECT语句缺少FROM子句

---

**行 942** (sql):

```sql
-- 创建带主权标签的表
CREATE TABLE user_data (
    id SERIAL PRIMARY KEY,
    name TEXT,
    email TEXT,
    country TEXT,

    -- 主权标签
    data_sovereignty TEXT DEFAULT 'GLOBAL',

    -- 分类标签
    data_classif
```

**错误**: SELECT语句缺少FROM子句

---

**行 1266** (sql):

```sql
-- 设置告警阈值
SELECT pg_dsr.set_alert_threshold(
    min_violations_per_hour = 10,
    alert_email = 'compliance@example.com',
    alert_webhook = 'https://example.com/compliance-alert'
);

```

**错误**: SELECT语句缺少FROM子句

---

**行 1464** (sql):

```sql
-- 1. 启用所有合规扩展
CREATE EXTENSION IF NOT EXISTS pg_dsr;
CREATE EXTENSION IF NOT EXISTS pgaudit;

-- 2. 配置合规策略
ALTER SYSTEM SET pg_dsr.enable_row_labels = on;
ALTER SYSTEM SET pg_dsr.enable_cross_border_
```

**错误**: SELECT语句缺少FROM子句

---

### 05-安全与合规\数据主权\行级主权标签.md

**行 302** (sql):

```sql
-- 创建标签层次表（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'sovereignty_tag_hierarchy') THEN
            CREA
```

**错误**: 单引号不匹配

---

### 05-安全与合规\数据主权\跨境数据拦截.md

**行 213** (sql):

```sql
-- 查询拦截触发器（带错误处理）
DO $$
BEGIN
    BEGIN
        CREATE OR REPLACE FUNCTION intercept_cross_border_query()
        RETURNS TRIGGER AS $$
        DECLARE
            user_country TEXT;
            data_
```

**错误**: 单引号不匹配

---

### 05-安全与合规\数据溯源\ProvSQL集成实践.md

**行 880** (sql):

```sql
   ALTER SYSTEM SET provsql.cache_enabled = true;
   ALTER SYSTEM SET provsql.cache_size = 10000;
   SELECT pg_reload_conf();

```

**错误**: SELECT语句缺少FROM子句

---

**行 894** (sql):

```sql
   ALTER SYSTEM SET provsql.max_provenance_depth = 10;
   SELECT pg_reload_conf();

```

**错误**: SELECT语句缺少FROM子句

---

**行 905** (sql):

```sql
   ALTER SYSTEM SET provsql.compress_provenance = true;
   SELECT pg_reload_conf();

```

**错误**: SELECT语句缺少FROM子句

---

**行 968** (sql):

```sql
-- 检查溯源缓存状态
SHOW provsql.cache_enabled;
SHOW provsql.cache_size;

-- 启用缓存
ALTER SYSTEM SET provsql.cache_enabled = true;
SELECT pg_reload_conf();

```

**错误**: SELECT语句缺少FROM子句

---

**行 980** (sql):

```sql
-- 检查概率精度设置
SHOW provsql.probability_precision;

-- 调整精度
ALTER SYSTEM SET provsql.probability_precision = 0.0001;
SELECT pg_reload_conf();

```

**错误**: SELECT语句缺少FROM子句

---

**行 993** (sql):

```sql
-- 启用调试日志
ALTER SYSTEM SET log_min_messages = 'debug1';
ALTER SYSTEM SET provsql.debug = true;
SELECT pg_reload_conf();

-- 查看日志
-- tail -f /var/log/postgresql/postgresql-18-main.log

```

**错误**: SELECT语句缺少FROM子句

---

**行 1177** (sql):

```sql
-- 获取记录的完整溯源图
SELECT provsql_provenance_graph('orders', 1);

-- 获取溯源路径
SELECT provsql_provenance_path('orders', 1, 'products', 1);

```

**错误**: SELECT语句缺少FROM子句

---

**行 1212** (sql):

```sql
-- 创建扩展
CREATE EXTENSION IF NOT EXISTS provsql;

-- 创建测试表
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name TEXT,
    price NUMERIC
);

CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    p
```

**错误**: SELECT语句缺少FROM子句

---

### 05-安全与合规\数据溯源\概率数据库实现.md

**行 1615** (sql):

```sql
-- 可能世界采样函数（带错误处理）
DO $$
BEGIN
    BEGIN
        CREATE OR REPLACE FUNCTION sample_possible_worlds(
            table_name TEXT,
            sample_size INT DEFAULT 1000
        ) RETURNS TABLE (

```

**错误**: 单引号不匹配

---

**行 8111** (sql):

```sql
-- 批量插入概率数据
INSERT INTO sensor_readings (sensor_id, temperature, humidity, timestamp)
SELECT
    generate_series(1, 100) AS sensor_id,
    ROW(
        20 + random() * 10,  -- 温度范围20-30度
        0.8 +
```

**错误**: SELECT语句缺少FROM子句

---

**行 8255** (sql):

```sql
-- 更新概率值（带验证）
CREATE OR REPLACE FUNCTION update_probability_value(
    table_name TEXT,
    record_id INTEGER,
    column_name TEXT,
    new_value NUMERIC,
    new_probability NUMERIC
) RETURNS BOOLEA
```

**错误**: SELECT语句缺少FROM子句

---

### 05-安全与合规\权限管理.md

**行 1730** (sql):

```sql
   -- ✅ 好：只授予必要的权限
   CREATE ROLE app_user;
   GRANT SELECT, INSERT, UPDATE ON orders TO app_user;
   -- 不授予DELETE权限，除非必要

   -- ❌ 不好：授予过多权限
   GRANT ALL ON orders TO app_user;  -- 权限过大

```

**错误**: SELECT语句缺少FROM子句

---

**行 1742** (sql):

```sql
   -- ✅ 好：使用角色继承简化权限管理
   CREATE ROLE app_readonly;
   GRANT SELECT ON ALL TABLES IN SCHEMA public TO app_readonly;

   CREATE ROLE app_user;
   GRANT app_readonly TO app_user;  -- 继承只读权限
   GRANT INS
```

**错误**: SELECT语句缺少FROM子句

---

**行 1781** (sql):

```sql
   -- ✅ 好：为新对象设置默认权限
   ALTER DEFAULT PRIVILEGES IN SCHEMA public
   GRANT SELECT, INSERT, UPDATE ON TABLES TO app_user;

   ALTER DEFAULT PRIVILEGES IN SCHEMA public
   GRANT EXECUTE ON FUNCTIONS TO
```

**错误**: SELECT语句缺少FROM子句

---

**行 1792** (sql):

```sql
   -- ✅ 好：使用脚本管理权限，便于版本控制
   -- 创建权限管理脚本
   -- grant_permissions.sql
   GRANT SELECT ON ALL TABLES IN SCHEMA public TO app_user;
   GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO app_user;

```

**错误**: SELECT语句缺少FROM子句

---

**行 1806** (sql):

```sql
   -- ❌ 不好：授予所有权限
   GRANT ALL ON DATABASE mydb TO app_user;
   GRANT ALL ON ALL TABLES IN SCHEMA public TO app_user;

   -- ✅ 好：只授予必要权限
   GRANT CONNECT ON DATABASE mydb TO app_user;
   GRANT SELECT,
```

**错误**: SELECT语句缺少FROM子句

---

### 05-安全与合规\零信任架构完整指南.md

**行 136** (sql):

```sql
-- 创建OAuth用户
CREATE USER app_user WITH PASSWORD NULL;

-- 授予权限
GRANT CONNECT ON DATABASE mydb TO app_user;
GRANT USAGE ON SCHEMA public TO app_user;
GRANT SELECT ON TABLE users TO app_user;

```

**错误**: SELECT语句缺少FROM子句

---

**行 182** (sql):

```sql
-- 创建角色层次
CREATE ROLE app_readonly;
CREATE ROLE app_readwrite;
CREATE ROLE app_admin;

-- 角色继承
GRANT app_readonly TO app_readwrite;
GRANT app_readwrite TO app_admin;

-- 授予权限
GRANT SELECT ON ALL TABLE
```

**错误**: SELECT语句缺少FROM子句

---

**行 561** (sql):

```sql
-- 创建角色映射函数
CREATE OR REPLACE FUNCTION map_oauth_role(claims JSONB)
RETURNS TEXT AS $$
DECLARE
    v_role TEXT;
    v_groups TEXT[];
BEGIN
    -- 从claims中提取组信息
    v_groups := ARRAY(SELECT jsonb_array
```

**错误**: SELECT语句缺少FROM子句

---

**行 712** (sql):

```sql
-- 使用索引支持RLS策略
CREATE INDEX idx_users_username ON users(username);

-- 优化RLS策略（使用稳定函数）
CREATE POLICY optimized_policy ON users
    FOR SELECT
    TO app_user
    USING (username = current_user)
    WI
```

**错误**: SELECT语句缺少FROM子句

---

### 06-扩展系统\【深入】Apache AGE图数据库完整实战指南.md

**行 1550** (sql):

```sql
-- PostgreSQL配置建议
ALTER SYSTEM SET shared_buffers = '4GB';
ALTER SYSTEM SET effective_cache_size = '12GB';
ALTER SYSTEM SET maintenance_work_mem = '1GB';
ALTER SYSTEM SET work_mem = '50MB';
ALTER SYST
```

**错误**: SELECT语句缺少FROM子句

---

**行 1946** (sql):

```sql
-- ❌ 危险：字符串拼接
SELECT * FROM cypher('social_network', $$
    MATCH (p:Person {name: '$$) || user_input || $$'}) RETURN p
$$) AS (p agtype);

-- ✅ 安全：使用参数化查询
SELECT * FROM cypher('social_network', $$

```

**错误**: 括号不匹配

---

### 06-扩展系统\【深入】PostgreSQL扩展开发完整实战指南.md

**行 641** (sql):

```sql
-- 创建扩展（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'pg_hashid') THEN
            CREATE EXTENSION pg_hashid;
            RAISE NOTICE '扩展 pg_hashid
```

**错误**: 单引号不匹配

---

### 06-扩展系统\扩展开发体系详解.md

**行 190** (sql):

```sql
-- 1. 创建扩展控制文件
-- my_extension.control
comment = 'My custom extension'
default_version = '1.0'
module_pathname = '$libdir/my_extension'
relocatable = true

-- 2. 创建SQL文件
-- my_extension--1.0.sql
CREAT
```

**错误**: SELECT语句缺少FROM子句

---

### 06-扩展系统\扩展开发完整指南.md

**行 166** (sql):

```sql
-- 创建实用函数扩展（带错误处理和性能测试）
CREATE OR REPLACE FUNCTION format_bytes(bytes BIGINT)
RETURNS TEXT AS $$
BEGIN
    -- 错误处理：检查NULL输入
    IF bytes IS NULL THEN
        RAISE EXCEPTION '输入参数不能为NULL';
    END IF;
```

**错误**: SELECT语句缺少FROM子句

---

### 06-扩展系统\扩展开发指南.md

**行 269** (sql):

```sql
-- 创建 SQL 函数
CREATE FUNCTION my_function(input_text TEXT)
RETURNS TEXT
LANGUAGE SQL
IMMUTABLE
AS $$
    SELECT upper(input_text);
$$;

```

**错误**: SELECT语句缺少FROM子句

---

**行 460** (sql):

```sql
-- 1. 使用RAISE NOTICE调试（带错误处理）
CREATE OR REPLACE FUNCTION my_function(input TEXT)
RETURNS TEXT AS $$
BEGIN
    -- 错误处理：检查NULL输入
    IF input IS NULL THEN
        RAISE EXCEPTION '输入参数不能为NULL';
    END
```

**错误**: SELECT语句缺少FROM子句

---

### 07-多模型数据库\JSONB时序向量\性能优化策略.md

**行 162** (sql):

```sql
-- 按设备ID空间分区（提高并行度）
SELECT create_hypertable('device_data', 'time',
    chunk_time_interval => INTERVAL '1 day',
    partitioning_column => 'device_id',
    number_partitions => 4,
    if_not_exists =
```

**错误**: SELECT语句缺少FROM子句

---

**行 321** (sql):

```sql
-- 多列分段压缩（提高压缩率）
ALTER TABLE device_data SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'device_id, device_info->>\'location\'->>\'region\'',
    timescaledb.compress_orderby = '
```

**错误**: 单引号不匹配

---

### 07-多模型数据库\PostGIS空间数据完整实战指南.md

**行 621** (sql):

```sql
-- 创建多边形（区域）
CREATE TABLE regions (
    id SERIAL PRIMARY KEY,
    name TEXT,
    boundary GEOGRAPHY(POLYGON, 4326),
    area_sqm NUMERIC  -- 面积（平方米）
);

-- 插入区域（注意：多边形必须闭合，第一个点和最后一个点相同）
INSERT INTO r
```

**错误**: 括号不匹配; 单引号不匹配

---

**行 717** (sql):

```sql
-- WKT (Well-Known Text) 格式
SELECT ST_GeomFromText('POINT(116.3912 39.9067)', 4326);
SELECT ST_GeomFromText('LINESTRING(116.3 39.9, 116.4 39.95, 116.5 40.0)', 4326);
SELECT ST_GeomFromText('POLYGON((1
```

**错误**: SELECT语句缺少FROM子句

---

**行 1168** (sql):

```sql
-- 创建GeoJSON导出函数
CREATE OR REPLACE FUNCTION export_to_geojson(
    p_table_name TEXT,
    p_geom_column TEXT DEFAULT 'geom',
    p_where_clause TEXT DEFAULT ''
) RETURNS JSONB AS $$
DECLARE
    sql_te
```

**错误**: 单引号不匹配

---

**行 1242** (sql):

```sql
-- WGS84 (EPSG:4326) - 全球定位系统标准
SELECT ST_GeomFromText('POINT(116.3912 39.9067)', 4326);

-- Web Mercator (EPSG:3857) - Web地图标准
SELECT ST_Transform(
    ST_GeomFromText('POINT(116.3912 39.9067)', 4326
```

**错误**: SELECT语句缺少FROM子句

---

**行 1444** (sql):

```sql
-- 计算两点之间的最短线
SELECT ST_ShortestLine(
    ST_GeomFromText('POINT(116.3912 39.9067)', 4326),
    ST_GeomFromText('POINT(116.4074 39.9042)', 4326)
);

```

**错误**: SELECT语句缺少FROM子句

---

### 07-多模型数据库\PostgreSQL-18新特性\异步I-O机制-改进补充.md

**行 232** (sql):

```sql
   ALTER SYSTEM SET io_direct = 'data';
   ALTER SYSTEM SET effective_io_concurrency = 200;
   SELECT pg_reload_conf();

```

**错误**: SELECT语句缺少FROM子句

---

**行 299** (sql):

```sql
   ALTER SYSTEM SET io_direct = 'data,wal';
   ALTER SYSTEM SET enable_builtin_connection_pooling = on;
   SELECT pg_reload_conf();

```

**错误**: SELECT语句缺少FROM子句

---

### 07-多模型数据库\PostgreSQL-18新特性\异步I-O机制\01-概述\README.md

**行 169** (sql):

```sql
-- 检查PostgreSQL版本
SELECT version();
-- 需要: PostgreSQL 18.1 或更高版本

```

**错误**: SELECT语句缺少FROM子句

---

### 07-多模型数据库\PostgreSQL-18新特性\异步I-O机制\07-配置优化\README.md

**行 257** (sql):

```sql
-- 异步I/O性能监控仪表板（带错误处理）
DO $$
DECLARE
    io_direct_val TEXT;
    io_concurrency_val INTEGER;
    total_reads BIGINT;
    total_writes BIGINT;
    total_read_time NUMERIC;
    total_write_time NUMERIC;
```

**错误**: 单引号不匹配

---

### 07-多模型数据库\PostgreSQL-18新特性\异步I-O机制\09-最佳实践\README.md

**行 419** (sql):

```sql
-- 创建专用用户
CREATE USER app_user WITH PASSWORD 'secure_password';

-- 授予必要权限
GRANT CONNECT ON DATABASE mydb TO app_user;
GRANT USAGE ON SCHEMA public TO app_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON
```

**错误**: SELECT语句缺少FROM子句

---

**行 442** (sql):

```sql
-- 启用审计日志
ALTER SYSTEM SET log_statement = 'all';
ALTER SYSTEM SET log_connections = on;
ALTER SYSTEM SET log_disconnections = on;
ALTER SYSTEM SET log_duration = on;

-- 重新加载配置
SELECT pg_reload_conf(
```

**错误**: SELECT语句缺少FROM子句

---

### 07-多模型数据库\PostgreSQL-18新特性\异步I-O机制\10-监控和诊断\README.md

**行 447** (sql):

```sql
-- 设置合适的I/O并发数
ALTER SYSTEM SET effective_io_concurrency = 200;
SELECT pg_reload_conf();

-- 验证
SHOW effective_io_concurrency;  -- 200

```

**错误**: SELECT语句缺少FROM子句

---

### 07-多模型数据库\PostgreSQL-18新特性\异步I-O机制\11-迁移指南\README.md

**行 79** (sql):

```sql
-- 启用Direct I/O
ALTER SYSTEM SET io_direct = 'data,wal';

-- 配置I/O并发数
ALTER SYSTEM SET effective_io_concurrency = 200;
ALTER SYSTEM SET maintenance_io_concurrency = 200;
ALTER SYSTEM SET wal_io_concur
```

**错误**: SELECT语句缺少FROM子句

---

### 07-多模型数据库\PostgreSQL-18新特性\异步I-O机制\12-性能调优检查清单\README.md

**行 102** (sql):

```sql
-- 记录当前性能基线
CREATE TABLE performance_baseline AS
SELECT
    NOW() AS test_time,
    (SELECT setting FROM pg_settings WHERE name = 'effective_io_concurrency) AS io_concurrency,
    (SELECT count(*) FRO
```

**错误**: 单引号不匹配

---

### 07-多模型数据库\PostgreSQL-18新特性\异步I-O机制\14-常见问题FAQ\README.md

**行 119** (sql):

```sql
-- 1. WAL I/O并发配置
ALTER SYSTEM SET wal_io_concurrency = 300;

-- 2. WAL同步提交配置
-- 异步I/O可以降低同步提交的延迟
ALTER SYSTEM SET synchronous_commit = 'local';  -- 降低延迟
-- 或
ALTER SYSTEM SET synchronous_commit = 'on
```

**错误**: SELECT语句缺少FROM子句

---

### 07-多模型数据库\PostgreSQL-18新特性\异步I-O机制\15-安全与高可用\README.md

**行 394** (sql):

```sql
-- 1. 启用SSL
ALTER SYSTEM SET ssl = on;
ALTER SYSTEM SET ssl_cert_file = '/etc/postgresql/ssl/server.crt';
ALTER SYSTEM SET ssl_key_file = '/etc/postgresql/ssl/server.key';

-- 2. 配置访问控制
-- 编辑pg_hba.co
```

**错误**: SELECT语句缺少FROM子句

---

### 07-多模型数据库\PostgreSQL-18新特性\异步I-O机制\22-未来发展趋势\README.md

**行 58** (sql):

```sql
   -- PostgreSQL 19计划新增
   SELECT pg_auto_tune_io();
   -- 自动根据工作负载调整I/O参数

```

**错误**: SELECT语句缺少FROM子句

---

### 07-多模型数据库\PostgreSQL-18新特性\异步I-O机制\25-快速参考指南\README.md

**行 177** (sql):

```sql
-- 根据存储类型调整
-- SSD: 200-300
-- NVMe: 300-500
-- HDD: 2-4
ALTER SYSTEM SET effective_io_concurrency = 200;
SELECT pg_reload_conf();

```

**错误**: SELECT语句缺少FROM子句

---

**行 450** (sql):

```sql
ALTER SYSTEM SET io_direct = 'data,wal';
ALTER SYSTEM SET effective_io_concurrency = 200;
SELECT pg_reload_conf();

```

**错误**: SELECT语句缺少FROM子句

---

**行 467** (sql):

```sql
-- 根据存储类型调整
ALTER SYSTEM SET effective_io_concurrency = 300;  -- NVMe
-- 或
ALTER SYSTEM SET effective_io_concurrency = 200;  -- SSD
SELECT pg_reload_conf();

```

**错误**: SELECT语句缺少FROM子句

---

**行 492** (sql):

```sql
-- 降低I/O并发数
ALTER SYSTEM SET effective_io_concurrency = 100;
ALTER SYSTEM SET io_uring_queue_depth = 256;
SELECT pg_reload_conf();

```

**错误**: SELECT语句缺少FROM子句

---

### 07-多模型数据库\PostgreSQL-18新特性\异步I-O机制\26-社区案例\README.md

**行 54** (sql):

```sql
-- PostgreSQL 18配置（RAG优化）
ALTER SYSTEM SET io_direct = 'data,wal';
ALTER SYSTEM SET effective_io_concurrency = 300;
ALTER SYSTEM SET wal_io_concurrency = 200;
ALTER SYSTEM SET io_uring_queue_depth = 5
```

**错误**: SELECT语句缺少FROM子句

---

**行 92** (sql):

```sql
-- PostgreSQL 18配置（混合负载优化）
ALTER SYSTEM SET io_direct = 'data,wal';
ALTER SYSTEM SET effective_io_concurrency = 250;
ALTER SYSTEM SET wal_io_concurrency = 150;
ALTER SYSTEM SET max_parallel_workers_pe
```

**错误**: SELECT语句缺少FROM子句

---

**行 241** (sql):

```sql
-- 快速回滚脚本
DO $$
BEGIN
    -- 回滚到安全配置
    ALTER SYSTEM SET effective_io_concurrency = 100;
    ALTER SYSTEM SET wal_io_concurrency = 50;
    SELECT pg_reload_conf();

    RAISE NOTICE '✅ 已回滚到安全配置';
END
```

**错误**: SELECT语句缺少FROM子句

---

### 07-多模型数据库\PostgreSQL-18新特性\异步I-O机制\28-实战技巧\README.md

**行 421** (sql):

```sql
-- I/O瓶颈深度分析函数
CREATE OR REPLACE FUNCTION analyze_io_bottleneck()
RETURNS TABLE(
    bottleneck_type TEXT,
    severity TEXT,
    description TEXT,
    recommendation TEXT
) AS $$
BEGIN
    RETURN QUE
```

**错误**: 括号不匹配

---

### 07-多模型数据库\PostgreSQL-18新特性\异步I-O机制\32-错误解决方案\README.md

**行 83** (sql):

```sql
-- 方案1：升级存储设备
-- HDD → SSD/NVMe

-- 方案2：提高I/O并发度
ALTER SYSTEM SET effective_io_concurrency = 400;
SELECT pg_reload_conf();

-- 方案3：优化查询
-- 添加索引，减少全表扫描
CREATE INDEX idx_your_table_column ON your_table(
```

**错误**: SELECT语句缺少FROM子句

---

**行 152** (sql):

```sql
-- 方案1：降低I/O并发度
ALTER SYSTEM SET effective_io_concurrency = 100;
SELECT pg_reload_conf();

-- 方案2：检查存储设备性能
-- 如果存储设备性能差，降低并发度

-- 方案3：检查系统资源
-- 如果CPU或内存不足，增加资源或降低并发度

-- 方案4：回滚配置
ALTER SYSTEM SET io_d
```

**错误**: SELECT语句缺少FROM子句

---

**行 216** (sql):

```sql
-- 方案1：增加io_uring队列深度
ALTER SYSTEM SET io_uring_queue_depth = 1024;
SELECT pg_reload_conf();

-- 方案2：优化批量大小
-- 根据数据规模调整批量大小
-- 参考第9章最佳实践

-- 方案3：检查存储设备
-- 确保存储设备性能稳定

-- 方案4：优化系统资源
-- 减少资源竞争

```

**错误**: SELECT语句缺少FROM子句

---

**行 279** (sql):

```sql
-- 方案1：降低io_uring队列深度
ALTER SYSTEM SET io_uring_queue_depth = 256;
SELECT pg_reload_conf();

-- 方案2：优化内存配置
ALTER SYSTEM SET work_mem = '64MB';
ALTER SYSTEM SET maintenance_work_mem = '1GB';
SELECT pg_
```

**错误**: SELECT语句缺少FROM子句

---

**行 402** (sql):

```sql
-- 方案1：降低I/O并发度
ALTER SYSTEM SET effective_io_concurrency = 100;
SELECT pg_reload_conf();

-- 方案2：减少并行工作进程
ALTER SYSTEM SET max_parallel_workers = 4;
ALTER SYSTEM SET max_parallel_workers_per_gather =
```

**错误**: SELECT语句缺少FROM子句

---

**行 459** (sql):

```sql
-- 方案1：升级到PostgreSQL 18
-- 参考第27章版本兼容性与升级路径

-- 方案2：使用替代方案（PostgreSQL 17）
-- 使用effective_io_concurrency（PostgreSQL 17支持）
ALTER SYSTEM SET effective_io_concurrency = 200;
SELECT pg_reload_conf();

-- 方
```

**错误**: SELECT语句缺少FROM子句

---

**行 508** (sql):

```sql
-- 方案1：使用Linux系统（推荐）
-- PostgreSQL 18异步I/O主要支持Linux

-- 方案2：升级内核（Linux < 5.1）
-- 升级到Linux 5.1+内核

-- 方案3：使用替代方案
-- 在Windows上使用effective_io_concurrency
ALTER SYSTEM SET effective_io_concurrency = 200;

```

**错误**: SELECT语句缺少FROM子句

---

**行 567** (sql):

```sql
-- 创建错误日志表
CREATE TABLE IF NOT EXISTS aio_error_log (
    id SERIAL PRIMARY KEY,
    error_type VARCHAR(50),
    error_message TEXT,
    error_context JSONB,
    solution TEXT,
    resolved_at TIMESTA
```

**错误**: SELECT语句缺少FROM子句

---

### 07-多模型数据库\PostgreSQL-18新特性\异步I-O机制\34-深度集成\README.md

**行 40** (sql):

```sql
-- 主库配置（发布端）
ALTER SYSTEM SET io_direct = 'data,wal';
ALTER SYSTEM SET wal_io_concurrency = 200;
ALTER SYSTEM SET effective_io_concurrency = 300;
SELECT pg_reload_conf();

-- 创建发布
CREATE PUBLICATION o
```

**错误**: SELECT语句缺少FROM子句

---

### 07-多模型数据库\PostgreSQL-18新特性\异步I-O机制\35-成熟案例\README.md

**行 76** (sql):

```sql
-- 1. 同步模式（sync）- 传统模式
-- 行为与PostgreSQL 17完全一致
ALTER SYSTEM SET io_workers = 0;  -- 禁用异步I/O
SELECT pg_reload_conf();

-- 2. 工作进程模式（worker）- 默认模式
ALTER SYSTEM SET io_workers = 8;  -- 使用8个I/O工作进程
SELECT
```

**错误**: SELECT语句缺少FROM子句

---

**行 109** (sql):

```sql
-- NVMe SSD配置
ALTER SYSTEM SET io_workers = 8;
ALTER SYSTEM SET effective_io_concurrency = 500;  -- NVMe推荐值
SELECT pg_reload_conf();

-- SATA SSD配置
ALTER SYSTEM SET io_workers = 4;
ALTER SYSTEM SET ef
```

**错误**: SELECT语句缺少FROM子句

---

### 07-多模型数据库\PostgreSQL-18新特性\异步I-O机制\37-实战演练\README.md

**行 156** (sql):

```sql
-- 连接到PostgreSQL
psql -U postgres

-- 创建测试数据库
CREATE DATABASE aio_test;
\c aio_test

-- 创建测试表
CREATE TABLE test_table (
    id SERIAL PRIMARY KEY,
    data TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW
```

**错误**: SELECT语句缺少FROM子句

---

**行 529** (sql):

```sql
-- 降低I/O并发度
ALTER SYSTEM SET effective_io_concurrency = 100;
SELECT pg_reload_conf();

-- 或根据存储类型调整
-- SSD: 200-400
-- HDD: 50-100

```

**错误**: SELECT语句缺少FROM子句

---

**行 563** (sql):

```sql
-- 降低io_uring队列深度
ALTER SYSTEM SET io_uring_queue_depth = 256;
SELECT pg_reload_conf();

-- 降低I/O并发度
ALTER SYSTEM SET effective_io_concurrency = 100;
SELECT pg_reload_conf();

```

**错误**: SELECT语句缺少FROM子句

---

### 07-多模型数据库\PostgreSQL-18新特性\归档文档\异步I-O机制-第十二轮推进总结-2025-01.md

**行 185** (sql):

```sql
-- SSD环境快速配置
ALTER SYSTEM SET io_direct = 'data,wal';
ALTER SYSTEM SET effective_io_concurrency = 200;
ALTER SYSTEM SET wal_io_concurrency = 150;
ALTER SYSTEM SET io_uring_queue_depth = 512;
SELECT pg
```

**错误**: SELECT语句缺少FROM子句

---

### 07-多模型数据库\图向量混合检索\金融反欺诈应用.md

**行 681** (sql):

```sql
-- 表设计
CREATE TABLE transaction_embeddings (
    transaction_id BIGSERIAL PRIMARY KEY,
    account_id BIGINT NOT NULL,
    amount DECIMAL(15,2),
    timestamp TIMESTAMPTZ NOT NULL,
    embedding vecto
```

**错误**: SELECT语句缺少FROM子句

---

### 07-多模型数据库\技术原理\数据一致性保证.md

**行 692** (sql):

```sql
-- PostgreSQL 自动检测死锁
-- 如果检测到死锁，会自动回滚其中一个事务

-- 避免死锁的最佳实践:
-- 1. 按相同顺序锁定资源
-- 2. 保持事务简短
-- 3. 使用较低的隔离级别（如果可能）
-- 4. 使用 SELECT FOR UPDATE NOWAIT 避免等待

```

**错误**: SELECT语句缺少FROM子句

---

### 07-多模型数据库\技术原理\统一查询接口.md

**行 846** (sql):

```sql
-- 使用查询分解和优化
CREATE OR REPLACE FUNCTION optimize_multi_modal_query(
    p_query_text TEXT
)
RETURNS TABLE (
    optimized_query TEXT,
    execution_plan JSONB,
    estimated_time_ms INTEGER
) AS $$
DE
```

**错误**: SELECT语句缺少FROM子句

---

### 07-多模型数据库\空间数据\PostGIS完整深化指南.md

**行 150** (sql):

```sql
-- 点（Point）
SELECT ST_GeomFromText('POINT(116.3912 39.9067)', 4326);

-- 线（LineString）
SELECT ST_GeomFromText('LINESTRING(116.3 39.9, 116.4 39.95, 116.5 40.0)', 4326);

-- 多边形（Polygon）
SELECT ST_GeomF
```

**错误**: SELECT语句缺少FROM子句

---

### 07-多模型数据库\空间数据\PostgreSQL18-PostGIS地理空间数据库实战.md

**行 878** (sql):

```sql
-- geometry: 平面坐标，快
SELECT ST_Distance(
    ST_MakePoint(116.4, 39.9),
    ST_MakePoint(116.5, 40.0)
);  -- 返回度数

-- geography: 球面坐标，准确
SELECT ST_Distance(
    ST_MakePoint(116.4, 39.9)::geography,

```

**错误**: SELECT语句缺少FROM子句

---

### 08-流处理与时序\10.03-数据库时序数据模型-时间序列分析与预测的形式化.md

**行 533** (sql):

```sql
-- 创建优化的时序表结构
CREATE TABLE sensor_data_optimized (
    time TIMESTAMPTZ NOT NULL,
    sensor_id INTEGER NOT NULL,
    value DOUBLE PRECISION NOT NULL,
    quality INTEGER DEFAULT 100, -- 数据质量指标
    me
```

**错误**: SELECT语句缺少FROM子句

---

### 08-流处理与时序\10.04-数据库流处理模型-流查询语言与窗口操作的形式化.md

**行 375** (sql):

```sql
-- 创建通知函数
CREATE OR REPLACE FUNCTION notify_stream_event()
RETURNS TRIGGER AS $$
BEGIN
    PERFORM pg_notify('sensor_stream',
        json_build_object(
            'time', NEW.time,
            'sens
```

**错误**: SELECT语句缺少FROM子句

---

### 08-流处理与时序\边缘计算与IoT数据管理完整指南.md

**行 797** (sql):

```sql
-- 基础传感器数据表
CREATE TABLE sensor_readings (
    id BIGSERIAL,
    time TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    device_id TEXT NOT NULL,
    sensor_id TEXT NOT NULL,
    value NUMERIC(12,4),
    unit TE
```

**错误**: SELECT语句缺少FROM子句

---

### 10-AI与机器学习\01-核心基础\PostgreSQL-AI全栈架构.md

**行 152** (sql):

```sql
-- 创建自动向量化表
SELECT ai.create_vectorizer(
    'news_articles'::regclass,
    destination => 'news_embeddings',
    embedding => ai.embedding_openai('text-embedding-3-small', 'content'),
    chunking =>
```

**错误**: SELECT语句缺少FROM子句

---

### 10-AI与机器学习\01-核心基础\PostgreSQL生态体系架构.md

**行 273** (sql):

```sql
-- 1. 安装扩展
CREATE EXTENSION IF NOT EXISTS pg_ai;

-- 2. SQL内调用AI模型
SELECT ai.embedding('text-embedding-3-small', 'Hello world') AS embedding;

-- 3. 自动向量化管道
SELECT ai.create_vectorizer(
    'news_arti
```

**错误**: SELECT语句缺少FROM子句

---

**行 630** (sql):

```sql
-- 1. 配置逻辑复制
ALTER SYSTEM SET wal_level = logical;
ALTER SYSTEM SET max_replication_slots = 10;
SELECT pg_reload_conf();

-- 2. 创建复制槽
SELECT pg_create_logical_replication_slot('debezium_slot', 'pgoutp
```

**错误**: SELECT语句缺少FROM子句

---

**行 925** (sql):

```sql
-- 1. 安装pg_ai
CREATE EXTENSION IF NOT EXISTS pg_ai;

-- 2. 设置自动向量化
SELECT ai.create_vectorizer(...);

```

**错误**: SELECT语句缺少FROM子句

---

### 10-AI与机器学习\01-核心基础\AI原生调用-pgai.md

**行 199** (sql):

```sql
-- 方式1：使用GUC参数（推荐）
ALTER SYSTEM SET pg_ai.openai_api_key = 'sk-...';
SELECT pg_reload_conf();

-- 方式2：使用环境变量
-- 在postgresql.conf中设置：
-- pg_ai.openai_api_key = 'sk-...'

-- 方式3：使用函数设置（会话级别）
SELECT ai.s
```

**错误**: SELECT语句缺少FROM子句

---

**行 214** (sql):

```sql
-- 设置Anthropic API密钥
ALTER SYSTEM SET pg_ai.anthropic_api_key = 'sk-ant-...';
SELECT pg_reload_conf();

```

**错误**: SELECT语句缺少FROM子句

---

**行 257** (sql):

```sql
-- 插入文档并自动生成embedding
INSERT INTO documents (content, embedding)
SELECT
    'New document content',
    ai.embedding_openai('text-embedding-3-small', 'New document content');

```

**错误**: SELECT语句缺少FROM子句

---

**行 339** (sql):

```sql
-- 1. 创建源表
CREATE TABLE news_articles (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. 创建目标向量表
CREATE TABLE news_embe
```

**错误**: SELECT语句缺少FROM子句

---

**行 402** (sql):

```sql
-- 使用不同的分块策略
SELECT ai.create_vectorizer(
    'documents'::regclass,
    destination => 'document_chunks',
    embedding => ai.embedding_openai('text-embedding-3-small', 'content'),
    chunking => ai
```

**错误**: SELECT语句缺少FROM子句

---

**行 624** (sql):

```sql
-- pg_ai自动缓存相同输入的embedding结果
-- 配置缓存大小
ALTER SYSTEM SET pg_ai.cache_size = '100MB';
SELECT pg_reload_conf();

```

**错误**: SELECT语句缺少FROM子句

---

**行 633** (sql):

```sql
-- 使用后台任务处理大量AI调用
CREATE EXTENSION IF NOT EXISTS pg_cron;

-- 定时批量向量化
SELECT cron.schedule(
    'batch-vectorize',
    '*/5 * * * *',  -- 每5分钟
    $$
    UPDATE documents
    SET embedding = ai.embedd
```

**错误**: SELECT语句缺少FROM子句

---

**行 652** (sql):

```sql
-- 限制并发API调用
ALTER SYSTEM SET pg_ai.max_concurrent_requests = 10;
SELECT pg_reload_conf();

```

**错误**: SELECT语句缺少FROM子句

---

### 10-AI与机器学习\01-核心基础\内置机器学习-PostgresML.md

**行 157** (sql):

```sql
-- 启用GPU加速（如果可用）
ALTER SYSTEM SET pgml.gpu_enabled = true;

-- 设置模型缓存大小
ALTER SYSTEM SET pgml.model_cache_size = '1GB';

-- 设置训练并发数
ALTER SYSTEM SET pgml.training_jobs = 4;

SELECT pg_reload_conf();

```

**错误**: SELECT语句缺少FROM子句

---

**行 263** (sql):

```sql
-- 1. predict_proba：返回概率分布
SELECT pgml.predict_proba(
    'fraud_detection',
    ARRAY[amount, user_age, transaction_count]
) AS probabilities;

-- 2. predict_batch：批量预测
SELECT pgml.predict_batch(

```

**错误**: SELECT语句缺少FROM子句

---

**行 356** (sql):

```sql
-- PostgresML自动缓存常用模型
-- 配置缓存大小
ALTER SYSTEM SET pgml.model_cache_size = '2GB';

-- 预热缓存（加载模型到内存）
SELECT pgml.load_model('fraud_detection');

```

**错误**: SELECT语句缺少FROM子句

---

### 10-AI与机器学习\01-核心基础\数据注入与治理.md

**行 120** (sql):

```sql
-- 1. 配置逻辑复制
ALTER SYSTEM SET wal_level = logical;
ALTER SYSTEM SET max_replication_slots = 10;
SELECT pg_reload_conf();

-- 2. 创建复制槽
SELECT pg_create_logical_replication_slot('debezium_slot', 'pgoutp
```

**错误**: SELECT语句缺少FROM子句

---

**行 286** (sql):

```sql
-- 1. 文本标准化
CREATE OR REPLACE FUNCTION normalize_text(text_content TEXT)
RETURNS TEXT AS $$
BEGIN
    -- 移除HTML标签
    text_content = regexp_replace(text_content, '<[^>]+>', '', 'g');
    -- 标准化空格

```

**错误**: 单引号不匹配

---

**行 414** (sql):

```sql
-- 1. 创建自动向量化器
SELECT ai.create_vectorizer(
    'documents'::regclass,
    destination => 'document_chunks',
    embedding => ai.embedding_openai('text-embedding-3-small', 'content'),
    chunking =>
```

**错误**: SELECT语句缺少FROM子句

---

**行 464** (sql):

```sql
-- 1. 增量更新向量
CREATE OR REPLACE FUNCTION incremental_vectorize()
RETURNS void AS $$
BEGIN
    UPDATE documents
    SET embedding = ai.embedding_openai('text-embedding-3-small', content)
    WHERE embed
```

**错误**: SELECT语句缺少FROM子句

---

### 10-AI与机器学习\19-实战案例\AI-Agent数据支撑.md

**行 280** (sql):

```sql
-- 1. 添加短期记忆
CREATE OR REPLACE FUNCTION add_short_term_memory(
    p_agent_id TEXT,
    p_session_id TEXT,
    p_memory_type TEXT,
    p_content TEXT
)
RETURNS INT AS $$
DECLARE
    v_memory_id INT;

```

**错误**: SELECT语句缺少FROM子句

---

### 10-AI与机器学习\19-实战案例\智能推荐系统.md

**行 211** (sql):

```sql
-- 使用pg_ai自动生成商品特征向量
SELECT ai.create_vectorizer(
    'items'::regclass,
    destination => 'item_feature_vectors',
    embedding => ai.embedding_openai('text-embedding-3-small', 'title || description
```

**错误**: SELECT语句缺少FROM子句

---

### 10-AI与机器学习\19-实战案例\Qunar途家案例.md

**行 372** (sql):

```sql
-- 设置查询时ef_search参数
SET hnsw.ef_search = 100;  -- 提升召回率

-- 使用LIMIT提前终止
SELECT ... LIMIT 20;  -- 只返回Top 20

```

**错误**: SELECT语句缺少FROM子句

---

**行 382** (sql):

```sql
-- PostgreSQL内置缓存
ALTER SYSTEM SET shared_buffers = '8GB';
SELECT pg_reload_conf();

-- 应用层缓存热门查询
-- 使用Redis缓存查询结果

```

**错误**: SELECT语句缺少FROM子句

---

**行 610** (sql):

```sql
-- 清理和标准化文本
CREATE OR REPLACE FUNCTION preprocess_text(text_content TEXT)
RETURNS TEXT AS $$
BEGIN
    -- 移除HTML标签
    text_content = regexp_replace(text_content, '<[^>]+>', '', 'g');
    -- 标准化空格

```

**错误**: 单引号不匹配

---

### 10-AI与机器学习\19-实战案例\Timescale-MarketReader案例.md

**行 165** (sql):

```sql
-- 1. 金融新闻表（TimescaleDB时序表）
CREATE TABLE financial_news (
    time TIMESTAMPTZ NOT NULL,
    id SERIAL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    source TEXT,
    category TEXT,
    sent
```

**错误**: SELECT语句缺少FROM子句

---

**行 200** (sql):

```sql
-- 使用pg_ai Vectorizer自动生成Embedding
SELECT ai.create_vectorizer(
    'financial_news'::regclass,
    destination => 'financial_news_embeddings',
    embedding => ai.embedding_openai('text-embedding-3-s
```

**错误**: SELECT语句缺少FROM子句

---

**行 227** (sql):

```sql
-- 安装TimescaleDB扩展
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- 创建超表
SELECT create_hypertable('financial_news', 'time');

-- 安装pgvector扩展
CREATE EXTENSION IF NOT EXISTS vector;

```

**错误**: SELECT语句缺少FROM子句

---

**行 264** (sql):

```sql
-- 创建自动向量化器
SELECT ai.create_vectorizer(
    'financial_news'::regclass,
    destination => 'financial_news',
    embedding => ai.embedding_openai('text-embedding-3-small', 'title || '' '' || content'
```

**错误**: SELECT语句缺少FROM子句

---

**行 276** (sql):

```sql
-- 增量处理新数据
CREATE OR REPLACE FUNCTION process_new_news()
RETURNS void AS $$
BEGIN
    -- 处理未向量化的新闻
    UPDATE financial_news
    SET embedding = ai.embedding_openai(
        'text-embedding-3-small',

```

**错误**: SELECT语句缺少FROM子句

---

**行 417** (sql):

```sql
-- 1. 创建Vectorizer
SELECT ai.create_vectorizer(
    'financial_news'::regclass,
    destination => 'financial_news',
    embedding => ai.embedding_openai('text-embedding-3-small', 'title || '' '' || c
```

**错误**: SELECT语句缺少FROM子句

---

### 10-AI与机器学习\21-最佳实践\成本优化指南.md

**行 272** (sql):

```sql
   -- 批量生成Embedding（pg_ai Vectorizer）
   SELECT ai.create_vectorizer(
       'documents'::regclass,
       destination => 'document_embeddings',
       embedding => ai.embedding_openai('text-embedding
```

**错误**: SELECT语句缺少FROM子句

---

**行 410** (sql):

```sql
-- 自动向量化，无需编写代码
SELECT ai.create_vectorizer(
    'documents'::regclass,
    destination => 'document_embeddings',
    embedding => ai.embedding_openai('text-embedding-3-small', 'content'),
    chunkin
```

**错误**: SELECT语句缺少FROM子句

---

**行 636** (sql):

```sql
-- 使用pg_ai Vectorizer批量处理
SELECT ai.create_vectorizer(
    'documents'::regclass,
    destination => 'document_embeddings',
    embedding => ai.embedding_openai('text-embedding-3-small', 'content'),

```

**错误**: SELECT语句缺少FROM子句

---

### 10-AI与机器学习\21-最佳实践\渐进式演进路线.md

**行 404** (sql):

```sql
-- 1. 安装pg_ai
CREATE EXTENSION IF NOT EXISTS pg_ai;

-- 2. 配置API密钥
ALTER SYSTEM SET pg_ai.openai_api_key = 'your-api-key';
SELECT pg_reload_conf();

-- 3. 安装PostgresML（可选）
CREATE EXTENSION IF NOT EXIS
```

**错误**: SELECT语句缺少FROM子句

---

**行 418** (sql):

```sql
-- 1. 创建自动向量化器
SELECT ai.create_vectorizer(
    'documents'::regclass,
    destination => 'document_embeddings',
    embedding => ai.embedding_openai('text-embedding-3-small', 'content'),
    chunking
```

**错误**: SELECT语句缺少FROM子句

---

**行 494** (sql):

```sql
-- 1. 记忆存储函数
CREATE OR REPLACE FUNCTION store_agent_memory(
    p_agent_id TEXT,
    p_content TEXT,
    p_memory_type TEXT DEFAULT 'episodic'
)
RETURNS INT AS $$
DECLARE
    v_embedding vector(1536);
```

**错误**: SELECT语句缺少FROM子句

---

### 10-AI与机器学习\21-最佳实践\部署方案设计.md

**行 584** (sql):

```sql
-- 主库配置
-- postgresql.conf
wal_level = replica
max_wal_senders = 3
max_replication_slots = 3
hot_standby = on

-- 创建复制用户
CREATE ROLE replicator WITH REPLICATION LOGIN PASSWORD 'password';

-- pg_hba.c
```

**错误**: SELECT语句缺少FROM子句

---

**行 927** (sql):

```sql
-- 1. 创建应用用户
CREATE USER app_user WITH PASSWORD 'strong_password';

-- 2. 授予最小权限
GRANT CONNECT ON DATABASE ai_db TO app_user;
GRANT USAGE ON SCHEMA public TO app_user;
GRANT SELECT, INSERT, UPDATE, DE
```

**错误**: SELECT语句缺少FROM子句

---

### 10-AI与机器学习\ROADMAP-2025.md\AI原生数据库演进.md

**行 90** (sql):

```sql
-- 当前：扩展方式
CREATE EXTENSION vector;
CREATE EXTENSION pg_ai;
CREATE EXTENSION pgml;

-- 使用扩展功能
CREATE TABLE documents (embedding vector(1536));
SELECT ai.embedding_openai('text-embedding-3-small', 'tex
```

**错误**: SELECT语句缺少FROM子句

---

**行 240** (sql):

```sql
-- 扩展函数
SELECT ai.embedding_openai('model', 'text');
SELECT ai.chat_complete('model', 'prompt');

```

**错误**: SELECT语句缺少FROM子句

---

**行 248** (sql):

```sql
-- 内置函数
SELECT embedding('model', 'text');
SELECT chat_complete('model', 'prompt');

```

**错误**: SELECT语句缺少FROM子句

---

**行 256** (sql):

```sql
-- 智能函数
SELECT semantic_search('query');  -- 自动选择模型
SELECT auto_complete('prompt');   -- 自动优化

```

**错误**: SELECT语句缺少FROM子句

---

**行 280** (sql):

```sql
-- 内置ML函数
SELECT train('model', 'xgboost', 'data', 'target');
SELECT predict('model', features);

```

**错误**: SELECT语句缺少FROM子句

---

**行 288** (sql):

```sql
-- 自动ML
SELECT auto_train('data', 'target');  -- 自动选择算法
SELECT auto_predict('model', features);

```

**错误**: SELECT语句缺少FROM子句

---

**行 334** (sql):

```sql
-- 自动索引推荐
SELECT recommend_indexes('documents');
-- 返回推荐的索引配置

-- 自动创建索引
CREATE INDEX AUTO ON documents (embedding);
-- 自动选择最优索引类型和参数

```

**错误**: SELECT语句缺少FROM子句

---

**行 378** (sql):

```sql
-- pg_ai Vectorizer
SELECT ai.create_vectorizer(...);

```

**错误**: SELECT语句缺少FROM子句

---

**行 405** (sql):

```sql
-- 自动RAG系统
SELECT create_rag_system(
    'documents',
    chunking => 'recursive',
    embedding => 'text-embedding-3-small',
    llm => 'gpt-4'
);
-- 自动创建所有表和函数

```

**错误**: SELECT语句缺少FROM子句

---

**行 428** (sql):

```sql
-- 自动模型部署
SELECT deploy_model(
    'sentiment',
    algorithm => 'xgboost',
    data => 'reviews'
);
-- 自动训练和部署

```

**错误**: SELECT语句缺少FROM子句

---

### 10-AI与机器学习\ROADMAP-2025.md\云原生集成趋势.md

**行 289** (sql):

```sql
-- 流复制配置
ALTER SYSTEM SET wal_level = replica;
ALTER SYSTEM SET max_wal_senders = 10;

-- 创建复制槽
SELECT pg_create_physical_replication_slot('standby1');

```

**错误**: SELECT语句缺少FROM子句

---

### 10-AI与机器学习\ROADMAP-2025.md\战略实施建议.md

**行 124** (sql):

```sql
-- 安装pg_ai
CREATE EXTENSION pg_ai;

-- 配置API密钥
ALTER SYSTEM SET pg_ai.openai_api_key = 'key';
SELECT pg_reload_conf();

-- AI函数调用
SELECT ai.embedding_openai('text-embedding-3-small', 'text');

```

**错误**: SELECT语句缺少FROM子句

---

### 10-AI与机器学习\ROADMAP-2025.md\扩展生态完善方向.md

**行 336** (sql):

```sql
-- 未来：Hugging Face集成（预测）
CREATE EXTENSION huggingface;

-- 使用Hugging Face模型
SELECT huggingface.embed(
    model => 'sentence-transformers/all-MiniLM-L6-v2',
    text => 'query'
) AS embedding;

-- 使用H
```

**错误**: SELECT语句缺少FROM子句

---

### 10-AI与机器学习\ROADMAP-2025.md\技术发展趋势.md

**行 191** (sql):

```sql
-- 未来：自动RAG构建（预测）
SELECT ai.create_rag_system(
    'documents'::regclass,
    chunking_strategy => 'recursive',
    embedding_model => 'text-embedding-3-small',
    llm_model => 'gpt-4'
);
-- 自动创建RAG系
```

**错误**: SELECT语句缺少FROM子句

---

**行 387** (sql):

```sql
-- 未来：边缘推理（预测）
-- 轻量级PostgreSQL + 量化模型
CREATE MODEL edge_model AS
SELECT pgml.train(
    algorithm => 'lightgbm',
    quantization => 'int8'  -- 量化到8位
);

```

**错误**: SELECT语句缺少FROM子句

---

### 10-AI与机器学习\10.01-向量处理\性能优化\HNSW性能优化.md

**行 392** (sql):

```sql
    -- 优化前：默认配置
    -- shared_buffers = 128MB
    -- effective_cache_size = 4GB

    -- 优化后：针对 64GB 内存服务器
    ALTER SYSTEM SET shared_buffers = '16GB';  -- 25% of RAM
    ALTER SYSTEM SET effective_ca
```

**错误**: SELECT语句缺少FROM子句

---

### 10-AI与机器学习\10.01-向量处理\性能优化\大规模部署优化.md

**行 117** (sql):

```sql
-- 使用 Citus 扩展实现哈希分片
CREATE EXTENSION IF NOT EXISTS citus;

-- 创建分布式表
CREATE TABLE documents (
    id BIGSERIAL,
    user_id BIGINT,
    content TEXT,
    embedding vector(1536)
);

-- 按 user_id 进行哈希分
```

**错误**: SELECT语句缺少FROM子句

---

### 10-AI与机器学习\10.01-向量处理\架构设计\向量数据库架构设计.md

**行 375** (sql):

```sql
-- 向量存储示例
CREATE TABLE documents (
    id BIGSERIAL PRIMARY KEY,
    content TEXT,
    embedding vector(1536),  -- 存储在 TOAST 表
    metadata JSONB
);

-- 查看存储大小
SELECT
    pg_size_pretty(pg_total_relat
```

**错误**: SELECT语句缺少FROM子句

---

**行 409** (sql):

```sql
-- HNSW 索引创建
CREATE INDEX ON documents
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- 索引大小
SELECT
    pg_size_pretty(pg_relation_size('documents_embedding_idx')) as
```

**错误**: SELECT语句缺少FROM子句

---

### 10-AI与机器学习\10.04-AI自治\强化学习优化器\优化器架构设计.md

**行 125** (python):

```python
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class QueryEnvironment:
    """查询环境感知（带错误处理）"""

    def __init__(self):
        """初始化环境"""
        try:

```

**错误**: 语法错误: invalid character '：' (U+FF1A) (行 77)

---

**行 334** (python):

```python
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class RewardFunction:
    """奖励函数（带错误处理）"""

    def __init__(self):
        """初始化奖励函数"""
        try:
            s
```

**错误**: 语法错误: expected 'except' or 'finally' block (行 37)

---

**行 520** (sql):

```sql
-- 启用 RL 优化器
ALTER SYSTEM SET pg_ai.enable_rl_optimizer = ON;

-- 学习率
ALTER SYSTEM SET pg_ai.learning_rate = 0.001;

-- 探索率
ALTER SYSTEM SET pg_ai.epsilon = 0.1;

-- 训练频率
ALTER SYSTEM SET pg_ai.update
```

**错误**: SELECT语句缺少FROM子句

---

### 10-AI与机器学习\10.04-AI自治\性能调优\缓存预热策略.md

**行 388** (sql):

```sql
-- 使用 pg_cron 调度预热任务
SELECT cron.schedule(
    'preheat-cache',
    '0 2 * * *',  -- 每天凌晨 2 点
    $$SELECT preheat_cache()$$
);

```

**错误**: SELECT语句缺少FROM子句

---

### 10-AI与机器学习\10.04-AI自治\技术原理\AI自治核心原理.md

**行 722** (sql):

```sql
-- 启用 pg_ai 插件
CREATE EXTENSION IF NOT EXISTS pg_ai;

-- 配置强化学习优化器
ALTER SYSTEM SET pg_ai.enable_rl_optimizer = ON;
ALTER SYSTEM SET pg_ai.rl_learning_rate = 0.001;
ALTER SYSTEM SET pg_ai.rl_epsilon =
```

**错误**: SELECT语句缺少FROM子句

---

**行 736** (sql):

```sql
-- 配置训练参数
ALTER SYSTEM SET pg_ai.training_batch_size = 32;
ALTER SYSTEM SET pg_ai.training_frequency = 100;  -- 每 100 个查询训练一次
ALTER SYSTEM SET pg_ai.target_update_frequency = 1000;  -- 每 1000 步更新目标网络

```

**错误**: SELECT语句缺少FROM子句

---

**行 849** (sql):

```sql
-- 预热期配置
ALTER SYSTEM SET pg_ai.enable_rl_optimizer = ON;
ALTER SYSTEM SET pg_ai.training_mode = 'monitor';  -- 仅监控，不优化
ALTER SYSTEM SET pg_ai.manual_intervention_threshold = 0.2;  -- 性能下降 > 20% 时告警
S
```

**错误**: SELECT语句缺少FROM子句

---

**行 865** (sql):

```sql
-- 生产环境配置
ALTER SYSTEM SET pg_ai.enable_rl_optimizer = ON;
ALTER SYSTEM SET pg_ai.training_mode = 'active';  -- 主动优化
ALTER SYSTEM SET pg_ai.performance_threshold = 0.1;  -- 性能提升阈值 10%
ALTER SYSTEM SET
```

**错误**: SELECT语句缺少FROM子句

---

### 10-AI与机器学习\10.04-AI自治\技术原理\强化学习在数据库优化中的应用.md

**行 705** (sql):

```sql
-- 安装 pg_ai 扩展
CREATE EXTENSION IF NOT EXISTS pg_ai;

-- 启用强化学习优化器
ALTER SYSTEM SET pg_ai.enable_rl_optimizer = on;
ALTER SYSTEM SET pg_ai.rl_algorithm = 'PPO';
ALTER SYSTEM SET pg_ai.rl_learning_rate
```

**错误**: SELECT语句缺少FROM子句

---

### 10-AI与机器学习\10.04-AI自治\智能运维\预测性维护系统.md

**行 710** (sql):

```sql
-- 创建时序表
CREATE TABLE sensor_data (
    time TIMESTAMPTZ NOT NULL,
    sensor_id INT NOT NULL,
    temperature NUMERIC,
    humidity NUMERIC,
    pressure NUMERIC
);

-- 转换为时序表
SELECT create_hypertabl
```

**错误**: SELECT语句缺少FROM子句

---

### 10-AI与机器学习\10.04-AI自治\查询优化\机器学习优化器实现.md

**行 572** (sql):

```sql
   -- 创建扩展
   CREATE EXTENSION pg_ai;

   -- 加载模型
   SELECT pg_ai_load_model('cost_model', '/path/to/model.json');

   -- 启用优化器
   SET pg_ai.enabled = true;

```

**错误**: SELECT语句缺少FROM子句

---

**行 754** (sql):

```sql
-- 启用机器学习优化器
ALTER SYSTEM SET pg_ai.enabled = on;
ALTER SYSTEM SET pg_ai.model_path = '/var/lib/postgresql/pg_ai/models';
SELECT pg_reload_conf();

-- 查看配置
SHOW pg_ai.enabled;
SHOW pg_ai.model_path;

```

**错误**: SELECT语句缺少FROM子句

---

### 10-AI与机器学习\10.04-AI自治\查询优化\自适应查询计划选择.md

**行 732** (sql):

```sql
-- 禁用自适应优化器
SET pg_ai.adaptive_enabled = false;

-- 重置学习状态
SELECT pg_ai_reset_learning();

-- 清理计划缓存
SELECT pg_ai_clear_cache();

```

**错误**: SELECT语句缺少FROM子句

---

### 10-AI与机器学习\10.04-AI自治\配置示例\pg_ai安装配置.md

**行 244** (sql):

```sql
-- 启用查询日志
SET pg_ai.query_logging = on;

-- 运行典型工作负载
-- ... 执行查询 ...

-- 导出训练数据
SELECT pg_ai.export_training_data('/var/lib/postgresql/pg_ai/training/data.csv');

```

**错误**: SELECT语句缺少FROM子句

---

### 10-AI与机器学习\pgvector-0.8.1-新特性完整指南.md

**行 393** (sql):

```sql
-- PostgreSQL 18的异步I/O可以加速向量索引构建
ALTER SYSTEM SET effective_io_concurrency = 200;
ALTER SYSTEM SET maintenance_io_concurrency = 200;

-- 重启后生效
SELECT pg_reload_conf();

```

**错误**: SELECT语句缺少FROM子句

---

**行 472** (sql):

```sql
-- PostgreSQL配置优化
ALTER SYSTEM SET shared_buffers = '8GB';
ALTER SYSTEM SET effective_cache_size = '24GB';
ALTER SYSTEM SET work_mem = '256MB';
ALTER SYSTEM SET maintenance_work_mem = '2GB';

-- pgvec
```

**错误**: SELECT语句缺少FROM子句

---

### 10-AI与机器学习\【深入】pgvector向量数据库与AI集成完整指南.md

**行 1177** (sql):

```sql
-- ✅ 1. 选择合适的向量维度
-- OpenAI ada-002: 1536维（高质量）
-- Sentence-BERT small: 384维（快速）
-- 权衡：维度越高越准确，但越慢

-- ✅ 2. 归一化向量（使用余弦距离时）
CREATE OR REPLACE FUNCTION normalize_vector(v vector)
RETURNS vector AS $$

```

**错误**: SELECT语句缺少FROM子句

---

**行 1223** (sql):

```sql
-- 1. 敏感数据不要存储在向量中
-- embedding可能泄露部分原文信息

-- 2. 访问控制
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;

CREATE POLICY documents_tenant_isolation ON documents
FOR SELECT
USING (tenant_id = current_sett
```

**错误**: SELECT语句缺少FROM子句

---

### 11-部署架构\04.01-单机部署与配置.md

**行 1698** (sql):

```sql
-- PostgreSQL 18 自我监测配置（带错误处理和性能测试）
DO $$
BEGIN
    BEGIN
        -- 启用pg_stat_statements扩展
        CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

        RAISE NOTICE '=== PostgreSQL 18自我监测配置 ==
```

**错误**: 单引号不匹配

---

### 11-部署架构\04.02-集群部署与高可用.md

**行 324** (sql):

```sql
-- 查看复制状态（带错误处理和性能测试）
DO $$
BEGIN
    BEGIN
        RAISE NOTICE '开始查看复制状态';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '查询准备失败: %', SQLERRM;
            RAISE;
    END;
END $$;

```

**错误**: SELECT语句缺少FROM子句

---

**行 986** (sql):

```sql
-- 在主库上执行（PostgreSQL 12+）
SELECT pg_promote();

-- 或使用recovery.conf（PostgreSQL 11及以下）
-- 在从库上创建trigger文件
touch /var/lib/postgresql/data/promote_trigger

```

**错误**: SELECT语句缺少FROM子句

---

**行 1020** (sql):

```sql
SELECT pg_is_in_recovery();

```

**错误**: SELECT语句缺少FROM子句

---

### 11-部署架构\99-归档\1.1.150-PostgreSQL部署方式与场景对比分析.md

**行 339** (sql):

```sql
-- 安装Citus扩展
CREATE EXTENSION citus;

-- 添加工作节点
SELECT citus_add_node('192.168.1.11', 5432);
SELECT citus_add_node('192.168.1.12', 5432);
SELECT citus_add_node('192.168.1.13', 5432);

-- 创建分布式表
CREATE
```

**错误**: SELECT语句缺少FROM子句

---

### 11-部署架构\99-归档\1.1.17-安全与合规.md

**行 107** (sql):

```sql
-- 创建角色层次
CREATE ROLE admin_role;
CREATE ROLE user_role;
CREATE ROLE readonly_role;

-- 权限继承
GRANT admin_role TO user_role;
GRANT user_role TO readonly_role;

-- 具体权限分配
GRANT ALL PRIVILEGES ON DATABAS
```

**错误**: SELECT语句缺少FROM子句

---

### 11-部署架构\【深入】Citus分布式PostgreSQL完整实战指南.md

**行 770** (sql):

```sql
-- ❌ 使用自增ID作为分片键
CREATE TABLE bad_table (
    id SERIAL PRIMARY KEY,  -- 自增，数据倾斜！
    data TEXT
);
SELECT create_distributed_table('bad_table', 'id');
-- 问题：新数据集中在一个分片，负载不均

-- ❌ 使用低基数列
SELECT create_
```

**错误**: SELECT语句缺少FROM子句

---

**行 819** (sql):

```sql
-- 分裂单个分片（当某个分片过大时）
SELECT citus_split_shard_by_split_points(
    'events',
    ARRAY[102008],  -- 要分裂的shardid
    ARRAY[-1000000, 0, 1000000],  -- 分裂点
    'citus-worker3',  -- 新分片的目标节点
    5432
);

```

**错误**: SELECT语句缺少FROM子句

---

**行 1220** (sql):

```sql
-- 调整并行参数
ALTER SYSTEM SET max_parallel_workers_per_gather = 4;
ALTER SYSTEM SET max_parallel_workers = 32;
ALTER SYSTEM SET parallel_tuple_cost = 0.01;
SELECT pg_reload_conf();

-- 强制并行（测试用）
SET forc
```

**错误**: SELECT语句缺少FROM子句

---

**行 1492** (sql):

```sql
-- 核心表设计
CREATE TABLE tenants (
    tenant_id SERIAL PRIMARY KEY,
    tenant_name VARCHAR(100),
    plan VARCHAR(20),
    created_at TIMESTAMPTZ
);
SELECT create_reference_table('tenants');  -- 广播表

C
```

**错误**: SELECT语句缺少FROM子句

---

**行 1691** (sql):

```sql
    -- ✅ 好：高基数
    SELECT create_distributed_table('users', 'user_id');  -- 百万+用户

    -- ❌ 坏：低基数
    SELECT create_distributed_table('users', 'country_code');  -- 只有200+国家

```

**错误**: SELECT语句缺少FROM子句

---

**行 1701** (sql):

```sql
    -- ✅ 好：相关表使用相同分片键
    CREATE TABLE orders (order_id BIGSERIAL, user_id BIGINT, ...);
    CREATE TABLE payments (payment_id BIGSERIAL, user_id BIGINT, ...);

    SELECT create_distributed_table('or
```

**错误**: SELECT语句缺少FROM子句

---

**行 1712** (sql):

```sql
    -- ✅ 好：小表广播到所有节点
    SELECT create_reference_table('countries');
    SELECT create_reference_table('product_categories');

```

**错误**: SELECT语句缺少FROM子句

---

### 11-部署架构\分布式部署\05.08-分布式架构设计.md

**行 421** (sql):

```sql
-- 1. 分片配置
-- 设置默认分片数量（建议：CPU核心数 * 2）
ALTER SYSTEM SET citus.shard_count = 32;
ALTER SYSTEM SET citus.shard_replication_factor = 1;  -- 生产环境建议2

-- 2. 执行器配置
ALTER SYSTEM SET citus.max_adaptive_executo
```

**错误**: SELECT语句缺少FROM子句

---

**行 491** (sql):

```sql
-- 分片数量建议：
-- - 小表（<10GB）: 4-8个分片
-- - 中表（10-100GB）: 16-32个分片
-- - 大表（>100GB）: 32-64个分片
-- - 超大表（>1TB）: 64-128个分片

-- 创建表时指定分片数量
SELECT create_distributed_table('large_table', 'id',
    shard_count =>
```

**错误**: SELECT语句缺少FROM子句

---

### 11-部署架构\单机部署\05.01-单机部署与配置.md

**行 1649** (sql):

```sql
-- 1. 创建分区表（按时间分区）
CREATE TABLE sales (
    id SERIAL,
    sale_date DATE,
    amount DECIMAL(10,2)
) PARTITION BY RANGE (sale_date);

-- 2. 创建分区
CREATE TABLE sales_2024_01 PARTITION OF sales
FOR VALU
```

**错误**: 单引号不匹配

---

**行 4039** (sql):

```sql
-- 创建日志清理函数
-- 清理旧日志函数（带完整错误处理）
CREATE OR REPLACE FUNCTION cleanup_old_logs(
    p_retention_days INTEGER DEFAULT 30
)
RETURNS TABLE (
    deleted_files INTEGER,
    freed_space TEXT
)
LANGUAGE plpgsq
```

**错误**: 单引号不匹配

---

**行 4225** (sql):

```sql
-- 从日志中分析连接模式（需要log_connections = on）
-- 使用pg_read_file读取日志文件

-- 分析连接日志函数（带完整错误处理）
CREATE OR REPLACE FUNCTION analyze_connections(
    p_log_file_path TEXT
)
RETURNS TABLE (
    connection_time TIMES
```

**错误**: 单引号不匹配; SELECT语句缺少FROM子句

---

### 11-部署架构\单机部署\05.02-性能调优实践.md

**行 1958** (sql):

```sql
-- PostgreSQL 18自动去重重复的索引键
-- 对于重复值，只存储一次，提高索引效率

-- 示例：大量重复值的列
CREATE TABLE logs (
    id SERIAL PRIMARY KEY,
    level VARCHAR(10),  -- 只有几个不同值：INFO, WARNING, ERROR
    message TEXT,
    created_at
```

**错误**: SELECT语句缺少FROM子句

---

**行 2239** (sql):

```sql
-- 策略1：高频更新表（每天ANALYZE）
-- 适用于：订单表、日志表等
CREATE OR REPLACE FUNCTION analyze_frequent_tables()
RETURNS void AS $$
BEGIN
    ANALYZE orders;
    ANALYZE order_items;
    ANALYZE logs;
END;
$$ LANGUAGE pl
```

**错误**: SELECT语句缺少FROM子句

---

**行 2815** (sql):

```sql
-- PostgreSQL自动记录死锁到日志
-- 日志格式：
-- ERROR: deadlock detected
-- DETAIL: Process 12345 waits for ShareLock on transaction 123456; blocked by process 12346.
-- Process 12346 waits for ShareLock on transa
```

**错误**: SELECT语句缺少FROM子句

---

**行 3408** (sql):

```sql
-- 会话级调整
SET work_mem = '32MB';

-- 用户级调整
ALTER USER app_user SET work_mem = '64MB';

-- 数据库级调整
ALTER DATABASE mydb SET work_mem = '32MB';

-- 查看当前work_mem设置
SHOW work_mem;
SELECT current_setting('wor
```

**错误**: SELECT语句缺少FROM子句

---

### 11-部署架构\容器化部署\05.12-Docker部署.md

**行 997** (sql):

```sql
-- scripts/init-extensions.sql
-- 启用常用扩展
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
CREATE EXTENSION IF NOT EXISTS pgvector;
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EX
```

**错误**: SELECT语句缺少FROM子句

---

### 11-部署架构\容器化部署\05.15-Serverless部署.md

**行 749** (sql):

```sql
-- 1. 启用实时功能
ALTER PUBLICATION supabase_realtime ADD TABLE messages;
ALTER PUBLICATION supabase_realtime ADD TABLE notifications;

-- 2. 配置行级安全策略
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;

CREAT
```

**错误**: SELECT语句缺少FROM子句

---

**行 800** (sql):

```sql
-- 1. 创建存储桶
INSERT INTO storage.buckets (id, name, public)
VALUES ('avatars', 'avatars', true);

-- 2. 配置存储策略
CREATE POLICY "Users can upload avatars"
ON storage.objects FOR INSERT
WITH CHECK (
  buck
```

**错误**: SELECT语句缺少FROM子句

---

**行 839** (sql):

```sql
-- 1. 启用行级安全
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;

-- 2. 创建策略
CREATE POLICY "Users can view own profile"
ON users FOR SELECT
USING (auth.uid() = i
```

**错误**: SELECT语句缺少FROM子句

---

### 11-部署架构\集群部署\05.05-主从复制.md

**行 591** (sql):

```sql
-- 删除物理复制槽
SELECT pg_drop_replication_slot('replica1');

-- 删除逻辑复制槽
SELECT pg_drop_replication_slot('logical_slot');

```

**错误**: SELECT语句缺少FROM子句

---

**行 637** (sql):

```sql
-- 在从库执行
SELECT
  pg_is_in_recovery() AS is_standby,
  pg_last_wal_receive_lsn() AS receive_lsn,
  pg_last_wal_replay_lsn() AS replay_lsn,
  pg_wal_lsn_diff(pg_last_wal_receive_lsn(), pg_last_wal_repl
```

**错误**: SELECT语句缺少FROM子句

---

**行 1879** (sql):

```sql
-- 在从库执行（PostgreSQL 12+，带错误处理）
DO $$
DECLARE
    is_standby BOOLEAN;
BEGIN
    SELECT pg_is_in_recovery() INTO is_standby;

    IF NOT is_standby THEN
        RAISE EXCEPTION '当前节点不是从库，无法提升';
    END
```

**错误**: SELECT语句缺少FROM子句

---

### 11-部署架构\集群部署\05.06-读写分离.md

**行 383** (python):

```python
import time

class LatencyBasedRouter:
    def __init__(self, read_hosts):
        self.read_hosts = read_hosts
        self.latencies = {host: 0 for host in read_hosts}

    def measure_latency(self,
```

**错误**: 语法错误: positional argument follows keyword argument (行 11)

---

**行 713** (sql):

```sql
-- 测试负载均衡（带错误处理）
DO $$
BEGIN
    RAISE NOTICE '测试负载均衡：执行多次查询，观察连接分布';
    RAISE NOTICE '请使用: SELECT pg_backend_pid(), inet_server_addr(), inet_server_port();';
EXCEPTION
    WHEN OTHERS THEN
        R
```

**错误**: SELECT语句缺少FROM子句

---

### 12-监控与诊断\30-性能调优/README.md

**行 684** (sql):

```sql
-- 参数回滚
ALTER SYSTEM SET shared_buffers = '256MB';  -- 恢复到旧值
SELECT pg_reload_conf();

-- 索引回滚
DROP INDEX CONCURRENTLY IF EXISTS idx_orders_created_at;

-- 更新变更记录
UPDATE performance_change_log
SET

```

**错误**: SELECT语句缺少FROM子句

---

### 12-监控与诊断\日志管理与分析.md

**行 817** (sql):

```sql
-- 1. 配置记录慢查询（超过1秒的查询）
ALTER SYSTEM SET log_min_duration_statement = 1000;  -- 单位：毫秒
ALTER SYSTEM SET log_statement = 'mod';  -- 记录DDL和修改语句
SELECT pg_reload_conf();

-- 2. 配置日志格式
ALTER SYSTEM SET log_
```

**错误**: SELECT语句缺少FROM子句

---

### 12-监控与诊断\监控与诊断.md

**行 937** (sql):

```sql
-- 创建慢查询分析函数
CREATE OR REPLACE FUNCTION analyze_slow_queries(
    min_exec_time_ms NUMERIC DEFAULT 1000
)
RETURNS TABLE (
    query_id BIGINT,
    query_preview TEXT,
    calls BIGINT,
    total_time_
```

**错误**: 单引号不匹配

---

**行 1037** (sql):

```sql
   -- ✅ 好：启用pg_stat_statements收集详细查询统计
   CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

   -- ✅ 好：配置统计信息收集
   ALTER SYSTEM SET track_activities = on;
   ALTER SYSTEM SET track_counts = on;
   AL
```

**错误**: SELECT语句缺少FROM子句

---

**行 1388** (sql):

```sql
-- PostgreSQL 18 pg_stat_io增强监控（带错误处理和性能测试）
DO $$
BEGIN
    BEGIN
        IF (SELECT current_setting('server_version_num')::int) < 180000 THEN
            RAISE WARNING 'pg_stat_io增强功能需要PostgreSQL 18+
```

**错误**: 单引号不匹配

---

**行 1431** (sql):

```sql
-- PostgreSQL 18 后端I/O追踪（带错误处理和性能测试）
DO $$
BEGIN
    BEGIN
        IF (SELECT current_setting('server_version_num')::int) < 180000 THEN
            RAISE WARNING 'pg_stat_get_backend_io()函数需要PostgreSQ
```

**错误**: SELECT语句缺少FROM子句

---

### 13-高可用架构\【深入】PostgreSQL逻辑复制高级特性与冲突解决.md

**行 1365** (sql):

```sql
-- 数据中心A
CREATE EXTENSION pglogical;

SELECT pglogical.create_node(
    node_name := 'dc_a',
    dsn := 'host=dc-a port=5432 dbname=mydb'
);

SELECT pglogical.create_replication_set(
    set_name := '
```

**错误**: SELECT语句缺少FROM子句

---

**行 1603** (sql):

```sql
-- 订阅端配置
ALTER SUBSCRIPTION my_sub SET (streaming = on);  -- PostgreSQL 14+流式应用
ALTER SUBSCRIPTION my_sub SET (binary = true);   -- PostgreSQL 14+二进制格式
ALTER SUBSCRIPTION my_sub SET (parallel_apply_wo
```

**错误**: SELECT语句缺少FROM子句

---

### 13-高可用架构\灾难恢复\RTO_RPO目标设定.md

**行 222** (sql):

```sql
-- PostgreSQL 18异步I/O配置
ALTER SYSTEM SET io_direct = 'data,wal';
ALTER SYSTEM SET io_combine_limit = '256kB';

-- 重启后生效
SELECT pg_reload_conf();

-- RTO优化效果:
-- 恢复时间: -20-25%
-- WAL应用速度: +30-35%

```

**错误**: SELECT语句缺少FROM子句

---

### 13-高可用架构\灾难恢复\业务连续性规划.md

**行 211** (sql):

```sql
-- 配置连续归档
ALTER SYSTEM SET wal_level = 'replica';
ALTER SYSTEM SET archive_mode = 'on';
ALTER SYSTEM SET archive_command = 'cp %p /backup/archive/%f';
SELECT pg_reload_conf();

-- 配置PITR恢复
-- recovery
```

**错误**: SELECT语句缺少FROM子句

---

### 13-高可用架构\监控与诊断\06.01-监控与诊断.md

**行 1379** (sql):

```sql
-- 终止阻塞事务（谨慎使用）
SELECT pg_terminate_backend(blocking_pid);

-- 优化事务逻辑
-- 减少事务持有时间
-- 使用更细粒度的锁

```

**错误**: SELECT语句缺少FROM子句

---

### 13-高可用架构\监控与诊断\06.04-性能问题案例库.md

**行 683** (sql):

```sql
-- 1. 增加max_wal_size（允许更大的WAL）
ALTER SYSTEM SET max_wal_size = '4GB';  -- 从1GB增加到4GB

-- 2. 增加checkpoint_timeout（延长检查点间隔）
ALTER SYSTEM SET checkpoint_timeout = '15min';  -- 从5min增加到15min

-- 3. 增加wal_
```

**错误**: SELECT语句缺少FROM子句

---

### 13-高可用架构\运维工具\README.md

**行 199** (sql):

```sql
-- 启用扩展
CREATE EXTENSION IF NOT EXISTS pg_repack;

-- 重建表
SELECT repack.repack_table('public.orders');

```

**错误**: SELECT语句缺少FROM子句

---

### 13-高可用架构\逻辑复制详解.md

**行 1135** (sql):

```sql
-- 1. 增加复制工作进程
ALTER SYSTEM SET max_logical_replication_workers = 20;
SELECT pg_reload_conf();

-- 2. 优化订阅参数
ALTER SUBSCRIPTION my_subscription
SET (synchronous_commit = off);

-- 3. 批量应用更改
ALTER SYST
```

**错误**: SELECT语句缺少FROM子句

---

### 13-高可用架构\高可用与容灾方案选型指南.md

**行 1039** (sql):

```sql
-- Primary 配置（默认异步）
synchronous_standby_names = ''

-- 或者显式设置
synchronous_commit = 'off'

-- 检查复制状态
SELECT
    application_name,
    sync_state,
    pg_wal_lsn_diff(pg_current_wal_lsn(), replay_lsn) A
```

**错误**: 单引号不匹配

---

**行 1056** (sql):

```sql
-- 创建复制槽
SELECT pg_create_physical_replication_slot('standby1_slot');

-- 从库使用复制槽
primary_slot_name = 'standby1_slot'

```

**错误**: SELECT语句缺少FROM子句

---

**行 1079** (sql):

```sql
   -- 防止WAL丢失
   SELECT pg_create_physical_replication_slot('standby1_slot');

```

**错误**: SELECT语句缺少FROM子句

---

**行 1086** (sql):

```sql
   -- 实时监控延迟
   SELECT pg_wal_lsn_diff(pg_current_wal_lsn(), replay_lsn) AS lag;

```

**错误**: SELECT语句缺少FROM子句

---

**行 1283** (sql):

```sql
   SELECT pg_create_physical_replication_slot('standby1_slot');

```

**错误**: SELECT语句缺少FROM子句

---

### 13-高可用架构\高可用体系详解.md

**行 1233** (sql):

```sql
   -- ✅ 好：金融系统使用同步复制
   synchronous_standby_names = 'standby1,standby2'
   synchronous_commit = on

   -- ❌ 不好：关键业务使用异步复制（可能丢失数据）
   -- synchronous_standby_names = ''

```

**错误**: 单引号不匹配

---

### 14-云原生与容器化\05.12-Docker部署.md

**行 997** (sql):

```sql
-- scripts/init-extensions.sql
-- 启用常用扩展
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
CREATE EXTENSION IF NOT EXISTS pgvector;
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EX
```

**错误**: SELECT语句缺少FROM子句

---

### 14-云原生与容器化\05.15-Serverless部署.md

**行 749** (sql):

```sql
-- 1. 启用实时功能
ALTER PUBLICATION supabase_realtime ADD TABLE messages;
ALTER PUBLICATION supabase_realtime ADD TABLE notifications;

-- 2. 配置行级安全策略
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;

CREAT
```

**错误**: SELECT语句缺少FROM子句

---

**行 800** (sql):

```sql
-- 1. 创建存储桶
INSERT INTO storage.buckets (id, name, public)
VALUES ('avatars', 'avatars', true);

-- 2. 配置存储策略
CREATE POLICY "Users can upload avatars"
ON storage.objects FOR INSERT
WITH CHECK (
  buck
```

**错误**: SELECT语句缺少FROM子句

---

**行 839** (sql):

```sql
-- 1. 启用行级安全
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;

-- 2. 创建策略
CREATE POLICY "Users can view own profile"
ON users FOR SELECT
USING (auth.uid() = i
```

**错误**: SELECT语句缺少FROM子句

---

### 14-云原生与容器化\CloudNativePG-CNCF-完整集成指南.md

**行 371** (sql):

```sql
-- 在主节点创建复制集
SELECT spock.create_replication_set('default');

-- 添加表到复制集
SELECT spock.replicate_set_add_table('default', 'public.users');
SELECT spock.replicate_set_add_table('default', 'public.orders
```

**错误**: SELECT语句缺少FROM子句

---

### 14-云原生与容器化\Neon平台\Neon架构详解.md

**行 6407** (sql):

```sql
-- 创建函数
-- 计算总价函数（带完整错误处理）
CREATE OR REPLACE FUNCTION calculate_total(p_price DECIMAL, p_quantity INTEGER)
RETURNS DECIMAL
LANGUAGE plpgsql
AS $$
DECLARE
    v_total DECIMAL;
BEGIN
    -- 参数验证
    IF
```

**错误**: 单引号不匹配

---

### 14-云原生与容器化\Serverless\Serverless PostgreSQL完整指南.md

**行 746** (sql):

```sql
-- 资源使用监控工具（带错误处理和性能测试）
DO $$
DECLARE
    db_record RECORD;
    total_connections int := 0;
    total_transactions bigint := 0;
    total_io_operations bigint := 0;
BEGIN
    RAISE NOTICE '=== Serverl
```

**错误**: 单引号不匹配

---

**行 808** (sql):

```sql
-- 查询优化工具（带错误处理和性能测试）
DO $$
DECLARE
    query_record RECORD;
    slow_query_count int := 0;
    total_query_time numeric := 0;
BEGIN
    -- 检查pg_stat_statements扩展
    IF NOT EXISTS (SELECT 1 FROM pg_e
```

**错误**: 单引号不匹配

---

**行 935** (sql):

```sql
-- 存储优化工具（带错误处理和性能测试）
DO $$
DECLARE
    table_record RECORD;
    total_size bigint := 0;
    compressed_size_estimate bigint;
    compression_ratio numeric;
    cold_data_size bigint := 0;
BEGIN
    R
```

**错误**: 单引号不匹配

---

### 14-云原生与容器化\Supabase平台\Supabase架构设计.md

**行 326** (sql):

```sql
-- 启用 RLS
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;

-- 创建策略
CREATE POLICY "Users can view own documents"
ON documents FOR SELECT
USING (auth.uid() = user_id);

```

**错误**: SELECT语句缺少FROM子句

---

### 14-云原生与容器化\成本分析\Serverless成本优化深度分析.md

**行 436** (sql):

```sql
   -- 使用 TimescaleDB 压缩历史数据
   SELECT add_compression_policy('metrics', INTERVAL '7 days');

```

**错误**: SELECT语句缺少FROM子句

---

### 15-分布式系统\02-实时流处理完整指南.md

**行 152** (sql):

```sql
-- 1. 配置wal_level
ALTER SYSTEM SET wal_level = logical;
SELECT pg_reload_conf();

-- 2. 检查wal_level
SHOW wal_level;  -- 应该返回 'logical'

-- 3. 创建复制用户
CREATE USER replicator WITH REPLICATION PASSWORD 'p
```

**错误**: SELECT语句缺少FROM子句

---

**行 396** (sql):

```sql
-- 暂停Subscription
ALTER SUBSCRIPTION events_sub DISABLE;

-- 恢复Subscription
ALTER SUBSCRIPTION events_sub ENABLE;

-- 删除Subscription
DROP SUBSCRIPTION events_sub;

-- 删除复制槽（谨慎操作）
SELECT pg_drop_replic
```

**错误**: SELECT语句缺少FROM子句

---

### 15-分布式系统\03-CDC完整实战指南.md

**行 81** (sql):

```sql
-- 1. 启用逻辑复制
ALTER SYSTEM SET wal_level = logical;
-- 重启PostgreSQL

-- 2. 创建Publication
CREATE PUBLICATION cdc_pub FOR ALL TABLES;

-- 3. 创建复制槽
SELECT pg_create_logical_replication_slot('cdc_slot', 'p
```

**错误**: SELECT语句缺少FROM子句

---

### 15-分布式系统\04-并行查询深度优化指南.md

**行 217** (sql):

```sql
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT ...;

-- 关注：
-- 1. Workers Planned vs Workers Launched
--    如果不一致，检查资源限制
-- 2. 每个Worker的actual time
--    如果差异大，负载不均衡
-- 3. Gather节点的时间
--    如果占比高，合并开销大

```

**错误**: SELECT语句缺少FROM子句

---

### 15-分布式系统\04.01-PostgreSQL分布式架构与系统优缺点.md

**行 1333** (sql):

```sql
-- 主节点配置异步复制
synchronous_standby_names = ''

-- 读写分离配置
-- 应用层路由：
-- - 写操作：主节点
-- - 读操作：备节点（负载均衡）

```

**错误**: 单引号不匹配

---

### 15-分布式系统\04.02-分布式一致性与CAP-形式化刻画与权衡.md

**行 553** (sql):

```sql
-- 主节点配置（postgresql.conf）（带错误处理）
DO $$
BEGIN
    BEGIN
        ALTER SYSTEM SET synchronous_standby_names = '';  -- 空，表示异步复制
        ALTER SYSTEM SET synchronous_commit = off;  -- 异步提交
        PERFORM
```

**错误**: 单引号不匹配

---

**行 825** (sql):

```sql
-- 配置异步复制（AP倾向）（带错误处理）
DO $$
BEGIN
    BEGIN
        ALTER SYSTEM SET synchronous_standby_names = '';  -- 异步复制
        ALTER SYSTEM SET synchronous_commit = off;
        ALTER SYSTEM SET wal_level = r
```

**错误**: 单引号不匹配

---

### 15-分布式系统\04.06-数据库区块链模型-分布式账本与共识机制的形式化.md

**行 444** (sql):

```sql
-- 场景：供应链溯源系统
-- 1. 创建产品表
CREATE TABLE products (
    id UUID PRIMARY KEY,
    name VARCHAR(200),
    producer_id UUID,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. 创建溯源链表（区块链）
CREATE TABLE supp
```

**错误**: 单引号不匹配

---

**行 538** (sql):

```sql
-- 场景：数字资产交易系统
-- 1. 创建资产表
CREATE TABLE digital_assets (
    id UUID PRIMARY KEY,
    token_id VARCHAR(100) UNIQUE,
    owner_address VARCHAR(42),
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAUL
```

**错误**: 单引号不匹配

---

**行 612** (sql):

```sql
-- PoW挖矿函数
CREATE OR REPLACE FUNCTION mine_block(
    p_previous_hash VARCHAR,
    p_transactions JSONB,
    p_difficulty INTEGER
) RETURNS JSONB AS $$
DECLARE
    v_nonce BIGINT := 0;
    v_hash VARC
```

**错误**: 单引号不匹配

---

### 15-分布式系统\06-Citus分布式实战指南.md

**行 466** (sql):

```sql
-- 查看分片分布（带错误处理和性能测试）
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT nodename, COUNT(*) AS shard_count
FROM citus_shards
GROUP BY nodename;

-- 移动特定分片（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SE
```

**错误**: 括号不匹配

---

### 15-分布式系统\08-分布式事务实战.md

**行 340** (sql):

```sql
-- 获取锁
SELECT pg_try_advisory_lock(12345);  -- true表示获取成功

-- 业务逻辑
UPDATE limited_resource SET ...;

-- 释放锁
SELECT pg_advisory_unlock(12345);

-- 会话级锁（连接断开自动释放）
SELECT pg_advisory_lock(12345);  -- 阻塞直
```

**错误**: SELECT语句缺少FROM子句

---

### 15-分布式系统\ACID视角下的CAP选择.md

**行 156** (sql):

```sql
-- 弱ACID + AP模式（带错误处理）
DO $$
BEGIN
    BEGIN
        ALTER SYSTEM SET synchronous_standby_names = '';
        ALTER SYSTEM SET synchronous_commit = 'local';
        ALTER SYSTEM SET default_transactio
```

**错误**: 单引号不匹配

---

**行 206** (sql):

```sql
-- 冲突处理：临时降级（带错误处理）
-- 强ACID + CP → 弱ACID + AP（临时）
DO $$
BEGIN
    BEGIN
        ALTER SYSTEM SET synchronous_standby_names = '';
        ALTER SYSTEM SET synchronous_commit = 'local';
        PERFORM
```

**错误**: 单引号不匹配

---

**行 286** (sql):

```sql
-- 金融场景：强ACID + CP（带错误处理）
DO $$
BEGIN
    BEGIN
        ALTER SYSTEM SET synchronous_standby_names = 'standby1,standby2';
        ALTER SYSTEM SET synchronous_commit = 'remote_apply';
        ALTER SY
```

**错误**: 单引号不匹配

---

### 15-分布式系统\CAP与ACID的映射关系.md

**行 141** (sql):

```sql
-- CP模式：强一致性+强隔离性（带错误处理）
DO $$
BEGIN
    BEGIN
        ALTER SYSTEM SET default_transaction_isolation = 'serializable';
        ALTER SYSTEM SET synchronous_standby_names = 'standby1,standby2';

```

**错误**: 单引号不匹配

---

### 15-分布式系统\MVCC-ACID-CAP统一框架.md

**行 262** (sql):

```sql
-- CP模式（带错误处理）
DO $$
BEGIN
    BEGIN
        ALTER SYSTEM SET synchronous_standby_names = 'standby1,standby2';
        ALTER SYSTEM SET synchronous_commit = 'remote_apply';
        ALTER SYSTEM SET de
```

**错误**: 单引号不匹配

---

### 15-分布式系统\区块链集成完整指南.md

**行 722** (sql):

```sql
-- 产品表
CREATE TABLE products (
    product_id VARCHAR(100) PRIMARY KEY,
    blockchain_hash VARCHAR(66) UNIQUE,  -- 区块链交易哈希
    name TEXT NOT NULL,
    manufacturer VARCHAR(42),  -- 制造商地址
    created_
```

**错误**: 单引号不匹配

---

### 15-分布式系统\原子性与分区容错.md

**行 208** (sql):

```sql
-- 两阶段提交超时配置（带错误处理）
DO $$
BEGIN
    BEGIN
        SET statement_timeout = '30s';  -- 语句超时
        SET lock_timeout = '10s';       -- 锁超时
        RAISE NOTICE '超时配置设置成功';
    EXCEPTION
        WHEN OTH
```

**错误**: SELECT语句缺少FROM子句

---

### 15-分布式系统\持久性与可用性的权衡.md

**行 434** (sql):

```sql
-- 动态切换到异步提交（提高可用性）（带错误处理）
DO $$
BEGIN
    BEGIN
        ALTER SYSTEM SET synchronous_commit = 'off';
        PERFORM pg_reload_conf();
        RAISE NOTICE '动态切换到异步提交成功';
    EXCEPTION
        WHEN O
```

**错误**: SELECT语句缺少FROM子句

---

### 15-分布式系统\隔离级别与一致性模型.md

**行 355** (sql):

```sql
-- AP模式：弱隔离级别（带错误处理）
DO $$
BEGIN
    BEGIN
        ALTER SYSTEM SET default_transaction_isolation = 'read committed';
        ALTER SYSTEM SET synchronous_standby_names = '';
        PERFORM pg_reload
```

**错误**: 单引号不匹配

---

### 16-应用设计与开发\PL-pgSQL编程详解.md

**行 197** (sql):

```sql
-- 基本函数
CREATE OR REPLACE FUNCTION add_numbers(a INTEGER, b INTEGER)
RETURNS INTEGER
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN a + b;
END;
$$;

-- 调用函数
SELECT add_numbers(10, 20);

```

**错误**: SELECT语句缺少FROM子句

---

### 16-应用设计与开发\【深入】PostgreSQL+GraphQL完整实战指南.md

**行 2171** (sql):

```sql
-- 创建当前用户函数（带错误处理）
CREATE OR REPLACE FUNCTION current_user_id() RETURNS INTEGER AS $$
BEGIN
  RETURN nullif(current_setting('jwt.claims.user_id', true), '')::integer;
EXCEPTION
  WHEN OTHERS THEN

```

**错误**: 单引号不匹配

---

**行 2934** (sql):

```sql
-- 实时协作表结构（带错误处理）
-- 1. 文档表
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'documents') THEN
        DROP TABLE documents CASCADE;

```

**错误**: 单引号不匹配

---

### 16-应用设计与开发\事件触发器完整实战指南.md

**行 276** (sql):

```sql
-- 使用pg_event_trigger_ddl_commands()获取命令信息
CREATE OR REPLACE FUNCTION log_ddl_details()
RETURNS event_trigger AS $$
DECLARE
    cmd RECORD;
    cmd_text TEXT := '';
BEGIN
    FOR cmd IN
        SELECT
```

**错误**: 单引号不匹配

---

### 16-应用设计与开发\函数与存储过程.md

**行 197** (sql):

```sql
-- 创建函数（带完整错误处理和验证）
CREATE OR REPLACE FUNCTION calculate_total(p_price DECIMAL, p_quantity INTEGER)
RETURNS DECIMAL
LANGUAGE plpgsql
AS $$
BEGIN
    -- 参数验证
    IF p_price IS NULL THEN
        RAISE E
```

**错误**: SELECT语句缺少FROM子句

---

**行 242** (sql):

```sql
-- 带默认参数的函数（带完整错误处理和验证）
CREATE OR REPLACE FUNCTION greet(p_name TEXT, p_greeting TEXT DEFAULT 'Hello')
RETURNS TEXT
LANGUAGE plpgsql
AS $$
BEGIN
    -- 参数验证
    IF p_name IS NULL OR length(trim(p_name
```

**错误**: SELECT语句缺少FROM子句

---

**行 347** (sql):

```sql
-- 计算阶乘（带完整错误处理和验证，防止栈溢出）
CREATE OR REPLACE FUNCTION factorial(p_n INTEGER)
RETURNS BIGINT
LANGUAGE plpgsql
AS $$
BEGIN
    -- 参数验证
    IF p_n IS NULL THEN
        RAISE EXCEPTION '参数不能为空';
    END IF
```

**错误**: SELECT语句缺少FROM子句

---

**行 563** (sql):

```sql
-- SQL 函数（更快）
CREATE OR REPLACE FUNCTION calculate_total_sql(price DECIMAL, quantity INTEGER)
RETURNS DECIMAL AS $$
    SELECT price * quantity;
$$ LANGUAGE sql IMMUTABLE;

-- PL/pgSQL 函数（更灵活）
CREATE
```

**错误**: SELECT语句缺少FROM子句

---

### 16-应用设计与开发\函数高级特性指南.md

**行 105** (sql):

```sql
-- IMMUTABLE: 纯函数，结果只依赖参数
CREATE OR REPLACE FUNCTION add_numbers(a INTEGER, b INTEGER)
RETURNS INTEGER
LANGUAGE sql
IMMUTABLE
AS $$
    SELECT a + b;
$$;

-- STABLE: 结果在同一事务中不变
CREATE OR REPLACE FUNCT
```

**错误**: SELECT语句缺少FROM子句

---

**行 661** (sql):

```sql
-- 重载函数：不同参数类型
CREATE OR REPLACE FUNCTION add_numbers(a INTEGER, b INTEGER)
RETURNS INTEGER
LANGUAGE plpgsql
IMMUTABLE
AS $$
BEGIN
    RETURN a + b;
END;
$$;

CREATE OR REPLACE FUNCTION add_numbers(a
```

**错误**: SELECT语句缺少FROM子句

---

### 16-应用设计与开发\字符串函数详解.md

**行 286** (sql):

```sql
-- REPLACE() 函数（带性能测试）
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT REPLACE('Hello World', 'World', 'PostgreSQL') AS result;

-- TRANSLATE() 函数（字符级替换）（带性能测试）
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT TRA
```

**错误**: SELECT语句缺少FROM子句

---

**行 449** (sql):

```sql
-- LENGTH() 函数（带性能测试）
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT LENGTH('PostgreSQL') AS length;  -- 10

-- CHAR_LENGTH() 函数（同 LENGTH）（带性能测试）
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT CHAR_LENGTH('Post
```

**错误**: SELECT语句缺少FROM子句

---

### 16-应用设计与开发\应用架构\07.05-实时推荐系统.md

**行 1206** (sql):

```sql
-- 使用NOTIFY/NOTIFY实现异步写入
CREATE OR REPLACE FUNCTION async_insert_behavior(
    p_user_id BIGINT,
    p_item_id BIGINT,
    p_behavior_type VARCHAR(20)
)
RETURNS VOID AS $$
BEGIN
    -- 插入到临时表
    INSE
```

**错误**: 单引号不匹配

---

### 16-应用设计与开发\应用架构\07.06-数据科学实践.md

**行 881** (sql):

```sql
-- 安装plpython3u扩展
CREATE EXTENSION IF NOT EXISTS plpython3u;

-- 在线推理函数（使用Python）
CREATE OR REPLACE FUNCTION predict_ctr(
    p_user_id BIGINT,
    p_item_id BIGINT
)
RETURNS NUMERIC AS $$
import json
```

**错误**: SELECT语句缺少FROM子句

---

### 16-应用设计与开发\数学函数详解.md

**行 208** (sql):

```sql
-- ABS(): 绝对值（带性能测试）
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT ABS(-10) AS result;  -- 10

-- ROUND(): 四舍五入（带性能测试）
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT ROUND(3.14159, 2) AS result;  -- 3.14

-- F
```

**错误**: SELECT语句缺少FROM子句

---

**行 246** (sql):

```sql
-- SIN(): 正弦（带性能测试）
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT SIN(PI() / 2) AS result;  -- 1

-- COS(): 余弦（带性能测试）
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT COS(0) AS result;  -- 1

-- TAN(): 正切（带性能测试）
```

**错误**: SELECT语句缺少FROM子句

---

**行 280** (sql):

```sql
-- LN(): 自然对数（带性能测试）
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT LN(2.71828) AS result;  -- 约 1

-- LOG(): 对数（底数为 10）（带性能测试）
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT LOG(100) AS result;  -- 2

-- LOG10
```

**错误**: SELECT语句缺少FROM子句

---

**行 515** (sql):

```sql
   -- ✅ 好：充分测试计算结果（正确性）
   -- 测试数学函数
   SELECT
       ROUND(10.5) AS round_test,  -- 11
       FLOOR(10.5) AS floor_test,  -- 10
       CEIL(10.5) AS ceil_test;  -- 11

```

**错误**: SELECT语句缺少FROM子句

---

### 16-应用设计与开发\数据模型设计\09.02-数据建模完整指南.md

**行 1607** (sql):

```sql
-- 文章表
CREATE TABLE articles (
    article_id BIGSERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    slug VARCHAR(200) UNIQUE NOT NULL,
    content TEXT NOT NULL,
    excerpt TEXT,
    author_id
```

**错误**: 单引号不匹配

---

### 16-应用设计与开发\数据模型设计\09.04-ETL流程完整指南.md

**行 418** (sql):

```sql
-- 数据验证函数（带完整错误处理）
CREATE OR REPLACE FUNCTION validate_staging_data()
RETURNS TABLE (
    validation_rule TEXT,
    passed BOOLEAN,
    error_count INTEGER,
    error_details TEXT
)
LANGUAGE plpgsql
A
```

**错误**: 单引号不匹配

---

### 16-应用设计与开发\数据模型设计\09.05-数据质量管理指南.md

**行 581** (sql):

```sql
-- 格式标准化：去除空格
UPDATE users
SET username = TRIM(username),
    email = LOWER(TRIM(email));

-- 格式标准化：统一日期格式
UPDATE orders
SET order_date = DATE(order_date);

-- 格式标准化：统一状态格式
UPDATE orders
SET status =
```

**错误**: 单引号不匹配

---

### 16-应用设计与开发\日期时间函数详解.md

**行 197** (sql):

```sql
-- 当前时间戳（带时区）（带性能测试）
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT NOW();

EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT CURRENT_TIMESTAMP;

-- 当前日期（带性能测试）
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT CURRENT_DA
```

**错误**: SELECT语句缺少FROM子句

---

**行 260** (sql):

```sql
-- 时间加法（带性能测试）
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT NOW() + INTERVAL '1 day';

EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT NOW() + INTERVAL '1 hour';

EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT NOW(
```

**错误**: SELECT语句缺少FROM子句

---

**行 333** (sql):

```sql
-- 字符串转时间（带性能测试）
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT '2024-01-01 10:00:00'::TIMESTAMPTZ;

EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT TO_TIMESTAMP('2024-01-01 10:00:00', 'YYYY-MM-DD HH24:MI:SS');

```

**错误**: SELECT语句缺少FROM子句

---

### 16-应用设计与开发\查询函数与动态SQL完整指南.md

**行 444** (sql):

```sql
-- ❌ 不安全：字符串拼接
CREATE OR REPLACE FUNCTION unsafe_query(user_input TEXT)
RETURNS TABLE(id INTEGER)
LANGUAGE plpgsql
AS $$
DECLARE
    v_query TEXT;
BEGIN
    -- 危险：容易SQL注入
    v_query := 'SELECT id FRO
```

**错误**: 单引号不匹配

---

### 16-应用设计与开发\测试与质量保证\压力测试.md

**行 462** (sql):

```sql
-- 压力测试专用配置
ALTER SYSTEM SET max_connections = 500;
ALTER SYSTEM SET shared_buffers = '4GB';
ALTER SYSTEM SET work_mem = '64MB';
ALTER SYSTEM SET maintenance_work_mem = '1GB';
ALTER SYSTEM SET checkpo
```

**错误**: SELECT语句缺少FROM子句

---

### 16-应用设计与开发\测试与质量保证\性能测试.md

**行 583** (sql):

```sql
-- 测试单条INSERT性能
\timing on
INSERT INTO users (name, email) VALUES ('Test', 'test@example.com');
\timing off

-- 批量INSERT测试
\timing on
INSERT INTO users (name, email)
SELECT 'User' || generate_series(1
```

**错误**: SELECT语句缺少FROM子句

---

**行 1018** (sql):

```sql
-- 创建优化效果评估函数
CREATE OR REPLACE FUNCTION evaluate_optimization(
    p_test_name TEXT,
    p_before_value NUMERIC,
    p_after_value NUMERIC
)
RETURNS TABLE (
    improvement_percent NUMERIC,
    statu
```

**错误**: SELECT语句缺少FROM子句

---

### 16-应用设计与开发\测试与质量保证\测试自动化.md

**行 798** (sql):

```sql
-- 每天凌晨2点执行测试
SELECT cron.schedule(
    'daily-tests',
    '0 2 * * *',
    $$SELECT run_tests()$$
);

```

**错误**: SELECT语句缺少FROM子句

---

### 16-应用设计与开发\程序特性最佳实践指南.md

**行 870** (sql):

```sql
-- ✅ 使用RAISE NOTICE调试
CREATE OR REPLACE FUNCTION debug_function(p_id INTEGER)
RETURNS INTEGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_result INTEGER;
BEGIN
    RAISE NOTICE 'Function called with id: %',
```

**错误**: 单引号不匹配

---

### 16-应用设计与开发\行业案例\向量检索与RAG.md

**行 461** (sql):

```sql
-- 创建RRF融合函数
CREATE OR REPLACE FUNCTION rrf_fusion(
    vector_rank INT,
    text_rank INT,
    k INT DEFAULT 60
)
RETURNS NUMERIC AS $$
    SELECT
        COALESCE(1.0 / (k + vector_rank), 0) +

```

**错误**: SELECT语句缺少FROM子句

---

### 16-应用设计与开发\行业案例\实时推荐.md

**行 344** (sql):

```sql
-- 启用逻辑复制
ALTER SYSTEM SET wal_level = logical;
SELECT pg_reload_conf();

-- 创建发布
CREATE PUBLICATION user_events_pub FOR TABLE user_events;

```

**错误**: SELECT语句缺少FROM子句

---

### 16-应用设计与开发\行业案例\性能问题-案例库.md

**行 574** (sql):

```sql
-- 1. 提升max_wal_size
ALTER SYSTEM SET max_wal_size = '4GB';  -- 从1GB提升到4GB

-- 2. 增加checkpoint_timeout
ALTER SYSTEM SET checkpoint_timeout = '15min';  -- 从5min增加到15min

-- 3. 优化checkpoint_completion_t
```

**错误**: SELECT语句缺少FROM子句

---

**行 660** (sql):

```sql
-- 方案1：使用fillfactor减少页分裂
ALTER TABLE events SET (fillfactor = 90);
REINDEX TABLE events;

-- 方案2：使用UUID或反向ID
-- 创建反向ID函数
CREATE OR REPLACE FUNCTION reverse_bigint(bigint)
RETURNS bigint AS $$
    SELE
```

**错误**: SELECT语句缺少FROM子句

---

### 16-应用设计与开发\行业案例\金融账务一致性.md

**行 998** (sql):

```sql
-- 启用逻辑复制
ALTER SYSTEM SET wal_level = logical;
SELECT pg_reload_conf();

-- 创建发布
CREATE PUBLICATION accounts_audit_pub FOR TABLE accounts, ledger;
CREATE PUBLICATION accounts_audit_pub FOR TABLE acco
```

**错误**: SELECT语句缺少FROM子句

---

### 17-数据模型设计\09.02-BCNF与3NF-完整证明稿.md

**行 704** (sql):

```sql
-- 范式验证函数（带错误处理）
DO $$
BEGIN
    BEGIN
        CREATE OR REPLACE FUNCTION verify_bcnf(
            p_table_name TEXT,
            p_functional_dependencies JSONB
        )
        RETURNS TABLE (

```

**错误**: 单引号不匹配

---

### 17-数据模型设计\09.02-数据建模完整指南.md

**行 1763** (sql):

```sql
-- 文章表
CREATE TABLE articles (
    article_id BIGSERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    slug VARCHAR(200) UNIQUE NOT NULL,
    content TEXT NOT NULL,
    excerpt TEXT,
    author_id
```

**错误**: 单引号不匹配

---

### 17-数据模型设计\09.03-数据仓库设计指南.md

**行 691** (sql):

```sql
-- 按日期分区事实表
CREATE TABLE sales_fact (
    sale_id BIGSERIAL,
    date_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    customer_id INTEGER NOT NULL,
    store_id INTEGER NOT NULL,
    quantit
```

**错误**: 单引号不匹配

---

### 17-数据模型设计\09.05-数据质量管理指南.md

**行 533** (sql):

```sql
-- 格式标准化：去除空格
UPDATE users
SET username = TRIM(username),
    email = LOWER(TRIM(email));

-- 格式标准化：统一日期格式
UPDATE orders
SET order_date = DATE(order_date);

-- 格式标准化：统一状态格式
UPDATE orders
SET status =
```

**错误**: 单引号不匹配

---

**行 1118** (sql):

```sql
-- 1. 数据质量问题解释函数
CREATE OR REPLACE FUNCTION explain_quality_issue(
    p_table_name TEXT,
    p_column_name TEXT,
    p_issue_type TEXT
)
RETURNS TABLE (
    issue_description TEXT,
    root_cause TEX
```

**错误**: SELECT语句缺少FROM子句

---

### 18-版本特性\18.01-PostgreSQL18新特性\02-跳跃扫描Skip-Scan完整指南.md

**行 832** (sql):

```sql
-- 性能测试：对比启用/禁用Skip Scan（带错误处理）
BEGIN;
DO $$
BEGIN
    SET LOCAL enable_indexskipscan = off;  -- 禁用
    RAISE NOTICE 'Skip Scan已禁用，执行查询...';
    -- EXPLAIN (ANALYZE, BUFFERS, TIMING) SELECT ...;
EXCEP
```

**错误**: SELECT语句缺少FROM子句

---

### 18-版本特性\18.01-PostgreSQL18新特性\03-虚拟生成列完整实战指南.md

**行 237** (sql):

```sql
-- 性能测试：表大小对比（带错误处理）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    pg_size_pretty(pg_total_relation_size('test_virtual')) AS virtual_size,
    pg_size_pretty(pg_total_relation_size('test_stored
```

**错误**: SELECT语句缺少FROM子句

---

**行 311** (sql):

```sql
CREATE TABLE analytics (
    id SERIAL PRIMARY KEY,
    data JSONB,
    -- 复杂聚合计算（昂贵）
    score GENERATED ALWAYS AS (
        calculate_complex_score(data)  -- 自定义函数，计算耗时
    ) STORED;  -- 必须STORED，否则
```

**错误**: 括号不匹配

---

### 18-版本特性\18.01-PostgreSQL18新特性\04-UUIDv7完整指南.md

**行 458** (sql):

```sql
-- 性能测试：从UUIDv7提取Unix时间戳（毫秒）（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT uuid_extract_time('018d2a54-6c1f-7000-8000-123456789abc'::uuid);
-- 输出：1701234567890（Unix毫秒）
COMMIT;
EXCEPTION
```

**错误**: SELECT语句缺少FROM子句

---

**行 1045** (sql):

```sql
-- 1. 检查UUIDv7格式
SELECT gen_uuid_v7();
-- 应该以018d开头（版本7标识）

-- 2. 检查时间戳提取
SELECT
    gen_uuid_v7() AS uuid,
    uuid_extract_time(gen_uuid_v7()) AS timestamp_ms,
    to_timestamp(uuid_extract_time(gen
```

**错误**: SELECT语句缺少FROM子句

---

### 18-版本特性\18.01-PostgreSQL18新特性\06-OAuth2.0认证集成完整指南.md

**行 212** (sql):

```sql
-- 性能测试：创建角色（带错误处理）
BEGIN;
CREATE ROLE IF NOT EXISTS google_users;
GRANT CONNECT ON DATABASE mydb TO google_users;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO google_users;
COMMIT;
EXCEPTION
    WH
```

**错误**: SELECT语句缺少FROM子句

---

**行 466** (sql):

```sql
-- 性能测试：创建受限角色（带错误处理）
BEGIN;
CREATE ROLE IF NOT EXISTS oauth_readonly;
GRANT CONNECT ON DATABASE mydb TO oauth_readonly;
GRANT USAGE ON SCHEMA public TO oauth_readonly;
GRANT SELECT ON ALL TABLES IN S
```

**错误**: SELECT语句缺少FROM子句

---

**行 507** (sql):

```sql
-- 性能测试：配置Azure AD OAuth（带错误处理）
BEGIN;
DO $$
BEGIN
    ALTER SYSTEM SET oauth_enabled = on;
    ALTER SYSTEM SET oauth_issuer = 'https://login.microsoftonline.com/company-tenant-id/v2.0';
    ALTER SY
```

**错误**: SELECT语句缺少FROM子句

---

**行 849** (sql):

```sql
-- 性能测试：1. 创建最小权限角色（带错误处理）
BEGIN;
CREATE ROLE IF NOT EXISTS oauth_readonly;
GRANT CONNECT ON DATABASE mydb TO oauth_readonly;
GRANT USAGE ON SCHEMA public TO oauth_readonly;
GRANT SELECT ON ALL TABLES
```

**错误**: SELECT语句缺少FROM子句

---

**行 978** (sql):

```sql
   ALTER SYSTEM SET oauth_enabled = on;
   ALTER SYSTEM SET oauth_issuer = 'https://oauth-provider.com';
   SELECT pg_reload_conf();

```

**错误**: SELECT语句缺少FROM子句

---

### 18-版本特性\18.01-PostgreSQL18新特性\08-EXPLAIN增强完整指南.md

**行 214** (sql):

```sql
EXPLAIN (
    ANALYZE,        -- 实际执行
    BUFFERS,        -- 缓冲区统计
    VERBOSE,        -- 详细输出
    TIMING,         -- 时间统计
    MEMORY,         -- ⭐ 内存统计（PG18）
    SERIALIZE,      -- ⭐ 序列化统计（PG18）

```

**错误**: SELECT语句缺少FROM子句

---

### 18-版本特性\18.01-PostgreSQL18新特性\08-性能调优实战指南.md

**行 533** (sql):

```sql
-- 自动创建分区（使用pg_partman扩展）
CREATE EXTENSION pg_partman;

SELECT partman.create_parent(
    p_parent_table := 'public.logs',
    p_control := 'timestamp',
    p_type := 'native',
    p_interval := 'mont
```

**错误**: SELECT语句缺少FROM子句

---

### 18-版本特性\18.01-PostgreSQL18新特性\11-查询优化器深度解析.md

**行 41** (sql):

```sql
-- 性能测试：查看成本参数（带错误处理）
BEGIN;
DO $$
DECLARE
    seq_cost TEXT;
    random_cost TEXT;
    tuple_cost TEXT;
BEGIN
    SHOW seq_page_cost INTO seq_cost;
    SHOW random_page_cost INTO random_cost;
    SHO
```

**错误**: SELECT语句缺少FROM子句

---

**行 148** (sql):

```sql
-- 性能测试：提高统计精度（带错误处理）
BEGIN;
ALTER TABLE users ALTER COLUMN email
SET STATISTICS 1000;  -- 默认100
COMMIT;
EXCEPTION
    WHEN undefined_table THEN
        RAISE NOTICE '表users不存在';
    WHEN undefined_co
```

**错误**: SELECT语句缺少FROM子句

---

**行 862** (sql):

```sql
-- 性能测试：降低某个路径成本（带错误处理）
BEGIN;
SET random_page_cost = 1.0;  -- 让索引更"便宜"
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '设置random_page_cost失败: %', SQLERRM;
        ROLLBACK;
        RAISE;
```

**错误**: SELECT语句缺少FROM子句

---

### 18-版本特性\18.01-PostgreSQL18新特性\12-时态约束与时间段完整性指南.md

**行 126** (sql):

```sql
-- 性能测试：❌ 传统主键（无法防止时间段冲突，带错误处理）
BEGIN;
CREATE TABLE IF NOT EXISTS room_booking_old (
    room_id INT,
    booking_date DATE,
    guest_name TEXT,
    PRIMARY KEY (room_id, booking_date)  -- 仅保证每天每房间一个
```

**错误**: 括号不匹配

---

**行 333** (sql):

```sql
-- 性能测试：案例：酒店房间预订系统（带错误处理）
BEGIN;
CREATE TABLE IF NOT EXISTS hotel_bookings (
    booking_id SERIAL,
    room_id INT NOT NULL,
    guest_name TEXT NOT NULL,
    check_in TIMESTAMPTZ NOT NULL,
    chec
```

**错误**: 括号不匹配

---

**行 443** (sql):

```sql
-- 性能测试：案例：租赁合同管理（带错误处理）
BEGIN;
CREATE TABLE IF NOT EXISTS lease_contracts (
    contract_id SERIAL PRIMARY KEY,
    property_id INT NOT NULL,
    tenant_name TEXT NOT NULL,
    lease_start DATE NOT N
```

**错误**: 括号不匹配

---

**行 555** (sql):

```sql
-- 性能测试：父表：员工合同（带错误处理）
BEGIN;
CREATE TABLE IF NOT EXISTS employee_contracts (
    employee_id INT,
    contract_start DATE NOT NULL,
    contract_end DATE NOT NULL,
    position TEXT,
    salary NUMER
```

**错误**: 括号不匹配

---

**行 727** (sql):

```sql
-- 禁止关系：overlaps, overlapped-by, starts, started-by,
--          during, contains, finishes, finished-by, equals

-- 允许关系：before, after, meets, met-by

-- 实例说明
-- Range A: [2025-01-15 08:00, 2025-01-1
```

**错误**: 括号不匹配

---

**行 749** (sql):

```sql
-- PostgreSQL 18使用左闭右开区间（数学标准）
-- Range类型：tstzrange(lower, upper, '[)')

-- 实例
SELECT tstzrange('2025-01-15 10:00', '2025-01-15 12:00');
-- 输出：["2025-01-15 10:00:00+00","2025-01-15 12:00:00+00")

-- 边
```

**错误**: 括号不匹配; SELECT语句缺少FROM子句

---

### 18-版本特性\18.01-PostgreSQL18新特性\13-存储过程与触发器实战.md

**行 418** (sql):

```sql
CREATE OR REPLACE FUNCTION safe_divide(a NUMERIC, b NUMERIC)
RETURNS NUMERIC AS $$
BEGIN
    RETURN a / b;
EXCEPTION
    WHEN division_by_zero THEN
        RAISE NOTICE '除数为零，返回NULL';
        RETURN N
```

**错误**: SELECT语句缺少FROM子句

---

**行 741** (sql):

```sql
CREATE OR REPLACE FUNCTION debug_function()
RETURNS VOID AS $$
DECLARE
    var1 INT := 100;
BEGIN
    RAISE NOTICE '变量值: %', var1;
    RAISE DEBUG '调试信息';
    RAISE LOG '日志信息';
    RAISE WARNING '警告信息
```

**错误**: SELECT语句缺少FROM子句

---

### 18-版本特性\18.01-PostgreSQL18新特性\14-数据类型深度解析.md

**行 15** (sql):

```sql
-- 性能测试：类型选择（带错误处理）
BEGIN;
-- 类型选择
-- SMALLINT    -- 2字节, -32768 to 32767
-- INTEGER     -- 4字节, -2^31 to 2^31-1
-- BIGINT      -- 8字节, -2^63 to 2^63-1

-- 自增
-- SERIAL      -- INTEGER + SEQUENCE
-- B
```

**错误**: SELECT语句缺少FROM子句

---

**行 451** (sql):

```sql
-- 安装扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- UUID生成
SELECT
    uuid_generate_v4() AS v4,      -- 随机UUID
    gen_random_uuid() AS random,   -- 随机（内置）
    uuidv7() AS v7;                -- UU
```

**错误**: SELECT语句缺少FROM子句

---

**行 571** (sql):

```sql
-- 范围类型
int4range     -- INTEGER范围
int8range     -- BIGINT范围
numrange      -- NUMERIC范围
tsrange       -- TIMESTAMP范围
tstzrange     -- TIMESTAMPTZ范围
daterange     -- DATE范围

-- 创建范围
SELECT
    int4rang
```

**错误**: 括号不匹配

---

**行 703** (sql):

```sql
-- 文本转数值
SELECT '123'::INTEGER;
SELECT CAST('123' AS INTEGER);

-- 数值转文本
SELECT 123::TEXT;

-- 日期转换
SELECT '2024-01-01'::DATE;
SELECT to_date('2024-01-01', 'YYYY-MM-DD');

-- JSONB转换
SELECT '{"name":"
```

**错误**: SELECT语句缺少FROM子句

---

### 18-版本特性\18.01-PostgreSQL18新特性\15-WAL与检查点优化完整指南.md

**行 381** (sql):

```sql
-- 性能测试：测试不同压缩算法（带错误处理）

-- 1. 无压缩（基线）
BEGIN;
ALTER SYSTEM SET wal_compression = off;
SELECT pg_reload_conf();
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '设置wal_compression失败: %', SQL
```

**错误**: SELECT语句缺少FROM子句

---

**行 719** (sql):

```sql
-- 检查点参数

-- 1. 检查点超时时间
SHOW checkpoint_timeout;  -- 默认：5min
-- 推荐：高写入场景15-30min
ALTER SYSTEM SET checkpoint_timeout = '15min';

-- 2. WAL大小触发阈值
SHOW max_wal_size;  -- 默认：1GB
-- 推荐：高写入场景4GB-16GB
ALTER
```

**错误**: SELECT语句缺少FROM子句

---

**行 753** (sql):

```sql
-- 高性能OLTP场景（1000+ TPS）

-- WAL配置
ALTER SYSTEM SET wal_buffers = '128MB';
ALTER SYSTEM SET wal_compression = 'lz4';  -- CPU友好
ALTER SYSTEM SET wal_level = 'replica';
ALTER SYSTEM SET synchronous_commi
```

**错误**: SELECT语句缺少FROM子句

---

### 18-版本特性\18.01-PostgreSQL18新特性\15-扩展开发完整指南.md

**行 209** (sql):

```sql
-- 性能测试：SQL包装（带错误处理）
BEGIN;
CREATE OR REPLACE FUNCTION add_numbers(INT, INT)
RETURNS INT AS '$libdir/my_extension', 'add_numbers'
LANGUAGE C IMMUTABLE STRICT;
COMMIT;
EXCEPTION
    WHEN OTHERS THEN

```

**错误**: SELECT语句缺少FROM子句

---

**行 311** (sql):

```sql
-- 性能测试：SQL定义（带错误处理）
BEGIN;
DO $$
BEGIN
    CREATE TYPE IF NOT EXISTS complex;
EXCEPTION
    WHEN duplicate_object THEN
        RAISE NOTICE '类型complex已存在';
    WHEN OTHERS THEN
        RAISE NOTICE '
```

**错误**: SELECT语句缺少FROM子句

---

**行 557** (sql):

```sql
-- 使用pgTAP
CREATE EXTENSION pgtap;

-- 测试脚本
BEGIN;
SELECT plan(5);

SELECT has_function('my_extension', 'hello', ARRAY['text']);
SELECT function_returns('my_extension', 'hello', ARRAY['text'], 'text')
```

**错误**: SELECT语句缺少FROM子句

---

**行 664** (sql):

```sql
-- 字符串工具
CREATE OR REPLACE FUNCTION utils.slugify(input TEXT)
RETURNS TEXT AS $$
BEGIN
    RETURN lower(regexp_replace(
        regexp_replace(input, '[^a-zA-Z0-9\s-]', '', 'g'),
        '[\s-]+', '-'
```

**错误**: 单引号不匹配; SELECT语句缺少FROM子句

---

### 18-版本特性\18.01-PostgreSQL18新特性\16-统计信息增强与查询规划指南.md

**行 408** (sql):

```sql
-- 性能测试：大表ANALYZE性能测试（带错误处理）
BEGIN;
CREATE TABLE IF NOT EXISTS huge_table AS
SELECT
    generate_series(1, 100000000) AS id,
    md5(random()::text) AS data,
    (random() * 1000)::int AS value;
COMMI
```

**错误**: SELECT语句缺少FROM子句

---

### 18-版本特性\18.01-PostgreSQL18新特性\18-存储管理与TOAST优化指南.md

**行 770** (sql):

```sql
-- 创建Large Object
SELECT lo_create(0);  -- 返回OID：16789

-- 写入数据（流式）
\lo_import /path/to/large_video.mp4 16789

-- 关联到表
CREATE TABLE videos (
    video_id SERIAL PRIMARY KEY,
    title TEXT,
    video_
```

**错误**: SELECT语句缺少FROM子句

---

**行 1095** (sql):

```sql
-- HDD配置（传统）
ALTER SYSTEM SET random_page_cost = 4.0;
ALTER SYSTEM SET seq_page_cost = 1.0;
ALTER SYSTEM SET effective_io_concurrency = 2;

-- SSD配置（推荐）
ALTER SYSTEM SET random_page_cost = 1.1;
ALTER
```

**错误**: SELECT语句缺少FROM子句

---

### 18-版本特性\18.01-PostgreSQL18新特性\18-并发控制深度解析.md

**行 335** (sql):

```sql
-- 终止阻塞会话
SELECT pg_cancel_backend(blocking_pid);   -- 温和取消
SELECT pg_terminate_backend(blocking_pid); -- 强制终止

```

**错误**: SELECT语句缺少FROM子句

---

### 18-版本特性\18.01-PostgreSQL18新特性\19-分区表增强与智能裁剪指南.md

**行 780** (sql):

```sql
-- 创建自动分区管理函数
CREATE OR REPLACE FUNCTION create_partitions_for_next_months(
    p_table_name TEXT,
    p_months_ahead INT DEFAULT 3
)
RETURNS TEXT AS $$
DECLARE
    v_start_date DATE;
    v_end_date D
```

**错误**: 单引号不匹配

---

**行 849** (sql):

```sql
-- 分区归档函数（移动到归档表）
CREATE OR REPLACE FUNCTION archive_old_partitions(
    p_table_name TEXT,
    p_months_old INT DEFAULT 12
)
RETURNS TEXT AS $$
DECLARE
    v_partition_record RECORD;
    v_archive_ta
```

**错误**: 单引号不匹配

---

### 18-版本特性\18.01-PostgreSQL18新特性\19-高级SQL查询技巧.md

**行 434** (sql):

```sql
-- 数组操作
SELECT
    ARRAY[1,2,3,4] && ARRAY[3,4,5,6] AS has_overlap,      -- true
    ARRAY[1,2,3,4] @> ARRAY[2,3] AS contains,             -- true
    ARRAY[1,2,3] || ARRAY[4,5] AS concatenate,
```

**错误**: SELECT语句缺少FROM子句

---

### 18-版本特性\18.01-PostgreSQL18新特性\20-全文检索与排序规则变更指南.md

**行 267** (sql):

```sql
-- 性能测试：PostgreSQL 18新增：casefold()函数（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    'straße'::text = 'STRASSE'::text AS traditional_compare,
    lower('STRASSE') = 'straße' AS lower_
```

**错误**: SELECT语句缺少FROM子句

---

### 18-版本特性\18.01-PostgreSQL18新特性\21-云原生部署与配置优化指南.md

**行 945** (sql):

```sql
-- 阿里云RDS PostgreSQL 18参数优化

-- 1. AIO配置
ALTER SYSTEM SET io_method = 'worker';  -- 阿里云推荐
ALTER SYSTEM SET effective_io_concurrency = 48;
ALTER SYSTEM SET maintenance_io_concurrency = 48;

-- 2. ESSD性
```

**错误**: SELECT语句缺少FROM子句

---

### 18-版本特性\18.01-PostgreSQL18新特性\23-PostGIS地理空间数据库实战.md

**行 621** (sql):

```sql
-- geometry: 平面坐标，快
SELECT ST_Distance(
    ST_MakePoint(116.4, 39.9),
    ST_MakePoint(116.5, 40.0)
);  -- 返回度数

-- geography: 球面坐标，准确
SELECT ST_Distance(
    ST_MakePoint(116.4, 39.9)::geography,

```

**错误**: SELECT语句缺少FROM子句

---

### 18-版本特性\18.01-PostgreSQL18新特性\24-全文检索深度实战.md

**行 42** (sql):

```sql
-- 性能测试：文本转向量（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT to_tsvector('english', 'PostgreSQL is a powerful database');
-- 结果: 'databas':5 'postgresql':1 'power':4
COMMIT;
EXCEPTION

```

**错误**: SELECT语句缺少FROM子句

---

**行 83** (sql):

```sql
-- 性能测试：安装zhparser（带错误处理）
BEGIN;
CREATE EXTENSION IF NOT EXISTS zhparser;
COMMIT;
EXCEPTION
    WHEN duplicate_object THEN
        RAISE NOTICE '扩展zhparser已存在';
    WHEN OTHERS THEN
        RAISE NOTI
```

**错误**: SELECT语句缺少FROM子句

---

### 18-版本特性\18.01-PostgreSQL18新特性\24-容灾与高可用架构设计指南.md

**行 1217** (sql):

```sql
-- RTO优化清单

-- 1. 减少检测时间
ALTER SYSTEM SET wal_receiver_timeout = 5000;  -- 5秒检测
ALTER SYSTEM SET wal_sender_timeout = 5000;

-- 2. 加速故障切换（Patroni配置）
# patroni.yml
bootstrap:
  dcs:
    ttl: 15  -- 缩短T
```

**错误**: SELECT语句缺少FROM子句

---

### 18-版本特性\18.01-PostgreSQL18新特性\25-性能基准测试与调优实战指南.md

**行 1085** (sql):

```sql
-- 1. 优化分区策略（按天分区）
CREATE TABLE sensor_data (
    device_id INT,
    timestamp TIMESTAMPTZ,
    value NUMERIC,
    PRIMARY KEY (device_id, timestamp)
) PARTITION BY RANGE (timestamp);

-- 2. 使用BRIN索引（
```

**错误**: SELECT语句缺少FROM子句

---

### 18-版本特性\18.01-PostgreSQL18新特性\26-扩展开发与插件生态指南.md

**行 494** (sql):

```sql
-- 性能测试：调试技巧1：使用RAISE NOTICE（带错误处理）
BEGIN;
CREATE OR REPLACE FUNCTION debug_example(p_value INT)
RETURNS INT AS $$
DECLARE
    v_result INT;
BEGIN
    RAISE NOTICE '输入参数: %', p_value;

    v_result :=
```

**错误**: SELECT语句缺少FROM子句

---

**行 711** (sql):

```sql
-- complex--1.0.sql

-- 注册类型
CREATE TYPE complex;

CREATE FUNCTION complex_in(cstring)
RETURNS complex
AS 'MODULE_PATHNAME'
LANGUAGE C IMMUTABLE STRICT;

CREATE FUNCTION complex_out(complex)
RETURNS c
```

**错误**: SELECT语句缺少FROM子句

---

### 18-版本特性\18.01-PostgreSQL18新特性\27-多模态数据库能力指南.md

**行 1288** (sql):

```sql
-- 多模态查询性能调优

-- 1. work_mem调整（向量/排序）
SET work_mem = '256MB';  -- 向量搜索需要更多内存

-- 2. 向量索引参数
SET hnsw.ef_search = 100;  -- 提高召回率

-- 3. 并行查询
SET max_parallel_workers_per_gather = 4;

-- 4. JIT编译
SET jit
```

**错误**: SELECT语句缺少FROM子句

---

### 18-版本特性\18.01-PostgreSQL18新特性\29-pg_cron定时任务实战.md

**行 336** (sql):

```sql
-- 性能测试：创建备份函数（带错误处理）
BEGIN;
CREATE OR REPLACE FUNCTION backup_database()
RETURNS VOID AS $$
DECLARE
    backup_file TEXT;
BEGIN
    backup_file := '/backup/db_' || to_char(now(), 'YYYYMMDD_HH24MISS')
```

**错误**: SELECT语句缺少FROM子句

---

### 18-版本特性\18.01-PostgreSQL18新特性\30-pg_stat_statements性能分析.md

**行 409** (sql):

```sql
-- 性能测试：重置所有统计（带错误处理）
BEGIN;
DO $$
BEGIN
    PERFORM pg_stat_statements_reset();
    RAISE NOTICE '所有统计已重置';
EXCEPTION
    WHEN undefined_function THEN
        RAISE NOTICE 'pg_stat_statements扩展未安装';

```

**错误**: SELECT语句缺少FROM子句

---

### 18-版本特性\18.01-PostgreSQL18新特性\31-连接管理深度优化.md

**行 521** (sql):

```sql
-- 创建只读用户（最小权限）
CREATE USER readonly_user WITH PASSWORD 'secure_password';
GRANT CONNECT ON DATABASE mydb TO readonly_user;
GRANT USAGE ON SCHEMA public TO readonly_user;
GRANT SELECT ON ALL TABLES IN
```

**错误**: SELECT语句缺少FROM子句

---

### 18-版本特性\18.01-PostgreSQL18新特性\36-SQL注入防御完整指南.md

**行 253** (sql):

```sql
-- 性能测试：应用账号：只授予必要权限（带错误处理）
BEGIN;
CREATE ROLE IF NOT EXISTS app_user LOGIN PASSWORD 'strong_password';
GRANT CONNECT ON DATABASE mydb TO app_user;
GRANT SELECT, INSERT, UPDATE ON users TO app_user;
-
```

**错误**: SELECT语句缺少FROM子句

---

**行 347** (sql):

```sql
-- 性能测试：启用查询日志（带错误处理）
BEGIN;
DO $$
BEGIN
    ALTER SYSTEM SET log_statement = 'all';  -- 或 'mod'（修改语句）
    ALTER SYSTEM SET log_min_duration_statement = 0;
    PERFORM pg_reload_conf();
    RAISE NOTI
```

**错误**: SELECT语句缺少FROM子句

---

### 18-版本特性\18.01-PostgreSQL18新特性\39-外键与约束完全实战.md

**行 564** (sql):

```sql
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    total_amount NUMERIC(10, 2) NOT NULL DEFAULT 0.00,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    notes TEXT  --
```

**错误**: 单引号不匹配

---

**行 616** (sql):

```sql
-- 防止时间重叠
CREATE EXTENSION btree_gist;

CREATE TABLE room_bookings (
    id SERIAL PRIMARY KEY,
    room_id INT,
    booked_range tstzrange,
    EXCLUDE USING gist (
        room_id WITH =,
        bo
```

**错误**: 括号不匹配

---

### 18-版本特性\18.01-PostgreSQL18新特性\41-实时数据库完全指南.md

**行 225** (sql):

```sql
-- Payload最大8000字节
SELECT length('very long string'::text);

-- 超过限制需要传递ID，再查询
PERFORM pg_notify(
    'large_data_event',
    json_build_object('id', NEW.id)::text
);

```

**错误**: SELECT语句缺少FROM子句

---

**行 454** (sql):

```sql
-- 消息表
CREATE TABLE messages (
    id BIGSERIAL PRIMARY KEY,
    room_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 通知函数
-
```

**错误**: 单引号不匹配

---

**行 706** (python):

```python
   try:
       conn.poll()
       # 处理通知
   except psycopg2.DatabaseError as e:
       print(f"数据库错误: {e}")
       # 重新连接
       reconnect()

```

**错误**: 语法错误: unexpected indent (行 1)

---

**行 718** (python):

```python
   import time

   last_notify_time = time.time()

   while True:
       # 10秒超时
       if select.select([conn], [], [], 10) == ([], [], []):
           # 发送心跳查询
           cursor.execute("SELECT 1;")
```

**错误**: 语法错误: unexpected indent (行 1)

---

### 18-版本特性\18.01-PostgreSQL18新特性\42-全文搜索深度实战.md

**行 58** (sql):

```sql
-- 性能测试：tsvector: 文档向量（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT to_tsvector('english', 'The quick brown fox jumps over the lazy dog');
-- 结果: 'brown':3 'dog':9 'fox':4 'jump':5 'la
```

**错误**: SELECT语句缺少FROM子句

---

**行 389** (sql):

```sql
-- 创建扩展
CREATE EXTENSION zhparser;

-- 创建中文文本搜索配置
CREATE TEXT SEARCH CONFIGURATION chinese (PARSER = zhparser);

-- 添加token映射
ALTER TEXT SEARCH CONFIGURATION chinese ADD MAPPING FOR
    n,v,a,i,e,l WI
```

**错误**: SELECT语句缺少FROM子句

---

**行 474** (sql):

```sql
-- 完整的博客搜索表
CREATE TABLE blog_posts (
    id BIGSERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    author_id BIGINT NOT NULL,
    category VARCHAR(50),
    tags TEXT[],
    pu
```

**错误**: 单引号不匹配

---

### 18-版本特性\18.01-PostgreSQL18新特性\AI_ML集成.md

**行 548** (sql):

```sql
-- 语义搜索函数
-- SELECT ai.semantic_search(
--     'What is PostgreSQL?',
--     'text-embedding-3-small',
--     10
-- );

-- 相似度计算函数
-- SELECT ai.cosine_similarity(
--     ai.generate_embedding('text-em
```

**错误**: SELECT语句缺少FROM子句

---

**行 1288** (sql):

```sql
-- 使用AI函数生成向量
SELECT ai.generate_embedding('text-embedding-3-small', 'text');
-- PostgreSQL 18支持AI函数

```

**错误**: SELECT语句缺少FROM子句

---

**行 1310** (sql):

```sql
-- ✅ 好：加载ML模型
SELECT ml.load_model('my_model', '/path/to/model.pkl');
-- 加载模型到数据库

```

**错误**: SELECT语句缺少FROM子句

---

### 18-版本特性\18.01-PostgreSQL18新特性\SQL新语法特性.md

**行 431** (sql):

```sql
-- 创建测试表
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(100),
    phone VARCHAR(20),
    name VARCHAR(100)
);

-- 插入测试数据
INSERT INTO users (email, phone, name)
VALUES
    ('user1@ex
```

**错误**: 单引号不匹配

---

**行 544** (sql):

```sql
-- 类型转换（PostgreSQL 18 增强）
SELECT
    '123'::INTEGER AS str_to_int,
    123::TEXT AS int_to_str,
    '2025-01-01'::DATE AS str_to_date,
    '100.50'::DECIMAL(10,2) AS str_to_decimal,
    '{"key": "valu
```

**错误**: SELECT语句缺少FROM子句

---

**行 563** (sql):

```sql
-- 类型函数增强（PostgreSQL 18）
SELECT
    -- 数组函数
    ARRAY[1, 2, 3] || ARRAY[4, 5] AS array_concat,
    array_length(ARRAY[1, 2, 3], 1) AS array_len,
    array_agg(id) AS id_array,
    -- 范围函数
    '[1,10]'
```

**错误**: SELECT语句缺少FROM子句

---

**行 1171** (sql):

```sql
-- ✅ 好：检查PostgreSQL版本
SELECT version();
-- 确保使用PostgreSQL 18+

```

**错误**: SELECT语句缺少FROM子句

---

### 18-版本特性\18.01-PostgreSQL18新特性\事务处理增强.md

**行 154** (sql):

```sql
-- PostgreSQL 18 优化：事务提交性能提升
-- 1. 快速提交
BEGIN;
INSERT INTO orders (customer_id, amount) VALUES (1, 100);
COMMIT;  -- 提交时间减少 40%

-- 2. 批量提交优化
BEGIN;
INSERT INTO orders (customer_id, amount)
SELECT gen
```

**错误**: SELECT语句缺少FROM子句

---

**行 456** (sql):

```sql
-- 优化：批量操作
BEGIN;
INSERT INTO orders (customer_id, amount)
SELECT generate_series(1, 1000), random() * 100;
COMMIT;

-- 优化：使用异步提交（谨慎使用）
SET synchronous_commit = off;
BEGIN;
INSERT INTO orders (custome
```

**错误**: SELECT语句缺少FROM子句

---

### 18-版本特性\18.01-PostgreSQL18新特性\向量数据库增强.md

**行 812** (sql):

```sql
-- 处理：索引损坏
REINDEX INDEX idx_documents_embedding_hnsw;

-- 处理：查询性能问题
-- 1. 检查索引使用情况
EXPLAIN (ANALYZE, BUFFERS, TIMING) SELECT ...;

-- 2. 更新统计信息
ANALYZE documents;

-- 3. 调整索引参数
DROP INDEX idx_documen
```

**错误**: SELECT语句缺少FROM子句

---

### 18-版本特性\18.01-PostgreSQL18新特性\复制机制改进.md

**行 398** (sql):

```sql
-- PostgreSQL 18 自动删除空闲复制槽
-- 1. 配置自动删除策略
-- postgresql.conf
max_slot_wal_keep_size = 10GB  -- 最大保留 WAL 大小
wal_keep_size = 1GB  -- 保留的 WAL 大小

-- 2. 自动删除条件
-- - 复制槽空闲超过配置的时间
-- - WAL 积累超过配置的大小
-- - 订阅
```

**错误**: SELECT语句缺少FROM子句

---

**行 917** (sql):

```sql
-- ✅ 好：配置并行度
ALTER SYSTEM SET max_logical_replication_workers = 8;
SELECT pg_reload_conf();
-- 配置并行工作进程数

```

**错误**: SELECT语句缺少FROM子句

---

**行 949** (sql):

```sql
-- ✅ 好：配置并行度
ALTER SYSTEM SET max_logical_replication_workers = 8;
ALTER SYSTEM SET max_sync_workers_per_subscription = 4;
SELECT pg_reload_conf();
-- 根据实际负载调整

```

**错误**: SELECT语句缺少FROM子句

---

**行 1048** (sql):

```sql
-- ✅ 好：删除空闲复制槽
SELECT pg_drop_replication_slot('idle_slot_name');
-- 删除空闲复制槽，释放WAL空间

```

**错误**: SELECT语句缺少FROM子句

---

### 18-版本特性\18.01-PostgreSQL18新特性\多租户增强.md

**行 340** (sql):

```sql
-- 租户创建
-- 1. 创建租户表
CREATE TABLE tenants (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    subdomain VARCHAR(100) UNIQUE NOT NULL,
    status VARCHAR(20) DEFAULT 'active',
    created_a
```

**错误**: SELECT语句缺少FROM子句

---

**行 386** (sql):

```sql
-- 租户配置
-- 1. 配置租户资源限制
CREATE OR REPLACE FUNCTION configure_tenant(
    p_tenant_id INTEGER,
    p_max_connections INTEGER,
    p_work_mem VARCHAR,
    p_statement_timeout VARCHAR
)
RETURNS VOID AS $$
```

**错误**: SELECT语句缺少FROM子句

---

### 18-版本特性\18.01-PostgreSQL18新特性\存储格式优化.md

**行 168** (sql):

```sql
-- 创建压缩表
CREATE TABLE compressed_table (
    id SERIAL PRIMARY KEY,
    data TEXT,
    metadata JSONB
) WITH (
    compression = 'pglz'  -- 使用 pglz 压缩
);

-- 查看压缩效果
SELECT
    pg_size_pretty(pg_total_
```

**错误**: SELECT语句缺少FROM子句

---

**行 1072** (sql):

```sql
-- 对比PostgreSQL 17和18的存储空间
SELECT pg_size_pretty(pg_total_relation_size('table_name'));
-- PostgreSQL 18存储空间更小

```

**错误**: SELECT语句缺少FROM子句

---

### 18-版本特性\18.01-PostgreSQL18新特性\安全功能升级.md

**行 477** (sql):

```sql
-- PostgreSQL 18 审计功能增强
-- 1. 启用审计日志
-- postgresql.conf
log_statement = 'all'
log_connections = on
log_disconnections = on
log_duration = on
log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,cli
```

**错误**: SELECT语句缺少FROM子句

---

**行 1241** (sql):

```sql
-- ✅ 好：启用FIPS模式
ALTER SYSTEM SET fips_mode = on;
SELECT pg_reload_conf();
-- 启用FIPS 140-2合规模式

```

**错误**: SELECT语句缺少FROM子句

---

**行 1320** (sql):

```sql
-- ✅ 好：配置TLS v1.3
ALTER SYSTEM SET ssl = on;
ALTER SYSTEM SET ssl_min_protocol_version = 'TLSv1.3';
SELECT pg_reload_conf();
-- 启用TLS v1.3

```

**错误**: SELECT语句缺少FROM子句

---

### 18-版本特性\18.01-PostgreSQL18新特性\审计功能增强.md

**行 292** (sql):

```sql
-- PostgreSQL 18 审计日志性能优化
-- postgresql.conf

-- 1. 异步日志写入
audit_log_async = on  -- 异步写入，提升性能
audit_log_buffer_size = 64MB  -- 日志缓冲区大小

-- 2. 批量日志写入
audit_log_batch_size = 1000  -- 批量写入大小
audit_log_ba
```

**错误**: SELECT语句缺少FROM子句

---

**行 676** (sql):

```sql
-- PostgreSQL 18 审计性能调优
-- postgresql.conf

-- 1. 异步日志写入
audit_log_async = on
audit_log_buffer_size = 64MB

-- 2. 批量日志写入
audit_log_batch_size = 1000
audit_log_batch_timeout = 1s

-- 3. 日志过滤
audit_log_
```

**错误**: SELECT语句缺少FROM子句

---

**行 738** (sql):

```sql
-- 推荐：使用异步日志写入
audit_log_async = on

-- 推荐：使用批量日志写入
audit_log_batch_size = 1000

-- 推荐：过滤不必要的操作
audit_log_filter = 'exclude:SELECT'

-- 避免：同步日志写入
-- 避免：审计所有操作

```

**错误**: SELECT语句缺少FROM子句

---

**行 1424** (sql):

```sql
-- ✅ 好：配置审计策略
SELECT audit.enable('orders', 'INSERT,UPDATE,DELETE');
-- 审计orders表的INSERT、UPDATE、DELETE操作

```

**错误**: SELECT语句缺少FROM子句

---

**行 1457** (sql):

```sql
-- ✅ 好：配置细粒度审计
SELECT audit.enable('users', 'SELECT,INSERT,UPDATE,DELETE');
-- 审计用户表的所有操作

```

**错误**: SELECT语句缺少FROM子句

---

### 18-版本特性\18.01-PostgreSQL18新特性\并发性能提升.md

**行 227** (sql):

```sql
-- PostgreSQL 18 优化：事务提交性能提升
-- 1. 快速提交
BEGIN;
INSERT INTO orders (customer_id, amount) VALUES (1, 100);
COMMIT;  -- 提交时间减少 35%

-- 2. 批量提交优化
BEGIN;
INSERT INTO orders (customer_id, amount)
SELECT gen
```

**错误**: SELECT语句缺少FROM子句

---

**行 1189** (sql):

```sql
    -- ✅ 好：调整并发参数
    ALTER SYSTEM SET max_connections = 200;
    ALTER SYSTEM SET max_locks_per_transaction = 256;
    SELECT pg_reload_conf();
    -- 根据实际负载调整

```

**错误**: SELECT语句缺少FROM子句

---

### 18-版本特性\18.01-PostgreSQL18新特性\并行文本处理.md

**行 472** (sql):

```sql
-- ✅ 好：配置并行参数
ALTER SYSTEM SET max_parallel_workers_per_gather = 4;
ALTER SYSTEM SET max_parallel_workers = 8;
SELECT pg_reload_conf();
-- 启用并行文本处理

```

**错误**: SELECT语句缺少FROM子句

---

### 18-版本特性\18.01-PostgreSQL18新特性\并行查询增强.md

**行 1404** (sql):

```sql
-- ✅ 好：配置并行参数
ALTER SYSTEM SET max_parallel_workers_per_gather = 4;
ALTER SYSTEM SET max_parallel_workers = 8;
SELECT pg_reload_conf();
-- 启用并行查询

```

**错误**: SELECT语句缺少FROM子句

---

### 18-版本特性\18.01-PostgreSQL18新特性\异步I-O机制.md

**行 766** (sql):

```sql
-- ✅ 好：配置异步I/O参数
ALTER SYSTEM SET effective_io_concurrency = 200;
ALTER SYSTEM SET maintenance_io_concurrency = 10;
SELECT pg_reload_conf();
-- 启用异步I/O

```

**错误**: SELECT语句缺少FROM子句

---

### 18-版本特性\18.01-PostgreSQL18新特性\性能基准测试.md

**行 745** (sql):

```sql
-- ✅ 好：优化配置参数
ALTER SYSTEM SET shared_buffers = '4GB';
ALTER SYSTEM SET work_mem = '64MB';
ALTER SYSTEM SET effective_io_concurrency = 200;
SELECT pg_reload_conf();
-- 根据测试结果调整配置

```

**错误**: SELECT语句缺少FROM子句

---

### 18-版本特性\18.01-PostgreSQL18新特性\机器学习集成.md

**行 430** (sql):

```sql
-- 预测函数
-- 1. 分类预测
SELECT pg_ai_predict_class(
    'classification_model',
    ARRAY[1.0, 2.0, 3.0]::float[]
) AS predicted_class;

-- 2. 回归预测
SELECT pg_ai_predict_regression(
    'regression_model',

```

**错误**: SELECT语句缺少FROM子句

---

**行 609** (sql):

```sql
-- 外部模型导入
-- 1. 导入 Scikit-learn 模型
SELECT pg_ai_import_model(
    'sklearn_model',
    '/path/to/model.pkl',
    'sklearn'
);

-- 2. 导入 TensorFlow 模型
SELECT pg_ai_import_model(
    'tensorflow_model',
```

**错误**: SELECT语句缺少FROM子句

---

**行 1417** (sql):

```sql
-- ✅ 好：加载模型
SELECT ai.load_model('my_model', '/path/to/model.pkl');
-- 加载ML模型

```

**错误**: SELECT语句缺少FROM子句

---

**行 1448** (sql):

```sql
-- ✅ 好：存储模型
SELECT ai.store_model('my_model', model_data::bytea);
-- 在数据库中存储模型

```

**错误**: SELECT语句缺少FROM子句

---

**行 1456** (sql):

```sql
-- ✅ 好：版本控制
SELECT ai.store_model('my_model_v2', model_data::bytea);
-- 存储新版本模型

```

**错误**: SELECT语句缺少FROM子句

---

**行 1464** (sql):

```sql
-- ✅ 好：更新模型
SELECT ai.update_model('my_model', new_model_data::bytea);
-- 更新现有模型

```

**错误**: SELECT语句缺少FROM子句

---

### 18-版本特性\18.01-PostgreSQL18新特性\查询语言增强.md

**行 596** (sql):

```sql
-- 新操作符（PostgreSQL 18）
-- 1. JSON 操作符
SELECT
    '{"key": "value"}'::JSONB -> 'key' AS json_value,
    '{"key": "value"}'::JSONB ->> 'key' AS json_text;

-- 2. 数组操作符
SELECT
    ARRAY[1, 2, 3] || ARRAY
```

**错误**: SELECT语句缺少FROM子句

---

### 18-版本特性\18.01-PostgreSQL18新特性\监控体系升级.md

**行 605** (sql):

```sql
-- 统计信息配置
-- 1. 启用扩展统计
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- 2. 重置统计信息
SELECT pg_stat_reset();
SELECT pg_stat_statements_reset();

-- 3. 查看统计信息配置
SHOW track_activities;
SHOW track_cou
```

**错误**: SELECT语句缺少FROM子句

---

### 18-版本特性\18.01-PostgreSQL18新特性\迁移指南_17到18.md

**行 225** (sql):

```sql
-- 1. 异步 I/O（新特性，自动启用）
-- 迁移后自动生效，无需手动配置
-- I/O 密集型查询性能提升 3 倍

-- 2. 生成列（新特性）
-- 迁移前：需要触发器维护计算列
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    price DECIMAL(10,2),
    quantity INTEGER,
    to
```

**错误**: SELECT语句缺少FROM子句

---

**行 805** (sql):

```sql
-- 1. 内存配置优化（根据服务器内存调整）
-- postgresql.conf

-- 共享内存（25% RAM）
shared_buffers = 4GB

-- 工作内存（每个查询操作）
work_mem = 64MB

-- 维护工作内存（维护操作）
maintenance_work_mem = 1GB

-- 有效缓存大小（50-75% RAM）
effective_cache_si
```

**错误**: SELECT语句缺少FROM子句

---

**行 1278** (sql):

```sql
-- ✅ 好：利用PostgreSQL 18新特性
-- 例如：调整并行查询参数
ALTER SYSTEM SET max_parallel_workers_per_gather = 4;
ALTER SYSTEM SET max_parallel_workers = 8;
SELECT pg_reload_conf();

```

**错误**: SELECT语句缺少FROM子句

---

### 18-版本特性\18.01-PostgreSQL18新特性\高可用方案升级.md

**行 227** (sql):

```sql
-- 配置多主复制
ALTER SYSTEM SET max_connections = 200;
ALTER SYSTEM SET max_prepared_transactions = 200;
ALTER SYSTEM SET max_wal_senders = 10;

-- 创建逻辑复制槽
SELECT pg_create_logical_replication_slot(
    'm
```

**错误**: SELECT语句缺少FROM子句

---

**行 604** (sql):

```sql
-- ✅ 好：配置故障检测
ALTER SYSTEM SET wal_receiver_timeout = '30s';
ALTER SYSTEM SET wal_receiver_status_interval = '10s';
SELECT pg_reload_conf();
-- 配置故障检测参数

```

**错误**: SELECT语句缺少FROM子句

---

### 18-版本特性\18.02-PostgreSQL17新特性\MVCC优化.md

**行 1149** (sql):

```sql
    -- ✅ 好：调整VACUUM参数
    ALTER SYSTEM SET autovacuum_vacuum_scale_factor = 0.1;
    ALTER SYSTEM SET autovacuum_vacuum_cost_delay = 10;
    SELECT pg_reload_conf();
    -- 更频繁但更快的VACUUM

```

**错误**: SELECT语句缺少FROM子句

---

**行 1159** (sql):

```sql
    -- ✅ 好：调整VACUUM工作负载
    ALTER SYSTEM SET vacuum_cost_limit = 2000;
    SELECT pg_reload_conf();
    -- VACUUM更快完成

```

**错误**: SELECT语句缺少FROM子句

---

**行 1368** (sql):

```sql
    -- ✅ 好：调整VACUUM参数
    ALTER SYSTEM SET autovacuum_vacuum_scale_factor = 0.1;
    ALTER SYSTEM SET autovacuum_vacuum_cost_delay = 10;
    SELECT pg_reload_conf();
    -- 更频繁的VACUUM，保持版本链短

```

**错误**: SELECT语句缺少FROM子句

---

### 18-版本特性\18.02-PostgreSQL17新特性\SQL标准兼容性增强.md

**行 468** (sql):

```sql
-- 标准数据类型
CREATE TABLE standard_types (
    id INTEGER,
    name VARCHAR(100),
    price DECIMAL(10,2),
    created_at TIMESTAMP,
    is_active BOOLEAN
);

-- 标准类型转换
SELECT CAST('123' AS INTEGER) AS i
```

**错误**: SELECT语句缺少FROM子句

---

**行 485** (sql):

```sql
-- SQL/JSON 标准函数
SELECT
    JSON_VALUE('{"name": "PostgreSQL"}', '$.name') AS name,
    JSON_QUERY('{"data": [1,2,3]}', '$.data') AS data,
    JSON_EXISTS('{"key": "value"}', '$.key') AS exists;

```

**错误**: SELECT语句缺少FROM子句

---

### 18-版本特性\18.02-PostgreSQL17新特性\分区管理增强.md

**行 608** (sql):

```sql
-- 使用 pg_partman 自动创建分区
-- 安装 pg_partman
CREATE EXTENSION IF NOT EXISTS pg_partman;

-- 配置自动分区
SELECT partman.create_parent(
    p_parent_table => 'public.orders',
    p_control => 'order_date',
    p
```

**错误**: SELECT语句缺少FROM子句

---

**行 628** (sql):

```sql
-- 配置自动删除旧分区
SELECT partman.set_config(
    p_parent_table => 'public.orders',
    p_retention => '12 months',
    p_retention_keep_table => false
);

-- 执行维护任务（删除超过 12 个月的分区）
SELECT partman.run_maint
```

**错误**: SELECT语句缺少FROM子句

---

**行 642** (sql):

```sql
-- 配置分区策略
SELECT partman.set_config(
    p_parent_table => 'public.orders',
    p_control => 'order_date',
    p_type => 'range',
    p_interval => 'monthly',
    p_premake => 3,
    p_retention => '1
```

**错误**: SELECT语句缺少FROM子句

---

**行 748** (sql):

```sql
   -- ✅ 好：使用自动化分区管理（可维护性）
   SELECT partman.create_parent(
       p_parent_table => 'public.orders',
       p_control => 'order_date',
       p_type => 'range',
       p_interval => 'monthly',

```

**错误**: SELECT语句缺少FROM子句

---

**行 910** (sql):

```sql
-- 1. 创建分区表
CREATE TABLE orders (
    id SERIAL,
    order_date DATE NOT NULL,
    customer_id INT,
    amount DECIMAL(10,2)
) PARTITION BY RANGE (order_date);

-- 2. 配置自动分区
SELECT partman.create_pare
```

**错误**: SELECT语句缺少FROM子句

---

**行 1141** (sql):

```sql
    -- ✅ 好：使用pg_partman扩展
    CREATE EXTENSION pg_partman;

    -- 配置自动分区
    SELECT partman.create_parent(
        p_parent_table => 'public.orders',
        p_control => 'order_date',
        p_type
```

**错误**: SELECT语句缺少FROM子句

---

### 18-版本特性\18.02-PostgreSQL17新特性\备份恢复改进.md

**行 508** (sql):

```sql
-- 配置 WAL 归档
ALTER SYSTEM SET wal_level = 'replica';
ALTER SYSTEM SET archive_mode = 'on';
ALTER SYSTEM SET archive_command = 'cp %p /archive/%f';

-- 重新加载配置
SELECT pg_reload_conf();

```

**错误**: SELECT语句缺少FROM子句

---

**行 564** (sql):

```sql
-- 恢复前配置
ALTER SYSTEM SET max_parallel_workers_per_gather = 8;
ALTER SYSTEM SET maintenance_work_mem = '2GB';

-- 重新加载
SELECT pg_reload_conf();

```

**错误**: SELECT语句缺少FROM子句

---

**行 807** (sql):

```sql
   -- ✅ 好：配置 WAL 归档（可维护性）
   ALTER SYSTEM SET wal_level = 'replica';
   ALTER SYSTEM SET archive_mode = 'on';
   ALTER SYSTEM SET archive_command = 'cp %p /archive/%f';
   SELECT pg_reload_conf();


```

**错误**: SELECT语句缺少FROM子句

---

### 18-版本特性\18.02-PostgreSQL17新特性\安全性增强.md

**行 467** (sql):

```sql
-- 创建角色
CREATE ROLE app_user WITH LOGIN PASSWORD 'secure_password';

-- 授予权限
GRANT SELECT, INSERT, UPDATE ON table_name TO app_user;

-- 行级安全策略
ALTER TABLE table_name ENABLE ROW LEVEL SECURITY;

CREAT
```

**错误**: SELECT语句缺少FROM子句

---

**行 487** (sql):

```sql
-- 创建角色层次
CREATE ROLE manager;
CREATE ROLE employee;
GRANT manager TO employee;

-- 权限继承
GRANT SELECT ON ALL TABLES IN SCHEMA public TO manager;

```

**错误**: SELECT语句缺少FROM子句

---

**行 551** (sql):

```sql
-- 启用审计日志
ALTER SYSTEM SET log_statement = 'all';
ALTER SYSTEM SET log_connections = 'on';
ALTER SYSTEM SET log_disconnections = 'on';

-- 重新加载配置
SELECT pg_reload_conf();

```

**错误**: SELECT语句缺少FROM子句

---

**行 694** (sql):

```sql
   -- ✅ 好：启用审计日志（可维护性）
   ALTER SYSTEM SET log_statement = 'all';
   ALTER SYSTEM SET log_connections = 'on';
   ALTER SYSTEM SET log_disconnections = 'on';
   ALTER SYSTEM SET log_duration = 'on';

```

**错误**: SELECT语句缺少FROM子句

---

**行 879** (sql):

```sql
-- ✅ 好：配置SSL连接
ALTER SYSTEM SET ssl = on;
ALTER SYSTEM SET ssl_cert_file = '/path/to/server.crt';
ALTER SYSTEM SET ssl_key_file = '/path/to/server.key';
SELECT pg_reload_conf();
-- 启用SSL加密连接

```

**错误**: SELECT语句缺少FROM子句

---

**行 890** (sql):

```sql
-- ✅ 好：配置密码加密
ALTER SYSTEM SET password_encryption = 'scram-sha-256';
SELECT pg_reload_conf();
-- 使用强密码加密

```

**错误**: SELECT语句缺少FROM子句

---

**行 972** (sql):

```sql
-- ✅ 好：授予权限
GRANT SELECT, INSERT, UPDATE ON orders TO app_user;
GRANT ALL ON orders TO app_admin;
-- 根据角色授予不同权限

```

**错误**: SELECT语句缺少FROM子句

---

**行 1006** (sql):

```sql
-- ✅ 好：启用日志记录
ALTER SYSTEM SET log_statement = 'all';
ALTER SYSTEM SET log_connections = on;
ALTER SYSTEM SET log_disconnections = on;
SELECT pg_reload_conf();
-- 记录所有SQL语句和连接

```

**错误**: SELECT语句缺少FROM子句

---

**行 1017** (sql):

```sql
-- ✅ 好：配置日志格式
ALTER SYSTEM SET log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h ';
SELECT pg_reload_conf();
-- 记录详细信息

```

**错误**: SELECT语句缺少FROM子句

---

**行 1077** (sql):

```sql
-- ✅ 好：配置SSL传输加密
ALTER SYSTEM SET ssl = on;
SELECT pg_reload_conf();
-- 启用SSL加密传输

```

**错误**: SELECT语句缺少FROM子句

---

### 18-版本特性\18.02-PostgreSQL17新特性\性能诊断改进.md

**行 1507** (sql):

```sql
-- ✅ 好：重置 pg_stat_statements
SELECT pg_stat_statements_reset();
-- 重置所有查询统计信息

-- ✅ 好：重置特定数据库统计
SELECT pg_stat_reset();
-- 重置当前数据库的统计信息

-- ✅ 好：重置特定表统计
SELECT pg_stat_reset_single_table_counters('tabl
```

**错误**: SELECT语句缺少FROM子句

---

### 18-版本特性\18.02-PostgreSQL17新特性\执行计划优化.md

**行 523** (sql):

```sql
-- 配置计划缓存
ALTER SYSTEM SET plan_cache_mode = 'force_custom_plan';
ALTER SYSTEM SET plan_cache_size = '100MB';

-- 重新加载配置
SELECT pg_reload_conf();

```

**错误**: SELECT语句缺少FROM子句

---

### 18-版本特性\18.02-PostgreSQL17新特性\查询优化器增强.md

**行 748** (sql):

```sql
-- 使用并行提示（如果支持）
-- 注意：PostgreSQL 原生不支持查询提示，但可以通过配置强制并行

-- 临时调整参数强制并行
SET max_parallel_workers_per_gather = 8;
SET parallel_setup_cost = 0;
SET parallel_tuple_cost = 0;

-- 执行查询
SELECT ...;

-- 恢复参数
R
```

**错误**: SELECT语句缺少FROM子句

---

### 18-版本特性\18.02-PostgreSQL17新特性\迁移指南_16到17.md

**行 1048** (sql):

```sql
    -- ✅ 好：利用PostgreSQL 17新特性
    -- 例如：调整并行查询参数
    ALTER SYSTEM SET max_parallel_workers_per_gather = 4;
    ALTER SYSTEM SET max_parallel_workers = 8;
    SELECT pg_reload_conf();

```

**错误**: SELECT语句缺少FROM子句

---

**行 1139** (sql):

```sql
    -- ✅ 好：检查版本
    SELECT version();
    -- 应该显示PostgreSQL 17.x

    -- 检查服务器版本
    SHOW server_version;

```

**错误**: SELECT语句缺少FROM子句

---

### 18-版本特性\18.03-PostgreSQL-18.1-更新说明.md

**行 194** (sql):

```sql
-- 修复前（会报错）
SELECT JSON_VALUE(
    '{"name": "test"}'::jsonb,
    '$.name'
    RETURNING TEXT
    DEFAULT 'default' COLLATE "C"
);

-- 修复后（正常工作）
SELECT JSON_VALUE(
    '{"name": "test"}'::jsonb,
    '
```

**错误**: SELECT语句缺少FROM子句

---

### 19-实战案例\02-OLAP分析系统\04-查询优化.md

**行 349** (sql):

```sql
-- 查询计划分析函数
CREATE OR REPLACE FUNCTION analyze_query_plan(
    p_query_text TEXT
)
RETURNS TABLE (
    plan_node TEXT,
    node_type TEXT,
    cost_start NUMERIC,
    cost_end NUMERIC,
    actual_time
```

**错误**: SELECT语句缺少FROM子句

---

**行 507** (sql):

```sql
-- PostgreSQL 18异步I/O配置
ALTER SYSTEM SET io_direct = 'data';
ALTER SYSTEM SET io_combine_limit = '512kB';

-- 重启后生效
SELECT pg_reload_conf();

-- 性能提升:
-- 大表扫描: +25-30%
-- 数据加载: +30-35%
-- 索引构建: +40-45
```

**错误**: SELECT语句缺少FROM子句

---

### 19-实战案例\02-OLAP分析系统\06-部署运维.md

**行 314** (sql):

```sql
-- 诊断: 检查并行配置
SHOW max_parallel_workers_per_gather;
SHOW max_parallel_workers;

-- 解决: 调整并行参数
ALTER SYSTEM SET max_parallel_workers_per_gather = 4;
ALTER SYSTEM SET max_parallel_workers = 8;
SELECT pg
```

**错误**: SELECT语句缺少FROM子句

---

### 19-实战案例\03-IoT时序数据系统\03-数据库设计.md

**行 34** (sql):

```sql
-- 设备表
CREATE TABLE devices (
    device_id SERIAL PRIMARY KEY,
    device_code VARCHAR(50) UNIQUE,
    device_name VARCHAR(200),
    device_type VARCHAR(50),
    location VARCHAR(200),
    install_da
```

**错误**: SELECT语句缺少FROM子句

---

### 19-实战案例\03-IoT时序数据系统\04-核心实现.md

**行 424** (python):

```python
from flask import Flask, request, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)

DB_CONFIG = {
    'dbname': 'iot_db',
    'user': 'postgres',
    'password
```

**错误**: 语法错误: expected 'except' or 'finally' block (行 55)

---

### 19-实战案例\03-IoT时序数据系统\05-测试验证.md

**行 124** (sql):

```sql
-- 测试压缩比
SELECT
    pg_size_pretty(pg_total_relation_size('sensor_data')) as total_size,
    pg_size_pretty(pg_relation_size('sensor_data')) as table_size,
    pg_size_pretty(pg_total_relation_size('s
```

**错误**: SELECT语句缺少FROM子句

---

### 19-实战案例\04-多租户SaaS系统\02-架构设计.md

**行 178** (sql):

```sql
-- 创建租户函数
CREATE OR REPLACE FUNCTION create_tenant(
    p_tenant_name TEXT,
    p_plan_type TEXT DEFAULT 'basic',
    p_admin_email TEXT,
    p_admin_password TEXT
)
RETURNS TABLE (
    tenant_id INT,
```

**错误**: SELECT语句缺少FROM子句

---

**行 262** (sql):

```sql
-- 租户数据迁移函数（用于升级套餐等场景）
CREATE OR REPLACE FUNCTION migrate_tenant_data(
    p_source_tenant_id INT,
    p_target_tenant_id INT,
    p_tables TEXT[] DEFAULT ARRAY['users', 'documents']
)
RETURNS TABLE (
```

**错误**: SELECT语句缺少FROM子句

---

### 19-实战案例\04-多租户SaaS系统\03-数据库设计.md

**行 819** (sql):

```sql
-- 租户数据备份函数
CREATE OR REPLACE FUNCTION backup_tenant_data(
    p_tenant_id INT,
    p_backup_path TEXT
)
RETURNS TABLE (
    backup_file TEXT,
    backup_size TEXT,
    backup_time TIMESTAMPTZ
) AS $$
```

**错误**: SELECT语句缺少FROM子句

---

### 19-实战案例\04-多租户SaaS系统\03-核心实现.md

**行 306** (python):

```python
class QuotaChecker:
    """配额检查器"""

    def __init__(self, conn, tenant_id):
        self.conn = conn
        self.cursor = conn.cursor()
        self.tenant_id = tenant_id

    def check_storage_quo
```

**错误**: 语法错误: expected 'except' or 'finally' block (行 24)

---

### 19-实战案例\04-多租户SaaS系统\06-生产部署.md

**行 275** (sql):

```sql
-- init-tenant.sql
-- 为新租户初始化schema和数据

CREATE OR REPLACE FUNCTION init_tenant(tenant_name TEXT)
RETURNS VOID AS $$
DECLARE
    tenant_schema TEXT;
BEGIN
    tenant_schema := 'tenant_' || tenant_name;
```

**错误**: SELECT语句缺少FROM子句

---

### 19-实战案例\05-金融交易系统\03-数据库设计.md

**行 387** (sql):

```sql
-- 事件存储函数（带完整错误处理）
CREATE OR REPLACE FUNCTION store_account_event(
    p_account_id BIGINT,
    p_event_type TEXT,
    p_event_data JSONB
)
RETURNS BIGINT AS $$
DECLARE
    v_sequence_number BIGINT;

```

**错误**: 单引号不匹配

---

### 19-实战案例\06-全文搜索系统\02-架构设计.md

**行 353** (sql):

```sql
-- 索引优化建议函数
CREATE OR REPLACE FUNCTION suggest_index_optimization()
RETURNS TABLE (
    table_name TEXT,
    current_indexes TEXT[],
    suggested_indexes TEXT[],
    optimization_reason TEXT
) AS $$

```

**错误**: SELECT语句缺少FROM子句

---

### 19-实战案例\06-全文搜索系统\07-生产优化.md

**行 35** (sql):

```sql
-- PostgreSQL 18: GIN索引优化
ALTER INDEX idx_docs_gin SET (fastupdate = on);
ALTER INDEX idx_docs_gin SET (gin_pending_list_limit = 4096);  -- 4MB

-- 效果：
-- 批量插入性能提升30%
-- 后台合并pending entries

-- 手动合并
S
```

**错误**: SELECT语句缺少FROM子句

---

### 19-实战案例\06.02-RAG知识库完整项目.md

**行 320** (sql):

```sql
-- ✅ [可运行] 完整的RAG知识库数据模型

-- 启用扩展
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================
-- 用户和权限管理
```

**错误**: 单引号不匹配

---

### 19-实战案例\08-知识图谱问答系统\03-数据库设计.md

**行 209** (sql):

```sql
-- 实体向量化函数（使用pg_ai）
CREATE OR REPLACE FUNCTION generate_entity_embedding(
    p_entity_name TEXT,
    p_entity_description TEXT DEFAULT NULL
)
RETURNS vector(768) AS $$
DECLARE
    v_text TEXT;
    v_
```

**错误**: SELECT语句缺少FROM子句

---

**行 321** (sql):

```sql
-- NL2Cypher函数（使用pg_ai）
CREATE OR REPLACE FUNCTION nl2cypher(
    p_question TEXT,
    p_schema_info JSONB DEFAULT NULL
)
RETURNS TEXT AS $$
DECLARE
    v_schema TEXT;
    v_prompt TEXT;
    v_cypher
```

**错误**: 括号不匹配; 单引号不匹配

---

### 19-实战案例\08-知识图谱问答系统\04-核心实现.md

**行 11** (python):

```python
"""
知识图谱问答系统
技术栈: PostgreSQL 18 + Apache AGE + LangChain
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate

```

**错误**: 语法错误: expected 'except' or 'finally' block (行 306)

---

### 19-实战案例\09-智能客服系统\01-需求分析.md

**行 246** (sql):

```sql
-- 意图表（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'intents') THEN
            CREATE TABLE intents (

```

**错误**: 单引号不匹配

---

**行 303** (sql):

```sql
-- 情感分析（使用pg_ai，带错误处理）
DO $$
DECLARE
    v_user_message TEXT := '示例消息';  -- 实际使用时从参数传入
    v_sentiment_score DECIMAL(3, 2);
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_extension WHERE extn
```

**错误**: 单引号不匹配

---

**行 401** (sql):

```sql
-- 语义检索（带错误处理和性能测试）
DO $$
DECLARE
    v_query_text TEXT := $1;  -- 实际使用时从参数传入
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_nam
```

**错误**: 单引号不匹配

---

**行 545** (sql):

```sql
-- RAG检索函数（带完整错误处理）
CREATE OR REPLACE FUNCTION rag_retrieve(
    p_query TEXT,
    p_limit INT DEFAULT 5
)
RETURNS TABLE(content TEXT, similarity FLOAT) AS $$
DECLARE
    v_query_vec vector(768);
BEGI
```

**错误**: 单引号不匹配

---

### 19-实战案例\09-智能客服系统\02-架构设计.md

**行 254** (sql):

```sql
-- 意图分类表（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'intent_categories') THEN
            CREATE TABLE i
```

**错误**: 单引号不匹配

---

**行 355** (sql):

```sql
-- 工单表
CREATE TABLE IF NOT EXISTS support_tickets (
    ticket_id SERIAL PRIMARY KEY,
    session_id INT REFERENCES conversation_sessions(session_id),
    user_id INT NOT NULL,
    subject TEXT NOT NU
```

**错误**: SELECT语句缺少FROM子句

---

### 19-实战案例\09-智能客服系统\03-数据库设计.md

**行 675** (sql):

```sql
-- PostgreSQL 18异步I/O配置
ALTER SYSTEM SET io_direct = 'data';
ALTER SYSTEM SET io_combine_limit = '128kB';

-- 重启后生效
SELECT pg_reload_conf();

```

**错误**: SELECT语句缺少FROM子句

---

**行 688** (sql):

```sql
-- PostgreSQL 18内置连接池配置
ALTER SYSTEM SET pool_mode = 'transaction';
ALTER SYSTEM SET pool_size = 100;
ALTER SYSTEM SET pool_max_wait = 5;

-- 重启后生效
SELECT pg_reload_conf();

```

**错误**: SELECT语句缺少FROM子句

---

**行 772** (sql):

```sql
-- 清理过期会话
CREATE OR REPLACE FUNCTION cleanup_expired_sessions(
    p_timeout_hours INT DEFAULT 24
)
RETURNS TABLE (
    closed_count INT
) AS $$
DECLARE
    v_closed INT := 0;
BEGIN
    -- 关闭超时会话

```

**错误**: SELECT语句缺少FROM子句

---

### 19-实战案例\09-智能客服系统\03-核心实现.md

**行 766** (sql):

```sql
-- 向量检索优化函数（带完整错误处理）
CREATE OR REPLACE FUNCTION optimize_faq_retrieval(
    p_query_text TEXT,
    p_top_k INT DEFAULT 5,
    p_threshold FLOAT DEFAULT 0.7
)
RETURNS TABLE (
    faq_id INT,
    questi
```

**错误**: 单引号不匹配

---

### 19-实战案例\10-金融反欺诈系统\04-核心实现.md

**行 61** (sql):

```sql
-- 欺诈检测主函数（带完整错误处理）
CREATE OR REPLACE FUNCTION detect_fraud(
    p_user_id BIGINT,
    p_amount NUMERIC,
    p_merchant_id BIGINT,
    p_device_id VARCHAR(100),
    p_ip_address INET
) RETURNS TABLE (
```

**错误**: 单引号不匹配

---

**行 372** (sql):

```sql
-- 特征提取函数（带完整错误处理）
CREATE OR REPLACE FUNCTION extract_features(
    p_user_id BIGINT,
    p_device_id VARCHAR(100)
) RETURNS JSONB AS $$
DECLARE
    v_features JSONB;
    v_user_features JSONB;
    v_
```

**错误**: 单引号不匹配

---

**行 488** (sql):

```sql
-- 设备特征提取（带完整错误处理）
CREATE OR REPLACE FUNCTION extract_device_features(
    p_device_id VARCHAR(100)
) RETURNS JSONB AS $$
DECLARE
    v_features JSONB;
BEGIN
    BEGIN
        IF p_device_id IS NULL O
```

**错误**: 单引号不匹配

---

**行 614** (sql):

```sql
-- 决策融合函数（带完整错误处理）
CREATE OR REPLACE FUNCTION fuse_decision(
    p_rule_score NUMERIC,
    p_ml_score NUMERIC DEFAULT NULL,
    p_rule_weight NUMERIC DEFAULT 0.6,
    p_ml_weight NUMERIC DEFAULT 0.4
)
```

**错误**: SELECT语句缺少FROM子句

---

**行 714** (sql):

```sql
-- 更新规则命中统计（带完整错误处理）
CREATE OR REPLACE FUNCTION update_rule_statistics(
    p_rule_id VARCHAR(50)
) RETURNS VOID AS $$
BEGIN
    BEGIN
        IF p_rule_id IS NULL OR p_rule_id = '' THEN
            R
```

**错误**: 单引号不匹配

---

**行 750** (sql):

```sql
-- 创建/更新规则（带完整错误处理）
CREATE OR REPLACE FUNCTION upsert_fraud_rule(
    p_rule_id VARCHAR(50),
    p_rule_name VARCHAR(200),
    p_conditions JSONB,
    p_actions JSONB,
    p_priority INTEGER DEFAULT 0
```

**错误**: 单引号不匹配

---

**行 851** (sql):

```sql
-- 记录审计日志（带完整错误处理）
CREATE OR REPLACE FUNCTION log_audit(
    p_transaction_id BIGINT,
    p_result_id BIGINT,
    p_action_type VARCHAR(50),
    p_action_details JSONB DEFAULT '{}'::jsonb,
    p_user_
```

**错误**: 单引号不匹配

---

### 19-实战案例\10-金融反欺诈系统\06-部署运维.md

**行 1084** (sql):

```sql
-- 启用异步I/O
ALTER SYSTEM SET io_direct = 'data,wal';
ALTER SYSTEM SET effective_io_concurrency = 200;
ALTER SYSTEM SET wal_io_concurrency = 200;

-- 重新加载配置
SELECT pg_reload_conf();

```

**错误**: SELECT语句缺少FROM子句

---

### 19-实战案例\交通场景\智能交通管理系统.md

**行 258** (sql):

```sql
-- 创建交通流量时序表
CREATE TABLE traffic_flow (
    time TIMESTAMPTZ NOT NULL,
    sensor_id TEXT NOT NULL,
    road_segment_id TEXT NOT NULL,
    vehicle_count INTEGER,
    average_speed DECIMAL(10, 2),

```

**错误**: SELECT语句缺少FROM子句

---

**行 531** (sql):

```sql
-- 启用TimescaleDB扩展
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- 创建交通流量时序表
CREATE TABLE traffic_flow (
    time TIMESTAMPTZ NOT NULL,
    sensor_id INTEGER NOT NULL,
    vehicle_count INTEGER,
    a
```

**错误**: SELECT语句缺少FROM子句

---

### 19-实战案例\仓储场景\智能仓储管理系统.md

**行 203** (sql):

```sql
-- 创建库存时序表
CREATE TABLE inventory_history (
    time TIMESTAMPTZ NOT NULL,
    product_id INTEGER NOT NULL,
    warehouse_id INTEGER NOT NULL,
    quantity INTEGER,
    location POINT,
    operation_t
```

**错误**: SELECT语句缺少FROM子句

---

**行 399** (sql):

```sql
-- 启用TimescaleDB和PostGIS扩展
CREATE EXTENSION IF NOT EXISTS timescaledb;
CREATE EXTENSION IF NOT EXISTS postgis;

-- 创建库存数据时序表
CREATE TABLE inventory_data (
    time TIMESTAMPTZ NOT NULL,
    warehouse_
```

**错误**: SELECT语句缺少FROM子句

---

### 19-实战案例\体育场景\运动数据分析系统.md

**行 194** (sql):

```sql
-- 创建运动数据时序表
CREATE TABLE athlete_data (
    time TIMESTAMPTZ NOT NULL,
    athlete_id TEXT NOT NULL,
    sport_type TEXT,
    heart_rate INTEGER,
    speed DECIMAL(10, 2),
    distance DECIMAL(10, 2)
```

**错误**: SELECT语句缺少FROM子句

---

**行 381** (sql):

```sql
-- 启用TimescaleDB和PostGIS扩展
CREATE EXTENSION IF NOT EXISTS timescaledb;
CREATE EXTENSION IF NOT EXISTS postgis;

-- 创建运动数据时序表
CREATE TABLE athlete_data (
    time TIMESTAMPTZ NOT NULL,
    athlete_id T
```

**错误**: SELECT语句缺少FROM子句

---

### 19-实战案例\供应链场景\智能供应链管理系统.md

**行 202** (sql):

```sql
-- 创建订单时序表
CREATE TABLE purchase_orders (
    time TIMESTAMPTZ NOT NULL,
    order_id INTEGER NOT NULL,
    supplier_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER,
    uni
```

**错误**: SELECT语句缺少FROM子句

---

**行 434** (sql):

```sql
-- 安装扩展
CREATE EXTENSION IF NOT EXISTS timescaledb;
CREATE EXTENSION IF NOT EXISTS postgis;

-- 创建供应商表
CREATE TABLE suppliers (
    supplier_id SERIAL PRIMARY KEY,
    supplier_name TEXT NOT NULL,

```

**错误**: SELECT语句缺少FROM子句

---

### 19-实战案例\保险场景\智能理赔系统.md

**行 399** (sql):

```sql
-- 启用pgvector和Apache AGE扩展
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS age;
LOAD 'age';
SET search_path = ag_catalog, "$user", public;

-- 创建理赔申请表
CREATE TABLE claims (
    i
```

**错误**: SELECT语句缺少FROM子句

---

### 19-实战案例\健身场景\智能健身管理系统.md

**行 203** (sql):

```sql
-- 创建运动数据时序表
CREATE TABLE workout_data (
    time TIMESTAMPTZ NOT NULL,
    user_id INTEGER NOT NULL,
    workout_type TEXT,
    heart_rate INTEGER,
    calories_burned DECIMAL(10, 2),
    distance DE
```

**错误**: SELECT语句缺少FROM子句

---

**行 410** (sql):

```sql
-- 启用TimescaleDB和pgvector扩展
CREATE EXTENSION IF NOT EXISTS timescaledb;
CREATE EXTENSION IF NOT EXISTS vector;

-- 创建运动数据时序表
CREATE TABLE workout_data (
    time TIMESTAMPTZ NOT NULL,
    user_id INTE
```

**错误**: SELECT语句缺少FROM子句

---

### 19-实战案例\农业场景\智慧农业监控系统.md

**行 215** (sql):

```sql
-- 创建环境数据时序表
CREATE TABLE environment_metrics (
    time TIMESTAMPTZ NOT NULL,
    sensor_id TEXT NOT NULL,
    field_id TEXT NOT NULL,
    temperature DECIMAL(10, 2),
    humidity DECIMAL(10, 2),

```

**错误**: SELECT语句缺少FROM子句

---

**行 257** (sql):

```sql
CREATE TABLE crop_growth (
    time TIMESTAMPTZ NOT NULL,
    field_id TEXT NOT NULL,
    crop_type TEXT,
    growth_stage TEXT,
    height DECIMAL(10, 2),
    leaf_area_index DECIMAL(10, 2),
    yiel
```

**错误**: SELECT语句缺少FROM子句

---

**行 726** (sql):

```sql
-- 启用TimescaleDB和PostGIS扩展
CREATE EXTENSION IF NOT EXISTS timescaledb;
CREATE EXTENSION IF NOT EXISTS postgis;

-- 创建环境数据时序表
CREATE TABLE environment_metrics (
    time TIMESTAMPTZ NOT NULL,
    senso
```

**错误**: SELECT语句缺少FROM子句

---

### 19-实战案例\制造场景\IoT时序数据分析.md

**行 221** (sql):

```sql
-- 启用 TimescaleDB
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- 创建设备时序数据表
CREATE TABLE device_metrics (
    time TIMESTAMPTZ NOT NULL,
    device_id TEXT NOT NULL,
    metric_name TEXT NOT NULL,

```

**错误**: SELECT语句缺少FROM子句

---

**行 527** (sql):

```sql
-- 优化前：普通表
CREATE TABLE device_metrics (
    time TIMESTAMPTZ NOT NULL,
    device_id TEXT NOT NULL,
    value DOUBLE PRECISION
);

-- 优化后：TimescaleDB 超表
CREATE TABLE device_metrics (
    time TIMESTA
```

**错误**: SELECT语句缺少FROM子句

---

**行 986** (sql):

```sql
-- 启用TimescaleDB和pgvector扩展
CREATE EXTENSION IF NOT EXISTS timescaledb;
CREATE EXTENSION IF NOT EXISTS vector;

-- 创建设备指标时序表
CREATE TABLE device_metrics (
    time TIMESTAMPTZ NOT NULL,
    device_id
```

**错误**: SELECT语句缺少FROM子句

---

### 19-实战案例\制造场景\故障预测准确率优化.md

**行 216** (sql):

```sql
-- 数据质量检查
-- 检查数据质量函数（带完整错误处理）
CREATE OR REPLACE FUNCTION check_data_quality(p_device_id TEXT)
RETURNS TABLE (
    metric_name TEXT,
    completeness NUMERIC,
    consistency NUMERIC,
    accuracy NUM
```

**错误**: 单引号不匹配

---

**行 306** (sql):

```sql
-- 使用 pg_ai 自动调优预测模型
SELECT pg_ai.optimize_prediction_model(
    model_type => 'fault_prediction',
    training_data => 'device_metrics',
    target_column => 'fault_occurred',
    optimization_metric
```

**错误**: SELECT语句缺少FROM子句

---

**行 406** (sql):

```sql
-- 启用TimescaleDB和pgvector扩展
CREATE EXTENSION IF NOT EXISTS timescaledb;
CREATE EXTENSION IF NOT EXISTS vector;

-- 创建设备指标时序表
CREATE TABLE device_metrics (
    time TIMESTAMPTZ NOT NULL,
    device_id
```

**错误**: SELECT语句缺少FROM子句

---

### 19-实战案例\制造场景\设备预测维护系统.md

**行 518** (sql):

```sql
-- 创建设备指标表
CREATE TABLE device_metrics (
    time TIMESTAMPTZ NOT NULL,
    device_id TEXT NOT NULL,

    -- 传感器数据
    temperature NUMERIC,
    vibration NUMERIC,
    pressure NUMERIC,
    current NUM
```

**错误**: SELECT语句缺少FROM子句

---

### 19-实战案例\化工场景\生产安全监控系统.md

**行 200** (sql):

```sql
-- 创建设备数据时序表
CREATE TABLE equipment_data (
    time TIMESTAMPTZ NOT NULL,
    equipment_id TEXT NOT NULL,
    temperature DECIMAL(10, 2),
    pressure DECIMAL(10, 2),
    flow_rate DECIMAL(10, 2),

```

**错误**: SELECT语句缺少FROM子句

---

**行 404** (sql):

```sql
-- 启用TimescaleDB和PostGIS扩展
CREATE EXTENSION IF NOT EXISTS timescaledb;
CREATE EXTENSION IF NOT EXISTS postgis;

-- 创建设备数据时序表
CREATE TABLE equipment_data (
    time TIMESTAMPTZ NOT NULL,
    equipment_
```

**错误**: SELECT语句缺少FROM子句

---

### 19-实战案例\医疗场景\实验数据版本管理.md

**行 617** (sql):

```sql
-- 1. 创建版本管理函数
-- 创建实验版本函数（带完整错误处理）
CREATE OR REPLACE FUNCTION create_experiment_version(
    p_experiment_id TEXT,
    p_data JSONB,
    p_metadata JSONB DEFAULT '{}'::JSONB
)
RETURNS INTEGER
LANGUAG
```

**错误**: 单引号不匹配

---

### 19-实战案例\医疗场景\药物研发与重定位.md

**行 876** (python):

```python
import psycopg2
from pgvector.psycopg2 import register_vector
import numpy as np
from typing import List, Dict

class DrugRepurposingSystem:
    """药物重定位系统"""

    def __init__(self, conn_str: str):

```

**错误**: 语法错误: unterminated string literal (detected at line 47) (行 47)

---

### 19-实战案例\图书场景\智能图书推荐系统.md

**行 427** (sql):

```sql
-- 启用pgvector扩展
CREATE EXTENSION IF NOT EXISTS vector;

-- 创建图书表
CREATE TABLE books (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    author TEXT,
    category TEXT,
    description TEXT,

```

**错误**: 单引号不匹配

---

### 19-实战案例\多模一体化场景\多模数据融合系统.md

**行 162** (sql):

```sql
-- 时序+向量融合表
CREATE TABLE device_metrics (
    time TIMESTAMPTZ NOT NULL,
    device_id INTEGER NOT NULL,
    metric_type TEXT,
    value DECIMAL(10, 2),
    feature_vector vector(256),  -- 特征向量
    me
```

**错误**: SELECT语句缺少FROM子句

---

**行 456** (sql):

```sql
-- 安装扩展
CREATE EXTENSION IF NOT EXISTS timescaledb;
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS age;
CREATE EXTENSION IF NOT EXISTS postgis;
LOAD 'age';
SET search_path = ag_
```

**错误**: SELECT语句缺少FROM子句

---

**行 561** (python):

```python
import psycopg2
from pgvector.psycopg2 import register_vector
import numpy as np
from typing import List, Dict

class GraphVectorFusion:
    """图+向量融合查询"""

    def __init__(self, conn_str: str):

```

**错误**: 语法错误: unterminated string literal (detected at line 50) (行 50)

---

### 19-实战案例\安全场景\智能安全监控系统.md

**行 201** (sql):

```sql
-- 创建安全事件时序表
CREATE TABLE security_events (
    time TIMESTAMPTZ NOT NULL,
    event_type TEXT NOT NULL,
    severity TEXT,
    source_ip INET,
    user_id INTEGER,
    resource TEXT,
    action TEXT,
```

**错误**: SELECT语句缺少FROM子句

---

**行 406** (sql):

```sql
-- 启用TimescaleDB扩展
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- 创建安全事件时序表
CREATE TABLE security_events (
    time TIMESTAMPTZ NOT NULL,
    event_type TEXT NOT NULL,  -- 'login', 'access', 'operati
```

**错误**: SELECT语句缺少FROM子句

---

### 19-实战案例\宠物场景\智能宠物健康管理系统.md

**行 203** (sql):

```sql
-- 创建健康数据时序表
CREATE TABLE pet_health_data (
    time TIMESTAMPTZ NOT NULL,
    pet_id INTEGER NOT NULL,
    weight DECIMAL(10, 2),
    activity_level INTEGER,
    heart_rate INTEGER,
    temperature D
```

**错误**: SELECT语句缺少FROM子句

---

**行 409** (sql):

```sql
-- 启用TimescaleDB和pgvector扩展
CREATE EXTENSION IF NOT EXISTS timescaledb;
CREATE EXTENSION IF NOT EXISTS vector;

-- 创建健康数据时序表
CREATE TABLE pet_health_data (
    time TIMESTAMPTZ NOT NULL,
    pet_id IN
```

**错误**: SELECT语句缺少FROM子句

---

### 19-实战案例\审计场景\智能审计系统.md

**行 198** (sql):

```sql
-- 创建审计日志时序表
CREATE TABLE audit_logs (
    time TIMESTAMPTZ NOT NULL,
    user_id INTEGER,
    username TEXT,
    action_type TEXT NOT NULL,
    table_name TEXT,
    record_id INTEGER,
    old_values
```

**错误**: SELECT语句缺少FROM子句

---

**行 433** (sql):

```sql
-- 启用TimescaleDB扩展
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- 创建审计日志时序表
CREATE TABLE audit_logs (
    time TIMESTAMPTZ NOT NULL,
    user_id INTEGER,
    username TEXT,
    action_type TEXT NOT N
```

**错误**: SELECT语句缺少FROM子句

---

### 19-实战案例\建筑场景\智慧工地管理系统.md

**行 212** (sql):

```sql
-- 创建人员位置时序表
CREATE TABLE personnel_location (
    time TIMESTAMPTZ NOT NULL,
    personnel_id TEXT NOT NULL,
    name TEXT,
    role TEXT,
    location GEOGRAPHY(POINT, 4326),
    zone_id TEXT,
    s
```

**错误**: SELECT语句缺少FROM子句

---

**行 235** (sql):

```sql
CREATE TABLE equipment_data (
    time TIMESTAMPTZ NOT NULL,
    equipment_id TEXT NOT NULL,
    equipment_type TEXT,
    location GEOGRAPHY(POINT, 4326),
    status TEXT,
    usage_hours DECIMAL(10,
```

**错误**: SELECT语句缺少FROM子句

---

**行 410** (sql):

```sql
-- 启用TimescaleDB和PostGIS扩展
CREATE EXTENSION IF NOT EXISTS timescaledb;
CREATE EXTENSION IF NOT EXISTS postgis;

-- 创建人员位置时序表
CREATE TABLE personnel_location (
    time TIMESTAMPTZ NOT NULL,
    person
```

**错误**: SELECT语句缺少FROM子句

---

### 19-实战案例\性能问题-案例库.md

**行 139** (sql):

```sql
-- 性能对比查询
CREATE OR REPLACE FUNCTION compare_query_performance()
RETURNS TABLE (
    metric_name TEXT,
    before_value NUMERIC,
    after_value NUMERIC,
    improvement_percent NUMERIC
) AS $$
BEGIN

```

**错误**: SELECT语句缺少FROM子句

---

**行 324** (sql):

```sql
-- 创建变更审批表
CREATE TABLE IF NOT EXISTS change_approvals (
    id SERIAL PRIMARY KEY,
    change_type TEXT,  -- 'parameter', 'index', 'ddl', 'sql'
    change_description TEXT,
    old_value TEXT,
    ne
```

**错误**: SELECT语句缺少FROM子句

---

**行 409** (sql):

```sql
-- 性能对比
CREATE OR REPLACE FUNCTION compare_io_performance()
RETURNS TABLE (
    metric_name TEXT,
    before_value NUMERIC,
    after_value NUMERIC,
    improvement_percent NUMERIC
) AS $$
BEGIN
    R
```

**错误**: SELECT语句缺少FROM子句

---

### 19-实战案例\房地产场景\智能楼宇管理系统.md

**行 206** (sql):

```sql
-- 创建设备数据时序表
CREATE TABLE equipment_metrics (
    time TIMESTAMPTZ NOT NULL,
    equipment_id TEXT NOT NULL,
    equipment_type TEXT,
    power_consumption DECIMAL(10, 2),
    temperature DECIMAL(10,
```

**错误**: SELECT语句缺少FROM子句

---

**行 228** (sql):

```sql
CREATE TABLE energy_consumption (
    time TIMESTAMPTZ NOT NULL,
    building_id TEXT NOT NULL,
    floor_id TEXT,
    total_power DECIMAL(10, 2),
    lighting_power DECIMAL(10, 2),
    hvac_power DEC
```

**错误**: SELECT语句缺少FROM子句

---

**行 402** (sql):

```sql
-- 启用TimescaleDB和PostGIS扩展
CREATE EXTENSION IF NOT EXISTS timescaledb;
CREATE EXTENSION IF NOT EXISTS postgis;

-- 创建设备数据时序表
CREATE TABLE equipment_metrics (
    time TIMESTAMPTZ NOT NULL,
    equipme
```

**错误**: SELECT语句缺少FROM子句

---

### 19-实战案例\政务场景\社保大数据系统.md

**行 450** (sql):

```sql
-- 启用扩展
CREATE EXTENSION IF NOT EXISTS pg_dsr;

-- 创建社保数据表
CREATE TABLE social_security_records (
    id SERIAL PRIMARY KEY,
    citizen_id TEXT NOT NULL,
    name TEXT NOT NULL,
    phone TEXT NOT NU
```

**错误**: SELECT语句缺少FROM子句

---

**行 1573** (sql):

```sql
-- 启用扩展
CREATE EXTENSION IF NOT EXISTS pg_dsr;

-- 创建社保数据表
CREATE TABLE social_security_records (
    id SERIAL PRIMARY KEY,
    citizen_id TEXT NOT NULL,
    name TEXT NOT NULL,
    phone TEXT NOT NU
```

**错误**: SELECT语句缺少FROM子句

---

**行 2047** (sql):

```sql
-- 1. 创建不可篡改审计日志表
CREATE TABLE audit_log (
    id SERIAL PRIMARY KEY,
    operation TEXT,
    old_data JSONB,
    new_data JSONB,
    user_name TEXT,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    previ
```

**错误**: 单引号不匹配

---

### 19-实战案例\气象场景\智能气象分析系统.md

**行 206** (sql):

```sql
-- 创建气象数据时序表
CREATE TABLE weather_data (
    time TIMESTAMPTZ NOT NULL,
    station_id INTEGER NOT NULL,
    location POINT NOT NULL,
    temperature DECIMAL(5, 2),
    humidity DECIMAL(5, 2),
    pre
```

**错误**: SELECT语句缺少FROM子句

---

**行 396** (sql):

```sql
-- 启用TimescaleDB和PostGIS扩展
CREATE EXTENSION IF NOT EXISTS timescaledb;
CREATE EXTENSION IF NOT EXISTS postgis;

-- 创建气象站点表
CREATE TABLE weather_stations (
    id SERIAL PRIMARY KEY,
    name TEXT NOT
```

**错误**: SELECT语句缺少FROM子句

---

### 19-实战案例\水利场景\智慧水利监控系统.md

**行 207** (sql):

```sql
-- 创建水位数据时序表
CREATE TABLE water_level_data (
    time TIMESTAMPTZ NOT NULL,
    station_id TEXT NOT NULL,
    station_name TEXT,
    location GEOGRAPHY(POINT, 4326),
    water_level DECIMAL(10, 2),

```

**错误**: SELECT语句缺少FROM子句

---

**行 230** (sql):

```sql
CREATE TABLE water_quality_data (
    time TIMESTAMPTZ NOT NULL,
    station_id TEXT NOT NULL,
    location GEOGRAPHY(POINT, 4326),
    ph DECIMAL(10, 2),
    dissolved_oxygen DECIMAL(10, 2),
    turb
```

**错误**: SELECT语句缺少FROM子句

---

**行 409** (sql):

```sql
-- 启用TimescaleDB和PostGIS扩展
CREATE EXTENSION IF NOT EXISTS timescaledb;
CREATE EXTENSION IF NOT EXISTS postgis;

-- 创建水位数据时序表
CREATE TABLE water_level_data (
    time TIMESTAMPTZ NOT NULL,
    station_
```

**错误**: SELECT语句缺少FROM子句

---

### 19-实战案例\汽车场景\智能驾驶数据系统.md

**行 200** (sql):

```sql
-- 创建车辆数据时序表
CREATE TABLE vehicle_data (
    time TIMESTAMPTZ NOT NULL,
    vehicle_id TEXT NOT NULL,
    speed DECIMAL(10, 2),
    acceleration DECIMAL(10, 2),
    brake_pressure DECIMAL(10, 2),

```

**错误**: SELECT语句缺少FROM子句

---

**行 387** (sql):

```sql
-- 启用TimescaleDB和PostGIS扩展
CREATE EXTENSION IF NOT EXISTS timescaledb;
CREATE EXTENSION IF NOT EXISTS postgis;

-- 创建车辆位置数据时序表
CREATE TABLE vehicle_location_data (
    time TIMESTAMPTZ NOT NULL,
    v
```

**错误**: SELECT语句缺少FROM子句

---

### 19-实战案例\港口场景\智慧港口管理系统.md

**行 216** (sql):

```sql
-- 创建船舶数据时序表
CREATE TABLE vessel_data (
    time TIMESTAMPTZ NOT NULL,
    vessel_id TEXT NOT NULL,
    vessel_name TEXT,
    location GEOGRAPHY(POINT, 4326),
    speed DECIMAL(10, 2),
    heading DEC
```

**错误**: SELECT语句缺少FROM子句

---

**行 239** (sql):

```sql
CREATE TABLE cargo_data (
    time TIMESTAMPTZ NOT NULL,
    cargo_id TEXT NOT NULL,
    vessel_id TEXT,
    location GEOGRAPHY(POINT, 4326),
    status TEXT,
    weight DECIMAL(10, 2),
    metadata J
```

**错误**: SELECT语句缺少FROM子句

---

**行 675** (sql):

```sql
-- 启用TimescaleDB和PostGIS扩展
CREATE EXTENSION IF NOT EXISTS timescaledb;
CREATE EXTENSION IF NOT EXISTS postgis;

-- 创建船舶数据时序表
CREATE TABLE vessel_data (
    time TIMESTAMPTZ NOT NULL,
    vessel_id TEX
```

**错误**: SELECT语句缺少FROM子句

---

### 19-实战案例\游戏场景\玩家行为分析系统.md

**行 255** (sql):

```sql
-- 创建玩家行为时序表
CREATE TABLE player_behaviors (
    time TIMESTAMPTZ NOT NULL,
    player_id TEXT NOT NULL,
    event_type TEXT NOT NULL,  -- 'login', 'play', 'purchase', 'logout'
    game_level INTEGER,
```

**错误**: SELECT语句缺少FROM子句

---

**行 534** (sql):

```sql
-- 启用TimescaleDB和pgvector扩展
CREATE EXTENSION IF NOT EXISTS timescaledb;
CREATE EXTENSION IF NOT EXISTS vector;

-- 创建玩家画像表
CREATE TABLE player_profiles (
    player_id TEXT PRIMARY KEY,
    registrati
```

**错误**: SELECT语句缺少FROM子句

---

### 19-实战案例\环保场景\环境监测预警系统.md

**行 213** (sql):

```sql
-- 创建环境数据时序表
CREATE TABLE environment_data (
    time TIMESTAMPTZ NOT NULL,
    sensor_id TEXT NOT NULL,
    data_type TEXT NOT NULL,  -- 'air_quality', 'water_quality', 'soil'
    pm25 DECIMAL(10, 2)
```

**错误**: SELECT语句缺少FROM子句

---

**行 455** (sql):

```sql
-- 启用TimescaleDB、PostGIS和pgvector扩展
CREATE EXTENSION IF NOT EXISTS timescaledb;
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS vector;

-- 创建环境数据时序表
CREATE TABLE environment_da
```

**错误**: SELECT语句缺少FROM子句

---

### 19-实战案例\生产场景\智能生产管理系统.md

**行 193** (sql):

```sql
-- 创建生产数据时序表
CREATE TABLE production_data (
    time TIMESTAMPTZ NOT NULL,
    production_line_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER,
    quality_score DECIMAL(5,
```

**错误**: SELECT语句缺少FROM子句

---

**行 378** (sql):

```sql
-- 启用TimescaleDB扩展
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- 创建生产数据时序表
CREATE TABLE production_data (
    time TIMESTAMPTZ NOT NULL,
    production_line_id TEXT NOT NULL,
    product_id TEXT NOT
```

**错误**: SELECT语句缺少FROM子句

---

### 19-实战案例\电信场景\网络质量监控系统.md

**行 200** (sql):

```sql
-- 创建网络质量时序表
CREATE TABLE network_quality (
    time TIMESTAMPTZ NOT NULL,
    device_id TEXT NOT NULL,
    base_station_id TEXT,
    latency_ms DECIMAL(10, 2),
    packet_loss DECIMAL(10, 2),
    ban
```

**错误**: SELECT语句缺少FROM子句

---

**行 377** (sql):

```sql
-- 启用TimescaleDB扩展
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- 创建网络质量数据时序表
CREATE TABLE network_quality_metrics (
    time TIMESTAMPTZ NOT NULL,
    node_id TEXT NOT NULL,  -- 网络节点ID
    node_type
```

**错误**: SELECT语句缺少FROM子句

---

### 19-实战案例\电力场景\智能电力调度系统.md

**行 204** (sql):

```sql
-- 创建负荷数据时序表
CREATE TABLE load_data (
    time TIMESTAMPTZ NOT NULL,
    node_id TEXT NOT NULL,
    location GEOGRAPHY(POINT, 4326),
    load_mw DECIMAL(10, 2),
    voltage DECIMAL(10, 2),
    frequen
```

**错误**: SELECT语句缺少FROM子句

---

**行 226** (sql):

```sql
CREATE TABLE generation_data (
    time TIMESTAMPTZ NOT NULL,
    generator_id TEXT NOT NULL,
    location GEOGRAPHY(POINT, 4326),
    output_mw DECIMAL(10, 2),
    fuel_consumption DECIMAL(10, 2),

```

**错误**: SELECT语句缺少FROM子句

---

**行 398** (sql):

```sql
-- 启用TimescaleDB扩展
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- 创建负荷数据时序表
CREATE TABLE load_data (
    time TIMESTAMPTZ NOT NULL,
    grid_id TEXT NOT NULL,
    load_mw DECIMAL(10, 2),  -- 负荷（MW）

```

**错误**: SELECT语句缺少FROM子句

---

### 19-实战案例\电商场景\商品混合搜索案例.md

**行 440** (sql):

```sql
-- 商品表
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    category TEXT NOT NULL,
    price NUMERIC(10, 2),

    -- 全文搜索字段
    search_text TEXT GENERA
```

**错误**: 单引号不匹配

---

**行 1316** (sql):

```sql
-- 启用扩展
CREATE EXTENSION IF NOT EXISTS vector;

-- 创建商品表
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    category TEXT NOT NULL,
    price NUMERIC(
```

**错误**: 单引号不匹配

---

### 19-实战案例\直播场景\智能直播推荐系统.md

**行 205** (sql):

```sql
-- 创建直播数据时序表
CREATE TABLE live_stream_data (
    time TIMESTAMPTZ NOT NULL,
    stream_id INTEGER NOT NULL,
    viewer_count INTEGER,
    like_count INTEGER,
    comment_count INTEGER,
    gift_count
```

**错误**: SELECT语句缺少FROM子句

---

**行 413** (sql):

```sql
-- 启用pgvector和TimescaleDB扩展
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- 创建直播表
CREATE TABLE live_streams (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
```

**错误**: SELECT语句缺少FROM子句

---

### 19-实战案例\石油场景\智能油田管理系统.md

**行 214** (sql):

```sql
-- 创建油井数据时序表
CREATE TABLE well_data (
    time TIMESTAMPTZ NOT NULL,
    well_id TEXT NOT NULL,
    location GEOGRAPHY(POINT, 4326),
    production_rate DECIMAL(10, 2),
    pressure DECIMAL(10, 2),

```

**错误**: SELECT语句缺少FROM子句

---

**行 237** (sql):

```sql
CREATE TABLE equipment_data (
    time TIMESTAMPTZ NOT NULL,
    equipment_id TEXT NOT NULL,
    well_id TEXT,
    location GEOGRAPHY(POINT, 4326),
    status TEXT,
    vibration DECIMAL(10, 2),
    t
```

**错误**: SELECT语句缺少FROM子句

---

**行 407** (sql):

```sql
-- 启用TimescaleDB和PostGIS扩展
CREATE EXTENSION IF NOT EXISTS timescaledb;
CREATE EXTENSION IF NOT EXISTS postgis;

-- 创建油井生产数据时序表
CREATE TABLE well_production_data (
    time TIMESTAMPTZ NOT NULL,
    we
```

**错误**: SELECT语句缺少FROM子句

---

### 19-实战案例\矿业场景\矿山安全监测系统.md

**行 205** (sql):

```sql
-- 创建环境数据时序表
CREATE TABLE environment_data (
    time TIMESTAMPTZ NOT NULL,
    sensor_id TEXT NOT NULL,
    location GEOGRAPHY(POINT, 4326),
    temperature DECIMAL(10, 2),
    humidity DECIMAL(10, 2
```

**错误**: SELECT语句缺少FROM子句

---

**行 229** (sql):

```sql
CREATE TABLE personnel_location (
    time TIMESTAMPTZ NOT NULL,
    personnel_id TEXT NOT NULL,
    location GEOGRAPHY(POINT, 4326),
    zone_id TEXT,
    status TEXT,
    metadata JSONB
);

-- 转换为时序
```

**错误**: SELECT语句缺少FROM子句

---

**行 403** (sql):

```sql
-- 启用TimescaleDB和PostGIS扩展
CREATE EXTENSION IF NOT EXISTS timescaledb;
CREATE EXTENSION IF NOT EXISTS postgis;

-- 创建环境数据时序表
CREATE TABLE environment_data (
    time TIMESTAMPTZ NOT NULL,
    sensor_i
```

**错误**: SELECT语句缺少FROM子句

---

### 19-实战案例\社交场景\智能社交推荐系统.md

**行 392** (sql):

```sql
-- 启用pgvector和Apache AGE扩展
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS age;
LOAD 'age';
SET search_path = ag_catalog, "$user", public;

-- 创建社交图谱
SELECT create_graph('social_
```

**错误**: SELECT语句缺少FROM子句

---

### 19-实战案例\科研场景\科学数据管理系统.md

**行 198** (sql):

```sql
-- 创建实验数据时序表
CREATE TABLE experiment_data (
    time TIMESTAMPTZ NOT NULL,
    experiment_id TEXT NOT NULL,
    measurement_type TEXT,
    value DECIMAL(10, 4),
    unit TEXT,
    metadata JSONB
);

-
```

**错误**: SELECT语句缺少FROM子句

---

**行 374** (sql):

```sql
-- 安装扩展
CREATE EXTENSION IF NOT EXISTS timescaledb;
CREATE EXTENSION IF NOT EXISTS vector;

-- 创建实验元数据表
CREATE TABLE experiments (
    experiment_id SERIAL PRIMARY KEY,
    experiment_name TEXT NOT NU
```

**错误**: SELECT语句缺少FROM子句

---

### 19-实战案例\纺织场景\智能纺织生产系统.md

**行 212** (sql):

```sql
-- 创建设备数据时序表
CREATE TABLE equipment_data (
    time TIMESTAMPTZ NOT NULL,
    equipment_id TEXT NOT NULL,
    equipment_type TEXT,
    temperature DECIMAL(10, 2),
    humidity DECIMAL(10, 2),
    spee
```

**错误**: SELECT语句缺少FROM子句

---

**行 402** (sql):

```sql
-- 启用TimescaleDB和pgvector扩展
CREATE EXTENSION IF NOT EXISTS timescaledb;
CREATE EXTENSION IF NOT EXISTS vector;

-- 创建生产数据时序表
CREATE TABLE textile_production_data (
    time TIMESTAMPTZ NOT NULL,
    m
```

**错误**: SELECT语句缺少FROM子句

---

### 19-实战案例\能源场景\智能电网监控系统.md

**行 238** (sql):

```sql
-- 创建时序表
CREATE TABLE power_metrics (
    time TIMESTAMPTZ NOT NULL,
    device_id TEXT NOT NULL,
    voltage DECIMAL(10, 2),
    current DECIMAL(10, 2),
    power DECIMAL(10, 2),
    temperature DECI
```

**错误**: SELECT语句缺少FROM子句

---

**行 698** (sql):

```sql
-- 启用TimescaleDB扩展
CREATE EXTENSION IF NOT EXISTS timescaledb;
CREATE EXTENSION IF NOT EXISTS vector;

-- 创建电力设备时序数据表
CREATE TABLE power_grid_metrics (
    time TIMESTAMPTZ NOT NULL,
    device_id TEX
```

**错误**: SELECT语句缺少FROM子句

---

### 19-实战案例\能源管理场景\智能能源管理系统.md

**行 193** (sql):

```sql
-- 创建能耗数据时序表
CREATE TABLE energy_consumption (
    time TIMESTAMPTZ NOT NULL,
    device_id INTEGER NOT NULL,
    device_type TEXT,
    energy_type TEXT,
    consumption DECIMAL(10, 2),
    cost DECIM
```

**错误**: SELECT语句缺少FROM子句

---

**行 383** (sql):

```sql
-- 启用TimescaleDB扩展
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- 创建能耗数据时序表
CREATE TABLE energy_consumption_data (
    time TIMESTAMPTZ NOT NULL,
    facility_id TEXT NOT NULL,
    energy_type TEXT,
```

**错误**: SELECT语句缺少FROM子句

---

### 19-实战案例\航空场景\航班数据分析系统.md

**行 206** (sql):

```sql
-- 创建航班数据时序表
CREATE TABLE flight_data (
    time TIMESTAMPTZ NOT NULL,
    flight_id TEXT NOT NULL,
    airline TEXT,
    departure_airport TEXT,
    arrival_airport TEXT,
    scheduled_departure TIME
```

**错误**: SELECT语句缺少FROM子句

---

**行 676** (sql):

```sql
-- 启用TimescaleDB扩展
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- 创建航班数据时序表
CREATE TABLE flight_data (
    time TIMESTAMPTZ NOT NULL,
    flight_number TEXT NOT NULL,
    airline TEXT,
    origin_air
```

**错误**: SELECT语句缺少FROM子句

---

**行 739** (python):

```python
import psycopg2
from datetime import datetime, timedelta
from typing import Optional, List, Dict

class FlightDataAnalyzer:
    def __init__(self, conn_str):
        """初始化航班数据分析器"""
        self.conn
```

**错误**: 语法错误: parameter without a default follows parameter with a default (行 14)

---

### 19-实战案例\视频场景\智能视频推荐系统.md

**行 440** (sql):

```sql
-- 启用pgvector和TimescaleDB扩展
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- 创建视频表
CREATE TABLE videos (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    c
```

**错误**: SELECT语句缺少FROM子句

---

### 19-实战案例\酒店场景\智能酒店管理系统.md

**行 290** (sql):

```sql
CREATE TABLE price_data (
    time TIMESTAMPTZ NOT NULL,
    room_type TEXT NOT NULL,
    date DATE NOT NULL,
    base_price DECIMAL(10, 2),
    dynamic_price DECIMAL(10, 2),
    availability INTEGER,
```

**错误**: SELECT语句缺少FROM子句

---

**行 312** (sql):

```sql
-- 查询指定时间段可用房间
SELECT
    r.id,
    r.room_number,
    r.room_type,
    r.location
FROM rooms r
WHERE r.id NOT IN (
    SELECT room_id
    FROM reservations
    WHERE reservation_period && '[2024-01-1
```

**错误**: 括号不匹配

---

**行 471** (sql):

```sql
-- 启用TimescaleDB和PostGIS扩展
CREATE EXTENSION IF NOT EXISTS timescaledb;
CREATE EXTENSION IF NOT EXISTS postgis;

-- 创建房间表
CREATE TABLE rooms (
    id SERIAL PRIMARY KEY,
    hotel_id INTEGER NOT NULL,

```

**错误**: SELECT语句缺少FROM子句

---

### 19-实战案例\金融场景\风险控制优化.md

**行 632** (sql):

```sql
-- 启用扩展
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS age;
LOAD 'age';
SET search_path = ag_catalog, "$user", public;

-- 创建交易表
CREATE TABLE transactions (
    transaction_id S
```

**错误**: SELECT语句缺少FROM子句

---

### 19-实战案例\金融行业完整案例.md

**行 122** (sql):

```sql
-- 交易记录表（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'transaction_records') THEN
            CREATE TABLE transaction_records (

```

**错误**: 单引号不匹配

---

### 19-实战案例\钢铁场景\智能钢铁生产系统.md

**行 214** (sql):

```sql
-- 创建温度数据时序表
CREATE TABLE temperature_data (
    time TIMESTAMPTZ NOT NULL,
    furnace_id TEXT NOT NULL,
    location GEOGRAPHY(POINT, 4326),
    temperature DECIMAL(10, 2),
    pressure DECIMAL(10,
```

**错误**: SELECT语句缺少FROM子句

---

**行 236** (sql):

```sql
CREATE TABLE quality_data (
    time TIMESTAMPTZ NOT NULL,
    batch_id TEXT NOT NULL,
    carbon_content DECIMAL(10, 2),
    manganese_content DECIMAL(10, 2),
    tensile_strength DECIMAL(10, 2),

```

**错误**: SELECT语句缺少FROM子句

---

**行 401** (sql):

```sql
-- 启用TimescaleDB扩展
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- 创建生产数据时序表
CREATE TABLE steel_production_data (
    time TIMESTAMPTZ NOT NULL,
    furnace_id TEXT NOT NULL,
    batch_id TEXT NOT NUL
```

**错误**: SELECT语句缺少FROM子句

---

### 19-实战案例\零售场景\智能库存管理系统.md

**行 289** (sql):

```sql
-- 创建销售时序表
CREATE TABLE sales_history (
    time TIMESTAMPTZ NOT NULL,
    product_id INTEGER NOT NULL,
    store_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    revenue DECIMAL(10, 2),
    di
```

**错误**: SELECT语句缺少FROM子句

---

**行 827** (sql):

```sql
-- 启用TimescaleDB扩展
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- 创建销售时序表
CREATE TABLE sales_history (
    time TIMESTAMPTZ NOT NULL,
    product_id INTEGER NOT NULL,
    store_id INTEGER NOT NULL,

```

**错误**: SELECT语句缺少FROM子句

---

### 19-实战案例\食品场景\食品安全追溯系统.md

**行 204** (sql):

```sql
-- 创建追溯数据时序表
CREATE TABLE trace_data (
    time TIMESTAMPTZ NOT NULL,
    batch_id TEXT NOT NULL,
    product_id TEXT NOT NULL,
    stage TEXT,
    location TEXT,
    operator TEXT,
    status TEXT,

```

**错误**: SELECT语句缺少FROM子句

---

**行 417** (sql):

```sql
-- 启用TimescaleDB和pgvector扩展
CREATE EXTENSION IF NOT EXISTS timescaledb;
CREATE EXTENSION IF NOT EXISTS vector;

-- 创建追溯数据时序表
CREATE TABLE trace_data (
    time TIMESTAMPTZ NOT NULL,
    batch_id TEXT
```

**错误**: SELECT语句缺少FROM子句

---

### 20-故障诊断案例\01-性能调优-变更闭环.md

**行 580** (sql):

```sql
-- 回滚变更（带完整错误处理）
CREATE OR REPLACE FUNCTION rollback_change(
    p_change_id INT
)
RETURNS TABLE (
    change_id INT,
    rollback_status TEXT,
    rollback_time TIMESTAMPTZ
) AS $$
DECLARE
    change
```

**错误**: 单引号不匹配

---

### 20-故障诊断案例\03-集群与高可用-演练SOP.md

**行 412** (sql):

```sql
-- PostgreSQL 18异步I/O配置
ALTER SYSTEM SET io_direct = 'data,wal';
ALTER SYSTEM SET io_combine_limit = '256kB';

-- 重启后生效
SELECT pg_reload_conf();

-- 性能提升:
-- WAL写入性能: +25-30%
-- 复制延迟: -20-25%
-- 故障恢复速
```

**错误**: SELECT语句缺少FROM子句

---

### 20-故障诊断案例\05-图数据库与Cypher-落地指南.md

**行 75** (sql):

```sql
-- 创建图数据库配置表
CREATE TABLE IF NOT EXISTS graph_config (
    graph_name TEXT PRIMARY KEY,
    max_nodes BIGINT DEFAULT 1000000,
    max_edges BIGINT DEFAULT 10000000,
    enable_indexing BOOLEAN DEFAULT
```

**错误**: SELECT语句缺少FROM子句

---

### 20-故障诊断案例\06-日志与可观测性-落地指南.md

**行 499** (sql):

```sql
-- 从日志中提取慢查询（带性能测试）
-- 注意：pg_log是系统视图，需要根据实际日志表结构调整
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    regexp_replace(message, '.*statement: ', '') AS query,
    regexp_replace(message, '.*duration: ([0-9.
```

**错误**: 单引号不匹配

---

### 21-最佳实践\快速开始\环境搭建指南.md

**行 618** (sql):

```sql
-- 配置压缩策略
ALTER TABLE test_metrics SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'device_id'
);

-- 启用自动压缩（保留策略）
SELECT add_compression_policy('test_metrics', INTERVAL '7 days')
```

**错误**: SELECT语句缺少FROM子句

---

### 21-最佳实践\成本优化\计算成本优化.md

**行 132** (sql):

```sql
-- 创建查询优化建议函数
CREATE OR REPLACE FUNCTION generate_query_optimization_suggestions()
RETURNS TABLE (
    query_text TEXT,
    current_cost NUMERIC,
    optimization_suggestion TEXT,
    expected_savings
```

**错误**: 单引号不匹配

---

### 21-最佳实践\迁移指南\从MongoDB迁移.md

**行 407** (python):

```python
from datetime import datetime
import pytz

# MongoDB 存储的是 UTC 时间
# PostgreSQL 使用 TIMESTAMPTZ 自动处理时区

# 转换示例
def convert_mongodb_date(mongo_date):
    if isinstance(mongo_date, datetime):
        # Mon
```

**错误**: 语法错误: invalid syntax (行 16)

---

### 21-最佳实践\迁移指南\从MySQL迁移.md

**行 1296** (sql):

```sql
-- 创建 MySQL DATE_FORMAT 兼容函数
CREATE OR REPLACE FUNCTION mysql_date_format(
    date_val DATE,
    format_str TEXT
)
RETURNS TEXT AS $$
BEGIN
    RETURN TO_CHAR(date_val, format_str);
END;
$$ LANGUAGE
```

**错误**: SELECT语句缺少FROM子句

---

**行 1531** (sql):

```sql
-- 1. 设置时区
SET timezone = 'UTC';

-- 2. 设置日期格式
SET datestyle = 'ISO, MDY';

-- 3. 日期转换
SELECT
    '2025-11-01'::DATE,
    '2025-11-01 10:00:00'::TIMESTAMPTZ,
    NOW()::TIMESTAMPTZ;

-- 4. 日期格式化
SELEC
```

**错误**: SELECT语句缺少FROM子句

---

### 22-工具与资源\08.04-最佳实践总结.md

**行 755** (sql):

```sql
-- ✅ 启用RLS
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- ✅ 创建RLS策略
CREATE POLICY user_access_policy ON users
    FOR ALL
    TO app_user
    USING (user_id = current_setting('app.user_id')::BIGINT)
```

**错误**: SELECT语句缺少FROM子句

---

**行 837** (sql):

```sql
-- ✅ 启用审计日志
ALTER SYSTEM SET log_statement = 'all';
ALTER SYSTEM SET log_min_duration_statement = 1000;  -- 记录超过1秒的查询
SELECT pg_reload_conf();

-- ✅ 创建审计表
CREATE TABLE audit_log (
    id BIGSERIAL PRI
```

**错误**: SELECT语句缺少FROM子句

---

### 22-工具与资源\BEST_PRACTICES.md

**行 411** (sql):

```sql
-- 启用异步I/O
ALTER SYSTEM SET io_direct = 'data,wal';
ALTER SYSTEM SET effective_io_concurrency = 200;
ALTER SYSTEM SET wal_io_concurrency = 200;
SELECT pg_reload_conf();

-- 性能提升：批量导入速度提升40%

```

**错误**: SELECT语句缺少FROM子句

---

**行 440** (sql):

```sql
-- 配置并行查询参数
ALTER SYSTEM SET max_parallel_workers_per_gather = 4;
ALTER SYSTEM SET max_parallel_workers = 8;
ALTER SYSTEM SET max_parallel_maintenance_workers = 4;
SELECT pg_reload_conf();

-- 性能提升：聚合
```

**错误**: SELECT语句缺少FROM子句

---

### 22-工具与资源\feature_bench\README.md

**行 103** (sql):

```sql
-- 详细查询计划
EXPLAIN (ANALYZE, BUFFERS, WAL, SUMMARY, VERBOSE, TIMING, COSTS)
SELECT ...;

-- 关键指标：
-- - Planning Time: 计划时间
-- - Execution Time: 执行时间
-- - Buffers: shared hit/read/dirtied/written
-- - I
```

**错误**: SELECT语句缺少FROM子句

---

### 22-工具与资源\feature_bench\brin_parallel_build.md

**行 213** (sql):

```sql
-- 记录构建开始时间
SELECT now() AS build_start;

-- 执行 CREATE INDEX

-- 记录构建结束时间
SELECT now() AS build_end;

-- 计算构建耗时
SELECT
    build_end - build_start AS build_duration;

```

**错误**: SELECT语句缺少FROM子句

---

### 22-工具与资源\knowledge_map.md

**行 390** (sql):

```sql
-- 更新知识节点
CREATE OR REPLACE FUNCTION update_knowledge_node(
    p_node_name TEXT,
    p_description TEXT DEFAULT NULL,
    p_document_path TEXT DEFAULT NULL
)
RETURNS TABLE (
    status TEXT,
    node
```

**错误**: SELECT语句缺少FROM子句

---

### 22-工具与资源\复制延迟-基准模板.md

**行 64** (sql):

```sql
-- 在从库检查恢复状态
SELECT
    pg_is_in_recovery() AS is_standby,
    pg_last_wal_receive_lsn() AS last_receive_lsn,
    pg_last_wal_replay_lsn() AS last_replay_lsn,
    pg_wal_lsn_diff(
        pg_last_wal_
```

**错误**: SELECT语句缺少FROM子句

---

**行 189** (sql):

```sql
-- 在主库设置异步复制
ALTER SYSTEM SET synchronous_commit = 'off';
SELECT pg_reload_conf();

-- 或针对特定会话
SET synchronous_commit = 'off';

```

**错误**: SELECT语句缺少FROM子句

---

**行 200** (sql):

```sql
-- 在主库设置同步复制
ALTER SYSTEM SET synchronous_commit = 'on';
ALTER SYSTEM SET synchronous_standby_names = 'FIRST 1 (standby1)';
SELECT pg_reload_conf();

```

**错误**: SELECT语句缺少FROM子句

---

**行 209** (sql):

```sql
-- 等待从库应用完成
ALTER SYSTEM SET synchronous_commit = 'remote_apply';
ALTER SYSTEM SET synchronous_standby_names = 'FIRST 1 (standby1)';
SELECT pg_reload_conf();

```

**错误**: SELECT语句缺少FROM子句

---

**行 293** (sql):

```sql
-- 监控 WAL 生成速率
SELECT
    pg_size_pretty(pg_current_wal_lsn() - '0/0') AS current_wal_size,
    pg_walfile_name(pg_current_wal_lsn()) AS current_wal_file;

-- 定期采样计算 WAL 生成速率
-- 需要定期执行并记录时间戳

```

**错误**: SELECT语句缺少FROM子句

---

### 22-工具与资源\开发工具\调试工具.md

**行 129** (sql):

```sql
-- 启用pg_stat_statements扩展
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- 配置参数
ALTER SYSTEM SET pg_stat_statements.track = 'all';
ALTER SYSTEM SET pg_stat_statements.max = 10000;
SELECT pg_relo
```

**错误**: SELECT语句缺少FROM子句

---

**行 267** (sql):

```sql
-- 创建调试函数
CREATE OR REPLACE FUNCTION debug_function(param1 INTEGER)
RETURNS INTEGER AS $$
DECLARE
    result INTEGER;
    debug_info TEXT;
BEGIN
    -- 记录输入参数
    RAISE NOTICE '输入参数: %', param1;


```

**错误**: SELECT语句缺少FROM子句

---

### 23-对比分析\TCO总拥有成本分析.md

**行 292** (sql):

```sql
-- 基础设施成本计算
CREATE OR REPLACE FUNCTION calculate_infrastructure_cost(
    p_server_count INT DEFAULT 3,
    p_server_cost NUMERIC DEFAULT 50000,  -- 每台服务器成本
    p_storage_tb NUMERIC DEFAULT 10,      -
```

**错误**: SELECT语句缺少FROM子句

---

**行 359** (sql):

```sql
-- 开发人力成本计算
CREATE OR REPLACE FUNCTION calculate_development_cost(
    p_developers INT DEFAULT 5,
    p_daily_rate NUMERIC DEFAULT 1000,    -- 每人每天成本
    p_development_days INT DEFAULT 180,    -- 开发天
```

**错误**: SELECT语句缺少FROM子句

---

**行 712** (sql):

```sql
-- 基础设施成本优化对比
SELECT
    '传统部署' as deployment_type,
    200000 as annual_cost
UNION ALL
SELECT
    '云服务（按需）' as deployment_type,
    150000 as annual_cost
UNION ALL
SELECT
    '云服务（预留实例）' as deploymen
```

**错误**: SELECT语句缺少FROM子句

---

**行 798** (sql):

```sql
-- ROI计算函数
CREATE OR REPLACE FUNCTION calculate_roi(
    p_initial_cost NUMERIC,
    p_annual_cost NUMERIC,
    p_annual_revenue NUMERIC,
    p_years INT DEFAULT 3
)
RETURNS TABLE (
    year INT,

```

**错误**: SELECT语句缺少FROM子句

---

**行 859** (sql):

```sql
-- 完整ROI分析
CREATE OR REPLACE FUNCTION comprehensive_roi_analysis(
    p_scenario TEXT DEFAULT 'medium'
)
RETURNS TABLE (
    metric TEXT,
    value NUMERIC
) AS $$
DECLARE
    v_tco NUMERIC;
    v_ann
```

**错误**: SELECT语句缺少FROM子句

---

**行 1011** (sql):

```sql
-- 成本优化建议
CREATE OR REPLACE FUNCTION generate_cost_optimization_suggestions(
    p_current_tco NUMERIC
)
RETURNS TABLE (
    suggestion TEXT,
    potential_savings NUMERIC,
    implementation_effort T
```

**错误**: SELECT语句缺少FROM子句

---

### 23-对比分析\场景适用性决策矩阵.md

**行 771** (sql):

```sql
-- 场景评分计算
CREATE OR REPLACE FUNCTION scenario_score(
    p_needs_sql BOOLEAN,
    p_needs_transaction BOOLEAN,
    p_needs_hybrid_query BOOLEAN,
    p_needs_managed_service BOOLEAN,
    p_data_scale T
```

**错误**: SELECT语句缺少FROM子句

---

### 23-对比分析\性能基准对比.md

**行 759** (sql):

```sql
-- ROI分析
CREATE OR REPLACE FUNCTION calculate_performance_roi(
    p_tco NUMERIC,
    p_qps NUMERIC,
    p_annual_revenue_per_qps NUMERIC DEFAULT 0.01
)
RETURNS TABLE (
    metric TEXT,
    value NUME
```

**错误**: SELECT语句缺少FROM子句

---

### 23-对比分析\技术能力对比矩阵.md

**行 567** (sql):

```sql
-- 综合评分计算函数
CREATE OR REPLACE FUNCTION calculate_comprehensive_score(
    p_performance_score NUMERIC,
    p_transaction_score NUMERIC,
    p_sql_score NUMERIC,
    p_hybrid_query_score NUMERIC,
    p
```

**错误**: SELECT语句缺少FROM子句

---

### 23-对比分析\风险与约束条件.md

**行 329** (sql):

```sql
-- 1. 数据本地化配置
-- 部署在指定区域的数据中心
-- 使用区域限制的网络策略

-- 2. 跨境数据拦截
CREATE POLICY cross_border_policy ON data
FOR SELECT
USING (
    data_sovereignty = current_user_sovereignty()
);

-- 3. 数据留存策略
CREATE TABLE
```

**错误**: SELECT语句缺少FROM子句

---

### 24-迁移指南\从MongoDB迁移.md

**行 407** (python):

```python
from datetime import datetime
import pytz

# MongoDB 存储的是 UTC 时间
# PostgreSQL 使用 TIMESTAMPTZ 自动处理时区

# 转换示例
def convert_mongodb_date(mongo_date):
    if isinstance(mongo_date, datetime):
        # Mon
```

**错误**: 语法错误: invalid syntax (行 16)

---

### 24-迁移指南\从MySQL迁移.md

**行 1296** (sql):

```sql
-- 创建 MySQL DATE_FORMAT 兼容函数
CREATE OR REPLACE FUNCTION mysql_date_format(
    date_val DATE,
    format_str TEXT
)
RETURNS TEXT AS $$
BEGIN
    RETURN TO_CHAR(date_val, format_str);
END;
$$ LANGUAGE
```

**错误**: SELECT语句缺少FROM子句

---

**行 1531** (sql):

```sql
-- 1. 设置时区
SET timezone = 'UTC';

-- 2. 设置日期格式
SET datestyle = 'ISO, MDY';

-- 3. 日期转换
SELECT
    '2025-11-01'::DATE,
    '2025-11-01 10:00:00'::TIMESTAMPTZ,
    NOW()::TIMESTAMPTZ;

-- 4. 日期格式化
SELEC
```

**错误**: SELECT语句缺少FROM子句

---

### 24-迁移指南\数据库迁移与升级场景分析指南.md

**行 874** (sql):

```sql
-- 1. 行数对比
SELECT
    'source' AS source,
    count(*) AS row_count
FROM source_table
UNION ALL
SELECT
    'target' AS source,
    count(*) AS row_count
FROM target_table;

-- 2. 数据校验和
SELECT
    md5(
```

**错误**: 单引号不匹配

---

### 25-理论体系\25.01-形式化方法\01.07-PostgreSQL18新特性完整分析.md

**行 1266** (sql):

```sql
-- 场景：查询导致OOM

-- Step 1: 启用内存上下文日志
SET log_memory_context = on;
SET client_min_messages = log;

-- Step 2: 执行问题查询
SELECT ...;

-- Step 3: 查看日志
/*
LOG: memory context stats:
TopMemoryContext: 8388608
```

**错误**: SELECT语句缺少FROM子句

---

**行 1802** (sql):

```sql
-- 启用RLS
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;

-- 创建策略
CREATE POLICY orders_isolation ON orders
    FOR SELECT
    USING (customer_id = current_user_id());

-- PostgreSQL 17：每行都计算策略（慢）
-- Pos
```

**错误**: SELECT语句缺少FROM子句

---

**行 2011** (sql):

```sql
SELECT gen_random_uuidv7();
-- 时间有序，索引性能优于UUIDv4

```

**错误**: SELECT语句缺少FROM子句

---

### 25-理论体系\25.03-查询语义\08.03-同态与查询包含-Containment_Equivalence判定.md

**行 633** (sql):

```sql
-- SQLite 3.45实现（简化版）
CREATE TABLE query_equivalence (
    query1_hash TEXT,
    query2_hash TEXT,
    is_equivalent BOOLEAN
);

-- 使用查询哈希进行等价性检查
INSERT INTO query_equivalence VALUES
    (hash_query('
```

**错误**: SELECT语句缺少FROM子句

---

### 25-理论体系\25.03-查询语义\08.04-Chase与Backchase-依赖下的查询最小化.md

**行 293** (sql):

```sql
-- Chase算法实现
CREATE OR REPLACE FUNCTION chase_query(
    p_query_id UUID,
    p_dependencies UUID[]
)
RETURNS UUID AS $$
DECLARE
    v_current_query_id UUID := p_query_id;
    v_iteration INTEGER := 0
```

**错误**: SELECT语句缺少FROM子句

---

### 25-理论体系\CAP理论\BASE理论详解.md

**行 153** (sql):

```sql
-- 异步复制（基本可用）
ALTER SYSTEM SET synchronous_standby_names = '';
ALTER SYSTEM SET synchronous_commit = 'local';

-- 特征：
-- ✅ 主库继续服务
-- ✅ 备库可能延迟
-- ✅ 保证基本可用

```

**错误**: 单引号不匹配

---

**行 194** (sql):

```sql
-- 异步复制（软状态）
ALTER SYSTEM SET synchronous_standby_names = '';
ALTER SYSTEM SET synchronous_commit = 'local';

-- 特征：
-- ✅ 主库和备库状态可能不一致
-- ✅ 状态动态变化
-- ✅ 最终会达到一致状态

```

**错误**: 单引号不匹配

---

**行 233** (sql):

```sql
-- 异步复制（最终一致性）
ALTER SYSTEM SET synchronous_standby_names = '';
ALTER SYSTEM SET synchronous_commit = 'local';

-- 特征：
-- ✅ 主库立即提交
-- ✅ 备库延迟同步
-- ✅ 最终所有节点一致

```

**错误**: 单引号不匹配

---

**行 252** (sql):

```sql
-- BASE模式配置
ALTER SYSTEM SET synchronous_standby_names = '';  -- 基本可用
ALTER SYSTEM SET synchronous_commit = 'local';     -- 软状态
ALTER SYSTEM SET default_transaction_isolation = 'read committed';  -- 最
```

**错误**: 单引号不匹配

---

### 25-理论体系\CAP理论\CAP与分布式系统设计.md

**行 157** (sql):

```sql
-- 支付服务：CP模式
ALTER SYSTEM SET synchronous_standby_names = 'standby1,standby2';
ALTER SYSTEM SET synchronous_commit = 'remote_apply';

-- 订单服务：AP模式
ALTER SYSTEM SET synchronous_standby_names = '';
ALTE
```

**错误**: 单引号不匹配

---

**行 241** (sql):

```sql
-- AP模式配置
ALTER SYSTEM SET synchronous_standby_names = '';
ALTER SYSTEM SET synchronous_commit = 'local';
ALTER SYSTEM SET default_transaction_isolation = 'read committed';

```

**错误**: 单引号不匹配

---

### 25-理论体系\CAP理论\CAP定理完整定义与证明.md

**行 267** (sql):

```sql
-- 异步复制配置（AP模式）
ALTER SYSTEM SET synchronous_standby_names = '';
ALTER SYSTEM SET synchronous_commit = 'local';

-- AP模式特征：
-- 1. 主库立即提交，不等待备库
-- 2. 分区时，主库继续服务
-- 3. 保证高可用性，但可能数据不一致

```

**错误**: 单引号不匹配

---

**行 345** (sql):

```sql
-- 主库配置
synchronous_standby_names = ''
synchronous_commit = 'local'

-- AP模式特征：
-- ❌ 弱一致性：主库立即提交，备库可能延迟
-- ✅ 高可用性：分区时，主库继续服务
-- ✅ 分区容错：系统在网络分区时继续运行

```

**错误**: 单引号不匹配

---

**行 381** (sql):

```sql
-- 根据场景动态调整
-- 金融交易：使用CP模式
ALTER SYSTEM SET synchronous_standby_names = 'standby1,standby2';
ALTER SYSTEM SET synchronous_commit = 'remote_apply';

-- 日志写入：使用AP模式
ALTER SYSTEM SET synchronous_standby_
```

**错误**: 单引号不匹配

---

### 25-理论体系\CAP理论\CAP权衡决策框架.md

**行 425** (sql):

```sql
-- AP模式配置
ALTER SYSTEM SET synchronous_standby_names = '';
ALTER SYSTEM SET synchronous_commit = 'local';
ALTER SYSTEM SET default_transaction_isolation = 'read committed';

-- 特征：
-- ❌ 弱一致性：异步复制，可能延迟
```

**错误**: 单引号不匹配

---

**行 447** (sql):

```sql
-- AP模式配置（只读备库）
-- 主库：异步复制
ALTER SYSTEM SET synchronous_standby_names = '';

-- 备库：只读查询
SET default_transaction_read_only = on;

-- 特征：
-- ❌ 弱一致性：备库可能延迟
-- ✅ 高可用性：备库继续查询

```

**错误**: 单引号不匹配

---

**行 470** (sql):

```sql
-- AP模式配置
ALTER SYSTEM SET synchronous_standby_names = '';
ALTER SYSTEM SET synchronous_commit = 'local';

-- 特征：
-- ❌ 弱一致性：可能读到旧数据
-- ✅ 高可用性：高并发性能好

```

**错误**: 单引号不匹配

---

**行 486** (sql):

```sql
-- 异步复制（AP模式）
ALTER SYSTEM SET synchronous_standby_names = '';
ALTER SYSTEM SET synchronous_commit = 'local';

```

**错误**: 单引号不匹配

---

**行 641** (sql):

```sql
-- AP模式配置
ALTER SYSTEM SET synchronous_standby_names = '';
ALTER SYSTEM SET synchronous_commit = 'local';
ALTER SYSTEM SET default_transaction_isolation = 'read committed';

```

**错误**: 单引号不匹配

---

**行 676** (sql):

```sql
-- 动态切换到AP模式（提高可用性）
ALTER SYSTEM SET synchronous_standby_names = '';
SELECT pg_reload_conf();

-- 动态切换到CP模式（提高一致性）
ALTER SYSTEM SET synchronous_standby_names = 'standby1,standby2';
SELECT pg_reload_co
```

**错误**: 单引号不匹配; SELECT语句缺少FROM子句

---

### 25-理论体系\CAP理论\PACELC定理详解.md

**行 303** (sql):

```sql
-- 配置同步复制
ALTER SYSTEM SET synchronous_standby_names = 'ANY 2 (standby1, standby2, standby3)';
SELECT pg_reload_conf();

```

**错误**: SELECT语句缺少FROM子句

---

**行 333** (sql):

```sql
-- 配置异步复制（默认）
ALTER SYSTEM SET synchronous_standby_names = '';
SELECT pg_reload_conf();

```

**错误**: 单引号不匹配; SELECT语句缺少FROM子句

---

**行 361** (sql):

```sql
-- 配置混合模式
ALTER SYSTEM SET synchronous_standby_names = 'ANY 1 (standby1, standby2)';
SELECT pg_reload_conf();

```

**错误**: SELECT语句缺少FROM子句

---

### 25-理论体系\CAP理论\一致性模型详解.md

**行 252** (sql):

```sql
-- 异步复制实现最终一致性
ALTER SYSTEM SET synchronous_standby_names = '';
ALTER SYSTEM SET synchronous_commit = 'local';

-- 最终一致性特征：
-- ✅ 主库立即提交
-- ✅ 备库延迟同步
-- ✅ 最终所有节点一致

```

**错误**: 单引号不匹配

---

### 25-理论体系\CAP理论\分区容错实现机制.md

**行 209** (sql):

```sql
-- AP模式：异步复制
ALTER SYSTEM SET synchronous_standby_names = '';

-- 分区时：
-- 1. 主库继续服务
-- 2. WAL缓冲在复制槽中
-- 3. 分区恢复后自动同步
-- 4. 最终数据一致

```

**错误**: 单引号不匹配

---

**行 264** (sql):

```sql
-- AP模式：异步复制，最终一致性
ALTER SYSTEM SET synchronous_standby_names = '';
ALTER SYSTEM SET synchronous_commit = 'local';

```

**错误**: 单引号不匹配

---

**行 307** (sql):

```sql
-- 创建复制槽
SELECT pg_create_physical_replication_slot('standby1_slot');

-- 配置复制槽
primary_slot_name = 'standby1_slot'

```

**错误**: SELECT语句缺少FROM子句

---

### 25-理论体系\CAP理论\可用性量化与测量.md

**行 144** (sql):

```sql
-- 健康检查查询
SELECT 1;

-- 监控查询
SELECT
    pg_is_in_recovery() AS is_standby,
    pg_last_wal_receive_lsn() AS receive_lsn,
    pg_last_wal_replay_lsn() AS replay_lsn;

```

**错误**: SELECT语句缺少FROM子句

---

### 25-理论体系\PostgreSQL版本特性\pg17-vacuum-memory.md

**行 579** (sql):

```sql
-- 1. 设置autovacuum_work_mem
-- 建议：maintenance_work_mem的50-70%
ALTER SYSTEM SET autovacuum_work_mem = '2GB';

-- 2. 调整max_parallel_maintenance_workers
-- 根据新内存管理，可以适当增加
ALTER SYSTEM SET max_parallel_ma
```

**错误**: SELECT语句缺少FROM子句

---

### 25-理论体系\PostgreSQL版本特性\pg18-aio.md

**行 359** (sql):

```sql
-- PostgreSQL 18推荐配置

-- 1. 启用AIO（默认启用）
-- 检查AIO支持：
SHOW effective_io_concurrency;

-- 2. 设置AIO并发数
-- SSD环境：
ALTER SYSTEM SET effective_io_concurrency = 200;

-- NVMe环境：
ALTER SYSTEM SET effective_io_
```

**错误**: SELECT语句缺少FROM子句

---

### 25-理论体系\PostgreSQL版本特性\pg18-virtual-columns.md

**行 330** (sql):

```sql
-- 测试场景：查询1000万行

-- 存储列：
-- SELECT time：10秒
-- 直接读取total_amount

-- 虚拟列：
-- SELECT time：12秒（20%下降）
-- 需要计算total_amount

-- 下降：20%
-- 原因：计算开销

-- 优化：如果total_amount有索引
-- 虚拟列：10秒（与存储列相同）
-- 原因：索引存储计算值

```

**错误**: SELECT语句缺少FROM子句

---

### 25-理论体系\事务模型\两阶段提交深度分析.md

**行 537** (sql):

```sql
-- PostgreSQL跨数据库事务（使用dblink）

-- 创建dblink扩展
CREATE EXTENSION dblink;

-- 跨数据库事务
BEGIN;
-- 本地操作
UPDATE local_accounts SET balance = balance - 100 WHERE id = 1;

-- 远程操作
SELECT dblink_exec('remote_db',
```

**错误**: SELECT语句缺少FROM子句

---

### 25-理论体系\事务模型\最终一致性.md

**行 270** (sql):

```sql
-- PostgreSQL流复制配置
-- 主节点配置（postgresql.conf）
wal_level = replica
max_wal_senders = 10
max_replication_slots = 10

-- 从节点配置（postgresql.conf）
hot_standby = on
max_standby_streaming_delay = 30s

-- 复制槽配置
```

**错误**: SELECT语句缺少FROM子句

---

### 25-理论体系\形式化证明\MVCC可见性定理证明.md

**行 310** (sql):

```sql
   -- 查看当前事务快照
   SELECT txid_current_snapshot();
   -- 输出格式: xmin:xmax:xip_list
   -- 例如: 100:200:100,101,102

```

**错误**: SELECT语句缺少FROM子句

---

**行 401** (sql):

```sql
   -- PostgreSQL利用可见性传递性优化版本链遍历
   -- 如果版本v在快照s中可见，且在扩展快照s'中仍可见
   -- 则无需重新检查版本链

```

**错误**: 单引号不匹配

---

### 26-数据管理\代码示例改进完成报告-2025-01.md

**行 97** (sql):

```sql
-- JSONB处理（已改进）
CREATE TABLE IF NOT EXISTS json_data (...)
CREATE INDEX ... USING GIN (data)
INSERT INTO json_data (data, source_system) VALUES (...)
SELECT ... WHERE data @> '{"name": "test"}'::jsonb
```

**错误**: SELECT语句缺少FROM子句

---

### 26-数据管理\分区表管理\PostgreSQL分区表高级优化指南.md

**行 287** (sql):

```sql
-- 安装pg_partman
CREATE EXTENSION pg_partman;

-- 创建父表
CREATE TABLE events (
    event_id bigserial,
    event_time timestamptz NOT NULL,
    data jsonb
) PARTITION BY RANGE (event_time);

-- 配置pg_part
```

**错误**: SELECT语句缺少FROM子句

---

**行 324** (sql):

```sql
-- 创建分区管理函数
-- 创建月度分区函数（带完整错误处理）
CREATE OR REPLACE FUNCTION create_monthly_partition(
    p_parent_table text,
    p_partition_date date
)
RETURNS void
LANGUAGE plpgsql
AS $$
DECLARE
    v_partition_n
```

**错误**: 单引号不匹配

---

**行 445** (sql):

```sql
-- 删除旧分区函数
-- 删除旧分区函数（带完整错误处理）
CREATE OR REPLACE FUNCTION drop_old_partitions(
    p_parent_table text,
    p_retention_months int DEFAULT 12
)
RETURNS void
LANGUAGE plpgsql
AS $$
DECLARE
    v_partit
```

**错误**: 单引号不匹配

---

**行 558** (sql):

```sql
-- 归档分区函数
-- 归档旧分区函数（带完整错误处理）
CREATE OR REPLACE FUNCTION archive_old_partition(
    p_parent_table text,
    p_partition_name text,
    p_archive_schema text DEFAULT 'archive'
)
RETURNS void
LANGUAGE
```

**错误**: 单引号不匹配

---

**行 683** (sql):

```sql
-- 方案1：每个分区独立索引（默认）
CREATE INDEX ON orders_2024_01 (customer_id);
CREATE INDEX ON orders_2024_02 (customer_id);
-- ...

-- 方案2：全局索引（在父表上）
CREATE INDEX ON orders (customer_id);
-- PostgreSQL会自动在所有分区上创建
```

**错误**: 单引号不匹配

---

### 26-数据管理\分区表管理\分区表管理基础.md

**行 910** (sql):

```sql
   -- ✅ 好：自动创建新分区
   CREATE OR REPLACE FUNCTION create_monthly_partition(
       table_name TEXT,
       start_date DATE
   ) RETURNS void AS $$
   -- ... 函数实现
   $$ LANGUAGE plpgsql;

   -- 使用 pg_cro
```

**错误**: SELECT语句缺少FROM子句

---

### 26-数据管理\分区表管理\分区表维护.md

**行 177** (sql):

```sql
-- 安装pg_partman
CREATE EXTENSION pg_partman;

-- 配置自动分区
SELECT partman.create_parent(
    p_parent_table => 'public.orders',
    p_control => 'order_date',
    p_type => 'range',
    p_interval => 'mo
```

**错误**: SELECT语句缺少FROM子句

---

**行 196** (sql):

```sql
-- 安装pg_cron
CREATE EXTENSION pg_cron;

-- 定期创建新分区（每月1号）
SELECT cron.schedule(
    'create_monthly_partition',
    '0 0 1 * *',
    $$SELECT create_monthly_partition('orders', CURRENT_DATE)$$
);

-- 定
```

**错误**: SELECT语句缺少FROM子句

---

### 26-数据管理\基础管理\序列管理.md

**行 299** (sql):

```sql
-- 获取下一个值（带错误处理）
DO $$
DECLARE
    next_val BIGINT;
BEGIN
    BEGIN
        next_val := nextval('user_id_seq');
        RAISE NOTICE '下一个序列值: %', next_val;
    EXCEPTION
        WHEN undefined_object
```

**错误**: SELECT语句缺少FROM子句

---

**行 723** (sql):

```sql
   -- ❌ 不好：假设序列值可以回滚
   BEGIN;
   SELECT nextval('order_id_seq');  -- 返回100
   ROLLBACK;  -- 序列值不会回滚，仍然是100
   SELECT nextval('order_id_seq');  -- 返回101，不是100

   -- ✅ 好：理解序列值不回滚的特性
   -- 序列值在事务提交前不会回
```

**错误**: SELECT语句缺少FROM子句

---

### 26-数据管理\基础管理\视图与物化视图.md

**行 482** (sql):

```sql
-- 启用 pg_cron
CREATE EXTENSION IF NOT EXISTS pg_cron;

-- 每小时刷新物化视图
SELECT cron.schedule(
    'refresh-user-order-summary',
    '0 * * * *',  -- 每小时
    $$REFRESH MATERIALIZED VIEW CONCURRENTLY user_o
```

**错误**: SELECT语句缺少FROM子句

---

**行 953** (sql):

```sql
   -- ✅ 好：使用pg_cron自动刷新
   CREATE EXTENSION IF NOT EXISTS pg_cron;

   SELECT cron.schedule(
       'refresh-daily-sales',
       '0 1 * * *',  -- 每天凌晨1点刷新
       $$REFRESH MATERIALIZED VIEW CONCURREN
```

**错误**: SELECT语句缺少FROM子句

---

**行 1054** (sql):

```sql
   -- ❌ 不好：刷新频率过高，浪费资源
   -- 每分钟刷新，但数据变化不频繁
   SELECT cron.schedule('refresh', '* * * * *', 'REFRESH MATERIALIZED VIEW mv');

   -- ✅ 好：根据数据变化频率调整刷新策略
   -- 数据每小时变化，每小时刷新一次
   SELECT cron.schedule('re
```

**错误**: SELECT语句缺少FROM子句

---

### 26-数据管理\数据仓库\ETL流程设计.md

**行 172** (sql):

```sql
-- ETL转换阶段：数据清洗

-- 1. 添加业务键列（用于去重）
ALTER TABLE staging_area
ADD COLUMN IF NOT EXISTS business_key VARCHAR(200) GENERATED ALWAYS AS (customer_name || '|' || COALESCE(email, '')) STORED;

-- 2. 清洗NULL值
```

**错误**: 单引号不匹配

---

### 26-数据管理\数据仓库\数据仓库最佳实践.md

**行 169** (sql):

```sql
-- 创建只读用户
CREATE USER dw_readonly WITH PASSWORD 'strong_password';
GRANT SELECT ON ALL TABLES IN SCHEMA dw TO dw_readonly;

```

**错误**: SELECT语句缺少FROM子句

---

### 26-数据管理\数据仓库\星型雪花模型.md

**行 555** (sql):

```sql
-- 星型模式存储空间
SELECT
    pg_size_pretty(pg_total_relation_size('dim_product')) AS star_storage;

-- 雪花型模式存储空间
SELECT
    pg_size_pretty(
        pg_total_relation_size('dim_product') +
        pg_total_
```

**错误**: SELECT语句缺少FROM子句

---

### 26-数据管理\数据湖\元数据管理.md

**行 182** (sql):

```sql
-- 定期更新元数据
SELECT cron.schedule(
    'update-metadata',
    '0 2 * * *',
    'SELECT collect_table_metadata();'
);

```

**错误**: SELECT语句缺少FROM子句

---

### 26-数据管理\数据湖\半结构化数据处理.md

**行 428** (sql):

```sql
-- JSONB验证函数（带错误处理和性能测试）
CREATE OR REPLACE FUNCTION validate_jsonb_schema(
    p_data JSONB,
    p_schema JSONB
)
RETURNS BOOLEAN AS $$
DECLARE
    required_field TEXT;
BEGIN
    -- 检查必需字段
    FOR req
```

**错误**: SELECT语句缺少FROM子句

---

### 26-数据管理\数据湖\数据湖架构设计.md

**行 120** (sql):

```sql
-- 创建只读用户
CREATE USER lake_reader WITH PASSWORD 'password';
GRANT SELECT ON lake_unified TO lake_reader;

```

**错误**: SELECT语句缺少FROM子句

---

**行 312** (sql):

```sql
-- 创建数据湖角色
CREATE ROLE lake_admin;
CREATE ROLE lake_analyst;
CREATE ROLE lake_reader;

-- 授予权限
-- 管理员：所有权限
GRANT ALL ON lake_raw, lake_processed, fact_events TO lake_admin;

-- 分析师：读取处理层和应用层
GRANT SEL
```

**错误**: SELECT语句缺少FROM子句

---

**行 341** (sql):

```sql
-- 启用行级安全
ALTER TABLE lake_raw ENABLE ROW LEVEL SECURITY;

-- 创建安全策略
CREATE POLICY lake_raw_access_policy ON lake_raw
FOR SELECT
TO lake_analyst
USING (
    source_system = current_setting('app.source
```

**错误**: SELECT语句缺少FROM子句

---

### 26-数据管理\数据管理模型\12.01-数据血缘-why_where_how形式语义.md

**行 242** (sql):

```sql
-- 1. 数据对象表（实体）
CREATE TABLE data_objects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    object_type VARCHAR(50) NOT NULL,  -- 'table', 'column', 'view', 'function'
    schema_name VARCHAR(1
```

**错误**: SELECT语句缺少FROM子句

---

### 26-数据管理\数据管理模型\12.03-数据库数据湖模型-半结构化数据与元数据管理的形式化.md

**行 367** (sql):

```sql
-- 场景：元数据驱动的数据发现
-- 1. 创建全文搜索索引
CREATE INDEX idx_catalog_fulltext ON data_lake_catalog
USING GIN(to_tsvector('english',
    COALESCE(schema_definition::TEXT, '') || ' ' ||
    COALESCE(classification,
```

**错误**: 单引号不匹配

---

### 26-数据管理\数据管理模型\12.06-数据库数据血缘模型-数据溯源与影响分析的形式化.md

**行 215** (sql):

```sql
-- 场景：企业数据血缘系统
-- 1. 创建血缘表
CREATE TABLE data_lineage (
    lineage_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_object_id UUID NOT NULL,
    target_object_id UUID NOT NULL,
    transforma
```

**错误**: SELECT语句缺少FROM子句

---

### 26-数据管理\数据编排模型\13.04-数据库数据编排模型-编排验证与形式化验证的形式化.md

**行 417** (sql):

```sql
-- 使用pg_tla扩展进行TLA+验证
CREATE EXTENSION IF NOT EXISTS pg_tla;

-- 创建TLA+规范
CREATE TABLE tla_specifications (
    spec_id UUID PRIMARY KEY,
    spec_name VARCHAR(200) NOT NULL,
    tla_code TEXT NOT NUL
```

**错误**: SELECT语句缺少FROM子句

---

**行 455** (sql):

```sql
-- SQLite 3.45: 使用触发器进行基本验证
CREATE TRIGGER validate_orchestration_state
BEFORE UPDATE ON orchestration_states
FOR EACH ROW
WHEN NEW.state NOT IN ('pending', 'running', 'completed', 'failed')
BEGIN

```

**错误**: SELECT语句缺少FROM子句

---

### 26-数据管理\数据编排模型\13.07-数据库数据编排模型-编排安全与访问控制的形式化.md

**行 356** (sql):

```sql
-- 场景：RBAC访问控制
-- 1. 创建角色
CREATE ROLE data_engineer;
CREATE ROLE data_analyst;
CREATE ROLE data_admin;

-- 2. 分配权限
INSERT INTO orchestration_permissions (orchestration_id, role_name, permission_type)

```

**错误**: SELECT语句缺少FROM子句

---

**行 444** (sql):

```sql
-- SQLite 3.45: 基本权限控制
-- 1. 使用触发器实现基本访问控制
CREATE TRIGGER check_orchestration_access
BEFORE INSERT OR UPDATE OR DELETE ON orchestration_executions
FOR EACH ROW
BEGIN
    -- 检查用户权限（简化实现）
    SELECT CAS
```

**错误**: SELECT语句缺少FROM子句

---

### 26-数据管理\数据编排模型\13.12-数据库数据编排模型-编排创新与前沿技术的形式化.md

**行 500** (sql):

```sql
-- 场景：区块链集成
-- 1. 区块链记录表
CREATE TABLE orchestration_blockchain_logs (
    log_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    execution_id UUID NOT NULL,
    block_hash VARCHAR(64),
    previous_ha
```

**错误**: 单引号不匹配

---

### 26-数据管理\数据编排模型\13.14-数据库数据编排模型-编排总结与展望的形式化.md

**行 587** (sql):

```sql
-- 场景：去中心化编排
-- 1. 联邦编排节点
CREATE TABLE federation_nodes (
    node_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    node_name VARCHAR(100) NOT NULL,
    node_endpoint VARCHAR(255),
    node_type VAR
```

**错误**: SELECT语句缺少FROM子句

---

### 28-知识图谱\01-Apache-AGE完整深化指南-v2.md

**行 1047** (python):

```python
from openai import OpenAI
import psycopg2
from typing import Dict, List
import json

class Text2CypherGenerator:
    """Text-to-Cypher生成器"""

    def __init__(self, conn, graph_name: str, openai_api_k
```

**错误**: 语法错误: unterminated string literal (detected at line 94) (行 94)

---

### 28-知识图谱\01-Apache-AGE完整深化指南.md

**行 89** (sql):

```sql
-- 创建扩展
CREATE EXTENSION age;

-- 加载AGE
LOAD 'age';

-- 设置搜索路径
SET search_path = ag_catalog, "$user", public;

-- 创建图
SELECT create_graph('social_network');

```

**错误**: SELECT语句缺少FROM子句

---

**行 347** (sql):

```sql
-- 为节点属性创建索引
SELECT create_vlabel('social_network', 'Person');

CREATE INDEX ON social_network."Person"
USING btree ((properties->>'name'));

CREATE INDEX ON social_network."Person"
USING btree ((prop
```

**错误**: SELECT语句缺少FROM子句

---

### 28-知识图谱\01-知识图谱Schema.md

**行 105** (sql):

```sql
-- 概念版本管理表
CREATE TABLE IF NOT EXISTS concept_versions (
    version_id SERIAL PRIMARY KEY,
    concept_id INT REFERENCES concepts(concept_id),
    version_number VARCHAR(20),
    description TEXT,

```

**错误**: SELECT语句缺少FROM子句

---

**行 512** (sql):

```sql
-- PostgreSQL 18异步I/O配置
ALTER SYSTEM SET io_direct = 'data';
ALTER SYSTEM SET io_combine_limit = '256kB';

-- 重启后生效
SELECT pg_reload_conf();

-- 性能提升:
-- 图查询性能: +20-25%
-- 图构建性能: +30-35%

```

**错误**: SELECT语句缺少FROM子句

---

### 28-知识图谱\02-RDF-SPARQL-OWL完整指南.md

**行 478** (sql):

```sql
-- 规则：对称属性
-- 如果 friendOf 是对称的，且 Alice friendOf Bob，则 Bob friendOf Alice

-- 推理对称属性函数（带完整错误处理）
CREATE FUNCTION infer_symmetric_property(p_property_uri TEXT)
RETURNS VOID
LANGUAGE plpgsql
AS $$
DECLARE
```

**错误**: 单引号不匹配

---

### 28-知识图谱\03-PostGIS完整深化指南.md

**行 106** (sql):

```sql
-- 点（Point）
SELECT ST_GeomFromText('POINT(116.3912 39.9067)', 4326);

-- 线（LineString）
SELECT ST_GeomFromText('LINESTRING(116.3 39.9, 116.4 39.95, 116.5 40.0)', 4326);

-- 多边形（Polygon）
SELECT ST_GeomF
```

**错误**: SELECT语句缺少FROM子句

---

### 28-知识图谱\04-TimescaleDB完整深化指南.md

**行 94** (sql):

```sql
-- 创建普通表
CREATE TABLE sensor_data (
    time TIMESTAMPTZ NOT NULL,
    sensor_id INT NOT NULL,
    temperature DOUBLE PRECISION,
    humidity DOUBLE PRECISION,
    pressure DOUBLE PRECISION
);

-- 转换为
```

**错误**: SELECT语句缺少FROM子句

---

**行 517** (sql):

```sql
-- 查询性能分析函数
CREATE OR REPLACE FUNCTION analyze_timescaledb_query(
    p_query_text TEXT
)
RETURNS TABLE (
    plan_node TEXT,
    hypertable_name TEXT,
    chunk_count INT,
    estimated_rows BIGINT,

```

**错误**: SELECT语句缺少FROM子句

---

### 28-知识图谱\07-LLM与知识图谱深度集成.md

**行 191** (python):

```python
import json
from typing import Dict, List, Optional
from openai import OpenAI

class CypherPromptTemplate:
    """Text-to-Cypher Prompt模板"""

    @staticmethod
    def get_system_prompt(schema: Dict)
```

**错误**: 语法错误: unterminated triple-quoted f-string literal (detected at line 28) (行 11)

---

### 28-知识图谱\07-LangChain深度集成完整指南.md

**行 15** (python):

```python
LangChain + PostgreSQL 18 + pgvector + Apache AGE
├─ LLM: OpenAI GPT-4 / Claude / 本地模型
├─ 向量数据库: pgvector
├─ 图数据库: Apache AGE
└─ 关系数据库: PostgreSQL 18

```

**错误**: 语法错误: invalid character '├' (U+251C) (行 2)

---

### 28-知识图谱\08-向量检索性能优化实战.md

**行 392** (sql):

```sql
-- PostgreSQL 18异步I/O配置
ALTER SYSTEM SET io_direct = 'data';
ALTER SYSTEM SET io_combine_limit = '256kB';

-- 重启后生效
SELECT pg_reload_conf();

-- 性能提升:
-- 向量索引扫描: +20-25%
-- 批量向量检索: +15-20%

```

**错误**: SELECT语句缺少FROM子句

---

### 28-知识图谱\11-LangChain企业知识库完整案例.md

**行 601** (python):

```python
import pytest
import requests

BASE_URL = "http://localhost:8000"

def test_upload_document():
    """测试文档上传"""

    with open('test.pdf', 'rb') as f:
        files = {'file': f}
        data = {

```

**错误**: 语法错误: invalid syntax (行 61)

---

### 28-知识图谱\14-知识图谱动态维护与更新完整指南.md

**行 897** (sql):

```sql
-- 查询特定版本的知识图谱状态
-- 查询指定版本的知识图谱函数（带完整错误处理）
CREATE OR REPLACE FUNCTION query_kg_at_version(p_version_id INTEGER)
RETURNS TABLE (
    entity_id TEXT,
    entity_name TEXT,
    entity_type TEXT,
    prop
```

**错误**: 单引号不匹配

---

### 29-社区生态\扩展生态全景图.md

**行 356** (sql):

```sql
-- 扩展评估工具（带错误处理和性能测试）
DO $$
DECLARE
    ext_record RECORD;
    assessment_record RECORD;
BEGIN
    RAISE NOTICE '=== PostgreSQL扩展评估 ===';

    FOR ext_record IN
        SELECT
            extname,

```

**错误**: 单引号不匹配

---

### 29-社区生态\社区贡献案例.md

**行 167** (sql):

```sql
-- 案例：添加测试用例
-- 功能：测试format_bytes函数
-- 贡献者：社区测试者

BEGIN;
SELECT plan(5);

SELECT is(
    format_bytes(1024),
    '1.00 KB',
    '1024 bytes should format as 1.00 KB'
);

SELECT is(
    format_bytes(10
```

**错误**: SELECT语句缺少FROM子句

---

### 30-性能调优\PostgreSQL-18-自动化运维与自我监测\02-自动化性能调优\01-异步I-O支持.md

**行 254** (sql):

```sql
-- PostgreSQL 18 异步I/O配置检查（带错误处理和性能测试）
DO $$
DECLARE
    pg_version int;
    io_method text;
    max_io_workers int;
    maintenance_io_workers int;
    kernel_version text;
BEGIN
    BEGIN
        --
```

**错误**: 单引号不匹配

---

### 30-性能调优\PostgreSQL-18-自动化运维与自我监测\02-自动化性能调优\03-并行查询追踪.md

**行 498** (sql):

```sql
   SELECT current_setting('server_version_num')::int >= 180000;

```

**错误**: SELECT语句缺少FROM子句

---

### 30-性能调优\PostgreSQL-18-自动化运维与自我监测\02-自动化性能调优\04-EXPLAIN增强.md

**行 223** (sql):

```sql
-- PostgreSQL 18 EXPLAIN增强功能（带错误处理和性能测试）
DO $$
DECLARE
    explain_result text;
BEGIN
    BEGIN
        -- 检查PostgreSQL版本
        IF (SELECT current_setting('server_version_num')::int) < 180000 THEN

```

**错误**: 单引号不匹配

---

**行 492** (sql):

```sql
   -- 第一步：查看执行计划（不执行）
   EXPLAIN SELECT ...;

   -- 第二步：查看详细计划（不执行）
   EXPLAIN (VERBOSE) SELECT ...;

   -- 第三步：实际执行并分析（谨慎使用）
   EXPLAIN (ANALYZE, BUFFERS, VERBOSE, SETTINGS) SELECT ...;

```

**错误**: SELECT语句缺少FROM子句

---

### 30-性能调优\PostgreSQL-18-自动化运维与自我监测\02-自动化性能调优\06-自动索引优化.md

**行 209** (sql):

```sql
-- PostgreSQL 18 自动索引优化系统（带错误处理和性能测试）
DO $$
DECLARE
    missing_index RECORD;
    index_count int := 0;
BEGIN
    BEGIN
        RAISE NOTICE '=== PostgreSQL 18自动索引优化系统 ===';
        RAISE NOTICE '扫描缺失
```

**错误**: 单引号不匹配

---

### 30-性能调优\PostgreSQL-18-自动化运维与自我监测\02-自动化性能调优\07-自动统计信息更新.md

**行 195** (sql):

```sql
-- PostgreSQL 18 自动统计信息更新系统（带错误处理和性能测试）
DO $$
DECLARE
    table_stats RECORD;
    update_count int := 0;
BEGIN
    BEGIN
        RAISE NOTICE '=== PostgreSQL 18自动统计信息更新系统 ===';
        RAISE NOTICE '分
```

**错误**: 单引号不匹配

---

### 30-性能调优\PostgreSQL-18-自动化运维与自我监测\02-自动化性能调优\08-自动VACUUM优化.md

**行 64** (sql):

```sql
-- PostgreSQL 18 自动VACUUM优化系统（带错误处理和性能测试）
DO $$
DECLARE
    vacuum_stats RECORD;
    vacuum_count int := 0;
BEGIN
    BEGIN
        RAISE NOTICE '=== PostgreSQL 18自动VACUUM优化系统 ===';
        RAISE NOTI
```

**错误**: 单引号不匹配

---

### 30-性能调优\PostgreSQL-18-自动化运维与自我监测\03-自我监测系统\01-pg_stat_io增强监控.md

**行 200** (sql):

```sql
-- PostgreSQL 18 pg_stat_io增强监控（带错误处理和性能测试）
DO $$
DECLARE
    io_stats RECORD;
    total_read_bytes bigint := 0;
    total_write_bytes bigint := 0;
    total_reads bigint := 0;
    total_writes bigint
```

**错误**: 单引号不匹配

---

**行 308** (sql):

```sql
-- 查询I/O统计（PostgreSQL 18增强，带错误处理和性能测试）
DO $$
DECLARE
    io_record RECORD;
BEGIN
    BEGIN
        -- 检查PostgreSQL版本
        IF (SELECT current_setting('server_version_num')::int) < 180000 THEN

```

**错误**: 单引号不匹配

---

**行 377** (sql):

```sql
-- 分析I/O吞吐量（带错误处理和性能测试）
DO $$
DECLARE
    throughput_record RECORD;
    efficiency_record RECORD;
BEGIN
    BEGIN
        -- 检查PostgreSQL版本
        IF (SELECT current_setting('server_version_num')::in
```

**错误**: 单引号不匹配

---

**行 532** (sql):

```sql
   -- 检查PostgreSQL版本（带错误处理）
   DO $$
   BEGIN
       BEGIN
           IF (SELECT current_setting('server_version_num')::int) < 180000 THEN
               RAISE WARNING 'pg_stat_io视图需要PostgreSQL 18+，当前
```

**错误**: SELECT语句缺少FROM子句

---

### 30-性能调优\PostgreSQL-18-自动化运维与自我监测\03-自我监测系统\02-后端I-O追踪.md

**行 342** (sql):

```sql
   -- 检查PostgreSQL版本（带错误处理）
   DO $$
   BEGIN
       BEGIN
           IF (SELECT current_setting('server_version_num')::int) < 180000 THEN
               RAISE WARNING '后端I/O追踪需要PostgreSQL 18+，当前版本: %
```

**错误**: SELECT语句缺少FROM子句

---

### 30-性能调优\PostgreSQL-18-自动化运维与自我监测\03-自我监测系统\03-连接性能监测.md

**行 156** (sql):

```sql
-- PostgreSQL 18 连接性能监测（带错误处理和性能测试）
DO $$
DECLARE
    connection_stats RECORD;
    connection_log_config text;
BEGIN
    BEGIN
        -- 检查PostgreSQL版本
        IF (SELECT current_setting('server_vers
```

**错误**: 单引号不匹配

---

**行 414** (sql):

```sql
   SELECT current_setting('server_version_num')::int >= 180000;

```

**错误**: SELECT语句缺少FROM子句

---

### 30-性能调优\PostgreSQL-18-自动化运维与自我监测\03-自我监测系统\04-WAL性能监测.md

**行 159** (sql):

```sql
-- PostgreSQL 18 WAL性能监测（带错误处理和性能测试）
DO $$
DECLARE
    wal_stats RECORD;
    checkpoint_stats RECORD;
BEGIN
    BEGIN
        -- 检查PostgreSQL版本
        IF (SELECT current_setting('server_version_num')
```

**错误**: 单引号不匹配

---

**行 560** (sql):

```sql
   SELECT current_setting('server_version_num')::int >= 180000;

```

**错误**: SELECT语句缺少FROM子句

---

### 30-性能调优\PostgreSQL-18-自动化运维与自我监测\04-自动化诊断\01-自动慢查询检测.md

**行 206** (sql):

```sql
-- PostgreSQL 18 自动慢查询检测系统（带错误处理和性能测试）
DO $$
DECLARE
    slow_query RECORD;
    slow_count int := 0;
    slow_threshold interval := '1 second';  -- 慢查询阈值
BEGIN
    BEGIN
        -- 检查pg_stat_statement
```

**错误**: 单引号不匹配

---

**行 412** (sql):

```sql
   SELECT current_setting('server_version_num')::int >= 180000;

```

**错误**: SELECT语句缺少FROM子句

---

### 30-性能调优\PostgreSQL-18-自动化运维与自我监测\04-自动化诊断\02-自动锁等待检测.md

**行 158** (sql):

```sql
-- PostgreSQL 18 自动锁等待检测系统（带错误处理和性能测试）
DO $$
DECLARE
    lock_wait RECORD;
    wait_count int := 0;
BEGIN
    BEGIN
        RAISE NOTICE '=== PostgreSQL 18自动锁等待检测系统 ===';
        RAISE NOTICE '扫描锁等待..
```

**错误**: 单引号不匹配

---

### 30-性能调优\PostgreSQL-18-自动化运维与自我监测\05-自动化运维脚本\01-自动化健康检查.md

**行 50** (sql):

```sql
-- PostgreSQL 18 自动化健康检查系统（带错误处理和性能测试）
DO $$
DECLARE
    health_status text := '健康';
    health_issues text[] := ARRAY[]::text[];
    check_result RECORD;
BEGIN
    BEGIN
        RAISE NOTICE '=== Pos
```

**错误**: 单引号不匹配

---

### 30-性能调优\PostgreSQL-18-自动化运维与自我监测\05-自动化运维脚本\03-自动化告警系统.md

**行 51** (sql):

```sql
-- PostgreSQL 18 自动化告警系统（带错误处理和性能测试）
DO $$
DECLARE
    alert_count int := 0;
    alert_level text;
    alert_message text;
BEGIN
    BEGIN
        RAISE NOTICE '=== PostgreSQL 18自动化告警系统 ===';

```

**错误**: 单引号不匹配

---

### 30-性能调优\PostgreSQL-18-自动化运维与自我监测\08-性能调优案例\01-高并发OLTP系统优化.md

**行 94** (sql):

```sql
ALTER SYSTEM SET io_method = 'worker';
ALTER SYSTEM SET max_io_workers = 10;
ALTER SYSTEM SET maintenance_io_workers = 4;
SELECT pg_reload_conf();

```

**错误**: SELECT语句缺少FROM子句

---

**行 103** (sql):

```sql
ALTER SYSTEM SET autovacuum_max_workers = 6;
ALTER SYSTEM SET autovacuum_vacuum_scale_factor = 0.05;
ALTER SYSTEM SET autovacuum_analyze_scale_factor = 0.05;
SELECT pg_reload_conf();

```

**错误**: SELECT语句缺少FROM子句

---

### 30-性能调优\PostgreSQL-18-自动化运维与自我监测\08-性能调优案例\02-数据仓库OLAP系统优化.md

**行 76** (sql):

```sql
ALTER SYSTEM SET io_method = 'io_uring';  -- 如果系统支持
ALTER SYSTEM SET max_io_workers = 20;
ALTER SYSTEM SET maintenance_io_workers = 8;
SELECT pg_reload_conf();

```

**错误**: SELECT语句缺少FROM子句

---

**行 85** (sql):

```sql
ALTER SYSTEM SET max_parallel_workers_per_gather = 8;
ALTER SYSTEM SET max_parallel_workers = 16;
ALTER SYSTEM SET max_parallel_maintenance_workers = 8;
SELECT pg_reload_conf();

```

**错误**: SELECT语句缺少FROM子句

---

**行 94** (sql):

```sql
ALTER SYSTEM SET work_mem = '256MB';
SELECT pg_reload_conf();

```

**错误**: SELECT语句缺少FROM子句

---

**行 101** (sql):

```sql
EXPLAIN (ANALYZE, BUFFERS, VERBOSE, SETTINGS, TIMING)
SELECT /* 复杂分析查询 */;

```

**错误**: SELECT语句缺少FROM子句

---

### 30-性能调优\PostgreSQL-18-自动化运维与自我监测\10-最佳实践\01-推荐做法与注意事项.md

**行 144** (sql):

```sql
EXPLAIN (ANALYZE, BUFFERS, VERBOSE, SETTINGS, TIMING)
SELECT /* 查询语句 */;

```

**错误**: SELECT语句缺少FROM子句

---

**行 195** (sql):

```sql
-- 每周清理一次
SELECT pg_stat_statements_reset();

```

**错误**: SELECT语句缺少FROM子句

---

### 30-性能调优\PostgreSQL-18-自动化运维与自我监测\12-监控与诊断/README.md

**行 307** (sql):

```sql
-- PostgreSQL 18 EXPLAIN增强功能（带错误处理和性能测试）
DO $$
DECLARE
    explain_result text;
BEGIN
    BEGIN
        -- 检查PostgreSQL版本
        IF (SELECT current_setting('server_version_num')::int) < 180000 THEN

```

**错误**: 单引号不匹配

---

**行 530** (sql):

```sql
-- PostgreSQL 18 自动索引优化系统（带错误处理和性能测试）
DO $$
DECLARE
    missing_index RECORD;
    index_count int := 0;
BEGIN
    BEGIN
        RAISE NOTICE '=== PostgreSQL 18自动索引优化系统 ===';
        RAISE NOTICE '扫描缺失
```

**错误**: 单引号不匹配

---

**行 609** (sql):

```sql
-- PostgreSQL 18 自动统计信息更新系统（带错误处理和性能测试）
DO $$
DECLARE
    table_stats RECORD;
    update_count int := 0;
BEGIN
    BEGIN
        RAISE NOTICE '=== PostgreSQL 18自动统计信息更新系统 ===';
        RAISE NOTICE '分
```

**错误**: 单引号不匹配

---

**行 676** (sql):

```sql
-- PostgreSQL 18 自动VACUUM优化系统（带错误处理和性能测试）
DO $$
DECLARE
    vacuum_stats RECORD;
    vacuum_count int := 0;
BEGIN
    BEGIN
        RAISE NOTICE '=== PostgreSQL 18自动VACUUM优化系统 ===';
        RAISE NOTI
```

**错误**: 单引号不匹配

---

**行 748** (sql):

```sql
-- PostgreSQL 18 pg_upgrade优化功能说明（带错误处理和性能测试）
DO $$
DECLARE
    pg_version int;
BEGIN
    BEGIN
        SELECT current_setting('server_version_num')::int INTO pg_version;

        RAISE NOTICE '=== Po
```

**错误**: SELECT语句缺少FROM子句

---

**行 843** (sql):

```sql
-- PostgreSQL 18 pg_stat_io增强监控（带错误处理和性能测试）
DO $$
DECLARE
    io_stats RECORD;
    total_read_bytes bigint := 0;
    total_write_bytes bigint := 0;
    total_reads bigint := 0;
    total_writes bigint
```

**错误**: 单引号不匹配

---

**行 1000** (sql):

```sql
-- PostgreSQL 18 连接性能监测（带错误处理和性能测试）
DO $$
DECLARE
    connection_stats RECORD;
    connection_log_config text;
BEGIN
    BEGIN
        -- 检查PostgreSQL版本
        IF (SELECT current_setting('server_vers
```

**错误**: 单引号不匹配

---

**行 1114** (sql):

```sql
-- PostgreSQL 18 WAL性能监测（带错误处理和性能测试）
DO $$
DECLARE
    wal_stats RECORD;
    checkpoint_stats RECORD;
BEGIN
    BEGIN
        -- 检查PostgreSQL版本
        IF (SELECT current_setting('server_version_num')
```

**错误**: 单引号不匹配

---

**行 1227** (sql):

```sql
-- PostgreSQL 18 自动慢查询检测系统（带错误处理和性能测试）
DO $$
DECLARE
    slow_query RECORD;
    slow_count int := 0;
    slow_threshold interval := '1 second';  -- 慢查询阈值
BEGIN
    BEGIN
        -- 检查pg_stat_statement
```

**错误**: 单引号不匹配

---

**行 1296** (sql):

```sql
-- PostgreSQL 18 自动锁等待检测系统（带错误处理和性能测试）
DO $$
DECLARE
    lock_wait RECORD;
    wait_count int := 0;
BEGIN
    BEGIN
        RAISE NOTICE '=== PostgreSQL 18自动锁等待检测系统 ===';
        RAISE NOTICE '扫描锁等待..
```

**错误**: 单引号不匹配

---

**行 1471** (sql):

```sql
-- PostgreSQL 18 自动化健康检查系统（带错误处理和性能测试）
DO $$
DECLARE
    health_status text := '健康';
    health_issues text[] := ARRAY[]::text[];
    check_result RECORD;
BEGIN
    BEGIN
        RAISE NOTICE '=== Pos
```

**错误**: 单引号不匹配

---

**行 1710** (sql):

```sql
-- PostgreSQL 18 自动化告警系统（带错误处理和性能测试）
DO $$
DECLARE
    alert_count int := 0;
    alert_level text;
    alert_message text;
BEGIN
    BEGIN
        RAISE NOTICE '=== PostgreSQL 18自动化告警系统 ===';

```

**错误**: 单引号不匹配

---

**行 3269** (sql):

```sql
-- 1. 启用PostgreSQL 18异步I/O
ALTER SYSTEM SET io_method = 'worker';
ALTER SYSTEM SET max_io_workers = 10;
ALTER SYSTEM SET maintenance_io_workers = 4;
SELECT pg_reload_conf();

-- 2. 优化autovacuum配置（Post
```

**错误**: SELECT语句缺少FROM子句

---

**行 3335** (sql):

```sql
-- 1. 启用PostgreSQL 18异步I/O（io_uring）
ALTER SYSTEM SET io_method = 'io_uring';  -- 如果系统支持
ALTER SYSTEM SET max_io_workers = 20;
ALTER SYSTEM SET maintenance_io_workers = 8;
SELECT pg_reload_conf();

--
```

**错误**: SELECT语句缺少FROM子句

---

### 30-性能调优\PostgreSQL性能调优整合完整指南.md

**行 1154** (sql):

```sql
-- 创建扩展
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- 配置
ALTER SYSTEM SET pg_stat_statements.max = 10000;
ALTER SYSTEM SET pg_stat_statements.track = all;
ALTER SYSTEM SET pg_stat_statements.
```

**错误**: SELECT语句缺少FROM子句

---

### 30-性能调优\参数调优.md

**行 57** (sql):

```sql
-- PostgreSQL内存参数配置（带错误处理和性能测试）
DO $$
DECLARE
    total_mem_gb numeric := 64;  -- 系统总内存（GB）
    shared_buffers_gb numeric;
    effective_cache_size_gb numeric;
    work_mem_mb numeric;
    maintenance
```

**错误**: 单引号不匹配

---

**行 202** (sql):

```sql
-- PostgreSQL连接参数配置（带错误处理和性能测试）
DO $$
DECLARE
    total_mem_gb numeric := 64;  -- 系统总内存（GB）
    max_connections int;
    superuser_reserved_connections int;
    work_mem_mb numeric;
    shared_buffers
```

**错误**: 单引号不匹配

---

**行 305** (sql):

```sql
-- PostgreSQL查询优化参数配置（带错误处理和性能测试）
DO $$
DECLARE
    storage_type text := 'SSD';  -- 存储类型（SSD/NVMe/HDD）
    random_page_cost numeric;
    effective_io_concurrency int;
    maintenance_io_concurrency in
```

**错误**: 单引号不匹配

---

**行 369** (sql):

```sql
-- PostgreSQL并行查询参数配置（带错误处理和性能测试）
DO $$
DECLARE
    cpu_cores int := 8;  -- CPU核心数
    max_parallel_workers_per_gather int;
    max_parallel_workers int;
    max_worker_processes int;
    parallel_tup
```

**错误**: 单引号不匹配

---

**行 430** (sql):

```sql
-- PostgreSQL自动清理参数配置（带错误处理和性能测试）
DO $$
DECLARE
    cpu_cores int := 8;  -- CPU核心数
    autovacuum_max_workers int;
    autovacuum_naptime_sec int;
    autovacuum_vacuum_cost_delay_ms int;
    autovacu
```

**错误**: 单引号不匹配

---

**行 490** (sql):

```sql
-- PostgreSQL检查点参数配置（带错误处理和性能测试）
DO $$
DECLARE
    total_mem_gb numeric := 64;  -- 系统总内存（GB）
    checkpoint_timeout_min int;
    checkpoint_completion_target numeric;
    max_wal_size_gb numeric;

```

**错误**: 单引号不匹配

---

### 30-性能调优\性能调优方法论.md

**行 105** (sql):

```sql
-- 建立性能基线（带错误处理和性能测试）
DO $$
DECLARE
    baseline_record RECORD;
BEGIN
    RAISE NOTICE '开始建立性能基线...';

    -- 记录系统配置
    RAISE NOTICE '=== 系统配置基线 ===';
    FOR baseline_record IN
        SELECT name,
```

**错误**: 单引号不匹配

---

**行 728** (sql):

```sql
-- PostgreSQL 18 自动参数调优（带错误处理和性能测试）
DO $$
DECLARE
    current_workload text;
    recommended_config text;
BEGIN
    BEGIN
        -- 分析当前工作负载
        SELECT
            CASE
                WHEN (SELE
```

**错误**: 单引号不匹配

---

### 30-性能调优\数据库级调优.md

**行 57** (sql):

```sql
-- PostgreSQL连接参数配置（带错误处理和性能测试）
DO $$
DECLARE
    total_mem_gb numeric := 64;  -- 系统总内存（GB）
    max_connections int;
    superuser_reserved_connections int;
    shared_buffers_gb numeric;
    work_mem
```

**错误**: 单引号不匹配

---

**行 107** (sql):

```sql
-- 查看连接使用情况（带错误处理和性能测试）
DO $$
DECLARE
    conn_record RECORD;
    current_connections int;
    max_connections int;
    usage_percent numeric;
    warning_threshold numeric := 80.0;
    critical_thres
```

**错误**: 单引号不匹配

---

**行 229** (sql):

```sql
-- PostgreSQL检查点参数配置（带错误处理和性能测试）
DO $$
DECLARE
    total_mem_gb numeric := 64;  -- 系统总内存（GB）
    checkpoint_timeout_min int;
    checkpoint_completion_target numeric;
    max_wal_size_gb numeric;

```

**错误**: 单引号不匹配

---

**行 346** (sql):

```sql
-- PostgreSQL WAL参数配置（带错误处理和性能测试）
DO $$
DECLARE
    total_mem_gb numeric := 64;  -- 系统总内存（GB）
    wal_level text;
    wal_buffers_mb int;
    wal_writer_delay_ms int;
    wal_compression boolean;
BEGI
```

**错误**: 单引号不匹配

---

**行 477** (sql):

```sql
-- PostgreSQL自动清理参数配置（带错误处理和性能测试）
DO $$
DECLARE
    cpu_cores int := 8;  -- CPU核心数
    autovacuum_max_workers int;
    autovacuum_naptime_sec int;
    autovacuum_vacuum_cost_delay_ms int;
    autovacu
```

**错误**: 单引号不匹配

---

### 30-性能调优\系统级调优.md

**行 193** (sql):

```sql
-- postgresql.conf内存配置（带错误处理和性能测试）
DO $$
DECLARE
    total_mem_gb numeric;
    shared_buffers_gb numeric;
    effective_cache_size_gb numeric;
    work_mem_mb numeric;
    maintenance_work_mem_gb nume
```

**错误**: 单引号不匹配

---

**行 457** (sql):

```sql
-- PostgreSQL I/O参数配置（带错误处理和性能测试）
DO $$
DECLARE
    storage_type text;
    random_page_cost numeric;
    effective_io_concurrency int;
    maintenance_io_concurrency int;
BEGIN
    -- 检测存储类型（这里假设为SSD，
```

**错误**: 单引号不匹配

---

**行 645** (sql):

```sql
-- PostgreSQL并行查询配置（带错误处理和性能测试）
DO $$
DECLARE
    cpu_cores int;
    max_parallel_workers_per_gather int;
    max_parallel_workers int;
    max_worker_processes int;
BEGIN
    -- 获取CPU核心数（假设8核，实际应从系统获
```

**错误**: 单引号不匹配

---

**行 722** (sql):

```sql
-- PostgreSQL 18 并行查询系统配置优化（带错误处理和性能测试）
DO $$
DECLARE
    cpu_cores int;
    total_mem_gb numeric;
    max_parallel_workers int;
    max_parallel_workers_per_gather int;
    max_parallel_maintenance_w
```

**错误**: 单引号不匹配

---

### 30-性能调优\索引调优.md

**行 60** (sql):

```sql
-- 创建B-tree索引（默认索引类型）
CREATE INDEX idx_orders_date ON orders(order_date);

-- 创建降序索引
CREATE INDEX idx_orders_date_desc ON orders(order_date DESC);

-- 创建唯一索引
CREATE UNIQUE INDEX idx_orders_id ON order
```

**错误**: 单引号不匹配

---

**行 103** (sql):

```sql
-- 创建GIN索引（数组）
CREATE INDEX idx_products_tags ON products USING GIN(tags);

-- 创建GIN索引（JSONB）
CREATE INDEX idx_products_metadata ON products USING GIN(metadata);

-- 创建GIN索引（全文搜索）
CREATE INDEX idx_doc
```

**错误**: 单引号不匹配

---

**行 175** (sql):

```sql
-- 创建复合索引（带错误处理和性能测试）
DO $$
DECLARE
    index_name text;
    table_name text := 'orders';
    column1 text := 'customer_id';
    column2 text := 'order_date';
BEGIN
    index_name := format('idx_%s_%s
```

**错误**: 单引号不匹配

---

**行 393** (sql):

```sql
-- 查看索引使用情况（带错误处理和性能测试）
DO $$
DECLARE
    index_record RECORD;
    unused_index_count int := 0;
    total_index_size bigint := 0;
BEGIN
    RAISE NOTICE '=== 索引使用情况监控 ===';

    -- 查看所有索引使用情况
    FOR
```

**错误**: 单引号不匹配

---

**行 467** (sql):

```sql
-- 查找未使用的索引（带错误处理和性能测试）
DO $$
DECLARE
    unused_index_record RECORD;
    total_unused_size bigint := 0;
    unused_count int := 0;
BEGIN
    RAISE NOTICE '=== 未使用索引识别 ===';

    FOR unused_index_reco
```

**错误**: 单引号不匹配

---

**行 538** (sql):

```sql
-- 查看索引大小（带错误处理和性能测试）
DO $$
DECLARE
    size_record RECORD;
    total_index_size bigint := 0;
    total_table_size bigint := 0;
    index_ratio numeric;
BEGIN
    RAISE NOTICE '=== 索引大小分析 ===';

    F
```

**错误**: 单引号不匹配

---

### 31-容量规划\PostgreSQL成本优化（FinOps）指南.md

**行 672** (sql):

```sql
-- 内存使用分析（带错误处理和性能测试）
DO $$
DECLARE
    setting_record RECORD;
    total_shared_buffers text;
BEGIN
    RAISE NOTICE '查询内存配置参数...';

    FOR setting_record IN
        SELECT
            name,

```

**错误**: 单引号不匹配

---

### 31-容量规划\增长预测.md

**行 309** (sql):

```sql
-- 预测准确性验证工具（带错误处理和性能测试）
DO $$
DECLARE
    predicted_size_gb numeric := 150;  -- 预测容量（GB）
    actual_size_gb numeric := 145;  -- 实际容量（GB）
    prediction_error_percent numeric;
    prediction_accuracy_
```

**错误**: 单引号不匹配

---

### 31-容量规划\容量监控.md

**行 294** (sql):

```sql
-- 监控内存使用（带错误处理和性能测试）
DO $$
DECLARE
    setting_record RECORD;
    memory_params text[] := ARRAY['shared_buffers', 'effective_cache_size', 'work_mem', 'maintenance_work_mem', 'temp_buffers'];
    para
```

**错误**: 单引号不匹配

---

**行 355** (sql):

```sql
-- 告警阈值配置和检查工具（带错误处理和性能测试）
DO $$
DECLARE
    storage_usage_percent numeric;
    cpu_usage_percent numeric := 85.0;  -- 假设从监控系统获取
    memory_usage_percent numeric := 75.0;  -- 假设从监控系统获取
    connection_
```

**错误**: 单引号不匹配

---

**行 538** (sql):

```sql
-- 容量监控报告生成工具（带错误处理和性能测试）
DO $$
DECLARE
    report_date date := CURRENT_DATE;
    db_record RECORD;
    table_record RECORD;
    total_db_size bigint := 0;
    total_table_size bigint := 0;
    total_
```

**错误**: 单引号不匹配

---

### 31-容量规划\容量评估方法.md

**行 379** (sql):

```sql
-- 容量评估报告生成工具（带错误处理和性能测试）
DO $$
DECLARE
    report_date date := CURRENT_DATE;
    db_record RECORD;
    table_record RECORD;
    total_db_size bigint := 0;
    total_table_size bigint := 0;
    total_
```

**错误**: 单引号不匹配

---

### 31-容量规划\扩容策略.md

**行 262** (sql):

```sql
-- 扩容时机判断工具（带错误处理和性能测试）
DO $$
DECLARE
    storage_usage_percent numeric;
    cpu_usage_percent numeric := 85.0;
    memory_usage_percent numeric := 80.0;
    connection_usage_percent numeric;
    curr
```

**错误**: 单引号不匹配

---

### 32-企业级特性\合规性管理.md

**行 359** (sql):

```sql
-- 记录数据处理合法性基础（带错误处理）
DO $$
BEGIN
    BEGIN
        IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'data_processing_consent') THEN
            RAISE
```

**错误**: 单引号不匹配

---

### 32-企业级特性\数据主权管理.md

**行 430** (sql):

```sql
-- 数据路由函数（带错误处理）
-- 路由数据到区域函数（带完整错误处理）
CREATE OR REPLACE FUNCTION route_data_by_region(
    p_user_region TEXT,
    p_data_type TEXT
)
RETURNS TEXT
LANGUAGE plpgsql
AS $$
DECLARE
    v_target_region T
```

**错误**: 单引号不匹配

---

**行 489** (sql):

```sql
-- 检查数据复制权限函数（带完整错误处理）
CREATE OR REPLACE FUNCTION check_replication_allowed(
    p_source_region TEXT,
    p_target_region TEXT,
    p_table_name TEXT
)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
DECLARE

```

**错误**: 单引号不匹配

---

**行 587** (sql):

```sql
-- 跨境传输申请表（带错误处理）
DO $$
BEGIN
    BEGIN
        IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'cross_border_transfer_requests') THEN
            RAI
```

**错误**: 单引号不匹配

---

### 33-数据处理与统计算法\01-数学函数与计算\基础数学函数.md

**行 1275** (sql):

```sql
-- 创建IMMUTABLE数学函数（函数结果只依赖输入参数）
CREATE OR REPLACE FUNCTION calculate_distance(
    x1 NUMERIC,
    y1 NUMERIC,
    x2 NUMERIC,
    y2 NUMERIC
) RETURNS NUMERIC
LANGUAGE SQL
IMMUTABLE
STRICT
AS $$

```

**错误**: SELECT语句缺少FROM子句

---

### 33-数据处理与统计算法\01-数学函数与计算\数值精度处理.md

**行 825** (sql):

```sql
-- 创建精度转换函数（IMMUTABLE）
CREATE OR REPLACE FUNCTION round_to_decimal(
    value NUMERIC,
    precision_scale INTEGER DEFAULT 2
) RETURNS NUMERIC
LANGUAGE SQL
IMMUTABLE
STRICT
AS $$
    SELECT ROUND(valu
```

**错误**: SELECT语句缺少FROM子句

---

### 33-数据处理与统计算法\01-数学函数与计算\数学算法实现.md

**行 672** (sql):

```sql
-- 最小公倍数函数（带错误处理）
CREATE OR REPLACE FUNCTION lcm(a INTEGER, b INTEGER)
RETURNS INTEGER
LANGUAGE plpgsql
IMMUTABLE
AS $$
BEGIN
    BEGIN
        IF a = 0 OR b = 0 THEN
            RETURN 0;
        END
```

**错误**: SELECT语句缺少FROM子句

---

### 33-数据处理与统计算法\02-数据统计与分析\分组统计分析.md

**行 267** (sql):

```sql
GROUP BY col1, col2
UNION ALL
GROUP BY col1
UNION ALL
GROUP BY col2
UNION ALL
SELECT ... (总计)

```

**错误**: SELECT语句缺少FROM子句

---

### 33-数据处理与统计算法\08-机器学习算法\线性回归.md

**行 698** (sql):

```sql
-- 岭回归实现（概念性，完整实现需要矩阵运算扩展）
WITH ridge_regression AS (
    SELECT
        -- 使用伪逆矩阵方法（简化）
        -- 实际中需要使用MADlib或外部工具
        lambda_param := 0.1
)
-- 注意：完整的岭回归需要矩阵求逆，PostgreSQL原生不支持
SELECT 'Ridge re
```

**错误**: SELECT语句缺少FROM子句

---

### 33-数据处理与统计算法\10-运维运营算法\预测性维护.md

**行 1926** (sql):

```sql
-- 智能预测性维护：自适应预测方法选择（带错误处理和性能测试）
DO $$
DECLARE
    equipment_degradation_rate NUMERIC;
    equipment_variance NUMERIC;
    recommended_method VARCHAR(50);
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT
```

**错误**: 括号不匹配

---

### 33-数据处理与统计算法\12-数据质量算法\数据标准化算法.md

**行 280** (sql):

```sql
-- 文本规范化综合处理
CREATE OR REPLACE FUNCTION normalize_text(input_text TEXT) RETURNS TEXT AS $$
BEGIN
    -- 去除首尾空格
    input_text := TRIM(input_text);
    -- 统一多个空格为单个空格
    input_text := REGEXP_REPLACE(i
```

**错误**: 单引号不匹配

---

**行 707** (sql):

```sql
-- 客户数据标准化：综合处理客户信息
WITH customer_standardization AS (
    SELECT
        customer_id,
        -- 姓名标准化
        INITCAP(TRIM(name)) AS standardized_name,
        -- 邮箱标准化
        LOWER(TRIM(email)) AS
```

**错误**: 单引号不匹配

---

**行 826** (sql):

```sql
-- 批量数据标准化：使用UPDATE批量更新标准化后的数据
-- 创建标准化后的表
CREATE TABLE IF NOT EXISTS customers_standardized AS
SELECT
    customer_id,
    INITCAP(TRIM(name)) AS standardized_name,
    LOWER(TRIM(email)) AS standard
```

**错误**: 单引号不匹配

---

### 33-数据处理与统计算法\12-数据质量算法\数据清洗算法.md

**行 582** (sql):

```sql
-- 数据格式标准化：统一电话号码、邮箱、日期格式
WITH raw_data AS (
    SELECT
        id,
        phone,
        email,
        date_string
    FROM customer_data
),
formatted_data AS (
    SELECT
        id,
        -- 电话
```

**错误**: 单引号不匹配

---

### 33-数据处理与统计算法\14-高维数据分析\张量分解算法.md

**行 213** (sql):

```sql
-- 秩估计：计算不同秩的重构误差
WITH rank_candidates AS (
    SELECT r FROM generate_series(1, 5) AS r
),
reconstruction_errors AS (
    SELECT
        r.r AS rank_value,
        AVG(POWER(td.value -
            (S
```

**错误**: 单引号不匹配

---

### 33-数据处理与统计算法\14-高维数据分析\独立成分分析ICA.md

**行 916** (sql):

```sql
-- 智能ICA优化：自适应分离策略选择（带错误处理和性能测试）
DO $$
DECLARE
    signal_count INTEGER;
    sample_count BIGINT;
    gaussian_ratio NUMERIC;
    recommended_method VARCHAR(50);
BEGIN
    BEGIN
        IF NOT EXISTS
```

**错误**: 括号不匹配

---

### 33-数据处理与统计算法\16-统计推断\假设检验算法.md

**行 178** (sql):

```sql
-- 单样本t检验实现（带错误处理和性能测试）
DO $$
BEGIN
    BEGIN
        IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'sample_data') THEN
            RAISE WARNING '表
```

**错误**: 单引号不匹配

---

**行 294** (sql):

```sql
-- 双样本t检验实现
DO $$
BEGIN
    BEGIN
        IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'two_sample_data') THEN
            RAISE WARNING '表 two_sam
```

**错误**: 单引号不匹配

---

**行 430** (sql):

```sql
-- 配对t检验：完整实现（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'paired_data') THEN
            RAISE WARNING '
```

**错误**: 单引号不匹配

---

### 33-数据处理与统计算法\16-统计推断\功效分析算法.md

**行 151** (sql):

```sql
-- 卡方检验功效分析
WITH chi_square_power AS (
    SELECT
        effect_size,  -- Cramér's V
        sample_size,
        alpha,
        -- 非中心参数：λ = n * V²
        sample_size * POWER(effect_size, 2) AS non
```

**错误**: 单引号不匹配

---

**行 250** (sql):

```sql
-- 功效曲线：不同样本量下的功效
WITH sample_sizes AS (
    SELECT generate_series(10, 200, 10) AS n
),
power_curve AS (
    SELECT
        n,
        0.5 AS effect_size,
        0.05 AS alpha,
        -- 功效估计

```

**错误**: 单引号不匹配

---

**行 494** (sql):

```sql
-- PostgreSQL 18 并行效应量分析（带错误处理和性能测试）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'experimental_data') THEN

```

**错误**: 单引号不匹配

---

### 33-数据处理与统计算法\17-高级机器学习\随机森林算法.md

**行 860** (sql):

```sql
   -- 特征数量计算
   SELECT
       CEIL(SQRT(5)) AS sqrt_features,  -- 5个特征 → 3个
       CEIL(LOG(2, 5)) AS log_features;  -- 5个特征 → 3个

```

**错误**: SELECT语句缺少FROM子句

---

### 33-数据处理与统计算法\20-数据安全与隐私\数据加密算法.md

**行 256** (sql):

```sql
-- RSA密钥对生成（简化：使用pgcrypto）
-- 注意：实际应用中应使用专门的密钥管理工具
DO $$
DECLARE
    public_key TEXT;
    private_key TEXT;
BEGIN
    BEGIN
        -- 生成RSA密钥对（简化实现）
        -- 实际应用中应使用openssl或专门的密钥管理工具
        RAISE
```

**错误**: SELECT语句缺少FROM子句

---

### 33-数据处理与统计算法\23-图论高级算法\图匹配算法.md

**行 464** (sql):

```sql
-- 权重矩阵准备
DO $$
BEGIN
    BEGIN
        IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'weighted_bipartite') THEN
            DROP TABLE weighted_bip
```

**错误**: 单引号不匹配

---

### 33-数据处理与统计算法\24-时间序列高级分析\ARIMA模型.md

**行 526** (sql):

```sql
-- AIC/BIC模型选择
WITH model_comparison AS (
    SELECT
        p, d, q,
        aic_value,
        bic_value,
        ROW_NUMBER() OVER (ORDER BY aic_value) AS aic_rank,
        ROW_NUMBER() OVER (ORDER
```

**错误**: 单引号不匹配

---

### 34-模型与建模\04-OLTP建模\Party模型.md

**行 335** (sql):

```sql
-- Person实体（标准模型，带错误处理）
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_tables WHERE tablename = 'person') THEN
        CREATE TABLE person (
            party_id INT PRIMARY KEY REFERENCES party(part
```

**错误**: 单引号不匹配

---

### 34-模型与建模\04-OLTP建模\产品管理模型.md

**行 868** (sql):

```sql
-- PostgreSQL 18: 虚拟生成列用于特征搜索
ALTER TABLE product_feature_applicability
ADD COLUMN feature_search_text TEXT
GENERATED ALWAYS AS (
    pf.feature_name || ' ' || COALESCE(pf.description, '')
) STORED;


```

**错误**: 单引号不匹配

---

### 34-模型与建模\04-OLTP建模\范式化设计.md

**行 398** (sql):

```sql
-- ✅ 反规范化：订单行表冗余行金额（避免计算，带错误处理）
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_tables WHERE tablename = 'order_items_denormalized') THEN
        CREATE TABLE order_items_denormalized (
            li
```

**错误**: 括号不匹配

---

### 34-模型与建模\05-OLAP建模\PostgreSQL列存实现.md

**行 803** (sql):

```sql
-- 对比行存和列存存储空间
SELECT
    'rowstore' AS storage_type,
    pg_size_pretty(pg_total_relation_size('fact_sales_rowstore')) AS size
UNION ALL
SELECT
    'columnar' AS storage_type,
    pg_size_pretty(pg_t
```

**错误**: SELECT语句缺少FROM子句

---

### 34-模型与建模\06-IoT与时序建模\TimescaleDB实践.md

**行 181** (sql):

```sql
-- 1. 创建普通表
CREATE TABLE sensor_readings (
    time TIMESTAMPTZ NOT NULL,
    device_id INT NOT NULL,
    sensor_type VARCHAR(50) NOT NULL,
    value DOUBLE PRECISION NOT NULL,
    quality INT DEFAULT
```

**错误**: SELECT语句缺少FROM子句

---

**行 238** (sql):

```sql
-- 按天分区（推荐用于高频数据）
SELECT create_hypertable(
    'sensor_readings',
    'time',
    chunk_time_interval => INTERVAL '1 day'
);

-- 按周分区（推荐用于中频数据）
SELECT create_hypertable(
    'sensor_readings',
    't
```

**错误**: SELECT语句缺少FROM子句

---

**行 263** (sql):

```sql
-- 按时间和设备ID分区
SELECT create_hypertable(
    'sensor_readings',
    'time',
    partitioning_column => 'device_id',
    number_partitions => 4,  -- 4个设备分区
    chunk_time_interval => INTERVAL '1 day'
);
```

**错误**: SELECT语句缺少FROM子句

---

**行 364** (sql):

```sql
-- 保留30天的数据
SELECT add_retention_policy(
    'sensor_readings',
    INTERVAL '30 days'
);

-- 保留策略执行后，自动删除30天前的数据

```

**错误**: SELECT语句缺少FROM子句

---

**行 413** (sql):

```sql
-- 启用压缩
ALTER TABLE sensor_readings SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'device_id',
    timescaledb.compress_orderby = 'time DESC'
);

-- 添加压缩策略（压缩7天前的数据）
SELECT add_
```

**错误**: SELECT语句缺少FROM子句

---

**行 1359** (sql):

```sql
-- 查看当前chunk大小
SELECT set_chunk_time_interval('sensor_readings', INTERVAL '1 day');

-- 根据数据量调整
-- 如果每天数据量100MB，设置1天chunk
-- 如果每天数据量500MB，设置2天chunk

```

**错误**: SELECT语句缺少FROM子句

---

**行 1372** (sql):

```sql
-- 优化1：选择合适的segmentby列
ALTER TABLE sensor_readings SET (
    timescaledb.compress_segmentby = 'device_id, sensor_type'
);

-- 优化2：选择合适的orderby列
ALTER TABLE sensor_readings SET (
    timescaledb.compre
```

**错误**: SELECT语句缺少FROM子句

---

### 34-模型与建模\06-IoT与时序建模\时序数据模型.md

**行 2103** (sql):

```sql
-- TimescaleDB压缩优化
ALTER TABLE sensor_readings SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'device_id',
    timescaledb.compress_orderby = 'timestamp DESC'
);

-- 设置压缩策略（延迟压缩）
```

**错误**: SELECT语句缺少FROM子句

---

### 34-模型与建模\06-IoT与时序建模\设备孪生模型.md

**行 341** (sql):

```sql
-- 更新设备状态
CREATE OR REPLACE FUNCTION update_device_state(
    p_device_id VARCHAR,
    p_status VARCHAR,
    p_state_data JSONB DEFAULT NULL,
    p_change_reason VARCHAR DEFAULT NULL
)
RETURNS VOID AS
```

**错误**: SELECT语句缺少FROM子句

---

**行 419** (sql):

```sql
-- 遥测数据表（使用TimescaleDB）
CREATE TABLE device_telemetry (
    time TIMESTAMPTZ NOT NULL,
    device_id VARCHAR(50) NOT NULL REFERENCES device_twin(device_id),
    -- 遥测数据（JSONB存储灵活结构）
    telemetry_data
```

**错误**: SELECT语句缺少FROM子句

---

**行 450** (sql):

```sql
-- 查询设备遥测数据
CREATE OR REPLACE FUNCTION get_device_telemetry(
    p_device_id VARCHAR,
    p_start_time TIMESTAMPTZ,
    p_end_time TIMESTAMPTZ,
    p_metric_name VARCHAR DEFAULT NULL
)
RETURNS TABLE (
```

**错误**: 括号不匹配

---

**行 628** (sql):

```sql
-- 设备孪生主表
CREATE TABLE device_twin (
    device_id VARCHAR(50) PRIMARY KEY,
    device_name VARCHAR(200) NOT NULL,
    device_type VARCHAR(50) NOT NULL,
    properties JSONB DEFAULT '{}',
    configur
```

**错误**: SELECT语句缺少FROM子句

---

### 34-模型与建模\07-工作流建模\BPMN建模.md

**行 897** (sql):

```sql
-- 任务超时检查函数
CREATE OR REPLACE FUNCTION check_task_timeout()
RETURNS INT AS $$
DECLARE
    v_count INT;
BEGIN
    -- 查找超时的任务
    UPDATE bpmn_task
    SET status = 'timeout',
        timeout_time = NOW(
```

**错误**: SELECT语句缺少FROM子句

---

### 34-模型与建模\08-PostgreSQL建模实践\分区策略.md

**行 697** (sql):

```sql
-- 添加新分区（带错误处理）
DO $$
BEGIN
    CREATE TABLE IF NOT EXISTS sales_2025_q1 PARTITION OF sales
        FOR VALUES FROM ('2025-01-01') TO ('2025-04-01');
    RAISE NOTICE '分区 sales_2025_q1 创建成功';
EXCEPTIO
```

**错误**: 单引号不匹配

---

### 34-模型与建模\08-PostgreSQL建模实践\向量数据库建模.md

**行 1644** (sql):

```sql
-- PostgreSQL 18：启用异步I/O优化向量操作
ALTER SYSTEM SET io_direct = 'data';
ALTER SYSTEM SET io_combine_limit = '256kB';
SELECT pg_reload_conf();

```

**错误**: SELECT语句缺少FROM子句

---

### 34-模型与建模\08-PostgreSQL建模实践\性能优化.md

**行 2081** (sql):

```sql
-- 应用级锁（不锁定数据）
SELECT pg_advisory_lock(123);  -- 锁定ID 123
-- 执行操作
SELECT pg_advisory_unlock(123);  -- 释放锁

-- 或使用事务级锁
BEGIN;
SELECT pg_advisory_xact_lock(123);
-- 操作
COMMIT;  -- 自动释放

```

**错误**: SELECT语句缺少FROM子句

---

### 34-模型与建模\08-PostgreSQL建模实践\数据类型选择.md

**行 3373** (sql):

```sql
-- ❌ 错误：金融金额使用浮点
SELECT 0.1 + 0.2;  -- 结果：0.30000000000000004

-- ✅ 正确：使用NUMERIC
SELECT 0.1::NUMERIC + 0.2::NUMERIC;  -- 结果：0.3

```

**错误**: SELECT语句缺少FROM子句

---

### 34-模型与建模\08-PostgreSQL建模实践\索引策略.md

**行 3391** (sql):

```sql
   -- 检查磁盘空间
   SELECT pg_size_pretty(pg_database_size(current_database()));

   -- 清理不需要的数据
   VACUUM FULL orders;

```

**错误**: SELECT语句缺少FROM子句

---

### 34-模型与建模\08-PostgreSQL建模实践\约束设计.md

**行 2644** (sql):

```sql
-- 案例：订单项可以引用产品或服务（多态关联）
-- 产品表（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'products_constraint_example'
```

**错误**: 括号不匹配

---

### 34-模型与建模\10-综合应用案例\IoT监控系统案例.md

**行 957** (sql):

```sql
-- TimescaleDB压缩配置
ALTER TABLE device_telemetry SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'device_id',
    timescaledb.compress_orderby = 'time DESC'
);

-- 设置压缩策略（7天后压缩）
SE
```

**错误**: SELECT语句缺少FROM子句

---

### 34-模型与建模\11-AI与ML集成建模\02-ML特征工程建模.md

**行 712** (sql):

```sql
-- PostgreSQL 18：启用异步I/O优化特征写入
ALTER SYSTEM SET io_direct = 'data';
ALTER SYSTEM SET io_combine_limit = '256kB';
SELECT pg_reload_conf();

```

**错误**: SELECT语句缺少FROM子句

---

### 34-模型与建模\11-AI与ML集成建模\03-模型训练数据管理.md

**行 670** (sql):

```sql
-- TimescaleDB自动分区优化
SELECT create_hypertable(
    'time_series_training_data',
    'time',
    chunk_time_interval => INTERVAL '1 day',
    if_not_exists => TRUE
);

-- 调整chunk大小以优化查询性能
SELECT set_ch
```

**错误**: SELECT语句缺少FROM子句

---

**行 745** (sql):

```sql
-- PostgreSQL 18：启用异步I/O优化数据写入
ALTER SYSTEM SET io_direct = 'data';
ALTER SYSTEM SET io_combine_limit = '256kB';
SELECT pg_reload_conf();

```

**错误**: SELECT语句缺少FROM子句

---

**行 869** (sql):

```sql
-- 计算标注一致性（Cohen's Kappa）
WITH annotation_stats AS (
    SELECT
        sample_id,
        COUNT(DISTINCT annotator_id) AS annotator_count,
        COUNT(DISTINCT label) AS label_count,
        MODE()
```

**错误**: 单引号不匹配

---

### 34-模型与建模\11-AI与ML集成建模\04-模型推理数据建模.md

**行 324** (sql):

```sql
-- 性能指标表（使用TimescaleDB）
CREATE TABLE inference_performance_metrics (
    time TIMESTAMPTZ NOT NULL,
    model_version_id INTEGER NOT NULL REFERENCES model_versions(id),
    metric_name VARCHAR(100) NO
```

**错误**: SELECT语句缺少FROM子句

---

**行 550** (sql):

```sql
-- TimescaleDB自动分区优化
SELECT create_hypertable(
    'inference_requests',
    'created_at',
    chunk_time_interval => INTERVAL '1 day',
    if_not_exists => TRUE
);

-- 调整chunk大小
SELECT set_chunk_time
```

**错误**: SELECT语句缺少FROM子句

---

**行 565** (sql):

```sql
-- 创建TimescaleDB超表
SELECT create_hypertable(
    'inference_performance_metrics',
    'timestamp',
    chunk_time_interval => INTERVAL '1 hour',
    if_not_exists => TRUE
);

```

**错误**: SELECT语句缺少FROM子句

---

### 34-模型与建模\11-AI与ML集成建模\05-AI应用场景建模.md

**行 250** (sql):

```sql
-- RAG检索函数（向量相似度 + 全文搜索，带性能测试）
CREATE OR REPLACE FUNCTION rag_retrieve(
    query_embedding vector(1536),
    query_text TEXT,
    top_k INTEGER DEFAULT 10,
    similarity_threshold FLOAT DEFAULT 0.7

```

**错误**: 单引号不匹配

---

**行 381** (sql):

```sql
-- 用户行为表（使用TimescaleDB）
CREATE TABLE user_behaviors (
    time TIMESTAMPTZ NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    item_id VARCHAR(255) NOT NULL,
    behavior_type VARCHAR(50) NOT NULL,  -- '
```

**错误**: SELECT语句缺少FROM子句

---

### 34-模型与建模\12-数据架构模式\02-数据湖架构.md

**行 507** (sql):

```sql
-- 为数据目录创建全文搜索索引
CREATE INDEX idx_data_lake_catalog_search ON data_lake_catalog
USING gin(to_tsvector('english', dataset_name || ' ' || COALESCE(description, '')));

```

**错误**: 单引号不匹配

---

### 34-模型与建模\12-数据架构模式\03-现代数据栈架构.md

**行 588** (sql):

```sql
-- TimescaleDB自动分区优化
SELECT create_hypertable(
    'pipeline_executions',
    'time',
    chunk_time_interval => INTERVAL '1 day',
    if_not_exists => TRUE
);

```

**错误**: SELECT语句缺少FROM子句

---

**行 600** (sql):

```sql
-- 创建TimescaleDB超表
SELECT create_hypertable(
    'data_application_usage_stats',
    'timestamp',
    chunk_time_interval => INTERVAL '1 hour',
    if_not_exists => TRUE
);

```

**错误**: SELECT语句缺少FROM子句

---

**行 660** (sql):

```sql
-- PostgreSQL 18：启用异步I/O优化数据管道写入
ALTER SYSTEM SET io_direct = 'data';
ALTER SYSTEM SET io_combine_limit = '256kB';
SELECT pg_reload_conf();

```

**错误**: SELECT语句缺少FROM子句

---
