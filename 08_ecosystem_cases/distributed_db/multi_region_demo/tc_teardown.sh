#!/usr/bin/env bash
set -euo pipefail
IFACE=${IFACE:-eth0}
echo "Removing tc qdisc on $IFACE"
tc qdisc del dev "$IFACE" root netem || true
echo "Done."

