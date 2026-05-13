"""Seed the database with historical lottery data from GitHub community datasets.

Usage:
    python seed_data.py                              # import marksix (default)
    python seed_data.py --lottery-type ssq           # import 双色球 into existing DB
    python seed_data.py --recreate --lottery-type ssq  # delete DB, recreate, import ssq
    python seed_data.py --recreate --all              # delete DB, recreate, import both
    python seed_data.py --all                         # import both into existing DB
"""
import asyncio
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from app.config import DB_PATH, LOTTERY_CONFIG
from app.database import engine, async_session
from app.models.draw import Base
from app.services.import_service import import_github_dataset
from app.services.scraper import rebuild_caches


async def seed(lottery_types: list[str], recreate: bool):
    for lt in lottery_types:
        if lt not in LOTTERY_CONFIG:
            print(f"Unknown lottery type: {lt}")
            print(f"Valid types: {', '.join(LOTTERY_CONFIG.keys())}")
            sys.exit(1)

    # Only delete DB on explicit --recreate
    if recreate and os.path.exists(DB_PATH):
        print(f"Deleting old database: {DB_PATH}")
        os.remove(DB_PATH)

    # Create tables (no-op if they already exist)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    for lottery_type in lottery_types:
        config = LOTTERY_CONFIG[lottery_type]
        print(f"\n=== Importing {lottery_type} ({config['name']}) ===")

        async with async_session() as db:
            print(f"Downloading historical data from {config['data_url']} ...")
            count = await import_github_dataset(db, lottery_type)
            print(f"Imported {count} new draws ({config['name']})")

        async with async_session() as db:
            print("Rebuilding frequency and pair caches...")
            await rebuild_caches(db, lottery_type)
            print("Caches rebuilt successfully")

    print("\nSeed complete!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed lottery database")
    parser.add_argument(
        "--lottery-type",
        default=None,
        choices=list(LOTTERY_CONFIG.keys()),
        help="Lottery type to import (default: marksix if --all not specified)",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Import all supported lottery types",
    )
    parser.add_argument(
        "--recreate",
        action="store_true",
        help="Delete existing database before importing",
    )
    args = parser.parse_args()

    # Determine which lottery types to import
    if args.all:
        lottery_types = list(LOTTERY_CONFIG.keys())
    elif args.lottery_type:
        lottery_types = [args.lottery_type]
    else:
        lottery_types = ["marksix"]

    asyncio.run(seed(lottery_types, args.recreate))
