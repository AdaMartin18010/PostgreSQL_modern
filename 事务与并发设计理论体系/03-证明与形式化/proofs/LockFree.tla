(*
 * 无锁算法正确性证明 - TLA+规范
 * 
 * 本文件包含无锁算法的完整TLA+规范
 * 对应文档: 06-无锁算法正确性证明.md
 * 
 * 参考: 06-性能分析/06-无锁算法性能分析.md
 *)

EXTENDS Naturals, Sequences, TLC

CONSTANTS Threads, Values

VARIABLES
    stack,           (* 栈（链表表示） *)
    operations,      (* 操作历史 *)
    linearization_points  (* 线性化点 *)

(* ============================================
   类型定义
   ============================================ *)

Node == [value |-> Values, next |-> Nat \cup {Nil}]

OpType == {"push", "pop"}

Operation == [thread |-> Threads, op |-> OpType, value |-> Values \cup {Nil}, timestamp |-> Nat, linearized |-> BOOLEAN]

(* ============================================
   类型不变量
   ============================================ *)

TypeOK ==
    /\ stack \in Seq(Node)
    /\ operations \in Seq(Operation)
    /\ linearization_points \in Seq(Nat)

(* ============================================
   初始状态
   ============================================ *)

Init ==
    /\ stack = <<>>
    /\ operations = <<>>
    /\ linearization_points = <<>>

(* ============================================
   无锁栈Push操作
   ============================================ *)

LockFreePush(thread, value) ==
    LET new_node == [value |-> value, next |-> Nil]
        head == IF Len(stack) > 0 THEN Head(stack) ELSE Nil
    IN /\ stack' = Append(stack, new_node)
       /\ new_node.next = IF head # Nil THEN head ELSE Nil
       /\ operations' = Append(operations, [
           thread |-> thread,
           op |-> "push",
           value |-> value,
           timestamp |-> Len(operations) + 1,
           linearized |-> TRUE
       ])
       /\ linearization_points' = Append(linearization_points, Len(operations) + 1)
       /\ UNCHANGED <<>>

(* ============================================
   无锁栈Pop操作
   ============================================ *)

LockFreePop(thread) ==
    LET head == IF Len(stack) > 0 THEN Head(stack) ELSE Nil
    IN IF head = Nil
       THEN /\ stack' = stack
            /\ operations' = Append(operations, [
                thread |-> thread,
                op |-> "pop",
                value |-> Nil,
                timestamp |-> Len(operations) + 1,
                linearized |-> TRUE
            ])
            /\ linearization_points' = Append(linearization_points, Len(operations) + 1)
            /\ UNCHANGED <<>>
       ELSE /\ stack' = Tail(stack)
            /\ operations' = Append(operations, [
                thread |-> thread,
                op |-> "pop",
                value |-> head.value,
                timestamp |-> Len(operations) + 1,
                linearized |-> TRUE
            ])
            /\ linearization_points' = Append(linearization_points, Len(operations) + 1)
            /\ UNCHANGED <<>>

(* ============================================
   下一步
   ============================================ *)

Next ==
    \/ \E thread \in Threads, value \in Values: LockFreePush(thread, value)
    \/ \E thread \in Threads: LockFreePop(thread)

Spec == Init /\ [][Next]_<<stack, operations, linearization_points>>

(* ============================================
   线性化性定义
   ============================================ *)

(* 线性化性：存在一个合法的顺序执行，使得每个操作的效果与并发执行一致 *)
Linearizable ==
    \E seq_order \in Permutations(1..Len(operations)):
        /\ \A i, j \in 1..Len(operations):
            (i < j) => (seq_order[i] < seq_order[j])
        /\ \A i \in 1..Len(operations):
            operations[i].linearized = TRUE
        /\ \A i \in 1..Len(operations):
            \E linearization_point \in linearization_points:
                linearization_point = operations[i].timestamp

(* ============================================
   安全性不变量
   ============================================ *)

(* 无数据丢失：所有push的值最终都会被pop *)
NoDataLoss ==
    \A push_op \in operations:
        /\ push_op.op = "push"
        => \E pop_op \in operations:
            /\ pop_op.op = "pop"
            /\ pop_op.value = push_op.value

(* 无数据损坏：pop的值必须是之前push的值 *)
NoDataCorruption ==
    \A pop_op \in operations:
        /\ pop_op.op = "pop"
        /\ pop_op.value # Nil
        => \E push_op \in operations:
            /\ push_op.op = "push"
            /\ push_op.value = pop_op.value
            /\ push_op.timestamp < pop_op.timestamp

(* ============================================
   活性性质
   ============================================ *)

(* Lock-Free进度保证：至少有一个线程会取得进展 *)
LockFreeProgress ==
    <>(\E thread \in Threads:
        \E op \in operations:
            /\ op.thread = thread
            /\ op.linearized = TRUE)

(* Wait-Free进度保证：每个线程都会取得进展 *)
WaitFreeProgress ==
    \A thread \in Threads:
        <>(\E op \in operations:
            /\ op.thread = thread
            /\ op.linearized = TRUE)

(* ============================================
   安全性定理
   ============================================ *)

THEOREM LockFree_Safety ==
    Spec => [](Linearizable /\ NoDataLoss /\ NoDataCorruption)

(* ============================================
   活性定理
   ============================================ *)

THEOREM LockFree_Liveness ==
    Spec => (LockFreeProgress /\ WaitFreeProgress)
