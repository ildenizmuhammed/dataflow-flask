from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
from models import db, ConferenceRoom, Participant
from freeswitch_client import get_freeswitch_client
import os
import requests
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
# Debian sunucuda MariaDB kullan
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:ildeniz@localhost:3306/dataflow_conference?charset=utf8mb4'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# FreeSWITCH Event Socket ayarları
FREESWITCH_HOST = '192.168.1.163'  # FreeSWITCH sunucusu
FREESWITCH_PORT = 8021
FREESWITCH_PASSWORD = 'ClueCon'

db.init_app(app)
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/rooms', methods=['GET'])
def get_rooms():
    """Aktif odaları listele"""
    rooms = ConferenceRoom.query.filter_by(is_active=True).all()
    return jsonify([room.to_dict() for room in rooms])

@app.route('/api/rooms', methods=['POST'])
def create_room():
    """Yeni oda oluştur"""
    data = request.get_json()
    
    # FreeSWITCH'te konferans oluştur
    conference_id = f"room_{len(ConferenceRoom.query.all()) + 1}"
    
    # FreeSWITCH client ile konferans oluştur (geçici olarak devre dışı)
    try:
        fs_client = get_freeswitch_client()
        if not fs_client.connected:
            if not fs_client.connect():
                print("⚠️ FreeSWITCH bağlantısı kurulamadı, devam ediliyor...")
                # return jsonify({'error': 'FreeSWITCH bağlantısı kurulamadı'}), 500
        
        # FreeSWITCH'te konferans oluştur
        if fs_client.connected and not fs_client.create_conference(conference_id):
            print("⚠️ FreeSWITCH konferansı oluşturulamadı, devam ediliyor...")
            # return jsonify({'error': 'FreeSWITCH konferansı oluşturulamadı'}), 500
    except Exception as e:
        print(f"⚠️ FreeSWITCH hatası: {e}, devam ediliyor...")
    
    room = ConferenceRoom(
        name=data['name'],
        description=data.get('description', ''),
        freeswitch_conference_id=conference_id
    )
    
    db.session.add(room)
    db.session.commit()
    
    return jsonify(room.to_dict()), 201

@app.route('/api/rooms/<room_id>/join', methods=['POST'])
def join_room_api(room_id):
    """Odaya katıl"""
    data = request.get_json()
    room = ConferenceRoom.query.get_or_404(room_id)
    
    if room.current_participants >= room.max_participants:
        return jsonify({'error': 'Oda dolu'}), 400
    
    participant = Participant(
        name=data['name'],
        session_id=data.get('session_id'),
        room_id=room_id,
        is_moderator=room.current_participants == 0  # İlk katılımcı moderatör
    )
    
    db.session.add(participant)
    room.current_participants += 1
    db.session.commit()
    
    return jsonify(participant.to_dict())

@app.route('/api/rooms/<room_id>/participants', methods=['GET'])
def get_participants(room_id):
    """Oda katılımcılarını listele"""
    participants = Participant.query.filter_by(room_id=room_id).all()
    return jsonify([p.to_dict() for p in participants])

# WebRTC API endpoints
@app.route('/api/webrtc/offer', methods=['POST'])
def handle_webrtc_offer():
    """WebRTC offer'ı işle ve FreeSWITCH'e gönder"""
    data = request.get_json()
    room_id = data['room_id']
    participant_id = data['participant_id']
    offer = data['offer']
    
    try:
        # FreeSWITCH Event Socket ile konferansa katıl
        # Bu kısım FreeSWITCH Event Socket API kullanarak yapılacak
        # Şimdilik mock response döndürüyoruz
        
        # Gerçek implementasyonda:
        # 1. FreeSWITCH Event Socket'e bağlan
        # 2. Conference bridge oluştur
        # 3. WebRTC session başlat
        # 4. Answer döndür
        
        mock_answer = {
            "type": "answer",
            "sdp": "v=0\r\no=- 1234567890 1234567890 IN IP4 127.0.0.1\r\n..."
        }
        
        return jsonify({
            'success': True,
            'answer': mock_answer
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/webrtc/ice-candidate', methods=['POST'])
def handle_ice_candidate():
    """ICE candidate'ı işle"""
    data = request.get_json()
    # ICE candidate'ı FreeSWITCH'e ilet
    return jsonify({'success': True})

@app.route('/api/webrtc/leave', methods=['POST'])
def handle_webrtc_leave():
    """WebRTC bağlantısını sonlandır"""
    data = request.get_json()
    room_id = data['room_id']
    participant_id = data['participant_id']
    
    try:
        # FreeSWITCH'ten katılımcıyı çıkar
        # Event Socket ile conference'den leave et
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/webrtc/mute-status', methods=['POST'])
def handle_mute_status():
    """Mute durumunu güncelle"""
    data = request.get_json()
    participant_id = data['participant_id']
    is_muted = data['is_muted']
    
    try:
        participant = Participant.query.get(participant_id)
        if participant:
            participant.is_muted = is_muted
            db.session.commit()
            
            # Socket.IO ile diğer katılımcılara bildir
            socketio.emit('participant_muted', {
                'participant_id': participant_id,
                'is_muted': is_muted
            }, room=data['room_id'])
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/webrtc/video-status', methods=['POST'])
def handle_video_status():
    """Video durumunu güncelle"""
    data = request.get_json()
    participant_id = data['participant_id']
    is_video_enabled = data['is_video_enabled']
    
    try:
        # Video durumunu veritabanında sakla (gerekirse)
        # Socket.IO ile diğer katılımcılara bildir
        socketio.emit('participant_video_toggled', {
            'participant_id': participant_id,
            'is_video_enabled': is_video_enabled
        }, room=data['room_id'])
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# WebSocket Events
@socketio.on('join_room')
def on_join_room(data):
    room_id = data['room_id']
    join_room(room_id)
    emit('status', {'msg': f'Room {room_id} joined'}, room=room_id)

@socketio.on('leave_room')
def on_leave_room(data):
    room_id = data['room_id']
    participant_id = data.get('participant_id')
    
    if participant_id:
        participant = Participant.query.get(participant_id)
        if participant:
            room = participant.room
            room.current_participants -= 1
            db.session.delete(participant)
            db.session.commit()
    
    leave_room(room_id)
    emit('status', {'msg': f'Room {room_id} left'}, room=room_id)

@socketio.on('update_participants')
def on_update_participants(data):
    room_id = data['room_id']
    participants = Participant.query.filter_by(room_id=room_id).all()
    emit('participants_updated', [p.to_dict() for p in participants], room=room_id)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
