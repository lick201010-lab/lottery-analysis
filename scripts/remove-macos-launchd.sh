#!/bin/bash
set -euo pipefail
LABEL="com.lsj.lottery.marksix-update"
PLIST="$HOME/Library/LaunchAgents/${LABEL}.plist"
launchctl unload "$PLIST" 2>/dev/null || true
rm -f "$PLIST"
echo "Removed ${LABEL}"
