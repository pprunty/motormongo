import asyncio
import os

from motormongo import DataBase
from tests.test_documents.items import Book, Electronics
from tests.test_documents.user import User


async def my_async_cleanup():
    await DataBase.connect(uri=os.getenv("MONGODB_URL"), db=os.getenv("MONGODB_DB"))
    await User.delete_many({})
    await Book.delete_many({})
    await Electronics.delete_many({})


def pytest_sessionfinish(session, exitstatus):
    loop = asyncio.get_event_loop()
    if loop.is_closed():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    loop.run_until_complete(my_async_cleanup())
    loop.close()
