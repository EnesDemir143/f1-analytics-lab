# F1 Analytics Lab

Formula 1 verisini ham halinden alıp temizleyen, 6 farklı ML task'ı için dataset üreten, EDA/outlier analizi yapan, 5+ modeli benchmark'layan ve sonuçları HF/Kaggle/W&B'de yayınlayan veri bilimi laboratuvarı.

## Datasets

| Dataset | Kaynak | Sezonlar |
|---------|--------|----------|
| Lap times | Fast-F1 | 2018-2026 |
| Qualifying | Fast-F1 | 2018-2026 |
| Weather | Fast-F1 | 2018-2026 |
| Circuit metadata | Manuel | All |

## Pipeline

```
data/raw/ → data/interim/ → data/processed/ → models/ → eval/
   ↑            ↑                ↑               ↑          ↑
 Fast-F1    Cleaning       Feature Eng.     Training    W&B Track
```

## ML Tasks

1. **Tyre Degradation** — Lap-time stint curve fitting
2. **Lap Time Prediction** — Driver/track/compound regression
3. **Overtake Prediction** — Binary classification (DRS zone window)
4. **Pit Strategy** — Optimal stop timing
5. **Qualifying Performance** — Gap-to-teammate regression
6. **Anomaly Detection** — Unusual lap/race flagging

## Quick Start

```bash
# Install uv (if not already)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and setup
git clone https://github.com/EnesDemir143/f1-analytics-lab.git
cd f1-analytics-lab
uv sync

# Verify
uv run python -c "import fastf1; print('Fast-F1 ready')"
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Data | Fast-F1, Pandas, NumPy |
| ML | Scikit-learn, XGBoost, LightGBM, CatBoost |
| Tracking | Weights & Biases |
| Viz | Matplotlib, Seaborn, Plotly |
| Package | uv |

## Project Structure

```
f1-analytics-lab/
├── configs/          # YAML configurations
├── data/
│   ├── raw/          # Fast-F1 downloads (gitignored)
│   ├── interim/      # Cleaned intermediates (gitignored)
│   ├── processed/    # ML-ready datasets
│   └── external/     # Manual metadata
├── notebooks/        # Jupyter notebooks
├── scripts/          # Pipeline scripts
├── src/
│   ├── data/         # Data loading & cleaning
│   ├── features/     # Feature engineering
│   ├── models/       # Model training & eval
│   ├── tasks/        # Task-specific pipelines
│   ├── visualization/# EDA & plotting
│   └── utils/        # Shared utilities
└── pyproject.toml
```

## License

MIT
