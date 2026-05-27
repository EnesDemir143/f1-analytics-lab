"""Build circuits.parquet — circuit metadata with DRS zone info."""

from __future__ import annotations

import pandas as pd

from src.data.fetch_fastf1 import iter_sessions
from src.utils.paths import EXTERNAL_DIR, INTERIM_DIR


def build_circuits_dataframe(
    start: int = 2018, end: int = 2026, types: tuple[str, ...] = ("R",)
) -> pd.DataFrame:
    """Build circuit metadata DataFrame.

    1. Collects circuit info from session events across all seasons.
    2. Merges DRS zone data from external CSV (if available).

    Returns:
        DataFrame with columns:
            circuit_name, country, num_laps (approximate from event),
            drs_zones (count), drs_zone_lengths (list, from external CSV)
    """
    circuit_rows: dict[str, dict] = {}

    for session in iter_sessions(start, end, types):
        event = session.event
        circuit_name = event.get("EventName", "")
        if not circuit_name or circuit_name in circuit_rows:
            continue

        country = event.get("Country", "")
        # Estimate total laps from the session object
        laps_est = 0
        try:
            total_laps = session.total_laps
            if total_laps:
                laps_est = int(total_laps)
        except (AttributeError, ValueError, TypeError):
            pass

        circuit_rows[circuit_name] = {
            "circuit_name": circuit_name,
            "country": country,
            "num_laps": laps_est,
        }

    df = pd.DataFrame(list(circuit_rows.values()))

    # ── Merge DRS zone data from external CSV ──────────────────────
    drs_path = EXTERNAL_DIR / "circuit_drs_zones.csv"
    if drs_path.exists():
        drs_df = pd.read_csv(drs_path)
        # Expect columns: circuit_name, drs_zones, drs_zone_lengths (comma-sep)
        if "circuit_name" in drs_df.columns:
            df = df.merge(drs_df, on="circuit_name", how="left")

    return df


def build_circuits(
    start: int = 2018, end: int = 2026, types: tuple[str, ...] = ("R",)
) -> None:
    """Build and save circuits.parquet."""
    df = build_circuits_dataframe(start, end, types)
    dst = INTERIM_DIR / "circuits.parquet"
    dst.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(dst, index=False)
    print(f"✓ circuits.parquet — {len(df)} rows → {dst}")


if __name__ == "__main__":
    build_circuits()
