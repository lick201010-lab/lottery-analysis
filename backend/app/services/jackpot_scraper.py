import asyncio
import re
from urllib.parse import urljoin

import httpx


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


# MarkSix prize levels (fixed amounts, not pool-based):
# 头奖(1): 6个正码
# 二奖(2): 5个正码 + 特别号
# 三奖(3): 5个正码
# 四奖(4): 4个正码 + 特别号
# 五奖(5): 4个正码
# 六奖(6): 3个正码 + 特别号
# 七奖(7): 3个正码
# 注：八奖(2个正码+特别号)通常为固定 HK$20，不再单独列出
MARKSIX_PRIZE_PLACEHOLDER = [
    {"level": 1, "count": 0, "amount_per_note": 0},
    {"level": 2, "count": 0, "amount_per_note": 0},
    {"level": 3, "count": 0, "amount_per_note": 0},
    {"level": 4, "count": 0, "amount_per_note": 0},
    {"level": 5, "count": 0, "amount_per_note": 0},
    {"level": 6, "count": 0, "amount_per_note": 0},
    {"level": 7, "count": 0, "amount_per_note": 0},
]


def _clean_number(s):
    """Remove commas and convert to int/float."""
    if not s:
        return 0
    s = re.sub(r'[^\d.-]', '', str(s).replace(",", "")).strip()
    try:
        return int(s)
    except ValueError:
        try:
            return float(s)
        except ValueError:
            return 0


def _strip_tags(value):
    """Remove HTML tags and compact whitespace."""
    text = re.sub(r'<[^>]+>', '', value or '')
    text = text.replace('&nbsp;', ' ')
    return re.sub(r'\s+', ' ', text).strip()


def _parse_money(value):
    """Extract a money amount such as HK$39,000,000 or $39,000,000."""
    if not value:
        return None
    text = _strip_tags(value)
    match = re.search(r'(?:HK\$|\$)\s*([\d,]+(?:\.\d+)?)', text, re.I)
    if not match:
        return None
    amount = _clean_number(match.group(1))
    return amount or None


def _parse_chinese_pool_amount(value):
    """Parse compact Chinese money amounts like 2.91亿 or 3500万 into yuan."""
    if not value:
        return None
    text = _strip_tags(value)
    match = re.search(r'([\d,]+(?:\.\d+)?)\s*([亿萬万])?', text)
    if not match:
        return None
    amount = _clean_number(match.group(1))
    if not amount:
        return None
    unit = match.group(2)
    if unit == "亿":
        return amount * 100000000
    if unit in ("万", "萬"):
        return amount * 10000
    return amount


def _parse_date(value):
    """Normalize common lottery date formats to YYYY-MM-DD."""
    if not value:
        return ""

    value = _strip_tags(value)

    iso_match = re.search(r'(\d{4})-(\d{2})-(\d{2})', value)
    if iso_match:
        return "-".join(iso_match.groups())

    zh_match = re.search(r'(\d{4})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日', value)
    if zh_match:
        year, month, day = zh_match.groups()
        return f"{year}-{month.zfill(2)}-{day.zfill(2)}"

    dmy_match = re.search(r'(\d{1,2})/(\d{1,2})/(\d{4})', value)
    if dmy_match:
        day, month, year = dmy_match.groups()
        return f"{year}-{month.zfill(2)}-{day.zfill(2)}"

    return value


def _to_number(value):
    """Convert numeric strings from APIs to int/float, preserving zero."""
    if value is None or value == "":
        return 0
    return _clean_number(str(value))


def _build_marksix_result(draw_number, draw_date, regular, special):
    """Build a normalized MarkSix result dict."""
    try:
        regular = [int(n) for n in regular]
        special = int(special)
    except (TypeError, ValueError):
        return None

    if len(regular) != 6:
        return None
    if not all(1 <= n <= 49 for n in regular) or not (1 <= special <= 49):
        return None

    return {
        "lottery_type": "marksix",
        "draw_number": str(draw_number).strip(),
        "draw_date": _parse_date(draw_date),
        "pool_amount": None,
        "sales_amount": None,
        "prize_breakdown": [dict(item) for item in MARKSIX_PRIZE_PLACEHOLDER],
        "red_balls": ",".join(str(n) for n in regular),
        "blue_ball": str(special),
    }


