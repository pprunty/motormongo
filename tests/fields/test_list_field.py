import pytest
from tests.test_documents.user import User
from motormongo.fields.exceptions import ListValueTypeError, ListItemTypeError

@pytest.mark.asyncio
async def test_list_field_valid_assignment():
    user = User(favorite_colors=["red", "blue", "green"])
    assert user.favorite_colors == ["red", "blue", "green"]

@pytest.mark.asyncio
async def test_list_field_invalid_assignment():
    with pytest.raises(ListValueTypeError):
        User(favorite_colors="not a list")

@pytest.mark.asyncio
async def test_list_field_item_type_mismatch():
    # Assuming favorite_colors is a ListField of StringField(s)
    with pytest.raises(ListItemTypeError):
        User(favorite_colors=["red", 123, "green"])  # 123 is not a valid string item
