class EnumFieldError(Exception):
    """Base exception for all EnumField errors."""


class InvalidEnumValueError(EnumFieldError):
    """Exception raised when an invalid value is assigned to an EnumField."""


class InvalidEnumTypeError(EnumFieldError):
    """Exception raised when a non-enum type is assigned to an EnumField."""
