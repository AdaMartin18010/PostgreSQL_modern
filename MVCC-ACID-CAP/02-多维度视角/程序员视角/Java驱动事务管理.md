# Java驱动PostgreSQL事务管理最佳实践

> **文档编号**: DEV-JAVA-001
> **语言**: Java
> **驱动**: JDBC / HikariCP
> **版本**: PostgreSQL 17 & 18

---

## 📑 目录

- [Java驱动PostgreSQL事务管理最佳实践](#java驱动postgresql事务管理最佳实践)
  - [📑 目录](#-目录)
  - [📋 概述](#-概述)
  - [🔍 第一部分：JDBC基础事务管理](#-第一部分jdbc基础事务管理)
    - [1.1 连接管理](#11-连接管理)
      - [JDBC连接配置](#jdbc连接配置)
      - [连接参数优化](#连接参数优化)
    - [1.2 事务管理基础](#12-事务管理基础)
      - [基本事务操作](#基本事务操作)
      - [事务提交和回滚](#事务提交和回滚)
    - [1.3 隔离级别设置](#13-隔离级别设置)
      - [Connection级别设置](#connection级别设置)
      - [事务级别设置](#事务级别设置)
    - [1.4 错误处理和重试](#14-错误处理和重试)
      - [SQLException处理](#sqlexception处理)
      - [死锁重试机制](#死锁重试机制)
      - [序列化错误重试](#序列化错误重试)
  - [🚀 第二部分：HikariCP连接池](#-第二部分hikaricp连接池)
    - [2.1 连接池配置](#21-连接池配置)
      - [基本配置](#基本配置)
      - [MVCC优化配置](#mvcc优化配置)
    - [2.2 连接池监控](#22-连接池监控)
      - [HikariCP监控指标](#hikaricp监控指标)
      - [JMX监控](#jmx监控)
    - [2.3 连接池最佳实践](#23-连接池最佳实践)
      - [连接池大小设置](#连接池大小设置)
      - [连接泄漏检测](#连接泄漏检测)
  - [📊 第三部分：Spring事务管理](#-第三部分spring事务管理)
    - [3.1 @Transactional注解](#31-transactional注解)
      - [基本使用](#基本使用)
      - [隔离级别设置](#隔离级别设置)
      - [传播行为](#传播行为)
    - [3.2 事务管理器配置](#32-事务管理器配置)
      - [DataSourceTransactionManager](#datasourcetransactionmanager)
      - [JpaTransactionManager](#jpatransactionmanager)
    - [3.3 事务回滚策略](#33-事务回滚策略)
      - [异常回滚配置](#异常回滚配置)
      - [自定义回滚规则](#自定义回滚规则)
  - [🔧 第四部分：MVCC最佳实践](#-第四部分mvcc最佳实践)
    - [4.1 短事务原则](#41-短事务原则)
      - [避免长事务](#避免长事务)
      - [批量操作优化](#批量操作优化)
    - [4.2 并发控制](#42-并发控制)
      - [SELECT FOR UPDATE使用](#select-for-update使用)
      - [乐观锁实现](#乐观锁实现)
      - [悲观锁实现](#悲观锁实现)
    - [4.3 性能优化](#43-性能优化)
      - [PreparedStatement使用](#preparedstatement使用)
      - [批量操作](#批量操作)
      - [连接池优化](#连接池优化)
  - [📈 第五部分：实际场景案例](#-第五部分实际场景案例)
    - [5.1 电商库存扣减场景](#51-电商库存扣减场景)
    - [5.2 银行转账场景](#52-银行转账场景)
    - [5.3 日志写入场景](#53-日志写入场景)
  - [📝 第六部分：常见问题和解决方案](#-第六部分常见问题和解决方案)
    - [6.1 常见错误](#61-常见错误)
      - [错误1：连接泄漏](#错误1连接泄漏)
      - [错误2：事务嵌套问题](#错误2事务嵌套问题)
    - [6.2 性能问题](#62-性能问题)
      - [问题1：N+1查询问题](#问题1n1查询问题)
    - [6.3 调试技巧](#63-调试技巧)
      - [查看事务信息](#查看事务信息)
  - [🎯 总结](#-总结)
    - [核心最佳实践](#核心最佳实践)
    - [关键配置](#关键配置)
    - [MVCC影响](#mvcc影响)

---

## 📋 概述

Java是PostgreSQL企业级应用的主要编程语言，主要通过**JDBC**驱动和**HikariCP**连接池与PostgreSQL交互。本文档深入分析Java驱动在PostgreSQL MVCC环境下的最佳实践，涵盖JDBC基础、HikariCP连接池、Spring事务管理和MVCC优化。

---

## 🔍 第一部分：JDBC基础事务管理

### 1.1 连接管理

#### JDBC连接配置

```java
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import java.util.Properties;

public class PostgreSQLConnection {
    // PostgreSQL 17/18推荐连接URL
    private static final String URL = "jdbc:postgresql://localhost:5432/mydb";

    // 连接参数
    private static Properties getConnectionProperties() {
        Properties props = new Properties();
        props.setProperty("user", "postgres");
        props.setProperty("password", "password");

        // MVCC相关参数
        props.setProperty("ApplicationName", "myapp");
        props.setProperty("connectTimeout", "10");
        props.setProperty("socketTimeout", "30");
        props.setProperty("tcpKeepAlive", "true");

        // 事务相关
        props.setProperty("defaultRowFetchSize", "1000");
        props.setProperty("reWriteBatchedInserts", "true");  // 批量插入优化

        return props;
    }

    public static Connection getConnection() throws SQLException {
        return DriverManager.getConnection(URL, getConnectionProperties());
    }
}
```

#### 连接参数优化

```java
// PostgreSQL 17/18推荐连接参数
Properties props = new Properties();
props.setProperty("user", "postgres");
props.setProperty("password", "password");

// 连接保持
props.setProperty("tcpKeepAlive", "true");
props.setProperty("socketTimeout", "30");

// 超时设置
props.setProperty("connectTimeout", "10");
props.setProperty("loginTimeout", "10");

// MVCC优化
props.setProperty("ApplicationName", "myapp");
props.setProperty("assumeMinServerVersion", "17");  // PostgreSQL 17+

// 批量操作优化
props.setProperty("reWriteBatchedInserts", "true");  // 批量插入重写
props.setProperty("defaultRowFetchSize", "1000");    // 默认获取行数
```

### 1.2 事务管理基础

#### 基本事务操作

```java
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.SQLException;

public class TransactionManager {

    public boolean transferMoney(Connection conn, int fromId, int toId, double amount)
            throws SQLException {
        // 关闭自动提交
        conn.setAutoCommit(false);

        try (PreparedStatement stmt1 = conn.prepareStatement(
                "UPDATE accounts SET balance = balance - ? WHERE id = ?");
             PreparedStatement stmt2 = conn.prepareStatement(
                "UPDATE accounts SET balance = balance + ? WHERE id = ?")) {

            // 扣减转出账户
            stmt1.setDouble(1, amount);
            stmt1.setInt(2, fromId);
            stmt1.executeUpdate();

            // 增加转入账户
            stmt2.setDouble(1, amount);
            stmt2.setInt(2, toId);
            stmt2.executeUpdate();

            // 提交事务
            conn.commit();
            return true;

        } catch (SQLException e) {
            // 回滚事务
            conn.rollback();
            throw e;
        } finally {
            // 恢复自动提交
            conn.setAutoCommit(true);
        }
    }
}
```

#### 事务提交和回滚

```java
public class TransactionExample {

    public void executeTransaction(Connection conn) throws SQLException {
        conn.setAutoCommit(false);

        try {
            // 执行多个操作
            executeOperation1(conn);
            executeOperation2(conn);
            executeOperation3(conn);

            // 提交
            conn.commit();

        } catch (SQLException e) {
            // 回滚
            conn.rollback();
            throw e;
        } finally {
            conn.setAutoCommit(true);
        }
    }
}
```

### 1.3 隔离级别设置

#### Connection级别设置

```java
import java.sql.Connection;

public class IsolationLevelExample {

    public void setIsolationLevel(Connection conn) throws SQLException {
        // READ COMMITTED（默认）
        conn.setTransactionIsolation(Connection.TRANSACTION_READ_COMMITTED);

        // REPEATABLE READ
        conn.setTransactionIsolation(Connection.TRANSACTION_REPEATABLE_READ);

        // SERIALIZABLE
        conn.setTransactionIsolation(Connection.TRANSACTION_SERIALIZABLE);

        // 查看当前隔离级别
        int level = conn.getTransactionIsolation();
        System.out.println("Current isolation level: " + level);
    }
}
```

#### 事务级别设置

```java
public void setTransactionIsolation(Connection conn) throws SQLException {
    conn.setAutoCommit(false);

    try (PreparedStatement stmt = conn.prepareStatement(
            "SET TRANSACTION ISOLATION LEVEL REPEATABLE READ")) {
        stmt.execute();

        // 执行事务操作
        executeOperations(conn);

        conn.commit();
    } catch (SQLException e) {
        conn.rollback();
        throw e;
    } finally {
        conn.setAutoCommit(true);
    }
}
```

### 1.4 错误处理和重试

#### SQLException处理

```java
import java.sql.SQLException;

public class ErrorHandler {

    public boolean isDeadlock(SQLException e) {
        // PostgreSQL死锁错误码：40001
        String sqlState = e.getSQLState();
        return "40001".equals(sqlState) ||
               e.getMessage().toLowerCase().contains("deadlock");
    }

    public boolean isSerializationError(SQLException e) {
        // PostgreSQL序列化错误码：40001
        String sqlState = e.getSQLState();
        return "40001".equals(sqlState) ||
               e.getMessage().toLowerCase().contains("serialization");
    }
}
```

#### 死锁重试机制

```java
import java.util.Random;

public class RetryableTransaction {
    private static final int MAX_RETRIES = 5;
    private static final Random random = new Random();

    public boolean executeWithRetry(Connection conn, TransactionOperation operation)
            throws SQLException {
        for (int attempt = 0; attempt < MAX_RETRIES; attempt++) {
            try {
                conn.setAutoCommit(false);
                boolean result = operation.execute(conn);
                conn.commit();
                return result;

            } catch (SQLException e) {
                conn.rollback();

                if (isDeadlock(e) && attempt < MAX_RETRIES - 1) {
                    // 指数退避
                    long delay = (long) (Math.pow(2, attempt) * 100 +
                                        random.nextInt(100));
                    try {
                        Thread.sleep(delay);
                    } catch (InterruptedException ie) {
                        Thread.currentThread().interrupt();
                        throw new SQLException("Retry interrupted", ie);
                    }
                    continue;
                }
                throw e;
            } finally {
                conn.setAutoCommit(true);
            }
        }
        return false;
    }

    @FunctionalInterface
    public interface TransactionOperation {
        boolean execute(Connection conn) throws SQLException;
    }
}
```

#### 序列化错误重试

```java
public class SerializableTransaction {

    public boolean executeSerializable(Connection conn, TransactionOperation operation)
            throws SQLException {
        // 设置SERIALIZABLE隔离级别
        conn.setTransactionIsolation(Connection.TRANSACTION_SERIALIZABLE);

        return executeWithRetry(conn, operation, this::isSerializationError);
    }

    private boolean executeWithRetry(Connection conn, TransactionOperation operation,
                                     java.util.function.Predicate<SQLException> retryCondition)
            throws SQLException {
        for (int attempt = 0; attempt < 5; attempt++) {
            try {
                conn.setAutoCommit(false);
                boolean result = operation.execute(conn);
                conn.commit();
                return result;

            } catch (SQLException e) {
                conn.rollback();

                if (retryCondition.test(e) && attempt < 4) {
                    // 短暂等待后重试
                    try {
                        Thread.sleep(10 + random.nextInt(90));
                    } catch (InterruptedException ie) {
                        Thread.currentThread().interrupt();
                        throw new SQLException("Retry interrupted", ie);
                    }
                    continue;
                }
                throw e;
            } finally {
                conn.setAutoCommit(true);
            }
        }
        return false;
    }
}
```

---

## 🚀 第二部分：HikariCP连接池

### 2.1 连接池配置

#### 基本配置

```java
import com.zaxxer.hikari.HikariConfig;
import com.zaxxer.hikari.HikariDataSource;

public class HikariCPConfig {

    public static HikariDataSource createDataSource() {
        HikariConfig config = new HikariConfig();

        // 基本连接配置
        config.setJdbcUrl("jdbc:postgresql://localhost:5432/mydb");
        config.setUsername("postgres");
        config.setPassword("password");
        config.setDriverClassName("org.postgresql.Driver");

        // 连接池大小
        config.setMinimumIdle(5);
        config.setMaximumPoolSize(20);

        // 连接超时
        config.setConnectionTimeout(10000);  // 10秒
        config.setIdleTimeout(600000);       // 10分钟
        config.setMaxLifetime(1800000);      // 30分钟

        // MVCC优化参数
        config.addDataSourceProperty("ApplicationName", "myapp");
        config.addDataSourceProperty("tcpKeepAlive", "true");
        config.addDataSourceProperty("socketTimeout", "30");

        // 批量操作优化
        config.addDataSourceProperty("reWriteBatchedInserts", "true");
        config.addDataSourceProperty("defaultRowFetchSize", "1000");

        return new HikariDataSource(config);
    }
}
```

#### MVCC优化配置

```java
public class OptimizedHikariCPConfig {

    public static HikariDataSource createOptimizedDataSource() {
        HikariConfig config = new HikariConfig();

        // 基本配置
        config.setJdbcUrl("jdbc:postgresql://localhost:5432/mydb");
        config.setUsername("postgres");
        config.setPassword("password");

        // 连接池大小（根据并发需求调整）
        config.setMinimumIdle(5);
        config.setMaximumPoolSize(20);

        // 连接泄漏检测（防止长事务）
        config.setLeakDetectionThreshold(60000);  // 60秒

        // 连接验证
        config.setConnectionTestQuery("SELECT 1");
        config.setValidationTimeout(3000);

        // PostgreSQL 17/18优化参数
        config.addDataSourceProperty("ApplicationName", "myapp");
        config.addDataSourceProperty("assumeMinServerVersion", "17");

        // MVCC相关
        config.addDataSourceProperty("tcpKeepAlive", "true");
        config.addDataSourceProperty("socketTimeout", "30");

        // 批量操作优化
        config.addDataSourceProperty("reWriteBatchedInserts", "true");
        config.addDataSourceProperty("defaultRowFetchSize", "1000");

        return new HikariDataSource(config);
    }
}
```

### 2.2 连接池监控

#### HikariCP监控指标

```java
import com.zaxxer.hikari.HikariDataSource;
import com.zaxxer.hikari.HikariPoolMXBean;

public class HikariCPMonitor {

    public void monitorPool(HikariDataSource dataSource) {
        HikariPoolMXBean poolBean = dataSource.getHikariPoolMXBean();

        System.out.println("=== HikariCP Pool Status ===");
        System.out.println("Active connections: " + poolBean.getActiveConnections());
        System.out.println("Idle connections: " + poolBean.getIdleConnections());
        System.out.println("Total connections: " + poolBean.getTotalConnections());
        System.out.println("Threads awaiting connection: " +
                          poolBean.getThreadsAwaitingConnection());

        // 连接池使用率
        double usageRate = (double) poolBean.getActiveConnections() /
                          dataSource.getMaximumPoolSize() * 100;
        System.out.println("Pool usage: " + String.format("%.2f%%", usageRate));

        if (usageRate > 80) {
            System.out.println("WARNING: Pool usage exceeds 80%");
        }
    }
}
```

#### JMX监控

```java
import javax.management.MBeanServer;
import java.lang.management.ManagementFactory;

public class JMXMonitoring {

    public void enableJMX(HikariDataSource dataSource) {
        // HikariCP自动注册JMX MBean
        // 可以通过JConsole或其他JMX客户端监控

        MBeanServer mbs = ManagementFactory.getPlatformMBeanServer();
        // HikariCP MBean名称: com.zaxxer.hikari:type=Pool (pool-name)
    }
}
```

### 2.3 连接池最佳实践

#### 连接池大小设置

```java
public class PoolSizeCalculator {

    /**
     * 计算推荐连接池大小
     * 公式: connections = ((core_count * 2) + effective_spindle_count)
     */
    public int calculateOptimalPoolSize(int cpuCores, int diskSpindles) {
        // 基本公式
        int baseSize = (cpuCores * 2) + diskSpindles;

        // 根据PostgreSQL MVCC特性调整
        // MVCC读不阻塞写，可以适当增加连接数
        int adjustedSize = (int) (baseSize * 1.2);

        // 限制最大连接数（避免超过max_connections）
        return Math.min(adjustedSize, 50);
    }

    // 推荐配置
    public HikariConfig getRecommendedConfig() {
        HikariConfig config = new HikariConfig();

        // CPU核心数
        int cores = Runtime.getRuntime().availableProcessors();

        // 推荐配置
        config.setMinimumIdle(cores);
        config.setMaximumPoolSize(cores * 2);

        return config;
    }
}
```

#### 连接泄漏检测

```java
public class LeakDetection {

    public HikariConfig configureLeakDetection(HikariConfig config) {
        // 设置泄漏检测阈值（60秒）
        // 如果连接持有时间超过阈值，会记录警告日志
        config.setLeakDetectionThreshold(60000);

        return config;
    }

    // 监控连接泄漏
    public void checkForLeaks(HikariDataSource dataSource) {
        HikariPoolMXBean poolBean = dataSource.getHikariPoolMXBean();

        // 检查等待连接的线程数
        int waitingThreads = poolBean.getThreadsAwaitingConnection();
        if (waitingThreads > 0) {
            System.out.println("WARNING: " + waitingThreads +
                             " threads waiting for connection");
        }

        // 检查连接使用率
        double usageRate = (double) poolBean.getActiveConnections() /
                          dataSource.getMaximumPoolSize();
        if (usageRate > 0.9) {
            System.out.println("WARNING: Pool usage exceeds 90%");
        }
    }
}
```

---

## 📊 第三部分：Spring事务管理

### 3.1 @Transactional注解

#### 基本使用

```java
import org.springframework.transaction.annotation.Transactional;
import org.springframework.stereotype.Service;

@Service
public class AccountService {

    @Transactional
    public void transferMoney(int fromId, int toId, double amount) {
        // 自动事务管理
        accountRepository.debit(fromId, amount);
        accountRepository.credit(toId, amount);
        // 方法结束时自动提交
    }

    @Transactional(rollbackFor = Exception.class)
    public void transferMoneyWithRollback(int fromId, int toId, double amount)
            throws Exception {
        // 任何异常都回滚
        accountRepository.debit(fromId, amount);
        if (someCondition()) {
            throw new Exception("Transfer failed");
        }
        accountRepository.credit(toId, amount);
    }
}
```

#### 隔离级别设置

```java
@Service
public class TransactionalService {

    // READ COMMITTED（默认）
    @Transactional(isolation = Isolation.READ_COMMITTED)
    public void readCommittedOperation() {
        // 操作
    }

    // REPEATABLE READ
    @Transactional(isolation = Isolation.REPEATABLE_READ)
    public void repeatableReadOperation() {
        // 操作
    }

    // SERIALIZABLE
    @Transactional(isolation = Isolation.SERIALIZABLE)
    public void serializableOperation() {
        // 操作
    }
}
```

#### 传播行为

```java
@Service
public class PropagationService {

    @Transactional(propagation = Propagation.REQUIRED)
    public void requiredTransaction() {
        // 如果存在事务则加入，否则创建新事务
    }

    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void requiresNewTransaction() {
        // 总是创建新事务
    }

    @Transactional(propagation = Propagation.NESTED)
    public void nestedTransaction() {
        // 嵌套事务（使用SAVEPOINT）
    }

    @Transactional(propagation = Propagation.NOT_SUPPORTED)
    public void notSupportedTransaction() {
        // 挂起当前事务，以非事务方式执行
    }
}
```

### 3.2 事务管理器配置

#### DataSourceTransactionManager

```java
import org.springframework.jdbc.datasource.DataSourceTransactionManager;
import org.springframework.transaction.PlatformTransactionManager;

@Configuration
@EnableTransactionManagement
public class TransactionConfig {

    @Bean
    public PlatformTransactionManager transactionManager(DataSource dataSource) {
        DataSourceTransactionManager tm = new DataSourceTransactionManager();
        tm.setDataSource(dataSource);

        // 设置默认超时（5秒）
        tm.setDefaultTimeout(5);

        // 设置是否允许嵌套事务
        tm.setNestedTransactionAllowed(true);

        return tm;
    }
}
```

#### JpaTransactionManager

```java
import org.springframework.orm.jpa.JpaTransactionManager;

@Configuration
@EnableTransactionManagement
public class JpaTransactionConfig {

    @Bean
    public PlatformTransactionManager transactionManager(EntityManagerFactory emf) {
        JpaTransactionManager tm = new JpaTransactionManager();
        tm.setEntityManagerFactory(emf);

        // 设置默认超时
        tm.setDefaultTimeout(5);

        return tm;
    }
}
```

### 3.3 事务回滚策略

#### 异常回滚配置

```java
@Service
public class RollbackService {

    // 默认：RuntimeException和Error回滚
    @Transactional
    public void defaultRollback() {
        throw new RuntimeException("Will rollback");
    }

    // 指定异常回滚
    @Transactional(rollbackFor = {SQLException.class, IOException.class})
    public void customRollback() throws SQLException {
        throw new SQLException("Will rollback");
    }

    // 指定异常不回滚
    @Transactional(noRollbackFor = {BusinessException.class})
    public void noRollback() {
        throw new BusinessException("Will NOT rollback");
    }
}
```

#### 自定义回滚规则

```java
import org.springframework.transaction.interceptor.RuleBasedTransactionAttribute;

@Configuration
public class CustomTransactionConfig {

    @Bean
    public TransactionAttribute customTransactionAttribute() {
        RuleBasedTransactionAttribute attr = new RuleBasedTransactionAttribute();

        // 添加回滚规则
        attr.getRollbackRules().add(new RollbackRuleAttribute(SQLException.class));
        attr.getRollbackRules().add(new NoRollbackRuleAttribute(BusinessException.class));

        // 设置超时
        attr.setTimeout(5);

        return attr;
    }
}
```

---

## 🔧 第四部分：MVCC最佳实践

### 4.1 短事务原则

#### 避免长事务

```java
// ❌ 错误示例：长事务
@Service
public class BadService {
    @Transactional
    public void badMethod() {
        // 耗时操作在事务内
        processLargeDataset();  // 耗时10分钟

        accountRepository.update();
        // 事务持有10分钟，导致表膨胀
    }
}

// ✅ 正确示例：短事务
@Service
public class GoodService {
    public void goodMethod() {
        // 先处理数据（事务外）
        List<Result> results = processLargeDataset();

        // 再批量更新（短事务）
        for (List<Result> batch : batchProcess(results, 1000)) {
            updateBatch(batch);
        }
    }

    @Transactional
    private void updateBatch(List<Result> batch) {
        // 短事务，每1000条提交
        accountRepository.batchUpdate(batch);
    }
}
```

#### 批量操作优化

```java
@Service
public class BatchService {

    @Transactional
    public void batchInsert(List<Entity> entities) {
        // 使用批量插入
        for (int i = 0; i < entities.size(); i += 1000) {
            List<Entity> batch = entities.subList(i,
                Math.min(i + 1000, entities.size()));
            repository.batchInsert(batch);
        }
    }

    // 使用JDBC批量操作
    public void jdbcBatchInsert(Connection conn, List<Entity> entities)
            throws SQLException {
        String sql = "INSERT INTO table (col1, col2) VALUES (?, ?)";

        try (PreparedStatement stmt = conn.prepareStatement(sql)) {
            conn.setAutoCommit(false);

            for (Entity entity : entities) {
                stmt.setString(1, entity.getCol1());
                stmt.setString(2, entity.getCol2());
                stmt.addBatch();

                // 每1000条执行一次
                if (stmt.getParameterMetaData().getParameterCount() % 1000 == 0) {
                    stmt.executeBatch();
                    conn.commit();
                }
            }

            // 执行剩余批次
            stmt.executeBatch();
            conn.commit();
        }
    }
}
```

### 4.2 并发控制

#### SELECT FOR UPDATE使用

```java
@Service
public class InventoryService {

    @Transactional(isolation = Isolation.REPEATABLE_READ)
    public boolean deductStock(int productId, int quantity) {
        // 使用SELECT FOR UPDATE加锁
        Inventory inventory = inventoryRepository.findByIdForUpdate(productId);

        if (inventory.getStock() < quantity) {
            throw new InsufficientStockException();
        }

        inventory.setStock(inventory.getStock() - quantity);
        inventoryRepository.save(inventory);

        return true;
    }
}

// Repository方法
public interface InventoryRepository extends JpaRepository<Inventory, Integer> {
    @Query("SELECT i FROM Inventory i WHERE i.productId = :productId FOR UPDATE")
    Inventory findByIdForUpdate(@Param("productId") int productId);
}
```

#### 乐观锁实现

```java
@Entity
public class Account {
    @Id
    private Integer id;

    private Double balance;

    @Version  // JPA乐观锁版本号
    private Integer version;

    // getters and setters
}

@Service
public class OptimisticLockService {

    @Transactional
    public void updateWithOptimisticLock(int accountId, double newBalance) {
        Account account = accountRepository.findById(accountId)
            .orElseThrow(() -> new AccountNotFoundException());

        // 检查版本号（JPA自动处理）
        account.setBalance(newBalance);
        accountRepository.save(account);
        // 如果版本号不匹配，会抛出OptimisticLockingFailureException
    }
}
```

#### 悲观锁实现

```java
@Service
public class PessimisticLockService {

    @Transactional(isolation = Isolation.REPEATABLE_READ)
    public void updateWithPessimisticLock(int accountId, double newBalance) {
        // 使用悲观锁
        Account account = accountRepository.findById(accountId)
            .orElseThrow(() -> new AccountNotFoundException());

        // JPA会自动加锁（SELECT FOR UPDATE）
        account.setBalance(newBalance);
        accountRepository.save(account);
    }
}

// Repository方法
public interface AccountRepository extends JpaRepository<Account, Integer> {
    @Lock(LockModeType.PESSIMISTIC_WRITE)
    @Query("SELECT a FROM Account a WHERE a.id = :id")
    Optional<Account> findByIdWithLock(@Param("id") Integer id);
}
```

### 4.3 性能优化

#### PreparedStatement使用

```java
public class PreparedStatementExample {

    public void usePreparedStatement(Connection conn, List<String> names)
            throws SQLException {
        String sql = "SELECT * FROM users WHERE name = ?";

        try (PreparedStatement stmt = conn.prepareStatement(sql)) {
            for (String name : names) {
                stmt.setString(1, name);
                try (ResultSet rs = stmt.executeQuery()) {
                    // 处理结果
                }
            }
        }
    }
}
```

#### 批量操作

```java
@Service
public class BatchOperationService {

    @Transactional
    public void batchUpdate(List<Account> accounts) {
        // Spring Data JPA批量更新
        accountRepository.saveAll(accounts);
    }

    // JDBC批量操作（性能最优）
    public void jdbcBatchUpdate(Connection conn, List<Account> accounts)
            throws SQLException {
        String sql = "UPDATE accounts SET balance = ? WHERE id = ?";

        try (PreparedStatement stmt = conn.prepareStatement(sql)) {
            conn.setAutoCommit(false);

            for (Account account : accounts) {
                stmt.setDouble(1, account.getBalance());
                stmt.setInt(2, account.getId());
                stmt.addBatch();
            }

            stmt.executeBatch();
            conn.commit();
        }
    }
}
```

#### 连接池优化

```java
@Configuration
public class OptimizedHikariConfig {

    @Bean
    public HikariDataSource dataSource() {
        HikariConfig config = new HikariConfig();

        // 根据系统资源调整
        int cores = Runtime.getRuntime().availableProcessors();

        config.setMinimumIdle(cores);
        config.setMaximumPoolSize(cores * 2);

        // 连接泄漏检测（防止长事务）
        config.setLeakDetectionThreshold(60000);  // 60秒

        // MVCC优化
        config.addDataSourceProperty("ApplicationName", "myapp");
        config.addDataSourceProperty("reWriteBatchedInserts", "true");

        return new HikariDataSource(config);
    }
}
```

---

## 📈 第五部分：实际场景案例

### 5.1 电商库存扣减场景

```java
@Service
public class InventoryService {

    private final InventoryRepository repository;

    @Transactional(isolation = Isolation.REPEATABLE_READ)
    public boolean deductStock(int productId, int quantity) {
        // 使用SELECT FOR UPDATE加锁
        Inventory inventory = repository.findByIdForUpdate(productId)
            .orElseThrow(() -> new ProductNotFoundException());

        if (inventory.getStock() < quantity) {
            throw new InsufficientStockException();
        }

        inventory.setStock(inventory.getStock() - quantity);
        repository.save(inventory);

        return true;
    }

    // 带重试的库存扣减
    @Retryable(value = {DeadlockLoserDataAccessException.class}, maxAttempts = 5)
    @Transactional(isolation = Isolation.REPEATABLE_READ)
    public boolean deductStockWithRetry(int productId, int quantity) {
        return deductStock(productId, quantity);
    }
}
```

### 5.2 银行转账场景

```java
@Service
public class TransferService {

    private final AccountRepository accountRepository;

    @Transactional(isolation = Isolation.REPEATABLE_READ)
    public void transfer(int fromId, int toId, double amount) {
        // 检查余额
        Account fromAccount = accountRepository.findById(fromId)
            .orElseThrow(() -> new AccountNotFoundException());

        if (fromAccount.getBalance() < amount) {
            throw new InsufficientBalanceException();
        }

        // 扣减转出账户
        fromAccount.setBalance(fromAccount.getBalance() - amount);
        accountRepository.save(fromAccount);

        // 增加转入账户
        Account toAccount = accountRepository.findById(toId)
            .orElseThrow(() -> new AccountNotFoundException());
        toAccount.setBalance(toAccount.getBalance() + amount);
        accountRepository.save(toAccount);
    }

    // SERIALIZABLE隔离级别，自动重试序列化错误
    @Retryable(value = {SerializationFailureException.class}, maxAttempts = 5)
    @Transactional(isolation = Isolation.SERIALIZABLE)
    public void transferSerializable(int fromId, int toId, double amount) {
        transfer(fromId, toId, amount);
    }
}
```

### 5.3 日志写入场景

```java
@Service
public class LogService {

    private final LogRepository logRepository;
    private final List<Log> buffer = new ArrayList<>();
    private static final int BUFFER_SIZE = 1000;

    public void writeLog(String message, String level) {
        synchronized (buffer) {
            buffer.add(new Log(message, level));

            if (buffer.size() >= BUFFER_SIZE) {
                flush();
            }
        }
    }

    @Transactional
    public void flush() {
        synchronized (buffer) {
            if (!buffer.isEmpty()) {
                logRepository.saveAll(buffer);
                buffer.clear();
            }
        }
    }

    @PreDestroy
    public void cleanup() {
        flush();
    }
}
```

---

## 📝 第六部分：常见问题和解决方案

### 6.1 常见错误

#### 错误1：连接泄漏

```java
// ❌ 错误示例：忘记关闭连接
public void badExample() throws SQLException {
    Connection conn = dataSource.getConnection();
    PreparedStatement stmt = conn.prepareStatement("SELECT * FROM table");
    ResultSet rs = stmt.executeQuery();
    // 忘记关闭连接和语句
}

// ✅ 正确示例：使用try-with-resources
public void goodExample() throws SQLException {
    try (Connection conn = dataSource.getConnection();
         PreparedStatement stmt = conn.prepareStatement("SELECT * FROM table");
         ResultSet rs = stmt.executeQuery()) {
        // 自动关闭资源
    }
}
```

#### 错误2：事务嵌套问题

```java
// ❌ 错误示例：事务嵌套导致问题
@Service
public class BadNestedService {
    @Transactional
    public void outerMethod() {
        innerMethod();  // 内部方法也是@Transactional
    }

    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void innerMethod() {
        // 创建新事务，可能导致数据不一致
    }
}

// ✅ 正确示例：合理使用传播行为
@Service
public class GoodNestedService {
    @Transactional
    public void outerMethod() {
        // 业务逻辑
        innerMethod();  // 加入当前事务
    }

    @Transactional(propagation = Propagation.REQUIRED)
    public void innerMethod() {
        // 加入外层事务
    }
}
```

### 6.2 性能问题

#### 问题1：N+1查询问题

```java
// ❌ 错误示例：N+1查询
@Service
public class BadQueryService {
    public List<Order> getOrders() {
        List<Order> orders = orderRepository.findAll();
        for (Order order : orders) {
            // 每个订单都查询一次用户（N+1问题）
            User user = userRepository.findById(order.getUserId());
            order.setUser(user);
        }
        return orders;
    }
}

// ✅ 正确示例：使用JOIN FETCH
@Service
public class GoodQueryService {
    public List<Order> getOrders() {
        // 一次查询获取所有数据
        return orderRepository.findAllWithUser();
    }
}

// Repository方法
public interface OrderRepository extends JpaRepository<Order, Integer> {
    @Query("SELECT o FROM Order o JOIN FETCH o.user")
    List<Order> findAllWithUser();
}
```

### 6.3 调试技巧

#### 查看事务信息

```java
import org.springframework.transaction.support.TransactionSynchronizationManager;

@Service
public class TransactionDebugService {

    public void debugTransaction() {
        // 检查是否在事务中
        boolean isActive = TransactionSynchronizationManager.isActualTransactionActive();
        System.out.println("Transaction active: " + isActive);

        // 查看当前事务名称
        String transactionName = TransactionSynchronizationManager.getCurrentTransactionName();
        System.out.println("Transaction name: " + transactionName);

        // 查看是否只读事务
        boolean isReadOnly = TransactionSynchronizationManager.isCurrentTransactionReadOnly();
        System.out.println("Read-only: " + isReadOnly);
    }
}
```

---

## 🎯 总结

### 核心最佳实践

1. **使用HikariCP连接池**：高性能、低延迟
2. **短事务原则**：避免在事务内执行耗时操作
3. **批量操作**：使用PreparedStatement批量操作
4. **错误重试**：实现死锁和序列化错误的重试机制
5. **Spring事务管理**：合理使用@Transactional注解

### 关键配置

- **连接池大小**：minimumIdle=5, maximumPoolSize=20
- **连接泄漏检测**：leakDetectionThreshold=60000（60秒）
- **事务超时**：defaultTimeout=5秒
- **隔离级别**：默认READ COMMITTED，必要时使用REPEATABLE READ

### MVCC影响

- ✅ 短事务减少表膨胀
- ✅ 批量操作提高性能
- ✅ 合理使用锁避免死锁
- ✅ Spring事务管理简化开发

PostgreSQL 17/18的MVCC机制在Java驱动下表现优异，通过HikariCP连接池和Spring事务管理，可以实现高性能、高可靠性的企业级应用。
