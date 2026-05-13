from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models.draw import Draw
from app.schemas.draw import DrawOut, DrawListOut

router = APIRouter(prefix="/api/v1/draws", tags=["draws"])


@router.get("", response_model=DrawListOut)
async def list_draws(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    start_date: str | None = None,
    end_date: str | None = None,
    lottery_type: str = Query("marksix", description="Lottery type: marksix or ssq"),
    db: AsyncSession = Depends(get_db),
):
    q = select(Draw).where(Draw.lottery_type == lottery_type)
    count_q = select(func.count(Draw.id)).where(Draw.lottery_type == lottery_type)

    if start_date:
        q = q.where(Draw.draw_date >= start_date)
        count_q = count_q.where(Draw.draw_date >= start_date)
    if end_date:
        q = q.where(Draw.draw_date <= end_date)
        count_q = count_q.where(Draw.draw_date <= end_date)

    total = (await db.execute(count_q)).scalar() or 0
    draws = (
        (await db.execute(
            q.order_by(Draw.draw_date.desc()).offset((page - 1) * per_page).limit(per_page)
        ))
        .scalars()
        .all()
    )

    return DrawListOut(
        draws=[DrawOut.model_validate(d) for d in draws],
        total=total,
        page=page,
        per_page=per_page,
    )


@router.get("/latest", response_model=DrawOut)
async def latest_draw(
    lottery_type: str = Query("marksix", description="Lottery type: marksix or ssq"),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Draw)
        .where(Draw.lottery_type == lottery_type)
        .order_by(Draw.draw_date.desc())
        .limit(1)
    )
    draw = result.scalars().first()
    if not draw:
        raise HTTPException(status_code=404, detail="No draw data available")
    return DrawOut.model_validate(draw)


@router.get("/{draw_id}", response_model=DrawOut)
async def get_draw(draw_id: int, db: AsyncSession = Depends(get_db)):
    draw = await db.get(Draw, draw_id)
    if not draw:
        raise HTTPException(status_code=404, detail="Draw not found")
    return DrawOut.model_validate(draw)
