import os

import pytest

from motormongo import DataBase
from motormongo.fields.exceptions import InvalidEnumTypeError, InvalidEnumValueError
from tests.test_documents.user import Status, User


@pytest.mark.asyncio
async def test_enum_assignment():
    await DataBase.connect(
        uri=os.getenv("MONGODB_URL"), db=os.getenv("MONGODB_COLLECTION")
    )

    user = User(status=Status.ACTIVE)
    assert user.status == Status.ACTIVE.value


@pytest.mark.asyncio
async def test_string_assignment():
    await DataBase.connect(
        uri=os.getenv("MONGODB_URL"), db=os.getenv("MONGODB_COLLECTION")
    )

    user = User(status="active")
    assert user.status == Status.ACTIVE.value


@pytest.mark.asyncio
async def test_invalid_string_assignment():
    await DataBase.connect(
        uri=os.getenv("MONGODB_URL"), db=os.getenv("MONGODB_COLLECTION")
    )

    with pytest.raises(InvalidEnumValueError):
        User(status="not_a_valid_status")


@pytest.mark.asyncio
async def test_invalid_type_assignment():
    await DataBase.connect(
        uri=os.getenv("MONGODB_URL"), db=os.getenv("MONGODB_COLLECTION")
    )

    with pytest.raises(InvalidEnumTypeError):
        User(status=123)  # Assuming integers are not valid for the Status enum
