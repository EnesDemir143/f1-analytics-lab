# RESEARCH — Faz 3: Veri Temizleme + Flag'ler

**Phase:** 3

## Z-Score Outlier Detection

```python
from scipy import stats

def flag_outliers_zscore(df, group_cols=['driver', 'circuit'], 
                         value_col='lap_time', threshold=3):
    """Per-group Z-score outlier flagging."""
    df['z_score'] = df.groupby(group_cols)[value_col].transform(
        lambda x: stats.zscore(x, nan_policy='omit')
    )
    df['is_outlier_lap'] = df['z_score'].abs() > threshold
    return df
```

## Duplicate Detection

```python
def find_duplicates(df, subset, keep='first'):
    dups = df.duplicated(subset=subset, keep=False)
    dup_df = df[dups].sort_values(subset)
    # Log duplicates
    print(f"Found {dup_df.shape[0]} duplicate rows in {subset}")
    return df.drop_duplicates(subset=subset, keep=keep)
```

## Missing Data Pattern Analysis

```python
def missing_report(df, name):
    missing = df.isnull().sum()
    missing_pct = (missing / len(df) * 100).round(2)
    report = pd.DataFrame({
        'column': missing.index,
        'missing_count': missing.values,
        'missing_pct': missing_pct.values
    }).query('missing_count > 0').sort_values('missing_count', ascending=False)
    print(f"\n=== {name} Missing Data ===")
    print(report.to_string(index=False))
    return report
```

## Compound Enum Validation

```python
VALID_COMPOUNDS = {'SOFT', 'MEDIUM', 'HARD', 'INTERMEDIATE', 'WET', 'UNKNOWN', 'TEST'}
# UNKNOWN = eski sezon, TEST = test lastiği
```

## Riskler

| Risk | Mitigation |
|------|-----------|
| Eski sezon track_status null | is_sc_lap vb. için null → False |
| Z-score division by zero (tek örnek) | min 5 örnek şartı, else NaN → False |
| Çok fazla duplicate | Log'la, manuel review gerekirse flag'le |
