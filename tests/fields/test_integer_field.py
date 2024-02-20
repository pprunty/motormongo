import pytest
from tests.test_documents.user import User
from motormongo.fields.exceptions import IntegerValueError, IntegerRangeError

@pytest.mark.asyncio
async def test_integer_field_valid_assignment():
    user = User(age=30)
    assert user.age == 30

@pytest.mark.asyncio
async def test_integer_field_invalid_assignment():
    with pytest.raises(IntegerValueError):
        User(age="not an integer")

@pytest.mark.asyncio
async def test_integer_field_below_min_value():
    with pytest.raises(IntegerRangeError):
        User(age=4)  # Assuming min_value is set to 5 in User's age field

@pytest.mark.asyncio
async def test_integer_field_above_max_value():
    with pytest.raises(IntegerRangeError):
        User(age=101)  # Assuming max_value is set to 100 in User's age field
