import unittest
from datetime import date

from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.database import ensure_jackpot_integrity
from app.models.draw import Base, Draw
from app.routers.jackpot import _upsert_draw_from_jackpot


class JackpotIntegrityTest(unittest.IsolatedAsyncioTestCase):
    async def test_repairs_legacy_duplicates_and_enforces_unique_key(self):
        engine = create_async_engine("sqlite+aiosqlite:///:memory:")
        try:
            async with engine.begin() as conn:
                await conn.execute(text("""
                    CREATE TABLE jackpot_data (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        lottery_type VARCHAR(20) NOT NULL,
                        draw_number VARCHAR(20) NOT NULL
                    )
                """))
                await conn.execute(text("""
                    INSERT INTO jackpot_data (lottery_type, draw_number)
                    VALUES ('ssq', '26083'), ('ssq', '26083')
                """))
                await ensure_jackpot_integrity(conn)

            async with engine.connect() as conn:
                count = await conn.scalar(text("SELECT COUNT(*) FROM jackpot_data"))
                self.assertEqual(count, 1)
                with self.assertRaises(IntegrityError):
                    await conn.execute(text("""
                        INSERT INTO jackpot_data (lottery_type, draw_number)
                        VALUES ('ssq', '26083')
                    """))
        finally:
            await engine.dispose()

    async def test_qxc_zero_special_number_is_written(self):
        engine = create_async_engine("sqlite+aiosqlite:///:memory:")
        Session = async_sessionmaker(engine, expire_on_commit=False)
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)

            async with Session() as session:
                await _upsert_draw_from_jackpot(session, {
                    "lottery_type": "qxc",
                    "draw_number": "26084",
                    "draw_date": "2026-07-22",
                    "red_balls": "1,2,3,4,5,6",
                    "blue_ball": "0",
                })
                await session.commit()

                result = await session.execute(
                    select(Draw).where(Draw.draw_number == "26084")
                )
                draw = result.scalar_one()
                self.assertEqual(draw.draw_date, date(2026, 7, 22))
                self.assertEqual(draw.special_num, 0)
        finally:
            await engine.dispose()


if __name__ == "__main__":
    unittest.main()
