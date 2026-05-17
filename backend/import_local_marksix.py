"""Import local marksix_draws.json into the database."""
import asyncio
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import date
from sqlalchemy import select
from app.database import async_session, engine
from app.models.draw import Base, Draw
from app.models.jackpot import JackpotData  # noqa: F401 - registers table on Base metadata


def _has_consecutive(sorted_nums: list[int]) -> bool:
    for i in range(len(sorted_nums) - 1):
        if sorted_nums[i + 1] - sorted_nums[i] == 1:
            return True
    return False


async def import_marksix():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Load local data
    local_path = os.path.join(os.path.dirname(__file__), "..", "marksix_draws.json")
    with open(local_path, "r", encoding="utf-8") as f:
        items = json.load(f)

    print(f"Loaded {len(items)} items from marksix_draws.json")

    async with async_session() as db:
        imported = 0
        skipped = 0

        for item in items:
            draw_date_str = item.get("draw_date", "")
            draw_number = item.get("draw_number", "")
            numbers = item.get("numbers", [])
            special = item.get("special_number", 0)

            if not draw_date_str or not draw_number or len(numbers) != 6:
                print(f"Skipping invalid item: {item}")
                continue

            draw_date = date.fromisoformat(draw_date_str)
            sorted_nums = sorted(numbers)
            midpoint = 49 // 2

            # Check if already exists
            existing = await db.execute(
                select(Draw).where(
                    Draw.draw_date == draw_date,
                    Draw.lottery_type == "marksix",
                )
            )
            if existing.scalars().first():
                skipped += 1
                continue

            draw = Draw(
                lottery_type="marksix",
                draw_date=draw_date,
                draw_number=draw_number,
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
            db.add(draw)
            imported += 1

            if imported % 50 == 0:
                await db.flush()

        await db.commit()
        print(f"Done! Imported: {imported}, Skipped (already exists): {skipped}")


if __name__ == "__main__":
    asyncio.run(import_marksix())
