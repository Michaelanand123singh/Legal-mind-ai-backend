from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class Database:
    client: AsyncIOMotorClient = None
    database = None

db = Database()

async def connect_db():
    try:
        db.client = AsyncIOMotorClient(settings.mongodb_url)
        db.database = db.client[settings.database_name]
        # Test the connection
        await db.client.admin.command('ping')
        logger.info("✅ Connected to MongoDB successfully")
        return True
    except Exception as e:
        logger.error(f"❌ MongoDB connection failed: {e}")
        # Don't fail startup, just log the error
        return False

async def close_db():
    if db.client:
        db.client.close()
        logger.info("Disconnected from MongoDB")

async def get_database():
    """
    Async dependency for getting database connection.
    Returns None if database is not connected (non-fatal).
    """
    try:
        if db.database is None:
            logger.warning("Database not initialized, attempting to connect...")
            await connect_db()
        
        return db.database
    except Exception as e:
        logger.error(f"Database error: {e}")
        return None

# Synchronous version for compatibility (returns None if not connected)
def get_database_sync():
    """
    Synchronous version that returns None if database is not available.
    Use this for non-critical operations.
    """
    return db.database