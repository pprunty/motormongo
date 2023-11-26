from motormongo.fields.field import Field
from bson import Binary


class BinaryField(Field):
    def __init__(self, hash_function=None, **kwargs):
        super().__init__(**kwargs)
        self.hash_function = hash_function

    def __set__(self, obj, value):
        if self.hash_function is not None and isinstance(value, str):
            value = self.hash_function(value)

        if value is not None and not isinstance(value, (bytes, Binary)):
            raise ValueError(f"Value for {self.name} must be a bytes object or bson.Binary")

        if isinstance(value, bytes):
            value = Binary(value)

        super().__set__(obj, value)

    def __get__(self, obj, objtype=None):
        value = obj.__dict__.get(self.name, self.options.get('default'))
        if isinstance(value, Binary):
            return value.decode()  # or return as-is, depending on your needs
        return value
