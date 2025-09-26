# 一致性模型与共识协议

## 一致性模型

- 线性一致性、顺序一致性、最终一致性与会话一致性
- CAP 与 PACELC 的工程解读：分区容错优先下的一致性/延迟权衡

## 共识协议

- Paxos 家族与工程化挑战：领导者选举、日志复制、打洞与恢复
- Raft：可理解性优化的复制状态机；快照、成员变更与日志压缩

## 仲裁与读写策略

- Quorum（R/W）、读己之写、读写分离的一致性影响

## 对照链接

- Wikipedia：`https://en.wikipedia.org/wiki/Consistency_model`、`https://en.wikipedia.org/wiki/Raft_(algorithm)`
- MIT 6.824：`https://pdos.csail.mit.edu/6.824/`