def _merge_marksix_detail(result, html):
    """Merge lottery.hk detail-page jackpot and prize table into a result."""
    if not result:
        return result

    promo_match = re.search(
        r'<div[^>]*class="[^"]*_amount[^"]*"[^>]*>(.*?)</div>',
        html,
        re.S | re.I,
    )
    promo_amount = _parse_money(promo_match.group(1)) if promo_match else None

    prize_breakdown = []
    table_match = re.search(
        r'<h2[^>]*>\s*(?:Prize Breakdown|六合彩獎金分配).*?</h2>\s*<table[^>]*>(.*?)</table>',
        html,
        re.S | re.I,
    )
    if table_match:
        rows = re.findall(r'<tr[^>]*>(.*?)</tr>', table_match.group(1), re.S | re.I)
        level = 1
        for row_html in rows:
            cells = re.findall(r'<td[^>]*>(.*?)</td>', row_html, re.S | re.I)
            if len(cells) < 5:
                continue
            tier = _strip_tags(cells[0])
            if re.search(r'\bTotal\b|总', tier, re.I):
                continue
            amount = _parse_money(cells[2]) or 0
            winners = _clean_number(_strip_tags(cells[3]))
            total = _parse_money(cells[4]) or 0
            prize_breakdown.append({
                "level": level,
                "count": winners,
                "amount_per_note": amount,
                "total_amount": total,
            })
            level += 1

    total_turnover_match = re.search(
        r'Total Turnover.*?<span[^>]*>(.*?)</span>',
        html,
        re.S | re.I,
    )
    if not total_turnover_match:
        total_turnover_match = re.search(
            r'总交易额.*?<span[^>]*>(.*?)</span>',
            html,
            re.S | re.I,
        )

    first_prize = prize_breakdown[0]["amount_per_note"] if prize_breakdown else None
    result["pool_amount"] = promo_amount or first_prize
    result["sales_amount"] = _parse_money(total_turnover_match.group(1)) if total_turnover_match else None
    if prize_breakdown:
        result["prize_breakdown"] = prize_breakdown
    return result


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


QXC_PRIZE_PLACEHOLDER = [
    {"level": 1, "count": 0, "amount_per_note": 0},
    {"level": 2, "count": 0, "amount_per_note": 0},
    {"level": 3, "count": 0, "amount_per_note": 0},
    {"level": 4, "count": 0, "amount_per_note": 0},
    {"level": 5, "count": 0, "amount_per_note": 0},
    {"level": 6, "count": 0, "amount_per_note": 0},
]


async def fetch_qxc_jackpot():
    """Fetch 7星彩 latest numbers from XML and pool amount from 500.com."""
    result = await _try_qxc_500_xml()
    if not result:
        return None

    pool_amount = await _try_qxc_500_pool()
    if pool_amount:
        result["pool_amount"] = pool_amount
    return result


async def _try_qxc_500_xml():
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT, follow_redirects=True) as client:
            url = "https://kaijiang.500.com/static/info/kaijiang/xml/qxc/list.xml"
            resp = await client.get(url, headers=HEADERS)
            if resp.status_code != 200:
                return None
            return _parse_qxc_500_xml(resp.text)
    except Exception as e:
        print(f"QXC 500 XML failed: {e}")
    return None


def _parse_qxc_500_xml(xml):
    try:
        row_match = re.search(
            r'<row[^>]*expect="([^"]+)"[^>]*opencode="([^"]+)"[^>]*opentime="([^"]+)"',
            xml,
            re.I,
        )
        if not row_match:
            return None

        draw_number, opencode, opentime = row_match.groups()
        values = [int(part.strip()) for part in opencode.split(",")]
        if len(values) != 7:
            return None

        regular = values[:6]
        special = values[6]
        if not all(0 <= n <= 9 for n in regular) or not (0 <= special <= 14):
            return None

        return {
            "lottery_type": "qxc",
            "draw_number": draw_number,
            "draw_date": opentime[:10] if opentime else "",
            "pool_amount": None,
            "sales_amount": None,
            "prize_breakdown": [dict(item) for item in QXC_PRIZE_PLACEHOLDER],
            "red_balls": ",".join(str(n) for n in regular),
            "blue_ball": str(special),
        }
    except Exception as e:
        print(f"Parse QXC XML failed: {e}")
        return None


