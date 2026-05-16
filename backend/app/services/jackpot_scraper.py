import asyncio
import json
import re
from datetime import datetime

import httpx

from app.config import LOTTERY_CONFIG


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Referer": "https://datachart.500.com/",
}

TIMEOUT = httpx.Timeout(30.0, connect=15.0)


def _clean_number(s):
    """Remove commas and convert to int/float."""
    if not s:
        return 0
    s = str(s).replace(",", "").strip()
    try:
        return int(s)
    except ValueError:
        try:
            return float(s)
        except ValueError:
            return 0


# ───────────────────────────────────────────────
# SSQ (双色球)
# ───────────────────────────────────────────────

async def fetch_ssq_jackpot():
    """Fetch SSQ data from datachart.500.com HTML table."""
    result = await _try_datachart_500()
    if result:
        return result

    # Fallback: 500.com XML (numbers only, no jackpot amount)
    result = await _try_500_xml()
    if result:
        return result

    return None


async def _try_datachart_500():
    """Parse datachart.500.com SSQ history table."""
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT, follow_redirects=True) as client:
            url = "https://datachart.500.com/ssq/history/newinc/history.php"
            resp = await client.get(url, headers=HEADERS)
            if resp.status_code != 200:
                return None
            return _parse_datachart_html(resp.text)
    except Exception as e:
        print(f"datachart.500.com failed: {e}")
    return None


def _parse_datachart_html(html):
    """Extract first data row from 500.com HTML table."""
    try:
        # Strategy 1: Find the first <tr> with class t_tr1 (data rows)
        # The table has header rows then data rows like:
        # <tr class="t_tr1"><td>26054</td><td>13</td>...<td>2026-05-14</td></tr>
        row_match = re.search(
            r'<tr[^>]*class="t_tr1"[^>]*>(.*?)</tr>',
            html,
            re.S | re.I,
        )
        if row_match:
            row_html = row_match.group(1)
            tds = re.findall(r'<td[^>]*>(.*?)</td>', row_html, re.S | re.I)
            tds = [re.sub(r'<[^>]+>', '', td).strip() for td in tds]
            return _build_ssq_from_tds(tds)

        # Strategy 2: Try matching the markdown-style text extraction
        md_match = re.search(
            r'\|\s*(\d{5})\|\s*(\d+)\|\s*(\d+)\|\s*(\d+)\|\s*(\d+)\|\s*(\d+)\|\s*(\d+)\|\s*(\d+)\|\s*\|\s*([\d,]+)\|\s*(\d+)\|\s*([\d,]+)\|\s*(\d+)\|\s*([\d,]+)\|\s*([\d,]+)\|\s*(\d{4}-\d{2}-\d{2})\|',
            html,
        )
        if md_match:
            g = md_match.groups()
            tds = [
                g[0], g[1], g[2], g[3], g[4], g[5], g[6],  # 期号 + 6红球
                g[7],                                      # 蓝球
                "",                                        # 快乐星期天（空）
                g[8],                                      # 奖池奖金
                g[9],                                      # 一等奖注数
                g[10],                                     # 一等奖奖金
                g[11],                                     # 二等奖注数
                g[12],                                     # 二等奖奖金
                g[13],                                     # 总投注额
                g[14],                                     # 开奖日期
            ]
            return _build_ssq_from_tds(tds)
    except Exception as e:
        print(f"Parse datachart failed: {e}")
    return None


