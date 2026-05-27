# CONTEXT — Faz 5: Lap Time Prediction ★★★

**Phase:** 5 | **Status:** locked | **Depends on:** Faz 3 (clean_laps)

## Critical: Leakage
Target `next_lap_time` GELECEK tur. Hiçbir feature gelecek bilgi içeremez.
Weather, track_status, compound değişimi → SADECE şu anki turun.

## Filtre
- is_valid_lap=True
- pit_lap, SC, rain, Lap 1, SON tur ÇIKARILIR

## Scope Fence
Sadece lap time prediction. Diğer task'lar YOK.
