import asyncio
import os
from datetime import datetime

import pytest

from motormongo import DataBase
from tests.test_documents.user import User
from motormongo.fields.exceptions import DateTimeValueError, DateTimeFormatError


@pytest.mark.asyncio
async def test_auto_now_field():
    await DataBase.connect(
        uri=os.getenv("MONGODB_URL"), db=os.getenv("MONGODB_COLLECTION")
    )

    # Assuming User has a field named 'last_login' with auto_now=True
    user = User(username="autonowuser")
    await user.save()

    first_access = user.last_login
    # Wait a bit to ensure a noticeable difference in time
    await asyncio.sleep(1)
    second_access = user.last_login

    assert first_access != second_access
    assert second_access > first_access

    await User.delete_one({"username": user.username})


@pytest.mark.asyncio
async def test_auto_now_add_field():
    await DataBase.connect(
        uri=os.getenv("MONGODB_URL"), db=os.getenv("MONGODB_COLLECTION")
    )

    # Assuming User has a field named 'created_at' with auto_now_add=True
    user = User(username="autonowadduser")
    await user.save()

    initial_value = user.created_at
    # Simulate update
    user.username = "updateduser"
    await user.save()
    updated_value = user.created_at

    assert initial_value == updated_value

    await User.delete_one({"username": user.username})


@pytest.mark.asyncio
async def test_datetime_field_parsing():
    await DataBase.connect(
        uri=os.getenv("MONGODB_URL"), db=os.getenv("MONGODB_COLLECTION")
    )

    user = User(username="datetimeuser", last_login="2023-01-01T12:00:00")
    await user.save()

    assert isinstance(user.last_login, datetime)
    assert user.last_login == datetime(2023, 1, 1, 12, 0, 0)

    await User.delete_one({"username": user.username})


@pytest.mark.asyncio
async def test_datetime_field_type_validation():
    await DataBase.connect(
        uri=os.getenv("MONGODB_URL"), db=os.getenv("MONGODB_COLLECTION")
    )

    with pytest.raises(ValueError):
        # Assuming User has a 'signup_date' DateTimeField
        user = User(username="wrongdateuser", last_login="not a real date")
        await user.save()


@pytest.mark.asyncio
async def test_datetime_field_valid_assignment():
    user = User(last_login="2023-01-01T12:00:00")
    assert user.last_login.year == 2023


@pytest.mark.asyncio
async def test_datetime_field_invalid_format():
    with pytest.raises(DateTimeFormatError):
        User(last_login="01-01-2023 12:00:00")  # Assuming this format is not supported


@pytest.mark.asyncio
async def test_datetime_field_invalid_type():
    with pytest.raises(DateTimeValueError):
        User(last_login=123)  # Not a datetime object, date object, or string
