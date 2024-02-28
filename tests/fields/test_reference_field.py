import os

import pytest
from bson import ObjectId

from motormongo import DataBase, Document, StringField
from motormongo.fields.exceptions import (
    ReferenceConversionError,
    ReferenceTypeError,
    ReferenceValueError,
)
from tests.test_documents.reference import Post, User


async def test_reference_field_set_with_instance():
    await DataBase.connect(uri=os.getenv("MONGODB_URL"), db=os.getenv("MONGODB_DB"))

    user = User(name="John Doe")
    await user.save()
    post = Post(author=user._id)

    referenced_user = (
        await post.author
    )  # Correctly await the coroutine to fetch the referenced document
    assert "_id" in referenced_user.to_dict()
    assert "name" in referenced_user.to_dict()
    assert referenced_user is not None, "Referenced user should not be None"


@pytest.mark.asyncio
async def test_reference_field_set_with_string_id():
    await DataBase.connect(uri=os.getenv("MONGODB_URL"), db=os.getenv("MONGODB_DB"))

    # Create and save a user
    user = User(name="Jane Doe")
    await user.save()

    # Create a post with the user's ID as a string
    user_id_str = str(user._id)
    post = Post(author=user_id_str)

    # Fetch the referenced user
    referenced_user = await post.author
    assert referenced_user is not None, "Referenced user should not be None"
    assert referenced_user._id == ObjectId(
        user_id_str
    ), "Referenced user ID should match the original user ID"


@pytest.mark.asyncio
async def test_reference_field_set_invalid_type():
    await DataBase.connect(uri=os.getenv("MONGODB_URL"), db=os.getenv("MONGODB_DB"))

    # Attempt to create a post with an invalid author reference
    with pytest.raises(ReferenceTypeError):
        Post(author=123)  # Using an integer instead of ObjectId or User instance


@pytest.mark.asyncio
async def test_async_fetch_referenced_document():
    await DataBase.connect(uri=os.getenv("MONGODB_URL"), db=os.getenv("MONGODB_DB"))

    # Create and save a user
    user = User(name="Alex Smith")
    await user.save()

    # Create a post referencing the user
    post = Post(author=user._id)
    await post.save()  # Assuming you have a method to save the post

    # Fetch the referenced user
    referenced_user = await post.author
    assert (
        referenced_user is not None
    ), "Should asynchronously fetch and find the referenced user"
    assert (
        referenced_user._id == user._id
    ), "Referenced user ID should match the original user ID"


# @pytest.mark.asyncio
# async def test_reference_field_with_missing_id_attr():
#     await DataBase.connect(uri=os.getenv("MONGODB_URL"), db=os.getenv("MONGODB_DB"))
#
#     user = User(name="Alex Smith")
#     await user.save()
#     del user._id
#
#     with pytest.raises(ReferenceValueError):
#         post = Post(author=user)  # This should raise an error


@pytest.mark.asyncio
async def test_reference_field_with_invalid_string():
    with pytest.raises(ReferenceConversionError):
        post = Post(author="invalid_object_id_string")  # This should raise an error
