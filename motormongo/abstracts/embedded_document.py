from motormongo.fields.field import Field


class EmbeddedDocument:
    def __init__(self, **kwargs):
        for name, field in self.__class__.__dict__.items():
            if isinstance(field, Field):
                setattr(self, name, kwargs.get(name, field.options.get("default")))

    def to_dict(self):
        return {
            k: (v.to_dict() if isinstance(v, EmbeddedDocument) else v)
            for k, v in self.__dict__.items()
            if "__" not in k and k != "Meta"
        }