async def _try_qxc_500_pool():
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT, follow_redirects=True) as client:
            url = "https://trade.500.com/qxc/"
            resp = await client.get(url, headers=HEADERS)
            if resp.status_code != 200:
                return None
            return _parse_qxc_pool_html(resp.text)
    except Exception as e:
        print(f"QXC 500 pool failed: {e}")
    return None


def _parse_qxc_pool_html(html):
    pool_match = re.search(
        r'奖池滚存\s*<span[^>]*class="[^"]*red[^"]*"[^>]*>(.*?)</span>\s*元',
        html,
        re.S | re.I,
    )
    if not pool_match:
        pool_match = re.search(
            r'獎池滾存\s*<span[^>]*class="[^"]*red[^"]*"[^>]*>(.*?)</span>\s*元',
            html,
            re.S | re.I,
        )
    if not pool_match:
        return None
    return _parse_chinese_pool_amount(pool_match.group(1))


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
        row_match = re.search(
            r'<tr[^>]*class="t_tr1"[^>]*>(.*?)</tr>',
            html,
            re.S | re.I,
        )
        if row_match:
            row_html = row_match.group(1)
            tds = re.findall(r'<td[^>]*>(.*?)</td>', row_html, re.S | re.I)
            tds = [re.sub(r'<[^>]+>', '', td).strip() for td in tds]
            result = _build_ssq_from_tds(tds)
            if result:
                return result

        # Strategy 2: Try any <tr> that contains a 5-digit draw number in its first <td>
        all_rows = re.findall(r'<tr[^>]*>(.*?)</tr>', html, re.S | re.I)
        for row_html in all_rows:
            tds = re.findall(r'<td[^>]*>(.*?)</td>', row_html, re.S | re.I)
            tds = [re.sub(r'<[^>]+>', '', td).strip() for td in tds]
            if len(tds) >= 10 and re.match(r'^\d{5}$', tds[0]):
                result = _build_ssq_from_tds(tds)
                if result:
                    return result

        # Strategy 3: Try matching the markdown-style text extraction
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
    """Build SSQ dict from table cell values — auto-detects serial-number column."""
    if len(tds) < 10:
        return None

    # Auto-detect column offset.
    # Some versions have an extra leading serial-number column (e.g. "1", "2").
    # The real draw_number is a 5-digit string like "26054".
    offset = 0
    if not re.match(r'^\d{5}$', tds[0].strip()):
        # First col is not a draw number → likely a serial number.
        # Look for 5-digit draw number in next few cols.
        for i in range(1, min(3, len(tds))):
            if re.match(r'^\d{5}$', tds[i].strip()):
                offset = i
                break

    draw_number = tds[offset]
    red_balls   = ",".join(tds[offset + 1 : offset + 7])
    blue_ball   = tds[offset + 7]

    # Remaining columns (after blue ball):
    #   idx +8  = 快乐星期天 (usually empty)
    #   idx +9  = 奖池奖金
    #   idx +10 = 一等奖注数
    #   idx +11 = 一等奖奖金
    #   idx +12 = 二等奖注数
    #   idx +13 = 二等奖奖金
    #   idx +14 = 总投注额
    #   idx +15 = 开奖日期
    base = offset + 8

    pool_amount   = _clean_number(tds[base + 1]) if len(tds) > base + 1 else 0
    first_count   = _clean_number(tds[base + 2]) if len(tds) > base + 2 else 0
    first_amount  = _clean_number(tds[base + 3]) if len(tds) > base + 3 else 0
    second_count  = _clean_number(tds[base + 4]) if len(tds) > base + 4 else 0
    second_amount = _clean_number(tds[base + 5]) if len(tds) > base + 5 else 0
    sales_amount  = _clean_number(tds[base + 6]) if len(tds) > base + 6 else 0
    draw_date     = tds[base + 7] if len(tds) > base + 7 else ""

    prize_breakdown = [
        {"level": 1, "count": first_count,  "amount_per_note": first_amount},
        {"level": 2, "count": second_count, "amount_per_note": second_amount},
        {"level": 3, "count": 0, "amount_per_note": 3000},
        {"level": 4, "count": 0, "amount_per_note": 200},
        {"level": 5, "count": 0, "amount_per_note": 10},
        {"level": 6, "count": 0, "amount_per_note": 5},
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
    """Fetch MarkSix data from multiple sources."""
    # Primary: HKJC official GraphQL is more stable from the production server
    # than HTML pages such as lottery.hk, which can time out by IP route.
    result = await _try_hkjc_graphql()
    if result:
        return result

    # Fallback: lottery.hk latest-results table.
    result = await _try_lottery_hk()
    if result:
        return result

    # Fallback: on.cc 東網 (Hong Kong server can access, but can lag or change markup)
    result = await _try_oncc()
    if result:
        return result

    # Fallback: 500.com
    result = await _try_marksix_500()
    if result:
        return result

    # Last fallback: generic HTML parser
    result = await _try_marksix_fallback()
    if result:
        return result

    return None


async def _try_hkjc_graphql():
    """Try HKJC official GraphQL MarkSix result API."""
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT, follow_redirects=True) as client:
            resp = await client.post(
                "https://info.cld.hkjc.com/graphql/base/",
                headers={
                    **HEADERS,
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "Origin": "https://bet.hkjc.com",
                    "Referer": "https://bet.hkjc.com/ch/marksix/results",
                },
                json={
                    "operationName": "marksixResult",
                    "query": MARKSIX_GRAPHQL_QUERY,
                    "variables": {"lastNDraw": 10},
                },
            )
            if resp.status_code != 200:
                return None
            return _parse_hkjc_graphql(resp.json())
    except Exception as e:
        print(f"HKJC GraphQL MarkSix failed: {e}")
    return None


