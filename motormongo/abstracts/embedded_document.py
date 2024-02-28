from motormongo import Document


class EmbeddedDocument(Document):
    _fields = {}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls._fields = (
            {}
        )  # Ensure this is explicitly done if not inherited automatically

    # def to_dict(self):
    #     return {
    #         k: (v.to_dict() if isinstance(v, EmbeddedDocument) else v)
    #         for k, v in self.__dict__.items()
    #         if "__" not in k and k != "Meta"
    #     }
