# CONTEXT — Faz 1: Proje İskeleti

**Created:** 2026-05-27 | **Phase:** 1 | **Status:** locked

## Prior Decisions (PROJECT.md'den)

| ID | Karar | Bu Faza Etkisi |
|----|-------|---------------|
| D-05 | uv paket yöneticisi | pyproject.toml uv formatında olacak |
| D-01 | Lap-level öncelikli | src/data/ modülleri lap-level çalışacak şekilde iskeletlenmeli |
| D-02 | Arayüz son fazda | app/ klasörü boş olacak, sadece __init__.py |
| D-06 | Bedava altyapı | W&B free tier, HF CPU Space |

## Gray Areas (Resolved)

### GA-01: Repo ismi
**Decision:** `f1-analytics-lab` — tasarım dökümanında kararlaştırıldı.
GitHub: enesdemir/f1-analytics-lab

### GA-02: Python version
**Decision:** `>=3.11` — Fast-F1 ve modern typing desteği için alt sınır.

### GA-03: Config format
**Decision:** YAML — insan tarafından okunabilir, yorum satırı destekler, pyyaml ile parse.

### GA-04: W&B project adı
**Decision:** `f1-analytics-lab` — repo ile aynı isim, tutarlı.

### GA-05: Veri klasörleri git'te olacak mı?
**Decision:** `data/raw/*` ve `data/interim/*` .gitignore'da. `data/processed/*` commit'lenecek (ML-ready dataset).
`data/external/` commit'lenecek (manuel metadata).

### GA-06: Notebook'lar commit'lenecek mi?
**Decision:** Evet, temiz output'lu. `jupyter nbconvert --clear-output` ile output temizlenip commit.

## Constraints

- pyproject.toml [project] section PEP 621 uyumlu olmalı
- `uv sync` 30 saniyeden kısa sürmeli (ağır CUDA paketleri yok)
- Tüm __init__.py dosyaları boş olabilir veya `from .module import *` içerebilir
- W&B anonymous modda değil, API key ile authenticated

## Scope Fence

Bu fazda YAPILMAYACAKLAR:
- Gerçek veri indirme (Faz 2)
- Herhangi bir ML model eğitimi
- Dashboard/arayüz
- Fast-F1 import (sadece pyproject.toml'da dependency olarak)

Bu fazda YAPILACAKLAR:
- Repo, git, .gitignore, README taslağı
- pyproject.toml + uv.lock
- 4 config YAML
- src/ dizin iskeleti (tüm __init__.py'ler)
- data/ klasör yapısı
- utils (paths, seed, logging, config reader)
- W&B project + .env.example
