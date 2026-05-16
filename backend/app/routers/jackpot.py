from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.jackpot import JackpotData
from app.models.draw import Draw
from app.services.jackpot_scraper import scrape_all

router = APIRouter(prefix="/api/v1/jackpot", tags=["jackpot"])


@router.get("/latest")
async def get_latest_jackpot(
    lottery_type: str = "ssq",
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(JackpotData)
        .where(JackpotData.lottery_type == lottery_type)
        .order_by(desc(JackpotData.draw_number))
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
        .order_by(desc(JackpotData.draw_number))
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


@router.post("/scrape")
async def trigger_jackpot_scrape(db: AsyncSession = Depends(get_db)):
    data = await scrape_all()
    inserted = []

    # ── SSQ: insert scraped data ──
    ssq_item = data.get("ssq")
    if ssq_item and ssq_item.get("draw_number"):
        existing = await db.execute(
            select(JackpotData).where(
                JackpotData.lottery_type == ssq_item["lottery_type"],
                JackpotData.draw_number == ssq_item["draw_number"],
            )
        )
        if not existing.scalar_one_or_none():
            db.add(JackpotData(**ssq_item))
            inserted.append(ssq_item["draw_number"])

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

    if marksix_item and marksix_item.get("draw_number"):
        existing = await db.execute(
            select(JackpotData).where(
                JackpotData.lottery_type == marksix_item["lottery_type"],
                JackpotData.draw_number == marksix_item["draw_number"],
            )
        )
        if not existing.scalar_one_or_none():
            db.add(JackpotData(**marksix_item))
            inserted.append(marksix_item["draw_number"])

    await db.commit()
    return {"inserted": inserted, "data": {k: v for k, v in data.items() if v}}
