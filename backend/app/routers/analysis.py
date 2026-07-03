from math import comb
from itertools import combinations as iter_combinations
from typing import List, Optional, Literal

from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.config import LOTTERY_CONFIG
from app.models.draw import Draw, FrequencyCache, PairFrequency

router = APIRouter(prefix="/api/v1/analysis", tags=["analysis"])

class LayeredPickRequest(BaseModel):
    lottery_type: Literal["marksix", "ssq", "qxc"] = "marksix"
    history_periods: int = Field(50, ge=10, le=500)
    hot_pct: int = Field(60, ge=20, le=100)
    hot_count: int = Field(3, ge=0, le=10)
    cold_count: int = Field(1, ge=0, le=10)
    trend_periods: int = Field(20, ge=5, le=100)
    consecutive: Literal["any", "include", "exclude"] = "any"
    odd_even: Literal["any", "more_odd", "more_even", "balanced"] = "any"
    big_small: Literal["any", "more_big", "more_small", "balanced"] = "any"
    sum_min: Optional[int] = None
    sum_max: Optional[int] = None
    must_include: List[int] = Field(default_factory=list)
    must_exclude: List[int] = Field(default_factory=list)
    pool1_size: int = Field(10, ge=6, le=30)
    pool2_size: int = Field(8, ge=6, le=20)
    pool3_size: int = Field(6, ge=6, le=12)
    qxc_pool1_size: int = Field(5, ge=2, le=10)
    qxc_pool2_size: int = Field(4, ge=2, le=8)
    qxc_pool3_size: int = Field(3, ge=1, le=6)
    count: int = Field(5, ge=1, le=10)


@router.get("/frequency")
async def frequency(
    lottery_type: str = Query("marksix", description="Lottery type: marksix or ssq"),
    type: str = Query("regular", description="regular, special, or both"),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(FrequencyCache)
        .where(FrequencyCache.lottery_type == lottery_type)
        .order_by(FrequencyCache.total_appearances.desc())
    )
    rows = result.scalars().all()
    return [
        {
            "number": r.number,
            "total_appearances": r.total_appearances,
            "special_appearances": r.special_appearances,
            "last_appearance_date": str(r.last_appearance_date) if r.last_appearance_date else None,
            "last_appearance_draw": r.last_appearance_draw,
            "consecutive_missed": r.consecutive_missed,
            "hotness_score": r.hotness_score,
        }
        for r in rows
    ]


@router.get("/hot-cold")
async def hot_cold(
    lottery_type: str = Query("marksix", description="Lottery type: marksix or ssq"),
    cutoff: int = Query(10, description="Number of hot/cold numbers to return"),
    db: AsyncSession = Depends(get_db),
):
    hot_result = await db.execute(
        select(FrequencyCache)
        .where(FrequencyCache.lottery_type == lottery_type)
        .order_by(FrequencyCache.hotness_score.desc())
        .limit(cutoff)
    )
    hot = hot_result.scalars().all()

    cold_result = await db.execute(
        select(FrequencyCache)
        .where(FrequencyCache.lottery_type == lottery_type)
        .order_by(FrequencyCache.hotness_score.asc())
        .limit(cutoff)
    )
    cold = cold_result.scalars().all()

    def serialize(r):
        return {
            "number": r.number,
            "total_appearances": r.total_appearances,
            "special_appearances": r.special_appearances,
            "consecutive_missed": r.consecutive_missed,
            "hotness_score": r.hotness_score,
        }

    return {"hot": [serialize(r) for r in hot], "cold": [serialize(r) for r in cold]}


@router.get("/overdue")
async def overdue(
    lottery_type: str = Query("marksix", description="Lottery type: marksix or ssq"),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(FrequencyCache)
        .where(FrequencyCache.lottery_type == lottery_type)
        .order_by(FrequencyCache.consecutive_missed.desc())
    )
    rows = result.scalars().all()
    return [
        {
            "number": r.number,
            "total_appearances": r.total_appearances,
            "consecutive_missed": r.consecutive_missed,
            "last_appearance_date": str(r.last_appearance_date) if r.last_appearance_date else None,
            "last_appearance_draw": r.last_appearance_draw,
        }
        for r in rows
    ]


@router.get("/trend/{number}")
async def trend(
    number: int,
    lottery_type: str = Query("marksix", description="Lottery type: marksix or ssq"),
    window: int = Query(50, description="Rolling window size"),
    db: AsyncSession = Depends(get_db),
):
    if lottery_type not in LOTTERY_CONFIG:
        raise HTTPException(status_code=400, detail=f"Unknown lottery type: {lottery_type}")
    config = LOTTERY_CONFIG[lottery_type]
    min_number = min(config.get("min_regular", 1), config.get("min_special", 1))
    max_number = max(config["max_regular"], config.get("max_special", config["max_regular"]))
    if number < min_number or number > max_number:
        raise HTTPException(
            status_code=400,
            detail=f"Number must be between {min_number} and {max_number}",
        )

    result = await db.execute(
        select(Draw)
        .where(Draw.lottery_type == lottery_type)
        .order_by(Draw.draw_date.asc())
    )
    draws = result.scalars().all()

    # Build rolling frequency data
    data = []
    regular_nums = []

    for draw in draws:
        regular_nums.append({
            draw.num1, draw.num2, draw.num3, draw.num4, draw.num5, draw.num6,
        })

    for i in range(len(regular_nums)):
        if i < window - 1:
            continue
        count = 0
        for j in range(i - window + 1, i + 1):
            if number in regular_nums[j]:
                count += 1
        data.append({
            "draw_date": str(draws[i].draw_date),
            "draw_number": draws[i].draw_number,
            "count": count,
        })

    return {
        "number": number,
        "window": window,
        "data": data,
    }


