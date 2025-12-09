"""
Admin Initialization Script
Creates the first admin user in MongoDB

Run this script once to set up the initial admin account.
Usage: python -m app.identity_vault.init_admin
"""

import asyncio
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from app.config.settings import settings
from app.identity_vault.services import UserService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def create_initial_admin():
    """Create the initial admin user"""
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DB_NAME]
    
    try:
        # Check if admin already exists
        collection = db["users"]
        existing_admin = await collection.find_one({"role": "admin"})
        
        if existing_admin:
            logger.warning("⚠️  Admin user already exists!")
            logger.info(f"   Email: {existing_admin['email']}")
            return
        
        # Create admin user
        logger.info("👑 Creating initial admin user...")
        
        admin_user = await UserService.create_user(
            db=db,
            full_name=settings.DEFAULT_ADMIN_FULLNAME,
            email="admin@sentinelops.com",
            password="AdminPassword123!",  # Change this in production!
            age=35,
            marital_status="married",
            criminal_record=False,
            role="admin",
            health_issues=False
        )
        
        logger.info("✅ Admin user created successfully!")
        logger.info(f"   User ID: {admin_user['_id']}")
        logger.info(f"   Email: {admin_user['email']}")
        logger.info(f"   Full Name: {admin_user['full_name']}")
        logger.info(f"   Role: {admin_user['role']}")
        logger.info("\n⚠️  IMPORTANT: Change the default password immediately!")
        logger.info("   Email: admin@sentinelops.com")
        logger.info("   Password: AdminPassword123!")
        
    except Exception as e:
        logger.error(f"❌ Error creating admin: {e}")
    
    finally:
        # Close connection
        client.close()


if __name__ == "__main__":
    asyncio.run(create_initial_admin())
