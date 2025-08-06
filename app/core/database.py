from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class Database:
    client: AsyncIOMotorClient = None
    database = None
    connected: bool = False

db = Database()

async def connect_db():
    """Connect to MongoDB database"""
    try:
        # Check if MongoDB URL is configured
        if not settings.mongodb_url or settings.mongodb_url == "mongodb://localhost:27017":
            logger.warning("⚠️  MongoDB URL not configured properly - running without database")
            logger.info("Set MONGODB_URL environment variable to connect to database")
            db.connected = False
            return False
            
        logger.info(f"Attempting to connect to MongoDB: {settings.mongodb_url[:20]}...")
        
        # Create client with timeout
        db.client = AsyncIOMotorClient(
            settings.mongodb_url,
            serverSelectionTimeoutMS=5000,  # 5 second timeout
            connectTimeoutMS=5000,
            socketTimeoutMS=5000
        )
        
        db.database = db.client[settings.database_name]
        
        # Test the connection with a simple command
        await db.client.admin.command('ping')
        db.connected = True
        logger.info("✅ Connected to MongoDB successfully")
        return True
        
    except Exception as e:
        logger.warning(f"⚠️  MongoDB connection failed: {str(e)}")
        logger.info("Application will run in demo mode without database persistence")
        db.connected = False
        db.client = None
        db.database = None
        return False

async def close_db():
    """Close database connection"""
    try:
        if db.client:
            db.client.close()
            logger.info("📴 Disconnected from MongoDB")
            db.connected = False
            db.client = None
            db.database = None
    except Exception as e:
        logger.warning(f"Error closing database connection: {e}")

async def get_database():
    """
    Dependency for getting database connection.
    Returns None if database is not connected (allows app to work without DB).
    """
    try:
        # Return None if not connected (this is normal and expected)
        if not db.connected or db.database is None:
            return None
        
        return db.database
    except Exception as e:
        logger.warning(f"Database access error: {e}")
        return None

def get_database_sync():
    """
    Synchronous version that returns None if database is not available.
    This is normal behavior when running without database.
    """
    if db.connected and db.database:
        return db.database
    return None

def is_database_connected() -> bool:
    """Check if database is connected"""
    return db.connected and db.database is not None