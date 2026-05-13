import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(os.path.dirname(BASE_DIR), "data")
DB_PATH = os.path.join(DATA_DIR, "marksix.db")

# Production: use env DATABASE_URL (PostgreSQL on Render, etc.)
# Development: fallback to local SQLite
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    f"sqlite+aiosqlite:///{DB_PATH}"
)

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
}

SCRAPE_DELAY_SECONDS = 3
