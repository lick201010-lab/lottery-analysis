import re
import sqlite3
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, validator

from app.config import DATA_DIR


router = APIRouter(prefix="/api/v1/newsletter", tags=["newsletter"])

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
NEWSLETTER_DB_PATH = f"{DATA_DIR}/newsletter.db"


class NewsletterSubscribeRequest(BaseModel):
    email: str

    @validator("email")
    def normalize_email(cls, value):
        email = value.strip().lower()
        if not EMAIL_RE.match(email):
            raise ValueError("请输入有效的邮箱地址")
        return email


@router.post("/subscribe")
async def subscribe_email(payload: NewsletterSubscribeRequest):
    try:
        status = save_subscriber(payload.email)
    except Exception as exc:
        raise HTTPException(status_code=500, detail="订阅暂时失败，请稍后再试") from exc

    # TODO: 接入 Resend Audience API 后，在这里把邮箱同步到邮件列表。
    return {"status": status, "email": payload.email}


def save_subscriber(email: str, db_path: str = NEWSLETTER_DB_PATH) -> str:
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS newsletter_subscribers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL UNIQUE,
                subscribed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        cursor = conn.execute(
            "INSERT OR IGNORE INTO newsletter_subscribers (email) VALUES (?)",
            (email,),
        )
        conn.commit()
        return "subscribed" if cursor.rowcount else "already_subscribed"