@router.get("/summary")
async def summary(
    lottery_type: str = Query("marksix", description="Lottery type: marksix or ssq"),
    db: AsyncSession = Depends(get_db),
):
    # Total draws
    total_result = await db.execute(
        select(func.count(Draw.id)).where(Draw.lottery_type == lottery_type)
    )
    total = total_result.scalar() or 0

    # Latest draw date
    latest_result = await db.execute(
        select(Draw.draw_date)
        .where(Draw.lottery_type == lottery_type)
        .order_by(Draw.draw_date.desc())
        .limit(1)
    )
    latest_date = latest_result.scalars().first()

    # Top 3 hot
    hot_result = await db.execute(
        select(FrequencyCache)
        .where(FrequencyCache.lottery_type == lottery_type)
        .order_by(FrequencyCache.hotness_score.desc())
        .limit(3)
    )
    hot = hot_result.scalars().all()

    # Top 3 cold
    cold_result = await db.execute(
        select(FrequencyCache)
        .where(FrequencyCache.lottery_type == lottery_type)
        .order_by(FrequencyCache.hotness_score.asc())
        .limit(3)
    )
    cold = cold_result.scalars().all()

    # Most overdue
    overdue_result = await db.execute(
        select(FrequencyCache)
        .where(FrequencyCache.lottery_type == lottery_type)
        .order_by(FrequencyCache.consecutive_missed.desc())
        .limit(1)
    )
    most_overdue = overdue_result.scalars().first()

    # Top 3 pairs
    pair_result = await db.execute(
        select(PairFrequency)
        .where(PairFrequency.lottery_type == lottery_type)
        .order_by(PairFrequency.co_occurrences.desc())
        .limit(3)
    )
    top_pairs = pair_result.scalars().all()

    def freq_to_dict(r):
        return {
            "number": r.number,
            "total_appearances": r.total_appearances,
            "consecutive_missed": r.consecutive_missed,
            "hotness_score": r.hotness_score,
        }

    return {
        "total_draws": total,
        "latest_date": str(latest_date) if latest_date else None,
        "top_hot": [freq_to_dict(r) for r in hot],
        "top_cold": [freq_to_dict(r) for r in cold],
        "most_overdue": freq_to_dict(most_overdue) if most_overdue else None,
        "top_pairs": [
            {"num_a": p.num_a, "num_b": p.num_b, "co_occurrences": p.co_occurrences}
            for p in top_pairs
        ],
    }


