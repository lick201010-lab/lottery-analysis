#!/usr/bin/env python3
"""Fetch recent Mark Six draws.

Primary source: HKJC official GraphQL (info.cld.hkjc.com), which is reachable
from more egresses than lottery.hk (GitHub-hosted runners and several cloud
networks time out on lottery.hk).

Fallback: lottery.hk HTML table.

Each attempt has a connect timeout, a read timeout, and a wall-clock deadline.
After a few attempts the script exits with a short error instead of blocking.
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

HKJC_URL = "https://info.cld.hkjc.com/graphql/base/"
LOTTERY_HK_URL = "https://lottery.hk/zh-hans/liuhecai/kaijiangjieguo/"
HEADERS = {"User-Agent": "Mozilla/5.0"}
HKJC_HEADERS = {
    **HEADERS,
    "Content-Type": "application/json",
    "Accept": "application/json",
    "Origin": "https://bet.hkjc.com",
    "Referer": "https://bet.hkjc.com/ch/marksix/results",
}
# Exact whitelisted query shape from the HKJC frontend / backend scraper.
MARKSIX_GRAPHQL_QUERY = """
fragment lotteryDrawsFragment on LotteryDraw {
    id
    year
    no
    openDate
    closeDate
    drawDate
    status
    snowballCode
    snowballName_en
    snowballName_ch
    lotteryPool {
      sell
      status
      totalInvestment
      jackpot
      unitBet
      estimatedPrize
      derivedFirstPrizeDiv
      lotteryPrizes {
        type
        winningUnit
        dividend
      }
    }
    drawResult {
      drawnNo
      xDrawnNo
    }
  }

        query marksixResult($lastNDraw: Int, $startDate: String, $endDate: String, $drawType: LotteryDrawType) {
            lotteryDraws(lastNDraw: $lastNDraw, startDate: $startDate, endDate: $endDate, drawType: $drawType) {
              ...lotteryDrawsFragment
            }
        }
"""
OUTPUT_PATH = Path("marksix_draws.json")

CONNECT_TIMEOUT = 10
READ_TIMEOUT = 20
ATTEMPT_DEADLINE = CONNECT_TIMEOUT + READ_TIMEOUT + 5
ATTEMPTS = 3
RETRY_BACKOFF_SECONDS = 2
HKJC_LAST_N = 30


class FetchDeadlineExceeded(Exception):
    """Wall-clock cap. Not an OSError, so urllib3 will not swallow it."""


def _arm_deadline(seconds):
    """Return a restore callback, or None when SIGALRM is unavailable."""
    if not hasattr(signal, "SIGALRM"):
        return None

    def _handle(signum, frame):
        raise FetchDeadlineExceeded(
            f"source did not respond within {seconds}s "
            "(DNS, connect, or read)"
        )

    previous = signal.signal(signal.SIGALRM, _handle)
    signal.alarm(int(seconds))

    def _restore():
        signal.alarm(0)
        signal.signal(signal.SIGALRM, previous)

    return _restore


def _session():
    session = requests.Session()
    adapter = HTTPAdapter(max_retries=0)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


def fetch_hkjc_draws(
    last_n=HKJC_LAST_N,
    connect_timeout=CONNECT_TIMEOUT,
    read_timeout=READ_TIMEOUT,
    deadline=ATTEMPT_DEADLINE,
):
    """POST HKJC GraphQL once. Raises on timeout/deadline/HTTP/parse error."""
    session = _session()
    restore_deadline = _arm_deadline(deadline)
    try:
        response = session.post(
            HKJC_URL,
            timeout=(connect_timeout, read_timeout),
            headers=HKJC_HEADERS,
            json={
                "operationName": "marksixResult",
                "query": MARKSIX_GRAPHQL_QUERY,
                "variables": {"lastNDraw": last_n},
            },
        )
        response.raise_for_status()
        payload = response.json()
    finally:
        if restore_deadline is not None:
            restore_deadline()
        session.close()

    if payload.get("errors"):
        raise ValueError(f"HKJC GraphQL errors: {payload['errors']!r}")

    raw_draws = ((payload.get("data") or {}).get("lotteryDraws") or [])
    draws = []
    for draw in raw_draws:
        if draw.get("status") != "Result":
            continue
        result = draw.get("drawResult") or {}
        regular = result.get("drawnNo") or []
        special = result.get("xDrawnNo")
        year = str(draw.get("year") or "")
        no = draw.get("no")
        date_str = str(draw.get("drawDate") or "")[:10]
        if not year or no is None or len(regular) != 6 or special is None:
            continue
        try:
            numbers = [int(n) for n in regular]
            special_number = int(special)
        except (TypeError, ValueError):
            continue
        draws.append(
            {
                "draw_number": f"{year[-2:]}/{int(no):03d}",
                "draw_date": date_str,
                "numbers": numbers,
                "special_number": special_number,
                "source": "hkjc-graphql",
            }
        )
    if not draws:
        raise ValueError("HKJC GraphQL returned no Mark Six Result draws")
    return draws


def fetch_html(
    url=LOTTERY_HK_URL,
    connect_timeout=CONNECT_TIMEOUT,
    read_timeout=READ_TIMEOUT,
    deadline=ATTEMPT_DEADLINE,
):
    """GET ``url`` once. Raises on timeout, deadline, or HTTP error."""
    session = _session()
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


def parse_lottery_hk_draws(html):
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


def with_retries(label, fn, attempts=ATTEMPTS, backoff_seconds=RETRY_BACKOFF_SECONDS):
    last_error = None
    for attempt in range(1, attempts + 1):
        print(
            f"{label} (attempt {attempt}/{attempts}, "
            f"connect={CONNECT_TIMEOUT}s read={READ_TIMEOUT}s "
            f"deadline={ATTEMPT_DEADLINE}s)",
            flush=True,
        )
        try:
            return fn()
        except (requests.RequestException, FetchDeadlineExceeded, TimeoutError, ValueError) as exc:
            last_error = exc
            print(
                f"{label} attempt {attempt} failed: {type(exc).__name__}: {exc}",
                file=sys.stderr,
                flush=True,
            )
            if attempt < attempts:
                time.sleep(backoff_seconds)
    raise RuntimeError(f"{label} failed after {attempts} attempts: {last_error}")


def write_draws(draws, path=OUTPUT_PATH):
    path = Path(path)
    payload = json.dumps(draws, ensure_ascii=False, indent=2)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(payload, encoding="utf-8")
    temporary.replace(path)


def main():
    draws = None
    errors = []

    try:
        draws = with_retries("HKJC GraphQL", fetch_hkjc_draws)
        print(f"HKJC GraphQL OK: {len(draws)} draws", flush=True)
    except RuntimeError as exc:
        errors.append(str(exc))
        print(f"WARN: {exc}", file=sys.stderr, flush=True)

    if draws is None:
        try:
            html = with_retries(
                "lottery.hk HTML",
                lambda: fetch_html(LOTTERY_HK_URL),
            )
            draws = parse_lottery_hk_draws(html)
            print(f"lottery.hk OK: {len(draws)} draws", flush=True)
        except (RuntimeError, ValueError) as exc:
            errors.append(str(exc))
            print(
                "ERROR: all Mark Six sources failed.\n" + "\n".join(errors),
                file=sys.stderr,
                flush=True,
            )
            raise SystemExit(1) from exc

    if not draws:
        print("ERROR: no Mark Six draws after fetch", file=sys.stderr)
        raise SystemExit(1)

    print(f"Total draws fetched: {len(draws)}")
    print(json.dumps(draws[:5], ensure_ascii=False, indent=2))
    write_draws(draws)
    print(f"Saved {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
