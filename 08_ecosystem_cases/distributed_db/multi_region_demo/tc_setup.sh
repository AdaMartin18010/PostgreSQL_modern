#!/usr/bin/env bash
# 使用 tc 注入跨 Region 延迟/抖动/丢包
# 需要 root 权限；示例对 docker 默认网桥或特定网卡生效

set -euo pipefail

IFACE=${IFACE:-eth0}
LATENCY_MS=${LATENCY_MS:-80}
JITTER_MS=${JITTER_MS:-20}
LOSS_PCT=${LOSS_PCT:-0.1}

echo "Applying tc on $IFACE: ${LATENCY_MS}ms +/-${JITTER_MS}ms, loss ${LOSS_PCT}%"
tc qdisc add dev "$IFACE" root netem delay ${LATENCY_MS}ms ${JITTER_MS}ms loss ${LOSS_PCT}% || {
  echo "qdisc exists, attempting change...";
  tc qdisc change dev "$IFACE" root netem delay ${LATENCY_MS}ms ${JITTER_MS}ms loss ${LOSS_PCT}%
}

echo "Done. Use ./tc_teardown.sh to remove."

