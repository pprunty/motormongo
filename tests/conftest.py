import asyncio
import os

from motormongo import DataBase
from tests.test_documents.items import Book, Electronics
from tests.test_documents.reference import Post, User
from tests.test_documents.user import User as Users


async def my_async_cleanup():
    await DataBase.connect(uri=os.getenv("MONGODB_URL"), db=os.getenv("MONGODB_DB"))
    await Users.delete_many({})
    await Book.delete_many({})
    await Electronics.delete_many({})
    await Post.delete_many({})
    await User.delete_many({})


def pytest_sessionfinish(session, exitstatus):
    loop = asyncio.get_event_loop()
    if loop.is_closed():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    loop.run_until_complete(my_async_cleanup())
    loop.close()
