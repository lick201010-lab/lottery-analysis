import unittest
from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.config import LOTTERY_CONFIG
from app.models.draw import Base, Draw, FrequencyCache
from app.routers.analysis import generate_numbers
from app.services.import_service import _parse_qxc_xml_row
from app.services.scraper import rebuild_caches


class QxcLotteryTest(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.engine = create_async_engine("sqlite+aiosqlite:///:memory:")
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        self.Session = async_sessionmaker(self.engine, expire_on_commit=False)

    async def asyncTearDown(self):
        await self.engine.dispose()

    def test_qxc_xml_parser_preserves_zero_duplicates_and_order(self):
        draw = _parse_qxc_xml_row(
            '<row expect="26068" opencode="0,9,1,1,6,2,14" '
            'opentime="2026-06-16 21:25:00" />',
            LOTTERY_CONFIG["qxc"],
        )

        self.assertIsNotNone(draw)
        self.assertEqual(draw.lottery_type, "qxc")
        self.assertEqual(draw.draw_number, "26068")
        self.assertEqual(draw.draw_date, date(2026, 6, 16))
        self.assertEqual(
            [draw.num1, draw.num2, draw.num3, draw.num4, draw.num5, draw.num6],
            [0, 9, 1, 1, 6, 2],
        )
        self.assertEqual(draw.special_num, 14)
        self.assertEqual(draw.sum_total, 19)
        self.assertEqual(draw.odd_count, 3)
        self.assertEqual(draw.even_count, 3)
        self.assertEqual(draw.small_count, 4)
        self.assertEqual(draw.big_count, 2)

    async def test_qxc_cache_includes_zero_and_back_zone_numbers(self):
        async with self.Session() as session:
            session.add_all(
                [
                    Draw(
                        lottery_type="qxc",
                        draw_date=date(2026, 6, 14),
                        draw_number="26067",
                        num1=3,
                        num2=6,
                        num3=5,
                        num4=7,
                        num5=1,
                        num6=4,
                        special_num=3,
                        odd_count=4,
                        even_count=2,
                        small_count=4,
                        big_count=2,
                        has_consecutive=True,
                        sum_total=26,
                    ),
                    Draw(
                        lottery_type="qxc",
                        draw_date=date(2026, 6, 16),
                        draw_number="26068",
                        num1=0,
                        num2=9,
                        num3=1,
                        num4=1,
                        num5=6,
                        num6=2,
                        special_num=14,
                        odd_count=3,
                        even_count=3,
                        small_count=4,
                        big_count=2,
                        has_consecutive=True,
                        sum_total=19,
                    ),
                ]
            )
            await session.commit()

            await rebuild_caches(session, "qxc")

            result = await session.execute(
                select(FrequencyCache)
                .where(FrequencyCache.lottery_type == "qxc")
                .order_by(FrequencyCache.number.asc())
            )
            rows = result.scalars().all()
            numbers = [row.number for row in rows]

            self.assertEqual(numbers, list(range(0, 15)))
            zero = next(row for row in rows if row.number == 0)
            fourteen = next(row for row in rows if row.number == 14)
            self.assertEqual(zero.total_appearances, 1)
            self.assertEqual(fourteen.total_appearances, 0)
            self.assertEqual(fourteen.special_appearances, 1)

    async def test_qxc_generator_returns_positional_digits_and_back_zone(self):
        async with self.Session() as session:
            for number in range(0, 15):
                session.add(
                    FrequencyCache(
                        lottery_type="qxc",
                        number=number,
                        total_appearances=number + 1,
                        special_appearances=1 if number in (0, 14) else 0,
                        consecutive_missed=14 - number,
                        hotness_score=(number + 1) * 100,
                    )
                )
            await session.commit()

            result = await generate_numbers(
                lottery_type="qxc",
                strategy="weighted_random",
                count=5,
                db=session,
            )

            self.assertEqual(result["strategy"], "weighted_random")
            self.assertEqual(len(result["sets"]), 5)
            for item in result["sets"]:
                self.assertEqual(len(item["regular"]), 6)
                self.assertTrue(all(0 <= n <= 9 for n in item["regular"]))
                self.assertTrue(0 <= item["special"] <= 14)
