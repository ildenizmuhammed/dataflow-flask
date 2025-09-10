"""
FreeSWITCH Event Socket Client
DataFlow Conference uygulaması için FreeSWITCH ile iletişim
"""

import socket
import time
import json
import threading
from typing import Dict, List, Optional

class FreeSWITCHClient:
    def __init__(self, host='192.168.1.163', port=8021, password='ClueCon'):
        self.host = host
        self.port = port
        self.password = password
        self.socket = None
        self.connected = False
        self.event_handlers = {}
        
    def connect(self) -> bool:
        """FreeSWITCH Event Socket'e bağlan"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            
            # Auth mesajını bekle
            auth_response = self.socket.recv(1024).decode('utf-8')
            if 'auth/request' in auth_response:
                # Şifre gönder
                self.socket.send(f'auth {self.password}\n\n'.encode('utf-8'))
                
                # Auth response'u bekle
                auth_result = self.socket.recv(1024).decode('utf-8')
                if 'reply-text: +OK accepted' in auth_result:
                    self.connected = True
                    print("✅ FreeSWITCH Event Socket bağlantısı kuruldu")
                    
                    # Event listener thread'i başlat
                    self.start_event_listener()
                    return True
                else:
                    print("❌ FreeSWITCH auth hatası")
                    return False
            else:
                print("❌ Beklenmeyen FreeSWITCH response")
                return False
                
        except Exception as e:
            print(f"❌ FreeSWITCH bağlantı hatası: {e}")
            return False
    
    def disconnect(self):
        """Bağlantıyı kapat"""
        if self.socket:
            self.socket.close()
            self.connected = False
            print("🔌 FreeSWITCH bağlantısı kapatıldı")
    
    def send_command(self, command: str) -> str:
        """FreeSWITCH'e komut gönder"""
        if not self.connected:
            return ""
        
        try:
            self.socket.send(f'{command}\n\n'.encode('utf-8'))
            response = self.socket.recv(4096).decode('utf-8')
            return response
        except Exception as e:
            print(f"❌ Komut gönderme hatası: {e}")
            return ""
    
    def create_conference(self, conference_id: str, max_members: int = 10) -> bool:
        """Konferans odası oluştur"""
        try:
            # Conference modülünü yükle
            response = self.send_command('load mod_conference')
            if '+OK' not in response:
                print("❌ Conference modülü yüklenemedi")
                return False
            
            # Konferans oluştur
            cmd = f'conference {conference_id} create'
            response = self.send_command(cmd)
            
            if '+OK' in response:
                print(f"✅ Konferans oluşturuldu: {conference_id}")
                return True
            else:
                print(f"❌ Konferans oluşturulamadı: {response}")
                return False
                
        except Exception as e:
            print(f"❌ Konferans oluşturma hatası: {e}")
            return False
    
    def join_conference(self, conference_id: str, caller_id: str) -> bool:
        """Konferansa katıl"""
        try:
            cmd = f'conference {conference_id} dial user/{caller_id}'
            response = self.send_command(cmd)
            
            if '+OK' in response:
                print(f"✅ Konferansa katıldı: {caller_id} -> {conference_id}")
                return True
            else:
                print(f"❌ Konferansa katılım hatası: {response}")
                return False
                
        except Exception as e:
            print(f"❌ Konferansa katılım hatası: {e}")
            return False
    
    def leave_conference(self, conference_id: str, caller_id: str) -> bool:
        """Konferanstan çık"""
        try:
            cmd = f'conference {conference_id} kick {caller_id}'
            response = self.send_command(cmd)
            
            if '+OK' in response:
                print(f"✅ Konferanstan çıkıldı: {caller_id}")
                return True
            else:
                print(f"❌ Konferanstan çıkış hatası: {response}")
                return False
                
        except Exception as e:
            print(f"❌ Konferanstan çıkış hatası: {e}")
            return False
    
    def mute_participant(self, conference_id: str, caller_id: str, mute: bool = True) -> bool:
        """Katılımcıyı mute/unmute yap"""
        try:
            action = 'mute' if mute else 'unmute'
            cmd = f'conference {conference_id} {action} {caller_id}'
            response = self.send_command(cmd)
            
            if '+OK' in response:
                print(f"✅ Katılımcı {action}: {caller_id}")
                return True
            else:
                print(f"❌ Mute/unmute hatası: {response}")
                return False
                
        except Exception as e:
            print(f"❌ Mute/unmute hatası: {e}")
            return False
    
    def get_conference_info(self, conference_id: str) -> Dict:
        """Konferans bilgilerini al"""
        try:
            cmd = f'conference {conference_id} list'
            response = self.send_command(cmd)
            
            # Response'u parse et
            info = {
                'id': conference_id,
                'participants': [],
                'count': 0
            }
            
            if '+OK' in response:
                lines = response.split('\n')
                for line in lines:
                    if 'member' in line.lower():
                        info['count'] += 1
                        # Participant bilgilerini parse et
                        # Bu kısım FreeSWITCH response formatına göre geliştirilebilir
            
            return info
            
        except Exception as e:
            print(f"❌ Konferans bilgisi alma hatası: {e}")
            return {}
    
    def start_event_listener(self):
        """Event listener thread'i başlat"""
        def listen_events():
            while self.connected:
                try:
                    data = self.socket.recv(4096).decode('utf-8')
                    if data:
                        self.handle_event(data)
                except Exception as e:
                    if self.connected:
                        print(f"❌ Event listener hatası: {e}")
                    break
        
        thread = threading.Thread(target=listen_events, daemon=True)
        thread.start()
    
    def handle_event(self, event_data: str):
        """Event'leri işle"""
        # FreeSWITCH event'lerini parse et ve işle
        if 'CHANNEL_ANSWER' in event_data:
            print("📞 Arama cevaplandı")
        elif 'CHANNEL_HANGUP' in event_data:
            print("📞 Arama sonlandırıldı")
        elif 'CONFERENCE_MAINT' in event_data:
            print("🎙️ Konferans güncellendi")
    
    def register_event_handler(self, event_type: str, handler):
        """Event handler kaydet"""
        self.event_handlers[event_type] = handler

# Global FreeSWITCH client instance
freeswitch_client = FreeSWITCHClient()

def get_freeswitch_client() -> FreeSWITCHClient:
    """FreeSWITCH client instance'ını döndür"""
    return freeswitch_client
