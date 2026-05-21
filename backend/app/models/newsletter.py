from sqlalchemy import Column, DateTime, Integer, String, func

from app.models.draw import Base


class NewsletterSubscriber(Base):
    __tablename__ = "newsletter_subscribers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), nullable=False, unique=True, index=True)
    subscribed_at = Column(DateTime, nullable=False, server_default=func.now())
