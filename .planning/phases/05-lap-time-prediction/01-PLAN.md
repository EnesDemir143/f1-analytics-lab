# Phase 5 — Lap Time Prediction ★★★

**Amaç:** Bir sonraki turun süresini tahmin et. Time-series forecasting.
**Bağımlılık:** Faz 3 (clean_laps.parquet), Faz 4 (evaluate.py, W&B pattern)
**Pipeline:** EDA → Outlier → Feature Engineering → Dataset → Model Train → Evaluate

## ⚠️ KRİTİK: Leakage kontrolü
Target `next_lap_time` — gelecek tur. Hiçbir feature gelecek bilgi içeremez.
Özellikle: weather, track_status, compound değişimi gibi "sonraki turda ne olacak" bilgileri feature olamaz.

## Task-spesifik filtre
- SADECE is_valid_lap=True
- pit_lap ÇIKARILIR
- SC/VSC lap ÇIKARILIR
- rain lap ÇIKARILIR
- İlk tur ÇIKARILIR
- SON tur ÇIKARILIR (target next_lap_time hesaplanamaz)

---

## Tasks

<task type="auto">
  <name>Lap Time EDA</name>
  <files>notebooks/05_eda_lap_time.ipynb</files>
  <action>
    1. Lap time dağılımı: per circuit histogram (small multiples)
    2. Valid vs invalid lap karşılaştırması: lap_time farkı
    3. Pit lap etkisi: pit lap normalden ne kadar yavaş? (bar chart: pit lap vs normal lap)
    4. SC/VSC etkisi: SC altında lap_time dağılımı
    5. Rain etkisi: yağmurda lap_time artışı (%)
    6. Yarış içi pace evrimi: race_progress vs lap_time (loess)
    7. Sektör bazlı varyans: hangi sektör daha çok değişiyor?
  </action>
  <verify>7 analiz tamam; grafikler reports/figures/ altında</verify>
  <done>Lap time EDA tamam, anormal durumlar kantifiye edildi</done>
</task>

<task type="auto">
  <name>Lap Time Outlier + Feature Engineering</name>
  <files>src/features/lap_features.py, src/features/rolling_features.py</files>
  <action>
    Outlier (lap time spesifik):
      1. Anormal sector split: bir sektör z-score > 3, diğerleri normal
      2. Aşırı yavaş tur: lap_time > circuit_median × 1.5 (pit/SC hariç)
      3. Aşırı hızlı tur: lap_time < circuit_median × 0.85
      4. Pace sıçraması: |lap_time_delta_from_prev| > 5 × rolling_std
    
    Features:
      1. previous_1_lap_time, previous_3_lap_mean, previous_5_lap_mean
      2. rolling_3_lap_std, rolling_5_lap_std
      3. lap_time_delta_from_prev (current - previous)
      4. pace_trend: last_3_laps slope
      5. race_progress: lap_number / total_laps (0-1)
      6. compound, tyre_age, stint (Faz 4'teki tyre feature'ları)
      7. track_temp, air_temp (o anki — gelecek değil!)
      8. driver, team, circuit (encoded)
  </action>
  <verify>Feature set'i hazır; leakage audit: hiçbir feature sonraki tura ait değil</verify>
  <done>Lap time feature'ları hazır, leakage audited</done>
</task>

<task type="auto">
  <name>Lap Time Dataset</name>
  <files>src/tasks/lap_time_prediction/build_dataset.py</files>
  <action>
    1. Target: next_lap_time (lap_number + 1'in lap_time'ı)
    2. Temporal split: train 2018-22, val 2023, test 2024-26
    3. DİKKAT: Split yaparken sezon sınırında leakage olmaması için:
       - 2022 son turunun next_lap_time'ı 2023'e ait OLAMAZ
       - Her sezon kendi içinde kapalı: son turda target NaN → drop
    4. Kaydet: data/processed/f1_lap_time_prediction/{train,val,test}.parquet
    5. ~200K+ örnek (temiz turlar, son tur hariç)
  </action>
  <verify>Split dosyaları mevcut; sezon sınırı leakage'ı yok; NaN target yok</verify>
  <done>Lap time dataset'i hazır, temporal split doğru</done>
</task>

<task type="auto">
  <name>Lap Time Model Training + Evaluation</name>
  <files>src/tasks/lap_time_prediction/train.py, src/tasks/lap_time_prediction/evaluate.py</files>
  <action>
    Train:
      1. Faz 4'teki aynı model set'i: Linear, Ridge, Lasso, RF, XGB, LGBM, CatBoost
      2. W&B logging: config, metrics
    
    Evaluate:
      1. Test setinde: MAE, RMSE, R², MAPE
      2. Residual analizi: circuit bazlı (hangi pistte en kötü?)
      3. Per-driver MAE: hangi pilot daha öngörülebilir?
      4. Feature importance: top-10
  </action>
  <verify>Test metrikleri hesaplandı; en iyi model XGBoost/LGBM (beklenen); residual normal dağılıma yakın</verify>
  <done>Lap time modeli eğitildi ve değerlendirildi, W&B'ye loglandı</done>
</task>
