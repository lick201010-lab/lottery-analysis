from fastapi import FastAPI, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import ensure_jackpot_integrity, get_db, engine
from app.models.draw import Base, Draw
from app.routers import analysis, draws, fortune, jackpot, newsletter, scrape
from app.schemas.draw import HealthOut


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await ensure_jackpot_integrity(conn)


app = FastAPI(
    title="彩票分析系统",
    description="Lottery Analysis API (Mark Six & Double Color Ball)",
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(draws.router)
app.include_router(scrape.router)
app.include_router(analysis.router)
app.include_router(jackpot.router)
app.include_router(newsletter.router)
app.include_router(fortune.router)


@app.on_event("startup")
async def startup():
    await init_db()


@app.get("/api/v1/health", response_model=HealthOut)
async def health(
    lottery_type: str = Query("marksix", description="Lottery type: marksix or ssq"),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(func.count(Draw.id)).where(Draw.lottery_type == lottery_type)
    )
    total = result.scalar() or 0
    last_draw_result = await db.execute(
        select(Draw.draw_date)
        .where(Draw.lottery_type == lottery_type)
        .order_by(Draw.draw_date.desc())
        .limit(1)
    )
    last_date = last_draw_result.scalars().first()
    return HealthOut(
        status="ok",
        total_draws=total,
        last_scrape=str(last_date) if last_date else None,
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
