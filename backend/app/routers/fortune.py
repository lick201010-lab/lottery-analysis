import json
import random
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.draw import (
    FortuneDailyResult,
    FortunePointEvent,
    FortunePoints,
    FortuneProfile,
)


router = APIRouter(prefix="/api/v1/fortune", tags=["fortune"])

LOCAL_TZ = timezone(timedelta(hours=8))
ALLOWED_LOTTERIES = {"marksix", "ssq", "qxc"}
ZODIACS = {"鼠", "牛", "虎", "兔", "龙", "蛇", "马", "羊", "猴", "鸡", "狗", "猪"}
CONSTELLATIONS = {
    "白羊",
    "金牛",
    "双子",
    "巨蟹",
    "狮子",
    "处女",
    "天秤",
    "天蝎",
    "射手",
    "摩羯",
    "水瓶",
    "双鱼",
}

OFFERINGS = {
    "incense": {
        "label": "上香",
        "cost": 5,
        "weights": [(1, 62), (2, 29), (3, 7), (4, 2)],
    },
    "peach": {
        "label": "桃子",
        "cost": 10,
        "weights": [(1, 55), (2, 32), (3, 10), (4, 3)],
    },
    "ingot": {
        "label": "元宝",
        "cost": 30,
        "weights": [(1, 40), (2, 38), (3, 16), (4, 6)],
    },
    "pouch": {
        "label": "锦囊",
        "cost": 60,
        "weights": [(1, 25), (2, 40), (3, 24), (4, 11)],
    },
}

DEFAULT_EFFECT_WEIGHTS = [(1, 70), (2, 24), (3, 5), (4, 1)]
EFFECT_NAMES = {
    1: "清风小吉",
    2: "金雨加持",
    3: "财神显灵",
    4: "天降鸿运",
}
AD_REWARD_POINTS = 10
AD_DAILY_LIMIT = 5

_rng = random.SystemRandom()


class FortuneProfileRequest(BaseModel):
    user_key: str = Field(min_length=8, max_length=80)
    zodiac: Optional[str] = None
    constellation: Optional[str] = None


class FortuneGenerateRequest(BaseModel):
    user_key: str = Field(min_length=8, max_length=80)
    lottery_type: str = "marksix"
    draw_date: Optional[str] = None
    zodiac: Optional[str] = None
    constellation: Optional[str] = None


class FortuneOfferingRequest(BaseModel):
    user_key: str = Field(min_length=8, max_length=80)
    offering_type: str


class FortuneAdRewardRequest(BaseModel):
    user_key: str = Field(min_length=8, max_length=80)


def _today():
    return datetime.now(LOCAL_TZ).date()


def _validate_lottery(lottery_type: str) -> str:
    value = (lottery_type or "").strip().lower()
    if value not in ALLOWED_LOTTERIES:
        raise HTTPException(status_code=400, detail="Unsupported lottery type")
    return value


def _validate_profile_values(zodiac: Optional[str], constellation: Optional[str]) -> None:
    if zodiac is not None and zodiac not in ZODIACS:
        raise HTTPException(status_code=400, detail="Invalid zodiac")
    if constellation is not None and constellation not in CONSTELLATIONS:
        raise HTTPException(status_code=400, detail="Invalid constellation")


def _draw_date_or_today(draw_date: Optional[str]) -> str:
    value = (draw_date or "").strip()
    if not value:
        return _today().isoformat()
    try:
        datetime.strptime(value[:10], "%Y-%m-%d")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid draw_date") from exc
    return value[:10]


def _weighted_effect(weights):
    total = sum(weight for _, weight in weights)
    roll = _rng.uniform(0, total)
    cursor = 0
    for level, weight in weights:
        cursor += weight
        if roll <= cursor:
            return {
                "level": level,
                "name": EFFECT_NAMES[level],
            }
    level = weights[-1][0]
    return {"level": level, "name": EFFECT_NAMES[level]}


def _generate_numbers_for_lottery(lottery_type: str):
    lottery_type = _validate_lottery(lottery_type)
    if lottery_type == "qxc":
        regular = [_rng.randint(0, 9) for _ in range(6)]
        special = _rng.randint(0, 14)
        return regular, special
    if lottery_type == "ssq":
        regular = sorted(_rng.sample(range(1, 34), 6))
        special = _rng.randint(1, 16)
        return regular, special

    drawn = _rng.sample(range(1, 50), 7)
    regular = sorted(drawn[:6])
    special = drawn[6]
    return regular, special


