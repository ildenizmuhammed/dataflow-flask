#!/bin/bash
# DataFlow Spaces - Debian Sunucu Deployment Script

echo "🚀 DataFlow Spaces - Debian Sunucu Kurulumu"
echo "=============================================="

# Renkli çıktı için
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Hata kontrolü
set -e

echo -e "${YELLOW}📋 Sistem güncellemeleri kontrol ediliyor...${NC}"
sudo apt update

echo -e "${YELLOW}🐍 Python ve pip kurulumu...${NC}"
sudo apt install -y python3 python3-pip python3-venv

echo -e "${YELLOW}🗄️ MariaDB kurulumu...${NC}"
sudo apt install -y mariadb-server mariadb-client

echo -e "${YELLOW}🔧 MariaDB servisini başlat...${NC}"
sudo systemctl start mariadb
sudo systemctl enable mariadb

echo -e "${YELLOW}🔐 MariaDB güvenlik kurulumu...${NC}"
echo "MariaDB güvenlik kurulumu yapılacak. Şifre: ildeniz"
sudo mysql_secure_installation

echo -e "${YELLOW}📦 Python sanal ortamı oluştur...${NC}"
python3 -m venv venv
source venv/bin/activate

echo -e "${YELLOW}📚 Python bağımlılıklarını yükle...${NC}"
pip install -r requirements.txt

echo -e "${YELLOW}🗄️ MariaDB veritabanını oluştur...${NC}"
python create_database.py

echo -e "${YELLOW}🌐 Nginx kurulumu (opsiyonel)...${NC}"
sudo apt install -y nginx

echo -e "${GREEN}✅ Kurulum tamamlandı!${NC}"
echo ""
echo -e "${YELLOW}🚀 Uygulamayı başlatmak için:${NC}"
echo "   source venv/bin/activate"
echo "   python index.py"
echo ""
echo -e "${YELLOW}🌐 Tarayıcıda test etmek için:${NC}"
echo "   http://localhost:5000"
echo "   veya"
echo "   http://$(hostname -I | awk '{print $1}'):5000"
echo ""
echo -e "${YELLOW}🔧 FreeSWITCH'i başlatmak için:${NC}"
echo "   cd /path/to/flowchat"
echo "   ./freeswitch -nc"
echo ""
echo -e "${GREEN}🎉 DataFlow Spaces hazır!${NC}"
