class Slot:
    """ Inventory slot
    """

    def __init__(self, data):
        type, pos, info, ico = data
        self.pos = pos
        self.type = type
        self.info = info
        self.ico = ico

    def get_icon(self):
        return self.ico

    def get_info(self):
        return self.info
