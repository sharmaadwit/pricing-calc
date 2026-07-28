#!/usr/bin/env python3
"""
Refresh PostgreSQL collation version after a Railway/host libc upgrade.

Run once against production (requires DATABASE_URL or default Railway URL in app.py):
  python3 scripts/fix_postgres_collation.py

Idempotent: safe to re-run if already at 2.41.
"""
from __future__ import annotations

import os
import sys

from sqlalchemy import create_engine, text

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

DEFAULT_URI = (
    "postgresql://postgres:prdeuXwtBzpLZaOGpxgRspfjfLNEQrys@gondola.proxy.rlwy.net:25504/railway"
)


def main() -> int:
    uri = os.environ.get("DATABASE_URL", DEFAULT_URI)
    engine = create_engine(uri, isolation_level="AUTOCOMMIT")
    with engine.connect() as conn:
        before = conn.execute(
            text("SELECT datcollversion FROM pg_database WHERE datname = current_database()")
        ).scalar()
        print(f"Collation version before: {before}")

        conn.execute(text("ALTER DATABASE railway REFRESH COLLATION VERSION"))

        after = conn.execute(
            text("SELECT datcollversion FROM pg_database WHERE datname = current_database()")
        ).scalar()
        print(f"Collation version after:  {after}")

        tables = conn.execute(
            text(
                "SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename"
            )
        ).scalars().all()
        for table in tables:
            conn.execute(text(f'REINDEX TABLE public."{table}"'))
            print(f"Reindexed public.{table}")

    print("Done. New connections should not emit collation mismatch warnings.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
