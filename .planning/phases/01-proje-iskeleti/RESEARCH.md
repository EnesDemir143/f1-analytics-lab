# RESEARCH — Faz 1: Proje İskeleti

**Phase:** 1 | **Researcher:** gsd-phase-researcher | **Date:** 2026-05-27

## Package Legitimacy Gate (slopcheck)

| Package | Source | Stars | Last Release | Verdict |
|---------|--------|-------|-------------|---------|
| pandas | pypi/pandas | 45K+ | Active | ✅ Core |
| numpy | pypi/numpy | 28K+ | Active | ✅ Core |
| fastf1 | theOehrly/Fast-F1 | 2.8K | 2026 | ✅ Domain (F1) |
| scikit-learn | scikit-learn/scikit-learn | 60K+ | Active | ✅ Core ML |
| xgboost | dmlc/xgboost | 26K+ | Active | ✅ Core ML |
| lightgbm | microsoft/LightGBM | 17K+ | Active | ✅ Core ML |
| catboost | catboost/catboost | 8K+ | Active | ✅ Core ML |
| matplotlib | matplotlib/matplotlib | 20K+ | Active | ✅ Viz |
| seaborn | mwaskom/seaborn | 12K+ | Active | ✅ Viz |
| plotly | plotly/plotly.py | 16K+ | Active | ✅ Viz (dashboard) |
| wandb | wandb/wandb | 9K+ | Active | ✅ Tracking |
| pyarrow | apache/arrow | 15K+ | Active | ✅ Parquet I/O |
| pyyaml | yaml/pyyaml | 2.5K+ | Active | ✅ Config |
| jupyter | jupyter/notebook | 12K+ | Active | ✅ Notebook |
| pytest | pytest-dev/pytest | 12K+ | Active | ✅ Test (dev) |

**Verdict:** Tüm paketler well-established, aktif maintenance, güvenli. Slopcheck geçti.

## uv vs pip vs poetry

| | uv | pip | poetry |
|---|----|-----|--------|
| Hız | ⚡ ~10x faster | 🐢 baseline | 🐢 ~pip |
| Lockfile | uv.lock (cross-platform) | requirements.txt | poetry.lock |
| PEP 621 | ✅ native | ❌ | ✅ |
| Install | `curl -LsSf ... | sh` | built-in | `pip install poetry` |

**Karar:** uv. Sebep: hız (Mac'te pandas+numpy kurulumu ~3 sn), PEP 621 uyumlu pyproject.toml, modern.

## Fast-F1 Cache Dizini

Fast-F1 veri indirmek için yerleşik cache kullanır. Default: `~/.fastf1/`
Proje için: `data/raw/fastf1_cache/`

```python
import fastf1
fastf1.Cache.enable_cache('data/raw/fastf1_cache')
```

Cache dizini .gitignore'da olacak (büyük binary dosyalar).

## W&B Setup

```python
import wandb
wandb.init(entity="enesdemir", project="f1-analytics-lab")
```

API key: `~/.netrc` veya `WANDB_API_KEY` env var.
.env dosyasında `WANDB_API_KEY=***` — asla commit'lenmez.

## Config YAML Yapısı

```yaml
# data.yaml
seasons: [2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]
sessions: ["R", "Q", "FP2"]
cache_dir: "data/raw/fastf1_cache"
data_dir: "data"

# features.yaml
active_features:
  lap_level: true
  rolling: true
  tyre: true
  weather: true
  overtake_pair: false   # Faz 6'da aktif
  pit_strategy: false     # Faz 7'de aktif

# models.yaml
classification:
  logistic_regression:
    C: 1.0
    max_iter: 1000
  random_forest:
    n_estimators: 100
    max_depth: 10
  xgboost:
    n_estimators: 100
    max_depth: 6
    learning_rate: 0.1
  lightgbm:
    n_estimators: 100
    num_leaves: 31
    learning_rate: 0.1
  catboost:
    iterations: 100
    depth: 6
    learning_rate: 0.1

regression:
  # aynı model set'i, regressor versiyonları

# wandb.yaml
entity: "enesdemir"
project: "f1-analytics-lab"
log_model: true
log_dataset: true
```

## utils/ Modülleri

- **paths.py:** `get_project_root()` — `pyproject.toml`'ı bularak root döner
- **seed.py:** `set_seed(42)` — random, numpy, torch (varsa)
- **logging.py:** `get_logger(name)` — timestamp'li, hem stdout hem dosya
- **config.py:** `load_config(name)` — YAML oku, `configs/{name}.yaml`

## Riskler

| Risk | Olasılık | Etki | Mitigation |
|------|---------|------|-----------|
| Fast-F1 API değişikliği | Düşük | Orta | Belli bir versiyona pin'le (`fastf1>=3.4,<4`) |
| W&B rate limit | Düşük | Düşük | Free tier 100GB — bu proje için fazlasıyla yeterli |
| uv macOS uyumsuzluğu | Çok düşük | Kritik | pip fallback her zaman mümkün |
