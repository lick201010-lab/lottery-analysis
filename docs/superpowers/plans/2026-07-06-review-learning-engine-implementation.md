# Review Learning Engine Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a dual-track review system that stores user and system generated picks, scores them after draws, and shows strategy review data in the Generate Numbers page.

**Architecture:** Add backend persistence models, a scoring/service layer, a review API router, and a small frontend review panel. Existing generation endpoints remain the source of numbers; the review feature records their output and reviews it after official draw data is available.

**Tech Stack:** FastAPI, SQLAlchemy async, SQLite, Vue 3, existing Vite/Vite-SSG frontend, unittest backend tests.

---

## File Structure

- Modify `backend/app/models/draw.py`: add `PredictionBatch`, `PredictionPick`, `PredictionReview`, and `StrategyPerformanceSnapshot`.
- Create `backend/app/services/review_learning.py`: scoring, save batch, run review, benchmark generation, snapshot aggregation.
- Create `backend/app/routers/review.py`: public review API endpoints.
- Modify `backend/app/main.py`: include review router.
- Modify `backend/app/routers/jackpot.py`: trigger review run after a successful latest draw sync.
- Create `backend/tests/test_review_learning.py`: unit tests for scoring, saving, idempotent benchmark creation, and review execution.
- Modify `frontend/src/api.js`: add review API helpers.
- Modify `frontend/src/views/GenerateNumbers.vue`: save generated picks and render review learning section.

## Task 1: Backend Models

**Files:**
- Modify: `backend/app/models/draw.py`
- Test: `backend/tests/test_review_learning.py`

- [ ] **Step 1: Add model imports**

In `backend/app/models/draw.py`, update the import line:

```python
from sqlalchemy import Column, Integer, String, Date, Boolean, DateTime, func, UniqueConstraint, ForeignKey, Float
```

- [ ] **Step 2: Add prediction models**

Append these classes after `FortunePointEvent` in `backend/app/models/draw.py`:

```python
class PredictionBatch(Base):
    __tablename__ = "prediction_batch"
    __table_args__ = (
        UniqueConstraint(
            "lottery_type",
            "source_type",
            "strategy",
            "strategy_version",
            "target_draw_date",
            "generator_mode",
            name="uq_prediction_system_batch",
        ),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    batch_key = Column(String(80), nullable=False, unique=True, index=True)
    lottery_type = Column(String(20), nullable=False, index=True)
    source_type = Column(String(20), nullable=False, index=True)
    user_key = Column(String(80), index=True)
    generator_mode = Column(String(40), nullable=False, index=True)
    strategy = Column(String(40), nullable=False, index=True)
    strategy_version = Column(String(20), nullable=False, default="v1")
    params_json = Column(String(2000), nullable=False, default="{}")
    target_draw_date = Column(Date, nullable=False, index=True)
    target_draw_number = Column(String(20), index=True)
    context_json = Column(String(2000), nullable=False, default="{}")
    reviewed_at = Column(DateTime)
    status = Column(String(20), nullable=False, default="pending", index=True)
    created_at = Column(DateTime, server_default=func.now())


class PredictionPick(Base):
    __tablename__ = "prediction_pick"

    id = Column(Integer, primary_key=True, autoincrement=True)
    batch_id = Column(Integer, ForeignKey("prediction_batch.id"), nullable=False, index=True)
    pick_index = Column(Integer, nullable=False, default=0)
    regular_numbers_json = Column(String(300), nullable=False)
    special_number = Column(Integer, nullable=False)
    display_json = Column(String(1000), nullable=False, default="{}")
    created_at = Column(DateTime, server_default=func.now())


class PredictionReview(Base):
    __tablename__ = "prediction_review"
    __table_args__ = (
        UniqueConstraint("pick_id", "draw_id", name="uq_prediction_review_pick_draw"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    pick_id = Column(Integer, ForeignKey("prediction_pick.id"), nullable=False, index=True)
    draw_id = Column(Integer, ForeignKey("draws.id"), nullable=False, index=True)
    lottery_type = Column(String(20), nullable=False, index=True)
    score = Column(Float, nullable=False, default=0)
    primary_hits = Column(Integer, nullable=False, default=0)
    special_hit = Column(Boolean, nullable=False, default=False)
    exact_hit = Column(Boolean, nullable=False, default=False)
    detail_json = Column(String(2000), nullable=False, default="{}")
    created_at = Column(DateTime, server_default=func.now())


class StrategyPerformanceSnapshot(Base):
    __tablename__ = "strategy_performance_snapshot"
    __table_args__ = (
        UniqueConstraint(
            "lottery_type",
            "source_type",
            "strategy",
            "window_size",
            name="uq_strategy_performance_window",
        ),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    lottery_type = Column(String(20), nullable=False, index=True)
    source_type = Column(String(20), nullable=False, index=True)
    strategy = Column(String(40), nullable=False, index=True)
    window_size = Column(String(20), nullable=False, default="24")
    sample_count = Column(Integer, nullable=False, default=0)
    avg_score = Column(Float, nullable=False, default=0)
    avg_primary_hits = Column(Float, nullable=False, default=0)
    high_hit_count = Column(Integer, nullable=False, default=0)
    exact_hit_count = Column(Integer, nullable=False, default=0)
    special_hit_rate = Column(Float, nullable=False, default=0)
    recommended_weight = Column(Float, nullable=False, default=1)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
```

- [ ] **Step 3: Verify models compile**

Run:

```powershell
cd D:\lottery-retro-engine\backend
python -m compileall app
```

Expected: compile listing with no syntax errors.

- [ ] **Step 4: Commit**

```powershell
cd D:\lottery-retro-engine
git add backend/app/models/draw.py
git commit -m "[Agent] feat: add prediction review models"
```

## Task 2: Review Scoring Service

**Files:**
- Create: `backend/app/services/review_learning.py`
- Test: `backend/tests/test_review_learning.py`

