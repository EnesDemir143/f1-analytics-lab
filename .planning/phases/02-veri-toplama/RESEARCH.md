# RESEARCH — Faz 2: Veri Toplama Pipeline'ı

**Phase:** 2 | **Researcher:** gsd-phase-researcher | **Date:** 2026-05-27

## Fast-F1 API Research

### Session Loading

```python
import fastf1

# Cache (MUTLAKA)
fastf1.Cache.enable_cache('data/raw/fastf1_cache')

# Event schedule
schedule = fastf1.get_event_schedule(2024)
# → DataFrame: Round, Country, EventName, EventDate, ...

# Session
session = fastf1.get_session(2024, 'Bahrain', 'R')
session.load()  # lap, weather, track_status yüklenir
# session.load_telemetry()  # BU FAZDA YOK

# Laps
laps = session.laps  # DataFrame
# Kolonlar: Time, Driver, LapTime, Sector1Time, Sector2Time, Sector3Time,
#           Compound, TyreLife, FreshTyre, Stint, LapNumber, Position, ...

# Weather
weather = session.weather_data  # DataFrame
# Kolonlar: Time, AirTemp, TrackTemp, Humidity, WindSpeed, WindDirection, Rainfall

# Track status
track_status = session.track_status  # DataFrame
# Kolonlar: Time, Status, Message

# Results
results = session.results  # DataFrame
# Kolonlar: DriverNumber, BroadcasterName, Abbreviation, TeamName, Position, ...
```

### Event Bilgileri

`session.event` dictionary:
```python
{
    'EventName': 'Bahrain Grand Prix',
    'Country': 'Bahrain',
    'EventDate': datetime,
    'RoundNumber': 1,
    'OfficialEventName': 'FORMULA 1 GULF AIR BAHRAIN GRAND PRIX 2024',
    ...
}
```

## Lap Table Schema Mapping

| Fast-F1 Kolonu | Bizim Kolon | Tip | Not |
|---------------|------------|-----|-----|
| Time | lap_start_time | datetime | Weather join için |
| Driver | driver | str (3 char) | LEC, HAM, VER... |
| LapTime | lap_time | float (seconds) | timedelta → seconds |
| Sector1Time | sector1_time | float | Nullable (eski sezon) |
| Sector2Time | sector2_time | float | Nullable |
| Sector3Time | sector3_time | float | Nullable |
| Compound | compound | str | Nullable (eski sezon) |
| TyreLife | tyre_life | int | Nullable |
| Stint | stint | int | |
| LapNumber | lap_number | int | |
| PitInTime | pit_in | bool | timedelta → bool |
| PitOutTime | pit_out | bool | timedelta → bool |
| TrackStatus | track_status | str | "1"→Green, mapping |
| Position | position | int | |
| Team | team | str | session.results'ten join |
| IsDeleted | is_deleted | bool | |

## Weather Merge Strategy

```python
# Her turun başlangıç zamanına en yakın weather sample
import pandas as pd

laps_sorted = laps.sort_values('lap_start_time')
weather_sorted = weather_data.sort_values('Time')

merged = pd.merge_asof(
    laps_sorted,
    weather_sorted[['Time', 'AirTemp', 'TrackTemp', 'Humidity', 
                     'WindSpeed', 'WindDirection', 'Rainfall']],
    left_on='lap_start_time',
    right_on='Time',
    direction='nearest'
)
```

## Track Status Mapping

Fast-F1'in track status kodları:
```
'1' = Green / Track Clear
'2' = Yellow Flag (Sector)
'4' = Safety Car (SC)
'5' = Virtual Safety Car (VSC)
'6' = Red Flag
```

Yeni mapping (string, daha okunur):
```python
STATUS_MAP = {
    '1': 'Green',
    '2': 'Yellow', 
    '4': 'SC',
    '5': 'VSC',
    '6': 'Red'
}
```

## Error Handling Pattern

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=2))
def load_session_safe(year, gp, session_type):
    session = fastf1.get_session(year, gp, session_type)
    session.load()
    return session
```

## Riskler

| Risk | Olasılık | Etki | Mitigation |
|------|---------|------|-----------|
| 2026 sezonu devam ediyor, eksik yarışlar | Kesin | Düşük | fetch hatasında skip, continue |
| Eski sezonlarda weather/track_status eksik | Yüksek | Orta | Null handling, merge_asof'da fallback |
| Fast-F1 internal rate limit (3 sn) | Kesin | Düşük | Built-in handling var, ek sleep gerekmez |
| Network timeout (uzun süren indirme) | Orta | Orta | Retry 3× exponential backoff |
| Bellek: ~200 session × lap verisi | Düşük | Düşük | ~300K satır, pandas'ta ~50MB — sorun değil |
