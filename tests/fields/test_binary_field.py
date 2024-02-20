import os

import pytest

from motormongo import BinaryField, DataBase, Document, StringField
from tests.test_documents.user import User


@pytest.mark.asyncio
async def test_password_verification_direct():
    await DataBase.connect(
        uri=os.getenv("MONGODB_URL"), db=os.getenv("MONGODB_COLLECTION")
    )

    user_data = {
        "username": "janedoe",
        "email": "janedoe@example.com",
        "password": "mypassword",
        "age": 25,
    }
    user = await User.insert_one(user_data)
    user_id = user._id

    retrieved_user = await User.find_one({"_id": user_id})
    assert retrieved_user is not None

    # Assuming User model has a method like this
    is_verified = retrieved_user.verify_password("mypassword")
    assert is_verified == True

    is_verified_wrong = retrieved_user.verify_password("wrongpassword")
    assert is_verified_wrong == False

    await User.delete_one({"_id": user_id})


@pytest.mark.asyncio
async def test_type_validation():
    await DataBase.connect(
        uri=os.getenv("MONGODB_URL"), db=os.getenv("MONGODB_COLLECTION")
    )

    user_data = {
        "username": "typevalidationuser",
        "email": "typevalidationuser@example.com",
        "password": 12345,  # Intentionally incorrect type
        "age": 30,
    }

    # Expecting a ValueError due to incorrect password type
    with pytest.raises(ValueError):
        await User.insert_one(user_data)


@pytest.mark.asyncio
async def test_custom_encode_decode_functions_w_bad_classname():
    await DataBase.connect(
        uri=os.getenv("MONGODB_URL"), db=os.getenv("MONGODB_COLLECTION")
    )

    # Custom encode/decode functions for testing
    def custom_encode(input_str: str) -> bytes:
        return ("custom_" + input_str).encode("utf-8")

    def custom_decode(input_bytes: bytes) -> str:
        return input_bytes.decode("utf-8").replace("custom_", "")

    class New__User(Document):
        username = StringField(min_length=3, max_length=50)
        password = BinaryField(
            encode=custom_encode, decode=custom_decode, return_decoded=True
        )

    user_data = {
        "username": "customencodetestuser",
        "password": "customencodingtest",
    }

    user = await New__User.insert_one(user_data)
    retrieved_user = await New__User.find_one({"_id": user._id})

    assert retrieved_user is not None
    # Check if custom encoding/decoding was applied
    assert retrieved_user.password == "customencodingtest"

    await New__User.delete_one({"_id": user._id})
