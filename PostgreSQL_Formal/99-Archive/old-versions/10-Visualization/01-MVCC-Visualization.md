# MVCC可视化图表

## 1. 版本链示意图

```text
Timeline →

T1: [INSERT x=10] ----→ [COMMIT] --------→
       ↓                      ↓
     xmin=100               x_max
       ↓
       v
Page: | Header | x=10 | (TID: 100)

T2: [UPDATE x=20] ----→ [COMMIT] --------→
       ↓                      ↓
     xmin=200               x_max
       ↓
       v
Page: | Header | x=10 | → | x=20 | (TID: 200)
                    ctid ↗

T3: [SELECT] @ snapshot [100, 200]
       ↓
   Visible: x=10 (T1 committed, T2 in progress)
```

## 2. 快照可见性图

```text
Transaction Timeline:

T1: |---[BEGIN]--------[COMMIT]---|
T2:     |---[BEGIN]--------[COMMIT]---|
T3:         |---[SELECT]---|

T3's Snapshot:
- xmin: T1.xid
- xmax: T2.xid + 1
- xip_list: {T2.xid}

Visibility:
- T1 changes: VISIBLE (committed before snapshot)
- T2 changes: NOT VISIBLE (in progress)
```

---

**完成度**: 100%
