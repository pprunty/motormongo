class EmbeddedDocumentFieldError(Exception):
    """Base exception for errors related to the EmbeddedDocumentField."""


class EmbeddedDocumentTypeError(EmbeddedDocumentFieldError):
    """Exception raised for invalid embedded document types."""
