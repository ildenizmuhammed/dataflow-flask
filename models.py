from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid

db = SQLAlchemy()

class ConferenceRoom(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    max_participants = db.Column(db.Integer, default=10)
    current_participants = db.Column(db.Integer, default=0)
    freeswitch_conference_id = db.Column(db.String(50), unique=True)
    
    # İlişkiler
    participants = db.relationship('Participant', backref='room', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat(),
            'is_active': self.is_active,
            'max_participants': self.max_participants,
            'current_participants': self.current_participants,
            'freeswitch_conference_id': self.freeswitch_conference_id
        }

class Participant(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    session_id = db.Column(db.String(100), unique=True)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_muted = db.Column(db.Boolean, default=False)
    is_moderator = db.Column(db.Boolean, default=False)
    
    # Foreign Key
    room_id = db.Column(db.String(36), db.ForeignKey('conference_room.id'), nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'session_id': self.session_id,
            'joined_at': self.joined_at.isoformat(),
            'is_muted': self.is_muted,
            'is_moderator': self.is_moderator,
            'room_id': self.room_id
        }
