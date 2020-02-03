from Engine.Actors.Player.state import PlayerState


class Items:

    def __init__(self):
        self.assets = base.collect_assets()
        self.state = PlayerState()
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
            self.dombra,
            self.piala,
            self.sword,
            self.axe
        ]

    """ Assign any item which is close to an actor enough """

    def item_selector(self, actor, anyjoint):
        if (actor and anyjoint
                and isinstance(anyjoint, list)):
            if (base.collide_item_name['name'] is not None
                    and isinstance(base.collide_item_name['name'], str)
                    and base.collide_item_name['type'] == 0):
                item = base.collide_item_name['name']
                self.state.pick_up_item(actor, anyjoint, item)

    def pick_up_dombra(self):
        if self.dombra['type'] == 'item':
            pass
            # TODO: Assign item to join below

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
