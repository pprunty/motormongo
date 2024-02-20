import pytest
from tests.test_documents.user import User  # Adjust the import according to your project structure
from motormongo.fields.exceptions import FloatValueError, FloatRangeError  # Adjust the import path

@pytest.mark.asyncio
async def test_net_worth_valid():
    model = User(net_worth=8)
    assert model.net_worth == 8

@pytest.mark.asyncio
async def test_net_worth_invalid_type():
    with pytest.raises(FloatValueError):
        User(net_worth="not a float")

@pytest.mark.asyncio
async def test_net_worth_below_min_value():
    with pytest.raises(FloatRangeError):
        User(net_worth=4.9)  # Assuming min_value is set to 5.0 in User

@pytest.mark.asyncio
async def test_net_worth_above_max_value():
    with pytest.raises(FloatRangeError):
        User(net_worth=10.1)  # Assuming max_value is set to 10.0 in User
