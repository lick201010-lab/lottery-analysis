#!/bin/bash
# auto-deploy.sh — 检查 origin/main 是否有新 commit，有就部署
# Run via cron every 2 minutes
# Logs: /var/log/yicai-deploy.log

# pipefail 让 git/npm 失败不会被 tail 管道吞掉。
set -eo pipefail
cd /opt/lottery-analysis

# data/marksix.db 是运行时 SQLite 数据库，不能在 cron 中 git checkout。
# 否则 uvicorn 持有的 SQLite 连接会写入失败，并可能回退最新开奖数据。

LOG=/var/log/yicai-deploy.log

ensure_uvicorn() {
  if curl -fsS --max-time 5 http://localhost:8000/api/v1/health >/dev/null 2>&1; then
    return 0
  fi

  {
    echo ""
    echo "=== [$(date '+%Y-%m-%d %H:%M:%S')] Backend health check failed; starting uvicorn ==="
  } >> "$LOG"

  pkill -f "uvicorn app.main:app" 2>/dev/null || true
  sleep 1
  cd /opt/lottery-analysis/backend
  setsid nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 >> /opt/uvicorn.log 2>&1 < /dev/null &
  cd /opt/lottery-analysis

  for _ in 1 2 3 4 5 6 7 8 9 10; do
    if curl -fsS --max-time 5 http://localhost:8000/api/v1/health >/dev/null 2>&1; then
      echo "[ok] uvicorn health check passed" >> "$LOG"
      return 0
    fi
    sleep 1
  done

  echo "[error] uvicorn failed health check after restart" >> "$LOG"
  tail -40 /opt/uvicorn.log >> "$LOG" 2>/dev/null || true
  return 1
}

# Fetch 远端
git fetch origin main 2>/dev/null

LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/main)

if [ "$LOCAL" = "$REMOTE" ]; then
  ensure_uvicorn
  exit 0  # nothing to deploy
fi

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
  pkill -f "uvicorn app.main:app" 2>/dev/null || true
  sleep 2
fi

ensure_uvicorn

echo "=== Deploy done ===" >> "$LOG"
