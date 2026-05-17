from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date
from app.database import get_db
from app.models.jackpot import JackpotData
from app.models.draw import Draw
from app.services.jackpot_scraper import scrape_all
from app.services.scraper import rebuild_caches

router = APIRouter(prefix="/api/v1/jackpot", tags=["jackpot"])


@router.get("/latest")
async def get_latest_jackpot(
    lottery_type: str = "ssq",
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(JackpotData)
        .where(JackpotData.lottery_type == lottery_type)
        .order_by(desc(JackpotData.draw_date), desc(JackpotData.draw_number))
        .limit(1)
    )
    row = result.scalar_one_or_none()
    if not row:
        raise HTTPException(status_code=404, detail="No jackpot data found")
    return {
        "lottery_type": row.lottery_type,
        "draw_number": row.draw_number,
        "draw_date": row.draw_date,
        "pool_amount": row.pool_amount,
        "sales_amount": row.sales_amount,
        "prize_breakdown": row.prize_breakdown,
        "red_balls": row.red_balls,
        "blue_ball": row.blue_ball,
    }


@router.get("/history")
async def get_jackpot_history(
    lottery_type: str = "ssq",
    limit: int = 30,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(JackpotData)
        .where(JackpotData.lottery_type == lottery_type)
        .order_by(desc(JackpotData.draw_date), desc(JackpotData.draw_number))
        .limit(limit)
    )
    rows = result.scalars().all()
    return [
        {
            "lottery_type": r.lottery_type,
            "draw_number": r.draw_number,
            "draw_date": r.draw_date,
            "pool_amount": r.pool_amount,
            "sales_amount": r.sales_amount,
            "prize_breakdown": r.prize_breakdown,
            "red_balls": r.red_balls,
            "blue_ball": r.blue_ball,
        }
        for r in rows
    ]


async def _upsert_jackpot(db: AsyncSession, item: dict, inserted: list):
    """Insert or update a jackpot record."""
    existing = await db.execute(
        select(JackpotData).where(
            JackpotData.lottery_type == item["lottery_type"],
            JackpotData.draw_number == item["draw_number"],
        )
    )
    record = existing.scalar_one_or_none()
    if record:
        record.draw_date = item.get("draw_date")
        record.pool_amount = item.get("pool_amount")
        record.sales_amount = item.get("sales_amount")
        record.prize_breakdown = item.get("prize_breakdown", [])
        record.red_balls = item.get("red_balls")
        record.blue_ball = item.get("blue_ball")
    else:
        db.add(JackpotData(**item))
    if item["draw_number"] not in inserted:
        inserted.append(item["draw_number"])


def _has_consecutive(sorted_nums: list[int]) -> bool:
    return any(sorted_nums[i + 1] - sorted_nums[i] == 1 for i in range(len(sorted_nums) - 1))


async def _upsert_draw_from_jackpot(db: AsyncSession, item: dict):
    """Keep the canonical draws table in sync with jackpot-sourced latest data."""
    balls = [n.strip() for n in str(item.get("red_balls") or "").split(",") if n.strip()]
    if len(balls) != 6 or not item.get("blue_ball") or not item.get("draw_date"):
        return

    try:
        regular = sorted(int(n) for n in balls)
        special = int(str(item["blue_ball"]).strip())
        draw_date = date.fromisoformat(str(item["draw_date"]))
    except (TypeError, ValueError):
        return

    midpoint = 33 // 2 if item["lottery_type"] == "ssq" else 49 // 2
    existing = await db.execute(
        select(Draw).where(
            Draw.draw_date == draw_date,
            Draw.lottery_type == item["lottery_type"],
        )
    )
    record = existing.scalar_one_or_none()
    payload = {
        "draw_number": str(item["draw_number"]),
        "num1": regular[0],
        "num2": regular[1],
        "num3": regular[2],
        "num4": regular[3],
        "num5": regular[4],
        "num6": regular[5],
        "special_num": special,
        "odd_count": sum(1 for n in regular if n % 2 == 1),
        "even_count": sum(1 for n in regular if n % 2 == 0),
        "small_count": sum(1 for n in regular if n <= midpoint),
        "big_count": sum(1 for n in regular if n > midpoint),
        "has_consecutive": _has_consecutive(regular),
        "sum_total": sum(regular),
    }

    if record:
        for key, value in payload.items():
            setattr(record, key, value)
    else:
        db.add(Draw(
            lottery_type=item["lottery_type"],
            draw_date=draw_date,
            **payload,
        ))


@router.post("/scrape")
async def trigger_jackpot_scrape(db: AsyncSession = Depends(get_db)):
    data = await scrape_all()
    inserted = []
    touched_lottery_types = set()

    # ── SSQ ──
    ssq_item = data.get("ssq")
    if ssq_item and ssq_item.get("draw_number"):
        await _upsert_jackpot(db, ssq_item, inserted)
        await _upsert_draw_from_jackpot(db, ssq_item)
        touched_lottery_types.add("ssq")

    # ── MarkSix: fallback to draws table if scraper failed ──
    marksix_item = data.get("marksix")
    if not marksix_item or not marksix_item.get("draw_number"):
        result = await db.execute(
            select(Draw)
            .where(Draw.lottery_type == "marksix")
            .order_by(desc(Draw.draw_date))
            .limit(1)
        )
        draw = result.scalar_one_or_none()
        if draw:
            marksix_item = {
                "lottery_type": "marksix",
                "draw_number": draw.draw_number,
                "draw_date": str(draw.draw_date),
                "pool_amount": None,
                "sales_amount": None,
                "prize_breakdown": [
                    {"level": 1, "count": 0, "amount_per_note": 0},
                    {"level": 2, "count": 0, "amount_per_note": 0},
                    {"level": 3, "count": 0, "amount_per_note": 0},
                ],
                "red_balls": ",".join(
                    str(n) for n in [draw.num1, draw.num2, draw.num3, draw.num4, draw.num5, draw.num6]
                ),
                "blue_ball": str(draw.special_num),
            }
        if marksix_item:
            data["marksix"] = marksix_item

    if marksix_item and marksix_item.get("draw_number"):
        await _upsert_jackpot(db, marksix_item, inserted)
        await _upsert_draw_from_jackpot(db, marksix_item)
        touched_lottery_types.add("marksix")

    for lottery_type in touched_lottery_types:
        await rebuild_caches(db, lottery_type)

    await db.commit()
    return {"inserted": inserted, "data": {k: v for k, v in data.items() if v}}
