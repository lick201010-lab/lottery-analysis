import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(os.path.dirname(BASE_DIR), "data")
DB_PATH = os.path.join(DATA_DIR, "marksix.db")

# Production: use env DATABASE_URL (PostgreSQL on Render, etc.)
# Development: fallback to local SQLite
raw_url = os.environ.get("DATABASE_URL", f"sqlite+aiosqlite:///{DB_PATH}")

# Render gives "postgres://..." or "postgresql://..." but async SQLAlchemy needs "postgresql+asyncpg://"
if raw_url.startswith("postgres://"):
    raw_url = raw_url.replace("postgres://", "postgresql+asyncpg://", 1)
elif raw_url.startswith("postgresql://") and "+asyncpg" not in raw_url:
    raw_url = raw_url.replace("postgresql://", "postgresql+asyncpg://", 1)

DATABASE_URL = raw_url

LOTTERY_CONFIG = {
    "marksix": {
        "name": "香港六合彩",
        "max_regular": 49,
        "max_special": 49,
        "regular_count": 6,
        "special_count": 1,
        "data_url": "https://raw.githubusercontent.com/icelam/mark-six-data-visualization/master/data/all.json",
    },
    "ssq": {
        "name": "双色球",
        "max_regular": 33,
        "max_special": 16,
        "regular_count": 6,
        "special_count": 1,
        "data_url": "https://raw.githubusercontent.com/womkim/caipiao/master/ssq/data.json",
    },
    "qxc": {
        "name": "7星彩",
        "min_regular": 0,
        "max_regular": 9,
        "min_special": 0,
        "max_special": 14,
        "regular_count": 6,
        "special_count": 1,
        "allow_duplicates": True,
        "positional": True,
        "draw_days": [2, 5, 0],
        "draw_time": "21:25",
        "data_url": "https://kaijiang.500.com/static/info/kaijiang/xml/qxc/list.xml",
        "pool_url": "https://trade.500.com/qxc/",
    },
}

SCRAPE_DELAY_SECONDS = 3

# Rewarded ads remain disabled until a verified provider callback is wired.
# Never expose FORTUNE_REWARDED_AD_SECRET to frontend code.
FORTUNE_REWARDED_AD_ENABLED = (
    os.environ.get("FORTUNE_REWARDED_AD_ENABLED", "").strip().lower()
    in {"1", "true", "yes", "on"}
)
FORTUNE_REWARDED_AD_SECRET = os.environ.get(
    "FORTUNE_REWARDED_AD_SECRET", ""
).strip()
