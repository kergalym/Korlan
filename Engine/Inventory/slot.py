class Slot:
    """ Inventory slot
    """

    def __init__(self, data):
        section = ''
        """ If we don't have section, data length become less 
        """
        if len(data) < 5:
            type, pos, info, ico = data
        else:
            section, type, pos, info, ico = data

        self.section_name = section
        self.pos = pos
        self.type = type
        self.info = info
        self.ico = ico
        self.data = data

    def get_icon(self):
        return self.ico

    def get_info(self):
        return self.info
