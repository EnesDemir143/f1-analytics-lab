# RESEARCH — Faz 5: Lap Time Prediction

## Leakage-Safe Feature Engineering

```python
# DOĞRU: sadece GEÇMİŞ turları kullan
df['prev_3_mean'] = df.groupby('driver')['lap_time'].transform(
    lambda x: x.shift(1).rolling(3).mean()
)
# shift(1) → bir önceki turdan başla, şu anki tur dahil DEĞİL

# YANLIŞ (leakage):
df['next_weather'] = df.groupby('driver')['track_temp'].shift(-1)  # GELECEK!
```

## Time-Series CV

```python
from sklearn.model_selection import TimeSeriesSplit
tscv = TimeSeriesSplit(n_splits=3)
# Sezon içi sıralı split
```
