

class Inventory:
    def __init__(self):
        self.item = None
        self.items = []

    def get_item(self, item):
        if item:
            self.item = item
            # Make inventory for 8 items
            if len(self.items) < 9:
                self.items.append(self.item)
                return self.items
