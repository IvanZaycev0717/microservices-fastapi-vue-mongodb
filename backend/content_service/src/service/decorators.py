from bson import ObjectId


def convert_objectid_to_str(cls):
    """Class decorator to convert ObjectId fields to strings in Pydantic models.

    Automatically converts any ObjectId values in the input data to strings
    before initializing the Pydantic model instance.

    Returns:
        The decorated class with modified __init__ method.

    Note:
        - Useful for MongoDB documents where _id is stored as ObjectId
        - Ensures JSON serialization compatibility
        - Modifies the class in-place by replacing the __init__ method
    """
    original_init = cls.__init__

    def new_init(self, **data):
        for key, value in data.items():
            if isinstance(value, ObjectId):
                data[key] = str(value)
        original_init(self, **data)

    cls.__init__ = new_init
    return cls
