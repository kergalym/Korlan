from Engine.Actors.Player.state import PlayerState


class Items:

    def __init__(self):
        self.base = base
        self.assets = base.assets_collector()
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

            if assets_children:

                for key in assets_children:
                    # Get bullet shape node path if it's here
                    bs_np = self.base.get_static_bullet_shape_node(asset=key)
                    if bs_np:
                        items[key] = (bs_np.get_pos())
                if items:
                    return items

    def get_item_distance_task(self, player, task):
        if player and base.game_mode and base.menu_mode is False:
            items_dist_vect = base.distance_calculate(
                self.usable_item_pos_collector(player), player)
            if items_dist_vect:
                items_dist_vect_y = [items_dist_vect[k][1] for k in items_dist_vect]
                items_dist_vect_y.sort()

                for name, y_pos in zip(items_dist_vect, items_dist_vect_y):
                    if (y_pos > 0.0 and y_pos < 0.7
                            and base.is_item_in_use is False):
                        base.is_item_close_to_use = True
                        base.is_item_far_to_use = False
                        base.close_item_name = name
                        base.in_use_item_name = None
                    elif (y_pos > 0.0 and y_pos < 0.7
                          and base.is_item_in_use):
                        base.close_item_name = name
                        base.is_item_close_to_use = False
                        base.is_item_far_to_use = False

        if base.game_mode is False and base.menu_mode:
            base.is_item_close_to_use = False
            base.is_item_far_to_use = False
            base.is_item_in_use = False
            base.is_item_in_use_long = False
            base.in_use_item_name = None
            return task.done

        return task.cont

    def item_selector(self, actor, joint):
        if (actor and joint
                and isinstance(joint, str)):
            item_vect_dict = base.distance_calculate(
                self.usable_item_pos_collector(actor), actor)
            self.state.take_item(actor, joint, item_vect_dict)

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
