# CONTEXT — Faz 7: Pit Strategy + Anomaly Detection ★★

**Phase:** 7 | **Status:** locked | **Depends on:** Faz 3 (clean_laps, clean_stints)

## İki Alt-Task
1. Pit Strategy (supervised): position_gain > 0 binary
2. Anomaly Detection (unsupervised): 6 tip, ML + statistical + rule-based

## Anomaly: Ensemble
En az 2 yöntem "outlier" dediyse → is_outlier_lap=True. Rule-based öncelikli tip ataması.

## Scope Fence
RL YOK (future work). Driver performance analytics opsiyonel.
