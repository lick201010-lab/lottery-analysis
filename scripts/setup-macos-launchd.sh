#!/bin/bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LABEL="com.lsj.lottery.marksix-update"
PLIST="$HOME/Library/LaunchAgents/${LABEL}.plist"
LOG_DIR="$ROOT/scripts/logs"
mkdir -p "$LOG_DIR" "$HOME/Library/LaunchAgents"
cat > "$PLIST" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>${LABEL}</string>
  <key>WorkingDirectory</key><string>${ROOT}</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/bash</string>
    <string>${ROOT}/scripts/run-macos-update.sh</string>
  </array>
  <key>StartCalendarInterval</key>
  <array>
    <dict><key>Weekday</key><integer>2</integer><key>Hour</key><integer>22</integer><key>Minute</key><integer>30</integer></dict>
    <dict><key>Weekday</key><integer>4</integer><key>Hour</key><integer>22</integer><key>Minute</key><integer>30</integer></dict>
    <dict><key>Weekday</key><integer>6</integer><key>Hour</key><integer>22</integer><key>Minute</key><integer>30</integer></dict>
  </array>
  <key>StandardOutPath</key><string>${LOG_DIR}/launchd.out.log</string>
  <key>StandardErrorPath</key><string>${LOG_DIR}/launchd.err.log</string>
  <key>EnvironmentVariables</key>
  <dict>
    <key>PATH</key>
    <string>/usr/local/bin:/usr/bin:/bin:${HOME}/Library/Python/3.9/bin</string>
    <key>PYTHONUNBUFFERED</key>
    <string>1</string>
    <key>https_proxy</key>
    <string>http://127.0.0.1:7897</string>
    <key>http_proxy</key>
    <string>http://127.0.0.1:7897</string>
    <key>HTTPS_PROXY</key>
    <string>http://127.0.0.1:7897</string>
    <key>HTTP_PROXY</key>
    <string>http://127.0.0.1:7897</string>
  </dict>
</dict>
</plist>
PLIST
chmod +x "$ROOT/scripts/run-macos-update.sh"
launchctl bootout "gui/$(id -u)/${LABEL}" 2>/dev/null || true
launchctl unload "$PLIST" 2>/dev/null || true
if launchctl bootstrap "gui/$(id -u)" "$PLIST"; then
  echo "bootstrap ok"
else
  launchctl load "$PLIST"
  echo "load ok"
fi
echo "Installed ${LABEL}"
echo "Root=${ROOT}"
echo "Schedule=Tue/Thu/Sat 22:30 local"
