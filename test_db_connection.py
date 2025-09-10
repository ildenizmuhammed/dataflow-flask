#!/usr/bin/env python3
"""
MariaDB bağlantı testi
"""

import pymysql
import sys

def test_connection():
    """MariaDB bağlantısını test et"""
    print("🔍 MariaDB bağlantı testi başlatılıyor...")
    
    try:
        # Bağlantı testi
        connection = pymysql.connect(
            host='192.168.1.165',
            port=3306,
            user='root',
            password='ildeniz',
            charset='utf8mb4'
        )
        
        print("✅ MariaDB bağlantısı başarılı!")
        
        with connection.cursor() as cursor:
            # MariaDB versiyonunu kontrol et
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()
            print(f"📊 MariaDB Versiyonu: {version[0]}")
            
            # Mevcut veritabanlarını listele
            cursor.execute("SHOW DATABASES")
            databases = cursor.fetchall()
            print("📁 Mevcut veritabanları:")
            for db in databases:
                print(f"   - {db[0]}")
        
        connection.close()
        return True
        
    except pymysql.err.OperationalError as e:
        print(f"❌ Bağlantı hatası: {e}")
        print("\n🔧 Olası çözümler:")
        print("1. MariaDB servisinin çalıştığından emin olun:")
        print("   sudo systemctl status mariadb")
        print("   sudo systemctl start mariadb")
        print("\n2. MariaDB portunu kontrol edin:")
        print("   sudo netstat -tlnp | grep 3306")
        print("\n3. Firewall ayarlarını kontrol edin:")
        print("   sudo ufw status")
        return False
        
    except pymysql.err.AccessDeniedError as e:
        print(f"❌ Yetki hatası: {e}")
        print("\n🔧 Olası çözümler:")
        print("1. Root şifresini kontrol edin")
        print("2. MariaDB'de root kullanıcısının uzaktan bağlantı iznini kontrol edin:")
        print("   mysql -u root -p")
        print("   GRANT ALL PRIVILEGES ON *.* TO 'root'@'localhost' IDENTIFIED BY 'ildeniz';")
        print("   FLUSH PRIVILEGES;")
        return False
        
    except Exception as e:
        print(f"❌ Beklenmeyen hata: {e}")
        return False

if __name__ == '__main__':
    print("🚀 DataFlow Conference - MariaDB Bağlantı Testi")
    print("=" * 50)
    
    if test_connection():
        print("\n🎉 Bağlantı testi başarılı!")
        print("Artık veritabanı oluşturma scriptini çalıştırabilirsiniz.")
    else:
        print("\n💡 Bağlantı sorununu çözdükten sonra tekrar deneyin.")
        sys.exit(1)
