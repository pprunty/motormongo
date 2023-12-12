from motormongo.fields.field import Field
from bson import Binary
from typing import Callable, Optional, Union

class BinaryField(Field):
    def __init__(self, hash_function: Optional[Callable[[str], bytes]] = None, **kwargs):
        super().__init__(**kwargs)
        self.hash_function = hash_function

    def __set__(self, obj, value: Union[str, bytes, Binary]):
        # Apply the hash function if it's provided and the value is a string
        if self.hash_function is not None and isinstance(value, str):
            value = self.hash_function(value)

        # Check if the value is of appropriate type
        if value is not None and not isinstance(value, (bytes, Binary)):
            raise ValueError(f"Value for {self.name} must be a bytes object or bson.Binary")

        # Convert bytes to bson.Binary for MongoDB storage
        if isinstance(value, bytes):
            value = Binary(value)

        super().__set__(obj, value)

    def __get__(self, obj, objtype=None):
        value = obj.__dict__.get(self.name, self.options.get('default'))
        # Optionally, decode the value if it's stored as Binary
        if isinstance(value, Binary):
            return value.decode()  # or return as-is, depending on your needs
        return value
