class BinaryFieldError(Exception):
    """Base exception for all BinaryField errors."""

class InvalidBinaryTypeError(BinaryFieldError):
    """Exception raised when an invalid type is set to a BinaryField."""

class BinaryDecodingError(BinaryFieldError):
    """Exception raised during decoding errors in a BinaryField."""
