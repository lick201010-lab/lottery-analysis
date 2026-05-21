import re

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, validator
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.newsletter import NewsletterSubscriber


router = APIRouter(prefix="/api/v1/newsletter", tags=["newsletter"])

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class NewsletterSubscribeRequest(BaseModel):
    email: str

    @validator("email")
    def normalize_email(cls, value):
        email = value.strip().lower()
        if not EMAIL_RE.match(email):
            raise ValueError("请输入有效的邮箱地址")
        return email


@router.post("/subscribe")
async def subscribe_email(payload: NewsletterSubscribeRequest, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(
        select(NewsletterSubscriber).where(NewsletterSubscriber.email == payload.email)
    )
    if existing.scalars().first():
        return {"status": "already_subscribed", "email": payload.email}

    subscriber = NewsletterSubscriber(email=payload.email)
    db.add(subscriber)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        return {"status": "already_subscribed", "email": payload.email}
    except Exception as exc:
        await db.rollback()
        raise HTTPException(status_code=500, detail="订阅暂时失败，请稍后再试") from exc

    # TODO: 接入 Resend Audience API 后，在这里把邮箱同步到邮件列表。
    return {"status": "subscribed", "email": payload.email}