- [ ] **Step 1: Create failing scoring tests**

Create `backend/tests/test_review_learning.py` with:

```python
import unittest
from datetime import date

from app.models.draw import Draw
from app.services.review_learning import score_pick_for_draw


class ReviewLearningScoringTest(unittest.TestCase):
    def test_marksix_scores_main_numbers_separately_from_special(self):
        draw = Draw(
            id=1,
            lottery_type="marksix",
            draw_date=date(2026, 7, 1),
            draw_number="26/060",
            num1=1,
            num2=2,
            num3=3,
            num4=4,
            num5=5,
            num6=6,
            special_num=49,
        )
        score = score_pick_for_draw("marksix", [1, 2, 3, 4, 5, 6], 7, draw)
        self.assertEqual(score["primary_hits"], 6)
        self.assertFalse(score["special_hit"])
        self.assertTrue(score["exact_hit"])
        self.assertEqual(score["score"], 60)

    def test_ssq_requires_blue_for_exact_hit(self):
        draw = Draw(
            id=2,
            lottery_type="ssq",
            draw_date=date(2026, 7, 2),
            draw_number="26060",
            num1=1,
            num2=2,
            num3=3,
            num4=4,
            num5=5,
            num6=6,
            special_num=16,
        )
        score = score_pick_for_draw("ssq", [1, 2, 3, 4, 5, 6], 15, draw)
        self.assertEqual(score["primary_hits"], 6)
        self.assertFalse(score["special_hit"])
        self.assertFalse(score["exact_hit"])
        self.assertEqual(score["score"], 60)

    def test_qxc_preserves_position_and_zero(self):
        draw = Draw(
            id=3,
            lottery_type="qxc",
            draw_date=date(2026, 7, 3),
            draw_number="26070",
            num1=0,
            num2=9,
            num3=1,
            num4=1,
            num5=6,
            num6=2,
            special_num=14,
        )
        score = score_pick_for_draw("qxc", [0, 1, 9, 1, 6, 2], 14, draw)
        self.assertEqual(score["primary_hits"], 4)
        self.assertTrue(score["special_hit"])
        self.assertFalse(score["exact_hit"])
        self.assertEqual(score["detail"]["position_hits"], [True, False, False, True, True, True])
```

- [ ] **Step 2: Run tests to verify failure**

Run:

```powershell
cd D:\lottery-retro-engine\backend
python -m unittest backend.tests.test_review_learning -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'app.services.review_learning'`.

- [ ] **Step 3: Implement scoring service**

Create `backend/app/services/review_learning.py`:

```python
from __future__ import annotations

import json
import uuid
from datetime import date
from typing import Any

from sqlalchemy import and_, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.draw import (
    Draw,
    FrequencyCache,
    PairFrequency,
    PredictionBatch,
    PredictionPick,
    PredictionReview,
    StrategyPerformanceSnapshot,
)
from app.routers.analysis import (
    LOTTERY_CONFIG,
    _gen_balanced,
    _gen_cold,
    _gen_hot,
    _gen_overdue,
    _gen_pair_chain,
    _gen_qxc_regular,
    _gen_qxc_special,
    _gen_special,
    _gen_weighted_random,
    layered_pick,
    LayeredPickRequest,
)

SYSTEM_STRATEGIES = ["hot", "weighted_random", "overdue", "balanced", "pair_chain"]
STRATEGY_VERSION = "v1"


def _draw_regular_numbers(draw: Draw) -> list[int]:
    return [draw.num1, draw.num2, draw.num3, draw.num4, draw.num5, draw.num6]


def score_pick_for_draw(
    lottery_type: str,
    regular_numbers: list[int],
    special_number: int,
    draw: Draw,
) -> dict[str, Any]:
    draw_regulars = _draw_regular_numbers(draw)
    if lottery_type == "qxc":
        position_hits = [
            idx < len(regular_numbers) and regular_numbers[idx] == draw_regulars[idx]
            for idx in range(6)
        ]
        primary_hits = sum(1 for hit in position_hits if hit)
        special_hit = special_number == draw.special_num
        exact_hit = primary_hits == 6 and special_hit
        digit_pool_hits = len(set(regular_numbers).intersection(draw_regulars))
        return {
            "score": primary_hits * 10 + (8 if special_hit else 0) + (30 if exact_hit else 0),
            "primary_hits": primary_hits,
            "special_hit": special_hit,
            "exact_hit": exact_hit,
            "detail": {
                "position_hits": position_hits,
                "digit_pool_hits": digit_pool_hits,
                "draw_regular": draw_regulars,
                "draw_special": draw.special_num,
            },
        }

    primary_hits = len(set(regular_numbers).intersection(draw_regulars))
    special_hit = special_number == draw.special_num
    if lottery_type == "ssq":
        exact_hit = primary_hits == 6 and special_hit
        score = primary_hits * 10 + (5 if special_hit else 0) + (20 if exact_hit else 0)
    else:
        exact_hit = primary_hits == 6
        score = primary_hits * 10 + (3 if special_hit else 0)
    return {
        "score": score,
        "primary_hits": primary_hits,
        "special_hit": special_hit,
        "exact_hit": exact_hit,
        "detail": {
            "draw_regular": draw_regulars,
            "draw_special": draw.special_num,
        },
    }
```

- [ ] **Step 4: Run tests to verify scoring passes**

Run:

```powershell
cd D:\lottery-retro-engine\backend
python -m unittest backend.tests.test_review_learning -v
```

Expected: 3 tests pass.

- [ ] **Step 5: Commit**

```powershell
cd D:\lottery-retro-engine
git add backend/app/services/review_learning.py backend/tests/test_review_learning.py
git commit -m "[Agent] feat: add lottery-specific review scoring"
```

## Task 3: Save Prediction Batches

**Files:**
- Modify: `backend/app/services/review_learning.py`
- Modify: `backend/tests/test_review_learning.py`

