# Phase 8 — Benchmark + W&B Report

**Amaç:** Tüm task'ların modellerini karşılaştır, comprehensive benchmark raporu üret.
**Bağımlılık:** Faz 4, 5, 6, 7 (tüm modeller eğitilmiş olmalı)

---

## Tasks

<task type="auto">
  <name>Cross-Task Benchmark Table</name>
  <files>src/models/evaluate.py (güncelle), scripts/run_benchmark.py</files>
  <action>
    1. Tüm task'lar için tüm modellerin test metriklerini tek bir DataFrame'de topla
    2. Classification tasks: overtake, pit_strategy
       Metrikler: ROC-AUC, PR-AUC, F1, Precision, Recall, Brier
    3. Regression tasks: tyre_degradation, lap_time_prediction
       Metrikler: MAE, RMSE, R², MAPE
    4. Markdown tablosu oluştur (GitHub README'ye gömülecek)
    5. Her task için "best model" işaretle (kalın)
  </action>
  <verify>Tabloda tüm task × model hücreleri dolu; best model'ler mantıklı</verify>
  <done>Benchmark tablosu hazır, markdown formatında</done>
</task>

<task type="auto">
  <name>Feature Importance Analizi</name>
  <files>src/visualization/model_plots.py</files>
  <action>
    1. Her task için en iyi modelin top-10 feature importance'ı
    2. Bar chart: feature ismi + importance score
    3. Domain yorumu: en önemli feature fiziksel olarak anlamlı mı?
       Örn: overtake'te speed_delta en önemli → mantıklı
       Örn: tyre'de tyre_age en önemli → mantıklı
  </action>
  <verify>Her task için feature importance grafiği; domain yorumu yazıldı</verify>
  <done>Feature importance analizi tamam</done>
</task>

<task type="auto">
  <name>Calibration + Residual Analizi</name>
  <files>src/visualization/model_plots.py</files>
  <action>
    Classification:
      1. Her model için calibration curve (predicted prob vs actual fraction)
      2. Brier score karşılaştırması
    
    Regression:
      1. Her model için residual plot (predicted vs actual scatter + y=x çizgisi)
      2. Residual dağılımı (histogram, normal dağılıma yakın mı?)
    
    Tüm grafikleri reports/figures/ altına kaydet
  </action>
  <verify>Calibration curve'ler makul; residual'lar normal dağılıma yakın</verify>
  <done>Calibration ve residual analizi tamam</done>
</task>

<task type="auto">
  <name>Domain Generalization Analizi</name>
  <files>scripts/run_domain_tests.py</files>
  <action>
    1. Circuit holdout split sonuçları:
       - Monza, Silverstone, Spa test'te (train'de hiç görülmedi)
       - Temporal split ile karşılaştır: ne kadar kötüleşti?
    
    2. Driver/Team leakage testi:
       - Model A: driver + team feature VAR
       - Model B: driver + team feature YOK
       - Fark < %5 ise → model gerçek dinamiklere bakıyor
       - Fark > %10 ise → model shortcut öğreniyor (raporda belirt)
    
    3. Sonuçları W&B'ye logla, benchmark raporuna ekle
  </action>
  <verify>Circuit holdout metrikleri hesaplandı; driver leakage test sonucu raporlandı</verify>
  <done>Domain generalization analizi tamam, leakage test sonuçları belgelendi</done>
</task>

<task type="auto">
  <name>W&B Comprehensive Report</name>
  <files>reports/model_benchmark_report.md</files>
  <action>
    1. W&B'de "F1 Analytics Lab — Comprehensive Benchmark" report oluştur
    2. İçerik:
       - Project overview
       - Dataset descriptions
       - EDA highlights (gömülü grafikler)
       - Model comparison tables
       - ROC curves, calibration plots
       - Feature importance
       - Residual analysis
       - Domain generalization results
       - Conclusions
    3. Markdown report'u GitHub'a da koy
  </action>
  <verify>W&B report URL'si erişilebilir; markdown report GitHub'da</verify>
  <done>W&B comprehensive report yayınlandı</done>
</task>
