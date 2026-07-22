#!/bin/bash
set -uo pipefail

LOCK_FILE=/var/lock/yicai-jackpot-scrape.lock
LOG_FILE=/var/log/jackpot_scrape.log

exec 9>"$LOCK_FILE"
if ! flock -n 9; then
    printf '[%s] skipped: another scrape is running\n' "$(date -Is)" >> "$LOG_FILE"
    exit 0
fi

printf '[%s] scrape started\n' "$(date -Is)" >> "$LOG_FILE"
if response=$(curl -fsS \
    --max-time 180 \
    --retry 2 \
    --retry-delay 5 \
    --retry-all-errors \
    -X POST \
    http://127.0.0.1:8000/api/v1/jackpot/scrape 2>&1); then
    printf '[%s] scrape succeeded: %s\n' "$(date -Is)" "$response" >> "$LOG_FILE"
else
    status=$?
    printf '[%s] scrape failed (curl=%s): %s\n' "$(date -Is)" "$status" "$response" >> "$LOG_FILE"
    exit "$status"
fi
