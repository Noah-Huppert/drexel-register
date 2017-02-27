class EnumHelpers(object):
    """Create instance of enum from str
    Relies on Enum emplenting __str__ method to match input

    Args:
        value (str): String to get name of enum instance from

    Raises:
        ValueError: If value is None or len(value) <= 0
        ValueError: If value is not a valid enum instance name

    Returns:
        Correct Enum value represented in string given
    """
    @classmethod
    def from_str(cls, value):
        if (value is None) or (type(value) is not str):
            raise ValueError("value must not be None and must be a str, was: {}".format(value))

        for enum in cls:
            if str(enum) == value:
                return enum

        raise ValueError("Enum {} has no value which matches value provided: {}".format(str(cls), value))

    """Default __str__ method which just returns enum name
    """
    def __str__(self):
        return self.name