class Helpers(object):
    """
    Helpers for SQLAlchemy models
    """

    """Helper which copies keys from item to course if the key exists in item
    For each `key` in keys set course[key] to item[key] if item[key] exists

    Attributes:
        item (drexel_register.items.Course: Item to get values from
        keys (str[]): Array of keys to attempt to set
    """
    def _set_if_present(self, item, keys):
        for key in keys:
            if key in item:
                self[key] = item[key]

