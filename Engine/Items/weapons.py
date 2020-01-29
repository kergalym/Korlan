

class Weapons:
    def __init__(self):
        self.assets = base.collect_assets()
        self.sword = {
            'type': 'weapon',
            'name': 'sword',
            'weight': 1.2,
            'in-use': False,
        }

        self.axe = {
            'type': 'weapon',
            'name': 'axe',
            'weight': 2.2,
            'in-use': False,
        }

        self.items = [
            self.sword,
            self.axe
        ]

    """ Get actor distance to item """
    def get_distance_to(self, actor, weapons):
        if actor and weapons:
            for item in weapons:
                item_pos = item.getPos()
                item_pos_y = item.getY()
                center_pos_y = 0.0
                print(
                    "item pos: ", item_pos, item_pos_y, "\n",
                    "center pos: ", center_pos_y, "\n",
                )
                # TODO: get model by node and do calculate the distance between actor and item

    """ Assign any item which is close to an actor enough """
    def selector(self, actor):
        # make pattern list from assets dict
        pattern = [key for key in self.assets]

        # use pattern to get all nodes corresponding to asset names
        nodes = [render.find("**/{0}".format(node)) for node in pattern]

        # pass nodes to get distance
        for node in nodes:
            self.get_distance_to(actor, node.getChildren())

    def take_sword(self):
        if self.sword['type'] == 'weapon':
            pass
            # TODO: Assign item to join below

    def take_axe(self):
        if self.axe['type'] == 'weapon':
            pass
            # TODO: Assign item to join below

    def take_naiza(self):
        # TODO: Put here joint controlling
        pass

    def take_bow(self):
        # TODO: Put here joint controlling
        pass
