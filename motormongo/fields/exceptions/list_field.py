class ListFieldError(Exception):
    """Base exception for errors related to the ListField."""


class ListValueTypeError(ListFieldError):
    """Exception raised for invalid value types in a ListField."""


class ListItemTypeError(ListFieldError):
    """Exception raised for invalid item types in a ListField."""
