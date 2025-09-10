#!/usr/bin/env python3
"""
MariaDB uzaktan bağlantı kurulumu
Bu scripti MariaDB sunucusunda (192.168.1.165) çalıştırın
"""

import pymysql
import sys

def setup_remote_access():
    """MariaDB'yi uzaktan bağlantıya aç"""
    print("🔧 MariaDB uzaktan bağlantı kurulumu")
    print("=" * 40)
    
    try:
        # Localhost'a bağlan
        connection = pymysql.connect(
            host='localhost',
            port=3306,
            user='root',
            password='ildeniz',
            charset='utf8mb4'
        )
        
        print("✅ MariaDB'ye bağlandı")
        
        with connection.cursor() as cursor:
            # Root kullanıcısına uzaktan erişim izni ver
            print("🔑 Root kullanıcısına uzaktan erişim izni veriliyor...")
            cursor.execute("GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' IDENTIFIED BY 'ildeniz' WITH GRANT OPTION;")
            
            # Veritabanını oluştur
            print("📊 Veritabanı oluşturuluyor...")
            cursor.execute("CREATE DATABASE IF NOT EXISTS dataflow_conference CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
            
            # İzinleri yenile
            print("🔄 İzinler yenileniyor...")
            cursor.execute("FLUSH PRIVILEGES;")
            
            print("✅ Kurulum tamamlandı!")
            print("\n📋 Yapılan işlemler:")
            print("1. Root kullanıcısına uzaktan erişim izni verildi")
            print("2. dataflow_conference veritabanı oluşturuldu")
            print("3. İzinler yenilendi")
            
        connection.close()
        return True
        
    except Exception as e:
        print(f"❌ Hata: {e}")
        return False

def check_config():
    """MariaDB konfigürasyonunu kontrol et"""
    print("\n🔍 MariaDB konfigürasyon kontrolü")
    print("=" * 40)
    
    print("📝 /etc/mysql/mariadb.conf.d/50-server.cnf dosyasında:")
    print("   bind-address = 0.0.0.0  (127.0.0.1 yerine)")
    print("\n📝 /etc/mysql/mariadb.conf.d/50-server.cnf dosyasında:")
    print("   [mysqld]")
    print("   bind-address = 0.0.0.0")
    print("   port = 3306")
    
    print("\n🔧 Konfigürasyon değişiklikleri için:")
    print("   sudo nano /etc/mysql/mariadb.conf.d/50-server.cnf")
    print("   sudo systemctl restart mariadb")

if __name__ == '__main__':
    print("🚀 DataFlow Conference - MariaDB Uzaktan Erişim Kurulumu")
    print("=" * 60)
    print("⚠️  Bu scripti MariaDB sunucusunda (192.168.1.165) çalıştırın!")
    print("=" * 60)
    
    if setup_remote_access():
        check_config()
        print("\n🎉 Kurulum başarılı!")
        print("Artık Windows'tan MariaDB'ye bağlanabilirsiniz.")
    else:
        print("\n❌ Kurulum başarısız!")
        sys.exit(1)
