import os

from motormongo import DataBase


async def init_db():
    await DataBase.connect(uri=os.getenv("MONOGODB_URL"), database=os.getenv("MONGODB_COLLECTION"))