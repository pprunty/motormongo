import pytest
import os
from motormongo import DataBase


@pytest.fixture(scope="module", autouse=True)
async def init_db_fixture():
    await DataBase.connect(uri=os.getenv("MONOGODB_URL"), db=os.getenv("MONGODB_COLLECTION"))
    yield
    await DataBase.close()