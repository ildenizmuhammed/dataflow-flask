#!/usr/bin/env python3
"""
MySQL veritabanı oluşturma scripti
DataFlow Conference uygulaması için gerekli tabloları oluşturur
"""

import pymysql
from models import db, ConferenceRoom, Participant
from index import app

def create_database():
    """Veritabanını oluştur"""
    try:
        # MariaDB sunucusuna bağlan (veritabanı olmadan)
        connection = pymysql.connect(
            host='localhost',
            port=3306,
            user='root',
            password='ildeniz',
            charset='utf8mb4'
        )
        
        with connection.cursor() as cursor:
            # Veritabanını oluştur
            cursor.execute("CREATE DATABASE IF NOT EXISTS dataflow_conference CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            print("✅ Veritabanı oluşturuldu: dataflow_conference")
        
        connection.close()
        
        # Flask uygulaması ile tabloları oluştur
        with app.app_context():
            db.create_all()
            print("✅ Tablolar oluşturuldu:")
            print("   - conference_room")
            print("   - participant")
        
        print("\n🎉 MariaDB veritabanı kurulumu tamamlandı!")
        print("📊 Veritabanı bilgileri:")
        print("   Host: 192.168.1.165:3306")
        print("   Database: dataflow_conference")
        print("   User: root")
        print("   Type: MariaDB")
        
    except Exception as e:
        print(f"❌ Hata: {e}")
        return False
    
    return True

def test_connection():
    """Veritabanı bağlantısını test et"""
    try:
        with app.app_context():
            # Test sorgusu
            rooms = ConferenceRoom.query.all()
            print(f"✅ Bağlantı başarılı! Mevcut oda sayısı: {len(rooms)}")
            return True
    except Exception as e:
        print(f"❌ Bağlantı hatası: {e}")
        return False

if __name__ == '__main__':
    print("🚀 DataFlow Conference - MariaDB Veritabanı Kurulumu")
    print("=" * 55)
    
    if create_database():
        print("\n🔍 Bağlantı testi yapılıyor...")
        test_connection()
    
    print("\n📝 Sonraki adımlar:")
    print("1. Flask uygulamasını çalıştırın: python index.py")
    print("2. Tarayıcıda https://dataflow.mildeniz.space/ adresine gidin")
    print("3. İlk konferans odanızı oluşturun!")
