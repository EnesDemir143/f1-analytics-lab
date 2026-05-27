# Phase 1 — Proje İskeleti

**Amaç:** Çalıştırılabilir boş proje. Tek bir `uv run` ile "hello world" verir.

## D-01: Lap-level öncelikli strateji
Tüm proje lap-level veriyle çalışacak. Telemetri sadece overtake penceresi için Faz 4'te.
Bu karar tüm src/data/ modüllerinin tasarımını etkiler.

## D-02: Arayüz son fazda
Dashboard Faz 10'da. İlk 9 faz arayüzsüz, tamamen pipeline + analiz + model.

## D-05: uv paket yöneticisi
Python environment yönetimi için uv kullanılacak. pyproject.toml bazlı.

---

## Tasks

<task type="auto">
  <name>Repo ve GitHub init</name>
  <files>.gitignore, README.md</files>
  <action>
    1. Proje dizininde git init
    2. .gitignore oluştur: __pycache__, .venv, data/raw/*, .env, *.pyc, .DS_Store, wandb/
    3. README.md taslağı yaz: başlık, one-liner, datasets, pipeline, quick start
    4. GitHub'da enesdemir/f1-analytics-lab repo oluştur
    5. İlk commit: "init: f1-analytics-lab project skeleton"
  </action>
  <verify>git status temiz; GitHub repo URL'si erişilebilir</verify>
  <done>Repo oluşturuldu, README taslağı yazıldı, ilk commit atıldı</done>
</task>

<task type="auto">
  <name>pyproject.toml ve uv environment</name>
  <files>pyproject.toml, uv.lock</files>
  <action>
    1. pyproject.toml oluştur:
       - [project]: name=f1-analytics-lab, requires-python>=3.11
       - dependencies: pandas, numpy, fastf1, scikit-learn, xgboost, lightgbm, catboost,
         matplotlib, seaborn, plotly, wandb, jupyter, pyarrow, pyyaml
       - [tool.uv]: dev-dependencies pytest
    2. uv sync (ortamı kur, lockfile oluştur)
    3. uv run python -c "import pandas; print('ok')" ile test et
  </action>
  <verify>uv sync hatasız; tüm dependency'ler import edilebiliyor</verify>
  <done>pyproject.toml hazır, uv environment kurulu, tüm paketler import edilebiliyor</done>
</task>

<task type="auto">
  <name>Config dosyaları</name>
  <files>configs/data.yaml, configs/features.yaml, configs/models.yaml, configs/wandb.yaml</files>
  <action>
    1. configs/data.yaml: seasons [2018-2026], sessions [R, Q, FP2], cache_dir
    2. configs/features.yaml: hangi feature set'leri aktif (tyre, rolling, weather, overtake, pit)
    3. configs/models.yaml: her model için default hyperparam'lar
    4. configs/wandb.yaml: entity=enesdemir, project=f1-analytics-lab
    5. src/utils/config.py: YAML okuyucu (path çözümlemeli)
  </action>
  <verify>Tüm YAML'ler geçerli; config.py ile okunabiliyor</verify>
  <done>4 config YAML + config okuyucu hazır</done>
</task>

<task type="auto">
  <name>src/ dizin iskeleti</name>
  <files>src/__init__.py, src/data/__init__.py, src/features/__init__.py, ...</files>
  <action>
    1. Tüm __init__.py dosyalarını oluştur:
       src/__init__.py
       src/data/__init__.py
       src/features/__init__.py
       src/tasks/__init__.py
       src/models/__init__.py
       src/visualization/__init__.py
       src/utils/__init__.py
    2. src/utils/paths.py: proje root bulan path resolver
    3. src/utils/seed.py: set_seed(42) fonksiyonu
    4. src/utils/logging.py: logger konfigürasyonu
  </action>
  <verify>Tüm __init__.py'ler mevcut; paths.py proje root'u doğru buluyor</verify>
  <done>src/ dizin iskeleti tamam, utils modülleri hazır</done>
</task>

<task type="auto">
  <name>data/ klasör yapısı</name>
  <files>data/raw/.gitkeep, data/interim/.gitkeep, data/processed/.gitkeep, data/external/.gitkeep</files>
  <action>
    1. data/raw/, data/interim/, data/processed/, data/external/ oluştur
    2. Her klasöre .gitkeep koy
    3. .gitignore'a data/raw/*, data/interim/* ekle (büyük dosyalar)
    4. data/external/ içine circuit_drs_zones.csv (manuel) ekle (opsiyonel, sonra)
  </action>
  <verify>Klasörler mevcut; .gitignore doğru</verify>
  <done>data/ klasör yapısı hazır</done>
</task>

<task type="auto">
  <name>W&B project + .env</name>
  <files>.env.example, scripts/</files>
  <action>
    1. scripts/ klasörü oluştur
    2. W&B'de enesdemir/f1-analytics-lab project'i aç
    3. .env.example: WANDB_API_KEY=, HF_TOKEN=, KAGGLE_USERNAME=, KAGGLE_KEY=
    4. .env .gitignore'a eklendi mi kontrol et
  </action>
  <verify>W&B project URL'si erişilebilir; .env.example mevcut</verify>
  <done>W&B project açıldı, .env.example hazır</done>
</task>
