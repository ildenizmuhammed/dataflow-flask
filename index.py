from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_socketio import SocketIO, emit, join_room, leave_room
from models import db, User, Room, RoomMember, SpeakingRequest, RoomInvite
import os
import requests
import json
import uuid
import string
import random
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
# Debian sunucuda MariaDB kullan
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:ildeniz@localhost:3306/dataflow_conference?charset=utf8mb4'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Helper functions
def generate_invite_code():
    """Rastgele davet kodu oluştur"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

def get_current_user():
    """Session'dan mevcut kullanıcıyı al"""
    if 'user_id' in session:
        return User.query.get(session['user_id'])
    return None

def require_auth(f):
    """Authentication gerektiren decorator"""
    def decorated_function(*args, **kwargs):
        if not get_current_user():
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@app.route('/')
def index():
    return render_template('index.html')

# User Management Routes
@app.route('/api/auth/register', methods=['POST'])
def register():
    """Kullanıcı kaydı"""
    data = request.get_json()
    
    # Kullanıcı adı kontrolü
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 400
    
    # Email kontrolü (eğer verilmişse)
    if data.get('email') and User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 400
    
    user = User(
        username=data['username'],
        display_name=data['display_name'],
        email=data.get('email'),
        avatar_url=data.get('avatar_url'),
        bio=data.get('bio')
    )
    
    db.session.add(user)
    db.session.commit()
    
    # Session'a kullanıcıyı kaydet
    session['user_id'] = user.id
    
    return jsonify(user.to_dict()), 201

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Kullanıcı girişi"""
    data = request.get_json()
    
    user = User.query.filter_by(username=data['username']).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Session'a kullanıcıyı kaydet
    session['user_id'] = user.id
    user.is_online = True
    user.last_seen = datetime.utcnow()
    db.session.commit()
    
    return jsonify(user.to_dict())

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    """Kullanıcı çıkışı"""
    user = get_current_user()
    if user:
        user.is_online = False
        user.last_seen = datetime.utcnow()
        db.session.commit()
    
    session.pop('user_id', None)
    return jsonify({'message': 'Logged out successfully'})

@app.route('/api/auth/me', methods=['GET'])
def get_current_user_info():
    """Mevcut kullanıcı bilgilerini al"""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Not authenticated'}), 401
    return jsonify(user.to_dict())

# Room Management Routes
@app.route('/api/rooms', methods=['GET'])
def get_rooms():
    """Aktif odaları listele"""
    rooms = Room.query.filter_by(is_active=True, is_public=True).all()
    return jsonify([room.to_dict() for room in rooms])

@app.route('/api/rooms', methods=['POST'])
@require_auth
def create_room():
    """Yeni oda oluştur"""
    data = request.get_json()
    user = get_current_user()
    
    room = Room(
        name=data['name'],
        description=data.get('description', ''),
        is_public=data.get('is_public', True),
        max_participants=data.get('max_participants', 50),
        owner_id=user.id
    )
    
    db.session.add(room)
    db.session.commit()
    
    # Oda sahibini otomatik olarak odaya ekle
    member = RoomMember(
        user_id=user.id,
        room_id=room.id,
        can_speak=True,  # Oda sahibi konuşabilir
        is_moderator=True
    )
    
    db.session.add(member)
    room.current_participants = 1
    db.session.commit()
    
    return jsonify(room.to_dict()), 201

@app.route('/api/rooms/<room_id>', methods=['GET'])
def get_room(room_id):
    """Oda detaylarını al"""
    room = Room.query.get_or_404(room_id)
    return jsonify(room.to_dict())

@app.route('/api/rooms/<room_id>/join', methods=['POST'])
@require_auth
def join_room_api(room_id):
    """Odaya katıl"""
    data = request.get_json()
    user = get_current_user()
    room = Room.query.get_or_404(room_id)
    
    # Zaten üye mi kontrol et
    existing_member = RoomMember.query.filter_by(user_id=user.id, room_id=room_id).first()
    if existing_member:
        return jsonify({'error': 'Already a member of this room'}), 400
    
    # Oda dolu mu kontrol et
    if room.current_participants >= room.max_participants:
        return jsonify({'error': 'Room is full'}), 400
    
    # Private oda ise davet kodu gerekli
    if not room.is_public:
        invite_code = data.get('invite_code')
        if not invite_code:
            return jsonify({'error': 'Invite code required for private room'}), 400
        
        invite = RoomInvite.query.filter_by(
            room_id=room_id, 
            invite_code=invite_code, 
            is_used=False
        ).first()
        
        if not invite:
            return jsonify({'error': 'Invalid invite code'}), 400
        
        # Davet kodunu kullanılmış olarak işaretle
        invite.is_used = True
        invite.used_at = datetime.utcnow()
        invite.used_by = user.id
    
    # Kullanıcıyı odaya ekle
    member = RoomMember(
        user_id=user.id,
        room_id=room_id,
        can_speak=False  # Başlangıçta konuşma yetkisi yok
    )
    
    db.session.add(member)
    room.current_participants += 1
    db.session.commit()
    
    return jsonify(member.to_dict())

@app.route('/api/rooms/<room_id>/leave', methods=['POST'])
@require_auth
def leave_room_api(room_id):
    """Odadan çık"""
    user = get_current_user()
    member = RoomMember.query.filter_by(user_id=user.id, room_id=room_id).first()
    
    if not member:
        return jsonify({'error': 'Not a member of this room'}), 400
    
    room = member.room
    room.current_participants -= 1
    
    # Eğer oda sahibi çıkıyorsa, odayı kapat
    if room.owner_id == user.id:
        room.is_active = False
    
    db.session.delete(member)
    db.session.commit()
    
    return jsonify({'message': 'Left room successfully'})

@app.route('/api/rooms/<room_id>/members', methods=['GET'])
def get_room_members(room_id):
    """Oda üyelerini listele"""
    members = RoomMember.query.filter_by(room_id=room_id).all()
    return jsonify([member.to_dict() for member in members])

@app.route('/api/rooms/<room_id>/invite', methods=['POST'])
@require_auth
def create_room_invite(room_id):
    """Oda için davet kodu oluştur"""
    user = get_current_user()
    room = Room.query.get_or_404(room_id)
    
    # Sadece oda sahibi davet kodu oluşturabilir
    if room.owner_id != user.id:
        return jsonify({'error': 'Only room owner can create invites'}), 403
    
    invite = RoomInvite(
        room_id=room_id,
        invite_code=generate_invite_code(),
        invited_by=user.id
    )
    
    db.session.add(invite)
    db.session.commit()
    
    return jsonify(invite.to_dict()), 201

# Speaking Permission Routes
@app.route('/api/rooms/<room_id>/request-speak', methods=['POST'])
@require_auth
def request_speak(room_id):
    """Konuşma yetkisi iste"""
    user = get_current_user()
    
    # Zaten bekleyen bir istek var mı kontrol et
    existing_request = SpeakingRequest.query.filter_by(
        user_id=user.id, 
        room_id=room_id, 
        status='pending'
    ).first()
    
    if existing_request:
        return jsonify({'error': 'Already have a pending request'}), 400
    
    # Kullanıcı oda üyesi mi kontrol et
    member = RoomMember.query.filter_by(user_id=user.id, room_id=room_id).first()
    if not member:
        return jsonify({'error': 'Not a member of this room'}), 400
    
    # Zaten konuşma yetkisi var mı kontrol et
    if member.can_speak:
        return jsonify({'error': 'Already have speaking permission'}), 400
    
    request_obj = SpeakingRequest(
        user_id=user.id,
        room_id=room_id
    )
    
    db.session.add(request_obj)
    db.session.commit()
    
    # Oda sahibine bildirim gönder
    socketio.emit('speaking_request', request_obj.to_dict(), room=room_id)
    
    return jsonify(request_obj.to_dict()), 201

@app.route('/api/rooms/<room_id>/approve-speak/<user_id>', methods=['POST'])
@require_auth
def approve_speak(room_id, user_id):
    """Konuşma yetkisi ver"""
    current_user = get_current_user()
    room = Room.query.get_or_404(room_id)
    
    # Sadece oda sahibi yetki verebilir
    if room.owner_id != current_user.id:
        return jsonify({'error': 'Only room owner can approve speaking'}), 403
    
    # İsteği bul ve onayla
    request_obj = SpeakingRequest.query.filter_by(
        user_id=user_id, 
        room_id=room_id, 
        status='pending'
    ).first()
    
    if not request_obj:
        return jsonify({'error': 'No pending request found'}), 404
    
    # Kullanıcıya konuşma yetkisi ver
    member = RoomMember.query.filter_by(user_id=user_id, room_id=room_id).first()
    if member:
        member.can_speak = True
    
    # İsteği onaylandı olarak işaretle
    request_obj.status = 'approved'
    request_obj.responded_at = datetime.utcnow()
    
    db.session.commit()
    
    # Tüm oda üyelerine bildirim gönder
    socketio.emit('speaking_approved', {
        'user_id': user_id,
        'room_id': room_id
    }, room=room_id)
    
    return jsonify({'message': 'Speaking permission granted'})

@app.route('/api/rooms/<room_id>/reject-speak/<user_id>', methods=['POST'])
@require_auth
def reject_speak(room_id, user_id):
    """Konuşma yetkisi reddet"""
    current_user = get_current_user()
    room = Room.query.get_or_404(room_id)
    
    # Sadece oda sahibi reddedebilir
    if room.owner_id != current_user.id:
        return jsonify({'error': 'Only room owner can reject speaking'}), 403
    
    # İsteği bul ve reddet
    request_obj = SpeakingRequest.query.filter_by(
        user_id=user_id, 
        room_id=room_id, 
        status='pending'
    ).first()
    
    if not request_obj:
        return jsonify({'error': 'No pending request found'}), 404
    
    # İsteği reddedildi olarak işaretle
    request_obj.status = 'rejected'
    request_obj.responded_at = datetime.utcnow()
    
    db.session.commit()
    
    # Kullanıcıya bildirim gönder
    socketio.emit('speaking_rejected', {
        'user_id': user_id,
        'room_id': room_id
    }, room=room_id)
    
    return jsonify({'message': 'Speaking request rejected'})

@app.route('/api/rooms/<room_id>/revoke-speak/<user_id>', methods=['POST'])
@require_auth
def revoke_speak(room_id, user_id):
    """Konuşma yetkisini geri al"""
    current_user = get_current_user()
    room = Room.query.get_or_404(room_id)
    
    # Sadece oda sahibi yetki geri alabilir
    if room.owner_id != current_user.id:
        return jsonify({'error': 'Only room owner can revoke speaking'}), 403
    
    # Kullanıcının konuşma yetkisini geri al
    member = RoomMember.query.filter_by(user_id=user_id, room_id=room_id).first()
    if member:
        member.can_speak = False
        member.is_speaking = False  # Konuşmayı da durdur
    
    db.session.commit()
    
    # Tüm oda üyelerine bildirim gönder
    socketio.emit('speaking_revoked', {
        'user_id': user_id,
        'room_id': room_id
    }, room=room_id)
    
    return jsonify({'message': 'Speaking permission revoked'})

@app.route('/api/rooms/<room_id>/mute/<user_id>', methods=['POST'])
@require_auth
def mute_user(room_id, user_id):
    """Kullanıcıyı sustur"""
    current_user = get_current_user()
    room = Room.query.get_or_404(room_id)
    
    # Sadece oda sahibi susturabilir
    if room.owner_id != current_user.id:
        return jsonify({'error': 'Only room owner can mute users'}), 403
    
    # Kullanıcıyı sustur
    member = RoomMember.query.filter_by(user_id=user_id, room_id=room_id).first()
    if member:
        member.is_muted = True
        member.is_speaking = False
    
    db.session.commit()
    
    # Tüm oda üyelerine bildirim gönder
    socketio.emit('user_muted', {
        'user_id': user_id,
        'room_id': room_id
    }, room=room_id)
    
    return jsonify({'message': 'User muted'})

@app.route('/api/rooms/<room_id>/unmute/<user_id>', methods=['POST'])
@require_auth
def unmute_user(room_id, user_id):
    """Kullanıcının susturmasını kaldır"""
    current_user = get_current_user()
    room = Room.query.get_or_404(room_id)
    
    # Sadece oda sahibi susturmayı kaldırabilir
    if room.owner_id != current_user.id:
        return jsonify({'error': 'Only room owner can unmute users'}), 403
    
    # Kullanıcının susturmasını kaldır
    member = RoomMember.query.filter_by(user_id=user_id, room_id=room_id).first()
    if member:
        member.is_muted = False
    
    db.session.commit()
    
    # Tüm oda üyelerine bildirim gönder
    socketio.emit('user_unmuted', {
        'user_id': user_id,
        'room_id': room_id
    }, room=room_id)
    
    return jsonify({'message': 'User unmuted'})

@app.route('/api/rooms/<room_id>/speaking-requests', methods=['GET'])
@require_auth
def get_speaking_requests(room_id):
    """Bekleyen konuşma isteklerini listele"""
    current_user = get_current_user()
    room = Room.query.get_or_404(room_id)
    
    # Sadece oda sahibi istekleri görebilir
    if room.owner_id != current_user.id:
        return jsonify({'error': 'Only room owner can view speaking requests'}), 403
    
    requests = SpeakingRequest.query.filter_by(room_id=room_id, status='pending').all()
    return jsonify([req.to_dict() for req in requests])

# WebSocket Events
@socketio.on('join_room')
def on_join_room(data):
    room_id = data['room_id']
    user_id = data.get('user_id')
    
    if user_id:
        # Kullanıcının oda üyesi olduğunu doğrula
        member = RoomMember.query.filter_by(user_id=user_id, room_id=room_id).first()
        if member:
            join_room(room_id)
            emit('status', {'msg': f'Room {room_id} joined'}, room=room_id)
            
            # Oda üyelerini güncelle
            members = RoomMember.query.filter_by(room_id=room_id).all()
            emit('members_updated', [m.to_dict() for m in members], room=room_id)

@socketio.on('leave_room')
def on_leave_room(data):
    room_id = data['room_id']
    user_id = data.get('user_id')
    
    if user_id:
        member = RoomMember.query.filter_by(user_id=user_id, room_id=room_id).first()
        if member:
            room = member.room
            room.current_participants -= 1
            
            # Eğer oda sahibi çıkıyorsa, odayı kapat
            if room.owner_id == user_id:
                room.is_active = False
            
            db.session.delete(member)
            db.session.commit()
    
    leave_room(room_id)
    emit('status', {'msg': f'Room {room_id} left'}, room=room_id)
    
    # Oda üyelerini güncelle
    members = RoomMember.query.filter_by(room_id=room_id).all()
    emit('members_updated', [m.to_dict() for m in members], room=room_id)

@socketio.on('update_members')
def on_update_members(data):
    room_id = data['room_id']
    members = RoomMember.query.filter_by(room_id=room_id).all()
    emit('members_updated', [m.to_dict() for m in members], room=room_id)

@socketio.on('start_speaking')
def on_start_speaking(data):
    room_id = data['room_id']
    user_id = data['user_id']
    
    member = RoomMember.query.filter_by(user_id=user_id, room_id=room_id).first()
    if member and member.can_speak and not member.is_muted:
        member.is_speaking = True
        db.session.commit()
        
        emit('user_started_speaking', {
            'user_id': user_id,
            'room_id': room_id
        }, room=room_id)

@socketio.on('stop_speaking')
def on_stop_speaking(data):
    room_id = data['room_id']
    user_id = data['user_id']
    
    member = RoomMember.query.filter_by(user_id=user_id, room_id=room_id).first()
    if member:
        member.is_speaking = False
        db.session.commit()
        
        emit('user_stopped_speaking', {
            'user_id': user_id,
            'room_id': room_id
        }, room=room_id)

@socketio.on('toggle_mute')
def on_toggle_mute(data):
    room_id = data['room_id']
    user_id = data['user_id']
    is_muted = data['is_muted']
    
    member = RoomMember.query.filter_by(user_id=user_id, room_id=room_id).first()
    if member:
        member.is_muted = is_muted
        if is_muted:
            member.is_speaking = False
        
        db.session.commit()
        
        emit('user_mute_toggled', {
            'user_id': user_id,
            'room_id': room_id,
            'is_muted': is_muted
        }, room=room_id)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
