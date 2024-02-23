class ReferenceFieldError(Exception):
    """Base exception for errors related to the ReferenceField."""


class ReferenceValueError(ReferenceFieldError):
    """Exception raised for invalid reference values."""


class ReferenceTypeError(ReferenceFieldError):
    """Exception raised when a reference value is of an incorrect type."""


class ReferenceConversionError(ReferenceFieldError):
    """Exception raised when a string value cannot be converted to an ObjectId."""
