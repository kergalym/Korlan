from Engine.Actors.Player.state import PlayerState
from Engine.Collisions.collisions import Collisions


class Items:

    def __init__(self):
        self.base = base
        self.assets = base.collect_assets()
        self.state = PlayerState()
        self.col = Collisions()

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

    def usable_item_pos_collector(self, player):
        if player:
            # parse player name to exclude them
            assets = base.asset_nodes_collector()
            t = []
            items = {}

            for asset in assets:
                # We exclude any actor from assets,
                # we need to retrieve the distance
                if (asset.get_name() != player.get_name()
                        and asset.get_name() != "NPC"
                        and asset.get_name() != "Sky"
                        and asset.get_name() != "Mountains"
                        and asset.get_name() != "Ground"
                        and asset.get_name() != "Grass"):
                    t.append(asset)

            assets_children = base.asset_node_children_collector(
                t, assoc_key=True)

            for key in assets_children:
                parent_node = assets_children[key].get_parent().get_parent()
                items[key] = (parent_node.get_pos())

            return items

    def item_selector(self, actor, joint):
        if (actor and joint
                and isinstance(joint, str)):
            item_vect_dict = base.distance_calculate(
                self.usable_item_pos_collector(actor), actor)
            self.state.pick_up_item(actor, joint, item_vect_dict)

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