- [ ] **Step 1: Add save-batch test**

Append to `ReviewLearningScoringTest` or create `ReviewLearningPersistenceTest` in `backend/tests/test_review_learning.py`:

```python
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from app.models.draw import Base, PredictionBatch, PredictionPick
from app.services.review_learning import save_prediction_batch


class ReviewLearningPersistenceTest(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.engine = create_async_engine("sqlite+aiosqlite:///:memory:")
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        self.Session = async_sessionmaker(self.engine, expire_on_commit=False)

    async def asyncTearDown(self):
        await self.engine.dispose()

    async def test_save_user_prediction_batch(self):
        async with self.Session() as session:
            result = await save_prediction_batch(
                db=session,
                lottery_type="ssq",
                source_type="user",
                user_key="review-user-1",
                generator_mode="simple",
                strategy="hot",
                params={"count": 1},
                target_draw_date=date(2026, 7, 7),
                sets=[{"regular": [1, 2, 3, 4, 5, 6], "special": 16}],
            )
            self.assertEqual(result["saved_count"], 1)
            batch_rows = (await session.execute(select(PredictionBatch))).scalars().all()
            pick_rows = (await session.execute(select(PredictionPick))).scalars().all()
            self.assertEqual(len(batch_rows), 1)
            self.assertEqual(batch_rows[0].source_type, "user")
            self.assertEqual(len(pick_rows), 1)
            self.assertEqual(json.loads(pick_rows[0].regular_numbers_json), [1, 2, 3, 4, 5, 6])
```

- [ ] **Step 2: Run test to verify failure**

Run:

```powershell
cd D:\lottery-retro-engine\backend
python -m unittest backend.tests.test_review_learning.ReviewLearningPersistenceTest.test_save_user_prediction_batch -v
```

Expected: FAIL with `ImportError` or `AttributeError` for `save_prediction_batch`.

- [ ] **Step 3: Implement validation and save**

Append to `backend/app/services/review_learning.py`:

```python
def _validate_pick_shape(lottery_type: str, regular: list[int], special: int) -> None:
    config = LOTTERY_CONFIG.get(lottery_type)
    if not config:
        raise ValueError("Unsupported lottery type")
    if len(regular) != config["regular_count"]:
        raise ValueError("Invalid regular number count")
    min_regular = config.get("min_regular", 1)
    if any(number < min_regular or number > config["max_regular"] for number in regular):
        raise ValueError("Regular number out of range")
    if special < config.get("min_special", 1) or special > config["max_special"]:
        raise ValueError("Special number out of range")
    if not config.get("allow_duplicates") and len(set(regular)) != len(regular):
        raise ValueError("Duplicate regular numbers are not allowed")


async def save_prediction_batch(
    db: AsyncSession,
    lottery_type: str,
    source_type: str,
    user_key: str | None,
    generator_mode: str,
    strategy: str,
    params: dict[str, Any],
    target_draw_date: date,
    sets: list[dict[str, Any]],
    target_draw_number: str | None = None,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if source_type not in {"user", "system"}:
        raise ValueError("Invalid source type")
    if source_type == "user" and not user_key:
        raise ValueError("user_key is required for user batches")
    if not sets:
        raise ValueError("sets cannot be empty")

    for item in sets:
        _validate_pick_shape(lottery_type, list(item["regular"]), int(item["special"]))

    batch = PredictionBatch(
        batch_key=f"pred-{uuid.uuid4()}",
        lottery_type=lottery_type,
        source_type=source_type,
        user_key=user_key,
        generator_mode=generator_mode,
        strategy=strategy,
        strategy_version=STRATEGY_VERSION,
        params_json=json.dumps(params, ensure_ascii=False),
        target_draw_date=target_draw_date,
        target_draw_number=target_draw_number,
        context_json=json.dumps(context or {}, ensure_ascii=False),
        status="pending",
    )
    db.add(batch)
    await db.flush()

    for index, item in enumerate(sets):
        db.add(
            PredictionPick(
                batch_id=batch.id,
                pick_index=index,
                regular_numbers_json=json.dumps(list(item["regular"]), ensure_ascii=False),
                special_number=int(item["special"]),
                display_json=json.dumps(item.get("display", {}), ensure_ascii=False),
            )
        )
    await db.commit()
    return {
        "batch_key": batch.batch_key,
        "target_draw_date": target_draw_date.isoformat(),
        "target_draw_number": target_draw_number,
        "saved_count": len(sets),
    }
```

- [ ] **Step 4: Run persistence test**

Run:

```powershell
cd D:\lottery-retro-engine\backend
python -m unittest backend.tests.test_review_learning.ReviewLearningPersistenceTest.test_save_user_prediction_batch -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```powershell
cd D:\lottery-retro-engine
git add backend/app/services/review_learning.py backend/tests/test_review_learning.py
git commit -m "[Agent] feat: save prediction batches"
```

## Task 4: Review Execution and Snapshots

**Files:**
- Modify: `backend/app/services/review_learning.py`
- Modify: `backend/tests/test_review_learning.py`

- [ ] **Step 1: Add review execution test**

Append to `ReviewLearningPersistenceTest`:

```python
from app.models.draw import PredictionReview, StrategyPerformanceSnapshot
from app.services.review_learning import run_review_for_draw

    async def test_run_review_scores_pending_batch_and_updates_snapshot(self):
        async with self.Session() as session:
            draw = Draw(
                lottery_type="ssq",
                draw_date=date(2026, 7, 7),
                draw_number="26061",
                num1=1,
                num2=2,
                num3=3,
                num4=4,
                num5=5,
                num6=6,
                special_num=16,
            )
            session.add(draw)
            await session.commit()
            await session.refresh(draw)
            await save_prediction_batch(
                db=session,
                lottery_type="ssq",
                source_type="system",
                user_key=None,
                generator_mode="system_benchmark",
                strategy="hot",
                params={"count": 1},
                target_draw_date=date(2026, 7, 7),
                sets=[{"regular": [1, 2, 3, 7, 8, 9], "special": 16}],
            )

            result = await run_review_for_draw(session, draw)
            reviews = (await session.execute(select(PredictionReview))).scalars().all()
            snapshots = (await session.execute(select(StrategyPerformanceSnapshot))).scalars().all()
            self.assertEqual(result["reviewed_pick_count"], 1)
            self.assertEqual(len(reviews), 1)
            self.assertEqual(reviews[0].primary_hits, 3)
            self.assertTrue(reviews[0].special_hit)
            self.assertEqual(len(snapshots), 1)
            self.assertEqual(snapshots[0].strategy, "hot")
