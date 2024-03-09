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

    def validate(self, value):
        """Validate or instantiate an embedded document from the provided value."""
        if isinstance(value, (BaseModel, dict)):
            value_dict = value.model_dump() if isinstance(value, BaseModel) else value
            try:
                # Attempt to instantiate document_type with the dictionary
                value = self.document_type(**value_dict)
            except Exception as e:
                raise EmbeddedDocumentTypeError(
                    f"Failed to instantiate {self.document_type.__name__} with provided value. Error: {e}"
                )
        elif not isinstance(value, self.document_type):
            raise EmbeddedDocumentTypeError(
                f"Value must be an instance of {self.document_type.__name__}, a dictionary, or a BaseModel. Got {type(value).__name__} of value: {value}."
            )
        return value  # Return the validated or instantiated value

    def __set__(self, obj, value):
        if value is not None:
            validated_value = self.validate(value)  # Use validate method
            super().__set__(obj, validated_value)
        else:
            super().__set__(obj, value)

    def __get__(self, obj, objtype=None):
        return super().__get__(obj, objtype)
