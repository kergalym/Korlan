class Item:
    """ Implementation of inventory item data. You can change this class
    to suit your needs, but it must contain next elements:
    slot_id: integer ID of slot
    count: integer amount of the item
    get_icon: function should return string with image file name
    get_info: function should return hint string
    get_slots: function should return list or tuple of the slot types in
    which is possible to place this item
    get_max_count: function return max count of items one (this) type,
    which may be in one slot
    get_type: function should return arbitrary 'type' of the item. This
    'type' needed to try to merge amount of items of one type in the
    one slot.
    """

    def __init__(self, data):
        self.section_name = data[0][0]
        self.slot_id = -1
        self.count = data[4]
        self.data = data

    def get_icon(self):
        return self.data[2]

    def get_info(self):
        txt = ''
        if self.data[1] == 'armor':
            txt = '%s\nArmor: %i' % (self.data[3], self.data[6])
        elif self.data[1] == 'weapon':
            txt = '%s\nDamage: %i' % (self.data[3], self.data[7])
        else:
            txt = self.data[3]
        return txt

    def get_slots(self):
        return self.data[0]

    def get_max_count(self):
        return self.data[5]

    def get_type(self):
        return self.data[1]

    def get_name(self):
        return self.data[3]
