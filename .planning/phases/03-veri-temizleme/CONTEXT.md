# CONTEXT — Faz 3: Veri Temizleme + Flag'ler

**Phase:** 3 | **Status:** locked | **Depends on:** Faz 2 (interim Parquet'ler)

## Prior Decisions

| ID | Karar | Etki |
|----|-------|------|
| D-04 | Outlier silinmez, flag'lenir | 7 boolean flag sütunu eklenecek |
| R1.2 | Data Cleaning | Eksik/bozuk/tekrarlı veri tespiti |

## Gray Areas (Resolved)

### GA-01: is_valid_lap final kural seti
**Decision:** pit_lap HARİÇ valid sayılır. Çünkü:
- Tyre degradation: pit lap ÇIKARILIR (task filtresi)
- Pit strategy: pit lap DAHİL (tam da bu lazım)
is_valid_lap = temel fiziksel geçerlilik, task filtresi ≠ is_valid_lap.

### GA-02: Flag isimlendirmesi
**Decision:** `is_` prefix, snake_case: is_pit_lap, is_sc_lap, is_vsc_lap, is_yellow_flag_lap, is_rain_lap, is_deleted_lap, is_outlier_lap.

### GA-03: is_outlier_lap nasıl hesaplanacak?
**Decision:** Faz 3'te basit: Z-score(|lap_time| per driver per circuit) > 3. Faz 4-7'de task-spesifik outlier detection ile iyileştirilecek.

### GA-04: Duplicate stratejisi
**Decision:** İlk bulunanı tut, sonrakileri drop. Log'a yaz (hangi satırlar silindi).

## Constraints

- Eski sezonlarda (2018-2019) bazı kolonlar null olabilir — flag'ler bu durumda False.
- Track status string olarak saklanıyor, flag hesaplarken string karşılaştır.
- SC ve VSC aynı `is_sc_lap` altında (ikisi de overtake yasak).

## Scope Fence

Bu fazda YAPILMAYACAKLAR:
- Task-spesifik outlier detection (Faz 4-7)
- EDA (Faz 4-7)
- Feature engineering (Faz 4-7)
- Model (Faz 4-7)
