class Items:

    def __init__(self):
        self.assets = base.collect_assets()
        self.dombra = {
            'type': 'item',
            'name': 'dombra',
            'weight': 0.5,
            'in-use': False,
        }

        self.piala = {
            'type': 'item',
            'name': 'piala',
            'weight': 0.1,
            'in-use': False,
        }

        self.items = [
            self.dombra,
            self.piala
        ]

    """ Get actor distance to item """

    def get_distance_to(self, actor, items):
        if actor and items:
            for item in items:
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

    def take_dombra(self):
        if self.dombra['type'] == 'item':
            pass
            # TODO: Assign item to join below