def _build_ssq_from_tds(tds):
    """Build SSQ dict from table cell values."""
    if len(tds) < 10:
        return None

    draw_number = tds[0]
    red_balls = ",".join(tds[1:7])
    blue_ball = tds[7]

    # Columns after blue ball:
    # idx 8 = 快乐星期天 (usually empty)
    # idx 9 = 奖池奖金
    # idx 10 = 一等奖注数
    # idx 11 = 一等奖奖金
    # idx 12 = 二等奖注数
    # idx 13 = 二等奖奖金
    # idx 14 = 总投注额
    # idx 15 = 开奖日期

    pool_amount = _clean_number(tds[9]) if len(tds) > 9 else 0
    first_count = _clean_number(tds[10]) if len(tds) > 10 else 0
    first_amount = _clean_number(tds[11]) if len(tds) > 11 else 0
    second_count = _clean_number(tds[12]) if len(tds) > 12 else 0
    second_amount = _clean_number(tds[13]) if len(tds) > 13 else 0
    sales_amount = _clean_number(tds[14]) if len(tds) > 14 else 0
    draw_date = tds[15] if len(tds) > 15 else ""

    prize_breakdown = [
        {"level": 1, "count": first_count, "amount_per_note": first_amount},
        {"level": 2, "count": second_count, "amount_per_note": second_amount},
    ]

    return {
        "lottery_type": "ssq",
        "draw_number": draw_number,
        "draw_date": draw_date,
        "pool_amount": pool_amount,
        "sales_amount": sales_amount,
        "prize_breakdown": prize_breakdown,
        "red_balls": red_balls,
        "blue_ball": blue_ball,
    }


async def _try_500_xml():
    """Try 500.com XML API (numbers only, no jackpot)."""
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT, follow_redirects=True) as client:
            url = "https://kaijiang.500.com/static/info/kaijiang/xml/ssq/list.xml"
            resp = await client.get(url, headers=HEADERS)
            if resp.status_code == 200:
                return _parse_500_xml(resp.text)
    except Exception as e:
        print(f"500 XML failed: {e}")
    return None


def _parse_500_xml(xml):
    try:
        row_match = re.search(
            r'<row expect="(\d+)" opencode="([^"]+)" opentime="([^"]+)"',
            xml,
        )
        if not row_match:
            return None

        draw_number, opencode, opentime = row_match.groups()
        red, blue = opencode.split("|") if "|" in opencode else (opencode, "")

        return {
            "lottery_type": "ssq",
            "draw_number": draw_number,
            "draw_date": opentime[:10] if opentime else "",
            "pool_amount": None,
            "sales_amount": None,
            "prize_breakdown": [],
            "red_balls": red,
            "blue_ball": blue,
        }
    except Exception as e:
        print(f"Parse 500 XML failed: {e}")
        return None


# ───────────────────────────────────────────────
# MarkSix (六合彩)
# ───────────────────────────────────────────────

async def fetch_marksix_jackpot():
    """Fetch MarkSix data from 500.com datachart."""
    result = await _try_marksix_500()
    if result:
        return result

    # Fallback to other sources
    result = await _try_marksix_fallback()
    if result:
        return result

    return None


async def _try_marksix_500():
    """Try 500.com MarkSix history page."""
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT, follow_redirects=True) as client:
            url = "https://datachart.500.com/hk6/history/inc/history.php"
            resp = await client.get(url, headers=HEADERS)
            if resp.status_code != 200:
                return None
            return _parse_marksix_datachart(resp.text)
    except Exception as e:
        print(f"MarkSix 500 datachart failed: {e}")
    return None


def _parse_marksix_datachart(html):
    """Parse MarkSix HTML from 500.com."""
    try:
        # Look for the first data row in the table
        # Format is typically: draw_number, date, numbers...
        row_match = re.search(
            r'<tr[^>]*class="t_tr1"[^>]*>(.*?)</tr>',
            html,
            re.S | re.I,
        )
        if row_match:
            row_html = row_match.group(1)
            tds = re.findall(r'<td[^>]*>(.*?)</td>', row_html, re.S | re.I)
            tds = [re.sub(r'<[^>]+>', '', td).strip() for td in tds]

            if len(tds) >= 9:
                draw_number = tds[0]
                draw_date = tds[1]
                # Numbers are typically in subsequent tds: regular balls + special
                numbers = []
                for td in tds[2:]:
                    m = re.search(r'(\d{1,2})', td)
                    if m:
                        n = int(m.group(1))
                        if 1 <= n <= 49 and n not in numbers:
                            numbers.append(n)
                            if len(numbers) >= 7:
                                break

                if len(numbers) >= 7:
                    regular = numbers[:6]
                    special = numbers[6]
                else:
                    regular = numbers[:6] if len(numbers) >= 6 else numbers
                    special = numbers[6] if len(numbers) >= 7 else 0

                return {
                    "lottery_type": "marksix",
                    "draw_number": draw_number,
                    "draw_date": draw_date,
                    "pool_amount": None,
                    "sales_amount": None,
                    "prize_breakdown": [
                        {"level": 1, "count": 0, "amount_per_note": 0},
                        {"level": 2, "count": 0, "amount_per_note": 0},
                        {"level": 3, "count": 0, "amount_per_note": 0},
                    ],
                    "red_balls": ",".join(str(n) for n in regular),
                    "blue_ball": str(special),
                }
    except Exception as e:
        print(f"Parse MarkSix datachart failed: {e}")
    return None


