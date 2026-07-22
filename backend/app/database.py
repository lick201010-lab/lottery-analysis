from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection, create_async_engine, async_sessionmaker
from app.config import DATABASE_URL

engine = create_async_engine(DATABASE_URL, echo=False)
async_session = async_sessionmaker(engine, expire_on_commit=False)


async def ensure_jackpot_integrity(conn: AsyncConnection) -> None:
    """Repair legacy SQLite databases that predate the jackpot unique key."""
    if conn.dialect.name != "sqlite":
        return

    await conn.execute(text("""
        DELETE FROM jackpot_data
        WHERE id NOT IN (
            SELECT MAX(id)
            FROM jackpot_data
            GROUP BY lottery_type, draw_number
        )
    """))
    await conn.execute(text("""
        CREATE UNIQUE INDEX IF NOT EXISTS uq_jackpot_lottery_draw_idx
        ON jackpot_data (lottery_type, draw_number)
    """))


async def get_db():
    async with async_session() as session:
        yield session
