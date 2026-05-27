# RESEARCH — Faz 7: Pit Strategy + Anomaly

## Anomaly Ensemble

```python
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor

iso = IsolationForest(contamination=0.1)
lof = LocalOutlierFactor(contamination=0.1)

# Ensemble: en az 2 oy
methods = ['zscore_3', 'iqr_15', 'iso_forest', 'lof']
df['outlier_votes'] = df[methods].sum(axis=1)
df['is_outlier_lap'] = df['outlier_votes'] >= 2
```

## Pit Position Gain

```python
df['position_gain'] = df['position_before_pit'] - df['position_after_pit']
df['pit_success'] = (df['position_gain'] > 0).astype(int)
```