```

- [ ] **Step 2: Run test to verify failure**

Run:

```powershell
cd D:\lottery-retro-engine\backend
python -m unittest backend.tests.test_review_learning.ReviewLearningPersistenceTest.test_run_review_scores_pending_batch_and_updates_snapshot -v
```

Expected: FAIL because `run_review_for_draw` is missing.

- [ ] **Step 3: Implement review execution**

Append to `backend/app/services/review_learning.py`:

```python
async def run_review_for_draw(db: AsyncSession, draw: Draw) -> dict[str, int]:
    batch_result = await db.execute(
        select(PredictionBatch).where(
            PredictionBatch.lottery_type == draw.lottery_type,
            PredictionBatch.status == "pending",
            PredictionBatch.target_draw_date <= draw.draw_date,
        )
    )
    batches = batch_result.scalars().all()
    reviewed_pick_count = 0
    reviewed_batch_count = 0

    for batch in batches:
        pick_result = await db.execute(
            select(PredictionPick).where(PredictionPick.batch_id == batch.id)
        )
        picks = pick_result.scalars().all()
        for pick in picks:
            existing = await db.execute(
                select(PredictionReview).where(
                    PredictionReview.pick_id == pick.id,
                    PredictionReview.draw_id == draw.id,
                )
            )
            if existing.scalars().first():
                continue
            regular = json.loads(pick.regular_numbers_json)
            score = score_pick_for_draw(batch.lottery_type, regular, pick.special_number, draw)
            db.add(
                PredictionReview(
                    pick_id=pick.id,
                    draw_id=draw.id,
                    lottery_type=batch.lottery_type,
                    score=score["score"],
                    primary_hits=score["primary_hits"],
                    special_hit=score["special_hit"],
                    exact_hit=score["exact_hit"],
                    detail_json=json.dumps(score["detail"], ensure_ascii=False),
                )
            )
            reviewed_pick_count += 1
        batch.status = "reviewed"
        batch.target_draw_number = draw.draw_number
        batch.reviewed_at = func.now()
        reviewed_batch_count += 1

    await db.flush()
    await recompute_strategy_snapshots(db, draw.lottery_type)
    await db.commit()
    return {
        "reviewed_batch_count": reviewed_batch_count,
        "reviewed_pick_count": reviewed_pick_count,
    }


async def recompute_strategy_snapshots(db: AsyncSession, lottery_type: str) -> int:
    updated = 0
    for source_type in ["user", "system", "all"]:
        for window_size in ["10", "24", "50", "all"]:
            source_filter = []
            if source_type != "all":
                source_filter.append(PredictionBatch.source_type == source_type)
            review_rows = await db.execute(
                select(
                    PredictionBatch.strategy,
                    PredictionReview.score,
                    PredictionReview.primary_hits,
                    PredictionReview.special_hit,
                    PredictionReview.exact_hit,
                )
                .join(PredictionPick, PredictionPick.batch_id == PredictionBatch.id)
                .join(PredictionReview, PredictionReview.pick_id == PredictionPick.id)
                .where(PredictionBatch.lottery_type == lottery_type, *source_filter)
                .order_by(desc(PredictionReview.created_at))
                .limit(None if window_size == "all" else int(window_size) * 60)
            )
            rows = review_rows.all()
            grouped: dict[str, list[Any]] = {}
            for row in rows:
                grouped.setdefault(row.strategy, []).append(row)
            for strategy, items in grouped.items():
                sample_count = len(items)
                avg_score = sum(item.score for item in items) / sample_count
                avg_primary_hits = sum(item.primary_hits for item in items) / sample_count
                special_hit_rate = sum(1 for item in items if item.special_hit) / sample_count
                high_hit_count = sum(1 for item in items if item.primary_hits >= 4)
                exact_hit_count = sum(1 for item in items if item.exact_hit)
                recommended_weight = max(0.2, min(3.0, 1.0 + (avg_score / 60.0)))
                existing = await db.execute(
                    select(StrategyPerformanceSnapshot).where(
                        StrategyPerformanceSnapshot.lottery_type == lottery_type,
                        StrategyPerformanceSnapshot.source_type == source_type,
                        StrategyPerformanceSnapshot.strategy == strategy,
                        StrategyPerformanceSnapshot.window_size == window_size,
                    )
                )
                snapshot = existing.scalars().first()
                if not snapshot:
                    snapshot = StrategyPerformanceSnapshot(
                        lottery_type=lottery_type,
                        source_type=source_type,
                        strategy=strategy,
                        window_size=window_size,
                    )
                    db.add(snapshot)
                snapshot.sample_count = sample_count
                snapshot.avg_score = avg_score
                snapshot.avg_primary_hits = avg_primary_hits
                snapshot.high_hit_count = high_hit_count
                snapshot.exact_hit_count = exact_hit_count
                snapshot.special_hit_rate = special_hit_rate
                snapshot.recommended_weight = recommended_weight
                updated += 1
    return updated
```

- [ ] **Step 4: Run review execution test**

Run:

```powershell
cd D:\lottery-retro-engine\backend
python -m unittest backend.tests.test_review_learning.ReviewLearningPersistenceTest.test_run_review_scores_pending_batch_and_updates_snapshot -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```powershell
cd D:\lottery-retro-engine
git add backend/app/services/review_learning.py backend/tests/test_review_learning.py
git commit -m "[Agent] feat: review pending predictions"
```

