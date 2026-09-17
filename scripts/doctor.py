#!/usr/bin/env python3
"""Read-only checks of configuration, database tables, relationships and totals."""
from pathlib import Path
import re
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from lms.config import Settings
from lms.db import Database
from lms.errors import LMSError


def main():
    print("Coursebook / environment check")
    print("Python:",sys.version.split()[0])
    if sys.version_info<(3,11):
        print("Use Python 3.11, 3.12 or 3.13."); return 1
    try:
        cfg=Settings.from_env()
        if not cfg.password or cfg.password.startswith("REPLACE_"):
            print("Set DB_PASSWORD in .env, or run python scripts/setup.py."); return 1
        if cfg.user.lower()=="root":
            print("Warning: configure a restricted application account instead of root.")
        db=Database(cfg)
        health=db.health()
        version=health["server_version"]
        m=re.match(r"(\d+)\.(\d+)\.(\d+)",version)
        if "mariadb" in version.lower() or not m or tuple(map(int,m.groups()))<(8,0,16):
            print("Unsupported server:",version); return 1
        print(f"MySQL: {version} | Database: {health['database_name']} | Account: {health['account']}")
        for table in ("students","instructors","courses","enrollments","grades"):
            n=db.fetch_one(f"SELECT COUNT(*) AS n FROM {table}")["n"]
            print(f"OK {table}: {n} record(s)")
        bad=db.fetch_one("SELECT COUNT(*) AS n FROM grades WHERE total_marks <> assignment_marks + quiz_marks + final_exam_marks")["n"]
        if bad:
            print("FAIL: grade totals are inconsistent."); return 1
        foreign_keys=db.fetch_one("SELECT COUNT(*) AS n FROM information_schema.table_constraints WHERE constraint_schema=%s AND constraint_type='FOREIGN KEY'",(cfg.database,))["n"]
        if foreign_keys<4:
            print("FAIL: expected four foreign keys. Import the supplied schema."); return 1
        print("OK four core foreign keys; stored grade totals agree with assessment marks.")
        print("Data mode:",cfg.data_mode)
        print("Ready: python -m streamlit run app.py")
        return 0
    except (LMSError,ValueError,ImportError) as exc:
        print("Check failed:",exc)
        return 1


if __name__=="__main__":
    raise SystemExit(main())
