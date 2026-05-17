---
name: lottery-analysis
description: Lottery data analysis platform for MarkSix (六合彩) and SSQ (双色球). Covers backend FastAPI, frontend Vue 3, deployment on Aliyun HK server, Caddy reverse proxy, data scrapers, and SQLite database. Use when working with lottery data scraping, API routes, frontend components, deployment, or database models in this project.
---

# Lottery Analysis — 弈彩 YiCai

## Project Overview

A full-stack lottery data analysis platform serving Hong Kong MarkSix (六合彩) and mainland China SSQ (双色球) data.

- **Frontend**: Vue 3 + Vite + Tailwind CSS v4 + Chart.js, deployed at `www.ckl.hk`
- **Backend**: FastAPI + SQLAlchemy async + SQLite, running at `api.ckl.hk` (port 8000)
- **Server**: Aliyun Light Server, Ubuntu 22.04, Hong Kong (direct internet, no GFW)
- **Database**: SQLite `data/marksix.db` (~8k records total)
- **Theme**: Glassmorphism cards on diamond gradient background (`#1a0b2e → #9d4edd`)

## Architecture

```
User → Caddy (443) → api.ckl.hk → localhost:8000 (FastAPI)
                → www.ckl.hk → /opt/lottery-analysis/frontend/dist
```

Caddy handles auto-HTTPS. Backend runs via `nohup uvicorn` with 2 workers.

## Key Conventions

### Naming
- `marksix` = 六合彩 (Hong Kong)
- `ssq` = 双色球 ( mainland China)
- Frontend labels: "六合彩" / "双色球"
- Brand: 弈彩 YiCai

### Ball Colors
- **MarkSix**: Official HKJC rules — Red (1,2,7,8,12,13,18,19,23,24,29,30,34,35,40,45,46), Blue (3,4,9,10,14,15,20,25,26,31,36,37,41,42,47,48), Green (5,6,11,16,17,21,22,27,28,32,33,38,39,43,44,49)
- **SSQ**: Red balls + Blue ball (only two colors)

### Tax Rules
- SSQ: 20% tax on prizes > ¥10,000 per ticket
- MarkSix: 0% tax (Hong Kong tax-free)

### Draw Schedule
- MarkSix: Tuesday/Thursday/Saturday at 21:30
- SSQ: Tuesday/Thursday/Sunday at 21:15

## Deployment Workflow

Run on the server (Aliyun HK, user `admin`):

```bash
cd /opt/lottery-analysis
git pull                          # HK server has direct GitHub access
cd backend
pkill -f "uvicorn"
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2 > uvicorn.log 2>&1 &
```

For frontend changes:
```bash
cd /opt/lottery-analysis/frontend
npm run build
```

No SSH access from local dev machine — all server operations are manual.

## Database Models

### `draws` table
- `lottery_type`: "marksix" or "ssq"
- `draw_number`: string (e.g. "26054" for SSQ, "2025/064" for MarkSix)
- `draw_date`: Date
- `num1`–`num6`, `special_num`: integers
- Computed fields: `odd_count`, `even_count`, `small_count`, `big_count`, `has_consecutive`, `sum_total`

### `jackpot_data` table
- `lottery_type`, `draw_number`, `draw_date`
- `pool_amount`, `sales_amount`: floats (yuan)
- `prize_breakdown`: JSON array `[{level, count, amount_per_note}]`
- `red_balls`, `blue_ball`: comma-separated strings

## Data Scrapers

### SSQ (双色球)
- **Primary**: `datachart.500.com/ssq/history/newinc/history.php` — HTML table with full prize data
- **Fallback**: `kaijiang.500.com/static/info/kaijiang/xml/ssq/list.xml` — XML, numbers only, no jackpot
- **Known issue**: HTML table may have an extra serial-number column; parser auto-detects offset
- **API**: `POST /api/v1/jackpot/scrape` triggers scraping, upserts into `jackpot_data`

### MarkSix (六合彩)
- **Primary**: `lottery.hk/zh-hans/liuhecai/kaijiangjieguo/` — stable latest-result table
- **Fallback**: `win.on.cc/marksix/`, then database `draws` table
- **Note**: MarkSix has no rolling jackpot; `pool_amount` is always `null`

### Data Sources Availability (from HK server)
| Source | Status |
|--------|--------|
| `cwl.gov.cn` (official) | 403 Forbidden |
| `datachart.500.com` | ✅ Working |
| `kaijiang.500.com` XML | ✅ Working (numbers only) |
| `win.on.cc/marksix/` | ✅ Accessible (best effort parser) |
| `lottery.hk` MarkSix results | ✅ Working (latest result fallback) |
| `bet.hkjc.com` | ❌ Empty/timeout |

## File Structure

```
backend/
  app/
    main.py           # FastAPI app, includes routers
    database.py       # SQLite async engine + session
    config.py         # LOTTERY_CONFIG
    models/
      draw.py         # Draw, FrequencyCache, PairFrequency, ScrapeLog
      jackpot.py      # JackpotData
    routers/
      draws.py        # /api/v1/draws/*
      analysis.py     # /api/v1/analysis/*
      jackpot.py      # /api/v1/jackpot/* — scrape + latest + history
    services/
      jackpot_scraper.py  # SSQ + MarkSix scrapers
  tests/
frontend/
  src/
    views/
      Dashboard.vue       # Hero cards + jackpot display
      JackpotAnalysis.vue # Tax calculator
    components/
      CountdownTimer.vue  # Real-time countdown
      AppFooter.vue
    api.js              # API client including jackpotLatest() + jackpotScrape()
  dist/               # Build output (served by Caddy)
data/
  marksix.db          # SQLite database
scripts/
  fetch_marksix.py    # Historical data scraper
  fetch_ssq.py        # Historical data scraper
  merge_marksix.py    # Data merge/deduplication
```

## Common Tasks

### Add a new data source for SSQ jackpot
Edit `backend/app/services/jackpot_scraper.py`:
1. Add async fetch function (e.g. `_try_new_source()`)
2. Add parser function
3. Add to `fetch_ssq_jackpot()` fallback chain

### Fix frontend API integration
Edit `frontend/src/api.js` — add method to `api` object, then call in Vue component.

### Update database schema
1. Edit model in `backend/app/models/*.py`
2. SQLite auto-creates tables on startup (DeclarativeBase), but migrations must be handled manually
3. Restart backend

### Check backend logs
```bash
cd /opt/lottery-analysis/backend
tail -f uvicorn.log
```

## Troubleshooting

### `pool_amount` is null for SSQ
- Check if `datachart.500.com` HTML structure changed
- Parser tries Strategy 1 (`t_tr1`), Strategy 2 (scan all `<tr>`), Strategy 3 (markdown format)
- Add debug: save HTML to `/tmp/datachart.html` and inspect table structure

### Git push fails from local dev
- Local machine is in mainland China, GitHub often times out
- Server (HK) can `git pull` directly — no proxy needed
- Use server as the git sync point

### MarkSix scraper returns empty
- Normal — on.cc HTML parsing is not yet robust
- Database fallback provides complete data automatically
- No user-visible impact

## References

- `references/deployment.md` — Detailed deployment and server configuration
- `references/data-sources.md` — All data sources, URLs, and parsing notes
- `references/frontend-guide.md` — Component structure and Tailwind v4 patterns
