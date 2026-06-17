import json
import re
from datetime import date, timedelta

import requests
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.draw import Draw
from app.config import LOTTERY_CONFIG


def _strip_git_conflicts(text: str) -> str:
    """Remove git merge conflict markers, keeping the HEAD version of each conflict."""
    # Remove everything between ======= and >>>>>>>, and the markers themselves.
    # Pattern: <<<<<<< HEAD\n (keep this content) =======\n (discard this) >>>>>>> branch
    pattern = r"<<<<<<<[^\n]*\n(.*?)=======\n.*?>>>>>>>[^\n]*\n?"
    text = re.sub(pattern, r"\1", text, flags=re.DOTALL)
    return text


def _estimate_ssq_date(issue_number: str) -> date:
    """Estimate draw date from 双色球 issue number like '2018022'.

    Draws happen 3x per week (Tue/Thu/Sun). This estimates ~2.33 days per draw
    starting from Jan 2 of the issue year. Not exact but preserves ordering.
    """
    year = int(issue_number[:4])
    issue_num = int(issue_number[4:])
    days_offset = (issue_num - 1) * 2
    return date(year, 1, 1) + timedelta(days=days_offset + 1)


def _has_consecutive(sorted_nums: list[int]) -> bool:
    for i in range(len(sorted_nums) - 1):
        if sorted_nums[i + 1] - sorted_nums[i] == 1:
            return True
    return False


def _parse_marksix_item(item: dict, config: dict) -> Draw | None:
    """Parse a Mark Six JSON item into a Draw object.

    Expected format: {"id": "25/134", "date": "2025-12-28", "no": ["7","10",...], "sno": "45"}
    """
    draw_date_str = item.get("date", "").strip()
    if not draw_date_str:
        return None

    try:
        draw_date = date.fromisoformat(draw_date_str)
    except (ValueError, TypeError):
        return None

    draw_id = str(item.get("id", f"IMPORTED-{draw_date_str}")).strip()
    no = item.get("no", [])
    sno = item.get("sno", "")

    if len(no) != config["regular_count"]:
        return None

    nums = []
    for n in no:
        try:
            nums.append(int(str(n).strip()))
        except (ValueError, TypeError):
            return None

    try:
        special = int(str(sno).strip())
    except (ValueError, TypeError):
        return None

    max_reg = config["max_regular"]
    max_spe = config["max_special"]
    if not all(1 <= n <= max_reg for n in nums) or not (1 <= special <= max_spe):
        return None

    sorted_nums = sorted(nums)
    midpoint = max_reg // 2

    return Draw(
        lottery_type="marksix",
        draw_date=draw_date,
        draw_number=draw_id,
        num1=sorted_nums[0],
        num2=sorted_nums[1],
        num3=sorted_nums[2],
        num4=sorted_nums[3],
        num5=sorted_nums[4],
        num6=sorted_nums[5],
        special_num=special,
        odd_count=sum(1 for n in sorted_nums if n % 2 == 1),
        even_count=sum(1 for n in sorted_nums if n % 2 == 0),
        small_count=sum(1 for n in sorted_nums if n <= midpoint),
        big_count=sum(1 for n in sorted_nums if n > midpoint),
        has_consecutive=_has_consecutive(sorted_nums),
        sum_total=sum(sorted_nums),
    )


def _parse_ssq_item(item: dict, config: dict) -> Draw | None:
    """Parse a 双色球 JSON ball item into a Draw object.

    Expected format: {"issueNumber": "2018022", "redBall": ["06","08",...], "blueBall": ["08"]}
    """
    issue_number = str(item.get("issueNumber", "")).strip()
    if not issue_number:
        return None

    red_ball = item.get("redBall", [])
    blue_ball = item.get("blueBall", [])

    if len(red_ball) != config["regular_count"] or len(blue_ball) != config["special_count"]:
        return None

    nums = []
    for n in red_ball:
        try:
            nums.append(int(str(n).strip()))
        except (ValueError, TypeError):
            return None

    try:
        special = int(str(blue_ball[0]).strip())
    except (ValueError, TypeError):
        return None

    max_reg = config["max_regular"]
    max_spe = config["max_special"]
    if not all(1 <= n <= max_reg for n in nums) or not (1 <= special <= max_spe):
        return None

    sorted_nums = sorted(nums)
    midpoint = max_reg // 2

    draw_date = _estimate_ssq_date(issue_number)

    return Draw(
        lottery_type="ssq",
        draw_date=draw_date,
        draw_number=issue_number,
        num1=sorted_nums[0],
        num2=sorted_nums[1],
        num3=sorted_nums[2],
        num4=sorted_nums[3],
        num5=sorted_nums[4],
        num6=sorted_nums[5],
        special_num=special,
        odd_count=sum(1 for n in sorted_nums if n % 2 == 1),
        even_count=sum(1 for n in sorted_nums if n % 2 == 0),
        small_count=sum(1 for n in sorted_nums if n <= midpoint),
        big_count=sum(1 for n in sorted_nums if n > midpoint),
        has_consecutive=_has_consecutive(sorted_nums),
        sum_total=sum(sorted_nums),
    )


