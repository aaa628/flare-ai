"""Data loading for Flare AI.

Rule: the app only ever shows records that have been verified by a second
person (verified_by and verified_date filled in). All statistics are computed
from these records. Nothing is hardcoded.
"""
from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

LABELS = ("measured", "published_conclusion", "our_interpretation")


def _read(name: str) -> pd.DataFrame:
    path = DATA_DIR / name
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path, dtype=str).fillna("")


def load_all_experiments() -> pd.DataFrame:
    return _read("experiments.csv")


def load_verified_experiments() -> pd.DataFrame:
    df = load_all_experiments()
    if df.empty:
        return df
    ok = (df["verified_by"].str.strip() != "") & (df["verified_date"].str.strip() != "")
    return df[ok].reset_index(drop=True)


def load_sources() -> pd.DataFrame:
    return _read("sources.csv")


def overview_stats() -> dict:
    """Every number on the Overview screen comes from here."""
    all_df = load_all_experiments()
    ver = load_verified_experiments()
    src = load_sources()
    return {
        "records_total": len(all_df),
        "records_verified": len(ver),
        "sources": len(src),
        "programs": sorted(ver["program"].unique().tolist()) if len(ver) else [],
        "status": "loaded" if len(ver) else ("no verified records yet" if len(all_df) else "dataset empty"),
    }
