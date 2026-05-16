from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.jackpot import JackpotData
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
    for lottery_type, item in data.items():
        if not item:
            continue
        # Check if exists
        existing = await db.execute(
            select(JackpotData)
            .where(
                JackpotData.lottery_type == item["lottery_type"],
                JackpotData.draw_number == item["draw_number"],
            )
        )
        if existing.scalar_one_or_none():
            continue
        record = JackpotData(**item)
        db.add(record)
        inserted.append(item["draw_number"])
    await db.commit()
    return {"inserted": inserted, "data": data}
