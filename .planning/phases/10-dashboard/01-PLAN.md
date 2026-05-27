# Phase 10 — Showcase Dashboard

**Amaç:** Projeyi interaktif vitrin olarak sergile. Ana ürün değil, showcase.
**Bağımlılık:** Faz 4-9 (tüm dataset, model ve benchmark sonuçları hazır)
**Deploy:** HF Space (CPU Basic — BEDAVA)

---

## Tasks

<task type="auto">
  <name>Streamlit App İskeleti</name>
  <files>app/streamlit_app.py, app/requirements.txt</files>
  <action>
    1. Streamlit app ana dosyası: app/streamlit_app.py
    2. Sidebar navigasyon: sayfa seçimi
    3. app/requirements.txt: streamlit, plotly, pandas, numpy, fastf1, pyarrow
    4. HF Space config: README.md (Space için), requirements.txt
    5. Local test: streamlit run app/streamlit_app.py
  </action>
  <verify>streamlit run çalışıyor; sidebar navigasyonu var</verify>
  <done>Streamlit app iskeleti hazır, local'de çalışıyor</done>
</task>

<task type="auto">
  <name>Dataset Explorer Sayfası</name>
  <files>app/pages/dataset_explorer.py</files>
  <action>
    1. Kontroller: Season dropdown, Circuit dropdown, Driver dropdown, Task dropdown
    2. Seçili dataset'in satırlarını göster (dataframe)
    3. Temel istatistikler: row count, null count, unique values
    4. Kolon açıklamaları (tooltip)
  </action>
  <verify>Dataset seçilebiliyor, satırlar gösteriliyor, filtre çalışıyor</verify>
  <done>Dataset Explorer sayfası tamam</done>
</task>

<task type="auto">
  <name>EDA Dashboard Sayfası</name>
  <files>app/pages/eda_dashboard.py</files>
  <action>
    1. Faz 3-7'deki EDA grafiklerini Plotly ile interaktif hale getir:
       - Lap time distribution (per circuit)
       - Tyre degradation curves (per compound)
       - Pit stop distribution
       - Track temperature effects
       - Overtake success rate (per circuit)
    2. Dropdown/checkbox ile filtreleme (season, circuit, compound)
  </action>
  <verify>Tüm grafikler interaktif; filtreler çalışıyor</verify>
  <done>EDA Dashboard sayfası tamam</done>
</task>

<task type="auto">
  <name>Model Benchmark + Overtake Demo Sayfaları</name>
  <files>app/pages/model_benchmark.py, app/pages/overtake_demo.py</files>
  <action>
    Model Benchmark:
      1. Benchmark tablosu (Faz 8'deki markdown → st.dataframe)
      2. ROC curve (seçili task, tüm modeller)
      3. Feature importance bar chart
      4. Calibration curve / Residual plot
    
    Overtake Demo:
      1. 3-5 önceden seçilmiş overtake case
      2. Her case için: driver pair, gap, speed delta, model tahmini, gerçek sonuç
      3. "Tahmin doğru/yanlış" göstergesi
      4. Feature değerleri tablosu
  </action>
  <verify>Benchmark tablosu render ediliyor; overtake demo case'leri anlamlı</verify>
  <done>Model Benchmark ve Overtake Demo sayfaları tamam</done>
</task>

<task type="auto">
  <name>Tyre Degradation Explorer + HF Space Deploy</name>
  <files>app/pages/tyre_explorer.py</files>
  <action>
    Tyre Explorer:
      1. Compound seç, circuit seç, stint seç
      2. Tahmini degradation eğrisi (model prediction) vs gerçek lap time
      3. Tablo: her tur için predicted vs actual
    
    Deploy:
      1. HF Space oluştur: enesdemir/f1-analytics-lab
      2. SDK: Streamlit
      3. app/ dosyasını push et
      4. data/processed/'ten seçili dosyaları Space'e koy (veya HF Dataset'ten load)
      5. Space'in çalıştığını kontrol et
  </action>
  <verify>HF Space URL'si çalışıyor; tyre explorer interaktif</verify>
  <done>Dashboard yayında: HF Space enesdemir/f1-analytics-lab</done>
</task>
