"""
Script to create default admin user in LOCAL MongoDB
Run this ONCE after setting up MongoDB locally
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.identity_vault.utils import hash_password, generate_qr_token
from datetime import datetime

# LOCAL MongoDB connection (no SSL required)
MONGODB_URL = "mongodb://localhost:27017"
DATABASE_NAME = "sentinelops_nexus"

async def create_default_admin():
    """Create the first admin user (Red Ranger)"""
    
    print("🔴 Creating Red Ranger (Admin User)...")
    
    try:
        # Connect to local MongoDB (simple, no SSL)
        client = AsyncIOMotorClient(MONGODB_URL)
        db = client[DATABASE_NAME]
        
        # Test connection
        await client.server_info()
        print("✅ Connected to local MongoDB successfully!")
        
        # Check if admin already exists
        existing_admin = await db.users.find_one({"username": "red_ranger"})
        if existing_admin:
            print("⚠️  Admin user 'red_ranger' already exists!")
            print("Skipping creation...")
            client.close()
            return
        
        # Admin user data
        admin_user = {
            "username": "red_ranger",
            "full_name": "Red Ranger - Team Leader",
            "hashed_password": hash_password("morphintime2024"),
            "role": "admin",
            "qr_token": generate_qr_token(),
            "is_active": True,
            "created_at": datetime.utcnow(),
            "last_login": None
        }
        
        # Insert admin user into database
        result = await db.users.insert_one(admin_user)
        print("✅ Admin user created successfully!")
        print("\n📋 Login Credentials:")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("Username: red_ranger")
        print("Password: morphintime2024")
        print("Role: 🔴 RED RANGER (Admin)")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"\n🆔 User ID: {result.inserted_id}")
        print(f"🔐 QR Token: {admin_user['qr_token'][:16]}...")
        
        client.close()
        print("\n✅ Database connection closed")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n💡 Troubleshooting tips:")
        print("1. Make sure MongoDB service is running")
        print("2. Check if port 27017 is available")
        print("3. Run: net start MongoDB")


if __name__ == "__main__":
    print("🚀 SentinelOps-Nexus Admin Creation Script")
    print("⚡ It's Morphin Time!\n")
    asyncio.run(create_default_admin())