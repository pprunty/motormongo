from motormongo.fields.exceptions import GeoCoordinateError
from motormongo.fields.field import Field


class GeoJSONField(Field):
    def __init__(self, return_as_list=False, **kwargs):
        super().__init__(type=(list, tuple, dict), **kwargs)
        self.return_as_list = return_as_list

    def __set__(self, obj, value):
        if value is not None:
            if isinstance(value, (list, tuple)) and len(value) == 2:
                longitude, latitude = value
                if not (-90 <= latitude <= 90) and (-180 <= longitude <= 180):
                    raise GeoCoordinateError(
                        "Latitude must be between -90 and 90, and Longitude must be between -180 and 180"
                    )
                value = {"type": "Point", "coordinates": [longitude, latitude]}
            elif (
                isinstance(value, dict)
                and value.get("type") == "Point"
                and len(value.get("coordinates", [])) == 2
            ):
                longitude, latitude = value["coordinates"]
                if not (-90 <= latitude <= 90) and (-180 <= longitude <= 180):
                    raise GeoCoordinateError(
                        "Latitude must be between -90 and 90, and Longitude must be between -180 and 180"
                    )
            else:
                raise GeoCoordinateError(
                    f"Value must be a list or tuple of [latitude, longitude] or a GeoJSON dictionary. Got {type(value)} of value: {value}"
                )

        super().__set__(obj, value)

    def __get__(self, obj, objtype=None):
        value = super().__get__(obj, objtype)
        if not self.return_as_list:
            return value
        if isinstance(value, dict) and value.get("type") == "Point":
            return value.get("coordinates")
        return value
