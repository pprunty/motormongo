import os
from datetime import datetime

import pytest
from pydantic import BaseModel

from motormongo import Document, EmbeddedDocument, EmbeddedDocumentField, StringField, DataBase
from motormongo.fields.exceptions import EmbeddedDocumentTypeError
from tests.test_documents.user import Profile, User


def test_embedded_document_field_valid_assignment():
    user = User(profile=Profile(bio="Software Developer", website="example.com"))
    print(user.profile.bio)
    assert user.profile.bio == "Software Developer"
    assert user.profile.website == "example.com"


def test_embedded_document_field_invalid_assignment():
    with pytest.raises(EmbeddedDocumentTypeError):
        User(profile="not a valid embedded document")


def test_embedded_document_field_assignment_with_dict():
    user = User(profile={"bio": "Loves coding", "website": "coder.com"})
    assert user.profile.bio == "Loves coding"
    assert user.profile.website == "coder.com"


class PydanticProfile(BaseModel):
    bio: str
    website: str


def test_embedded_document_field_assignment_with_pydantic_model():
    pydantic_profile = PydanticProfile(bio="Pydantic User", website="pydantic.com")
    user = User(profile=pydantic_profile)
    assert user.profile.bio == "Pydantic User"
    assert user.profile.website == "pydantic.com"


def test_embedded_document_field_none_assignment():
    user = User(profile=None)
    assert user.profile is None


def test_update_embedded_document_field():
    user = User(profile=Profile(bio="Original Bio", website="original.com"))
    user.profile.bio = "Updated Bio"
    assert user.profile.bio == "Updated Bio"


def test_partial_dict_assignment_to_embedded_document():
    user = User(profile={"bio": "Partial info"})
    assert user.profile.bio == "Partial info"
    # Assuming 'website' is optional or has a default value
    assert user.profile.website is None or isinstance(user.profile.website, str)


def test_embedded_document_invalid_assignment():
    with pytest.raises(EmbeddedDocumentTypeError):

        class Doc(Document):
            metadata = EmbeddedDocumentField(document_type=object)


@pytest.mark.asyncio
async def test_embedded_with_timestamps():
    await DataBase.connect(uri=os.getenv("MONGODB_URL"), db=os.getenv("MONGODB_DB"))

    user = User(username="datetimeuser", dob="2023-01-01T12:00:00", profile=Profile(bio="hello world"))

    await user.save()

    print(f"user profile = {user.profile.to_dict()}")
    assert isinstance(user.profile.created_at, datetime)
    assert isinstance(user.profile.updated_at, datetime)

    await User.delete_many({})
