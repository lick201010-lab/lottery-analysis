import asyncio
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.draw import ScrapeLog
from app.schemas.draw import ScrapeTriggerIn, ScrapeStatusOut
from app.services.import_service import import_github_dataset
from app.services.scraper import rebuild_caches

router = APIRouter(prefix="/api/v1/scrape", tags=["scrape"])

# In-memory job tracking
_scrape_jobs: dict[str, dict] = {}


@router.post("/trigger")
async def trigger_scrape(body: ScrapeTriggerIn, db: AsyncSession = Depends(get_db)):
    job_id = str(uuid.uuid4())[:8]
    log = ScrapeLog(
        source=body.source,
        lottery_type=body.lottery_type,
        status="running",
        started_at=datetime.now(),
    )
    db.add(log)
    await db.commit()
    await db.refresh(log)

    _scrape_jobs[job_id] = {"status": "running", "log_id": log.id, "new": 0, "fetched": 0}

    asyncio.create_task(_run_scrape(job_id, body.source, body.lottery_type, db))

    return ScrapeStatusOut(job_id=job_id, status="running", draws_fetched=0, draws_new=0)


@router.get("/status/{job_id}", response_model=ScrapeStatusOut)
async def scrape_status(job_id: str):
    job = _scrape_jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return ScrapeStatusOut(
        job_id=job_id,
        status=job["status"],
        draws_fetched=job.get("fetched", 0),
        draws_new=job.get("new", 0),
        error_message=job.get("error"),
    )


@router.get("/logs")
async def scrape_logs(
    lottery_type: str = "marksix",
    db: AsyncSession = Depends(get_db),
    limit: int = 10,
):
    result = await db.execute(
        select(ScrapeLog)
        .where(ScrapeLog.lottery_type == lottery_type)
        .order_by(ScrapeLog.id.desc())
        .limit(limit)
    )
    logs = result.scalars().all()
    return [
        {
            "id": l.id,
            "lottery_type": l.lottery_type,
            "started_at": str(l.started_at),
            "finished_at": str(l.finished_at) if l.finished_at else None,
            "status": l.status,
            "draws_fetched": l.draws_fetched,
            "draws_new": l.draws_new,
            "source": l.source,
        }
        for l in logs
    ]


async def _run_scrape(job_id: str, source: str, lottery_type: str, db_session: AsyncSession):
    new = 0
    fetched = 0
    error = None
    try:
        if source in ("github", "hkjc"):
            new = await import_github_dataset(db_session, lottery_type)
            fetched = new
            await rebuild_caches(db_session, lottery_type)

        _scrape_jobs[job_id]["new"] = new
        _scrape_jobs[job_id]["fetched"] = fetched
        _scrape_jobs[job_id]["status"] = "success"

        # Update scrape log
        log = await db_session.get(ScrapeLog, _scrape_jobs[job_id]["log_id"])
        if log:
            log.status = "success" if error is None else "failed"
            log.draws_fetched = fetched
            log.draws_new = new
            log.finished_at = datetime.now()
            log.error_message = error
            await db_session.commit()
    except Exception as e:
        error = str(e)
        _scrape_jobs[job_id]["status"] = "failed"
        _scrape_jobs[job_id]["error"] = error
        log = await db_session.get(ScrapeLog, _scrape_jobs[job_id]["log_id"])
        if log:
            log.status = "failed"
            log.error_message = error
            log.finished_at = datetime.now()
            await db_session.commit()