async def _try_marksix_fallback():
    """Try alternative MarkSix sources."""
    # Try kj.13322.com
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT, follow_redirects=True) as client:
            url = "https://kj.13322.com/hk6/"
            resp = await client.get(url, headers=HEADERS)
            if resp.status_code == 200:
                return _parse_marksix_html_generic(resp.text)
    except Exception as e:
        print(f"MarkSix 13322 failed: {e}")
    return None


def _parse_marksix_html_generic(html):
    """Generic HTML parser for MarkSix."""
    try:
        # Try to find draw number and numbers
        num_match = re.search(r'第\s*(\d+)\s*期', html)
        draw_number = num_match.group(1) if num_match else ""

        date_match = re.search(r'(\d{4})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日', html)
        if date_match:
            draw_date = f"{date_match.group(1)}-{date_match.group(2).zfill(2)}-{date_match.group(3).zfill(2)}"
        else:
            # Try ISO format
            date_match2 = re.search(r'(\d{4}-\d{2}-\d{2})', html)
            draw_date = date_match2.group(1) if date_match2 else ""

        # Extract ball numbers - look for specific patterns
        numbers = []
        # Pattern 1: balls in spans with class containing ball number
        spans = re.findall(r'<span[^>]*>(\d{1,2})</span>', html)
        for n_str in spans:
            n = int(n_str)
            if 1 <= n <= 49 and n not in numbers:
                numbers.append(n)

        # Pattern 2: text format "01 02 03..."
        if len(numbers) < 7:
            text_nums = re.findall(r'\b(\d{1,2})\b', html)
            for n_str in text_nums:
                n = int(n_str)
                if 1 <= n <= 49 and n not in numbers:
                    numbers.append(n)
                if len(numbers) >= 20:  # Limit to avoid too many matches
                    break

        if len(numbers) >= 7:
            regular = sorted(numbers[:6])
            special = numbers[6]
        else:
            regular = sorted(numbers[:6]) if len(numbers) >= 6 else numbers
            special = numbers[6] if len(numbers) >= 7 else 0

        return {
            "lottery_type": "marksix",
            "draw_number": draw_number,
            "draw_date": draw_date,
            "pool_amount": None,
            "sales_amount": None,
            "prize_breakdown": [
                {"level": 1, "count": 0, "amount_per_note": 0},
                {"level": 2, "count": 0, "amount_per_note": 0},
                {"level": 3, "count": 0, "amount_per_note": 0},
            ],
            "red_balls": ",".join(str(n) for n in regular),
            "blue_ball": str(special),
        }
    except Exception as e:
        print(f"Parse MarkSix generic failed: {e}")
        return None


# ───────────────────────────────────────────────
# Entry point
# ───────────────────────────────────────────────

async def scrape_all():
    """Scrape jackpot data for all lottery types."""
    results = {}
    tasks = [
        ("ssq", fetch_ssq_jackpot()),
        ("marksix", fetch_marksix_jackpot()),
    ]
    for lottery_type, task in tasks:
        try:
            result = await asyncio.wait_for(task, timeout=60.0)
            if result:
                results[lottery_type] = result
        except Exception as e:
            print(f"Scrape {lottery_type} failed: {e}")
    return results