def _parse_hkjc_graphql(payload):
    try:
        draws = ((payload or {}).get("data") or {}).get("lotteryDraws") or []
        for draw in draws:
            if draw.get("status") != "Result":
                continue

            result = draw.get("drawResult") or {}
            regular = result.get("drawnNo") or []
            special = result.get("xDrawnNo")
            draw_year = str(draw.get("year") or "")
            draw_no = draw.get("no")
            draw_date = str(draw.get("drawDate") or "")[:10]
            if not draw_year or draw_no is None:
                continue

            normalized = _build_marksix_result(
                f"{draw_year[-2:]}/{int(draw_no):03d}",
                draw_date,
                regular,
                special,
            )
            if not normalized:
                continue

            pool = draw.get("lotteryPool") or {}
            unit_bet = _to_number(pool.get("unitBet")) or 10
            prizes = []
            for prize in pool.get("lotteryPrizes") or []:
                level = _to_number(prize.get("type"))
                if not level:
                    continue
                amount = _to_number(prize.get("dividend"))
                winning_units = _to_number(prize.get("winningUnit"))
                count = winning_units / unit_bet if unit_bet else winning_units
                prizes.append({
                    "level": int(level),
                    "count": count,
                    "amount_per_note": amount,
                    "total_amount": amount * count,
                })

            normalized["pool_amount"] = (
                _to_number(pool.get("estimatedPrize"))
                or _to_number(pool.get("derivedFirstPrizeDiv"))
                or _to_number(pool.get("jackpot"))
                or None
            )
            normalized["sales_amount"] = _to_number(pool.get("totalInvestment")) or None
            if prizes:
                normalized["prize_breakdown"] = sorted(prizes, key=lambda item: item["level"])
            return normalized
    except Exception as e:
        print(f"Parse HKJC GraphQL MarkSix failed: {e}")
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


