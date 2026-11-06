#!/bin/bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
LOG_DIR="$ROOT/scripts/logs"
mkdir -p "$LOG_DIR"
LOG="$LOG_DIR/update_$(date +%Y%m%d).log"
exec >>"$LOG" 2>&1
echo "==== $(date '+%Y-%m-%d %H:%M:%S %Z') macos marksix update ===="
# Local Clash/V2Ray HTTP proxy (required for github.com from this Mac)
export https_proxy="${https_proxy:-http://127.0.0.1:7897}"
export http_proxy="${http_proxy:-http://127.0.0.1:7897}"
export HTTPS_PROXY="$https_proxy"
export HTTP_PROXY="$http_proxy"
PYTHON="${MARKSIX_PYTHON:-$(command -v python3)}"
git fetch origin
git checkout main
git pull --ff-only origin main || echo "WARN: pull failed; continuing with local tree"
"$PYTHON" -m pip install --user -q -r requirements.txt || true
# HKJC does not need the proxy; leave proxy on so git push still works.
"$PYTHON" scripts/update.py
echo "==== done ===="
