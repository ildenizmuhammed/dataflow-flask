# 🎙️ DataFlow Spaces - Sesli Konferans Uygulaması

FreeSWITCH + Flask ile geliştirilmiş modern sesli konferans uygulaması.

## 🚀 Özellikler

- ✅ **Oda Oluşturma**: Kullanıcılar kolayca konferans odaları oluşturabilir
- ✅ **Gerçek Zamanlı Katılım**: WebRTC ile anlık sesli konferans
- ✅ **Modern Arayüz**: Responsive ve kullanıcı dostu tasarım
- ✅ **FreeSWITCH Entegrasyonu**: Güçlü telekomünikasyon altyapısı
- ✅ **MariaDB Desteği**: Güvenilir veritabanı yönetimi
- ✅ **WebSocket**: Gerçek zamanlı güncellemeler

## 🛠️ Teknoloji Stack

- **Backend**: Flask + SQLAlchemy
- **Database**: MariaDB
- **Frontend**: HTML5 + JavaScript + WebRTC
- **Real-time**: Socket.IO
- **Telecom**: FreeSWITCH + mod_conference
- **Web Server**: Nginx

## 📋 Kurulum

### 1. Bağımlılıkları Yükle
```bash
pip install -r requirements.txt
```

### 2. MariaDB Veritabanını Oluştur
```bash
python create_database.py
```

### 3. FreeSWITCH Konfigürasyonu
FreeSWITCH sunucunuzda aşağıdaki dosyaların mevcut olduğundan emin olun:
- `dialplan/default/conference.xml`
- `sip_profiles/webrtc.xml`

### 4. Uygulamayı Başlat
```bash
python index.py
```

## 🌐 Erişim

- **Web Arayüzü**: https://dataflow.mildeniz.space/
- **API Endpoint**: https://dataflow.mildeniz.space/api/

## 📊 Veritabanı Yapısı

### ConferenceRoom Tablosu
- `id`: Benzersiz oda ID'si
- `name`: Oda adı
- `description`: Oda açıklaması
- `created_at`: Oluşturulma tarihi
- `is_active`: Aktif durumu
- `max_participants`: Maksimum katılımcı sayısı
- `current_participants`: Mevcut katılımcı sayısı
- `freeswitch_conference_id`: FreeSWITCH konferans ID'si

### Participant Tablosu
- `id`: Benzersiz katılımcı ID'si
- `name`: Katılımcı adı
- `session_id`: WebRTC session ID'si
- `joined_at`: Katılım tarihi
- `is_muted`: Mute durumu
- `is_moderator`: Moderatör durumu
- `room_id`: Bağlı olduğu oda ID'si

## 🔧 API Endpoints

### Oda Yönetimi
- `GET /api/rooms` - Aktif odaları listele
- `POST /api/rooms` - Yeni oda oluştur
- `GET /api/rooms/<room_id>/participants` - Oda katılımcılarını listele

### Katılım
- `POST /api/rooms/<room_id>/join` - Odaya katıl

### WebRTC
- `POST /api/webrtc/offer` - WebRTC offer işle
- `POST /api/webrtc/ice-candidate` - ICE candidate işle
- `POST /api/webrtc/leave` - Konferanstan çık
- `POST /api/webrtc/mute-status` - Mute durumu güncelle
- `POST /api/webrtc/video-status` - Video durumu güncelle

## 🎯 Kullanım

1. **Oda Oluşturma**: Ana sayfada "Yeni Oda Oluştur" formunu doldurun
2. **Katılım**: Mevcut odalardan birini seçin ve adınızı girin
3. **Konferans**: WebRTC ile sesli konferansa katılın
4. **Kontrol**: Mute/unmute, video açma/kapama özelliklerini kullanın

## 🔒 Güvenlik

- MariaDB bağlantısı şifrelenmiş
- WebRTC güvenli protokol kullanır
- FreeSWITCH Event Socket authentication

## 🐛 Sorun Giderme

### FreeSWITCH Bağlantı Hatası
```bash
# FreeSWITCH Event Socket'in çalıştığından emin olun
telnet localhost 8021
```

### MariaDB Bağlantı Hatası
```bash
# MariaDB servisinin çalıştığından emin olun
systemctl status mariadb
```

### WebRTC Sorunları
- Tarayıcı HTTPS gerektirir
- Mikrofon/kamera izinlerini kontrol edin
- Firewall ayarlarını kontrol edin

## 📝 Geliştirme

### Yeni Özellik Ekleme
1. `models.py` - Veritabanı modeli
2. `index.py` - API endpoint
3. `templates/index.html` - Frontend
4. `static/webrtc.js` - WebRTC işlevleri

### Test
```bash
# Veritabanı testi
python create_database.py

# API testi
curl -X GET https://dataflow.mildeniz.space/api/rooms
```

## 📞 Destek

Herhangi bir sorun için:
- GitHub Issues kullanın
- Log dosyalarını kontrol edin
- FreeSWITCH ve MariaDB loglarını inceleyin

---

**DataFlow Spaces** - Modern sesli konferans deneyimi 🎙️
