import pytest

from motormongo.fields.exceptions import (
    StringLengthError,
    StringPatternError,
    StringValueError,
)
from tests.test_documents.user import User


@pytest.mark.asyncio
async def test_string_field_valid_assignment():
    user = User(username="validUser")
    assert user.username == "validUser"


@pytest.mark.asyncio
async def test_string_field_invalid_type_assignment():
    with pytest.raises(StringValueError):
        User(username=123)  # Not a string


@pytest.mark.asyncio
async def test_string_field_below_min_length():
    with pytest.raises(StringLengthError):
        User(username="")  # Assuming min_length > 0


@pytest.mark.asyncio
async def test_string_field_above_max_length():
    with pytest.raises(StringLengthError):
        User(username="a" * 51)  # Assuming max_length is 50


@pytest.mark.asyncio
async def test_string_field_regex_mismatch():
    with pytest.raises(StringPatternError):
        User(email="invalidemail")  # Assuming regex for email validation
