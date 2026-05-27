# ROADMAP — F1 Analytics Lab

**Granularity:** standard (10 faz) | **Per-task pipeline:** her task kendi veri→model döngüsünü takip eder.

```
Faz 1-3:   ORTAK ALTYAPI (tüm task'lar için bir kere)
    │
    ├── Faz 1: Proje iskeleti
    ├── Faz 2: Veri toplama pipeline'ı
    └── Faz 3: Veri temizleme + flag'ler + validasyon
    │
    ▼
Faz 4-7:   PER-TASK PIPELINE (her task bağımsız)
    │
    ├── Faz 4: Tyre Degradation ★★★
    │     EDA → Outlier → Feature Eng → Dataset → Model → Evaluate
    │
    ├── Faz 5: Lap Time Prediction ★★★
    │     EDA → Outlier → Feature Eng → Dataset → Model → Evaluate
    │
    ├── Faz 6: Overtake Prediction ★★
    │     EDA → Outlier → Feature Eng → Dataset → Model → Evaluate
    │
    └── Faz 7: Pit Strategy + Anomaly ★★
          EDA → Outlier → Feature Eng → Dataset → Model → Evaluate
    │
    ▼
Faz 8-10:  ENTEGRASYON & YAYIN
    │
    ├── Faz 8: Benchmark + W&B report
    ├── Faz 9: Yayın (HF Dataset, Kaggle, README)
    └── Faz 10: Showcase Dashboard
```

---

## Faz Detayları

### ~~Faz 1 — Proje İskeleti~~ ✅

**Amaç:** Çalıştırılabilir boş proje. Tek bir `uv run` ile "hello world" verir.

```
Çıktılar:
  - repo: f1-analytics-lab (GitHub) ✅
  - pyproject.toml + uv.lock ✅
  - configs/ (data.yaml, features.yaml, models.yaml, wandb.yaml) ✅
  - src/ dizin iskeleti (tüm __init__.py'ler) ✅
  - data/ klasör yapısı (raw, interim, processed, external) ✅
  - .gitignore, .env.example, README taslağı ✅
  - W&B project: enesdemir/f1-analytics-lab — kullanıcı tarafından oluşturulacak
```

**Tamamlanma:** 2026-05-27

### Faz 2 — Veri Toplama Pipeline'ı

**Amaç:** Fast-F1'den 2018-2026 sezon verilerini çek, interim Parquet olarak kaydet.

```
Çıktılar:
  - src/data/fetch_fastf1.py — session iterator
  - src/data/build_sessions.py → interim/sessions.parquet
  - src/data/build_laps.py → interim/laps.parquet
  - src/data/build_stints.py → interim/stints.parquet
  - src/data/build_weather.py → interim/weather.parquet
  - src/data/build_track_status.py → interim/track_status.parquet
  - src/data/build_drivers.py → interim/drivers.parquet
  - src/data/build_circuits.py → interim/circuits.parquet
  - src/data/validators.py — schema validation
```

### Faz 3 — Veri Temizleme + Flag'ler

**Amaç:** Ham veriyi flag'le, validate et, temizle.

```
Çıktılar:
  - Eksik veri analizi ve raporu
  - Flag sütunları: is_pit_lap, is_sc_lap, is_vsc_lap, is_yellow_flag_lap,
    is_rain_lap, is_valid_lap, is_deleted, is_outlier_lap
  - is_valid_lap kural seti
  - Duplicate kontrolü ve temizliği
  - Schema validation (her Parquet)
  - data/interim/clean_laps.parquet, clean_stints.parquet, clean_weather.parquet
  - Notebook: 02_data_cleaning.ipynb
```

### Faz 4 — Tyre Degradation ★★★

**Amaç:** Lastik aşınma verisini anla, outlier'ları bul, feature üret, dataset oluştur, model eğit ve değerlendir.

```
Pipeline:
  EDA → Outlier → Feature Engineering → Dataset → Model Train → Evaluate

Çıktılar:
  - EDA: compound bazlı degradation curves, track temp vs degradation,
    circuit bazlı farklar, stint başı/sonu pace analizi
  - Outlier: aşırı degradation tespiti, anormal stint davranışı
  - Features: compound_encoded, tyre_age_normalized, degradation_rate,
    tyre_age_x_track_temp, rolling pace features
  - Dataset: data/processed/f1_tyre_degradation/ (train/val/test.parquet)
  - Models: Linear, Ridge, Lasso, RF, XGBoost, LightGBM, CatBoost
  - Metrics: MAE, RMSE, R², MAPE, per-compound error, per-circuit error
  - Notebook: 07_tyre_degradation_dataset.ipynb
  - src/tasks/tyre_degradation/ (build_dataset.py, train.py, evaluate.py)
```

### Faz 5 — Lap Time Prediction ★★★

**Amaç:** Bir sonraki tur süresini tahmin et. Time-series forecasting, leakage kontrolü kritik.

```
Pipeline:
  EDA → Outlier → Feature Engineering → Dataset → Model Train → Evaluate

Çıktılar:
  - EDA: lap time dağılımları, valid/invalid, pit/SC/rain etkisi
  - Outlier: anormal sector split, aşırı yavaş/hızlı turlar
  - Features: rolling mean/std (prev_3, prev_5), pace_trend,
    race_progress, weather features
  - Dataset: data/processed/f1_lap_time_prediction/ (train/val/test.parquet)
  - Leakage audit: gelecek bilgisi sızmadığına dair rapor
  - Models: Linear, Ridge, Lasso, RF, XGBoost, LightGBM, CatBoost
  - Metrics: MAE, RMSE, R², MAPE, residual analizi
  - Notebook: 08_lap_time_dataset.ipynb
  - src/tasks/lap_time_prediction/ (build_dataset.py, train.py, evaluate.py)
```

