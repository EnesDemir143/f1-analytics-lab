# CONTEXT — Faz 6: Overtake Prediction ★★

**Phase:** 6 | **Status:** locked | **Depends on:** Faz 3 (clean_laps)

## Critical: Class Imbalance
~%25-35 overtake success. PR-AUC > ROC-AUC önemli. `class_weight='balanced'`.

## Window Definition
gap < 1.0s AND chasing car direkt arkasında. Window sonucu: pozisyon değişti mi?

## Scope Fence
Sadece overtake prediction. Lap-level (telemetri YOK).
