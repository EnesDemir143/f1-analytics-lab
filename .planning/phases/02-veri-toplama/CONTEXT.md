# CONTEXT — Faz 2: Veri Toplama Pipeline'ı

**Created:** 2026-05-27 | **Phase:** 2 | **Status:** locked
**Depends on:** Faz 1 (src/ iskeleti, config, utils, pyproject.toml)

## Prior Decisions

| ID | Karar | Bu Faza Etkisi |
|----|-------|---------------|
| D-01 | Lap-level öncelikli | Telemetri (`load_telemetry()`) bu fazda KULLANILMAYACAK. Sadece `session.load()`. |
| D-04 | Outlier silinmez, flag'lenir | Bu fazda outlier handling YOK. Ham veri olduğu gibi interim'e yazılır. |
| R1.1 | 2018-2026 tüm race session'ları | fetch_fastf1.py bu aralığı kapsamalı |

## Gray Areas (Resolved)

### GA-01: Hangi session tipleri?
**Decision:** R (Race), Q (Qualifying), FP2. FP1/FP3 temsili düşük, sprint weekend'lerinde FP2 yerine Sprint var.
Config'den override edilebilir: `configs/data.yaml → sessions`.

### GA-02: Fast-F1 rate limiting
**Decision:** Fast-F1 internal rate limit var (3 sn). fetch_fastf1.py'de ek sleep gerekmez.
Ama network timeout için retry mantığı eklenecek (3 deneme, exponential backoff).

### GA-03: Weather join stratejisi
**Decision:** `pd.merge_asof(direction='nearest')` — her turun başlangıç zamanına en yakın weather sample.
Weather ~30 sn'de bir örneklendiği için her tura bir weather satırı denk gelir.

### GA-04: is_valid_lap tanımı (başlangıç)
**Decision:** Basit kural seti:
- lap_time > 0 AND < circuit_record * 1.4
- compound not null
- driver not null
Faz 3'te iyileştirilecek (pit/SC/VSC flag'leri eklenince).

### GA-05: Parquet vs CSV
**Decision:** Parquet — sıkıştırma (daha küçük), şema gömülü, hızlı okuma, pandas native.

### GA-06: DRS zone bilgisi nereden?
**Decision:** Şimdilik data/external/circuit_drs_zones.csv (manuel). Fast-F1'in `get_circuit_info()` API'si tam DRS zone bilgisi vermiyor.
Faz 6'da overtake için gerekli olacak. Faz 2'de circuits.parquet'e temel bilgiler yazılır.

## Constraints

- `session.load()` her session için ~2-5 sn sürer. ~200 session → ~10 dk.
- Fast-F1 cache aktif olmazsa her seferinde yeniden indirir — cache MUTLAKA aktif olmalı.
- Eski sezonlarda (2018-2019) weather_data eksik olabilir → null handling.
- Eski sezonlarda sector times eksik olabilir → nullable kolonlar.

## Scope Fence

Bu fazda YAPILMAYACAKLAR:
- Veri temizleme (flag'ler, outlier — Faz 3)
- EDA (Faz 4-7)
- Feature engineering (Faz 4-7)
- Model eğitimi (Faz 4-7)
- Telemetri yükleme (`session.load_telemetry()` — Faz 6'da overtake için)