def _parse_qxc_xml_row(row_xml: str, config: dict) -> Draw | None:
    """Parse one 7星彩 XML row into a Draw object.

    Expected format:
    <row expect="26068" opencode="7,5,1,1,6,2,5" opentime="2026-06-16 21:25:00" />

    QXC is positional: the first six digits must stay in draw order, can be 0-9,
    and can repeat. The seventh digit is the back-zone number and can be 0-14.
    """
    expect_match = re.search(r'expect="([^"]+)"', row_xml)
    opencode_match = re.search(r'opencode="([^"]+)"', row_xml)
    opentime_match = re.search(r'opentime="([^"]+)"', row_xml)

    if not expect_match or not opencode_match or not opentime_match:
        return None

    draw_number = expect_match.group(1).strip()
    opencode = opencode_match.group(1).strip()
    opentime = opentime_match.group(1).strip()

    try:
        draw_date = date.fromisoformat(opentime[:10])
    except (ValueError, TypeError):
        return None

    try:
        values = [int(part.strip()) for part in opencode.split(",")]
    except (ValueError, TypeError):
        return None

    if len(values) != config["regular_count"] + config["special_count"]:
        return None

    nums = values[:config["regular_count"]]
    special = values[-1]

    min_reg = config.get("min_regular", 1)
    max_reg = config["max_regular"]
    min_spe = config.get("min_special", 1)
    max_spe = config["max_special"]

    if not all(min_reg <= n <= max_reg for n in nums) or not (min_spe <= special <= max_spe):
        return None

    midpoint = (min_reg + max_reg) // 2

    return Draw(
        lottery_type="qxc",
        draw_date=draw_date,
        draw_number=draw_number,
        num1=nums[0],
        num2=nums[1],
        num3=nums[2],
        num4=nums[3],
        num5=nums[4],
        num6=nums[5],
        special_num=special,
        odd_count=sum(1 for n in nums if n % 2 == 1),
        even_count=sum(1 for n in nums if n % 2 == 0),
        small_count=sum(1 for n in nums if n <= midpoint),
        big_count=sum(1 for n in nums if n > midpoint),
        has_consecutive=_has_consecutive(nums),
        sum_total=sum(nums),
    )


async def import_github_dataset(db: AsyncSession, lottery_type: str = "marksix") -> int:
    """Import the community-maintained dataset for the given lottery type.

    Returns count of newly imported draws.
    """
    if lottery_type not in LOTTERY_CONFIG:
        raise ValueError(f"Unknown lottery type: {lottery_type}")

    config = LOTTERY_CONFIG[lottery_type]
    resp = requests.get(config["data_url"], timeout=120)
    resp.raise_for_status()

    text = resp.text
    # Strip git merge conflict markers (harmless no-op if none present)
    text = _strip_git_conflicts(text)

    if lottery_type == "qxc":
        rows = re.findall(r'<row\b[^>]*/>', text, re.I)
        imported = 0
        for row in rows:
            try:
                draw = _parse_qxc_xml_row(row, config)
                if not draw:
                    continue

                existing = await db.execute(
                    select(Draw).where(
                        Draw.draw_date == draw.draw_date,
                        Draw.lottery_type == lottery_type,
                    )
                )
                if existing.scalars().first():
                    continue

                db.add(draw)
                imported += 1

                if imported % 500 == 0:
                    await db.flush()
            except (ValueError, KeyError, TypeError):
                continue

        await db.commit()
        return imported

    raw_data = json.loads(text)

    if lottery_type == "marksix":
        items = raw_data  # top-level list
    elif lottery_type == "ssq":
        items = raw_data.get("balls", [])
    else:
        items = raw_data if isinstance(raw_data, list) else raw_data.get("balls", raw_data)

    if lottery_type == "marksix":
        parse_fn = _parse_marksix_item
    elif lottery_type == "ssq":
        parse_fn = _parse_ssq_item
    else:
        raise ValueError(f"No parser for lottery type: {lottery_type}")

    imported = 0

    for item in items:
        try:
            draw = parse_fn(item, config)
            if not draw:
                continue

            existing = await db.execute(
                select(Draw).where(
                    Draw.draw_date == draw.draw_date,
                    Draw.lottery_type == lottery_type,
                )
            )
            if existing.scalars().first():
                continue

            db.add(draw)
            imported += 1

            if imported % 500 == 0:
                await db.flush()
        except (ValueError, KeyError, TypeError):
            continue

    await db.commit()
    return imported
