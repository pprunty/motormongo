from motormongo.fields.field import Field


class GeoPointField(Field):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __set__(self, obj, value):
        if value is not None:
            if not (isinstance(value, (list, tuple)) and len(value) == 2):
                raise ValueError(f"Value for {self.name} must be a list or tuple of length 2")
            latitude, longitude = value
            if not (-90 <= latitude <= 90):
                raise ValueError("Latitude must be between -90 and 90")
            if not (-180 <= longitude <= 180):
                raise ValueError("Longitude must be between -180 and 180")
            # Store as GeoJSON
            value = {"type": "Point", "coordinates": [longitude, latitude]}
        super().__set__(obj, value)
