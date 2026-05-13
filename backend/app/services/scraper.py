from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import LOTTERY_CONFIG
from app.models.draw import Draw, FrequencyCache, PairFrequency


def _has_consecutive(sorted_nums: list[int]) -> bool:
    for i in range(len(sorted_nums) - 1):
        if sorted_nums[i + 1] - sorted_nums[i] == 1:
            return True
    return False


async def rebuild_caches(db: AsyncSession, lottery_type: str = "marksix") -> None:
    """Rebuild frequency_cache and pair_frequency tables for the given lottery type."""
    if lottery_type not in LOTTERY_CONFIG:
        raise ValueError(f"Unknown lottery type: {lottery_type}")

    config = LOTTERY_CONFIG[lottery_type]
    max_regular = config["max_regular"]

    # Clear existing caches for this lottery type only
    await db.execute(
        text("DELETE FROM frequency_cache WHERE lottery_type = :lt"),
        {"lt": lottery_type},
    )
    await db.execute(
        text("DELETE FROM pair_frequency WHERE lottery_type = :lt"),
        {"lt": lottery_type},
    )

    # Fetch all draws for this lottery type
    result = await db.execute(
        select(Draw)
        .where(Draw.lottery_type == lottery_type)
        .order_by(Draw.draw_date.asc())
    )
    draws = result.scalars().all()

    if not draws:
        await db.commit()
        return

    freq: dict[int, dict] = {}
    pair_counts: dict[tuple[int, int], int] = {}
    total_draws = len(draws)

    for idx, draw in enumerate(draws):
        regulars = [draw.num1, draw.num2, draw.num3, draw.num4, draw.num5, draw.num6]
        special = draw.special_num

        for n in regulars:
            if n not in freq:
                freq[n] = {
                    "total": 0, "special": 0,
                    "last_date": draw.draw_date, "last_draw": draw.draw_number,
                    "last_seq": idx, "appearances": [],
                }
            freq[n]["total"] += 1
            freq[n]["last_date"] = draw.draw_date
            freq[n]["last_draw"] = draw.draw_number
            freq[n]["last_seq"] = idx
            freq[n]["appearances"].append(idx)

        if special not in freq:
            freq[special] = {
                "total": 0, "special": 0,
                "last_date": draw.draw_date, "last_draw": draw.draw_number,
                "last_seq": idx, "appearances": [],
            }
        freq[special]["special"] += 1
        freq[special]["last_date"] = draw.draw_date
        freq[special]["last_draw"] = draw.draw_number
        freq[special]["last_seq"] = idx

        # Pair counting
        for i in range(6):
            for j in range(i + 1, 6):
                a, b = regulars[i], regulars[j]
                key = (min(a, b), max(a, b))
                pair_counts[key] = pair_counts.get(key, 0) + 1

    # Insert frequency cache for all valid numbers in this lottery
    for n in range(1, max_regular + 1):
        if n in freq:
            f = freq[n]
            missed = total_draws - f["last_seq"] - 1 if f.get("appearances") else total_draws
            score = f["total"] * 100 + f["special"] * 50
            db.add(FrequencyCache(
                lottery_type=lottery_type,
                number=n,
                total_appearances=f["total"],
                special_appearances=f["special"],
                last_appearance_date=f["last_date"],
                last_appearance_draw=f["last_draw"],
                consecutive_missed=missed,
                hotness_score=score,
            ))
        else:
            db.add(FrequencyCache(
                lottery_type=lottery_type,
                number=n,
                total_appearances=0,
                special_appearances=0,
                consecutive_missed=total_draws,
                hotness_score=0,
            ))

    # Insert pair frequency
    for (a, b), count in pair_counts.items():
        db.add(PairFrequency(
            lottery_type=lottery_type,
            num_a=a, num_b=b, co_occurrences=count,
        ))

    await db.commit()
