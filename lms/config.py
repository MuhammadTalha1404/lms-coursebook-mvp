"""Read configuration once per app rerun. Never cache database passwords in UI."""
from dataclasses import dataclass, field
from pathlib import Path
import os
import re

ROOT = Path(__file__).resolve().parents[1]


def load_environment() -> None:
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env", override=False)


def identifier(value: str) -> str:
    """Database and account names are identifiers, not SQL value parameters."""
    if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]{0,47}", value):
        raise ValueError("Use a name beginning with a letter, then letters, numbers or underscores (48 characters maximum).")
    return value


@dataclass(frozen=True)
class Settings:
    host: str = "127.0.0.1"
    port: int = 3306
    database: str = "lms"
    user: str = "lms_app"
    password: str = field(default="", repr=False)
    ssl_ca: str = ""
    institute: str = "Learning & Training Institute"
    currency: str = "PKR"
    data_mode: str = "sample"
    privacy_contact: str = ""

    @classmethod
    def from_env(cls) -> "Settings":
        load_environment()
        try:
            port = int(os.getenv("DB_PORT", "3306"))
        except ValueError as exc:
            raise ValueError("DB_PORT must be a whole number.") from exc
        if not 1 <= port <= 65535:
            raise ValueError("DB_PORT must be between 1 and 65535.")
        mode = os.getenv("APP_DATA_MODE", "sample").lower().strip()
        if mode not in {"sample", "live"}:
            raise ValueError("APP_DATA_MODE must be sample or live.")
        currency = os.getenv("APP_CURRENCY", "PKR").strip().upper()
        if not re.fullmatch(r"[A-Z]{3}", currency):
            raise ValueError("APP_CURRENCY must be a three-letter currency code.")
        return cls(
            host=os.getenv("DB_HOST", "127.0.0.1").strip(), port=port,
            database=identifier(os.getenv("DB_NAME", "lms")),
            user=os.getenv("DB_USER", "lms_app"), password=os.getenv("DB_PASSWORD", ""),
            ssl_ca=os.getenv("DB_SSL_CA", "").strip(),
            institute=os.getenv("INSTITUTE_NAME", "Learning & Training Institute").strip(),
            currency=currency, data_mode=mode,
            privacy_contact=os.getenv("PRIVACY_CONTACT", "").strip(),
        )

    def connection_args(self, *, include_database: bool = True) -> dict:
        args = dict(host=self.host, port=self.port, user=self.user,
                    password=self.password, connection_timeout=8,
                    charset="utf8mb4", autocommit=False,
                    sql_mode="STRICT_TRANS_TABLES,NO_ZERO_DATE,NO_ZERO_IN_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION,ONLY_FULL_GROUP_BY")
        if include_database:
            args["database"] = self.database
        if self.ssl_ca:
            args.update(ssl_ca=self.ssl_ca, ssl_verify_cert=True, ssl_verify_identity=True)
        return args
