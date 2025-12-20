(*
 * 串行化证明 - TLA+规范
 * 
 * 本文件包含冲突可串行化和SSI算法的完整TLA+规范
 * 对应文档: 03-串行化证明.md
 *)

EXTENDS Naturals, Sequences, TLC

CONSTANTS Transactions, Resources

VARIABLES schedule, conflict_graph, serial_order, committed

(* ============================================
   类型定义
   ============================================ *)

OpType == {"read", "write"}

Operation == [tx |-> TransactionId, op |-> OpType, res |-> Resources, ts |-> Nat]

(* ============================================
   类型不变量
   ============================================ *)

TypeOK ==
    /\ schedule \in Seq(Operation)
    /\ conflict_graph \in [Transactions -> SUBSET Transactions]
    /\ serial_order \in Seq(Transactions)
    /\ committed \in SUBSET Transactions

(* ============================================
   初始状态
   ============================================ *)

Init ==
    /\ schedule = <<>>
    /\ conflict_graph = [t \in Transactions |-> {}]
    /\ serial_order = <<>>
    /\ committed = {}

(* ============================================
   冲突定义
   ============================================ *)

Conflict(op1, op2) ==
    /\ op1.tx # op2.tx
    /\ op1.res = op2.res
    /\ (op1.op = "read" /\ op2.op = "write") \/
       (op1.op = "write" /\ op2.op = "read") \/
       (op1.op = "write" /\ op2.op = "write")

(* ============================================
   构建冲突图
   ============================================ *)

BuildConflictGraph ==
    LET all_ops == [i \in 1..Len(schedule) |-> schedule[i]]
        conflicts == {<<i, j>> \in DOMAIN all_ops \X DOMAIN all_ops:
                        i < j /\ Conflict(all_ops[i], all_ops[j])}
    IN conflict_graph' = [t \in Transactions |->
                            {all_ops[j].tx : <<i, j>> \in conflicts /\ all_ops[i].tx = t}]
    /\ UNCHANGED <<schedule, serial_order, committed>>

(* ============================================
   检测环（DFS）
   ============================================ *)

HasCycle ==
    LET visited == {}
        rec_stack == {}
        DFS(node) ==
            IF node \in rec_stack THEN TRUE
            ELSE IF node \in visited THEN FALSE
            ELSE LET visited' == visited \cup {node}
                     rec_stack' == rec_stack \cup {node}
                 IN \E neighbor \in conflict_graph[node]:
                     DFS(neighbor)
    IN \E start \in Transactions: DFS(start)

IsAcyclic == ~HasCycle

(* ============================================
   拓扑排序
   ============================================ *)

TopologicalSort ==
    /\ IsAcyclic
    /\ serial_order' \in Permutations(Transactions)
    /\ \A i, j \in DOMAIN serial_order':
        (i < j) => (serial_order'[j] \notin conflict_graph[serial_order'[i]])

(* ============================================
   冲突可串行化判定
   ============================================ *)

ConflictSerializable ==
    /\ BuildConflictGraph
    /\ IsAcyclic
    /\ TopologicalSort
    /\ UNCHANGED <<schedule, committed>>

(* ============================================
   提交事务
   ============================================ *)

CommitTransaction(tx) ==
    /\ tx \in Transactions
    /\ tx \notin committed
    /\ committed' = committed \cup {tx}
    /\ UNCHANGED <<schedule, conflict_graph, serial_order>>

(* ============================================
   下一步
   ============================================ *)

Next ==
    \/ ConflictSerializable
    \/ \E tx \in Transactions: CommitTransaction(tx)

Spec == Init /\ [][Next]_<<schedule, conflict_graph, serial_order, committed>>

(* ============================================
   安全性不变量
   ============================================ *)

Invariant ==
    /\ IsAcyclic => \E order \in Permutations(Transactions):
                      (\A i, j \in DOMAIN order:
                          (i < j) => (order[j] \notin conflict_graph[order[i]]))
    /\ ~IsAcyclic => ~(\E order \in Permutations(Transactions):
                          (\A i, j \in DOMAIN order:
                              (i < j) => (order[j] \notin conflict_graph[order[i]])))

THEOREM Serializability_Safety ==
    Spec => []Invariant
