class FloatFieldError(Exception):
    """Base exception for all FloatField errors."""


class FloatValueError(FloatFieldError):
    """Exception raised for invalid float values."""


class FloatRangeError(FloatFieldError):
    """Exception raised when a float value is out of the specified range."""
