class DocumentError(Exception):
    """Base exception class for Document errors."""

    pass


class DocumentInsertError(DocumentError):
    """Raised when an error occurs during document insertion."""

    pass


class DocumentUpdateError(DocumentError):
    """Raised when an error occurs during document update."""

    pass


class DocumentDeleteError(DocumentError):
    """Raised when an error occurs during document deletion."""

    pass


class DocumentNotFoundError(DocumentError):
    """Raised when a document is not found for a query."""

    pass


class DocumentAggregationError(DocumentError):
    """Raised when an error occurs during aggregation."""

    pass


class DocumentValidationError(DocumentError):
    """Raised when a document fails to validate."""

    pass
