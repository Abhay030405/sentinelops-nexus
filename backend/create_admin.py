"""
Quick Admin Creation Script
Run this to create the admin user in MongoDB
"""

import asyncio
import sys
sys.path.insert(0, '/itsMe/Projects/demo-sentinelops-nexus/sentinelops-nexus/backend')

from motor.motor_asyncio import AsyncIOMotorClient
from app.config.settings import settings
from passlib.context import CryptContext

async def create_admin():
    """Create admin user directly in MongoDB"""
    
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    db = client['sentinelops']
    users_collection = db['users']
    
    try:
        # Check if admin exists
        existing = await users_collection.find_one({'email': 'admin@sentinelops.com'})
        if existing:
            print("✅ Admin user already exists!")
            print(f"   Email: {existing['email']}")
            print(f"   Role: {existing['role']}")
            client.close()
            return
        
        # Hash password
        pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
        hashed_password = pwd_context.hash("AdminPassword123!")
        
        # Create admin user
        admin_data = {
            'email': 'admin@sentinelops.com',
            'password_hash': hashed_password,
            'full_name': 'System Administrator',
            'role': 'admin',
            'status': 'active',
            'created_at': asyncio.get_event_loop().time()
        }
        
        result = await users_collection.insert_one(admin_data)
        print("✅ Admin user created successfully!")
        print(f"   Email: admin@sentinelops.com")
        print(f"   Password: AdminPassword123!")
        print(f"   Role: admin")
        print(f"   ID: {result.inserted_id}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(create_admin())
