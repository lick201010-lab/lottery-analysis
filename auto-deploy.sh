#!/bin/bash
# auto-deploy.sh — 检查 origin/main 是否有新 commit，有就部署
# Run via cron every 2 minutes
# Logs: /var/log/yicai-deploy.log

# pipefail 让 git/npm 失败不会被 tail 管道吞掉。
set -eo pipefail

LOCK_FILE=/tmp/yicai-auto-deploy.lock
exec 9>"$LOCK_FILE"
if ! flock -n 9; then
  exit 0
fi

cd /opt/lottery-analysis

# data/marksix.db 是运行时 SQLite 数据库，不能在 cron 中 git checkout。
# 否则 uvicorn 持有的 SQLite 连接会写入失败，并可能回退最新开奖数据。

LOG=/var/log/yicai-deploy.log

build_frontend() {
  local frontend_dir=/opt/lottery-analysis/frontend
  local next_dir="$frontend_dir/dist.next"
  local current_dir="$frontend_dir/dist"
  local previous_dir="$frontend_dir/dist.previous"

  rm -rf "$next_dir"
  cd "$frontend_dir"
  echo "[npm run build -> dist.next]" >> "$LOG"
  VITE_OUT_DIR=dist.next npm run build 2>&1 | tail -12 >> "$LOG"

  test -s "$next_dir/index.html"
  test -s "$next_dir/marksix/results.html"
  test -s "$next_dir/ssq/results.html"
  test -s "$next_dir/sitemap.xml"

  rm -rf "$previous_dir"
  if [ -d "$current_dir" ]; then
    mv "$current_dir" "$previous_dir"
  fi
  mv "$next_dir" "$current_dir"
  rm -rf "$previous_dir"
  cd /opt/lottery-analysis
  echo "[ok] frontend build published atomically" >> "$LOG"
}

ensure_uvicorn() {
  if curl -fsS --max-time 5 http://localhost:8000/api/v1/health >/dev/null 2>&1; then
    return 0
  fi

  {
    echo ""
    echo "=== [$(date '+%Y-%m-%d %H:%M:%S')] Backend health check failed; starting uvicorn ==="
  } >> "$LOG"

  pkill -f "[u]vicorn app.main:app" 2>/dev/null || true
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

draw_fingerprint() {
  {
    curl -fsS --max-time 8 "http://localhost:8000/api/v1/draws/latest?lottery_type=marksix"
    curl -fsS --max-time 8 "http://localhost:8000/api/v1/draws/latest?lottery_type=ssq"
    curl -fsS --max-time 8 "http://localhost:8000/api/v1/draws/latest?lottery_type=qxc"
  } | sha256sum | awk '{print $1}'
}

refresh_seo_when_draws_change() {
  local fingerprint
  local stamp_file=/opt/lottery-analysis/frontend/.generated/draw-version

  fingerprint=$(draw_fingerprint) || {
    echo "[warn] unable to calculate draw fingerprint; keeping current static SEO pages" >> "$LOG"
    return 0
  }

  if [ -f "$stamp_file" ] && [ "$(cat "$stamp_file")" = "$fingerprint" ]; then
    return 0
  fi

  {
    echo ""
    echo "=== [$(date '+%Y-%m-%d %H:%M:%S')] Draw data changed; rebuilding static SEO pages ==="
  } >> "$LOG"

  build_frontend
  cd /opt/lottery-analysis/frontend
  mkdir -p .generated
  printf '%s' "$fingerprint" > "$stamp_file"
  cd /opt/lottery-analysis
  echo "[ok] static SEO pages and sitemaps refreshed" >> "$LOG"
}

# Fetch 远端
git fetch origin main 2>/dev/null

LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/main)

if [ "$LOCAL" = "$REMOTE" ]; then
  ensure_uvicorn
  refresh_seo_when_draws_change
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
  cd ..
  build_frontend
  cd frontend
  fingerprint=$(draw_fingerprint || true)
  if [ -n "$fingerprint" ]; then
    mkdir -p .generated
    printf '%s' "$fingerprint" > .generated/draw-version
  fi
  cd ..
fi

# 后端变更（需重启 uvicorn）
if echo "$CHANGED" | grep -q '^backend/'; then
  echo "[restart uvicorn]" >> "$LOG"
  pkill -f "[u]vicorn app.main:app" 2>/dev/null || true
  sleep 2
fi

ensure_uvicorn
refresh_seo_when_draws_change

echo "=== Deploy done ===" >> "$LOG"
