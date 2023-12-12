import os

from motor.motor_asyncio import AsyncIOMotorClient
# from motormongo.utils.odm_init import initialize_odm


class DataBase:
    client = None
    db = None


async def connect(uri: str, db: str):
    DataBase.client = AsyncIOMotorClient(uri or os.getenv("MONGODB_URL"))
    DataBase.db = AsyncIOMotorClient(uri or os.getenv("MONGODB_URL"))[db or os.getenv("MONGODB_COLLECTION")]
    # todo: initialize odm class indexes, etc.
    # await initialize_odm()

# todo: add methods to check if uri and db is correct based on pymongo errors

async def get_db():
    if DataBase.db is None:
        raise RuntimeError("Database not connected")
    return DataBase.db