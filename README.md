# 🎙️ Clubhouse Spaces - Sesli Sohbet Uygulaması

Modern Clubhouse benzeri sesli sohbet uygulaması. Kullanıcılar public ve private odalar oluşturabilir, konuşma yetkisi sistemi ile kontrollü sohbetler yapabilir.

## ✨ Özellikler

### 🔐 Kullanıcı Yönetimi
- Kullanıcı kaydı ve girişi
- Profil yönetimi (avatar, bio)
- Online durumu takibi

### 🏠 Oda Yönetimi
- **Public Odalar**: Herkes katılabilir
- **Private Odalar**: Davet kodu ile katılım
- Oda oluşturma ve yönetimi
- Maksimum katılımcı sınırı

### 🎤 Konuşma Sistemi
- **Sadece oda sahibi konuşabilir** (başlangıçta)
- **Konuşma yetkisi isteği**: El emojisi ile istek
- **Oda sahibi onayı**: Kabul/Red seçenekleri
- **Yetki verme**: İstediği kişilere konuşma yetkisi
- **Yetki geri alma**: Konuşma yetkisini iptal etme

### 👥 Katılımcı Görünümü
- **Yuvarlak çember tasarım**: Clubhouse benzeri
- **Avatar sistemi**: Kullanıcı fotoğrafları
- **Durum göstergeleri**:
  - 👑 Oda sahibi
  - 🎤 Konuşuyor
  - 🔇 Susturulmuş
  - ✋ Konuşma isteği

### 🔧 Moderasyon
- **Susturma**: Kullanıcıları susturma
- **Susturmayı kaldırma**: Ses açma
- **Konuşma isteklerini yönetme**: Onaylama/Reddetme

## 🚀 Kurulum

### Gereksinimler
- Python 3.8+
- MariaDB/MySQL
- Modern web tarayıcısı (WebRTC desteği)

### 1. Bağımlılıkları Yükle
```bash
pip install -r requirements.txt
```

### 2. Veritabanını Kur
```bash
python create_database.py
```

### 3. Uygulamayı Çalıştır
```bash
python index.py
```

### 4. Tarayıcıda Aç
```
http://localhost:5000
```

## 📱 Kullanım

### İlk Giriş
1. **Kayıt Ol**: Kullanıcı adı ve görünen ad ile
2. **Giriş Yap**: Kayıtlı kullanıcı adı ile

### Oda Oluşturma
1. **"Oda Oluştur"** butonuna tıkla
2. **Oda bilgilerini** doldur:
   - Oda adı
   - Açıklama
   - Public/Private seçimi
   - Maksimum katılımcı sayısı
3. **"Oda Oluştur"** ile onayla

### Odaya Katılma
- **Public odalar**: Direkt katıl
- **Private odalar**: Davet kodu gerekli

### Konuşma Sistemi
1. **Oda sahibi**: Direkt konuşabilir
2. **Diğer katılımcılar**: "Konuşma İste" butonu
3. **Oda sahibi**: İstekleri onaylar/reddeder
4. **Yetki verilenler**: Konuşma butonu aktif olur

## 🎨 Tasarım

### Modern UI
- **Koyu tema**: Siyah arka plan
- **Glassmorphism**: Şeffaf kartlar
- **Gradient butonlar**: Renkli geçişler
- **Responsive**: Mobil uyumlu

### Clubhouse Benzeri
- **Yuvarlak avatarlar**: Katılımcı çemberleri
- **Durum göstergeleri**: Görsel feedback
- **Minimal tasarım**: Sade ve şık

## 🔧 Teknik Detaylar

### Backend
- **Flask**: Web framework
- **SQLAlchemy**: ORM
- **Socket.IO**: Real-time iletişim
- **MariaDB**: Veritabanı

### Frontend
- **Vanilla JavaScript**: Framework yok
- **WebRTC**: Sesli iletişim
- **Socket.IO Client**: Real-time güncellemeler
- **CSS3**: Modern stiller

### WebRTC Özellikleri
- **Sesli konferans**: Audio-only
- **Otomatik konuşma tespiti**: Ses seviyesi analizi
- **Echo cancellation**: Ses kalitesi
- **Noise suppression**: Gürültü azaltma

## 📊 Veritabanı Yapısı

### Tablolar
- **user**: Kullanıcı bilgileri
- **room**: Oda bilgileri
- **room_member**: Oda üyelikleri
- **speaking_request**: Konuşma istekleri
- **room_invite**: Davet kodları

## 🔒 Güvenlik

- **Session yönetimi**: Flask sessions
- **SQL injection koruması**: SQLAlchemy ORM
- **XSS koruması**: Template escaping
- **CSRF koruması**: Flask-WTF (gelecek)

## 🚀 Gelecek Özellikler

- [ ] **Video desteği**: Görüntülü sohbet
- [ ] **Kayıt özelliği**: Sohbet kaydetme
- [ ] **Bildirimler**: Push notifications
- [ ] **Mobil uygulama**: React Native
- [ ] **Çoklu dil**: i18n desteği
- [ ] **Tema seçenekleri**: Açık/koyu tema
- [ ] **Ses efektleri**: Katılım/çıkış sesleri

## 📝 Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

## 🤝 Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit yapın (`git commit -m 'Add amazing feature'`)
4. Push yapın (`git push origin feature/amazing-feature`)
5. Pull Request oluşturun

## 📞 İletişim

- **Geliştirici**: İldeniz
- **Email**: ildeniz@example.com
- **GitHub**: [@ildeniz](https://github.com/ildeniz)

---

**🎉 Clubhouse Spaces ile sesli sohbetlerin keyfini çıkarın!**
