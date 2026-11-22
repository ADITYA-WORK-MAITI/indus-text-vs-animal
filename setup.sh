#!/usr/bin/env bash
# Fetch the two public corpora this project reads. Needs git and about 130 MB of disk.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p data
[ -d data/koskenni_indus ] || git clone --depth 1 https://github.com/koskenni/indus data/koskenni_indus
[ -d data/mayig ] || git clone --depth 1 https://github.com/mayig/indus-valley-script-corpus data/mayig
pip install -r requirements.txt
echo "setup done"