## Task 5: Review API Router

**Files:**
- Create: `backend/app/routers/review.py`
- Modify: `backend/app/main.py`
- Test: `backend/tests/test_review_learning.py`

- [ ] **Step 1: Create review router**

Create `backend/app/routers/review.py`:

```python
from __future__ import annotations

from datetime import date
from typing import Any, Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.draw import Draw, PredictionBatch, PredictionPick, PredictionReview, StrategyPerformanceSnapshot
from app.services.review_learning import save_prediction_batch, run_review_for_draw

router = APIRouter(prefix="/api/v1/review", tags=["review"])


class PredictionSetIn(BaseModel):
    regular: list[int]
    special: int
    display: dict[str, Any] = Field(default_factory=dict)


class PredictionBatchIn(BaseModel):
    lottery_type: str
    source_type: Literal["user"] = "user"
    user_key: str = Field(min_length=8, max_length=80)
    generator_mode: str
    strategy: str
    params: dict[str, Any] = Field(default_factory=dict)
    target_draw_date: date
    target_draw_number: str | None = None
    sets: list[PredictionSetIn]


class ReviewRunIn(BaseModel):
    lottery_type: str | None = None
    draw_id: int | None = None
    target_draw_date: date | None = None


@router.post("/predictions")
async def create_prediction_batch(payload: PredictionBatchIn, db: AsyncSession = Depends(get_db)):
    try:
        return await save_prediction_batch(
            db=db,
            lottery_type=payload.lottery_type,
            source_type=payload.source_type,
            user_key=payload.user_key,
            generator_mode=payload.generator_mode,
            strategy=payload.strategy,
            params=payload.params,
            target_draw_date=payload.target_draw_date,
            target_draw_number=payload.target_draw_number,
            sets=[item.model_dump() for item in payload.sets],
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/me")
async def my_review_history(
    user_key: str = Query(..., min_length=8, max_length=80),
    lottery_type: str = Query("ssq"),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    rows = await db.execute(
        select(PredictionBatch)
        .where(PredictionBatch.user_key == user_key, PredictionBatch.lottery_type == lottery_type)
        .order_by(desc(PredictionBatch.created_at))
        .limit(limit)
    )
    batches = rows.scalars().all()
    result = []
    for batch in batches:
        picks = (
            await db.execute(select(PredictionPick).where(PredictionPick.batch_id == batch.id))
        ).scalars().all()
        result.append(
            {
                "batch_key": batch.batch_key,
                "strategy": batch.strategy,
                "generator_mode": batch.generator_mode,
                "target_draw_date": batch.target_draw_date.isoformat(),
                "target_draw_number": batch.target_draw_number,
                "status": batch.status,
                "picks": [
                    {
                        "regular": __import__("json").loads(pick.regular_numbers_json),
                        "special": pick.special_number,
                    }
                    for pick in picks
                ],
            }
        )
    return {"batches": result}


@router.get("/strategies")
async def strategy_performance(
    lottery_type: str = Query("ssq"),
    source_type: str = Query("system"),
    window: str = Query("24"),
    db: AsyncSession = Depends(get_db),
):
    rows = await db.execute(
        select(StrategyPerformanceSnapshot)
        .where(
            StrategyPerformanceSnapshot.lottery_type == lottery_type,
            StrategyPerformanceSnapshot.source_type == source_type,
            StrategyPerformanceSnapshot.window_size == window,
        )
        .order_by(desc(StrategyPerformanceSnapshot.avg_score))
    )
    return {
        "strategies": [
            {
                "strategy": row.strategy,
                "sample_count": row.sample_count,
                "avg_score": row.avg_score,
                "avg_primary_hits": row.avg_primary_hits,
                "high_hit_count": row.high_hit_count,
                "exact_hit_count": row.exact_hit_count,
                "special_hit_rate": row.special_hit_rate,
                "recommended_weight": row.recommended_weight,
            }
            for row in rows.scalars().all()
        ]
    }


@router.post("/run")
async def run_review(payload: ReviewRunIn, db: AsyncSession = Depends(get_db)):
    query = select(Draw).order_by(desc(Draw.draw_date))
    if payload.draw_id:
        query = select(Draw).where(Draw.id == payload.draw_id)
    elif payload.lottery_type and payload.target_draw_date:
        query = select(Draw).where(
            Draw.lottery_type == payload.lottery_type,
            Draw.draw_date == payload.target_draw_date,
        )
    elif payload.lottery_type:
        query = query.where(Draw.lottery_type == payload.lottery_type)
    draw = (await db.execute(query.limit(1))).scalars().first()
    if not draw:
        raise HTTPException(status_code=404, detail="Draw not found")
    return await run_review_for_draw(db, draw)
```

- [ ] **Step 2: Register router**

Modify `backend/app/main.py`:

```python
from app.routers import analysis, draws, fortune, jackpot, newsletter, review, scrape
```

Add after `app.include_router(newsletter.router)`:

```python
app.include_router(review.router)
```

- [ ] **Step 3: Run compile**

Run:

```powershell
cd D:\lottery-retro-engine\backend
python -m compileall app
```

Expected: no syntax errors.

- [ ] **Step 4: Commit**

```powershell
cd D:\lottery-retro-engine
git add backend/app/routers/review.py backend/app/main.py
git commit -m "[Agent] feat: add review learning API"
```

## Task 6: System Benchmark Creation

**Files:**
- Modify: `backend/app/services/review_learning.py`
- Modify: `backend/app/routers/review.py`
- Test: `backend/tests/test_review_learning.py`

- [ ] **Step 1: Add idempotent benchmark test**

Append to `ReviewLearningPersistenceTest`:

