import inspect
import typing
from typing import Callable, Optional, Union

from bson import Binary

from motormongo.fields.exceptions import (
    BinaryDecodingError,
    InvalidBinaryTypeError,
    MissingTypeAnnotationError,
)
from motormongo.fields.field import Field


class BinaryField(Field):
    def __init__(
        self,
        hash_function: Optional[Callable[[Union[str, bytes]], bytes]] = None,
        return_decoded: bool = False,
        encode: Optional[Callable[[str], bytes]] = None,
        decode: Optional[Callable[[bytes], str]] = None,
        **kwargs,
    ):
        super().__init__(type=Binary, **kwargs)
        self.hash_function = hash_function
        self.return_decoded = return_decoded
        self.encode = encode or (lambda s: s.encode("utf-8"))  # Default UTF-8 encode
        self.decode = decode or (lambda b: b.decode("utf-8"))  # Default UTF-8 decode
        if self.hash_function:
            self._check_hash_function_annotation()

    def __set__(self, obj, value: Union[str, bytes, Binary]):
        if value is not None and not isinstance(value, (str, bytes, Binary)):
            raise InvalidBinaryTypeError(
                f"Value must be a string, bytes object, or bson.Binary. Got {type(value).__name__} of value {value}."
            )

        if isinstance(value, str) and self.hash_function:
            # Determine the parameter type of the hash_function
            param = list(inspect.signature(self.hash_function).parameters.values())[0]
            if param.annotation in [str, typing.Union[str, bytes]]:
                # If the hash function accepts a string, pass it directly
                value = self.hash_function(value)
            else:
                # Otherwise, encode the string and then hash
                encoded_value = self.encode(value)
                value = self.hash_function(encoded_value)
        elif isinstance(value, str):
            # If there's no hash function, but an encode function, just encode
            value = self.encode(value)

        if isinstance(value, bytes):
            value = Binary(value)

        super().__set__(obj, value)

    def __get__(self, obj, objtype=None):
        value = super().__get__(obj, objtype)
        # Attempt to decode only if return_decoded is True and hash_function is not used
        if (
            self.return_decoded
            and self.hash_function is None
            and isinstance(value, Binary)
        ):
            try:
                # Decode using the provided or default decode function
                value = self.decode(value)
            except Exception as e:
                raise BinaryDecodingError(f"Error decoding Binary field: {e}")
        return value

    def _check_hash_function_annotation(self):
        params = list(inspect.signature(self.hash_function).parameters.values())
        if not params or params[0].annotation is inspect._empty:
            raise MissingTypeAnnotationError(
                "The BinaryField hash_function must have a type annotation indicating "
                "whether it expects a 'str' or 'bytes'. This is necessary to "
                "determine if encoding should take place within the BinaryField class or "
                "by the hash_function itself. If you want to use custom encoding and not "
                "BinaryField's default encoding, pass encoding function to encode parameter."
            )
