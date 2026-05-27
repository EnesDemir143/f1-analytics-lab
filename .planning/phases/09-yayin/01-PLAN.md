# Phase 9 — Yayın

**Amaç:** Dataset ve sonuçları HuggingFace, Kaggle ve GitHub'da public hale getir.
**Bağımlılık:** Faz 4-8 (tüm dataset ve benchmark sonuçları hazır)

---

## Tasks

<task type="auto">
  <name>HuggingFace Dataset</name>
  <files>scripts/publish_hf.py</files>
  <action>
    1. HF'de enesdemir/f1-analytics-dataset reposu oluştur
    2. Her dataset için config:
       - f1_tyre_degradation: train/val/test.parquet
       - f1_lap_time_prediction: train/val/test.parquet
       - f1_overtake_prediction: train/val/test.parquet
       - f1_pit_strategy: train/val/test.parquet
       - f1_anomaly_events: all.parquet
    3. Dataset card (her config için):
       - Dataset description
       - Data source (Fast-F1)
       - Schema (tüm kolonlar, tipler, açıklamalar)
       - Target definition
       - Feature definitions
       - Known limitations
       - Leakage warnings
       - Example usage (Python kodu)
       - Citation
    4. huggingface_hub kütüphanesi ile push
    5. HF token'ı .env'den oku
  </action>
  <verify>HF dataset URL'si erişilebilir; tüm config'ler yüklenebiliyor; dataset card render ediliyor</verify>
  <done>HF Dataset yayınlandı: enesdemir/f1-analytics-dataset</done>
</task>

<task type="auto">
  <name>Kaggle Dataset</name>
  <files>scripts/publish_kaggle.py</files>
  <action>
    1. Kaggle'da enesdemir143/f1-analytics-dataset oluştur
    2. HF'teki aynı Parquet dosyalarını CSV olarak da koy (Kaggle kullanıcıları için)
    3. Dataset description (Kaggle'a özel format)
    4. Example usage notebook: kaggle_notebook.ipynb
       - Veriyi yükleme
       - Basit EDA
       - Örnek model eğitimi
    5. Kaggle API ile push
  </action>
  <verify>Kaggle dataset URL'si erişilebilir; notebook çalışıyor</verify>
  <done>Kaggle Dataset yayınlandı: enesdemir143/f1-analytics-dataset</done>
</task>

<task type="auto">
  <name>GitHub README Final</name>
  <files>README.md</files>
  <action>
    1. README'yi tamamla:
       - Proje açıklaması
       - EDA figürleri (gömülü PNG, reports/figures/)
       - Model benchmark tablosu (markdown)
       - Dataset şeması
       - How to reproduce
       - HF/Kaggle/W&B linkleri
       - Badge'ler: HF Dataset, Kaggle, W&B, License
       - Future work
    2. Tüm linklerin çalıştığını kontrol et
    3. Son commit: "release: v0.1.0 — datasets + benchmarks published"
  </action>
  <verify>README eksiksiz; tüm linkler çalışıyor; badge'ler render ediliyor</verify>
  <done>GitHub README finalize edildi, tüm linkler aktif</done>
</task>

<task type="auto">
  <name>Reproducibility Script</name>
  <files>scripts/publish_all.py</files>
  <action>
    1. scripts/publish_all.py: tek komutla tüm yayın işlemleri
    2. Sırayla: HF push → Kaggle push → README kontrol
    3. Progress ve error handling
  </action>
  <verify>uv run scripts/publish_all.py hatasız tamamlanıyor</verify>
  <done>Tek komutla yayın pipeline'ı hazır</done>
</task>
