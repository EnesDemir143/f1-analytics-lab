# Phase 7 — Pit Strategy + Anomaly Detection ★★

**Amaç:** Pit sonrası pozisyon kazancı tahmini (binary CLF) + outlier detection pipeline'ı tamamlama.
**Bağımlılık:** Faz 3 (clean_laps.parquet, clean_stints.parquet)
**Pipeline:** EDA → Outlier → Feature Engineering → Dataset → Model Train → Evaluate

Bu faz iki alt-task'tan oluşur: Pit Strategy (supervised) ve Anomaly Detection (unsupervised).
Anomaly Detection için model eğitimi yok — detection yöntemleri uygulanıp sonuçlar kaydedilir.

---

## Tasks — Pit Strategy

<task type="auto">
  <name>Pit Strategy EDA</name>
  <files>notebooks/07_pit_strategy_eda.ipynb</files>
  <action>
    1. Pit stop dağılımı: hangi turlarda pit yapılıyor? (histogram)
    2. Compound değişimi: hangi compound'a geçiliyor? (Sankey veya bar)
    3. Pit öncesi/sonrası pozisyon değişimi (scatter: before vs after)
    4. Undercut analizi: rakip pitten önce pit yapıp pozisyon kazananlar
    5. Pit süresi dağılımı (histogram, outlier pit'ler)
    6. Strateji pattern'leri: 1-stop vs 2-stop vs 3-stop (bar per circuit)
  </action>
  <verify>6 grafik; pit strateji pattern'leri belirgin</verify>
  <done>Pit strategy EDA tamam</done>
</task>

<task type="auto">
  <name>Pit Strategy Features + Dataset</name>
  <files>src/features/pit_features.py, src/tasks/pit_strategy/build_dataset.py</files>
  <action>
    Features:
      1. Pit öncesi: position, gap_to_ahead, gap_to_behind, compound, tyre_age, stint_length
      2. Pit: lap_number, pit_duration_s
      3. Pit sonrası (target hesaplama için, FEATURE DEĞİL): position_after
      4. Context: circuit, track_temp, weather
      
    Target:
      position_gain = position_before - position_after (>0 = kazanç)
      → binary: position_gain > 0 ? 1 : 0
    
    Dataset:
      1. Sadece pit yapılan stint'ler
      2. SC/VSC altında pit ÇIKARILIR (zorunlu pit, stratejik değil)
      3. Temporal split
      4. Kaydet: data/processed/f1_pit_strategy/{train,val,test}.parquet
  </action>
  <verify>~3K pit stop; target dağılımı dengeli (~0.5); leakage yok</verify>
  <done>Pit strategy dataset'i hazır</done>
</task>

<task type="auto">
  <name>Pit Strategy Model Train + Evaluate</name>
  <files>src/tasks/pit_strategy/train.py, src/tasks/pit_strategy/evaluate.py</files>
  <action>
    Train: LogisticRegression, RF, XGBoost, LightGBM, CatBoost
    Evaluate: ROC-AUC, F1, Precision, Recall, confusion matrix, feature importance
    W&B logging
  </action>
  <verify>Modeller eğitildi; AUC > 0.65 (random'dan iyi); top feature: gap_to_ahead</verify>
  <done>Pit strategy modeli eğitildi ve değerlendirildi</done>
</task>

---

## Tasks — Anomaly Detection

<task type="auto">
  <name>Anomaly Detection Pipeline</name>
  <files>src/tasks/anomaly_detection/detect_outliers.py, src/tasks/anomaly_detection/classify_outliers.py</files>
  <action>
    1. 6 outlier tipi için detection uygula:
    
       Rule-based:
         - Pit lap: pit_in or pit_out (zaten flag'li, teyit)
         - SC/VSC lap: track_status (zaten flag'li)
         - Rain lap: compound INTER/WET (zaten flag'li)
       
       Statistical:
         - Damage/spin: lap_time_delta > 3× rolling_std AND NOT pit/SC/rain
         - Abnormal sector split: max(|sector_z_score|) > 3 AND others < 1
         - Abnormal degradation: stint içi pace_loss_rate > expected × 2
       
       ML-based:
         - Isolation Forest: tüm lap feature'larıyla unsupervised outlier detection
         - LOF: density-based, local context
         - DBSCAN: cluster + noise (opsiyonel, veri büyük olduğu için seçili yarışlarda)
    
    2. Her yöntemin sonucunu birleştir: 
       - Ensemble: en az 2 yöntem "outlier" dediyse → is_outlier_lap = True
       - outlier_type: en olası sebep (rule-based öncelikli)
    
    3. Kaydet: data/processed/f1_anomaly_events/all.parquet
       Kolonlar: lap_id, outlier_score, outlier_type, outlier_reason, detection_methods
    
    4. Notebook: 06_outlier_analysis.ipynb (güncelle, Faz 3'teki basit versiyonu genişlet)
       - Her outlier tipi için örnek olaylar
       - Outlier dağılımı (per circuit, per season, per driver)
  </action>
  <verify>Tüm yöntemler uygulandı; 6 tip için örnek olaylar notebook'ta; is_outlier_lap dağılımı ~%8-15</verify>
  <done>Anomaly detection pipeline tamam, 6 tip tespit ediliyor, dataset hazır</done>
</task>

<task type="auto">
  <name>Driver Performance Analytics (opsiyonel)</name>
  <files>src/tasks/anomaly_detection/driver_performance.py</files>
  <action>
    1. Aynı compound'da teammate pace karşılaştırması
    2. Clean-air pace (traffic yokken)
    3. Stint consistency: stint içi lap_time std
    4. Qualifying vs race pace gap
    5. Sonuçları tablo olarak kaydet (model eğitimi yok, analytics)
  </action>
  <verify>Driver performance tablosu hazır; teammate comparison anlamlı</verify>
  <done>Driver performance analytics tamam (opsiyonel task)</done>
</task>
