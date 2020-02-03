class PlayerState:

    def __init__(self):
        base.player_state_unarmed = False
        base.player_state_armed = False
        base.player_state_magic = False
        base.item_player_access_codes = {'NOT_USABLE': 0,
                                         'USABLE': 1,
                                         'DEFORMED': 2
                                         }

    def set_player_state(self, task):
        base.player_state_unarmed = True
        if base.player_state_armed:
            base.player_state_unarmed = False
            base.player_state_magic = False
        elif base.player_state_magic:
            base.player_state_unarmed = False
            base.player_state_armed = False
        elif base.player_state_unarmed:
            base.player_state_armed = False
            base.player_state_magic = False
        return task.cont

    def actor_life(self, task):
        self.has_actor_life()
        return task.cont

    def has_actor_life(self):
        if (base.actor_is_dead is False
                and base.actor_is_alive is False):
            base.actor_life_perc = 100
            base.actor_is_alive = True
        else:
            return False

    def has_actor_any_item(self):
        children = base.asset_node_children_collector(
            base.asset_nodes_collector(),
            assoc_key=True
        )
        if children and isinstance(children, dict):
            for child in children:
                for joint in base.korlan_joints:
                    if child == joint.getName():
                        return True
                    else:
                        return False

    def pick_up_item(self, player, anyjoint, item):
        if (player
                and isinstance(anyjoint, list)
                and item):
            for hand in anyjoint:
                # TODO: check if any hand is free
                exposed_joint = player.exposeJoint(None, "modelRoot", hand)
                if self.has_actor_any_item() is False:
                    item.reparentTo(exposed_joint)
                elif self.has_actor_any_item() is True:
                    item.detachNode()

    def pass_item(self, player, anyjoint, item):
        if (player
                and isinstance(anyjoint, str)
                and item):
            exposed_joint = player.exposeJoint(None, "modelRoot", anyjoint)
            item.reparentTo(exposed_joint)

    def drop_item(self, object, item):
        if object and item:
            item.reparentTo(object)
            item.setPos(object.getPos())