```python
from app.services.review_learning import create_system_benchmarks

    async def test_system_benchmarks_are_idempotent(self):
        async with self.Session() as session:
            first = await create_system_benchmarks(session, "ssq", date(2026, 7, 9))
            second = await create_system_benchmarks(session, "ssq", date(2026, 7, 9))
            batches = (await session.execute(select(PredictionBatch))).scalars().all()
            self.assertGreater(first["created_batches"], 0)
            self.assertEqual(second["created_batches"], 0)
            self.assertEqual(len(batches), first["created_batches"])
```

- [ ] **Step 2: Implement benchmark generation**

Append to `backend/app/services/review_learning.py`:

```python
async def _load_generation_inputs(db: AsyncSession, lottery_type: str):
    freq_result = await db.execute(
        select(FrequencyCache)
        .where(FrequencyCache.lottery_type == lottery_type)
        .order_by(FrequencyCache.hotness_score.desc())
    )
    freqs = freq_result.scalars().all()
    pair_result = await db.execute(select(PairFrequency).where(PairFrequency.lottery_type == lottery_type))
    pair_index: dict[int, list[tuple[int, int]]] = {}
    for pair in pair_result.scalars().all():
        pair_index.setdefault(pair.num_a, []).append((pair.num_b, pair.co_occurrences))
        pair_index.setdefault(pair.num_b, []).append((pair.num_a, pair.co_occurrences))
    return freqs, pair_index


def _generate_system_sets(lottery_type: str, strategy: str, freqs, pair_index, count: int = 10):
    config = LOTTERY_CONFIG[lottery_type]
    sets = []
    for _ in range(count):
        if lottery_type == "qxc":
            regular = _gen_qxc_regular(freqs, strategy, config["regular_count"])
            special = _gen_qxc_special(freqs)
        elif strategy == "hot":
            regular = sorted(_gen_hot(freqs, config["regular_count"], config["max_regular"]))
            special = _gen_special(freqs, config["max_special"])
        elif strategy == "weighted_random":
            regular = sorted(_gen_weighted_random(freqs, config["regular_count"], config["max_regular"]))
            special = _gen_special(freqs, config["max_special"])
        elif strategy == "overdue":
            regular = sorted(_gen_overdue(freqs, config["regular_count"], config["max_regular"]))
            special = _gen_special(freqs, config["max_special"])
        elif strategy == "pair_chain":
            regular = sorted(_gen_pair_chain(freqs, pair_index, config["regular_count"], config["max_regular"]))
            special = _gen_special(freqs, config["max_special"])
        else:
            regular = sorted(_gen_balanced(freqs, config["regular_count"], config["max_regular"]))
            special = _gen_special(freqs, config["max_special"])
        sets.append({"regular": regular, "special": special})
    return sets


async def create_system_benchmarks(
    db: AsyncSession,
    lottery_type: str,
    target_draw_date: date,
) -> dict[str, int]:
    freqs, pair_index = await _load_generation_inputs(db, lottery_type)
    created_batches = 0
    for strategy in SYSTEM_STRATEGIES:
        existing = await db.execute(
            select(PredictionBatch).where(
                PredictionBatch.lottery_type == lottery_type,
                PredictionBatch.source_type == "system",
                PredictionBatch.strategy == strategy,
                PredictionBatch.strategy_version == STRATEGY_VERSION,
                PredictionBatch.target_draw_date == target_draw_date,
                PredictionBatch.generator_mode == "system_benchmark",
            )
        )
        if existing.scalars().first():
            continue
        sets = _generate_system_sets(lottery_type, strategy, freqs, pair_index, count=10)
        await save_prediction_batch(
            db=db,
            lottery_type=lottery_type,
            source_type="system",
            user_key=None,
            generator_mode="system_benchmark",
            strategy=strategy,
            params={"count": 10, "strategy_version": STRATEGY_VERSION},
            target_draw_date=target_draw_date,
            sets=sets,
            context={"benchmark": True},
        )
        created_batches += 1
    return {"created_batches": created_batches}
```

- [ ] **Step 3: Extend manual run endpoint**

In `backend/app/routers/review.py`, import `create_system_benchmarks` and add endpoint:

```python
@router.post("/benchmarks")
async def create_benchmarks(
    lottery_type: str = Query(...),
    target_draw_date: date = Query(...),
    db: AsyncSession = Depends(get_db),
):
    return await create_system_benchmarks(db, lottery_type, target_draw_date)
```

- [ ] **Step 4: Run benchmark test**

Run:

```powershell
cd D:\lottery-retro-engine\backend
python -m unittest backend.tests.test_review_learning.ReviewLearningPersistenceTest.test_system_benchmarks_are_idempotent -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```powershell
cd D:\lottery-retro-engine
git add backend/app/services/review_learning.py backend/app/routers/review.py backend/tests/test_review_learning.py
git commit -m "[Agent] feat: create system benchmark predictions"
```

## Task 7: Frontend API and Save Flow

**Files:**
- Modify: `frontend/src/api.js`
- Modify: `frontend/src/views/GenerateNumbers.vue`

- [ ] **Step 1: Add API helpers**

Add to `frontend/src/api.js` inside `api`:

```javascript
  async savePrediction(payload) {
    return request(`/api/v1/review/predictions`, {
      method: "POST",
      body: JSON.stringify({ lottery_type: lotteryType.value, ...payload }),
    });
  },

  async myReview(userKey, limit = 20) {
    return request(
      `/api/v1/review/me?user_key=${encodeURIComponent(userKey)}&lottery_type=${lotteryType.value}&limit=${limit}`
    );
  },

  async strategyReview(window = "24") {
    return request(
      `/api/v1/review/strategies?lottery_type=${lotteryType.value}&source_type=system&window=${window}`
    );
  },
