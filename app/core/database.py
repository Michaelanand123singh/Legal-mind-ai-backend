from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

class Database:
    client: AsyncIOMotorClient = None
    database = None

db = Database()

async def connect_db():
    db.client = AsyncIOMotorClient(settings.mongodb_url)
    db.database = db.client[settings.database_name]
    print("Connected to MongoDB")

async def close_db():
    if db.client:
        db.client.close()
        print("Disconnected from MongoDB")

def get_database():
    return db.database