---
title: "F1 Analytics Lab — Tasarım Dökümanı"
status: draft
created: 2026-05-26
updated: 2026-05-27
author: Enes Demir (230202066)
tags: [f1, telemetry, dataset, eda, outlier, benchmark, ml, huggingface, kaggle, wandb]
---

# F1 Analytics Lab

**Dataset Collection, EDA, Outlier Analysis & ML Benchmarks from Formula 1 Telemetry**

Formula 1 verisini ham halinden alıp temizleyen, farklı ML problemleri için hazır datasetler üreten, kapsamlı EDA ve outlier analizi yapan, klasik ML modellerini karşılaştıran ve sonuçları HuggingFace/Kaggle/W&B üzerinden yayınlayan bir veri bilimi ve makine öğrenmesi laboratuvarı.

**Ana ürün dataset ve analiz altyapısıdır — arayüz değil.**

---

## İçindekiler

1. [Proje Özeti ve Motivasyon](#1-proje-özeti-ve-motivasyon)
2. [Rakip Analizi](#2-rakip-analizi)
3. [Mimari](#3-mimari)
4. [Repository Yapısı](#4-repository-yapısı)
5. [Veri Toplama Pipeline'ı](#5-veri-toplama-pipelineı)
6. [Veri Temizleme ve Outlier Stratejisi](#6-veri-temizleme-ve-outlier-stratejisi)
7. [EDA Planı](#7-eda-planı)
8. [Outlier Analizi](#8-outlier-analizi)
9. [Dataset Factory](#9-dataset-factory)
10. [Feature Engineering](#10-feature-engineering)
11. [ML Task'ları](#11-ml-taskları)
12. [Model Benchmark Planı](#12-model-benchmark-planı)
13. [Split Stratejisi](#13-split-stratejisi)
14. [W&B Kullanımı](#14-wb-kullanımı)
15. [Yayın Stratejisi](#15-yayın-stratejisi)
16. [Arayüz Planı (Sonraki Faz)](#16-arayüz-planı-sonraki-faz)
17. [RL — Nerede ve Ne Zaman?](#17-rl--nerede-ve-ne-zaman)
18. [Fazlara Bölünmüş Yol Haritası](#18-fazlara-bölünmüş-yol-haritası)
19. [README Taslağı](#19-readme-taslağı)
20. [CV Entegrasyonu](#20-cv-entegrasyonu)

---

## 1. Proje Özeti ve Motivasyon

### Eski ve Yeni Konumlandırma

| | Eski Fikir | **Yeni Fikir** |
|---|---|---|
| Odak | Overtake tahmini yapan replay dashboard | **Dataset + EDA + Outlier + ML Benchmark laboratuvarı** |
| Ana ürün | Streamlit arayüz | **Temizlenmiş datasetler, analiz raporları, model karşılaştırmaları** |
| Arayüz rolü | Merkezde | **En sonda, showcase amaçlı** |
| CV değeri | "Dashboard yaptım" | **"Veri pipeline'ı kurdum, EDA yaptım, 6 task için benchmark çıkardım, HF/Kaggle'da yayınladım"** |

### Neden Bu Değişiklik?

Mevcut CV'de (MetroCast tarafında) zaten dashboard, W&B, React, AWS, ONNX ve MLOps pipeline anlatısı var. Bu projede ekstra site yapmak yerine **dataset/benchmark tarafını öne çıkarmak** daha farklı yetkinlik gösterir:

- Veri toplama ve temizleme pipeline'ı
- Feature engineering (time-series, rolling features, domain-specific)
- Outlier detection ve açıklama (sadece silmek değil, anlamak)
- Birden fazla ML task'ı için model karşılaştırma
- Public dataset ve reproducible benchmark yayını
- Domain generalization (circuit holdout, temporal split)

### Ana Çıktılar

```
1. Temizlenmiş F1 datasetleri (HF + Kaggle)
2. EDA ve outlier analiz raporları (GitHub README + markdown reports)
3. 6 farklı ML task'ı için hazır dataset
4. Model benchmark sonuçları (W&B)
5. Dataset card + schema dokümantasyonu
6. Reproducible pipeline (tek komutla baştan sona)
7. Son aşamada küçük interaktif arayüz (HF Space)
```

---

## 2. Rakip Analizi

### Var Olan Projeler

| Proje | Ne Yapıyor? | ML? | Dataset? | Benchmark? | EDA? |
|-------|-------------|-----|----------|------------|------|
| [F1 StratLab](https://github.com/VforVitorio/F1-StratLab) | 7 ML model + 6 LangGraph agent. Pit stratejisi. | ✅ | ✅ HF | ❌ | ❌ |
| [pk2971/F1-dashboards](https://github.com/pk2971/F1-dashboards) | 6 sayfalı Streamlit dashboard. Altair. | ❌ | ❌ | ❌ | Kısmen |
| [VforVitorio/F1_Telemetry_Manager](https://github.com/VforVitorio/F1_Telemetry_Manager) | FastAPI + Streamlit. Driver karşılaştırma. MCP. | ❌ | ❌ | ❌ | ❌ |
| [Sleepy-F1](https://sleepy-f1.streamlit.app/) | Streamlit Cloud'da F1 dashboard. | ❌ | ❌ | ❌ | ❌ |
| [Fast-F1](https://github.com/theOehrly/Fast-F1) | Veri erişim kütüphanesi (bizim veri kaynağımız). | ❌ | ❌ | ❌ | ❌ |

**Ortak eksik:** Hiçbiri **çok-tasklı ML benchmark** yapmıyor. Hiçbiri **sistematik outlier analizi** sunmuyor. Hiçbiri **dataset factory** mantığıyla farklı problemler için temiz dataset üretmiyor. Hepsi ya saf görselleştirme ya da tek bir probleme odaklı.

### Bizim Farkımız

| Yetenek | Rakipler | **BİZ** |
|---------|----------|---------|
| Fast-F1 veri erişimi | ✅ | ✅ |
| **Çok-tasklı ML dataset üretimi** | ❌ | ✅ |
| **Sistematik outlier analizi (6 tip)** | ❌ | ✅ |
| **Kapsamlı EDA raporu** | ❌ | ✅ |
| **5+ model benchmark (classification + regression)** | ❌ | ✅ |
| **Domain generalization split (temporal + circuit holdout)** | ❌ | ✅ |
| **Leakage-aware feature engineering** | ❌ | ✅ |
| HF Dataset yayını | Sadece StratLab | ✅ |
| Kaggle Dataset | ❌ | ✅ |
| W&B experiment tracking | ❌ | ✅ |
| HF Space dashboard | sleep-f1 | ✅ (son faz) |

> **Öz:** Rakipler ya "dashboard" ya da "tek problem". Biz **"F1 verisi için ML laboratuvarı"** kuruyoruz. Veriyi anlıyor, temizliyor, birden fazla probleme dataset üretiyor, modelleri karşılaştırıyor ve her şeyi public yayınlıyoruz.

---

## 3. Mimari

### 3.1 Genel Veri Akışı

```
Fast-F1 / Historical F1 Data (2018–2026)
        │
        ▼
┌───────────────────────────┐
│  Raw Data Extraction       │
│  · sessions, laps, stints  │
│  · weather, track_status   │
│  · pit_stops, telemetry    │
│  · drivers, circuits       │
└───────────┬───────────────┘
            │
            ▼
┌───────────────────────────┐
│  Cleaning + Validation     │
│  · missing data analysis   │
│  · invalid lap flagging    │
│  · pit/SC/VSC/rain flags   │
│  · schema validation       │
│  · duplicate detection      │
└───────────┬───────────────┘
            │
            ▼
┌───────────────────────────┐
│  EDA + Outlier Analysis    │
│  · distribution analysis   │
│  · compound/tyre analysis  │
│  · circuit differences     │
│  · outlier detection (6 tip)│
│  · outlier reason tagging  │
└───────────┬───────────────┘
            │
            ▼
┌───────────────────────────┐
│  Feature Engineering       │
│  · lap-level features      │
│  · rolling/time-series     │
│  · tyre degradation        │
│  · weather features        │
│  · overtake pair features  │
│  · pit strategy features   │
└───────────┬───────────────┘
            │
            ▼
┌───────────────────────────────────────────┐
│  DATASET FACTORY                           │
│                                            │
│  ├── Overtake Prediction (binary clf)      │
│  ├── Tyre Degradation (regression)         │
│  ├── Lap Time Prediction (regression)      │
│  ├── Pit Strategy / Undercut (binary clf)  │
│  ├── Anomaly Detection (unsupervised)      │
│  └── Driver/Team Performance (analytics)   │
└───────────┬───────────────────────────────┘
            │
            ▼
┌───────────────────────────┐
│  ML Benchmarks             │
│  · Logistic Regression     │
│  · Random Forest           │
│  · XGBoost                 │
│  · LightGBM                │
│  · CatBoost                 │
│  · MLP baseline (optional)  │
└───────────┬───────────────┘
            │
            ▼
┌───────────────────────────┐
│  Publishing                │
│  · HuggingFace Dataset     │
│  · Kaggle Dataset          │
│  · W&B Reports             │
│  · GitHub README + reports │
└───────────┬───────────────┘
            │
            ▼
┌───────────────────────────┐
│  Dashboard (Faz 7)         │
│  · Streamlit / HF Space    │
│  · Dataset Explorer        │
│  · EDA Dashboard           │
│  · Model Comparison        │
│  · Overtake Demo           │
└───────────────────────────┘
```

### 3.2 Tech Stack

| Katman | Teknoloji | Not |
|--------|-----------|-----|
| Veri erişim | Fast-F1, Pandas, NumPy | Temel veri kaynağı |
| İşleme | Python, Polars (opsiyonel) | Pandas yeterli, büyük veride Polars |
| Görselleştirme | Matplotlib, Seaborn, Plotly | EDA ve rapor figürleri |
| ML (classification) | Logistic Regression, Random Forest, XGBoost, LightGBM, CatBoost | Scikit-learn + ilgili kütüphaneler |
| ML (regression) | Linear/Ridge/Lasso, RF, XGBoost, LightGBM, CatBoost | Aynı ekosistem |
| Outlier detection | Z-score, IQR, Isolation Forest, LOF, DBSCAN | Scikit-learn |
| Experiment tracking | Weights & Biases | Tüm model benchmark'ları |
| Dataset yayını | HuggingFace Hub, Kaggle API | Public artifact |
| Environment | uv (Python package manager) | Hızlı, modern |
| Dashboard (sonra) | Streamlit, Plotly | HF Space deploy |
| CI/CD (sonra) | GitHub Actions | Otomatik veri güncelleme |

---

## 4. Repository Yapısı

```
f1-analytics-lab/
│
├── README.md
├── pyproject.toml
├── .env.example
├── .gitignore
│
├── configs/
│   ├── data.yaml            # Fast-F1 cache, sezon listesi, session tipleri
│   ├── features.yaml        # Hangi feature set'leri aktif
│   ├── models.yaml          # Model hyperparametreleri
│   └── wandb.yaml           # W&B project/entity config
│
├── data/
│   ├── raw/                 # Fast-F1'den ham çıktı (cache)
│   ├── interim/             # İşlenmemiş ama birleştirilmiş Parquet
│   ├── processed/           # ML-ready datasetler
│   └── external/            # Circuit metadata, FIA rules, vb.
│
├── notebooks/
│   ├── 01_data_collection.ipynb
│   ├── 02_data_cleaning.ipynb
│   ├── 03_eda_general.ipynb
│   ├── 04_eda_tyre.ipynb
│   ├── 05_eda_overtake.ipynb
│   ├── 06_outlier_analysis.ipynb
│   ├── 07_tyre_degradation_dataset.ipynb
│   ├── 08_lap_time_dataset.ipynb
│   ├── 09_overtake_dataset.ipynb
│   ├── 10_pit_strategy_dataset.ipynb
│   ├── 11_model_benchmarks_classification.ipynb
│   ├── 12_model_benchmarks_regression.ipynb
│   └── 13_results_summary.ipynb
│
├── src/
│   ├── __init__.py
│   │
│   ├── data/
│   │   ├── __init__.py
│   │   ├── fetch_fastf1.py       # Fast-F1'den session/lap/weather çekme
│   │   ├── build_sessions.py     # Session metadata tablosu
│   │   ├── build_laps.py         # Ana lap tablosu
│   │   ├── build_stints.py       # Stint ve pit stop tablosu
│   │   ├── build_weather.py      # Hava durumu tablosu
│   │   ├── build_track_status.py # Track status (SC/VSC/yellow) tablosu
│   │   └── validators.py         # Schema ve veri doğrulama
│   │
│   ├── features/
│   │   ├── __init__.py
│   │   ├── lap_features.py       # Tur bazlı temel feature'lar
│   │   ├── rolling_features.py   # Rolling mean/std/trend
│   │   ├── tyre_features.py      # Lastik aşınma feature'ları
│   │   ├── overtake_features.py  # Geçiş ikilisi feature'ları
│   │   ├── weather_features.py   # Hava durumu feature'ları
│   │   └── pit_features.py       # Pit strateji feature'ları
│   │
│   ├── tasks/
│   │   ├── __init__.py
│   │   ├── overtake_prediction/
│   │   │   ├── build_dataset.py
│   │   │   ├── train.py
│   │   │   └── evaluate.py
│   │   ├── tyre_degradation/
│   │   │   ├── build_dataset.py
│   │   │   ├── train.py
│   │   │   └── evaluate.py
│   │   ├── lap_time_prediction/
│   │   │   ├── build_dataset.py
│   │   │   ├── train.py
│   │   │   └── evaluate.py
│   │   ├── pit_strategy/
│   │   │   ├── build_dataset.py
│   │   │   ├── train.py
│   │   │   └── evaluate.py
│   │   └── anomaly_detection/
│   │       ├── detect_outliers.py
│   │       └── classify_outliers.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── train_classification.py  # Tüm classifier'lar için ortak train
│   │   ├── train_regression.py      # Tüm regressor'lar için ortak train
│   │   ├── evaluate.py              # Ortak metrik hesaplama
│   │   └── model_registry.py        # Model isimleri ve hyperparam mapping
│   │
│   ├── visualization/
│   │   ├── __init__.py
│   │   ├── eda_plots.py             # EDA figürleri
│   │   ├── outlier_plots.py         # Outlier görselleştirme
│   │   └── model_plots.py           # ROC, calibration, residual, feature importance
│   │
│   └── utils/
│       ├── __init__.py
│       ├── paths.py                 # Proje path çözümleyici
│       ├── logging.py               # Logger konfigürasyonu
│       ├── seed.py                  # Reproducibility
│       └── config.py                # YAML config okuyucu
│
├── reports/
│   ├── dataset_card.md              # Her dataset için schema + açıklama
│   ├── eda_report.md                # Genel EDA bulguları
│   ├── outlier_report.md            # Outlier tipleri ve dağılımları
│   ├── model_benchmark_report.md    # Tüm modellerin karşılaştırması
│   └── figures/                     # Rapor figürleri (PNG/SVG)
│
├── app/
│   └── streamlit_app.py             # Faz 7: interaktif dashboard
│
└── scripts/
    ├── build_all_datasets.py        # Tüm datasetleri tek seferde üret
    ├── run_full_eda.py              # Tüm EDA notebook'larını çalıştır
    ├── train_all_models.py          # Tüm modelleri eğit ve benchmark yap
    └── publish_all.py               # HF + Kaggle + W&B publish
```

---

## 5. Veri Toplama Pipeline'ı

### 5.1 Veri Kaynağı

[Fast-F1](https://github.com/theOehrly/Fast-F1) kütüphanesi üzerinden F1 resmi veri akışı (Jolpica-F1 / Ergast). Tamamen tarihsel veri — canlı API yok.

### 5.2 Kapsam

| Parametre | Değer | Açıklama |
|-----------|-------|----------|
| Sezonlar | 2018–2026 | 2018'den itibaren telemetri verisi daha zengin |
| Session tipleri | R, Q, FP2 | FP1/FP3 temsili az, Q ve R ana odak |
| Pistler | Tüm F1 takvimi | ~25 pist/sezon |
| Pilotlar | Tüm grid | ~20 pilot/sezon |
| Veri tipleri | Lap, telemetry, weather, track_status, stint, pit | Hepsi |

### 5.3 Çıkarılacak Ham Tablolar

| Tablo | İçerik | Tahmini Boyut |
|-------|--------|---------------|
| `sessions` | Sezon, GP, session tipi, tarih, pist | ~500 satır |
| `laps` | Her tur: pilot, takım, süre, sektör, lastik, pit, track status | ~300K satır |
| `stints` | Stint başlangıç/bitiş, compound, tur sayısı | ~5K satır |
| `weather` | Hava sıcaklığı, pist sıcaklığı, nem, rüzgar, yağmur | ~500K satır (örneklenmiş) |
| `track_status` | Yeşil/sarı/SC/VSC/kırmızı zaman damgaları | ~10K satır |
| `pit_stops` | Pit zamanı, süre, lastik değişimi | ~5K satır |
| `drivers` | Pilot kodu, isim, takım (sezon bazlı) | ~500 satır |
| `circuits` | Pist adı, ülke, tur sayısı, DRS bölgeleri | ~30 satır |
| `telemetry_samples` | Hız, gaz, fren, DRS, RPM (örneklenmiş) | Büyük — sadece seçili yarışlar |

### 5.4 Örnek Lap Tablosu Şeması

```
laps.parquet
├── season: int
├── round: int
├── grand_prix: str
├── session: str              # R, Q, FP2
├── driver: str               # LEC, HAM, VER...
├── team: str                 # Ferrari, Mercedes...
├── lap_number: int
├── lap_time: float           # Saniye
├── sector1_time: float
├── sector2_time: float
├── sector3_time: float
├── compound: str             # SOFT, MEDIUM, HARD, INTERMEDIATE, WET
├── tyre_life: int            # Lastik kaç tur kullanılmış
├── stint: int                # Kaçıncı stint
├── pit_in: bool              # Bu turda pite mi girdi?
├── pit_out: bool             # Bu tur pitten mi çıktı?
├── track_status: str         # Green, Yellow, SC, VSC, Red
├── air_temp: float
├── track_temp: float
├── humidity: float
├── is_valid_lap: bool        # Geçerli tur mu?
├── is_deleted: bool          # Silinmiş tur mu?
└── position: int             # Tur sonu pozisyonu
```

### 5.5 Veri Granülaritesi Stratejisi: Lap-Level Öncelikli

Proje genelinde analiz birimi **tur (lap)** olacak. Sebebi:

- Tyre degradation, lap time prediction, pit strategy gibi task'lar doğası gereği lap-level
- Lap-level veri hem daha küçük (300K satır) hem daha hızlı işleniyor
- Feature engineering (rolling mean/std/trend) lap bazında doğal
- Telemetriye (milyonlarca sample) sadece ihtiyaç olduğunda inilecek

**Timestamp ne zaman kullanılacak?**

Fast-F1 verisinde 4 farklı zaman tipi var. Her birinin kullanım yeri farklı:

| Zaman Tipi | Veride Nerede? | Biz Ne İçin Kullanacağız? |
|------------|---------------|---------------------------|
| `lap_number` (ordinal) | `session.laps` | **Ana sıralama.** Rolling feature'lar, önceki/sonraki tur. Timestamp'e gerek yok. |
| `SessionTime` (saniye, seans başına göre) | Telemetri, weather, track_status | Weather/track_status join'leri, overtake penceresi zamanlaması |
| `Time` (datetime) | `session.weather_data`, `session.track_status` | Lap-Time join'lerinde en yakın örneği bulmak (`merge_asof`) |
| `season` (yıl) | `session.event` | **Temporal split için.** Train/val/test ayrımı. |

**Hangi işlem hangi zamanı kullanır:**

```
Lap sıralaması           → lap_number (timestamp gerekmez)
Rolling features         → lap_number (önceki/sonraki N tur)
Temporal split           → season (yıl bazlı)
Weather join             → SessionTime + merge_asof (en yakın sample)
Track status join        → SessionTime + interval kontrolü
Overtake penceresi       → Telemetri SessionTime (Faz 4'te)
Leakage kontrolü         → lap_number (gelecek tur) + season (gelecek sezon)
```

**Neden telemetriyi ilk fazda yüklemiyoruz?**

```python
session = fastf1.get_session(2024, 'Bahrain', 'R')
session.load()              # lap, weather, track_status — HIZLI
# session.load_telemetry()  # telemetri — YAVAŞ ve BÜYÜK, sadece ihtiyaç olursa
```

Telemetri oturum başına ~1-2 milyon satır. Overteke penceresi tespiti için gerekecek ama o Faz 4'te. İlk 3 faz için lap-level yeterli.

Weather ve track status join'leri için `SessionTime` kullanılacak ama bu join işlemi yine lap-level sonuç üretiyor. Yani hava verisinin hangi tura denk geldiğini bulup o turun satırına yazıyoruz, timestamp'i saklamıyoruz.

**Pratik kod akışı:**

```python
# 1. Ana lap tablosu — lap_number ile sıralı
laps = session.laps  # DataFrame, her satır = 1 tur

# 2. Weather join: en yakın weather sample'ı bul
weather = session.weather_data  # Time kolonlu
laps = pd.merge_asof(
    laps.sort_values('LapStartTime'),
    weather.sort_values('Time'),
    left_on='LapStartTime',
    right_on='Time',
    direction='nearest'
)

# 3. Track status: interval join (tur zamanı hangi status aralığında?)
track_status = session.track_status
# Her tur için: turun SessionTime'ı hangi status interval'ine düşüyor?
# → track_status sütunu laps'e yazılır
```

Özet: **Lap-level başla, timestamp'i sadece join ve doğrulama için kullan, telemetriyi sonraya bırak.** Bu bizi Faz 1-3'te hızlandırır, Faz 4'te overtake detayı için telemetri eklenir.

---

## 6. Veri Temizleme ve Outlier Stratejisi

Her outlier direkt silinmez. Üç kategoriye ayrılır:

### 6.1 Silinecek Veriler (Hard Remove)

```
- Eksik driver/session bilgisi
- Bozuk lap_time (NaN, negatif, 0)
- Telemetry join hatası (eşleşmeyen timestamp)
- Açıkça invalid sample (veri toplama hatası)
```

### 6.2 Flag Olarak Tutulacak Veriler (Keep + Flag)

Bunları silmek yerine feature yapmak daha değerli:

| Flag | Anlamı | Neden Silinmez? |
|------|--------|-----------------|
| `is_pit_lap` | Pit giriş/çıkış turu | Pit strateji analizinde lazım |
| `is_safety_car_lap` | SC arkasındaki tur | SC etkisi analizi için |
| `is_vsc_lap` | VSC altındaki tur | VSC etkisi analizi için |
| `is_yellow_flag_lap` | Sarı bayrak turu | Track status analizi |
| `is_rain_lap` | Yağmur turu | Hava durumu etkisi |
| `is_outlier_lap` | Anormal yavaş/hızlı | Anomali tiplendirmesi |
| `is_deleted_lap` | FIA tarafından silinmiş | Neden silindiği önemli |

### 6.3 Task'a Göre Filtreleme

Her task kendi filtreleme politikasını uygular:

| Task | Pit Lap? | SC/VSC? | Rain? | Outlier? |
|------|----------|---------|-------|----------|
| Tyre degradation | ÇIKAR | ÇIKAR | ÇIKAR | ÇIKAR |
| Lap time prediction | ÇIKAR | AYRI ANALİZ | AYRI ANALİZ | ÇIKAR |
| Overtake prediction | ÇIKAR | ÇIKAR | ÇIKAR | ÇIKAR |
| Anomaly detection | DAHİL | DAHİL | DAHİL | **HEDEF** |
| Pit strategy | **HEDEF** | DAHİL | AYRI ANALİZ | ÇIKAR |

> Tek bir "temiz veri" yok. Her task'ın kendi `build_dataset()` fonksiyonu kendi filtrelemesini yapar.

---

## 7. EDA Planı

EDA projeyi ciddi gösteren ana kısım. Acele geçilmemeli.

### 7.1 Genel EDA

```
- Sezonlara göre yarış sayısı
- Pistlere göre lap time dağılımı
- Compound kullanım dağılımı (SOFT/MEDIUM/HARD/INT/WET)
- Stint uzunluğu dağılımı
- Track temperature dağılımı
- Safety car / VSC sıklığı ve etkisi (lap time'a etkisi)
- Pit stop sayıları ve zamanlaması
- Pilot ve takım bazlı veri miktarı (class imbalance kontrolü)
- Sektör bazlı pace farklılıkları
```

### 7.2 Tyre EDA

```
- Compound bazlı ortalama tyre_life
- Tyre_age arttıkça lap_time değişimi (degradation curve)
- Track temperature vs degradation (sıcak pist = daha hızlı aşınma mı?)
- Pist bazlı degradation farkı (hangi pist lastik yiyor?)
- Soft vs Medium vs Hard karşılaştırması
- Stint başı ve sonu pace farkı
- Compound değişiminin etkisi (MED → HARD geçişte pace kaybı)
```

### 7.3 Overtake EDA

```
- Pistlere göre overtake window sayısı
- Gap < 1s olan durumların başarı oranı
- DRS etkisi (DRS açıkken vs kapalıyken geçiş oranı)
- Speed delta etkisi
- Tyre age delta etkisi (taze lastik = daha fazla geçiş mi?)
- Compound advantage etkisi
- Track status etkisi
- Sektör bazlı: hangi sektörlerde daha çok geçiş oluyor?
```

### 7.4 Lap Time EDA

```
- Lap time dağılımı (pist, sezon, session)
- Valid vs invalid lap analizi
- Pit lap etkisi (pit lap normalden ne kadar yavaş?)
- SC/VSC lap etkisi
- Rain/yağmur etkisi
- Sektör bazlı anomaliler
- Yarış içi pace evrimi (başlangıç vs bitiş)
```

### 7.5 Outlier EDA (Preliminary)

```
- Aşırı yavaş turların nedenleri (pit, SC, rain, damage?)
- Aşırı hızlı turlar hangi koşullarda?
- Pit lap ile normal lap nasıl ayrılıyor? (lap_time threshold)
- SC/VSC lap temizlenince dağılım nasıl değişiyor?
- Tyre degradation outlierları hangi pistlerde fazla?
- Hangi pilotlar daha tutarlı? (lap_time std)
```

---

## 8. Outlier Analizi

### 8.1 Outlier Tipleri

| # | Tip | Açıklama | Tespit Yöntemi |
|---|-----|----------|----------------|
| 1 | **Pit lap** | Pit giriş/çıkış turu | Rule-based + pit_in/pit_out flag |
| 2 | **Safety car lap** | SC arkasındaki yavaş tur | track_status + lap_time > median × 1.5 |
| 3 | **VSC lap** | VSC altındaki tur | track_status |
| 4 | **Rain lap** | Yağmur/ıslak zemin turu | compound INT/WET veya weather |
| 5 | **Damage/spin olası lap** | Aniden yavaşlayan tur | lap_time_delta > 3× rolling_std |
| 6 | **Beklenmeyen pit** | Normal stint dışı pit | stint_length < expected × 0.5 |
| 7 | **Anormal sector split** | Bir sektör çok yavaş, diğerleri normal | sector_z_score > 3 |
| 8 | **Aşırı degradation** | Normalden hızlı lastik aşınması | pace_loss > expected × 2 |

### 8.2 Yöntemler

```
Rule-based filtering:
  - pit_in / pit_out flag
  - track_status string
  - compound değişimi

Statistical:
  - Z-score (per driver, per circuit)
  - IQR (per compound, per session)
  - Rolling statistics (3-lap, 5-lap window)

ML-based:
  - Isolation Forest (unsupervised outlier detection)
  - Local Outlier Factor (density-based)
  - DBSCAN (cluster + noise detection)
```

### 8.3 Outlier Çıktı Formatı

```python
outlier_events = {
    "lap_id": "2023_BHR_R_LEC_L25",
    "outlier_score": 0.92,          # 0-1, ne kadar anormal
    "outlier_type": "damage/spin",  # Yukarıdaki tiplerden biri
    "outlier_reason": "Lap time 12.3s slower than rolling mean, sector 2 anomaly",
    "detection_method": "isolation_forest + z_score",
    "features_at_time": {
        "lap_time": 112.3,
        "rolling_mean_3": 98.1,
        "sector2_time": 45.2,       # Anormal olan sektör
        "track_status": "Green",
        "compound": "SOFT"
    }
}
```

---

## 9. Dataset Factory

Asıl önemli kısım. Tek bir dataset değil, birden fazla task için dataset üretilir.

### 9.1 Ortak Temel Tablolar

Tüm task'ların kullanacağı ortak `interim/` tabloları:

```
interim/sessions.parquet
interim/laps.parquet         ← ana tablo, en çok kullanılan
interim/stints.parquet
interim/weather.parquet
interim/pit_stops.parquet
interim/track_status.parquet
interim/drivers.parquet
interim/circuits.parquet
```

### 9.2 Datasetler

| # | Dataset | Task Tipi | Target | Öncelik |
|---|---------|-----------|--------|---------|
| 1 | `f1_tyre_degradation` | Regression | `lap_time_delta` / `degradation_rate` | ★★★ |
| 2 | `f1_lap_time_prediction` | Regression | `next_lap_time` | ★★★ |
| 3 | `f1_overtake_prediction` | Binary classification | `overtake_success` (0/1) | ★★ |
| 4 | `f1_pit_strategy` | Binary classification | `position_gain_after_pit` (0/1) | ★★ |
| 5 | `f1_anomaly_events` | Unsupervised / analytics | `outlier_type` | ★ |
| 6 | `f1_driver_performance` | Analytics / regression | `normalized_pace` | ★ |

### 9.3 Dataset Kartı Formatı

Her dataset için `reports/dataset_card.md` içinde:

```markdown
## Dataset: f1_tyre_degradation

**Task:** Regression — predict lap time change due to tyre wear

**Source:** Fast-F1, 2018–2026 race sessions

**Target:** `lap_time_delta` (seconds) — difference from stint-opening pace

**Samples:** ~25,000 (clean laps only, pit/SC/VSC/rain removed)

**Features (20):**
| Feature | Type | Description |
|---------|------|-------------|
| compound | cat | SOFT/MEDIUM/HARD |
| tyre_age | int | Laps on current tyre |
| stint_length | int | Total stint length so far |
| track_temp | float | Track temperature (°C) |
| ... | ... | ... |

**Split:** Temporal (train 2018–2022, val 2023, test 2024–2026)

**Known limitations:**
- Fuel load not directly available (proxied by race_progress)
- Inter-team tyre management differences not captured
- Weather data is point-sampled, not continuous

**Leakage warnings:**
- `lap_time` used to compute target — don't include as raw feature
- Future lap info must not leak into features
```

---

## 10. Feature Engineering

### 10.1 Lap-Level Features (Tüm task'larda ortak)

```
lap_time, sector_times
lap_number, race_progress
is_valid_lap, is_pit_lap, is_sc_lap, is_rain_lap
compound, tyre_life, stint
track_status
air_temp, track_temp, humidity
driver, team, circuit (categorical)
```

### 10.2 Rolling / Time-Series Features

```
previous_1_lap_time
previous_3_lap_mean
previous_5_lap_mean
lap_time_delta_from_prev
rolling_3_lap_std
rolling_5_lap_std
pace_trend (+ / - / flat)
```

### 10.3 Tyre Features

```
compound_encoded (ordinal: SOFT=3, MED=2, HARD=1)
tyre_age_normalized (age / expected_life)
stint_length_so_far
stint_progress (tyre_age / total_stint_length)
expected_degradation_rate (per compound, per circuit)
tyre_age_x_track_temp (interaction)
```

### 10.4 Weather Features

```
air_temp, track_temp
temp_delta (track - air)
humidity
rainfall (varsa)
wind_speed, wind_direction
headwind_component (DRS düzlüğüne göre)
weather_change_flag (önceki tura göre değişim)
```

### 10.5 Overtake Pair Features (sadece overtake dataset'i için)

```
chasing_driver, ahead_driver
gap_s (saniye)
gap_trend (kapanıyor mu?)
speed_delta_kmh
closing_rate_ms
tyre_age_delta (chasing - ahead)
compound_advantage (-1/0/+1)
drs_available (chasing DRS bölgesinde mi?)
drs_zone_length_m
distance_to_corner_m
track_status
```

### 10.6 Pit Strategy Features

```
gap_to_ahead_before_pit
gap_to_behind_before_pit
position_before_pit
compound_before, compound_after
tyre_age_before_pit
pit_lap_number
pit_duration_s
competitor_pit_lap (öndeki/arkadaki ne zaman pit yaptı?)
```

### ⚠️ En Kritik Kural: Leakage Kontrolü

```
Feature üretirken GELECEĞİ KULLANMA.

Mesela:
  Target: next_lap_time ise,
  ✗ sonraki turun weather verisi feature olamaz
  ✗ sonraki turun track_status'ü feature olamaz
  ✗ "sonraki turda pit var mı" feature olamaz

  Target: overtake_success ise,
  ✗ overtake sonrası speed delta feature olamaz
  ✗ "yarış sonundaki pozisyon" feature olamaz
```

Her dataset için leakage audit yapılacak ve raporlanacak.

---

## 11. ML Task'ları

### Task 1 — Tyre Degradation Prediction ★★★

| | Detay |
|---|---|
| **Amaç** | Lastik yaşlandıkça tur zamanı ne kadar kötüleşiyor? |
| **Target** | `lap_time_delta` (stint-opening pace'ten sapma, saniye) |
| **Tip** | Regression |
| **Sample** | ~25K temiz tur |
| **Önem** | En değerli regression task'ı. Time-series + domain-specific feature engineering. |
| **Metrikler** | MAE, RMSE, R², MAPE, per-compound error, per-circuit error |

### Task 2 — Lap Time Prediction ★★★

| | Detay |
|---|---|
| **Amaç** | Bir sonraki turun süresi kaç olur? |
| **Target** | `next_lap_time` (saniye) |
| **Tip** | Regression (time-series forecasting) |
| **Sample** | ~250K tur (geçerli turlar) |
| **Önem** | Time-series forecasting. Leakage kontrolü kritik. |
| **Metrikler** | MAE, RMSE, R², MAPE, residual analizi |

### Task 3 — Overtake Prediction ★★

| | Detay |
|---|---|
| **Amaç** | Takip eden araç önündekini geçecek mi? |
| **Target** | `overtake_success` (0/1) |
| **Tip** | Binary classification |
| **Sample** | ~5K overtake penceresi (gap < 1s) |
| **Önem** | Class imbalance (çoğu yakın takip geçişle bitmez). PR-AUC önemli. |
| **Metrikler** | ROC-AUC, PR-AUC, F1, Precision, Recall, Brier Score, Calibration |

### Task 4 — Pit Strategy / Undercut ★★

| | Detay |
|---|---|
| **Amaç** | Pit sonrası pozisyon kazanıldı mı? |
| **Target** | `position_gain_after_pit` veya `undercut_success` (0/1) |
| **Tip** | Binary classification |
| **Sample** | ~3K pit stop |
| **Önem** | RL'ye giden yolun ilk adımı. |
| **Metrikler** | ROC-AUC, F1, Precision, Recall |

### Task 5 — Anomaly Detection ★

| | Detay |
|---|---|
| **Amaç** | Anormal tur, stint, pit veya pace davranışlarını bulmak |
| **Target** | `outlier_type` (multi-class veya unsupervised) |
| **Tip** | Unsupervised / semi-supervised |
| **Sample** | Tüm turlar |
| **Önem** | Veri kalitesi için kritik. Modellemeden önce yapılmalı. |
| **Yöntemler** | Z-score, IQR, Isolation Forest, LOF, DBSCAN |

### Task 6 — Driver/Team Performance ★

| | Detay |
|---|---|
| **Amaç** | Pilot ve takım performansını normalize ederek karşılaştırmak |
| **Target** | `normalized_pace` (kontrollü koşullarda) |
| **Tip** | Analytics + regression |
| **Sample** | ~100K tur |
| **Önem** | Daha çok EDA + istatistiksel analiz. ML opsiyonel. |

---

## 12. Model Benchmark Planı

### 12.1 Classification Modelleri

Task'lar: `overtake_prediction`, `pit_strategy`, `undercut_success`

| Model | Kütüphane | Hyperparam Arama |
|-------|-----------|-----------------|
| Logistic Regression | scikit-learn | C, penalty |
| Random Forest | scikit-learn | n_estimators, max_depth |
| XGBoost | xgboost | n_estimators, max_depth, lr |
| LightGBM | lightgbm | n_estimators, num_leaves, lr |
| CatBoost | catboost | iterations, depth, lr |
| MLP (baseline) | scikit-learn | hidden_layer_sizes |

### 12.2 Regression Modelleri

Task'lar: `tyre_degradation`, `lap_time_prediction`

| Model | Kütüphane | Hyperparam Arama |
|-------|-----------|-----------------|
| Linear Regression | scikit-learn | — |
| Ridge | scikit-learn | alpha |
| Lasso | scikit-learn | alpha |
| Random Forest | scikit-learn | n_estimators, max_depth |
| XGBoost | xgboost | n_estimators, max_depth, lr |
| LightGBM | lightgbm | n_estimators, num_leaves, lr |
| CatBoost | catboost | iterations, depth, lr |
| MLP (baseline) | scikit-learn | hidden_layer_sizes |

### 12.3 Metrikler

**Classification:**
```
Accuracy, Precision, Recall, F1 (macro + weighted)
ROC-AUC, PR-AUC
Brier Score
Calibration Curve
Confusion Matrix
```

**Regression:**
```
MAE, RMSE, R², MAPE
Residual plots
Error by circuit
Error by compound
Error by team/driver
```

### 12.4 Benchmark Çıktı Formatı

Markdown tablosu:

| Task | Model | ROC-AUC | F1 | Precision | Recall | Train Time |
|------|-------|---------|-----|-----------|--------|------------|
| overtake | Logistic Reg. | 0.72 | 0.45 | 0.52 | 0.40 | 0.3s |
| overtake | Random Forest | 0.81 | 0.58 | 0.61 | 0.55 | 12s |
| overtake | XGBoost | 0.84 | 0.62 | 0.64 | 0.60 | 45s |
| overtake | LightGBM | **0.85** | **0.64** | 0.65 | **0.63** | 8s |
| overtake | CatBoost | 0.84 | 0.63 | **0.66** | 0.61 | 90s |

---

## 13. Split Stratejisi

Random split yapılırsa leakage olur. Üç farklı split test edilecek:

### 13.1 Temporal Split (Ana Split)

```
Train:  2018–2022
Val:    2023
Test:   2024–2026
```

Gerçekçi — model geçmişten geleceğe genelleme yapıyor.

### 13.2 Circuit Holdout Split

```
Train:  Monza, Silverstone, Spa, ... dışındaki tüm pistler
Test:   Monza, Silverstone, Spa (hiç train'de görülmemiş)
```

"Yeni piste genelleme" ölçer. Domain generalization.

### 13.3 Driver/Team Leakage Kontrolü

İki deney:

```
Model A: driver + team feature'ları VAR
Model B: driver + team feature'ları YOK
```

Amaç: Model gerçekten fiziksel yarış dinamiklerini mi öğreniyor, yoksa sadece "Red Bull hızlıdır" gibi shortcut mu?

Eğer Model A >> Model B ise → model shortcut öğreniyor, domain generalization zayıf.

Bu analiz rapora eklenir.

---

## 14. W&B Kullanımı

### Project Yapısı

```
Entity:  enesdemir
Project: f1-analytics-lab

Group'lar:
  group="tyre_degradation"  → tüm regression modelleri
  group="lap_time"           → tüm regression modelleri
  group="overtake"           → tüm classification modelleri
  group="pit_strategy"       → tüm classification modelleri
```

### Loglanacaklar

```python
wandb.init(
    project="f1-analytics-lab",
    group="overtake_prediction",
    name="lightgbm_baseline",
    config={
        "task": "overtake_prediction",
        "model": "lightgbm",
        "split": "temporal",
        "features": ["speed_delta", "tyre_delta", ...],
        "hyperparams": {"n_estimators": 100, "num_leaves": 31}
    }
)

# Log metrics
wandb.log({"roc_auc": 0.85, "f1": 0.64, "precision": 0.65})

# Log artifacts
wandb.log_artifact("models/overtake_lgbm.pkl", type="model")
wandb.log_artifact("data/processed/overtake_dataset.parquet", type="dataset")

# Log plots
wandb.log({
    "roc_curve": wandb.plot.roc_curve(y_test, y_pred_proba),
    "confusion_matrix": wandb.plot.confusion_matrix(y_test, y_pred),
    "feature_importance": wandb.plot.bar(fi_table)
})
```

---

## 15. Yayın Stratejisi

### 15.1 HuggingFace Dataset

**Repo:** `enesdemir/f1-analytics-dataset`

İçerik:
```
f1_tyre_degradation/
  ├── train.parquet
  ├── val.parquet
  └── test.parquet

f1_lap_time_prediction/
  ├── train.parquet
  ├── val.parquet
  └── test.parquet

f1_overtake_prediction/
  ├── train.parquet
  ├── val.parquet
  └── test.parquet

f1_pit_strategy/
  ├── train.parquet
  ├── val.parquet
  └── test.parquet

f1_anomaly_events/
  └── all.parquet
```

Dataset card: `README.md` (HF'te otomatik render), schema, target, feature açıklamaları, known limitations, citation.

### 15.2 Kaggle Dataset

**Repo:** `enesdemir143/f1-analytics-dataset`

HF'in CSV/Parquet aynası. Ek olarak Kaggle notebook'ları (example usage).

### 15.3 GitHub

```
README.md:
  - Proje açıklaması
  - EDA figürleri (gömülü PNG)
  - Model benchmark tablosu
  - How to reproduce
  - HF/Kaggle/W&B linkleri
  - License
```

### 15.4 W&B Reports

Her task için ayrı report veya tek bir comprehensive report:

```
f1-analytics-lab main report:
  - Project overview
  - Dataset descriptions
  - EDA highlights
  - Model comparison tables
  - ROC curves, calibration plots
  - Feature importance
  - Residual analysis
```

---

## 16. Arayüz Planı (Sonraki Faz)

Dashboard ana ürün değil, showcase vitrini.

### Sayfalar

| # | Sayfa | Amaç |
|---|-------|------|
| 1 | **Dataset Explorer** | Sezon/pist/pilot/task seç, dataset satırlarını gör |
| 2 | **EDA Dashboard** | Lap time dist, degradation curves, pit stop dist, track temp effects |
| 3 | **Outlier Explorer** | Anormal turları listele, sebebini göster |
| 4 | **Model Benchmark** | Model karşılaştırma tablosu, ROC/MAE, feature importance |
| 5 | **Overtake Predictor** | 3-5 seçilmiş overtake case, model tahmini vs gerçek sonuç |
| 6 | **Tyre Degradation Explorer** | Compound/pist seç, degradation curve, tahmin vs gerçek |

### Tech Stack

```
Streamlit + Plotly
HF Space (CPU Basic — BEDAVA)
```

---

## 17. RL — Nerede ve Ne Zaman?

RL ilk fazda merkezde değil. Sıralama:

```
1. Tyre degradation modeli (supervised regression)
2. Lap time prediction modeli
3. Pit sonrası time loss modeli
4. Basit pit strategy simulator (rule-based)
5. Sonra RL agent (PPO)
```

### RL State

```
lap_number, position
gap_to_ahead, gap_to_behind
compound, tyre_age
predicted_degradation (Task 1 çıktısı)
track_status, weather
```

### RL Action

```
stay_out
pit_soft
pit_medium
pit_hard
push
conserve
```

### RL Reward

```
position_gain
lap_time_gain
penalty_for_extra_pit
tyre_degradation_penalty
```

Bu Faz 2 veya 3 işi. İlk CV versiyonu için şart değil. README'de "Future Work" olarak dursun.

---

## 18. Yol Haritası

Aşağıda genel yön ve çıktılar özetlenmiştir. Detaylı faz planlaması `.planning/ROADMAP.md` ve `.planning/phases/` altında GSD ile yönetilmektedir.

### Genel Akış

Her bir ML task'ı (tyre degradation, lap time prediction, overtake, vb.) için pipeline şu sırayla ilerler:

```
Task X:
  Veri çekme → Temizleme → EDA → Outlier analizi → Feature engineering
         │
         ▼
  Dataset üretimi → Train/val/test split → Model eğitimi → Benchmark → Yayın
```

Fazlar task'lar arası bağımlılığa göre gruplandırılır. Ortak veri altyapısı (extraction, cleaning, validation) tüm task'lar için bir kere kurulur. Sonrasında her task kendi EDA/outlier/feature/dataset/train/evaluate döngüsünü takip eder.

### Ana İş Paketleri

```
1. Proje iskeleti        — repo, env, config, W&B project
2. Veri toplama          — Fast-F1'den 2018-2026 verileri, interim Parquet
3. Temizleme + flag'ler  — is_pit_lap, is_sc_lap, is_valid_lap, outlier flags
4. EDA (tüm task'lar)    — dağılımlar, compound/tyre/circuit analizleri
5. Outlier analizi        — 6+ outlier tipi, detection + tagging
6. Feature engineering    — rolling, tyre, weather, task-spesifik
7. Dataset factory        — her task için ML-ready dataset + split
8. Model eğitimi          — classification + regression, tüm modeller
9. Benchmark + W&B        — metrik karşılaştırma, report, artifact
10. Yayın                 — HF Dataset, Kaggle, README, W&B report
11. Showcase dashboard    — Streamlit / HF Space
```

### Öncelikli Task'lar

| Öncelik | Task | Faz Grubu |
|---------|------|-----------|
| ★★★ | Tyre Degradation | İlk işlenecek — en güçlü regression showcase |
| ★★★ | Lap Time Prediction | Time-series forecasting, leakage kontrolü kritik |
| ★★ | Overtake Prediction | Binary classification, class imbalance challenge |
| ★★ | Pit Strategy | Supervised → ileride RL'ye bağlanacak |
| ★ | Anomaly Detection | Unsupervised, veri kalitesi için temel |
| ★ | Driver Performance | Analytics ağırlıklı, ML opsiyonel |

---

## 19. README Taslağı

```markdown
# 🏎️ F1 Analytics Lab

**Dataset Collection, EDA, Outlier Analysis & ML Benchmarks from Formula 1 Telemetry**

[![HuggingFace](https://img.shields.io/badge/🤗-Dataset-blue)](link)
[![Kaggle](https://img.shields.io/badge/📊-Kaggle-blue)](link)
[![W&B](https://img.shields.io/badge/📈-W&B-orange)](link)
[![License: MIT](https://img.shields.io/badge/License-MIT-green)](LICENSE)

## What is this?

A comprehensive data science and ML engineering project that:
- Extracts and cleans historical F1 telemetry data (2018–2026)
- Performs extensive EDA and outlier analysis
- Produces ML-ready datasets for 6 different tasks
- Benchmarks Logistic Regression, Random Forest, XGBoost, LightGBM, and CatBoost
- Publishes everything on HuggingFace, Kaggle, and W&B

## Why?

F1 data is incredibly rich but notoriously messy. This project builds a reusable pipeline that transforms raw telemetry into ML-ready datasets — with proper leakage control, domain-specific feature engineering, and careful split strategies.

## Datasets

| Dataset | Task | Samples | Target |
|---------|------|---------|--------|
| Tyre Degradation | Regression | ~25K | lap_time_delta |
| Lap Time Prediction | Regression | ~250K | next_lap_time |
| Overtake Prediction | Binary CLF | ~5K | overtake_success |
| Pit Strategy | Binary CLF | ~3K | position_gain |
| Anomaly Events | Analytics | ~300K | outlier_type |
| Driver Performance | Analytics | ~100K | normalized_pace |

## Pipeline

```
Fast-F1 → Extract → Clean → EDA → Feature Engineering → Dataset Factory → ML Benchmarks → Publish
```

## EDA Highlights

[EDA figürleri gömülü]

## Model Benchmarks

| Task | Best Model | ROC-AUC / R² | Train Time |
|------|------------|--------------|------------|
| Overtake | LightGBM | 0.85 AUC | 8s |
| Tyre Deg. | CatBoost | 0.78 R² | 90s |
| Lap Time | XGBoost | 0.92 R² | 45s |
| Pit Strategy | LightGBM | 0.72 AUC | 5s |

## Quick Start

```bash
git clone https://github.com/enesdemir/f1-analytics-lab
cd f1-analytics-lab
uv sync
python scripts/build_all_datasets.py
python scripts/train_all_models.py
```

## Reproducibility

All experiments are tracked with fixed seeds. Splits are deterministic. W&B logs every run.
Full reproduction: `uv run scripts/train_all_models.py`

## Links

- 🤗 HuggingFace Dataset: [enesdemir/f1-analytics-dataset](link)
- 📊 Kaggle Dataset: [enesdemir143/f1-analytics-dataset](link)
- 📈 W&B Project: [f1-analytics-lab](link)
- 🏎️ Live Demo: [HF Space](link) *(coming soon)*

## Future Work

- RL-based pit strategy simulator
- RAG-powered FIA rules explorer
- LLM automated race reports
- GitHub Actions auto-update pipeline

## License

MIT
```

---

## 20. CV Entegrasyonu

### CV'ye Yazılacak Blok

```markdown
**F1 Analytics Lab** | Python, Fast-F1, Pandas, Scikit-learn, XGBoost,
LightGBM, CatBoost, W&B, HuggingFace, Kaggle

- Built a reusable data pipeline that extracts, cleans, and validates
  historical Formula 1 telemetry, lap, tyre, weather, pit stop, and
  race-status data (2018–2026, 200+ Grand Prix weekends) using Fast-F1.
- Created 6 ML-ready datasets for tyre degradation modeling, lap time
  prediction, overtake prediction, pit strategy analysis, anomaly
  detection, and driver performance analysis — with task-specific
  filtering, leakage-aware feature engineering, and temporal/circuit
  holdout splits.
- Performed extensive EDA and outlier analysis to identify and explain
  pit-lap effects, safety-car periods, abnormal stint behavior, tyre
  degradation patterns, and circuit-specific pace differences.
- Benchmarked Logistic Regression, Random Forest, XGBoost, LightGBM,
  and CatBoost across classification and regression tasks with W&B
  experiment tracking, achieving ROC-AUC 0.85 on overtake prediction
  and R² 0.92 on lap time forecasting.
- Published curated datasets and reproducible benchmark notebooks on
  HuggingFace and Kaggle, with dataset cards, target schemas, and
  domain generalization analysis.
```

### CV'de Anlattığı Hikaye

| Yetkinlik | Projedeki Karşılığı |
|-----------|---------------------|
| **Veri pipeline'ı** | Fast-F1 → extract → clean → validate → Parquet |
| **EDA ve outlier analizi** | 6 tip outlier, kapsamlı EDA raporu |
| **Feature engineering** | Rolling, tyre, weather, domain-specific |
| **Classification benchmark** | 5 model, 2 task, W&B tracking |
| **Regression benchmark** | 5 model, 2 task, residual analizi |
| **Domain generalization** | Temporal split, circuit holdout, driver leakage test |
| **Leakage control** | Task'a özel filtreleme, gelecek bilgisi audit |
| **HuggingFace ekosistemi** | Dataset + Space (sonra) |
| **Kaggle** | Dataset yayını + notebook |
| **W&B** | Experiment tracking, model registry, reports |
| **Reproducibility** | Tek komutla baştan sona pipeline |

---

## Referanslar

- [Fast-F1 GitHub](https://github.com/theOehrly/Fast-F1) — veri kaynağı
- [F1 StratLab](https://github.com/VforVitorio/F1-StratLab) — referans mimari (farklı problem)
- [pk2971/F1-dashboards](https://github.com/pk2971/F1-dashboards) — Streamlit dashboard referansı
- [HuggingFace Datasets](https://huggingface.co/docs/datasets) — dataset yayınlama
- [Weights & Biases](https://wandb.ai/) — experiment tracking

---

*Son güncelleme: 2026-05-27 — Stratejik pivot: Dashboard-merkezli → Dataset/Benchmark-merkezli.*
