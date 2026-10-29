#!/usr/bin/env python3
"""Fetch recent Mark Six draws from lottery.hk.

Each attempt has a connect timeout, a read timeout, and a wall-clock deadline.
The deadline also covers DNS, which ``requests`` does not time out. After a
few attempts the script exits with a short error instead of blocking the
update job.
"""
import json
import re
import signal
import sys
import time
from datetime import datetime
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter

URL = "https://lottery.hk/zh-hans/liuhecai/kaijiangjieguo/"
HEADERS = {"User-Agent": "Mozilla/5.0"}
OUTPUT_PATH = Path("marksix_draws.json")

CONNECT_TIMEOUT = 10
READ_TIMEOUT = 20
# Slightly above connect + read so the HTTP timeouts usually fire first.
# The alarm is what stops a stuck DNS lookup.
ATTEMPT_DEADLINE = CONNECT_TIMEOUT + READ_TIMEOUT + 5
ATTEMPTS = 3
RETRY_BACKOFF_SECONDS = 2


class FetchDeadlineExceeded(Exception):
    """Wall-clock cap. Not an OSError, so urllib3 will not swallow it."""


def _arm_deadline(seconds):
    """Return a restore callback, or None when SIGALRM is unavailable."""
    if not hasattr(signal, "SIGALRM"):
        return None

    def _handle(signum, frame):
        raise FetchDeadlineExceeded(
            f"lottery.hk did not respond within {seconds}s "
            "(DNS, connect, or read)"
        )

    previous = signal.signal(signal.SIGALRM, _handle)
    signal.alarm(int(seconds))

    def _restore():
        signal.alarm(0)
        signal.signal(signal.SIGALRM, previous)

    return _restore


def fetch_html(
    url=URL,
    connect_timeout=CONNECT_TIMEOUT,
    read_timeout=READ_TIMEOUT,
    deadline=ATTEMPT_DEADLINE,
):
    """GET ``url`` once. Raises on timeout, deadline, or HTTP error."""
    session = requests.Session()
    adapter = HTTPAdapter(max_retries=0)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    restore_deadline = _arm_deadline(deadline)
    try:
        response = session.get(
            url,
            timeout=(connect_timeout, read_timeout),
            headers=HEADERS,
        )
        response.raise_for_status()
        return response.text
    finally:
        if restore_deadline is not None:
            restore_deadline()
        session.close()


def fetch_html_with_retries(
    url=URL,
    attempts=ATTEMPTS,
    connect_timeout=CONNECT_TIMEOUT,
    read_timeout=READ_TIMEOUT,
    deadline=ATTEMPT_DEADLINE,
    backoff_seconds=RETRY_BACKOFF_SECONDS,
):
    last_error = None
    for attempt in range(1, attempts + 1):
        print(
            f"Fetching {url} (attempt {attempt}/{attempts}, "
            f"connect={connect_timeout}s read={read_timeout}s deadline={deadline}s)",
            flush=True,
        )
        try:
            return fetch_html(
                url,
                connect_timeout=connect_timeout,
                read_timeout=read_timeout,
                deadline=deadline,
            )
        except (requests.RequestException, FetchDeadlineExceeded, TimeoutError) as exc:
            last_error = exc
            print(
                f"lottery.hk attempt {attempt} failed: {type(exc).__name__}: {exc}",
                file=sys.stderr,
                flush=True,
            )
            if attempt < attempts:
                time.sleep(backoff_seconds)

    print(
        "ERROR: lottery.hk unreachable after "
        f"{attempts} attempts "
        f"(connect timeout {connect_timeout}s, read timeout {read_timeout}s, "
        f"deadline {deadline}s). Last error: {last_error}",
        file=sys.stderr,
        flush=True,
    )
    raise SystemExit(1)


def parse_draws(html):
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table")
    if table is None:
        raise ValueError("lottery.hk response did not contain a results table")

    draws = []
    for row in table.find_all("tr"):
        cols = row.find_all(["td", "th"])
        if len(cols) < 3:
            continue

        period = cols[0].get_text(strip=True)
        if not re.match(r"^\d{2}/\d{3}$", period):
            continue

        date_str = cols[1].get_text(strip=True)
        balls_ul = cols[2].find("ul", class_="balls")
        if not balls_ul:
            continue

        lis = balls_ul.find_all("li")
        numbers = [
            li.get_text(strip=True)
            for li in lis
            if "-plus" not in (li.get("class") or [])
        ]
        special = [
            li.get_text(strip=True)
            for li in lis
            if "-plus" in (li.get("class") or [])
        ]
        if len(numbers) != 6 or not special:
            continue

        try:
            dt = datetime.strptime(date_str, "%d/%m/%Y")
            iso_date = dt.strftime("%Y-%m-%d")
        except ValueError:
            iso_date = date_str

        draws.append(
            {
                "draw_number": period,
                "draw_date": iso_date,
                "numbers": [int(n) for n in numbers],
                "special_number": int(special[0]),
                "source": "lottery.hk",
            }
        )
    return draws


def write_draws(draws, path=OUTPUT_PATH):
    path = Path(path)
    payload = json.dumps(draws, ensure_ascii=False, indent=2)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(payload, encoding="utf-8")
    temporary.replace(path)


def main():
    try:
        html = fetch_html_with_retries()
        draws = parse_draws(html)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc

    if not draws:
        print("ERROR: lottery.hk returned no Mark Six draws", file=sys.stderr)
        raise SystemExit(1)

    print(f"Total draws fetched: {len(draws)}")
    print(json.dumps(draws[:5], ensure_ascii=False, indent=2))
    write_draws(draws)
    print(f"Saved {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
