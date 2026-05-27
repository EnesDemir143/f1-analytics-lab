# F1 Analytics Lab

**Dataset Collection, EDA, Outlier Analysis & ML Benchmarks from Formula 1 Telemetry**

## Project Identity

| Alan | Değer |
|------|-------|
| GitHub | enesdemir/f1-analytics-lab |
| HF Dataset | enesdemir/f1-analytics-dataset |
| Kaggle | enesdemir143/f1-analytics-dataset |
| W&B | enesdemir/f1-analytics-lab |
| Author | Enes Demir (230202066) |
| License | MIT |

## One-Liner

Formula 1 verisini ham halinden alıp temizleyen, 6 farklı ML task'ı için dataset üreten, EDA/outlier analizi yapan, 5+ modeli benchmark'layan ve sonuçları HF/Kaggle/W&B'de yayınlayan veri bilimi laboratuvarı.

## Motivation

F1 verisi inanılmaz zengin ama son derece dağınık. Mevcut projeler ya saf görselleştirme aracı ya da tek bir probleme odaklı. Bu proje:

- Sistematik veri temizleme pipeline'ı kurar
- 6 farklı ML problemi için task-spesifik dataset üretir
- Kapsamlı EDA ve outlier analizi yapar
- Domain generalization split stratejileri uygular
- Reproducible benchmark sonuçları yayınlar

## Core Decisions

| ID | Karar | Tarih |
|----|-------|-------|
| D-01 | **Lap-level öncelikli.** Telemetri sadece overtake penceresi için Faz 4'te. | 2026-05-27 |
| D-02 | **Arayüz son fazda.** Ana ürün dataset ve benchmark, dashboard değil. | 2026-05-27 |
| D-03 | **Temporal split ana split.** Circuit holdout ek deney. Driver/team leakage testi. | 2026-05-27 |
| D-04 | **Outlier silinmez, flag'lenir.** Her task kendi filtresini uygular. | 2026-05-27 |
| D-05 | **RL Faz 2'de.** İlk faz supervised modeller. | 2026-05-27 |
| D-06 | **uv paket yöneticisi.** Hızlı, modern Python environment. | 2026-05-27 |
| D-07 | **Per-task faz yapısı.** Her task: veri → EDA → outlier → feature → dataset → model → evaluate | 2026-05-27 |

## Tech Stack

| Katman | Teknoloji |
|--------|-----------|
| Veri | Fast-F1, Pandas, NumPy |
| ML | Scikit-learn, XGBoost, LightGBM, CatBoost |
| Outlier | Z-score, IQR, Isolation Forest, LOF, DBSCAN |
| Tracking | Weights & Biases |
| Dataset | HuggingFace Hub, Kaggle API |
| Viz | Matplotlib, Seaborn, Plotly |
| Dashboard | Streamlit (Faz 10) |
| Package | uv |

## Key Constraints

- **Bedava altyapı:** HF CPU Space, Kaggle, GitHub Actions free tier
- **GPU yok:** Tüm modeller CPU'da eğitilebilir olmalı (tabular ML, derin öğrenme değil)
- **Reproducible:** Tek komutla baştan sona çalışabilmeli
- **Public:** Tüm dataset ve sonuçlar açık

## Reference Docs

- Tasarım dökümanı: `docs/f1-analytics-platform.md`
- Fast-F1: https://github.com/theOehrly/Fast-F1
- StratLab (referans): https://github.com/VforVitorio/F1-StratLab
