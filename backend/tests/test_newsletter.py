import asyncio
import unittest

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.models.draw import Base
from app.models.newsletter import NewsletterSubscriber
from app.routers.newsletter import NewsletterSubscribeRequest, subscribe_email


class NewsletterSubscribeTest(unittest.TestCase):
    def test_invalid_email_is_rejected(self):
        with self.assertRaises(ValueError):
            NewsletterSubscribeRequest(email="not-an-email")

    def test_subscribe_normalizes_and_deduplicates_email(self):
        async def scenario():
            engine = create_async_engine("sqlite+aiosqlite:///:memory:")
            try:
                async with engine.begin() as conn:
                    await conn.run_sync(Base.metadata.create_all)

                Session = async_sessionmaker(engine, expire_on_commit=False)
                async with Session() as session:
                    first = await subscribe_email(NewsletterSubscribeRequest(email=" User@Example.COM "), session)
                    second = await subscribe_email(NewsletterSubscribeRequest(email="user@example.com"), session)

                    rows = (await session.execute(NewsletterSubscriber.__table__.select())).all()
                    self.assertEqual(first["status"], "subscribed")
                    self.assertEqual(second["status"], "already_subscribed")
                    self.assertEqual(len(rows), 1)
                    self.assertEqual(rows[0]._mapping["email"], "user@example.com")
            finally:
                await engine.dispose()

        asyncio.run(scenario())


if __name__ == "__main__":
    unittest.main()
