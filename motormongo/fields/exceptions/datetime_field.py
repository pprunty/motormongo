class DateTimeFieldError(Exception):
    """Base exception for errors related to the DateTimeField."""


class DateTimeValueError(DateTimeFieldError):
    """Exception raised for invalid datetime values."""


class DateTimeFormatError(DateTimeFieldError):
    """Exception raised when a datetime value does not meet the required format."""
