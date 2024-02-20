class GeoJSONFieldError(Exception):
    """Base exception for errors related to the GeoJSONField."""


class GeoCoordinateError(GeoJSONFieldError):
    """Exception raised for invalid geographic coordinates."""
