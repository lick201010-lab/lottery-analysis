from pydantic import BaseModel
from datetime import date
from typing import Optional


class DrawOut(BaseModel):
    id: int
    draw_date: date
    draw_number: str
    lottery_type: str
    num1: int
    num2: int
    num3: int
    num4: int
    num5: int
    num6: int
    special_num: int
    odd_count: int
    even_count: int
    small_count: int
    big_count: int
    has_consecutive: bool
    sum_total: int

    model_config = {"from_attributes": True}


class DrawListOut(BaseModel):
    draws: list[DrawOut]
    total: int
    page: int
    per_page: int


class ScrapeTriggerIn(BaseModel):
    source: str = "github"
    lottery_type: str = "marksix"
    date_from: Optional[str] = None
    date_to: Optional[str] = None


class ScrapeStatusOut(BaseModel):
    job_id: str
    status: str
    draws_fetched: int
    draws_new: int
    error_message: Optional[str] = None


class HealthOut(BaseModel):
    status: str
    total_draws: int
    last_scrape: Optional[str] = None
