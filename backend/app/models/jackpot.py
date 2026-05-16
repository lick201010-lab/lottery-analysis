from sqlalchemy import Column, Integer, String, DateTime, Float, JSON, func
from app.models.draw import Base


class JackpotData(Base):
    __tablename__ = "jackpot_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    lottery_type = Column(String(20), nullable=False, index=True)
    draw_number = Column(String(20), nullable=False, index=True)
    draw_date = Column(String(20))

    # Jackpot / pool amount (in yuan/hkd)
    pool_amount = Column(Float, nullable=True)
    sales_amount = Column(Float, nullable=True)

    # Prize breakdown (JSON array of {level, count, amount_per_note})
    prize_breakdown = Column(JSON, default=list)

    # Winning numbers
    red_balls = Column(String(50))
    blue_ball = Column(String(10))

    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
