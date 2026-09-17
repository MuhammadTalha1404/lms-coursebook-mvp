"""Pandas CSV export with spreadsheet-formula injection protection."""
from decimal import Decimal
import pandas as pd


def safe_csv(frame: pd.DataFrame) -> bytes:
    def safe(value):
        if isinstance(value, str) and value.lstrip().startswith(("=", "+", "-", "@", "\t", "\r")):
            return "'" + value
        if isinstance(value, str) and value.startswith(("\t", "\r")):
            return "'" + value
        return value
    clean = frame.map(safe)
    return clean.to_csv(index=False, lineterminator="\n").encode("utf-8-sig")


def display_frame(rows: list[dict], columns: dict[str, str] | None = None) -> pd.DataFrame:
    frame = pd.DataFrame(rows)
    if columns:
        frame = frame.reindex(columns=list(columns)).rename(columns=columns)
    return frame.map(lambda value: float(value) if isinstance(value, Decimal) else value)