def _compose_fortune_text(
    lottery_type: str,
    zodiac: Optional[str],
    constellation: Optional[str],
    effect_name: str,
) -> str:
    lottery_label = {
        "marksix": "六合彩",
        "ssq": "双色球",
        "qxc": "七星彩",
    }.get(lottery_type, "数字")
    profile_bits = [bit for bit in [zodiac and f"属{zodiac}", constellation and f"{constellation}座"] if bit]
    profile_text = "、".join(profile_bits) if profile_bits else "今日"
    return (
        f"{profile_text}的手气签为「{effect_name}」。"
        f"本次{lottery_label}娱乐选号以均衡分布和随机扰动为主，适合轻松参考；"
        "开奖结果仍以官方公告为准。"
    )


def _profile_payload(profile: Optional[FortuneProfile]) -> Optional[dict[str, Any]]:
    if not profile:
        return None
    return {
        "user_key": profile.user_key,
        "zodiac": profile.zodiac,
        "constellation": profile.constellation,
    }


def _result_payload(result: Optional[FortuneDailyResult]) -> Optional[dict[str, Any]]:
    if not result:
        return None
    regular = [int(value) for value in result.regular_numbers.split(",") if value != ""]
    return {
        "id": result.id,
        "lottery_type": result.lottery_type,
        "draw_date": result.draw_date,
        "local_date": result.local_date.isoformat(),
        "zodiac": result.zodiac,
        "constellation": result.constellation,
        "fortune_text": result.fortune_text,
        "regular_numbers": regular,
        "special_number": result.special_number,
        "effect_level": result.effect_level,
        "effect_name": result.effect_name,
        "created_at": result.created_at.isoformat() if result.created_at else None,
    }


async def _get_profile(db: AsyncSession, user_key: str) -> Optional[FortuneProfile]:
    result = await db.execute(
        select(FortuneProfile).where(FortuneProfile.user_key == user_key)
    )
    return result.scalars().first()


async def _upsert_profile(
    db: AsyncSession,
    user_key: str,
    zodiac: Optional[str] = None,
    constellation: Optional[str] = None,
    *,
    commit: bool = True,
) -> FortuneProfile:
    _validate_profile_values(zodiac, constellation)
    profile = await _get_profile(db, user_key)
    if not profile:
        profile = FortuneProfile(user_key=user_key)
        db.add(profile)
    if zodiac is not None:
        profile.zodiac = zodiac
    if constellation is not None:
        profile.constellation = constellation
    if commit:
        await db.commit()
        await db.refresh(profile)
    else:
        await db.flush()
    return profile


async def _ensure_points(db: AsyncSession, user_key: str) -> FortunePoints:
    result = await db.execute(
        select(FortunePoints).where(FortunePoints.user_key == user_key)
    )
    points = result.scalars().first()
    if points:
        return points
    points = FortunePoints(user_key=user_key, balance=0)
    db.add(points)
    await db.flush()
    return points


async def _get_daily_result(
    db: AsyncSession,
    user_key: str,
    lottery_type: str,
    local_date,
) -> Optional[FortuneDailyResult]:
    result = await db.execute(
        select(FortuneDailyResult).where(
            FortuneDailyResult.user_key == user_key,
            FortuneDailyResult.lottery_type == lottery_type,
            FortuneDailyResult.local_date == local_date,
        )
    )
    return result.scalars().first()


async def _ad_rewards_used(db: AsyncSession, user_key: str, local_date) -> int:
    result = await db.execute(
        select(func.count(FortunePointEvent.id)).where(
            FortunePointEvent.user_key == user_key,
            FortunePointEvent.event_type == "ad_reward",
            FortunePointEvent.local_date == local_date,
        )
    )
    return result.scalar() or 0


