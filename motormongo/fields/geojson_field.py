from motormongo.fields.field import Field


class GeoJSONField(Field):
    def __init__(self, return_as_list=False, **kwargs):
        super().__init__(type=(list, tuple, dict), **kwargs)
        self.return_as_list = return_as_list

    def __set__(self, obj, value):
        if value is not None:
            # Check if value is a list or tuple of length 2 (latitude, longitude)
            if isinstance(value, (list, tuple)) and len(value) == 2:
                latitude, longitude = value
                if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
                    raise ValueError(
                        "Latitude must be between -90 and 90, and Longitude must be between -180 and 180"
                    )
                value = {"type": "Point", "coordinates": [longitude, latitude]}
            # Check if value is in GeoJSON format
            elif (
                isinstance(value, dict)
                and value.get("type") == "Point"
                and len(value.get("coordinates", [])) == 2
            ):
                latitude, longitude = value["coordinates"]
                if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
                    raise ValueError(
                        "Latitude must be between -90 and 90, and Longitude must be between -180 and 180"
                    )
            else:
                raise ValueError(
                    "Value for GeoJSONField must be a list or tuple of [latitude, longitude] or a GeoJSON dictionary"
                )

        super().__set__(obj, value)

    def __get__(self, obj, objtype=None):
        value = super().__get__(obj, objtype)
        # Return the entire GeoJSON dictionary if the flag is set
        if not self.return_as_list:
            return value
        # Otherwise, return just the coordinates
        if isinstance(value, dict) and value.get("type") == "Point":
            return value.get("coordinates")
        return value
