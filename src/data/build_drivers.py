"""Build drivers.parquet — driver-team mapping per season."""

from __future__ import annotations

import pandas as pd

from src.data.fetch_fastf1 import iter_sessions
from src.utils.paths import INTERIM_DIR


def build_drivers_dataframe(
    start: int = 2018, end: int = 2026, types: tuple[str, ...] = ("R",)
) -> pd.DataFrame:
    """Build driver-team mapping DataFrame.

    Records each (season, driver) pair with the team they drove for.
    If a driver switched teams mid-season, the last team is kept
    (assumes the most recent race reflects their final team for that season).

    Returns:
        DataFrame with columns: season, driver_code, driver_name, team
    """
    rows: list[dict] = []

    for session in iter_sessions(start, end, types):
        results = session.results
        if results is None or results.empty:
            continue
        season = int(session.event.year)
        for _, r in results.iterrows():
            rows.append(
                {
                    "season": season,
                    "driver_code": r.get("Abbreviation", ""),
                    "driver_name": r.get("BroadcasterName", r.get("FullName", "")),
                    "team": r.get("TeamName", ""),
                }
            )

    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows)
    # Deduplicate: for (season, driver_code) pairs that appear multiple times
    # (driver switched teams), keep the last entry.
    df = df.drop_duplicates(subset=["season", "driver_code"], keep="last")
    df = df.sort_values(["season", "driver_code"]).reset_index(drop=True)
    return df


def build_drivers(
    start: int = 2018, end: int = 2026, types: tuple[str, ...] = ("R",)
) -> None:
    """Build and save drivers.parquet."""
    df = build_drivers_dataframe(start, end, types)
    dst = INTERIM_DIR / "drivers.parquet"
    dst.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(dst, index=False)
    print(f"✓ drivers.parquet — {len(df)} rows → {dst}")


if __name__ == "__main__":
    build_drivers()
