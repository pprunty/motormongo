import pytest

from motormongo import Document, GeoJSONField
from motormongo.fields.exceptions import GeoCoordinateError
from tests.test_documents.user import User


def test_geojson_field_valid_assignment():
    user = User(location=[40.730610, -73.935242])  # longitude, latitude for New York
    assert user.location == [40.730610, -73.935242]  # Assuming return_as_list = True


def test_geojson_field_invalid_coordinates():
    with pytest.raises(GeoCoordinateError):
        User(location=[95, -190])  # Invalid longitude and latitude


def test_geojson_field_dict_assignment():
    user = User(location={"type": "Point", "coordinates": [40.730610, -73.935242]})
    assert user.location == [40.730610, -73.935242]  # Assuming return_as_list = True


def test_geojson_field_dict_assignment_w_json():
    class Location(Document):
        coords = GeoJSONField(return_as_list=False)

    location = Location(
        coords={"type": "Point", "coordinates": [40.730610, -73.935242]}
    )
    assert location.coords == {"type": "Point", "coordinates": [40.730610, -73.935242]}


def test_geojson_field_invalid_dict():
    with pytest.raises(GeoCoordinateError):
        User(
            location={"type": "Point", "coordinates": [95, -190]}
        )  # Invalid coordinates in dict

async def test_invalid_geojson_assignment():
    with pytest.raises(GeoCoordinateError):
        User(
            location="12,12"
        )  # Invalid type


# TODO: Test return_as_list retrieval here