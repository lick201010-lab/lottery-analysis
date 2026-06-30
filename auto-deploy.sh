#!/bin/bash
# auto-deploy.sh — 检查 origin/main 是否有新 commit，有就部署
# Run via cron every 2 minutes
# Logs: /var/log/yicai-deploy.log

set -e
cd /opt/lottery-analysis

# data/marksix.db 是运行时 SQLite 数据库，不能在 cron 中 git checkout。
# 否则 uvicorn 持有的 SQLite 连接会写入失败，并可能回退最新开奖数据。

# Fetch 远端
git fetch origin main 2>/dev/null

LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/main)

if [ "$LOCAL" = "$REMOTE" ]; then
  exit 0  # nothing to do
fi

LOG=/var/log/yicai-deploy.log
{
  echo ""
  echo "=== [$(date '+%Y-%m-%d %H:%M:%S')] Deploying $LOCAL → $REMOTE ==="
} >> "$LOG"

# 看哪些文件变了
CHANGED=$(git diff --name-only "$LOCAL" "$REMOTE")
{
  echo "Changed files:"
  echo "$CHANGED" | sed 's/^/  /'
} >> "$LOG"

# Pull
git pull --ff-only origin main 2>&1 | tail -3 >> "$LOG"

# 前端变更
if echo "$CHANGED" | grep -q '^frontend/'; then
  cd frontend
  if echo "$CHANGED" | grep -qE '^frontend/(package\.json|package-lock\.json)$'; then
    echo "[npm install]" >> "$LOG"
    npm install 2>&1 | tail -3 >> "$LOG"
  fi
  echo "[npm run build]" >> "$LOG"
  npm run build 2>&1 | tail -3 >> "$LOG"
  cd ..
fi

# 后端变更（需重启 uvicorn）
if echo "$CHANGED" | grep -q '^backend/'; then
  echo "[restart uvicorn]" >> "$LOG"
  pkill -f uvicorn 2>/dev/null || true
  sleep 2
  cd backend
  setsid nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2 > uvicorn.log 2>&1 < /dev/null &
  cd ..
fi

echo "=== Deploy done ===" >> "$LOG"
