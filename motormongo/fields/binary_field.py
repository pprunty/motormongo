from typing import Callable, Optional, Union

from bson import Binary

from motormongo.fields.exceptions import BinaryDecodingError, InvalidBinaryTypeError
from motormongo.fields.field import Field


class BinaryField(Field):
    def __init__(
        self,
        hash_function: Optional[Callable[[str], bytes]] = None,
        return_decoded: bool = False,
        encode: Optional[Callable[[str], bytes]] = None,
        decode: Optional[Callable[[bytes], str]] = None,
        **kwargs,
    ):
        super().__init__(type=Binary, **kwargs)
        self.hash_function = hash_function
        self.return_decoded = return_decoded
        self.encode = encode if encode is not None else (lambda x: x.encode("utf-8"))
        self.decode = decode if decode is not None else (lambda x: x.decode("utf-8"))

    def __set__(self, obj, value: Union[str, bytes, Binary]):
        if value is not None and not isinstance(value, (str, bytes, Binary)):
            raise InvalidBinaryTypeError(
                f"Value must be a string, bytes object, or bson.Binary. Got {type(value).__name__}"
            )

        if isinstance(value, str):
            value = self.encode(value)
            if self.hash_function is not None:
                value = self.hash_function(value)

        if isinstance(value, bytes):
            value = Binary(value)

        super().__set__(obj, value)

    def __get__(self, obj, objtype=None):
        value = super().__get__(obj, objtype)
        # Decode the value if it's stored as Binary and return_decoded is True
        if self.return_decoded and isinstance(value, Binary):
            try:
                return self.decode(value)
            except Exception as e:
                raise BinaryDecodingError(f"Error decoding Binary field: {e}")
        return value
