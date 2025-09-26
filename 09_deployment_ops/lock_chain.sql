-- 锁链路诊断（阻塞链）
SELECT bl.pid AS blocked_pid, ka.query AS blocked_query,
       kl.pid AS blocking_pid, kb.query AS blocking_query
FROM pg_catalog.pg_locks bl
JOIN pg_catalog.pg_stat_activity ka ON ka.pid = bl.pid
JOIN pg_catalog.pg_locks kl ON bl.locktype = kl.locktype
  AND bl.DATABASE IS NOT DISTINCT FROM kl.DATABASE
  AND bl.relation IS NOT DISTINCT FROM kl.relation
  AND bl.page IS NOT DISTINCT FROM kl.page
  AND bl.tuple IS NOT DISTINCT FROM kl.tuple
  AND bl.virtualxid IS NOT DISTINCT FROM kl.virtualxid
  AND bl.transactionid IS NOT DISTINCT FROM kl.transactionid
  AND bl.classid IS NOT DISTINCT FROM kl.classid
  AND bl.objid IS NOT DISTINCT FROM kl.objid
  AND bl.objsubid IS NOT DISTINCT FROM kl.objsubid
  AND bl.pid <> kl.pid
JOIN pg_catalog.pg_stat_activity kb ON kb.pid = kl.pid
WHERE NOT bl.granted;
