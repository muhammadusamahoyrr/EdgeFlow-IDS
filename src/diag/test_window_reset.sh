#!/usr/bin/env bash
# Sanity check for per-window reset: DDoS then BruteForce with block-on-first-verdict.
# The BruteForce window's OVS dump must not contain the DDoS drop rules. Run as root in WSL.
set -eo pipefail
cd "$(dirname "$0")/.."
bash stop_live.sh > /dev/null 2>&1 || true
rm -rf ../results/live/test_reset
python3 ../topology/live_experiment.py --tag test_reset --enforce --policy none \
  --only DDoS-SYN_Flood DictionaryBruteForce 2>&1 | grep -v bogus || true
D=../results/live/test_reset
echo "--- drop rules in DDoS dump:       $(grep -c 'priority=100' $D/ovs_flows_DDoS-SYN_Flood.txt || true)"
echo "--- drop rules in BruteForce dump: $(grep -c 'priority=100' $D/ovs_flows_DictionaryBruteForce.txt || true)"
echo "--- DDoS attacker IPs in BruteForce dump (must be 0): $(grep -cE 'nw_src=192.168.137.(201|99|36|34|153|87),' $D/ovs_flows_DictionaryBruteForce.txt || true)"
grep -E "gateway: (ready|wrote)" $D/gateway.log
/opt/edgeflow/bin/python eval_enforce.py --tag test_reset 2>&1 | grep -E "Blocked host|Packets dropped|^\| [A-Z]" || true
