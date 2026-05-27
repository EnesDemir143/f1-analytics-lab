# Phase 6 — Overtake Prediction ★★

**Amaç:** Takip eden araç önündekini geçecek mi? Binary classification, class imbalance.
**Bağımlılık:** Faz 3 (clean_laps.parquet)
**Pipeline:** EDA → Outlier → Feature Engineering → Dataset → Model Train → Evaluate

## Class Imbalance Uyarısı
Çoğu yakın takip (gap < 1s) geçişle sonuçlanmaz. Tahmini ratio: %25-35 positive.
PR-AUC ve F1, ROC-AUC'den daha önemli. Brier Score ve calibration eğrisi de raporlanacak.

## Overtake Penceresi Tanımı
"Geçiş penceresi": chasing car'ın ahead car'a gap'i < 1.0s olduğu ve DRS bölgesinde bulunduğu an.
Window kapanışı: gap > 1.5s veya DRS bölgesi sonu.
Target: window içinde chasing car ahead car'ı GEÇTİ mi? (pozisyon değişimi)

---

## Tasks

<task type="auto">
  <name>Overtake EDA</name>
  <files>notebooks/06_eda_overtake.ipynb</files>
  <action>
    1. Pistlere göre overtake window sayısı (bar chart, top-10)
    2. Gap < 1s durumların başarı oranı (pie veya bar)
    3. DRS etkisi: DRS açıkken vs kapalıyken geçiş oranı
    4. Speed delta vs overtake success (boxplot: success/fail)
    5. Tyre age delta vs overtake success
    6. Compound advantage vs overtake success
    7. Sektör bazlı: hangi sektörde daha çok overtake?
    8. Gap trend (kapanma hızı) vs success
  </action>
  <verify>8 EDA grafiği; class imbalance oranı belgelendi</verify>
  <done>Overtake EDA tamam, imbalance ratio ~0.3, DRS ve speed delta en güçlü sinyaller</done>
</task>

<task type="auto">
  <name>Overtake Window Detection</name>
  <files>src/tasks/overtake_prediction/detect_windows.py</files>
  <action>
    1. Lap-level gap analizi (telemetriye inmeden):
       - Her tur için her driver pair arası gap (session.laps'tan pozisyon bazlı)
       - NOT: Bu yaklaşık — gerçek gap için telemetri lazım. Ama lap-level başlangıç için yeterli.
    2. Window tanımı: gap < 1.0s AND driver_ahead.position == driver_chasing.position - 1
    3. Window sonucu: window boyunca pozisyon değişti mi?
    4. Edge case: aynı turda birden fazla geçiş → ayrı window
  </action>
  <verify>~5000 overtake penceresi tespit edildi; window başlangıç/bitiş mantıklı</verify>
  <done>Overtake window'ları tespit edildi, target label'landı</done>
</task>

<task type="auto">
  <name>Overtake Feature Engineering</name>
  <files>src/features/overtake_features.py</files>
  <action>
    1. Chasing car features: speed (tahmini, lap_time'dan), compound, tyre_age
    2. Ahead car features: aynı
    3. Pair features:
       - gap_s: chasing - ahead gap (saniye)
       - gap_trend: son 3 sample'da gap değişimi (artıyor/azalıyor)
       - speed_delta_kmh: chasing_speed - ahead_speed
       - closing_rate_ms: gap'in saniyede kaç metre kapandığı
       - tyre_age_delta: chasing_tyre_age - ahead_tyre_age (+ taze)
       - compound_advantage: SOFT=3, MED=2, HARD=1 → diff
    4. Context features:
       - drs_zone_length_m (circuit metadata'dan)
       - distance_to_corner_m (DRS zone sonuna mesafe)
       - track_status (encoder)
       - track_temp
  </action>
  <verify>Tüm feature'lar hesaplandı; leakage yok (window sonrası bilgi feature'da yok)</verify>
  <done>Overtake feature set'i hazır, 12+ feature</done>
</task>

<task type="auto">
  <name>Overtake Dataset + Split</name>
  <files>src/tasks/overtake_prediction/build_dataset.py</files>
  <action>
    1. Target: overtake_success = 0/1
    2. Temporal split: train 2018-22, val 2023, test 2024-26
    3. Stratified split (class imbalance nedeniyle)
    4. Kaydet: data/processed/f1_overtake_prediction/{train,val,test}.parquet
    5. Dataset card: class ratio, feature descriptions, known limitations
  </action>
  <verify>Split'ler arası class ratio tutarlı (~0.3); dataset card yazıldı</verify>
  <done>Overtake dataset'i hazır, stratified split'li</done>
</task>

<task type="auto">
  <name>Overtake Model Training</name>
  <files>src/tasks/overtake_prediction/train.py</files>
  <action>
    1. Modeller: LogisticRegression, RandomForest, XGBoost, LightGBM, CatBoost
       (MLP baseline opsiyonel)
    2. Class imbalance handling: class_weight='balanced' veya scale_pos_weight
    3. W&B logging: config, metrics
    4. Cross-validation: 3-fold stratified time-series
    5. En iyi modeli kaydet
  </action>
  <verify>Tüm classifier'lar eğitildi; W&B'de run'lar; class imbalance handling aktif</verify>
  <done>5 classifier eğitildi, W&B'de</done>
</task>

<task type="auto">
  <name>Overtake Model Evaluation</name>
  <files>src/tasks/overtake_prediction/evaluate.py</files>
  <action>
    1. Test metrikleri: ROC-AUC, PR-AUC, F1, Precision, Recall
    2. Brier Score (calibration)
    3. Calibration curve (her model için)
    4. Confusion matrix
    5. Feature importance (en iyi model)
    6. Per-circuit breakdown
    7. Precision-Recall curve (imbalance'da daha bilgilendirici)
  </action>
  <verify>PR-AUC > 0.5 (random'dan iyi); calibration curve makul; top feature speed_delta</verify>
  <done>Overtake evaluation tamam, PR-AUC ve calibration vurgulu</done>
</task>
