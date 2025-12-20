(*
 * SSI算法 - TLA+规范
 * 
 * 本文件包含SSI（Serializable Snapshot Isolation）算法的完整TLA+规范
 * 对应文档: 03-串行化证明.md
 *)

EXTENDS Naturals, Sequences, TLC

CONSTANTS Transactions, Resources

VARIABLES schedule, rw_dependencies, dangerous_structures, aborted

(* ============================================
   类型定义
   ============================================ *)

OpType == {"read", "write"}

Operation == [tx |-> TransactionId, op |-> OpType, res |-> Resources, ts |-> Nat]

RWDependency == [reader |-> TransactionId, writer |-> TransactionId, resource |-> Resources]

(* ============================================
   类型不变量
   ============================================ *)

TypeOK ==
    /\ schedule \in Seq(Operation)
    /\ rw_dependencies \in Seq(RWDependency)
    /\ dangerous_structures \in SUBSET (Transactions \X Transactions)
    /\ aborted \in SUBSET Transactions

(* ============================================
   初始状态
   ============================================ *)

Init ==
    /\ schedule = <<>>
    /\ rw_dependencies = <<>>
    /\ dangerous_structures = {}
    /\ aborted = {}

(* ============================================
   检测rw依赖
   ============================================ *)

DetectRWDependency ==
    LET all_ops == [i \in 1..Len(schedule) |-> schedule[i]]
        new_deps == {[reader |-> all_ops[i].tx, writer |-> all_ops[j].tx, resource |-> all_ops[i].res] :
                        <<i, j>> \in DOMAIN all_ops \X DOMAIN all_ops /\
                        i < j /\
                        all_ops[i].op = "read" /\
                        all_ops[j].op = "write" /\
                        all_ops[i].res = all_ops[j].res}
    IN rw_dependencies' = rw_dependencies \o Seq(new_deps)
       /\ UNCHANGED <<schedule, dangerous_structures, aborted>>

(* ============================================
   检测危险结构
   ============================================ *)

DetectDangerousStructure ==
    LET dep_graph == [t \in Transactions |->
                        {dep.writer : dep \in rw_dependencies /\ dep.reader = t}]
        has_cycle(t1, t2) ==
            t2 \in dep_graph[t1] /\ t1 \in dep_graph[t2]
    IN dangerous_structures' = {<<t1, t2>> \in Transactions \X Transactions : has_cycle(t1, t2)}
       /\ UNCHANGED <<schedule, rw_dependencies, aborted>>

(* ============================================
   中止事务（检测到危险结构）
   ============================================ *)

AbortTransaction(tx) ==
    /\ tx \in Transactions
    /\ \E other_tx \in Transactions :
        <<tx, other_tx>> \in dangerous_structures \/
        <<other_tx, tx>> \in dangerous_structures
    /\ aborted' = aborted \cup {tx}
    /\ UNCHANGED <<schedule, rw_dependencies, dangerous_structures>>

(* ============================================
   提交事务
   ============================================ *)

CommitTransaction(tx) ==
    /\ tx \in Transactions
    /\ tx \notin aborted
    /\ \A other_tx \in Transactions :
        ~(<<tx, other_tx>> \in dangerous_structures) /\
        ~(<<other_tx, tx>> \in dangerous_structures)
    /\ UNCHANGED <<schedule, rw_dependencies, dangerous_structures, aborted>>

(* ============================================
   下一步
   ============================================ *)

Next ==
    \/ DetectRWDependency
    \/ DetectDangerousStructure
    \/ \E tx \in Transactions: AbortTransaction(tx)
    \/ \E tx \in Transactions: CommitTransaction(tx)

Spec == Init /\ [][Next]_<<schedule, rw_dependencies, dangerous_structures, aborted>>

(* ============================================
   安全性不变量
   ============================================ *)

Invariant ==
    /\ \A tx1, tx2 \in Transactions :
        (<<tx1, tx2>> \in dangerous_structures) =>
        (tx1 \in aborted \/ tx2 \in aborted)
    /\ \A tx \in Transactions :
        (tx \in aborted) =>
        (\E other_tx \in Transactions :
            <<tx, other_tx>> \in dangerous_structures \/
            <<other_tx, tx>> \in dangerous_structures)

THEOREM SSI_Safety ==
    Spec => []Invariant