```

- [ ] **Step 2: Add local review key and state**

In `frontend/src/views/GenerateNumbers.vue`, after existing refs:

```javascript
const REVIEW_USER_KEY = "yicai_review_user_key";
const reviewUserKey = ref("");
const reviewSaveWarning = ref("");
const reviewHistory = ref([]);
const strategyReview = ref([]);
const reviewLoading = ref(false);

function ensureReviewUserKey() {
  if (typeof localStorage === "undefined") return "";
  let key = localStorage.getItem(REVIEW_USER_KEY);
  if (!key) {
    const suffix = crypto?.randomUUID ? crypto.randomUUID() : `${Date.now()}-${Math.random().toString(16).slice(2)}`;
    key = `review-${suffix}`.slice(0, 80);
    localStorage.setItem(REVIEW_USER_KEY, key);
  }
  reviewUserKey.value = key;
  return key;
}
```

- [ ] **Step 3: Add save helper**

In `GenerateNumbers.vue`, add:

```javascript
function nextTargetDrawDate() {
  const today = new Date();
  today.setDate(today.getDate() + 1);
  return today.toISOString().slice(0, 10);
}

async function saveGeneratedPrediction({ mode, activeStrategy, sets, params }) {
  const userKey = ensureReviewUserKey();
  if (!userKey || !sets?.length) return;
  try {
    await api.savePrediction({
      source_type: "user",
      user_key: userKey,
      generator_mode: mode,
      strategy: activeStrategy,
      params,
      target_draw_date: nextTargetDrawDate(),
      sets: sets.map((set) => ({
        regular: set.regular || set.numbers || [],
        special: set.special ?? set.special_pick,
      })),
    });
    reviewSaveWarning.value = "";
    await loadReviewPanel();
  } catch (error) {
    reviewSaveWarning.value = t("本次号码已生成，但复盘记录保存失败；不影响查看号码。");
  }
}

async function loadReviewPanel() {
  const userKey = ensureReviewUserKey();
  reviewLoading.value = true;
  try {
    const [mine, strategies] = await Promise.all([
      api.myReview(userKey, 20),
      api.strategyReview("24"),
    ]);
    reviewHistory.value = mine.batches || [];
    strategyReview.value = strategies.strategies || [];
  } catch {
    reviewHistory.value = [];
    strategyReview.value = [];
  } finally {
    reviewLoading.value = false;
  }
}
```

- [ ] **Step 4: Call save after simple generation**

In `generate()`, after `result.value = data;`, add:

```javascript
    await saveGeneratedPrediction({
      mode: "simple",
      activeStrategy: strategy.value,
      sets: data.sets || [],
      params: { count: count.value },
    });
```

- [ ] **Step 5: Call save after layered generation**

In the layered generation success branch after `layeredResult.value = data;`, add:

```javascript
    await saveGeneratedPrediction({
      mode: "layered",
      activeStrategy: "layered",
      sets: (data.combinations || []).map((combo) => ({
        regular: Array.isArray(combo) ? combo : combo.regular,
        special: data.special_pick ?? data.back_zone?.pick,
      })),
      params: { ...layered.value },
    });
```

- [ ] **Step 6: Load review panel on mount and lottery change**

Add:

```javascript
watch(lotteryType, () => {
  loadReviewPanel();
});

