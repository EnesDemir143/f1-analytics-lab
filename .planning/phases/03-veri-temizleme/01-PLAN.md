# Phase 3 — Veri Temizleme + Flag'ler + Validasyon

**Amaç:** Ham veriyi flag'le, eksik/bozuk/tekrarlı verileri temizle, her task'ın kullanacağı temiz tabloları üret.
**Bağımlılık:** Faz 2 (interim Parquet'ler hazır)

## D-04 tekrarı: Outlier silinmez, flag'lenir
Her anormal durum için boolean flag sütunu eklenir. Silme işlemi task bazında yapılır.

## Flag Stratejisi

| Flag | Ne Zaman True? | Neden Flag'lenir? |
|------|---------------|-------------------|
| is_valid_lap | Temel geçerlilik koşulları | Her task'ın ilk filtresi |
| is_pit_lap | pit_in=True veya pit_out=True | Pit strateji analizinde lazım |
| is_sc_lap | track_status='SC' veya 'VSC' | SC etkisi analizi |
| is_rain_lap | compound INTERMEDIATE veya WET | Hava durumu etkisi |
| is_yellow_flag_lap | track_status='Yellow' | Track status analizi |
| is_deleted_lap | FIA tarafından silinmiş | Neden silindiği önemli |
| is_outlier_lap | İstatistiksel anomali | Faz 4-7'de detaylandırılacak |

---

## Tasks

<task type="auto">
  <name>Eksik veri analizi</name>
  <files>notebooks/02_data_cleaning.ipynb</files>
  <action>
    1. Her interim tablo için: df.isnull().sum() / len(df) oranları
    2. En çok eksik olan kolonlar: sırala, nedenini açıkla
       - Örn: sector2_time bazen null (eski sezonlarda sektör verisi yok)
       - Örn: humidity bazen null (eski weather data)
    3. Eksik veri pattern'leri: belirli sezon/pist/session'da mı yoğun?
    4. Rapor: hangi kolonlar zorunlu, hangileri opsiyonel, hangileri impute edilebilir
  </action>
  <verify>Eksik veri raporu notebook'ta tablo + görsel olarak mevcut</verify>
  <done>Eksik veri analizi tamam, hangi kolonların nasıl handle edileceği belirlendi</done>
</task>

<task type="auto">
  <name>Flag sütunlarını ekle</name>
  <files>src/data/build_laps.py (güncelle), src/data/cleaning.py (yeni)</files>
  <action>
    1. src/data/cleaning.py oluştur: add_flags(df) fonksiyonu
    2. Her flag için kural seti:
    
       is_pit_lap: df['pit_in'] == True or df['pit_out'] == True
       is_sc_lap: df['track_status'].isin(['SC', 'VSC'])
       is_rain_lap: df['compound'].isin(['INTERMEDIATE', 'WET'])
       is_yellow_flag_lap: df['track_status'] == 'Yellow'
       is_deleted_lap: df['is_deleted'] == True (varsa)
       
    3. is_valid_lap iyileştir:
       - lap_time > 0 AND lap_time < circuit_record * 1.6
       - compound not in [null, 'UNKNOWN']
       - driver not null
       - NOT is_pit_lap (pit lap her zaman invalid sayılmaz, task'a bağlı — 
         ama valid_lap tanımında pit lap genelde invalid)
       
    4. is_outlier_lap (basit versiyon, Faz 4-7'de detaylanacak):
       - Z-score(|lap_time| per driver per circuit) > 3
       
    5. Tüm flag'leri laps.parquet'e yaz
    6. Kaydet: data/interim/clean_laps.parquet
  </action>
  <verify>Tüm flag sütunları mevcut; her flag için True/False dağılımı mantıklı (örn: is_sc_lap < %5)</verify>
  <done>7 flag sütunu eklendi, clean_laps.parquet hazır</done>
</task>

<task type="auto">
  <name>Duplicate kontrolü ve temizliği</name>
  <files>src/data/cleaning.py</files>
  <action>
    1. Laps için duplicate kontrolü: aynı season+round+session+driver+lap_number
    2. Duplicate varsa: ilkini tut, diğerlerini log'a yaz
    3. Stints için: aynı season+round+driver+stint_number
    4. Sessions için: aynı season+round+session
    5. Rapor: kaç duplicate bulundu, hangi tabloda
  </action>
  <verify>Duplicate raporu; tekrarlı satır kalmadı</verify>
  <done>Duplicate'ler temizlendi, log raporu mevcut</done>
</task>

<task type="auto">
  <name>Schema validation ve temiz veri seti</name>
  <files>src/data/validators.py (güncelle)</files>
  <action>
    1. validators.py güncelle: clean_laps için schema
       - Zorunlu kolonlar: season, round, driver, lap_number, lap_time, compound
       - Opsiyonel: sector_times (eski sezonlarda olmayabilir)
       - Enum kontrolü: compound, track_status
    2. clean_stints.parquet üret (Faz 2 stints'i flag'le)
    3. clean_weather.parquet üret (temizle)
    4. validate_all() güncelle: clean_* dosyalarını da kontrol et
    5. Notebook'a ekle: temizleme öncesi/sonrası karşılaştırma
  </action>
  <verify>validate_all() tüm clean_*.parquet'leri onaylıyor; temiz veri seti hazır</verify>
  <done>Tüm clean tablolar hazır, schema validation'dan geçti</done>
</task>