@router.get("/patterns/distribution")
async def patterns_distribution(
    lottery_type: str = Query("marksix"),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Draw).where(Draw.lottery_type == lottery_type).order_by(Draw.draw_date.asc())
    )
    draws = result.scalars().all()
    config = LOTTERY_CONFIG.get(lottery_type, LOTTERY_CONFIG["marksix"])
    min_reg = config.get("min_regular", 1)
    max_reg = config["max_regular"]

    odd_even_counts = {}
    big_small_counts = {}
    consecutive_counts = {}
    range_labels = []
    range_counts = {}
    sum_values = []

    # Dynamic ranges
    range_size = max(10, max_reg // 5)
    for start in range(min_reg, max_reg + 1, range_size):
        end = min(start + range_size - 1, max_reg)
        label = f"{start}-{end}"
        range_labels.append(label)
        range_counts[label] = 0

    for draw in draws:
        regulars = [draw.num1, draw.num2, draw.num3, draw.num4, draw.num5, draw.num6]

        # Odd/even
        oe_key = f"{draw.odd_count}:{draw.even_count}"
        odd_even_counts[oe_key] = odd_even_counts.get(oe_key, 0) + 1

        # Big/small
        midpoint = max_reg // 2
        small = sum(1 for n in regulars if n <= midpoint)
        big = 6 - small
        bs_key = f"{small}:{big}"
        big_small_counts[bs_key] = big_small_counts.get(bs_key, 0) + 1

        # Consecutive
        sorted_ns = sorted(regulars)
        cons_count = 0
        for i in range(len(sorted_ns) - 1):
            if sorted_ns[i + 1] - sorted_ns[i] == 1:
                cons_count += 1
        consecutive_counts[str(cons_count)] = consecutive_counts.get(str(cons_count), 0) + 1

        # Range distribution
        for n in regulars:
            idx = min((n - min_reg) // range_size, len(range_labels) - 1)
            range_counts[range_labels[idx]] += 1

        # Sum
        sum_values.append(draw.sum_total)

    # Build range data sorted by label
    range_data = [{"range": lbl, "count": range_counts[lbl]} for lbl in range_labels]

    # Sum distribution histogram
    if sum_values:
        sum_min = min(sum_values)
        sum_max = max(sum_values)
        num_bins = 20
        bin_width = max(1, (sum_max - sum_min) // num_bins)
        bins = {}
        for s in sum_values:
            b = (s // bin_width) * bin_width
            bins[b] = bins.get(b, 0) + 1
        sum_histogram = [{"bin": k, "count": v} for k, v in sorted(bins.items())]
    else:
        sum_histogram = []

    # Summary stats
    total = len(draws)
    odd_total = sum(d.odd_count for d in draws)
    even_total = sum(d.even_count for d in draws)
    small_total = sum(d.small_count for d in draws)
    big_total = sum(d.big_count for d in draws)

    # Format to match frontend expectations
    has_consecutive = sum(c for k, c in consecutive_counts.items() if int(k) > 0)
    no_consecutive = sum(c for k, c in consecutive_counts.items() if int(k) == 0)

    return {
        "total_draws": total,
        "odd_even": {
            "labels": ["奇数", "偶数"],
            "values": [odd_total, even_total],
        },
        "big_small": {
            "labels": ["大数", "小数"],
            "values": [big_total, small_total],
        },
        "consecutive": {
            "has_consecutive": has_consecutive,
            "no_consecutive": no_consecutive,
        } if has_consecutive or no_consecutive else {
            "labels": list(consecutive_counts.keys()),
            "values": list(consecutive_counts.values()),
        },
        "range_distribution": {
            "labels": [r["range"] for r in range_data],
            "values": [r["count"] for r in range_data],
        },
        "sum_distribution": {
            "labels": [str(h["bin"]) for h in sum_histogram],
            "values": [h["count"] for h in sum_histogram],
        },
        "summary": {
            "odd_pct": round(odd_total / (odd_total + even_total) * 100, 1) if (odd_total + even_total) > 0 else 0,
            "even_pct": round(even_total / (odd_total + even_total) * 100, 1) if (odd_total + even_total) > 0 else 0,
            "small_pct": round(small_total / (small_total + big_total) * 100, 1) if (small_total + big_total) > 0 else 0,
            "big_pct": round(big_total / (small_total + big_total) * 100, 1) if (small_total + big_total) > 0 else 0,
            "avg_sum": round(sum(sum_values) / total, 1) if total > 0 else 0,
            "sum_range": f"{min(sum_values)}-{max(sum_values)}" if sum_values else "N/A",
        },
    }


@router.get("/pairs/top")
async def pairs_top(
    lottery_type: str = Query("marksix"),
    db: AsyncSession = Depends(get_db),
    limit: int = Query(50),
):
    result = await db.execute(
        select(PairFrequency)
        .where(PairFrequency.lottery_type == lottery_type)
        .order_by(PairFrequency.co_occurrences.desc())
        .limit(limit)
    )
    pairs = result.scalars().all()
    return [
        {"num_a": p.num_a, "num_b": p.num_b, "co_occurrences": p.co_occurrences}
        for p in pairs
    ]


@router.get("/pairs/top/{number}")
async def pairs_for_number(
    number: int,
    lottery_type: str = Query("marksix"),
    db: AsyncSession = Depends(get_db),
    limit: int = Query(50),
):
    result = await db.execute(
        select(PairFrequency)
        .where(
            PairFrequency.lottery_type == lottery_type,
            (PairFrequency.num_a == number) | (PairFrequency.num_b == number),
        )
        .order_by(PairFrequency.co_occurrences.desc())
        .limit(limit)
    )
    pairs = result.scalars().all()
    return [
        {"num_a": p.num_a, "num_b": p.num_b, "co_occurrences": p.co_occurrences}
        for p in pairs
    ]


@router.get("/generate")
async def generate_numbers(
    lottery_type: str = Query("marksix"),
    strategy: str = Query("hot", description="hot, cold, balanced, weighted_random, pair_chain, overdue"),
    count: int = Query(1, ge=1, le=10, description="Number of sets to generate"),
    db: AsyncSession = Depends(get_db),
):
    import random

    config = LOTTERY_CONFIG.get(lottery_type, LOTTERY_CONFIG["marksix"])
    max_reg = config["max_regular"]
    max_spe = config["max_special"]
    reg_count = config["regular_count"]

    freq_result = await db.execute(
        select(FrequencyCache)
        .where(FrequencyCache.lottery_type == lottery_type)
        .order_by(FrequencyCache.hotness_score.desc())
    )
    freqs = freq_result.scalars().all()
    freq_by_num = {f.number: f for f in freqs}

    pair_result = await db.execute(
        select(PairFrequency)
        .where(PairFrequency.lottery_type == lottery_type)
    )
    all_pairs = pair_result.scalars().all()
    pair_index: dict[int, list[tuple[int, int]]] = {}
    for p in all_pairs:
        pair_index.setdefault(p.num_a, []).append((p.num_b, p.co_occurrences))
        pair_index.setdefault(p.num_b, []).append((p.num_a, p.co_occurrences))

    sets = []

    for _ in range(count):
        if lottery_type == "qxc":
            regulars = _gen_qxc_regular(freqs, strategy, reg_count)
            special = _gen_qxc_special(freqs)
            sets.append({"regular": regulars, "special": special, "strategy": strategy})
            continue

        if strategy == "hot":
            regulars = _gen_hot(freqs, reg_count, max_reg)
        elif strategy == "cold":
            regulars = _gen_cold(freqs, reg_count, max_reg)
        elif strategy == "weighted_random":
            regulars = _gen_weighted_random(freqs, reg_count, max_reg)
        elif strategy == "pair_chain":
            regulars = _gen_pair_chain(freqs, pair_index, reg_count, max_reg)
        elif strategy == "overdue":
            regulars = _gen_overdue(freqs, reg_count, max_reg)
        else:
            regulars = _gen_balanced(freqs, reg_count, max_reg)

        special = _gen_special(freqs, max_spe)
        sets.append({"regular": sorted(regulars), "special": special, "strategy": strategy})

    return {"sets": sets, "strategy": strategy}


def _weighted_sample_without_replacement(values, weights, count):
    import random

    picked = []
    remaining = list(values)
    remaining_weights = [max(float(w), 1.0) for w in weights]
    for _ in range(min(count, len(remaining))):
        idx = random.choices(range(len(remaining)), weights=remaining_weights, k=1)[0]
        picked.append(remaining.pop(idx))
        remaining_weights.pop(idx)
    return picked


def _gen_hot(freqs, count, max_reg):
    valid = [f for f in freqs if f.number <= max_reg]
    pool = valid[:max(count * 3, count + 4)]
    return _weighted_sample_without_replacement(
        [f.number for f in pool],
        [max(f.hotness_score, 1) for f in pool],
        count,
    )


def _gen_cold(freqs, count, max_reg):
    pool = [f for f in reversed(freqs) if f.number <= max_reg][:max(count * 3, count + 4)]
    max_score = max((f.hotness_score for f in pool), default=1)
    return _weighted_sample_without_replacement(
        [f.number for f in pool],
        [max_score - f.hotness_score + 1 for f in pool],
        count,
    )


def _gen_balanced(freqs, count, max_reg):
    import random
    valid = [f for f in freqs if f.number <= max_reg]
    hot_pool = valid[:len(valid) // 3]
    mid_pool = valid[len(valid)//3:2*len(valid)//3]
    cold_pool = valid[2*len(valid)//3:]

    result = []
    for pool, n in [(hot_pool, (count + 1)//3), (mid_pool, count//3), (cold_pool, count - (count+1)//3 - count//3)]:
        if pool:
            picked = random.sample([f.number for f in pool], min(n, len(pool)))
            result.extend(picked)
    return result[:count]


def _gen_weighted_random(freqs, count, max_reg):
    valid = [(f.number, max(f.hotness_score, 1)) for f in freqs if f.number <= max_reg]
    return _weighted_sample_without_replacement(
        [v[0] for v in valid],
        [v[1] for v in valid],
        count,
    )


def _gen_pair_chain(freqs, pair_index, count, max_reg):
    import random
    freq_nums = [f.number for f in freqs if f.number <= max_reg]

    if not freq_nums:
        return [1, 2, 3, 4, 5, 6][:count]

    seed_pool = freq_nums[:max(count * 2, count + 2)]
    current = random.choice(seed_pool)
    result = [current]

    while len(result) < count:
        pairs = pair_index.get(current, [])
        if not pairs:
            for n in freq_nums:
                if n not in result:
                    result.append(n)
                    current = n
                    break
            continue

        pairs_sorted = sorted(pairs, key=lambda x: x[1], reverse=True)
        pair_candidates = [
            (nb, co_oc)
            for (nb, co_oc) in pairs_sorted
            if nb not in result and nb <= max_reg
        ][:max(count, 3)]
        best_next = None
        if pair_candidates:
            best_next = random.choices(
                [nb for nb, _ in pair_candidates],
                weights=[max(co_oc, 1) for _, co_oc in pair_candidates],
                k=1,
            )[0]

        if best_next is None:
            for n in freq_nums:
                if n not in result:
                    best_next = n
                    break

        if best_next is None:
            break

        result.append(best_next)
        current = best_next

    return result[:count]


def _gen_overdue(freqs, count, max_reg):
    overdue = sorted(
        [f for f in freqs if f.number <= max_reg],
        key=lambda f: f.consecutive_missed,
        reverse=True,
    )
    pool = overdue[:max(count * 3, count + 4)]
    return _weighted_sample_without_replacement(
        [f.number for f in pool],
        [max(f.consecutive_missed, 1) for f in pool],
        count,
    )


def _gen_special(freqs, max_spe):
    import random
    valid = [f for f in freqs if f.number <= max_spe]
    if not valid:
        return 1
    return random.choices(
        [f.number for f in valid],
        weights=[max(f.hotness_score, 1) for f in valid],
        k=1,
    )[0]


@router.post("/layered_pick")
async def layered_pick(
    payload: LayeredPickRequest,
    db: AsyncSession = Depends(get_db),
):
    """分层筛选漏斗：按 pool1_size → pool2_size → pool3_size 三步逐步压缩号码池。

    Step 1（大底）：冷热配比 + 补充号 → 按综合得分保留 pool1_size 个
    Step 2（走势）：连号特征过滤 → 按综合得分保留 pool2_size 个
    Step 3（精选）：奇偶/大小/胆码/杀号 → 按综合得分保留 pool3_size 个（最终投注号码）
    """
    if payload.lottery_type == "qxc":
        return await _qxc_position_layered_pick(payload, db)

    config = LOTTERY_CONFIG.get(payload.lottery_type, LOTTERY_CONFIG["marksix"])
    max_reg = config["max_regular"]
    max_spe = config["max_special"]
    midpoint = max_reg // 2

    # 校验漏斗大小顺序
    if not (payload.pool1_size >= payload.pool2_size >= payload.pool3_size >= 6):
        raise HTTPException(
            status_code=400,
            detail=f"漏斗步数必须满足 pool1_size({payload.pool1_size}) >= pool2_size({payload.pool2_size}) >= pool3_size({payload.pool3_size}) >= 6",
        )

    # 取近 N 期 draws（按 draw_date 倒序）
    draws_result = await db.execute(
        select(Draw)
        .where(Draw.lottery_type == payload.lottery_type)
        .order_by(Draw.draw_date.desc())
        .limit(payload.history_periods)
    )
    recent_draws = list(draws_result.scalars().all())

    if not recent_draws:
        raise HTTPException(status_code=404, detail="历史开奖数据为空，无法做分层筛选")

    # 取 FrequencyCache 用于综合得分
    freq_result = await db.execute(
        select(FrequencyCache).where(FrequencyCache.lottery_type == payload.lottery_type)
    )
    freq_cache = {f.number: f for f in freq_result.scalars().all()}

    # ===== 历史出现统计（近 history_periods 期）=====
    appearance_count = {n: 0 for n in range(1, max_reg + 1)}
    for d in recent_draws:
        for n in (d.num1, d.num2, d.num3, d.num4, d.num5, d.num6):
            if 1 <= n <= max_reg:
                appearance_count[n] += 1

    # ===== 近期走势出现统计（trend_periods 期）=====
    trend_draws = recent_draws[: payload.trend_periods]
    trend_appearance = {n: 0 for n in range(1, max_reg + 1)}
    appearance_in_consecutive = {n: 0 for n in range(1, max_reg + 1)}
    for d in trend_draws:
        nums = sorted([d.num1, d.num2, d.num3, d.num4, d.num5, d.num6])
        had_consecutive = any(nums[i + 1] - nums[i] == 1 for i in range(len(nums) - 1))
        for n in nums:
            if 1 <= n <= max_reg:
                trend_appearance[n] += 1
                if had_consecutive:
                    appearance_in_consecutive[n] += 1

    def composite_score(number):
        """综合得分 = 历史热度×2 + 近期走势×3 + 遗漏修正（最多+10）"""
        base = appearance_count.get(number, 0) * 2
        trend = trend_appearance.get(number, 0) * 3
        fc = freq_cache.get(number)
        overdue_bonus = min(fc.consecutive_missed, 10) if fc else 0
        return base + trend + overdue_bonus

    # ===== Step 1: 大底 — 冷热配比 + 综合得分截断 =====
    all_numbers = list(range(1, max_reg + 1))

    sorted_by_hot = sorted(all_numbers, key=lambda n: (-appearance_count[n], n))
    sorted_by_cold = sorted(all_numbers, key=lambda n: (appearance_count[n], n))

    hot_count = min(payload.hot_count, payload.pool1_size)
    cold_count = min(payload.cold_count, max(0, payload.pool1_size - hot_count))

    hot_numbers = sorted_by_hot[:hot_count]
    hot_set = set(hot_numbers)

    cold_numbers = []
    for n in sorted_by_cold:
        if n not in hot_set:
            cold_numbers.append(n)
        if len(cold_numbers) >= cold_count:
            break
    cold_set = set(cold_numbers)

    selected_set = hot_set | cold_set
    supplement_numbers = []
    for n in sorted_by_hot:
        if n not in selected_set:
            supplement_numbers.append(n)
        if len(selected_set) + len(supplement_numbers) >= payload.pool1_size:
            break

    # 综合得分排序后截断到 pool1_size
    step1_candidates = sorted(selected_set | set(supplement_numbers))
    step1_candidates.sort(key=lambda n: -composite_score(n))
    pool1 = sorted(step1_candidates[: payload.pool1_size])
    pool1_set = set(pool1)
    pool1_eliminated = sorted(n for n in all_numbers if n not in pool1_set)

    # ===== Step 2: 走势 — 连号特征过滤 + 综合得分截断 =====
    if payload.consecutive == "include":
        step2_filtered = [n for n in pool1 if appearance_in_consecutive.get(n, 0) > 0]
    elif payload.consecutive == "exclude":
        step2_filtered = [
            n for n in pool1
            if trend_appearance.get(n, 0) > appearance_in_consecutive.get(n, 0)
            or trend_appearance.get(n, 0) == 0
        ]
    else:
        step2_filtered = list(pool1)

    if len(step2_filtered) < payload.pool2_size:
        # 过滤后不够，从 pool1 里按得分补
        extras = [n for n in sorted(pool1, key=lambda n: -composite_score(n)) if n not in step2_filtered]
        step2_filtered = step2_filtered + extras

    step2_filtered.sort(key=lambda n: -composite_score(n))
    pool2 = sorted(step2_filtered[: payload.pool2_size])
    pool2_set = set(pool2)
    pool2_eliminated = sorted(n for n in pool1 if n not in pool2_set)

    # ===== Step 3: 精选 — 奇偶/大小/胆码/杀号 + 综合得分截断 =====
    must_include = [n for n in payload.must_include if 1 <= n <= max_reg]
    must_exclude_set = set(n for n in payload.must_exclude if 1 <= n <= max_reg)
    must_include_set = set(must_include)

    step3_filtered = [n for n in pool2 if n not in must_exclude_set]
    step3_filtered = _apply_odd_even(step3_filtered, payload.odd_even)
    step3_filtered = _apply_big_small(step3_filtered, payload.big_small, midpoint)

    # 保证胆码必含
    for n in must_include:
        if n not in step3_filtered:
            step3_filtered.append(n)

    # 如果过滤后不够，从 pool2 里补（排除杀号）
    if len(step3_filtered) < payload.pool3_size:
        extras = [
            n for n in sorted(pool2, key=lambda n: -composite_score(n))
            if n not in step3_filtered and n not in must_exclude_set
        ]
        step3_filtered = step3_filtered + extras

    step3_filtered.sort(key=lambda n: (-1 if n in must_include_set else 0, -composite_score(n)))
    pool3 = sorted(step3_filtered[: payload.pool3_size])

    # 兜底：仍然不够就从全集补热号
    if len(pool3) < payload.pool3_size:
        all_extra = sorted(
            (n for n in all_numbers if n not in pool3 and n not in must_exclude_set),
            key=lambda n: -composite_score(n),
        )
        pool3 = sorted(pool3 + all_extra[: payload.pool3_size - len(pool3)])

    pool3_set = set(pool3)
    pool3_eliminated = sorted(n for n in pool2 if n not in pool3_set)

    # ===== 特别号候选 =====
    spe_count = {n: 0 for n in range(1, max_spe + 1)}
    for d in recent_draws:
        if d.special_num and 1 <= d.special_num <= max_spe:
            spe_count[d.special_num] += 1
    spe_sorted = sorted(spe_count.items(), key=lambda x: (-x[1], x[0]))
    special_pool = spe_sorted[:5]
    special_candidates = [n for n, _ in special_pool]
    special_pick = (
        _weighted_sample_without_replacement(
            special_candidates,
            [max(count, 1) for _, count in special_pool],
            1,
        )[0]
        if special_candidates
        else 1
    )

    # ===== 推荐组合：从 pool3 里按综合得分总和排出 top 5 组 6 选组合 =====
    combinations_list = []
    if len(pool3) >= 6:
        all_combos = list(iter_combinations(pool3, 6))
        all_combos.sort(key=lambda c: -sum(composite_score(n) for n in c))
        candidate_limit = max(payload.count * 8, payload.count + 5)

        filtered = []
        for combo in all_combos:
            s = sum(combo)
            if payload.sum_min is not None and s < payload.sum_min:
                continue
            if payload.sum_max is not None and s > payload.sum_max:
                continue
            filtered.append(combo)
            if len(filtered) >= candidate_limit:
                break

        # 兜底：和值过滤后空集就用未过滤的 top 5
        candidate_pool = filtered if filtered else all_combos[:candidate_limit]
        chosen = _weighted_sample_without_replacement(
            candidate_pool,
            [max(sum(composite_score(n) for n in combo), 1) for combo in candidate_pool],
            payload.count,
        )
        for combo in chosen:
            combinations_list.append({
                "numbers": sorted(combo),
                "sum": sum(combo),
                "score": sum(composite_score(n) for n in combo),
            })

    return {
        "pool1": pool1,
        "pool1_eliminated": pool1_eliminated,
        "pool2": pool2,
        "pool2_eliminated": pool2_eliminated,
        "pool3": pool3,
        "pool3_eliminated": pool3_eliminated,
        "pool1_groups": {
            "hot_numbers": sorted(hot_numbers),
            "cold_numbers": sorted(cold_numbers),
            "supplement_numbers": sorted(
                n for n in pool1 if n not in hot_set and n not in cold_set
            ),
        },
        "combinations": combinations_list,
        "special_candidates": special_candidates,
        "special_pick": special_pick,
        "stats": {
            "pool1_size": len(pool1),
            "pool2_size": len(pool2),
            "pool3_size": len(pool3),
            "hot_count": len(hot_numbers),
            "cold_count": len(cold_numbers),
            "combinations_count": len(combinations_list),
            "draws_analyzed": len(recent_draws),
        },
    }


async def _qxc_position_layered_pick(payload: LayeredPickRequest, db: AsyncSession):
    if not (
        payload.qxc_pool1_size
        >= payload.qxc_pool2_size
        >= payload.qxc_pool3_size
        >= 1
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                "七星彩位置漏斗必须满足 "
                f"qxc_pool1_size({payload.qxc_pool1_size}) >= "
                f"qxc_pool2_size({payload.qxc_pool2_size}) >= "
                f"qxc_pool3_size({payload.qxc_pool3_size}) >= 1"
            ),
        )

    draws_result = await db.execute(
        select(Draw)
        .where(Draw.lottery_type == "qxc")
        .order_by(Draw.draw_date.desc())
        .limit(payload.history_periods)
    )
    recent_draws = list(draws_result.scalars().all())
    if not recent_draws:
        raise HTTPException(status_code=404, detail="七星彩历史开奖数据为空，无法做位置漏斗")

    freq_result = await db.execute(
        select(FrequencyCache).where(FrequencyCache.lottery_type == "qxc")
    )
    freq_cache = {f.number: f for f in freq_result.scalars().all()}

    trend_draws = recent_draws[: payload.trend_periods]
    digits = list(range(0, 10))
    excluded_digits = {
        n for n in payload.must_exclude if 0 <= n <= 9
    }
    must_digits = [
        n for n in dict.fromkeys(payload.must_include)
        if 0 <= n <= 9 and n not in excluded_digits
    ]

    position_values = [
        [d.num1, d.num2, d.num3, d.num4, d.num5, d.num6]
        for d in recent_draws
    ]
    trend_values = [
        [d.num1, d.num2, d.num3, d.num4, d.num5, d.num6]
        for d in trend_draws
    ]

    def freq_hot(number: int) -> float:
        found = freq_cache.get(number)
        return float(found.hotness_score) if found else 0.0

    def missed(number: int) -> int:
        found = freq_cache.get(number)
        return int(found.consecutive_missed) if found else 0

    def filter_digits(candidates: list[int]) -> list[int]:
        filtered = list(candidates)
        if payload.odd_even == "more_odd":
            filtered = [n for n in filtered if n % 2 == 1]
        elif payload.odd_even == "more_even":
            filtered = [n for n in filtered if n % 2 == 0]

        if payload.big_small == "more_big":
            filtered = [n for n in filtered if n >= 5]
        elif payload.big_small == "more_small":
            filtered = [n for n in filtered if n <= 4]

        return filtered

    position_pools = []
    position_scores: list[dict[int, float]] = []
    for pos in range(6):
        appearance = {n: 0 for n in digits}
        trend = {n: 0 for n in digits}
        for values in position_values:
            number = values[pos]
            if 0 <= number <= 9:
                appearance[number] += 1
        for values in trend_values:
            number = values[pos]
            if 0 <= number <= 9:
                trend[number] += 1

        def score(number: int) -> float:
            return (
                appearance[number] * 8
                + trend[number] * 5
                + freq_hot(number) * 0.02
                + min(missed(number), 12) * 0.3
            )

        allowed = [n for n in digits if n not in excluded_digits]
        if not allowed:
            allowed = digits[:]

        hot_count = min(payload.hot_count, payload.qxc_pool1_size, len(allowed))
        cold_count = min(
            payload.cold_count,
            max(0, payload.qxc_pool1_size - hot_count),
            max(0, len(allowed) - hot_count),
        )
        hot_numbers = sorted(allowed, key=lambda n: (-appearance[n], -trend[n], -score(n), n))[:hot_count]
        selected = set(hot_numbers)
        cold_numbers = []
        for number in sorted(allowed, key=lambda n: (appearance[n], trend[n], -missed(n), n)):
            if number not in selected:
                cold_numbers.append(number)
                selected.add(number)
            if len(cold_numbers) >= cold_count:
                break

        pool1_seed = list(dict.fromkeys(hot_numbers + cold_numbers))
        for number in sorted(allowed, key=lambda n: (-score(n), n)):
            if number not in pool1_seed:
                pool1_seed.append(number)
            if len(pool1_seed) >= payload.qxc_pool1_size:
                break
        pool1 = pool1_seed[: payload.qxc_pool1_size]

        pool2 = sorted(pool1, key=lambda n: (-score(n), n))[: payload.qxc_pool2_size]
        filtered_pool2 = filter_digits(pool2)
        if len(filtered_pool2) < payload.qxc_pool3_size:
            for number in pool2:
                if number not in filtered_pool2:
                    filtered_pool2.append(number)
                if len(filtered_pool2) >= payload.qxc_pool3_size:
                    break
        pool3 = filtered_pool2[: payload.qxc_pool3_size]

        position_pools.append(
            {
                "position": pos + 1,
                "pool1": pool1,
                "pool2": pool2,
                "pool3": pool3,
                "hot_numbers": hot_numbers,
                "cold_numbers": cold_numbers,
                "pool1_eliminated": [n for n in digits if n not in set(pool1)],
                "pool2_eliminated": [n for n in pool1 if n not in set(pool2)],
                "pool3_eliminated": [n for n in pool2 if n not in set(pool3)],
            }
        )
        position_scores.append({number: score(number) for number in digits})

    for index, number in enumerate(must_digits):
        target = position_pools[index % 6]["pool3"]
        if number not in target:
            if len(target) >= payload.qxc_pool3_size:
                target[-1] = number
            else:
                target.append(number)

    special_appearance = {n: 0 for n in range(0, 15)}
    special_trend = {n: 0 for n in range(0, 15)}
    for draw in recent_draws:
        if draw.special_num is not None and 0 <= draw.special_num <= 14:
            special_appearance[draw.special_num] += 1
    for draw in trend_draws:
        if draw.special_num is not None and 0 <= draw.special_num <= 14:
            special_trend[draw.special_num] += 1

    def special_score(number: int) -> float:
        found = freq_cache.get(number)
        special_freq = float(found.special_appearances) if found else 0.0
        return special_appearance[number] * 8 + special_trend[number] * 5 + special_freq * 2 + freq_hot(number) * 0.01

    back_pool1_size = min(8, max(3, payload.qxc_pool1_size + 2))
    back_pool2_size = min(back_pool1_size, max(3, payload.qxc_pool2_size + 1))
    back_pool3_size = min(back_pool2_size, max(2, payload.qxc_pool3_size))
    special_ranked = sorted(range(0, 15), key=lambda n: (-special_score(n), n))
    special_pool1 = special_ranked[:back_pool1_size]
    special_pool2 = special_pool1[:back_pool2_size]
    special_pool3 = special_pool2[:back_pool3_size]
    special_pick = (
        _weighted_sample_without_replacement(
            special_pool3,
            [max(special_score(number), 1) for number in special_pool3],
            1,
        )[0]
        if special_pool3
        else 0
    )

    combinations_list = []
    attempts = 0
    max_attempts = max(payload.count * 8, 20)
    while len(combinations_list) < payload.count and attempts < max_attempts:
        regular = []
        for pos, pool in enumerate(position_pools):
            candidates = pool["pool3"] or pool["pool2"] or pool["pool1"] or digits
            regular.append(
                _weighted_sample_without_replacement(
                    candidates,
                    [max(position_scores[pos].get(number, 0), 1) for number in candidates],
                    1,
                )[0]
            )

        if must_digits and not all(number in regular for number in must_digits):
            attempts += 1
            continue

        total_sum = sum(regular)
        if payload.sum_min is not None and total_sum < payload.sum_min:
            attempts += 1
            continue
        if payload.sum_max is not None and total_sum > payload.sum_max:
            attempts += 1
            continue

        special_candidates = special_pool3 or special_pool2 or special_pool1 or list(range(0, 15))
        special = _weighted_sample_without_replacement(
            special_candidates,
            [max(special_score(number), 1) for number in special_candidates],
            1,
        )[0]
        repeated_count = len(regular) - len(set(regular))
        span = max(regular) - min(regular) if regular else 0
        score_value = sum(position_scores[pos].get(number, 0) for pos, number in enumerate(regular))
        score_value += special_score(special)
        combinations_list.append(
            {
                "regular": regular,
                "numbers": regular,
                "special": special,
                "sum": total_sum,
                "score": round(score_value, 2),
                "repeated_count": repeated_count,
                "span": span,
            }
        )
        attempts += 1

    if not combinations_list:
        regular = [
            (pool["pool3"] or pool["pool2"] or pool["pool1"] or digits)[0]
            for pool in position_pools
        ]
        combinations_list.append(
            {
                "regular": regular,
                "numbers": regular,
                "special": (special_pool3 or special_pool2 or special_pool1 or [0])[0],
                "sum": sum(regular),
                "score": round(sum(position_scores[pos].get(number, 0) for pos, number in enumerate(regular)), 2),
                "repeated_count": len(regular) - len(set(regular)),
                "span": max(regular) - min(regular) if regular else 0,
            }
        )

    return {
        "mode": "qxc_position_layered",
        "position_pools": position_pools,
        "combinations": combinations_list,
        "special_candidates": special_pool3,
        "special_pick": special_pick,
        "back_zone": {
            "pool1": special_pool1,
            "pool2": special_pool2,
            "pool3": special_pool3,
            "pick": special_pick,
        },
        "stats": {
            "pool1_size": payload.qxc_pool1_size,
            "pool2_size": payload.qxc_pool2_size,
            "pool3_size": payload.qxc_pool3_size,
            "positions": 6,
            "combinations_count": len(combinations_list),
            "draws_analyzed": len(recent_draws),
        },
    }


def _apply_odd_even(pool, mode):
    if mode == "any" or len(pool) < 6:
        return pool
    odds = [n for n in pool if n % 2 == 1]
    evens = [n for n in pool if n % 2 == 0]
    if mode == "more_odd":
        # 保留所有奇数 + 一半偶数
        return sorted(odds + evens[: max(1, len(odds) // 2)])
    if mode == "more_even":
        return sorted(evens + odds[: max(1, len(evens) // 2)])
    if mode == "balanced":
        m = min(len(odds), len(evens))
        if m == 0:
            return pool
        return sorted(odds[:m] + evens[:m])
    return pool


def _apply_big_small(pool, mode, midpoint):
    if mode == "any" or len(pool) < 6:
        return pool
    bigs = [n for n in pool if n > midpoint]
    smalls = [n for n in pool if n <= midpoint]
    if mode == "more_big":
        return sorted(bigs + smalls[: max(1, len(bigs) // 2)])
    if mode == "more_small":
        return sorted(smalls + bigs[: max(1, len(smalls) // 2)])
    if mode == "balanced":
        m = min(len(bigs), len(smalls))
        if m == 0:
            return pool
        return sorted(bigs[:m] + smalls[:m])
    return pool


def _gen_qxc_regular(freqs, strategy, count):
    import random

    freq_by_number = {f.number: f for f in freqs}
    candidates = list(range(0, 10))

    def score(number):
        found = freq_by_number.get(number)
        return max(found.hotness_score, 1) if found else 1

    def missed(number):
        found = freq_by_number.get(number)
        return found.consecutive_missed if found else 0

    if strategy == "hot":
        pool = sorted(candidates, key=score, reverse=True)[:5]
        weights = [score(n) for n in pool]
    elif strategy == "cold":
        pool = sorted(candidates, key=score)[:5]
        weights = [max(score(pool[-1]) - score(n) + 1, 1) for n in pool]
    elif strategy == "overdue":
        pool = sorted(candidates, key=missed, reverse=True)[:5]
        weights = [max(missed(n), 1) for n in pool]
    elif strategy == "balanced":
        hot = sorted(candidates, key=score, reverse=True)[:3]
        cold = sorted(candidates, key=score)[:3]
        mid = [n for n in candidates if n not in set(hot + cold)]
        pool = hot + mid + cold
        weights = [max(score(n), 1) for n in pool]
    else:
        pool = candidates
        weights = [score(n) for n in pool]

    if not pool:
        pool = candidates
        weights = [1] * len(pool)

    return random.choices(pool, weights=weights, k=count)


def _gen_qxc_special(freqs):
    import random

    freq_by_number = {f.number: f for f in freqs}
    candidates = list(range(0, 15))
    weights = [
        max(
            (freq_by_number[n].special_appearances * 100 + freq_by_number[n].hotness_score)
            if n in freq_by_number
            else 1,
            1,
        )
        for n in candidates
    ]
    return random.choices(candidates, weights=weights, k=1)[0]