@router.get("/today")
async def fortune_today(
    user_key: str = Query(..., min_length=8, max_length=80),
    lottery_type: str = Query("marksix"),
    draw_date: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    lottery_type = _validate_lottery(lottery_type)
    local_date = _today()
    _draw_date_or_today(draw_date)
    profile = await _get_profile(db, user_key)
    points = await _ensure_points(db, user_key)
    daily = await _get_daily_result(db, user_key, lottery_type, local_date)
    used = await _ad_rewards_used(db, user_key, local_date)
    await db.commit()
    await db.refresh(points)
    return {
        "profile": _profile_payload(profile),
        "result": _result_payload(daily),
        "points_balance": points.balance,
        "ad_reward_points": AD_REWARD_POINTS,
        "ad_rewards_remaining": max(AD_DAILY_LIMIT - used, 0),
        "local_date": local_date.isoformat(),
    }


@router.post("/profile")
async def fortune_profile(
    payload: FortuneProfileRequest,
    db: AsyncSession = Depends(get_db),
):
    profile = await _upsert_profile(
        db,
        payload.user_key,
        zodiac=payload.zodiac,
        constellation=payload.constellation,
    )
    return {"profile": _profile_payload(profile)}


@router.post("/generate")
async def fortune_generate(
    payload: FortuneGenerateRequest,
    db: AsyncSession = Depends(get_db),
):
    lottery_type = _validate_lottery(payload.lottery_type)
    draw_date = _draw_date_or_today(payload.draw_date)
    local_date = _today()
    profile = await _upsert_profile(
        db,
        payload.user_key,
        zodiac=payload.zodiac,
        constellation=payload.constellation,
        commit=False,
    )
    if not profile.zodiac or not profile.constellation:
        raise HTTPException(status_code=400, detail="Profile is incomplete")

    existing = await _get_daily_result(db, payload.user_key, lottery_type, local_date)
    if existing:
        await db.commit()
        return {
            "already_generated": True,
            "profile": _profile_payload(profile),
            "result": _result_payload(existing),
        }

    regular, special = _generate_numbers_for_lottery(lottery_type)
    effect = _weighted_effect(DEFAULT_EFFECT_WEIGHTS)
    result = FortuneDailyResult(
        user_key=payload.user_key,
        lottery_type=lottery_type,
        draw_date=draw_date,
        local_date=local_date,
        zodiac=profile.zodiac,
        constellation=profile.constellation,
        fortune_text=_compose_fortune_text(
            lottery_type,
            profile.zodiac,
            profile.constellation,
            effect["name"],
        ),
        regular_numbers=",".join(str(number) for number in regular),
        special_number=special,
        effect_level=effect["level"],
        effect_name=effect["name"],
    )
    db.add(result)
    await db.commit()
    await db.refresh(profile)
    await db.refresh(result)
    return {
        "already_generated": False,
        "profile": _profile_payload(profile),
        "result": _result_payload(result),
    }


@router.post("/offering")
async def fortune_offering(
    payload: FortuneOfferingRequest,
    db: AsyncSession = Depends(get_db),
):
    offering = OFFERINGS.get(payload.offering_type)
    if not offering:
        raise HTTPException(status_code=400, detail="Unsupported offering type")

    local_date = _today()
    points = await _ensure_points(db, payload.user_key)
    if points.balance < offering["cost"]:
        await db.commit()
        raise HTTPException(status_code=400, detail="Insufficient points")

    effect = _weighted_effect(offering["weights"])
    points.balance -= offering["cost"]
    db.add(
        FortunePointEvent(
            user_key=payload.user_key,
            event_type="offering",
            points_delta=-offering["cost"],
            metadata_json=json.dumps(
                {
                    "offering_type": payload.offering_type,
                    "offering_label": offering["label"],
                    "effect_level": effect["level"],
                    "effect_name": effect["name"],
                },
                ensure_ascii=False,
            ),
            local_date=local_date,
        )
    )
    await db.commit()
    await db.refresh(points)
    return {
        "points_balance": points.balance,
        "offering_label": offering["label"],
        "effect": effect,
    }


@router.post("/ad-reward")
async def fortune_ad_reward(
    payload: FortuneAdRewardRequest,
    db: AsyncSession = Depends(get_db),
):
    local_date = _today()
    used = await _ad_rewards_used(db, payload.user_key, local_date)
    if used >= AD_DAILY_LIMIT:
        raise HTTPException(status_code=400, detail="Daily ad reward limit reached")

    points = await _ensure_points(db, payload.user_key)
    points.balance += AD_REWARD_POINTS
    db.add(
        FortunePointEvent(
            user_key=payload.user_key,
            event_type="ad_reward",
            points_delta=AD_REWARD_POINTS,
            metadata_json=json.dumps({"source": "simulated_ad"}, ensure_ascii=False),
            local_date=local_date,
        )
    )
    await db.commit()
    await db.refresh(points)
    return {
        "points_balance": points.balance,
        "ad_reward_points": AD_REWARD_POINTS,
        "ad_rewards_remaining": max(AD_DAILY_LIMIT - used - 1, 0),
    }
