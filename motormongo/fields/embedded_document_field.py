from pydantic import BaseModel

from motormongo.fields.exceptions import EmbeddedDocumentTypeError
from motormongo.fields.field import Field


class EmbeddedDocumentField(Field):
    def __init__(self, document_type, **kwargs):
        from motormongo.abstracts.embedded_document import EmbeddedDocument

        super().__init__(type=(dict, EmbeddedDocument), **kwargs)
        if not issubclass(document_type, (EmbeddedDocument, BaseModel)):
            raise EmbeddedDocumentTypeError(
                f"document_type must be a subclass of EmbeddedDocument or Pydantic BaseModel. Got {type(document_type)}."
            )
        self.document_type = document_type

    def __set__(self, obj, value):
        # Check if the value is a Pydantic BaseModel or a dictionary, and convert to document_type
        if isinstance(value, (BaseModel, dict)):
            # For Pydantic BaseModel, use .dict() method to convert to dictionary
            value_dict = value.model_dump() if isinstance(value, BaseModel) else value
            try:
                # Attempt to instantiate document_type with the dictionary
                value = self.document_type(**value_dict)
            except Exception as e:
                raise EmbeddedDocumentTypeError(
                    f"Failed to instantiate {self.document_type.__name__} with provided value. Error: {e}"
                )

        # Now check if value is None or an instance of the document_type or EmbeddedDocument
        if value is not None and not isinstance(value, self.document_type):
            raise EmbeddedDocumentTypeError(
                f"Value must be an instance of {self.document_type.__name__}, a dictionary, or a BaseModel. Got {type(value).__name__} of value: {value}."
            )

        super().__set__(obj, value)

    def __get__(self, obj, objtype=None):
        return super().__get__(obj, objtype)
