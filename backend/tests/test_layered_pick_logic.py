import asyncio
from datetime import date, timedelta
import unittest

from app.models.draw import Draw, FrequencyCache
from app.routers.analysis import (
    LayeredPickRequest,
    layered_pick,
)


class _ScalarResult:
    def __init__(self, rows):
        self._rows = rows

    def scalars(self):
        return self

    def all(self):
        return self._rows


class _FakeSession:
    """Fake DB session that returns draws on the first query and freq cache on the second."""

    def __init__(self, draws, freq_rows=None):
        self._draws = draws
        self._freq_rows = freq_rows or []
        self._call_count = 0

    async def execute(self, _query):
        self._call_count += 1
        # First call → draws, second call → FrequencyCache
        if self._call_count == 1:
            return _ScalarResult(self._draws)
        return _ScalarResult(self._freq_rows)


def _draw(days_ago, nums, special=1, lottery_type="marksix"):
    return Draw(
        draw_date=date(2026, 5, 20) - timedelta(days=days_ago),
        draw_number=f"26/{days_ago:03d}",
        lottery_type=lottery_type,
        num1=nums[0],
        num2=nums[1],
        num3=nums[2],
        num4=nums[3],
        num5=nums[4],
        num6=nums[5],
        special_num=special,
    )


def _freq(number, hotness=10, missed=0, lottery_type="marksix"):
    f = FrequencyCache()
    f.lottery_type = lottery_type
    f.number = number
    f.hotness_score = hotness
    f.consecutive_missed = missed
    f.total_appearances = hotness
    f.special_appearances = 0
    return f


class LayeredPickLogicTest(unittest.TestCase):
    def _make_draws_and_freq(self):
        draws = [
            _draw(0, [1, 2, 3, 4, 5, 6]),
            _draw(1, [1, 2, 3, 4, 7, 8]),
            _draw(2, [1, 2, 3, 9, 10, 11]),
            _draw(3, [1, 2, 12, 13, 14, 15]),
            _draw(4, [1, 16, 17, 18, 19, 20]),
            _draw(5, [21, 22, 23, 24, 25, 26]),
            _draw(6, [27, 28, 29, 30, 31, 32]),
            _draw(7, [33, 34, 35, 36, 37, 38]),
            _draw(8, [39, 40, 41, 42, 43, 44]),
            _draw(9, [45, 46, 47, 48, 49, 1]),
        ]
        # Give every possible marksix number a freq entry
        freq = [_freq(n, hotness=max(1, 10 - n % 5), missed=n % 7) for n in range(1, 50)]
        return draws, freq

    def test_funnel_default_10_8_6(self):
        draws, freq = self._make_draws_and_freq()
        payload = LayeredPickRequest(
            lottery_type="marksix",
            history_periods=10,
            hot_count=3,
            cold_count=1,
            trend_periods=10,
            consecutive="any",
            odd_even="any",
            big_small="any",
            pool1_size=10,
            pool2_size=8,
            pool3_size=6,
        )

        result = asyncio.run(layered_pick(payload, db=_FakeSession(draws, freq)))

        self.assertEqual(len(result["pool1"]), 10)
        self.assertEqual(len(result["pool2"]), 8)
        self.assertEqual(len(result["pool3"]), 6)
        self.assertIn("pool1_eliminated", result)
        self.assertIn("pool2_eliminated", result)
        self.assertIn("pool3_eliminated", result)
        self.assertIn("special_pick", result)
        self.assertEqual(result["stats"]["pool1_size"], 10)
        self.assertEqual(result["stats"]["pool2_size"], 8)
        self.assertEqual(result["stats"]["pool3_size"], 6)

    def test_funnel_custom_12_9_6(self):
        draws, freq = self._make_draws_and_freq()
        payload = LayeredPickRequest(
            lottery_type="marksix",
            history_periods=10,
            hot_count=4,
            cold_count=2,
            trend_periods=10,
            consecutive="any",
            odd_even="any",
            big_small="any",
            pool1_size=12,
            pool2_size=9,
            pool3_size=6,
        )

        result = asyncio.run(layered_pick(payload, db=_FakeSession(draws, freq)))

        self.assertEqual(len(result["pool1"]), 12)
        self.assertEqual(len(result["pool2"]), 9)
        self.assertEqual(len(result["pool3"]), 6)

    def test_funnel_invalid_size_order_raises(self):
        draws, freq = self._make_draws_and_freq()
        payload = LayeredPickRequest(
            lottery_type="marksix",
            history_periods=10,
            pool1_size=8,
            pool2_size=10,   # wrong: pool2 > pool1
            pool3_size=6,
        )
        from fastapi import HTTPException
        with self.assertRaises(HTTPException) as ctx:
            asyncio.run(layered_pick(payload, db=_FakeSession(draws, freq)))
        self.assertEqual(ctx.exception.status_code, 400)

    def test_pool3_contains_must_include(self):
        draws, freq = self._make_draws_and_freq()
        payload = LayeredPickRequest(
            lottery_type="marksix",
            history_periods=10,
            hot_count=3,
            cold_count=1,
            pool1_size=10,
            pool2_size=8,
            pool3_size=6,
            must_include=[7],
        )

        result = asyncio.run(layered_pick(payload, db=_FakeSession(draws, freq)))

        self.assertIn(7, result["pool3"])

    def test_pool3_excludes_must_exclude(self):
        draws, freq = self._make_draws_and_freq()
        # Exclude numbers 1..10 — they're all hot, so this forces the funnel to use less popular ones
        payload = LayeredPickRequest(
            lottery_type="marksix",
            history_periods=10,
            hot_count=3,
            cold_count=1,
            pool1_size=10,
            pool2_size=8,
            pool3_size=6,
            must_exclude=list(range(1, 11)),
        )

        result = asyncio.run(layered_pick(payload, db=_FakeSession(draws, freq)))

        for n in range(1, 11):
            self.assertNotIn(n, result["pool3"])


if __name__ == "__main__":
    unittest.main()
