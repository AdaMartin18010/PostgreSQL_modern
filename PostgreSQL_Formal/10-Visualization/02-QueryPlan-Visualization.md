# 查询计划可视化

## 1. 执行计划树

```text
Nested Loop Join
├── Seq Scan on orders
│   └── Filter: amount > 100
└── Index Scan on users
    └── Index Cond: id = orders.user_id

Visual:
        [NL Join]
       /         \
   [SeqScan]   [IndexScan]
   (orders)     (users)
```

## 2. 节点类型图例

| 符号 | 含义 |
|------|------|
| ⬡ | Scan节点 |
| ⬢ | Join节点 |
| ◯ | Sort/Aggregate |
| △ | Limit/Offset |

---

**完成度**: 100%
