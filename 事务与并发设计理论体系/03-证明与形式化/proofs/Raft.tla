(*
 * Raft共识协议证明 - TLA+规范
 * 
 * 本文件包含Raft共识协议的完整TLA+规范
 * 对应文档: 05-共识协议证明.md
 *)

EXTENDS Naturals, Sequences, TLC

CONSTANTS Servers, Clients

VARIABLES
    currentTerm,      (* 当前任期 *)
    votedFor,        (* 投票给谁 *)
    log,             (* 日志 *)
    commitIndex,     (* 提交索引 *)
    lastApplied,     (* 最后应用索引 *)
    state,           (* FOLLOWER/CANDIDATE/LEADER *)
    nextIndex,       (* 下一个发送索引 *)
    matchIndex       (* 匹配索引 *)

(* ============================================
   类型定义
   ============================================ *)

LogEntry == [term |-> Nat, command |-> STRING]

ServerState == {"FOLLOWER", "CANDIDATE", "LEADER"}

(* ============================================
   类型不变量
   ============================================ *)

TypeOK ==
    /\ currentTerm \in [Servers -> Nat]
    /\ votedFor \in [Servers -> Servers \cup {Nil}]
    /\ log \in [Servers -> Seq(LogEntry)]
    /\ commitIndex \in [Servers -> Nat]
    /\ lastApplied \in [Servers -> Nat]
    /\ state \in [Servers -> ServerState]
    /\ nextIndex \in [Servers -> [Servers -> Nat]]
    /\ matchIndex \in [Servers -> [Servers -> Nat]]
    /\ \A s \in Servers:
        /\ commitIndex[s] <= Len(log[s])
        /\ lastApplied[s] <= commitIndex[s]

(* ============================================
   初始状态
   ============================================ *)

Init ==
    /\ currentTerm = [s \in Servers |-> 0]
    /\ votedFor = [s \in Servers |-> Nil]
    /\ log = [s \in Servers |-> <<>>]
    /\ commitIndex = [s \in Servers |-> 0]
    /\ lastApplied = [s \in Servers |-> 0]
    /\ state = [s \in Servers |-> "FOLLOWER"]
    /\ nextIndex = [s \in Servers |-> [t \in Servers |-> 1]]
    /\ matchIndex = [s \in Servers |-> [t \in Servers |-> 0]]

(* ============================================
   选举请求投票
   ============================================ *)

RequestVote(s, c) ==
    /\ state[s] = "FOLLOWER"
    /\ currentTerm[c] > currentTerm[s]
    /\ \/ votedFor[s] = Nil
       \/ votedFor[s] = c
    /\ votedFor' = [votedFor EXCEPT ![s] = c]
    /\ currentTerm' = [currentTerm EXCEPT ![s] = currentTerm[c]]
    /\ state' = [state EXCEPT ![s] = "FOLLOWER"]
    /\ UNCHANGED <<log, commitIndex, lastApplied, nextIndex, matchIndex>>

(* ============================================
   成为候选者
   ============================================ *)

BecomeCandidate(s) ==
    /\ state[s] = "FOLLOWER"
    /\ currentTerm' = [currentTerm EXCEPT ![s] = currentTerm[s] + 1]
    /\ votedFor' = [votedFor EXCEPT ![s] = s]
    /\ state' = [state EXCEPT ![s] = "CANDIDATE"]
    /\ UNCHANGED <<log, commitIndex, lastApplied, nextIndex, matchIndex>>

(* ============================================
   成为领导者
   ============================================ *)

BecomeLeader(s) ==
    /\ state[s] = "CANDIDATE"
    /\ \A t \in Servers:
        (t # s) => (votedFor[t] = s \/ votedFor[t] = Nil)
    /\ Cardinality({t \in Servers : votedFor[t] = s}) > Cardinality(Servers) \div 2
    /\ state' = [state EXCEPT ![s] = "LEADER"]
    /\ nextIndex' = [nextIndex EXCEPT ![s] = [t \in Servers |-> Len(log[s]) + 1]]
    /\ matchIndex' = [matchIndex EXCEPT ![s] = [t \in Servers |-> 0]]
    /\ UNCHANGED <<currentTerm, votedFor, log, commitIndex, lastApplied>>

(* ============================================
   追加日志条目
   ============================================ *)

AppendEntries(s, l) ==
    /\ state[s] = "LEADER"
    /\ l' = Append(log[s], [term |-> currentTerm[s], command |-> "cmd"])
    /\ log' = [log EXCEPT ![s] = l']
    /\ UNCHANGED <<currentTerm, votedFor, commitIndex, lastApplied, state, nextIndex, matchIndex>>

(* ============================================
   复制日志到跟随者
   ============================================ *)

