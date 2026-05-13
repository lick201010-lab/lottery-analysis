from sqlalchemy import Column, Integer, String, Date, Boolean, DateTime, func, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class Draw(Base):
    __tablename__ = "draws"
    __table_args__ = (
        UniqueConstraint("draw_date", "lottery_type", name="uq_draw_date_lottery"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    draw_date = Column(Date, nullable=False, index=True)
    draw_number = Column(String(20), nullable=False, index=True)
    lottery_type = Column(String(20), nullable=False, default="marksix", index=True)
    num1 = Column(Integer, nullable=False)
    num2 = Column(Integer, nullable=False)
    num3 = Column(Integer, nullable=False)
    num4 = Column(Integer, nullable=False)
    num5 = Column(Integer, nullable=False)
    num6 = Column(Integer, nullable=False)
    special_num = Column(Integer, nullable=False)
    odd_count = Column(Integer, nullable=False, default=0)
    even_count = Column(Integer, nullable=False, default=0)
    small_count = Column(Integer, nullable=False, default=0)
    big_count = Column(Integer, nullable=False, default=0)
    has_consecutive = Column(Boolean, nullable=False, default=False)
    sum_total = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, server_default=func.now())


class FrequencyCache(Base):
    __tablename__ = "frequency_cache"

    lottery_type = Column(String(20), primary_key=True, default="marksix")
    number = Column(Integer, primary_key=True)
    total_appearances = Column(Integer, nullable=False, default=0)
    special_appearances = Column(Integer, nullable=False, default=0)
    last_appearance_date = Column(Date)
    last_appearance_draw = Column(String(20))
    consecutive_missed = Column(Integer, nullable=False, default=0)
    hotness_score = Column(Integer, nullable=False, default=0)
    updated_at = Column(DateTime, server_default=func.now())


class PairFrequency(Base):
    __tablename__ = "pair_frequency"

    lottery_type = Column(String(20), primary_key=True, default="marksix")
    num_a = Column(Integer, primary_key=True)
    num_b = Column(Integer, primary_key=True)
    co_occurrences = Column(Integer, nullable=False, default=0)


class ScrapeLog(Base):
    __tablename__ = "scrape_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    lottery_type = Column(String(20), nullable=False, default="marksix")
    started_at = Column(DateTime, nullable=False, default=func.now())
    finished_at = Column(DateTime)
    status = Column(String(20), nullable=False, default="running")
    draws_fetched = Column(Integer, default=0)
    draws_new = Column(Integer, default=0)
    error_message = Column(String)
    source = Column(String(50), nullable=False, default="hkjc")
