import pytest
from tests.test_documents.user import User
from motormongo.fields.exceptions import BooleanFieldError


@pytest.mark.asyncio
async def test_boolean_field_valid_assignment():
    user = User(alive=True)
    assert user.alive is True

    user = User(alive=False)
    assert user.alive is False


@pytest.mark.asyncio
async def test_boolean_field_invalid_assignment():
    with pytest.raises(BooleanFieldError):
        User(alive="not a boolean")


@pytest.mark.asyncio
async def test_boolean_field_none_assignment_w_default():
    user = User(alive=None)
    assert user.alive is True  # Assuming the User BooleanField has default set to True
