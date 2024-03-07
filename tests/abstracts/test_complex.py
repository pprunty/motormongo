import os

import pytest

from motormongo import DataBase
from tests.test_documents.user import User


@pytest.mark.asyncio
async def test_find_one_success():
    await DataBase.connect(uri=os.getenv("MONGODB_URL"), db=os.getenv("MONGODB_DB"))
    from datetime import datetime

    from motormongo import (DateTimeField, EmbeddedDocument,
                            EmbeddedDocumentField, GeoJSONField, ListField,
                            Document, ReferenceField, IntegerField)

    from tests.test_documents.user import User

    class Location(EmbeddedDocument):
        coordinates = GeoJSONField(
            help_text="The coordinates for the user's location")
        last_seen = DateTimeField(
            default=datetime.now(),
            required=True,
            help_text="The last time the user was at this location")
        frequency = IntegerField(
            default=0, help_text="How many times the user was in this location")

        class Meta:
            created_at_timestamp = True
            updated_at_timestamp = True
            indexes = [
                {'fields': [('frequency', -1)]},
            ]

    class UserLocation(Document):
        user = ReferenceField(User,
                              help_text="A reference back to the User document",
                              editable=False,
                              updated=False)
        refuge = GeoJSONField(help_text="The user's refuge/home location")
        locations = ListField(EmbeddedDocumentField(Location),
                              help_text="A list of the user's past locations")

    user = {
        "username": "johndoe",
        "email": "johndoe@hotmail.com",
        "password": "password123",
        "age": 69,
    }

    new_user = await User.insert_one(user)

    new_coordinates = [0,0]

    new_user_location = UserLocation(
        user=new_user._id,
        refuge=new_coordinates,
        locations=[
            Location(coordinates=new_coordinates,
                     last_seen=datetime.utcnow())
        ])

    user_location, exists = await UserLocation.find_one_or_create(
        {"_id": new_user._id},
        new_user_location.to_dict()
    )

    assert user_location
    # await UserLocation.delete_many({})
    await User.delete_many({})
