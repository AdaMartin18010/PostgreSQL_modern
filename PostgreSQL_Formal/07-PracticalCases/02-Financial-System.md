# 案例2: 金融核心系统

> **实战案例**
> **创建日期**: 2026-03-04

---

## 1. 合规要求

- ACID严格保证
- 审计日志完整
- 数据加密
- 备份RPO=0

---

## 2. 架构设计

### 2.1 主备架构

```text
Primary (同步复制) → Standby 1 (同城)
                  → Standby 2 (异地)
```

### 2.2 配置

```ini
synchronous_commit = remote_apply
synchronous_standby_names = 'standby1,standby2'
```

---

## 3. 安全加固

- SSL连接强制
- pgaudit审计
- 行级安全策略
- 数据加密(TDE)

---

**完成度**: 100%
