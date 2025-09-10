# 🚀 DataFlow Spaces - Debian Sunucu Kurulumu

## 📋 Ön Gereksinimler

- Debian 11+ sunucu
- Root veya sudo erişimi
- İnternet bağlantısı
- Domain adı (dataflow.mildeniz.space)

## 🛠️ Kurulum Adımları

### 1. Dosyaları Sunucuya Kopyala

```bash
# Windows'tan Debian sunucuya dosyaları kopyala
scp -r C:\Users\ildeniz\Documents\Github\dataflow-flask root@192.168.1.165:/var/www/dataflow
```

### 2. Sunucuda Kurulum

```bash
# Sunucuya bağlan
ssh root@192.168.1.165

# Proje dizinine git
cd /var/www/dataflow

# Deployment scriptini çalıştır
chmod +x deploy.sh
./deploy.sh
```

### 3. Manuel Kurulum (Alternatif)

```bash
# Sistem güncellemeleri
sudo apt update && sudo apt upgrade -y

# Python ve MariaDB kurulumu
sudo apt install -y python3 python3-pip python3-venv mariadb-server mariadb-client nginx

# MariaDB servisini başlat
sudo systemctl start mariadb
sudo systemctl enable mariadb

# MariaDB güvenlik kurulumu
sudo mysql_secure_installation
# Şifre: ildeniz

# Python sanal ortamı
python3 -m venv venv
source venv/bin/activate

# Bağımlılıkları yükle
pip install -r requirements.txt

# Veritabanını oluştur
python create_database.py
```

### 4. FreeSWITCH Kurulumu

```bash
# FreeSWITCH'i başlat
cd /path/to/flowchat
./freeswitch -nc

# Veya systemd service olarak
sudo systemctl start freeswitch
sudo systemctl enable freeswitch
```

### 5. Nginx Konfigürasyonu

```bash
# Nginx konfigürasyonunu kopyala
sudo cp nginx-dataflow.conf /etc/nginx/sites-available/dataflow
sudo ln -s /etc/nginx/sites-available/dataflow /etc/nginx/sites-enabled/

# SSL sertifikası (Let's Encrypt)
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d dataflow.mildeniz.space

# Nginx'i yeniden başlat
sudo systemctl reload nginx
```

### 6. Systemd Service Kurulumu

```bash
# Service dosyasını kopyala
sudo cp dataflow-spaces.service /etc/systemd/system/

# Service'i etkinleştir
sudo systemctl daemon-reload
sudo systemctl enable dataflow-spaces
sudo systemctl start dataflow-spaces

# Durumu kontrol et
sudo systemctl status dataflow-spaces
```

## 🔧 Konfigürasyon

### MariaDB Ayarları

```bash
# MariaDB'ye bağlan
mysql -u root -p

# Veritabanı oluştur
CREATE DATABASE IF NOT EXISTS dataflow_conference CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# Kullanıcı oluştur (opsiyonel)
CREATE USER 'dataflow'@'localhost' IDENTIFIED BY 'güçlü_şifre';
GRANT ALL PRIVILEGES ON dataflow_conference.* TO 'dataflow'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### FreeSWITCH Konfigürasyonu

```bash
# Conference modülünü etkinleştir
echo "load mod_conference" >> /path/to/flowchat/autoload_configs/modules.conf.xml

# WebRTC profili etkinleştir
echo "load mod_sofia" >> /path/to/flowchat/autoload_configs/modules.conf.xml
```

## 🚀 Uygulamayı Başlatma

### Manuel Başlatma

```bash
cd /var/www/dataflow
source venv/bin/activate
python index.py
```

### Systemd Service ile

```bash
sudo systemctl start dataflow-spaces
sudo systemctl status dataflow-spaces
```

## 🌐 Erişim

- **Web Arayüzü**: https://dataflow.mildeniz.space/
- **API**: https://dataflow.mildeniz.space/api/
- **WebSocket**: wss://dataflow.mildeniz.space/socket.io/

## 📊 Monitoring

### Log Dosyaları

```bash
# Uygulama logları
sudo journalctl -u dataflow-spaces -f

# Nginx logları
sudo tail -f /var/log/nginx/dataflow.access.log
sudo tail -f /var/log/nginx/dataflow.error.log

# MariaDB logları
sudo tail -f /var/log/mysql/error.log
```

### Sistem Durumu

```bash
# Servis durumları
sudo systemctl status dataflow-spaces
sudo systemctl status mariadb
sudo systemctl status nginx
sudo systemctl status freeswitch

# Port kontrolü
sudo netstat -tlnp | grep -E "(5000|3306|5060|8021)"
```

## 🔧 Sorun Giderme

### MariaDB Bağlantı Sorunu

```bash
# MariaDB servisini kontrol et
sudo systemctl status mariadb

# Bağlantıyı test et
mysql -u root -p -e "SELECT 1;"

# Port kontrolü
sudo netstat -tlnp | grep 3306
```

### FreeSWITCH Sorunu

```bash
# FreeSWITCH loglarını kontrol et
tail -f /path/to/flowchat/log/freeswitch.log

# Event Socket bağlantısını test et
telnet localhost 8021
```

### Nginx Sorunu

```bash
# Nginx konfigürasyonunu test et
sudo nginx -t

# Nginx'i yeniden başlat
sudo systemctl reload nginx
```

## 🔒 Güvenlik

### Firewall Ayarları

```bash
# UFW firewall
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

### SSL Sertifikası Yenileme

```bash
# Otomatik yenileme
sudo certbot renew --dry-run

# Manuel yenileme
sudo certbot renew
sudo systemctl reload nginx
```

## 📈 Performans Optimizasyonu

### MariaDB Optimizasyonu

```bash
# /etc/mysql/mariadb.conf.d/50-server.cnf
[mysqld]
innodb_buffer_pool_size = 256M
max_connections = 100
query_cache_size = 32M
```

### Nginx Optimizasyonu

```bash
# /etc/nginx/nginx.conf
worker_processes auto;
worker_connections 1024;
```

## 🎉 Başarılı Kurulum

Kurulum tamamlandıktan sonra:

1. ✅ https://dataflow.mildeniz.space/ adresine gidin
2. ✅ İlk konferans odanızı oluşturun
3. ✅ WebRTC ile sesli konferansı test edin
4. ✅ FreeSWITCH entegrasyonunu kontrol edin

---

**DataFlow Spaces** - Debian sunucuda çalışan modern sesli konferans uygulaması! 🎙️
