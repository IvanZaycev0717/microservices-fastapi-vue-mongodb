from bson import ObjectId


def convert_objectid_to_str(cls):
    original_init = cls.__init__

    def new_init(self, **data):
        for key, value in data.items():
            if isinstance(value, ObjectId):
                data[key] = str(value)
        original_init(self, **data)

    cls.__init__ = new_init
    return cls
