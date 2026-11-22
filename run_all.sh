#!/usr/bin/env bash
# Rerun every analysis. Takes about 10 minutes on a laptop. Outputs go to results/ and figures/.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p results figures
python3 src/match_cisi.py
python3 src/icon_test.py main
python3 src/icon_test.py all
python3 src/power_check.py
python3 src/chart.py
python3 src/probes.py
python3 src/numerals.py
echo "all done"
