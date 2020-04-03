import re


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

    def get_item_thumbs(self, images):
        if images and isinstance(images, dict):
            thumbs = {}
            # Make thumb names same as item names
            for image in images:
                if isinstance(image, str):
                    thumb = re.sub('_thumbs', '', image.lower())
                    thumb = thumb.capitalize()
                    thumbs["{0}:BS".format(thumb)] = images[image]
            return thumbs
