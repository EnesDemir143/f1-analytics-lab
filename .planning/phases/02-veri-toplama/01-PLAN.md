# Phase 2 — Veri Toplama Pipeline'ı

**Amaç:** Fast-F1'den 2018-2026 sezon verilerini çek, interim Parquet olarak kaydet.
**Bağımlılık:** Faz 1 (src/ iskeleti, config, utils)

## D-01 tekrarı: Lap-level öncelikli
Tüm build modülleri lap-level çalışır. Telemetri (`session.load_telemetry()`) bu fazda kullanılmaz.
Sadece `session.load()` yeterli — lap, weather, track_status.

## Önemli: Fast-F1 Cache
Fast-F1'in yerleşik cache mekanizması kullanılacak. `fastf1.Cache.enable_cache(cache_dir)` ile.
Aynı veriyi tekrar indirmez. Cache dizini: `data/raw/fastf1_cache/`

---

## Tasks

<task type="auto">
  <name>fetch_fastf1.py — Session iterator ve cache</name>
  <files>src/data/fetch_fastf1.py</files>
  <action>
    1. fastf1.Cache.enable_cache('data/raw/fastf1_cache')
    2. get_seasons(): config'den sezon listesini oku
    3. get_events(season): fastf1.get_event_schedule(season)
    4. get_sessions(event, types=['R', 'Q', 'FP2']): session objelerini döndür
    5. Ana iterator: for session in iter_sessions(start=2018, end=2026, types=['R']):
       session.load()  # lap, weather, track_status — telemetri DEĞİL
    6. Progress bar (tqdm) ve error handling (tek session fail olursa devam et)
    7. Retry: network timeout için 3 deneme
  </action>
  <verify>iter_sessions(2024, 2024, ['R']) 2024 sezonu tüm yarışları döndürüyor; cache çalışıyor</verify>
  <done>Session iterator hazır, cache aktif, error handling var</done>
</task>

<task type="auto">
  <name>build_sessions.py — Session metadata</name>
  <files>src/data/build_sessions.py</files>
  <action>
    1. session.event bilgilerinden: season, round, country, circuit_name, session_type, date
    2. session.results'ten: driver, team, grid_position, finish_position, status
    3. DataFrame'e dönüştür, schema validation
    4. Kaydet: data/interim/sessions.parquet
  </action>
  <verify>sessions.parquet'te 500+ satır; şema: season, round, country, circuit, session, date, driver, team, grid, finish</verify>
  <done>sessions.parquet hazır, 2018-2026 tüm GP weekend'leri</done>
</task>

<task type="auto">
  <name>build_laps.py — Ana lap tablosu</name>
  <files>src/data/build_laps.py</files>
  <action>
    1. session.laps DataFrame'i işle
    2. Kolonlar: season, round, grand_prix, session, driver, team, lap_number,
       lap_time, sector1_time, sector2_time, sector3_time, compound, tyre_life,
       stint, pit_in, pit_out, track_status, position
    3. session.weather_data'dan en yakın weather sample'ını merge_asof ile ekle:
       air_temp, track_temp, humidity
    4. is_valid_lap hesapla (başlangıç kural seti):
       - lap_time > 0
       - lap_time < circuit_lap_record * 1.4  (pit/SC için toleranslı)
       - compound not null
       - driver not null
    5. Kaydet: data/interim/laps.parquet
  </action>
  <verify>laps.parquet'te 250K+ satır; tüm kolonlar mevcut; weather join başarılı; is_valid_lap dağılımı mantıklı</verify>
  <done>Ana lap tablosu hazır, weather join'li, is_valid_lap flag'li</done>
</task>

<task type="auto">
  <name>build_stints.py + build_weather.py + build_track_status.py</name>
  <files>src/data/build_stints.py, src/data/build_weather.py, src/data/build_track_status.py</files>
  <action>
    build_stints.py:
      1. session.laps'ten stint başlangıç/bitiş tespit et (compound değişimi + pit_in)
      2. Kolonlar: season, round, driver, stint_number, start_lap, end_lap,
         compound, num_laps, avg_lap_time, stint_start_tyre_age, stint_end_tyre_age
    
    build_weather.py:
      1. session.weather_data'dan: Time, AirTemp, TrackTemp, Humidity, WindSpeed, WindDirection, Rainfall
      2. Kaydet: data/interim/weather.parquet
    
    build_track_status.py:
      1. session.track_status'tan: Time, Status, Message
      2. Status mapping: 1=Green, 2=Yellow, 4=SC, 5=VSC, 6=Red
      3. Kaydet: data/interim/track_status.parquet
  </action>
  <verify>stints.parquet 3K+ satır; weather.parquet timestamp'li; track_status event'leri doğru mapped</verify>
  <done>Stint, weather, track_status tabloları hazır</done>
</task>

<task type="auto">
  <name>build_drivers.py + build_circuits.py — Metadata</name>
  <files>src/data/build_drivers.py, src/data/build_circuits.py</files>
  <action>
    build_drivers.py:
      1. session.results'tan: driver_code, driver_name, team, season
      2. Her sezon için driver-team mapping
      3. Kaydet: data/interim/drivers.parquet
    
    build_circuits.py:
      1. session.event'ten: circuit_name, country, num_laps
      2. DRS zone bilgisi: manuel olarak data/external/circuit_drs_zones.csv'den
         (veya fastf1'in get_circuit_info() API'sinden)
      3. Kaydet: data/interim/circuits.parquet
  </action>
  <verify>drivers.parquet: tüm pilotlar + sezon bazlı takım; circuits.parquet: tüm pistler + DRS zone</verify>
  <done>Driver ve circuit metadata tabloları hazır</done>
</task>

<task type="auto">
  <name>validators.py — Schema validation</name>
  <files>src/data/validators.py</files>
  <action>
    1. validate_laps(df): zorunlu kolonlar, veri tipleri, value ranges
       - lap_time > 0 and < 300
       - compound in {SOFT, MEDIUM, HARD, INTERMEDIATE, WET, UNKNOWN}
       - driver not null and len(driver) == 3
    2. validate_all(): tüm interim Parquet'leri oku, validate et, rapor üret
    3. validation_report(): kaç satır, kaç hata, hangi kolonda sorun var
  </action>
  <verify>validate_all() çalışıyor; rapor üretiyor; bilinen edge case'leri yakalıyor</verify>
  <done>Schema validator hazır, tüm interim dosyalarını denetliyor</done>
</task>

<task type="auto">
  <name>End-to-end build script</name>
  <files>scripts/build_all_interim.py</files>
  <action>
    1. scripts/build_all_interim.py oluştur
    2. Sırayla tüm build modüllerini çağır:
       fetch → sessions → laps → stints → weather → track_status → drivers → circuits
    3. Sonunda validate_all() çağır
    4. Progress bar + summary: kaç session, kaç lap, süre
    5. uv run scripts/build_all_interim.py ile çalışabilmeli
  </action>
  <verify>uv run scripts/build_all_interim.py hatasız tamamlanıyor; tüm .parquet'ler mevcut</verify>
  <done>Tek komutla tüm veri pipeline'ı çalışıyor</done>
</task>
