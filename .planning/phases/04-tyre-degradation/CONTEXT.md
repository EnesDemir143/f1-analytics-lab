# CONTEXT — Faz 4: Tyre Degradation ★★★

**Phase:** 4 | **Status:** locked | **Depends on:** Faz 3 (clean_laps, clean_stints)

## Per-Task Pipeline
İlk per-task faz. Bu fazda: EDA → Outlier → Feature Eng → Dataset → Model Train → Evaluate.

## Critical Decisions

### D-03: Temporal Split
Train: 2018-2022 | Val: 2023 | Test: 2024-2026. Bu split'in uygulanacağı ilk faz.

### Target: lap_time_delta
Stint-opening pace'ten sapma (saniye). Stint başındaki ilk geçerli tur referans alınır.

### Hangi lap'ler kullanılır?
- is_valid_lap=True
- is_pit_lap, is_sc_lap, is_rain_lap ÇIKARILIR
- Lap 1 ÇIKARILIR (start chaos)

## Scope Fence
Sadece tyre degradation. Lap time prediction, overtake, pit strategy bu fazda YOK.
