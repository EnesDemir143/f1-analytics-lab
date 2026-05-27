# RESEARCH — Faz 10: Showcase Dashboard

## Streamlit HF Space Deploy

HF Space yapısı:
```
space/
├── app.py                    # Ana Streamlit app
├── requirements.txt          # streamlit, plotly, pandas, fastf1, pyarrow
└── README.md                 # Space açıklaması
```

SDK: Streamlit, Hardware: CPU Basic (BEDAVA)

## Sayfa Yapısı

```python
# app.py
st.set_page_config(page_title="F1 Analytics Lab", layout="wide")

pages = {
    "Dataset Explorer": dataset_explorer_page,
    "EDA Dashboard": eda_dashboard_page,
    "Outlier Explorer": outlier_explorer_page,
    "Model Benchmark": model_benchmark_page,
    "Overtake Demo": overtake_demo_page,
    "Tyre Explorer": tyre_explorer_page,
}

# Sidebar navigation
page = st.sidebar.selectbox("Navigation", list(pages.keys()))
pages[page]()
```

## Riskler
- HF Space CPU 16GB RAM → büyük Parquet'ler sığar (~50MB × 6 = 300MB)
- Plotly interaktif grafikler CPU'da render → WebGL değil SVG, yavaş olabilir
- 2026 sezonu devam ediyor → Space'teki veri güncel değil, statik snapshot
