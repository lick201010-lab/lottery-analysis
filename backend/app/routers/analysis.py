from math import comb
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
    lottery_type: Literal["marksix", "ssq"] = "marksix"
    history_periods: int = Field(50, ge=10, le=500)
    hot_pct: int = Field(60, ge=20, le=100)
    trend_periods: int = Field(20, ge=5, le=100)
    consecutive: Literal["any", "include", "exclude"] = "any"
    odd_even: Literal["any", "more_odd", "more_even", "balanced"] = "any"
    big_small: Literal["any", "more_big", "more_small", "balanced"] = "any"
    sum_min: Optional[int] = None
    sum_max: Optional[int] = None
    must_include: List[int] = Field(default_factory=list)
    must_exclude: List[int] = Field(default_factory=list)
    complex_size: int = Field(8, ge=7, le=12)


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
    if number < 1 or number > config["max_regular"]:
        raise HTTPException(
            status_code=400,
            detail=f"Number must be between 1 and {config['max_regular']}",
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
    max_reg = config["max_regular"]

    odd_even_counts = {}
    big_small_counts = {}
    consecutive_counts = {}
    range_labels = []
    range_counts = {}
    sum_values = []

    # Dynamic ranges
    range_size = max(10, max_reg // 5)
    for start in range(1, max_reg + 1, range_size):
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
            idx = min((n - 1) // range_size, len(range_labels) - 1)
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


def _gen_hot(freqs, count, max_reg):
    hot = [f.number for f in freqs[:count * 2] if f.number <= max_reg]
    return list(dict.fromkeys(hot))[:count]


def _gen_cold(freqs, count, max_reg):
    cold = [f.number for f in reversed(freqs) if f.number <= max_reg]
    return list(dict.fromkeys(cold))[:count]


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
    import random
    valid = [(f.number, max(f.hotness_score, 1)) for f in freqs if f.number <= max_reg]
    nums = [v[0] for v in valid]
    weights = [v[1] for v in valid]
    result = []
    remaining = list(nums)
    remaining_weights = list(weights)
    for _ in range(count):
        if not remaining:
            break
        total_w = sum(remaining_weights)
        probs = [w / total_w for w in remaining_weights]
        pick = random.choices(remaining, weights=probs, k=1)[0]
        idx = remaining.index(pick)
        result.append(pick)
        remaining.pop(idx)
        remaining_weights.pop(idx)
    return result


def _gen_pair_chain(freqs, pair_index, count, max_reg):
    import random
    freq_nums = [f.number for f in freqs if f.number <= max_reg]

    if not freq_nums:
        return [1, 2, 3, 4, 5, 6][:count]

    current = freq_nums[0]
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
        best_next = None
        for (nb, co_oc) in pairs_sorted:
            if nb not in result and nb <= max_reg:
                best_next = nb
                break

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
    return [f.number for f in overdue[:count]]


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
    """分层筛选：四层逐步过滤号码池，最终输出复式。

    Layer 1（大底）：近 history_periods 期出现率前 hot_pct% 的号码
    Layer 2（走势）：近 trend_periods 期是否在连号场次中出现
    Layer 3（统计）：奇偶比、大小比偏好过滤
    Layer 4（个人）：胆码必含、杀号必排
    """
    config = LOTTERY_CONFIG.get(payload.lottery_type, LOTTERY_CONFIG["marksix"])
    max_reg = config["max_regular"]
    max_spe = config["max_special"]
    midpoint = max_reg // 2

    # 取近 N 期 draws（按 draw_date 倒序）
    result = await db.execute(
        select(Draw)
        .where(Draw.lottery_type == payload.lottery_type)
        .order_by(Draw.draw_date.desc())
        .limit(payload.history_periods)
    )
    recent_draws = list(result.scalars().all())

    if not recent_draws:
        raise HTTPException(status_code=404, detail="历史开奖数据为空，无法做分层筛选")

    # ===== Layer 1: 大底 — 历史冷热 =====
    appearance_count = {n: 0 for n in range(1, max_reg + 1)}
    for d in recent_draws:
        for n in (d.num1, d.num2, d.num3, d.num4, d.num5, d.num6):
            if 1 <= n <= max_reg:
                appearance_count[n] += 1

    sorted_by_hot = sorted(appearance_count.items(), key=lambda x: (-x[1], x[0]))
    keep_count = max(6, int(round(max_reg * payload.hot_pct / 100)))
    layer1_pool = sorted(n for n, _ in sorted_by_hot[:keep_count])

    # ===== Layer 2: 走势 — 近期连号特征 =====
    trend_draws = recent_draws[: payload.trend_periods]
    trend_appearance = {n: 0 for n in layer1_pool}
    appearance_in_consecutive = {n: 0 for n in layer1_pool}

    for d in trend_draws:
        nums = sorted([d.num1, d.num2, d.num3, d.num4, d.num5, d.num6])
        had_consecutive = any(nums[i + 1] - nums[i] == 1 for i in range(len(nums) - 1))
        for n in nums:
            if n in trend_appearance:
                trend_appearance[n] += 1
                if had_consecutive:
                    appearance_in_consecutive[n] += 1

    if payload.consecutive == "include":
        layer2_pool = sorted(n for n, c in appearance_in_consecutive.items() if c > 0)
    elif payload.consecutive == "exclude":
        layer2_pool = sorted(
            n for n in layer1_pool
            if trend_appearance.get(n, 0) > appearance_in_consecutive.get(n, 0)
            or trend_appearance.get(n, 0) == 0
        )
    else:
        layer2_pool = layer1_pool

    if len(layer2_pool) < 6:
        layer2_pool = layer1_pool

    # ===== Layer 3: 统计 — 奇偶/大小偏好 =====
    layer3_pool = list(layer2_pool)
    layer3_pool = _apply_odd_even(layer3_pool, payload.odd_even)
    layer3_pool = _apply_big_small(layer3_pool, payload.big_small, midpoint)

    if len(layer3_pool) < 6:
        layer3_pool = layer2_pool

    # ===== Layer 4: 个人 — 胆码必含 + 杀号必排 =====
    must_include = [n for n in payload.must_include if 1 <= n <= max_reg]
    must_exclude = set(n for n in payload.must_exclude if 1 <= n <= max_reg)
    must_include_set = set(must_include)

    layer4_pool = [n for n in layer3_pool if n not in must_exclude]
    for n in must_include:
        if n not in layer4_pool:
            layer4_pool.append(n)
    layer4_pool = sorted(set(layer4_pool))

    if len(layer4_pool) < payload.complex_size:
        # 不够复式数量，从全集补热度高的（且不在杀号里）
        all_extra = sorted(
            (n for n in range(1, max_reg + 1)
             if n not in layer4_pool and n not in must_exclude),
            key=lambda n: -appearance_count.get(n, 0),
        )
        layer4_pool = sorted(set(layer4_pool + all_extra[: payload.complex_size - len(layer4_pool)]))

    # ===== 最终复式：胆码优先 + 按热度补足 =====
    final_pool = list(must_include_set)
    remaining = [n for n in layer4_pool if n not in must_include_set]
    remaining.sort(key=lambda n: -appearance_count.get(n, 0))

    needed = payload.complex_size - len(final_pool)
    if needed > 0:
        final_pool.extend(remaining[:needed])

    final_pool = sorted(set(final_pool))[: payload.complex_size]

    # ===== 特别号候选（按近期出现频次） =====
    spe_count = {n: 0 for n in range(1, max_spe + 1)}
    for d in recent_draws:
        if d.special_num and 1 <= d.special_num <= max_spe:
            spe_count[d.special_num] += 1
    spe_sorted = sorted(spe_count.items(), key=lambda x: (-x[1], x[0]))
    special_candidates = [n for n, _ in spe_sorted[:5]]
    special_pick = special_candidates[0] if special_candidates else 1

    # ===== 组合统计 =====
    n_pool = len(final_pool)
    combos_total = comb(n_pool, 6) if n_pool >= 6 else 0

    # 和值范围统计（采样：列举所有 6 选组合算和值分布）
    combos_in_sum_range = combos_total
    if combos_total > 0 and (payload.sum_min is not None or payload.sum_max is not None):
        from itertools import combinations
        smin = payload.sum_min if payload.sum_min is not None else 0
        smax = payload.sum_max if payload.sum_max is not None else 999
        count_ok = 0
        for combo in combinations(final_pool, 6):
            s = sum(combo)
            if smin <= s <= smax:
                count_ok += 1
        combos_in_sum_range = count_ok

    return {
        "layer1_pool": layer1_pool,
        "layer2_pool": layer2_pool,
        "layer3_pool": layer3_pool,
        "layer4_pool": layer4_pool,
        "final_pool": final_pool,
        "special_candidates": special_candidates,
        "special_pick": special_pick,
        "complex_label": f"{n_pool}+1",
        "combos_total": combos_total,
        "combos_in_sum_range": combos_in_sum_range,
        "stats": {
            "layer1_kept": len(layer1_pool),
            "layer2_kept": len(layer2_pool),
            "layer3_kept": len(layer3_pool),
            "layer4_kept": len(layer4_pool),
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
