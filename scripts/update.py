#!/usr/bin/env python3
"""
Unified MarkSix data update script with auto git commit.
Usage: python scripts/update.py
"""
import subprocess
import sys
from pathlib import Path
from datetime import datetime

SCRIPTS_DIR = Path(__file__).parent.resolve()
ROOT_DIR = SCRIPTS_DIR.parent
LOG_DIR = SCRIPTS_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

# Files to track for auto-commit
TRACKED_PATHS = [
    "frontend/public/data/draws.json",
    "frontend/public/data/frequency.json",
    "frontend/public/data/pairs.json",
    "frontend/public/data/patterns.json",
    "frontend/public/data/trends.json",
    "marksix_draws.json",
    "data/marksix.db",
]


def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    try:
        print(line)
    except UnicodeEncodeError:
        print(line.encode("gbk", "ignore").decode("gbk"))
    log_file = LOG_DIR / f"update_{datetime.now().strftime('%Y%m%d')}.log"
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def run(name, *args):
    log("=" * 50)
    log(f"Running: {name}")
    log("=" * 50)
    result = subprocess.run(
        [sys.executable, *args],
        cwd=ROOT_DIR,
        capture_output=False,
    )
    if result.returncode != 0:
        log(f"ERROR: {name} failed with code {result.returncode}")
        sys.exit(result.returncode)


def git_cmd(*args, check=True):
    """Run a git command and return (returncode, stdout, stderr)."""
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT_DIR,
        capture_output=True,
        text=True,
    )
    if check and result.returncode != 0:
        log(f"Git error: git {' '.join(args)} -> {result.returncode}")
        if result.stderr:
            log(f"  stderr: {result.stderr.strip()}")
    return result


def ensure_git_identity():
    """Ensure git user.name and user.email are set for auto-commits."""
    name_result = git_cmd("config", "user.name", check=False)
    email_result = git_cmd("config", "user.email", check=False)
    if not name_result.stdout.strip():
        git_cmd("config", "user.name", "MarkSix Bot")
        log("Set git user.name = MarkSix Bot")
    if not email_result.stdout.strip():
        git_cmd("config", "user.email", "bot@marksix.local")
        log("Set git user.email = bot@marksix.local")


def has_changes():
    """Check if any tracked files have changes."""
    result = git_cmd("status", "--porcelain", *TRACKED_PATHS, check=False)
    return bool(result.stdout.strip())


def auto_commit():
    """Auto-commit data changes if any."""
    log("")
    log("Checking for data changes...")

    # Stage tracked files
    for p in TRACKED_PATHS:
        path = ROOT_DIR / p
        if path.exists():
            git_cmd("add", p, check=False)

    # Also stage new scripts if they exist
    for script in ["scripts/update.py", "scripts/fetch_marksix.py", "scripts/merge_marksix.py"]:
        path = ROOT_DIR / script
        if path.exists():
            git_cmd("add", script, check=False)

    if not has_changes():
        log("No data changes to commit.")
        return

    # Commit
    date_str = datetime.now().strftime("%Y-%m-%d")
    commit_msg = f"auto: update MarkSix data {date_str}"
    result = git_cmd("commit", "-m", commit_msg, check=False)
    if result.returncode != 0:
        log(f"ERROR: Git commit failed: {result.stderr.strip()}")
        return
    log(f"Committed: {commit_msg}")

    # Push
    log("Pushing to remote...")
    push_result = git_cmd("push", check=False)
    if push_result.returncode == 0:
        log("Push successful.")
    else:
        log(f"Push failed: {push_result.stderr.strip()}")
        log("(Data is still saved locally; push manually later.)")


if __name__ == "__main__":
    log("MarkSix auto-update started")
    run("Fetch from lottery.hk", str(SCRIPTS_DIR / "fetch_marksix.py"))
    run("Merge & recalculate", str(SCRIPTS_DIR / "merge_marksix.py"))

    ensure_git_identity()
    auto_commit()

    log("Update complete!")
