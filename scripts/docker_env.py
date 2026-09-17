#!/usr/bin/env python3
"""Generate fresh Docker-only credentials without storing any root login supplied by a user."""
import argparse
from pathlib import Path
import secrets

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument("--sample",action="store_true",help="Use fictional sample data via compose.sample.yaml.")
args=parser.parse_args()
root=Path(__file__).resolve().parents[1]
path=root/".env"
if path.exists():
    raise SystemExit(".env already exists. It has not been overwritten. See the Docker section in README.md.")
mode="sample" if args.sample else "live"
path.write_text(f"""# Generated local Docker credentials. Do not commit this file.
DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=lms
DB_USER=lms_app
DB_PASSWORD={secrets.token_urlsafe(32)}
MYSQL_ROOT_PASSWORD={secrets.token_urlsafe(40)}
DB_SSL_CA=
INSTITUTE_NAME=Learning & Training Institute
APP_CURRENCY=PKR
APP_DATA_MODE={mode}
PRIVACY_CONTACT=
""",encoding="utf-8")
path.chmod(0o600)
print("Created .env with random, separate application and MySQL root passwords.")
print("docker compose -f compose.yaml -f compose.sample.yaml up --build" if args.sample else "docker compose up --build")
