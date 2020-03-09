

class Inventory:
    def __init__(self):
        self.item = None
        self.items = []

    def get_item(self, item):
        if item:
            self.item = item
            return item

    def set_item(self):
        if self.item:
            if hasattr(self.item, 'get_name'):
                return [self.item.get_name]

    def inv_space(self):
        self.items.append(self.set_item())
        return self.items
