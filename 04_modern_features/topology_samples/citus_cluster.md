# Citus 集群样例（示意）

- coordinator: 1 节点
- workers: N 节点（每节点 replicas=k）
- 与 HA 方案：每个节点依旧可用物理/逻辑复制实现 HA/DR
- 入口：路由到 coordinator；监控路由/重分布/失败重试
