# RESEARCH — Faz 4: Tyre Degradation

## Degradation Curve Fitting

```python
from scipy.optimize import curve_fit

def linear_degradation(tyre_age, base_pace, deg_rate):
    return base_pace + deg_rate * tyre_age

def exponential_degradation(tyre_age, base_pace, deg_rate, exp_factor):
    return base_pace + deg_rate * tyre_age ** exp_factor
```

## Target Calculation

```python
def compute_lap_time_delta(df):
    # Her stint için opening pace (ilk 3 geçerli turun median'ı)
    opening_pace = df.groupby(['season','round','driver','stint'])['lap_time']\
                     .transform(lambda x: x.head(3).median())
    df['lap_time_delta'] = df['lap_time'] - opening_pace
    return df
```

## Feature: Fuel Proxy

```python
# Yakıt etkisi: F1'de ~0.03s/lap per lap of fuel
df['fuel_proxy'] = df['race_progress'] * 0.03 * df['total_laps']
```

## Package Check

| Package | Need | Status |
|---------|------|--------|
| scipy | curve_fit, zscore | ✅ Faz 1'de eklendi |
| scikit-learn | RF, Ridge, Lasso | ✅ |
| xgboost, lightgbm, catboost | Regressors | ✅ |

## Riskler
- Eski sezonlarda compound UNKNOWN → bu örnekler drop
- Stint boundary detection: compound değişimi + pit flag
- Multi-stint yarışlarda stint numarası doğru tespit edilmeli
