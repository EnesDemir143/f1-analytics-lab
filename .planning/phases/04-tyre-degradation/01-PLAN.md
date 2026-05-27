# Phase 4 — Tyre Degradation ★★★

**Amaç:** Lastik aşınmasının tur zamanına etkisini modelle. En güçlü regression showcase.
**Bağımlılık:** Faz 3 (clean_laps.parquet, clean_stints.parquet hazır)
**Pipeline:** EDA → Outlier → Feature Engineering → Dataset → Model Train → Evaluate

## D-03: Temporal split (ilk kez bu fazda uygulanacak)
Train: 2018-2022 | Val: 2023 | Test: 2024-2026
Circuit holdout ek deney olarak yapılacak.

## Önemli: Bu task'ta hangi lap'ler kullanılır?
- SADECE is_valid_lap=True
- pit_lap ÇIKARILIR
- SC/VSC lap ÇIKARILIR
- rain lap ÇIKARILIR
- İlk tur (Lap 1) ÇIKARILIR (start chaos)

---

## Tasks

<task type="auto">
  <name>Tyre Degradation EDA</name>
  <files>notebooks/04_eda_tyre.ipynb, src/visualization/eda_plots.py</files>
  <action>
    1. Compound bazlı ortalama tyre_life (bar chart)
    2. Tyre_age vs lap_time scatter (her compound için ayrı renk, loess trend çizgisi)
    3. Track temperature vs degradation rate (renk: compound)
    4. Circuit bazlı degradation farkı (top-10 pist, boxplot)
    5. Stint başı vs stint sonu pace farkı (bar chart, per compound)
    6. Soft vs Medium vs Hard: degradation eğrisi karşılaştırması (tek grafikte 3 eğri)
    7. Compound değişimi etkisi: MED→HARD geçişte pace kaybı
    8. Tüm grafikleri reports/figures/ altına kaydet
  </action>
  <verify>8 grafik üretildi; her biri anlamlı pattern gösteriyor</verify>
  <done>Tyre EDA tamam, tüm grafikler reports/figures/ altında</done>
</task>

<task type="auto">
  <name>Tyre Outlier Analizi</name>
  <files>src/tasks/tyre_degradation/outlier_analysis.py</files>
  <action>
    1. Tyre-spesifik outlier tipleri:
       - Aşırı degradation: stint içinde pace_loss > expected × 2
       - Anormal stint uzunluğu: stint_length < expected × 0.4 veya > 2×
       - Compound anomalisi: beklenmeyen compound'da anormal pace
    2. Yöntem: per-driver per-circuit per-compound rolling stats
    3. Her outlier için: lap_id, outlier_score, outlier_type, reason
    4. Görselleştir: outlier'ları degradation eğrisinde kırmızı işaretle
  </action>
  <verify>Outlier events tespit edildi; degradation grafiğinde işaretlenebiliyor</verify>
  <done>Tyre outlier'ları tespit edildi, etiketlendi</done>
</task>

<task type="auto">
  <name>Tyre Feature Engineering</name>
  <files>src/features/tyre_features.py</files>
  <action>
    1. compound_encoded: SOFT=3, MEDIUM=2, HARD=1 (ordinal)
    2. tyre_age_normalized: tyre_age / expected_tyre_life (per compound)
    3. stint_progress: tyre_age / stint_length (0-1, stint'in ne kadarı kaldı)
    4. degradation_rate: son N turdaki pace kaybı (rolling slope)
    5. tyre_age_x_track_temp: interaction feature
    6. stint_length_so_far: o ana kadarki stint uzunluğu
    7. lap_number, race_progress (lap_number / total_laps)
    8. previous_3_lap_mean, previous_3_lap_std
    9. Fuel proxy: race_progress × estimated_fuel_effect (lineer)
    10. driver, team, circuit: label encoding
    
    NOT: lap_time_raw feature olarak kullanılMAZ (target'ı hesaplamada kullanılıyor)
  </action>
  <verify>Tüm feature'lar hesaplanıyor; NaN yok; value range'ler mantıklı</verify>
  <done>15+ tyre feature'ı hazır, leakage kontrolü yapıldı</done>
</task>

<task type="auto">
  <name>Tyre Degradation Dataset</name>
  <files>src/tasks/tyre_degradation/build_dataset.py</files>
  <action>
    1. Target: lap_time_delta = current_lap_time - stint_opening_pace
       (stint'in ilk geçerli turundaki pace'ten sapma)
    2. Filtre: is_valid_lap AND NOT is_pit_lap AND NOT is_sc_lap AND NOT is_rain_lap
    3. Feature'ları hesapla, target'ı ekle
    4. Temporal split: train 2018-22, val 2023, test 2024-26
    5. Circuit holdout split (ek): Monza/Silverstone/Spa test'te, train'de yok
    6. Leakage audit:
       - Hiçbir feature gelecek tur bilgisi içermiyor mu?
       - stint_opening_pace hesaplanırken sadece GEÇMİŞ turlar kullanılıyor mu?
    7. Kaydet: data/processed/f1_tyre_degradation/{train,val,test}.parquet
  </action>
  <verify>3 split dosyası mevcut; leakage audit temiz; ~25K örnek (temiz turlar)</verify>
  <done>Tyre degradation dataset'i hazır, split'li, leakage audited</done>
</task>

<task type="auto">
  <name>Tyre Degradation Model Training</name>
  <files>src/tasks/tyre_degradation/train.py</files>
  <action>
    1. Modeller: LinearRegression, Ridge, Lasso, RandomForestRegressor,
       XGBRegressor, LGBMRegressor, CatBoostRegressor
    2. Her model için: default hyperparam'larla train
    3. W&B logging: config, metrics, feature_importance
    4. Cross-validation: 3-fold time-series CV (train dönemi içinde)
    5. En iyi modeli kaydet: models/tyre_degradation_best.pkl
  </action>
  <verify>Tüm modeller eğitildi; W&B'de run'lar görünüyor; model dosyası kaydedildi</verify>
  <done>7 regression model eğitildi, W&B'ye loglandı</done>
</task>

<task type="auto">
  <name>Tyre Degradation Evaluation</name>
  <files>src/tasks/tyre_degradation/evaluate.py, src/models/evaluate.py</files>
  <action>
    1. Test setinde tüm modelleri değerlendir
    2. Metrikler: MAE, RMSE, R², MAPE
    3. Per-compound error analizi (hangi compound'da en kötü?)
    4. Per-circuit error analizi (hangi pistte en kötü?)
    5. Residual plot: her model için predicted vs actual scatter
    6. Feature importance: top-10 feature (en iyi model için)
    7. Sonuçları W&B'ye logla
  </action>
  <verify>Test metrikleri hesaplandı; per-compound ve per-circuit breakdown mevcut; residual plot mantıklı</verify>
  <done>Tyre degradation model evaluation tamam, tüm metrikler W&B'de</done>
</task>
