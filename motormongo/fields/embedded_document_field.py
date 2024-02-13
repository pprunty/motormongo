from motormongo.fields.field import Field
from motormongo.abstracts.embedded_document import EmbeddedDocument
from pydantic import BaseModel

class EmbeddedDocumentField(Field):
    def __init__(self, document_type, **kwargs):
        super().__init__(type=(dict, EmbeddedDocument), **kwargs)
        if not issubclass(document_type, EmbeddedDocument):
            raise TypeError("document_type must be a subclass of Document")
        self.document_type = document_type

    def __set__(self, obj, value):
        # If the value is an instance of Pydantic BaseModel, convert to document_type
        if isinstance(value, BaseModel):
            value = self.document_type(**value.dict())
        # Check if value is None, an instance of dict, an instance of EmbeddedDocument, or an instance of the specified document_type.
        if value is not None and not isinstance(value, (dict, EmbeddedDocument, self.document_type)):
            raise TypeError(f"Value must be an instance of dict, EmbeddedDocument, or {self.document_type.__name__}. Got {type(value)}.")
        super().__set__(obj, value)

    def __get__(self, obj, objtype=None):
        return super().__get__(obj, objtype)
