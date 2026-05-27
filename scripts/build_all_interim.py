#!/usr/bin/env python3
"""End-to-end data pipeline: fetch → build → validate.

Usage:
    uv run scripts/build_all_interim.py                        # all race sessions
    uv run scripts/build_all_interim.py --years 2024 2024      # single year
    uv run scripts/build_all_interim.py --types R Q            # race + quali only
"""

from __future__ import annotations

import argparse
import time

from src.data.build_circuits import build_circuits
from src.data.build_drivers import build_drivers
from src.data.build_laps import build_laps
from src.data.build_sessions import build_sessions
from src.data.build_stints import build_stints
from src.data.build_track_status import build_track_status
from src.data.build_weather import build_weather
from src.data.fetch_fastf1 import _ensure_cache
from src.data.validators import validation_report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build all interim datasets from Fast-F1")
    parser.add_argument(
        "--years",
        type=int,
        nargs=2,
        default=(2018, 2026),
        metavar=("START", "END"),
        help="Season range (default: 2018 2026)",
    )
    parser.add_argument(
        "--types",
        type=str,
        nargs="+",
        default=["R"],
        choices=["R", "Q", "FP2", "S"],
        help="Session types (default: R)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    start, end = args.years
    types = tuple(args.types)

    print("=" * 55)
    print("  F1 Analytics Lab — Interim Data Pipeline")
    print(f"  Seasons: {start}-{end} | Types: {', '.join(types)}")
    print("=" * 55)

    # Ensure cache is initialised
    _ensure_cache()

    total_start = time.time()

    # Ordered pipeline — each step reads data freshly via fetch_fastf1 iter_sessions
    steps = [
        ("sessions", lambda: build_sessions(start, end, types)),
        ("laps", lambda: build_laps(start, end, types)),
        ("stints", lambda: build_stints(start, end, types)),
        ("weather", lambda: build_weather(start, end, types)),
        ("track_status", lambda: build_track_status(start, end, types)),
        ("drivers", lambda: build_drivers(start, end, types)),
        ("circuits", lambda: build_circuits(start, end, types)),
    ]

    step_times: list[tuple[str, float]] = []
    for name, step_fn in steps:
        s = time.time()
        print(f"\n── {name} ──")
        step_fn()
        elapsed = time.time() - s
        step_times.append((name, elapsed))

    # Validation
    print("\n" + "=" * 55)
    print("  Validation")
    print("=" * 55)
    print(validation_report())

    total_elapsed = time.time() - total_start
    print(f"\nPipeline complete in {total_elapsed:.1f}s")

    # Timing summary
    print("\n── Timing ──")
    for name, t in step_times:
        print(f"  {name:15s}  {t:.1f}s")


if __name__ == "__main__":
    main()
