# Deployment Reference

## Server Configuration

- **OS**: Ubuntu 22.04 LTS
- **IP**: 47.237.181.181
- **User**: admin
- **Domain**: www.ckl.hk (frontend), api.ckl.hk (backend)
- **Caddy**: Auto HTTPS, reverse proxy
- **Python**: 3.12
- **Node**: v20.20.2

## Operating Rule

All accepted code or UI changes for this project must be updated on the production site:

- Frontend: `https://www.ckl.hk`
- Backend API: `https://api.ckl.hk`

After local verification, the normal handoff is: commit and push to GitHub, pull on the server, rebuild the frontend, restart the backend when backend files changed, then verify the production URLs.

## Caddyfile

```
www.ckl.hk {
    root * /opt/lottery-analysis/frontend/dist
    file_server
}

api.ckl.hk {
    reverse_proxy localhost:8000
}
```

## Backend Service

Runs via `nohup` (not systemd):

```bash
cd /opt/lottery-analysis/backend
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2 > uvicorn.log 2>&1 &
```

Restart procedure:
```bash
pkill -f "uvicorn"
cd /opt/lottery-analysis/backend
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2 > uvicorn.log 2>&1 &
```

## Git Workflow

Local dev machine (mainland China):
- Cannot reliably push to GitHub (timeouts)
- Write code locally, test in backend/ directory

Server (Hong Kong):
- Direct GitHub access, no proxy needed
- `git pull` from `/opt/lottery-analysis`
- Restart backend after pull

## Database

SQLite at `data/marksix.db`:
- Auto-creates tables via SQLAlchemy `DeclarativeBase`
- No migrations — schema changes handled manually
- Backup: simply copy the `.db` file

## Frontend Build

```bash
cd /opt/lottery-analysis/frontend
npm run build
```

Output goes to `frontend/dist/`, served by Caddy.