ensureReviewUserKey();
loadReviewPanel();
```

Place this near existing lifecycle/watch setup, not inside a function.

- [ ] **Step 7: Run frontend build**

Run:

```powershell
cd D:\lottery-retro-engine\frontend
npm run build
```

Expected: Vite-SSG build completes.

- [ ] **Step 8: Commit**

```powershell
cd D:\lottery-retro-engine
git add frontend/src/api.js frontend/src/views/GenerateNumbers.vue
git commit -m "[Agent] feat: save generated picks for review"
```

## Task 8: Frontend Review Panel

**Files:**
- Modify: `frontend/src/views/GenerateNumbers.vue`

- [ ] **Step 1: Add review panel template**

Before the bottom disclaimer/ad slot in `GenerateNumbers.vue`, add:

```vue
    <section class="card-stripe p-6 sm:p-8 space-y-5">
      <div class="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p class="text-xs font-bold uppercase tracking-[0.24em] text-[#9d7a42]">Review Learning</p>
          <h2 class="mt-2 text-2xl font-black text-[#233142]">{{ t("复盘增强") }}</h2>
          <p class="mt-1 text-sm text-[#6c7570]">
            {{ t("系统会把模拟选号与后续开奖结果做对照，长期复盘不同策略的表现。") }}
          </p>
        </div>
        <button type="button" class="rounded-lg border border-[#d9c8ad] px-4 py-2 text-sm font-semibold text-[#233142]" @click="loadReviewPanel">
          {{ reviewLoading ? t("更新中...") : t("刷新复盘") }}
        </button>
      </div>

      <p v-if="reviewSaveWarning" class="rounded-lg bg-[#fff3d6] px-4 py-3 text-sm text-[#8d6220]">
        {{ reviewSaveWarning }}
      </p>

      <div class="grid gap-4 lg:grid-cols-2">
        <div class="rounded-xl border border-[#e5d8c5] bg-white/70 p-4">
          <h3 class="text-base font-bold text-[#233142]">{{ t("我的最近选号") }}</h3>
          <div v-if="reviewHistory.length" class="mt-3 space-y-3">
            <div v-for="batch in reviewHistory.slice(0, 3)" :key="batch.batch_key" class="rounded-lg bg-[#faf7ef] p-3">
              <div class="flex items-center justify-between gap-3 text-xs font-semibold text-[#7d867f]">
                <span>{{ batch.strategy }} · {{ batch.target_draw_date }}</span>
                <span>{{ batch.status === "reviewed" ? t("已复盘") : t("待开奖") }}</span>
              </div>
              <div class="mt-2 flex flex-wrap gap-1">
                <span v-for="(pick, index) in batch.picks.slice(0, 2)" :key="index" class="rounded-full bg-white px-2 py-1 text-xs text-[#233142]">
                  {{ pick.regular.join(", ") }} + {{ pick.special }}
                </span>
              </div>
            </div>
          </div>
          <p v-else class="mt-3 text-sm text-[#7d867f]">{{ t("生成号码后，这里会显示待复盘记录。") }}</p>
        </div>

        <div class="rounded-xl border border-[#e5d8c5] bg-white/70 p-4">
          <h3 class="text-base font-bold text-[#233142]">{{ t("系统策略榜（近24期）") }}</h3>
          <div v-if="strategyReview.length" class="mt-3 space-y-2">
            <div v-for="item in strategyReview.slice(0, 5)" :key="item.strategy" class="grid grid-cols-[1fr_auto] items-center gap-3 rounded-lg bg-[#faf7ef] px-3 py-2">
              <span class="text-sm font-semibold text-[#233142]">{{ strategyInfo(item.strategy).label || item.strategy }}</span>
              <span class="text-xs font-bold text-[#8d6220]">{{ item.avg_primary_hits.toFixed(2) }} {{ t("均命中") }}</span>
            </div>
          </div>
          <p v-else class="mt-3 text-sm text-[#7d867f]">{{ t("系统自动样本需要等待至少一次开奖复盘后显示。") }}</p>
        </div>
      </div>

      <p class="text-xs leading-6 text-[#8d8d7e]">
        {{ t("复盘数据仅用于对照历史开奖结果。彩票开奖具有随机性，历史表现不能保证未来结果。本功能仅供娱乐和数据复盘参考。") }}
      </p>
    </section>
```

- [ ] **Step 2: Add missing translations**

If `npm run build` reports missing generated i18n keys, add simplified Chinese strings to the current source if the repo uses a source dictionary. If there is no source dictionary, rely on `scripts/gen-i18n.mjs` extracting strings automatically.

- [ ] **Step 3: Run frontend build**

Run:

```powershell
cd D:\lottery-retro-engine\frontend
npm run build
```

Expected: build passes and `gen-i18n` completes.

- [ ] **Step 4: Commit**

```powershell
cd D:\lottery-retro-engine
git add frontend/src/views/GenerateNumbers.vue frontend/src/data/seoTopics.tw.js frontend/src/i18n.tw.js
git commit -m "[Agent] feat: show review learning panel"
```

## Task 9: Hook Review Into Draw Sync

**Files:**
- Modify: `backend/app/routers/jackpot.py`
- Modify: `backend/app/services/review_learning.py`

- [ ] **Step 1: Find latest draw upsert point**

Open `backend/app/routers/jackpot.py` and locate the code that writes or updates `Draw` rows from jackpot-sourced latest data.

- [ ] **Step 2: Import review helpers**

At the top of `backend/app/routers/jackpot.py`, add:

```python
from app.services.review_learning import create_system_benchmarks, run_review_for_draw
```

- [ ] **Step 3: Trigger review after draw upsert**

After the code has a committed or flushed `Draw` instance for the latest item, add:

```python
        await run_review_for_draw(db, draw)
        await create_system_benchmarks(db, draw.lottery_type, draw.draw_date)
```

If the local variable is named differently, use the actual `Draw` instance variable created by the upsert function. Do not trigger this before the row has an `id`.

- [ ] **Step 4: Protect scrape path from review failure**

Wrap the trigger:

```python
        try:
            await run_review_for_draw(db, draw)
            await create_system_benchmarks(db, draw.lottery_type, draw.draw_date)
        except Exception as exc:
            print(f"[review-learning] failed for {draw.lottery_type} {draw.draw_number}: {exc}")
```

This keeps the draw sync from failing if review aggregation has a bug.

- [ ] **Step 5: Compile backend**

Run:

```powershell
cd D:\lottery-retro-engine\backend
python -m compileall app
```

Expected: no syntax errors.

- [ ] **Step 6: Commit**

```powershell
cd D:\lottery-retro-engine
git add backend/app/routers/jackpot.py backend/app/services/review_learning.py
git commit -m "[Agent] feat: run review after draw sync"
```

## Task 10: Full Verification

**Files:**
- No planned code edits unless tests fail.

- [ ] **Step 1: Run backend unit tests**

Run:

```powershell
cd D:\lottery-retro-engine\backend
python -m unittest discover -s tests -v
```

Expected: all tests pass.

- [ ] **Step 2: Run backend compile**

Run:

```powershell
cd D:\lottery-retro-engine\backend
python -m compileall app
```

Expected: no syntax errors.

- [ ] **Step 3: Run frontend build**

Run:

```powershell
cd D:\lottery-retro-engine\frontend
npm run build
```

Expected: Vite-SSG build finishes.

- [ ] **Step 4: Manual API smoke**

Start backend locally, then run:

```powershell
Invoke-WebRequest -UseBasicParsing http://localhost:8000/api/v1/review/strategies?lottery_type=ssq
```

Expected: `200 OK` with JSON body containing `strategies`.

- [ ] **Step 5: Manual frontend smoke**

Start frontend locally, open `/generate`, generate one simple pick, and verify:

- Numbers still display even if save fails.
- "复盘增强" section appears.
- "我的最近选号" shows a pending batch after save succeeds.
- No navbar overlap on desktop or mobile.

- [ ] **Step 6: Final commit if smoke fixes were needed**

If smoke fixes were needed:

```powershell
cd D:\lottery-retro-engine
git add <changed-files>
git commit -m "[Agent] fix: stabilize review learning smoke tests"
```

If no fixes were needed, do not create an empty commit.

## Self-Review

- Spec coverage: data models, scoring, user save flow, system benchmark, review trigger, strategy snapshots, frontend review panel, and compliance copy are all mapped to tasks.
- Placeholder scan: the plan contains no TBD/TODO placeholders. The only conditional instruction is Task 10 Step 6, which explicitly says not to create an empty commit.
- Type consistency: model names, service function names, endpoint names, and frontend helper names are consistent across tasks.
