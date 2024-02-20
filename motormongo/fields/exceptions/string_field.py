class StringFieldError(Exception):
    """Base exception for errors related to the StringField."""


class StringValueError(StringFieldError):
    """Exception raised for invalid string values."""


class StringLengthError(StringFieldError):
    """Exception raised when a string value does not meet length requirements."""


class StringPatternError(StringFieldError):
    """Exception raised when a string value does not match the required pattern."""