ReplicateLog(leader, follower) ==
    /\ state[leader] = "LEADER"
    /\ state[follower] = "FOLLOWER"
    /\ currentTerm[leader] >= currentTerm[follower]
    /\ \A i \in 1..(nextIndex[leader][follower] - 1):
        log[leader][i].term = log[follower][i].term
    /\ log' = [log EXCEPT ![follower] = 
                SubSeq(log[leader], 1, nextIndex[leader][follower] - 1) \o
                SubSeq(log[leader], nextIndex[leader][follower], Len(log[leader]))]
    /\ nextIndex' = [nextIndex EXCEPT ![leader][follower] = Len(log'[follower]) + 1]
    /\ matchIndex' = [matchIndex EXCEPT ![leader][follower] = Len(log'[follower])]
    /\ currentTerm' = [currentTerm EXCEPT ![follower] = currentTerm[leader]]
    /\ UNCHANGED <<votedFor, commitIndex, lastApplied, state>>

(* ============================================
   提交日志
   ============================================ *)

CommitLog(s) ==
    /\ state[s] = "LEADER"
    /\ \E n \in 1..Len(log[s]):
        /\ n > commitIndex[s]
        /\ Cardinality({t \in Servers : matchIndex[s][t] >= n}) > Cardinality(Servers) \div 2
        /\ log[s][n].term = currentTerm[s]
    /\ commitIndex' = [commitIndex EXCEPT ![s] = n]
    /\ UNCHANGED <<currentTerm, votedFor, log, lastApplied, state, nextIndex, matchIndex>>

(* ============================================
   应用日志
   ============================================ *)

ApplyLog(s) ==
    /\ lastApplied[s] < commitIndex[s]
    /\ lastApplied' = [lastApplied EXCEPT ![s] = commitIndex[s]]
    /\ UNCHANGED <<currentTerm, votedFor, log, commitIndex, state, nextIndex, matchIndex>>

(* ============================================
   下一步
   ============================================ *)

Next ==
    \/ \E s \in Servers: BecomeCandidate(s)
    \/ \E s \in Servers: BecomeLeader(s)
    \/ \E s, c \in Servers: RequestVote(s, c)
    \/ \E s \in Servers: AppendEntries(s, log[s])
    \/ \E leader, follower \in Servers: ReplicateLog(leader, follower)
    \/ \E s \in Servers: CommitLog(s)
    \/ \E s \in Servers: ApplyLog(s)

Spec == Init /\ [][Next]_<<currentTerm, votedFor, log, commitIndex, lastApplied, state, nextIndex, matchIndex>>

(* ============================================
   安全性不变量
   ============================================ *)

(* 选举安全性：每个任期最多一个Leader *)
ElectionSafety ==
    \A s1, s2 \in Servers:
        /\ state[s1] = "LEADER"
        /\ state[s2] = "LEADER"
        /\ currentTerm[s1] = currentTerm[s2]
        => s1 = s2

(* 日志匹配性：相同索引和任期的日志条目相同 *)
LogMatching ==
    \A s1, s2 \in Servers, i \in 1..Min(Len(log[s1]), Len(log[s2])):
        /\ log[s1][i].term = log[s2][i].term
        => log[s1][i].command = log[s2][i].command

(* Leader完整性：已提交的日志条目在所有更高任期的Leader日志中 *)
LeaderCompleteness ==
    \A s1, s2 \in Servers:
        /\ state[s1] = "LEADER"
        /\ state[s2] = "LEADER"
        /\ currentTerm[s2] > currentTerm[s1]
        /\ \E i \in 1..Len(log[s1]):
            /\ i <= commitIndex[s1]
            => \E j \in 1..Len(log[s2]): log[s2][j] = log[s1][i]

(* 状态机安全性：相同commitIndex的状态相同 *)
StateMachineSafety ==
    \A s1, s2 \in Servers:
        /\ commitIndex[s1] = commitIndex[s2]
        => SubSeq(log[s1], 1, commitIndex[s1]) = SubSeq(log[s2], 1, commitIndex[s2])

(* ============================================
   活性性质
   ============================================ *)

(* 选举活性：最终会选出Leader *)
ElectionLiveness ==
    <>(\E s \in Servers: state[s] = "LEADER")

(* 日志复制活性：Leader的日志最终会被复制到多数派 *)
LogReplicationLiveness ==
    \A s \in Servers:
        /\ state[s] = "LEADER"
        => <>(\A t \in Servers:
            (t # s) => (log[t] = log[s] \/ Len(log[t]) < Len(log[s])))

(* ============================================
   安全性定理
   ============================================ *)

THEOREM Raft_Safety ==
    Spec => [](ElectionSafety /\ LogMatching /\ LeaderCompleteness /\ StateMachineSafety)

(* ============================================
   活性定理
   ============================================ *)

THEOREM Raft_Liveness ==
    Spec => (ElectionLiveness /\ LogReplicationLiveness)
