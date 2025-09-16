#!/usr/bin/env python3
"""
Database creation script for Clubhouse Spaces
Creates the database and tables for the audio conference application
"""

import pymysql
from models import db, User, Room, RoomMember, SpeakingRequest, RoomInvite
from index import app

def create_database():
    """Create the database and tables"""
    try:
        # Connect to MariaDB server (without database)
        connection = pymysql.connect(
            host='localhost',
            port=3306,
            user='root',
            password='ildeniz',
            charset='utf8mb4'
        )
        
        with connection.cursor() as cursor:
            # Create database
            cursor.execute("CREATE DATABASE IF NOT EXISTS dataflow_conference CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            print("✅ Database created: dataflow_conference")
        
        connection.close()
        
        # Create tables using Flask app
        with app.app_context():
            db.create_all()
            print("✅ Tables created:")
            print("   - user")
            print("   - room")
            print("   - room_member")
            print("   - speaking_request")
            print("   - room_invite")
        
        print("\n🎉 Clubhouse Spaces database setup completed!")
        print("📊 Database information:")
        print("   Host: localhost:3306")
        print("   Database: dataflow_conference")
        print("   User: root")
        print("   Type: MariaDB")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

def test_connection():
    """Test database connection"""
    try:
        with app.app_context():
            # Test query
            users = User.query.all()
            rooms = Room.query.all()
            print(f"✅ Connection successful! Users: {len(users)}, Rooms: {len(rooms)}")
            return True
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

def create_sample_data():
    """Create sample data for testing"""
    try:
        with app.app_context():
            # Check if sample data already exists
            if User.query.first():
                print("ℹ️ Sample data already exists, skipping...")
                return
            
            # Create sample users
            user1 = User(
                username='admin',
                display_name='Admin User',
                email='admin@example.com',
                bio='System administrator'
            )
            
            user2 = User(
                username='demo',
                display_name='Demo User',
                email='demo@example.com',
                bio='Demo user for testing'
            )
            
            db.session.add(user1)
            db.session.add(user2)
            db.session.commit()
            
            # Create sample room
            room = Room(
                name='Welcome Room',
                description='Welcome to Clubhouse Spaces! This is a demo room.',
                is_public=True,
                max_participants=50,
                owner_id=user1.id
            )
            
            db.session.add(room)
            db.session.commit()
            
            # Add owner as member
            member = RoomMember(
                user_id=user1.id,
                room_id=room.id,
                can_speak=True,
                is_moderator=True
            )
            
            db.session.add(member)
            room.current_participants = 1
            db.session.commit()
            
            print("✅ Sample data created:")
            print("   - 2 users (admin, demo)")
            print("   - 1 public room (Welcome Room)")
            print("   - Admin user is room owner and moderator")
            
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")

if __name__ == '__main__':
    print("🚀 Clubhouse Spaces - Database Setup")
    print("=" * 40)
    
    if create_database():
        print("\n🔍 Testing connection...")
        if test_connection():
            print("\n📝 Creating sample data...")
            create_sample_data()
    
    print("\n📝 Next steps:")
    print("1. Run Flask app: python index.py")
    print("2. Open browser: http://localhost:5000")
    print("3. Login with username 'admin' or 'demo'")
    print("4. Create your first room or join the Welcome Room!")