async def _try_lottery_hk():
    """Try lottery.hk MarkSix results page."""
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT, follow_redirects=True) as client:
            url = "https://lottery.hk/zh-hans/liuhecai/kaijiangjieguo/"
            headers = {
                **HEADERS,
                "Referer": "https://lottery.hk/zh-hans/liuhecai/",
                "Accept-Language": "zh-Hans,zh-CN;q=0.9,zh;q=0.8,en;q=0.7",
            }
            resp = await client.get(url, headers=headers)
            if resp.status_code != 200:
                return None
            result = _parse_lottery_hk_marksix(resp.text)
            if not result:
                return None

            detail_url = result.pop("_detail_url", None)
            if not detail_url and result.get("draw_date"):
                detail_url = f"https://lottery.hk/en/mark-six/results/{result['draw_date']}"

            if detail_url:
                detail_resp = await client.get(
                    detail_url,
                    headers={**HEADERS, "Referer": url, "Accept-Language": "en,zh-CN;q=0.9"},
                )
                if detail_resp.status_code == 200:
                    result = _merge_marksix_detail(result, detail_resp.text)
            return result
    except Exception as e:
        print(f"lottery.hk MarkSix failed: {e}")
    return None


def _parse_lottery_hk_marksix(html):
    """Parse lottery.hk MarkSix rows like 26/052 + 6 balls + special ball."""
    try:
        rows = re.findall(r'<tr[^>]*>(.*?)</tr>', html, re.S | re.I)
        for row_html in rows:
            cells = re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', row_html, re.S | re.I)
            if len(cells) < 3:
                continue

            draw_number = _strip_tags(cells[0])
            if not re.match(r'^\d{2}/\d{3}$', draw_number):
                continue

            draw_date = _parse_date(cells[1])
            ball_matches = re.findall(
                r'<li[^>]*class="([^"]*)"[^>]*>\s*(\d{1,2})\s*</li>',
                cells[2],
                re.S | re.I,
            )

            regular = []
            special = None
            for class_name, number in ball_matches:
                if "-plus" in class_name:
                    special = number
                else:
                    regular.append(number)

            result = _build_marksix_result(draw_number, draw_date, regular, special)
            if result:
                detail_match = re.search(r'<a[^>]+href="([^"]+)"[^>]*class="[^"]*-arrow[^"]*"', row_html, re.I)
                if detail_match:
                    result["_detail_url"] = urljoin("https://lottery.hk", detail_match.group(1))
                return result
    except Exception as e:
        print(f"Parse lottery.hk MarkSix failed: {e}")
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

                return _build_marksix_result(draw_number, draw_date, regular, special)
    except Exception as e:
        print(f"Parse MarkSix datachart failed: {e}")
    return None


async def _try_oncc():
    """Try on.cc 東網 MarkSix page."""
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT, follow_redirects=True) as client:
            url = "https://win.on.cc/marksix/"
            headers = {
                **HEADERS,
                "Referer": "https://win.on.cc/",
                "Accept-Language": "zh-HK,zh-TW;q=0.9,zh;q=0.8,en;q=0.7",
            }
            resp = await client.get(url, headers=headers)
            if resp.status_code == 200:
                return _parse_oncc_marksix(resp.text)
    except Exception as e:
        print(f"on.cc failed: {e}")
    return None


