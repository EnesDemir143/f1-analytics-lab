# Requirements — F1 Analytics Lab

## R1: Data Pipeline

### R1.1 Fast-F1 Extraction
- 2018-2026 arası tüm race session'larını çek
- Session, lap, stint, weather, track_status, pit_stop, driver, circuit tablolarını oluştur
- Fast-F1 cache mekanizmasını kullan (tekrar indirme yok)

### R1.2 Data Cleaning
- Eksik/bozuk verileri tespit et ve işaretle
- Flag sütunları ekle: is_pit_lap, is_sc_lap, is_vsc_lap, is_yellow_flag_lap, is_rain_lap
- is_valid_lap kural seti uygula
- Duplicate kontrolü
- Schema validation (her Parquet için)

### R1.3 Data Storage
- `data/raw/` → Fast-F1 cache
- `data/interim/` → Temizlenmiş ortak tablolar (Parquet)
- `data/processed/` → Task-spesifik ML datasetleri (Parquet)

## R2: EDA & Outlier Analysis

### R2.1 EDA
- Genel EDA: sezon/pist/compound dağılımları
- Tyre EDA: degradation curves, compound comparison, track temp vs degradation
- Overtake EDA: gap analizi, DRS etkisi, success rate
- Lap time EDA: valid/invalid, pit/SC/rain etkisi

### R2.2 Outlier Analysis
- 6+ outlier tipi tespit et: pit lap, SC, VSC, rain, damage/spin, abnormal degradation, abnormal sector split
- Rule-based + statistical + ML (Isolation Forest, LOF, DBSCAN) yöntemleri
- Her outlier için: score, type, reason, features_at_time
- Outlier raporu üret

## R3: Dataset Factory

### R3.1 Datasets

| # | Dataset | Task | Target | Öncelik |
|---|---------|------|--------|---------|
| 1 | f1_tyre_degradation | Regression | lap_time_delta | ★★★ |
| 2 | f1_lap_time_prediction | Regression | next_lap_time | ★★★ |
| 3 | f1_overtake_prediction | Binary CLF | overtake_success | ★★ |
| 4 | f1_pit_strategy | Binary CLF | position_gain | ★★ |
| 5 | f1_anomaly_events | Unsupervised | outlier_type | ★ |
| 6 | f1_driver_performance | Analytics | normalized_pace | ★ |

### R3.2 Dataset Requirements
- Her dataset için train/val/test split (temporal: 2018-22 / 2023 / 2024-26)
- Circuit holdout split (ek deney)
- Leakage audit (gelecek bilgisi feature'a sızmamalı)
- Dataset card (schema, target, features, limitations, leakage warnings)
- Task-spesifik filtreleme (örn: tyre degradation için pit/SC/rain lap'leri çıkar)

## R4: Feature Engineering

### R4.1 Feature Types
- Lap-level: lap_time, sector_times, compound, tyre_life, stint, position
- Rolling: prev_N_lap_mean, rolling_std, pace_trend
- Tyre: compound_encoded, tyre_age_normalized, degradation_rate, tyre_age_x_track_temp
- Weather: air_temp, track_temp, humidity, headwind_component, weather_change_flag
- Overtake pair: gap_s, speed_delta, closing_rate, tyre_age_delta, compound_advantage, DRS zone
- Pit strategy: gap_to_ahead/behind, compound_before/after, tyre_age_before_pit

### R4.2 Leakage Control
- Feature üretirken gelecek tur/sezon bilgisi kullanılmamalı
- Her dataset için leakage audit raporu

## R5: ML Benchmarks

### R5.1 Classification
- Logistic Regression, Random Forest, XGBoost, LightGBM, CatBoost
- Metrikler: ROC-AUC, PR-AUC, F1, Precision, Recall, Brier Score, Calibration

### R5.2 Regression
- Linear, Ridge, Lasso, Random Forest, XGBoost, LightGBM, CatBoost
- Metrikler: MAE, RMSE, R², MAPE, Residual plots

### R5.3 W&B Integration
- Her run: config, metrics, feature importance, confusion matrix, calibration, residuals
- Artifact: model + dataset
- Report: tüm benchmark sonuçları

## R6: Publishing

### R6.1 HuggingFace
- Dataset: enesdemir/f1-analytics-dataset (6 config, train/val/test split)
- Dataset card: schema, features, target, limitations, citation

### R6.2 Kaggle
- Dataset: enesdemir143/f1-analytics-dataset
- Example usage notebook

### R6.3 GitHub
- README: proje açıklaması, EDA figürleri, benchmark tablosu, how to reproduce
- Badge'ler: HF, Kaggle, W&B, license

## R7: Dashboard (Faz 10)

- Streamlit / HF Space
- Sayfalar: Dataset Explorer, EDA Dashboard, Outlier Explorer, Model Benchmark, Overtake Demo, Tyre Explorer
- HF Space deploy (CPU Basic — BEDAVA)

## R8: Non-Functional

- **Reproducibility:** Tek komutla (`uv run scripts/build_all.py`) baştan sona
- **Performance:** CPU'da makul sürede (tek seferlik run < 30 dk)
- **Portability:** uv ile her ortamda aynı
- **Documentation:** Her fonksiyon docstring, her dataset dataset card
