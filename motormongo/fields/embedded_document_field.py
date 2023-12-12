from motormongo.abstracts.document import Document
from motormongo.fields.field import Field

class EmbeddedDocumentField(Field):
    def __init__(self, document_type, **kwargs):
        super().__init__(type=(dict, None), **kwargs)
        if not issubclass(document_type, Document):
            raise TypeError("document_type must be a subclass of Document")
        self.document_type = document_type

    def __set__(self, obj, value):
        if value is not None and not isinstance(value, self.document_type):
            raise TypeError(f"Value must be an instance of {self.document_type.__name__}")
        super().__set__(obj, value)

    def __get__(self, obj, objtype=None):
        return super().__get__(obj, objtype)
