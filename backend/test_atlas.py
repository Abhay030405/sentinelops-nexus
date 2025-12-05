import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def test_connection():
    # Replace with your actual connection string
    MONGODB_URL = "mongodb+srv://officialabhay030405_db_user:iFzFEl1N9CLZ6ody@sentinelops-cluster.rhsca7d.mongodb.net/"
    
    try:
        client = AsyncIOMotorClient(MONGODB_URL)
        
        # Test connection
        await client.admin.command('ping')
        print("✅ MongoDB Atlas connection successful!")
        
        # List databases
        db_list = await client.list_database_names()
        print(f"📊 Available databases: {db_list}")
        
        client.close()
    except Exception as e:
        print(f"❌ Connection failed: {e}")

asyncio.run(test_connection())