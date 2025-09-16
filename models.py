from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid
import hashlib

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(50), unique=True, nullable=False)
    display_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    avatar_url = db.Column(db.String(500), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_online = db.Column(db.Boolean, default=False)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    
    # İlişkiler
    owned_rooms = db.relationship('Room', backref='owner', lazy=True, foreign_keys='Room.owner_id')
    room_memberships = db.relationship('RoomMember', backref='user', lazy=True, cascade='all, delete-orphan')
    speaking_requests = db.relationship('SpeakingRequest', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'display_name': self.display_name,
            'email': self.email,
            'avatar_url': self.avatar_url,
            'bio': self.bio,
            'created_at': self.created_at.isoformat(),
            'is_online': self.is_online,
            'last_seen': self.last_seen.isoformat()
        }

class Room(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    is_public = db.Column(db.Boolean, default=True)
    max_participants = db.Column(db.Integer, default=50)
    current_participants = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign Keys
    owner_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    
    # İlişkiler
    members = db.relationship('RoomMember', backref='room', lazy=True, cascade='all, delete-orphan')
    speaking_requests = db.relationship('SpeakingRequest', backref='room', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'is_public': self.is_public,
            'max_participants': self.max_participants,
            'current_participants': self.current_participants,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'owner_id': self.owner_id,
            'owner_name': self.owner.display_name if self.owner else None
        }

class RoomMember(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_speaking = db.Column(db.Boolean, default=False)
    is_muted = db.Column(db.Boolean, default=False)
    can_speak = db.Column(db.Boolean, default=False)  # Konuşma yetkisi
    is_moderator = db.Column(db.Boolean, default=False)
    
    # Foreign Keys
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    room_id = db.Column(db.String(36), db.ForeignKey('room.id'), nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'joined_at': self.joined_at.isoformat(),
            'is_speaking': self.is_speaking,
            'is_muted': self.is_muted,
            'can_speak': self.can_speak,
            'is_moderator': self.is_moderator,
            'user_id': self.user_id,
            'room_id': self.room_id,
            'user': self.user.to_dict() if self.user else None
        }

class SpeakingRequest(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    requested_at = db.Column(db.DateTime, default=datetime.utcnow)
    responded_at = db.Column(db.DateTime, nullable=True)
    
    # Foreign Keys
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    room_id = db.Column(db.String(36), db.ForeignKey('room.id'), nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'status': self.status,
            'requested_at': self.requested_at.isoformat(),
            'responded_at': self.responded_at.isoformat() if self.responded_at else None,
            'user_id': self.user_id,
            'room_id': self.room_id,
            'user': self.user.to_dict() if self.user else None
        }

class RoomInvite(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    invite_code = db.Column(db.String(20), unique=True, nullable=False)
    is_used = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    used_at = db.Column(db.DateTime, nullable=True)
    
    # Foreign Keys
    room_id = db.Column(db.String(36), db.ForeignKey('room.id'), nullable=False)
    invited_by = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    used_by = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'invite_code': self.invite_code,
            'is_used': self.is_used,
            'created_at': self.created_at.isoformat(),
            'used_at': self.used_at.isoformat() if self.used_at else None,
            'room_id': self.room_id,
            'invited_by': self.invited_by,
            'used_by': self.used_by
        }