### Faz 6 — Overtake Prediction ★★

**Amaç:** Takip eden araç önündekini geçecek mi? Binary classification, class imbalance.

```
Pipeline:
  EDA → Outlier → Feature Engineering → Dataset → Model Train → Evaluate

Çıktılar:
  - EDA: pistlere göre overtake penceresi, gap < 1s başarı oranı,
    DRS etkisi, speed delta etkisi, compound advantage etkisi
  - Features: gap_s, gap_trend, speed_delta_kmh, closing_rate_ms,
    tyre_age_delta, compound_advantage, drs_available, drs_zone_length_m
  - Dataset: data/processed/f1_overtake_prediction/ (train/val/test.parquet)
    ~5000 overtake penceresi, class imbalance not edilmiş
  - Models: Logistic Regression, RF, XGBoost, LightGBM, CatBoost
  - Metrics: ROC-AUC, PR-AUC, F1, Precision, Recall, Brier, Calibration
  - Notebook: 09_overtake_dataset.ipynb
  - src/tasks/overtake_prediction/ (build_dataset.py, train.py, evaluate.py)
```

### Faz 7 — Pit Strategy + Anomaly Detection ★★

**Amaç:** Pit sonrası pozisyon kazancını tahmin et (binary CLF) + outlier detection pipeline'ını tamamla.

```
Pipeline:
  EDA → Outlier → Feature Engineering → Dataset → Model Train → Evaluate

Çıktılar:
  - Pit Strategy EDA: pit zamanlaması, compound değişimi, undercut analizi
  - Pit Features: gap_to_ahead/behind, compound_before/after,
    tyre_age_before_pit, position_before/after_pit
  - Dataset: data/processed/f1_pit_strategy/ (train/val/test.parquet)
  - Models: Logistic Regression, RF, XGBoost, LightGBM, CatBoost
  - Anomaly dataset: data/processed/f1_anomaly_events/all.parquet
  - Outlier methods: Z-score, IQR, Isolation Forest, LOF, DBSCAN
  - Notebooks: 10_pit_strategy_dataset.ipynb, 06_outlier_analysis.ipynb
  - src/tasks/pit_strategy/, src/tasks/anomaly_detection/
```

### Faz 8 — Benchmark + W&B Report

**Amaç:** Tüm modelleri karşılaştır, W&B'de comprehensive report oluştur.

```
Çıktılar:
  - Benchmark tablosu: tüm task'lar × tüm modeller × metrikler (markdown)
  - Feature importance analizi (her task için top-10 feature)
  - Calibration analizi (classification task'ları)
  - Residual analizi (regression task'ları)
  - Circuit holdout split sonuçları
  - Driver/team leakage test sonuçları
  - W&B report: f1-analytics-lab comprehensive benchmark
  - reports/model_benchmark_report.md
  - Notebook: 11_model_benchmarks.ipynb, 12_results_summary.ipynb
```

### Faz 9 — Yayın

**Amaç:** Dataset ve sonuçları public hale getir.

```
Çıktılar:
  - HF Dataset: enesdemir/f1-analytics-dataset (6 config, train/val/test)
  - Kaggle Dataset: enesdemir143/f1-analytics-dataset
  - Dataset card (her config için README)
  - Example usage notebook (Kaggle'da)
  - GitHub README final: EDA figürleri, benchmark tablosu, badge'ler
  - scripts/publish_all.py (tek komutla tüm yayın)
```

### Faz 10 — Showcase Dashboard

**Amaç:** Projeyi interaktif vitrin olarak sergile.

```
Çıktılar:
  - Streamlit app: app/streamlit_app.py
  - Sayfalar: Dataset Explorer, EDA Dashboard, Outlier Explorer,
    Model Benchmark, Overtake Demo, Tyre Degradation Explorer
  - HF Space deploy: enesdemir/f1-analytics-lab
  - app/requirements.txt (streamlit, plotly, pandas, fastf1)
```

---

## Bağımlılık Grafiği

```
Faz 1 ──→ Faz 2 ──→ Faz 3
                     │
         ┌───────────┼───────────┬───────────┐
         ▼           ▼           ▼           ▼
       Faz 4       Faz 5       Faz 6       Faz 7
         │           │           │           │
         └───────────┴───────────┴───────────┘
                     │
                     ▼
                   Faz 8
                     │
                     ▼
                   Faz 9
                     │
                     ▼
                  Faz 10
```

Faz 4-7 birbirinden bağımsız, paralel çalışabilir.

---

## Tahmini Süre

| Faz | Tahmin |
|-----|--------|
| Faz 1: İskelet | 2-3 gün |
| Faz 2: Veri toplama | 3-5 gün |
| Faz 3: Temizleme | 2-3 gün |
| Faz 4: Tyre Deg. | 5-7 gün |
| Faz 5: Lap Time | 5-7 gün |
| Faz 6: Overtake | 5-7 gün |
| Faz 7: Pit + Anomaly | 5-7 gün |
| Faz 8: Benchmark | 3-5 gün |
| Faz 9: Yayın | 2-3 gün |
| Faz 10: Dashboard | 3-5 gün |
| **Toplam** | **35-52 gün** |
