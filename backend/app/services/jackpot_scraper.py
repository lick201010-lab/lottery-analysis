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
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}

TIMEOUT = httpx.Timeout(30.0, connect=15.0)


async def fetch_ssq_jackpot():
    """Fetch SSQ jackpot data from multiple sources."""
    # Try official CWL API first
    result = await _try_cwl_api()
    if result:
        return result

    # Fallback: scrape from 500.com or caibaobei
    result = await _try_500_xml()
    if result:
        return result

    return None


async def _try_cwl_api():
    """Try China Welfare Lottery official API."""
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT, follow_redirects=True) as client:
            url = "https://www.cwl.gov.cn/cwl_admin/kjxx/findDrawNotice"
            params = {"name": "ssq", "issueCount": 1}
            resp = await client.get(url, params=params, headers=HEADERS)
            if resp.status_code == 200:
                data = resp.json()
                return _parse_cwl_ssq(data)
    except Exception as e:
        print(f"CWL API failed: {e}")
    return None


def _parse_cwl_ssq(data):
    """Parse CWL API response for SSQ."""
    try:
        if not data.get("success") or not data.get("result"):
            return None
        item = data["result"][0]

        prize_breakdown = []
        for pg in item.get("prizegrades", []):
            prize_breakdown.append({
                "level": int(pg.get("type", 0)),
                "count": int(pg.get("typenum", "0").replace(",", "")),
                "amount_per_note": int(pg.get("typemoney", "0").replace(",", "")),
            })

        return {
            "lottery_type": "ssq",
            "draw_number": str(item.get("code", "")),
            "draw_date": item.get("date", ""),
            "pool_amount": float(item.get("poolamount", 0) or 0),
            "sales_amount": float(item.get("sales", 0) or 0),
            "prize_breakdown": prize_breakdown,
            "red_balls": item.get("red", ""),
            "blue_ball": item.get("blue", ""),
        }
    except Exception as e:
        print(f"Parse CWL failed: {e}")
        return None


async def _try_500_xml():
    """Try 500.com XML API."""
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT, follow_redirects=True) as client:
            url = "https://kaijiang.500.com/static/info/kaijiang/xml/ssq/list.xml"
            resp = await client.get(url, headers=HEADERS)
            if resp.status_code == 200:
                xml = resp.text
                return _parse_500_xml(xml)
    except Exception as e:
        print(f"500 XML failed: {e}")
    return None


def _parse_500_xml(xml):
    """Parse 500.com XML for SSQ."""
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
            "pool_amount": None,  # not available in this XML
            "sales_amount": None,
            "prize_breakdown": [],
            "red_balls": red,
            "blue_ball": blue,
        }
    except Exception as e:
        print(f"Parse 500 XML failed: {e}")
        return None


async def fetch_marksix_jackpot():
    """Fetch MarkSix data from HKJC or fallback sources."""
    # HKJC does not expose a public JSON API for jackpot amounts.
    # We can try to scrape their results page.
    result = await _try_hkjc_html()
    if result:
        return result

    return None


async def _try_hkjc_html():
    """Try scraping HKJC results page."""
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT, follow_redirects=True) as client:
            url = "https://bet.hkjc.com/marksix/default.aspx"
            resp = await client.get(url, headers=HEADERS)
            if resp.status_code == 200:
                html = resp.text
                return _parse_hkjc_html(html)
    except Exception as e:
        print(f"HKJC failed: {e}")
    return None


def _parse_hkjc_html(html):
    """Parse HKJC HTML for latest MarkSix draw."""
    try:
        # Extract draw number
        num_match = re.search(r'第\s*(\d+)\s*期', html)
        draw_number = num_match.group(1) if num_match else ""

        # Extract draw date
        date_match = re.search(r'(\d{4})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日', html)
        draw_date = f"{date_match.group(1)}-{date_match.group(2).zfill(2)}-{date_match.group(3).zfill(2)}" if date_match else ""

        # Extract numbers - look for td elements with numbers
        numbers = re.findall(r'>(\d{1,2})<', html)
        numbers = [int(n) for n in numbers if 1 <= int(n) <= 49]

        if len(numbers) >= 7:
            regular = numbers[:6]
            special = numbers[6]
        else:
            regular = numbers[:6] if len(numbers) >= 6 else numbers
            special = numbers[6] if len(numbers) >= 7 else 0

        # MarkSix has fixed prize structure, no rolling pool
        prize_breakdown = [
            {"level": 1, "count": 0, "amount_per_note": 0},  # 头奖 - variable
            {"level": 2, "count": 0, "amount_per_note": 0},  # 二等奖 - variable
            {"level": 3, "count": 0, "amount_per_note": 0},  # 三等奖 - variable
        ]

        return {
            "lottery_type": "marksix",
            "draw_number": draw_number,
            "draw_date": draw_date,
            "pool_amount": None,  # MarkSix has no rolling pool
            "sales_amount": None,
            "prize_breakdown": prize_breakdown,
            "red_balls": ",".join(str(n) for n in regular),
            "blue_ball": str(special),
        }
    except Exception as e:
        print(f"Parse HKJC failed: {e}")
        return None


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
