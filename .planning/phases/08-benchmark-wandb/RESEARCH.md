# RESEARCH — Faz 8: Benchmark + W&B

## W&B Report API

```python
# Panels: line, bar, run_comparison, custom_chart, custom_chart_table
wandb_report = wandb.init(project="f1-analytics-lab", job_type="report")

# Markdown report
report_text = """
# F1 Analytics Lab — Comprehensive Benchmark
## Overview
...
## Classification Results
...
"""
```

## Benchmark Table Format (Markdown)

GitHub README'ye gömülecek tablo:
```markdown
| Task | Model | ROC-AUC | F1 | MAE | R² | Train Time |
|------|-------|---------|-----|-----|-----|------------|
| overtake | LightGBM | 0.85 | 0.64 | — | — | 8s |
| tyre | CatBoost | — | — | 0.12 | 0.78 | 90s |
```

## Domain Generalization Test Design

**Circuit holdout:** Monza, Silverstone, Spa → train'de 0 örnek
**Driver leakage:** Model A (driver+team var) vs Model B (yok) → Δ > %10 = shortcut

## Riskler
- W&B rate limit: Free tier 100GB, proje ~100MB → sorun değil
- Report rendering: WandB markdown büyük tablolarda yavaş → tablo limit 20 satır
