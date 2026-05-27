# RESEARCH — Faz 6: Overtake Prediction

## Imbalance Handling

```python
# LightGBM
LGBMClassifier(class_weight='balanced', ...)
# XGBoost
XGBClassifier(scale_pos_weight=sum(neg)/sum(pos), ...)
# CatBoost
CatBoostClassifier(auto_class_weights='Balanced', ...)
```

## PR-AUC vs ROC-AUC

```python
from sklearn.metrics import precision_recall_curve, auc
precision, recall, _ = precision_recall_curve(y_true, y_pred_proba)
pr_auc = auc(recall, precision)
```

## Window Detection (lap-level)

```python
# Her tur için: driver pozisyonundan chasing-ahead pair'leri bul
# gap hesapla (tam değil, lap_time farkından approximate)
```
