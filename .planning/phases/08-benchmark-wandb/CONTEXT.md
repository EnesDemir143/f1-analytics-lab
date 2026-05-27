# CONTEXT — Faz 8: Benchmark + W&B Report

**Phase:** 8 | **Status:** locked | **Depends on:** Faz 4-7 (tüm modeller eğitilmiş)

## Amaç
Tüm task × model metriklerini tek tabloda topla. Domain generalization (circuit holdout, driver leakage) testlerini yap. W&B comprehensive report oluştur.

## Gray Areas

### GA-01: Circuit holdout pistleri
**Decision:** Monza, Silverstone, Spa-Francorchamps. 3 farklı karakter: düzlük ağırlıklı, hızlı viraj, karma.
Train'de hiç görülmemiş → "yeni piste genelleme" testi.

### GA-02: Driver leakage test
**Decision:** Aynı modelleri iki kez eğit: driver+team feature VAR ve YOK. Fark > %10 ise shortcut öğreniyor.
