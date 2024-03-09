from motormongo.fields import Field
from motormongo.fields.exceptions import ListItemTypeError, ListValueTypeError


class ListField(Field):
    def __init__(self, field=None, **kwargs):
        super().__init__(type=list, **kwargs)
        self.field = field  # This should be an instance of a Field subclass

    def __set__(self, obj, value):
        if value is not None:
            if not isinstance(value, list):
                raise ListValueTypeError(
                    f"Value for {self.name} must be a list. Got {type(value).__name__} of value: {value}."
                )

            processed_list = []
            if hasattr(self.field, "validate"):
                # Use the field's validate method for each item if available
                for item in value:
                    try:
                        # Validate the item using the field's validate method, which also handles instantiation for EmbeddedDocumentField
                        validated_item = self.field.validate(item)
                    except Exception as e:
                        # Handle or raise validation errors as appropriate
                        raise ListItemTypeError(
                            f"Error validating ListField item's datatypes: {e}"
                        )
                    processed_list.append(validated_item)
            else:
                # No specific field validation available, use the items directly
                processed_list = value

            # Finally, set the processed list to the object's attribute
            super().__set__(obj, processed_list)

    def __get__(self, obj, objtype=None):
        # Simply return the attribute's value, assuming it's already a processed list
        return super().__get__(obj, objtype)
