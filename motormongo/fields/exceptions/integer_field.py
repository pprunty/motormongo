class IntegerFieldError(Exception):
    """Base exception for errors related to the IntegerField."""


class IntegerValueError(IntegerFieldError):
    """Exception raised for invalid integer values."""


class IntegerRangeError(IntegerFieldError):
    """Exception raised when an integer value is out of the specified range."""
