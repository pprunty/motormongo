# import os
#
# import pytest
# from motormongo import DataBase
#
# @pytest.fixture(scope="session", autouse=True)
# async def db_connection():
#     await DataBase.connect(uri=os.getenv("MONGODB_URL"), db=os.getenv("MONGODB_COLLECTION"))
#     yield
#     await DataBase.close()