def _parse_oncc_marksix(html):
    """Parse on.cc MarkSix HTML — smart multi-pattern parser."""
    try:
        # ── 1. Extract draw number ──
        # Patterns: "第 2025064 期" or "第2025064期"
        num_match = re.search(r'第\s*(\d{6,7})\s*期', html)
        draw_number = num_match.group(1) if num_match else ""
        if not draw_number:
            # Try alternate: "2025064期" or just 7 digits near "期"
            alt_match = re.search(r'(\d{7})\s*期', html)
            draw_number = alt_match.group(1) if alt_match else ""

        # ── 2. Extract draw date ──
        draw_date = ""
        date_patterns = [
            r'(\d{4})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日',
            r'(\d{4})-(\d{2})-(\d{2})',
            r'(\d{2})/(\d{2})/(\d{4})',
        ]
        for pattern in date_patterns:
            m = re.search(pattern, html)
            if m:
                groups = m.groups()
                if '年' in pattern:
                    draw_date = f"{groups[0]}-{groups[1].zfill(2)}-{groups[2].zfill(2)}"
                elif '/' in pattern:
                    draw_date = f"{groups[2]}-{groups[0].zfill(2)}-{groups[1].zfill(2)}"
                else:
                    draw_date = f"{groups[0]}-{groups[1]}-{groups[2]}"
                break

        # ── 3. Extract 7 unique numbers (1-49) ──
        numbers = []

        # Strategy A: Look for a sequence of 7 numbers near the draw number
        # Search within ±2000 chars of the draw number match
        if num_match:
            start = max(0, num_match.start() - 2000)
            end = min(len(html), num_match.end() + 2000)
            vicinity = html[start:end]

            # Find spans/divs/tds/strongs in the vicinity that contain numbers
            elems = re.findall(
                r'(?:<span|<div|<td|<strong|<em|<b|<i)[^>]*>(\d{1,2})</(?:span|div|td|strong|em|b|i)>',
                vicinity,
                re.S | re.I,
            )
            for n_str in elems:
                n = int(n_str)
                if 1 <= n <= 49 and n not in numbers:
                    numbers.append(n)
                    if len(numbers) >= 7:
                        break

            # If still not enough, look for plain text numbers grouped together
            if len(numbers) < 7:
                # Find text like "01, 02, 03, 15, 23, 33, 45" or "01 02 03 15 23 33 45"
                text_groups = re.findall(
                    r'(?:\b\d{1,2}[\s,]+){6,}\b\d{1,2}\b',
                    vicinity,
                )
                for group in text_groups:
                    nums = [int(x) for x in re.findall(r'\b(\d{1,2})\b', group)]
                    for n in nums:
                        if 1 <= n <= 49 and n not in numbers:
                            numbers.append(n)
                    if len(numbers) >= 7:
                        break

        # Strategy B: Fallback — scan whole page for numbers in styled elements
        if len(numbers) < 7:
            # Look for elements with ball-related classes or inline background colors
            ball_elems = re.findall(
                r'<(?:span|div|td)[^>]*(?:class="[^"]*(?:ball|num|no|red|blue|green|special)[^"]*"|style="[^"]*(?:background|color)[^"]*")[^>]*>(\d{1,2})</(?:span|div|td)>',
                html,
                re.S | re.I,
            )
            for n_str in ball_elems:
                n = int(n_str)
                if 1 <= n <= 49 and n not in numbers:
                    numbers.append(n)
                    if len(numbers) >= 7:
                        break

        # Strategy C: Last resort — scan page-wide spans for 1-49 numbers
        if len(numbers) < 7:
            all_spans = re.findall(r'<span[^>]*>(\d{1,2})</span>', html, re.S | re.I)
            for n_str in all_spans:
                n = int(n_str)
                if 1 <= n <= 49 and n not in numbers:
                    numbers.append(n)
                    if len(numbers) >= 7:
                        break

        if len(numbers) < 6:
            return None  # Not enough numbers found

        regular = numbers[:6]
        special = numbers[6] if len(numbers) >= 7 else 0

        return _build_marksix_result(draw_number, draw_date, regular, special)
    except Exception as e:
        print(f"Parse on.cc failed: {e}")
        return None


async def _try_marksix_fallback():
    """Try alternative MarkSix sources."""
    for url in ["https://kj.13322.com/hk6/", "https://kaijiang.500.com/shtml/hk6/"]:
        try:
            async with httpx.AsyncClient(timeout=TIMEOUT, follow_redirects=True) as client:
                resp = await client.get(url, headers=HEADERS)
                if resp.status_code == 200:
                    return _parse_marksix_html_generic(resp.text)
        except Exception as e:
            print(f"MarkSix fallback {url} failed: {e}")
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

        return _build_marksix_result(draw_number, draw_date, regular, special)
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
        ("qxc", fetch_qxc_jackpot()),
    ]
    for lottery_type, task in tasks:
        try:
            result = await asyncio.wait_for(task, timeout=60.0)
            if result:
                results[lottery_type] = result
        except Exception as e:
            print(f"Scrape {lottery_type} failed: {e}")
    return results
