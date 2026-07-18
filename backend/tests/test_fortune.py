import hashlib
import hmac
import unittest
from unittest.mock import patch

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.models.draw import Base
from app.routers.fortune import (
    FortuneAdRewardRequest,
    FortuneGenerateRequest,
    FortuneOfferingRequest,
    FortuneProfileRequest,
    _generate_numbers_for_lottery,
    fortune_ad_reward,
    fortune_generate,
    fortune_offering,
    fortune_profile,
)


class FortuneRouterTest(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.engine = create_async_engine("sqlite+aiosqlite:///:memory:")
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        self.Session = async_sessionmaker(self.engine, expire_on_commit=False)

    async def asyncTearDown(self):
        await self.engine.dispose()

    async def test_profile_upsert_keeps_existing_fields(self):
        async with self.Session() as session:
            first = await fortune_profile(
                FortuneProfileRequest(user_key="fortune-user-0001", zodiac="龙"),
                db=session,
            )
            second = await fortune_profile(
                FortuneProfileRequest(
                    user_key="fortune-user-0001",
                    constellation="天秤",
                ),
                db=session,
            )

            self.assertEqual(first["profile"]["zodiac"], "龙")
            self.assertEqual(second["profile"]["zodiac"], "龙")
            self.assertEqual(second["profile"]["constellation"], "天秤")

    async def test_daily_result_is_idempotent_per_user_and_lottery(self):
        async with self.Session() as session:
            payload = FortuneGenerateRequest(
                user_key="fortune-user-0002",
                lottery_type="ssq",
                draw_date="2026-07-03",
                zodiac="虎",
                constellation="狮子",
            )
            first = await fortune_generate(payload, db=session)
            second = await fortune_generate(payload, db=session)

            self.assertFalse(first["already_generated"])
            self.assertTrue(second["already_generated"])
            self.assertEqual(first["result"]["id"], second["result"]["id"])
            self.assertEqual(
                first["result"]["regular_numbers"],
                second["result"]["regular_numbers"],
            )
            self.assertEqual(
                first["result"]["special_number"],
                second["result"]["special_number"],
            )

    async def test_offering_requires_enough_points(self):
        async with self.Session() as session:
            with self.assertRaises(HTTPException) as raised:
                await fortune_offering(
                    FortuneOfferingRequest(
                        user_key="fortune-user-0003",
                        offering_type="peach",
                    ),
                    db=session,
                )

            self.assertEqual(raised.exception.status_code, 400)

    async def test_ad_reward_is_disabled_without_verified_provider(self):
        async with self.Session() as session:
            with self.assertRaises(HTTPException) as raised:
                await fortune_ad_reward(
                    FortuneAdRewardRequest(
                        user_key="fortune-user-0004",
                        provider="test-provider",
                        reward_id="reward-0001",
                        verification_token="0" * 64,
                    ),
                    db=session,
                )
            self.assertEqual(raised.exception.status_code, 503)

    async def test_ad_reward_requires_signature_and_blocks_replay(self):
        user_key = "fortune-user-0005"
        provider = "test-provider"
        reward_id = "reward-0002"
        from app.routers.fortune import _today

        message = f"{provider}:{user_key}:{reward_id}:{_today().isoformat()}".encode()
        token = hmac.new(b"test-secret", message, hashlib.sha256).hexdigest()
        request = FortuneAdRewardRequest(
            user_key=user_key,
            provider=provider,
            reward_id=reward_id,
            verification_token=token,
        )

        with (
            patch("app.routers.fortune.FORTUNE_REWARDED_AD_ENABLED", True),
            patch(
                "app.routers.fortune.FORTUNE_REWARDED_AD_SECRET",
                "test-secret",
            ),
        ):
            async with self.Session() as session:
                invalid = request.model_copy(
                    update={"verification_token": "0" * 64}
                )
                with self.assertRaises(HTTPException) as raised:
                    await fortune_ad_reward(invalid, db=session)
                self.assertEqual(raised.exception.status_code, 403)

                reward = await fortune_ad_reward(request, db=session)
                self.assertEqual(reward["points_balance"], 10)
                with self.assertRaises(HTTPException) as raised:
                    await fortune_ad_reward(request, db=session)
                self.assertEqual(raised.exception.status_code, 409)

    def test_lottery_number_rules(self):
        marksix_regular, marksix_special = _generate_numbers_for_lottery("marksix")
        self.assertEqual(len(marksix_regular), 6)
        self.assertEqual(len(set(marksix_regular + [marksix_special])), 7)
        self.assertTrue(all(1 <= number <= 49 for number in marksix_regular))
        self.assertTrue(1 <= marksix_special <= 49)
        self.assertEqual(marksix_regular, sorted(marksix_regular))

        ssq_regular, ssq_special = _generate_numbers_for_lottery("ssq")
        self.assertEqual(len(ssq_regular), 6)
        self.assertEqual(len(set(ssq_regular)), 6)
        self.assertTrue(all(1 <= number <= 33 for number in ssq_regular))
        self.assertTrue(1 <= ssq_special <= 16)
        self.assertEqual(ssq_regular, sorted(ssq_regular))

        qxc_regular, qxc_special = _generate_numbers_for_lottery("qxc")
        self.assertEqual(len(qxc_regular), 6)
        self.assertTrue(all(0 <= number <= 9 for number in qxc_regular))
        self.assertTrue(0 <= qxc_special <= 14)


if __name__ == "__main__":
    unittest.main()
