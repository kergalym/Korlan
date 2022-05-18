from panda3d.core import BitMask32


class NpcPhysics:

    def __init__(self):
        self.base = base
        self.render = render

    def actor_hitbox_trace_task(self, actor, actor_bs, request, task):
        if self.base.game_instance['menu_mode']:
            return task.done

        if actor and actor_bs and actor.find("**/**Hips:HB") and request:
            parent_node = actor.find("**/**Hips:HB").node()
            parent_np = actor.find("**/**Hips:HB")

            for node in parent_node.get_overlapping_nodes():
                damage_weapons = actor.get_python_tag("damage_weapons")
                for weapon in damage_weapons:
                    # Exclude our own weapon hits
                    if (weapon in node.get_name()
                            and actor.get_name() not in node.get_name()):
                        hitbox_np = render.find("**/{0}".format(node.get_name()))
                        if hitbox_np:
                            # Deactivate enemy weapon if we got hit
                            if str(hitbox_np.get_collide_mask()) != " 0000 0000 0000 0000 0000 0000 0000 0000\n":
                                distance = round(hitbox_np.get_distance(parent_np), 1)
                                if distance >= 0.5 and distance <= 1.8:
                                    hitbox_np.set_collide_mask(BitMask32.allOff())
                                    if actor.get_python_tag("health_np"):
                                        # NPC gets damage if he has health point
                                        if actor.get_python_tag("health_np")['value'] > 1:
                                            request.request("Attacked", actor, "HitToBody", "play")
                                            actor.get_python_tag("health_np")['value'] -= 50

            # NPC dies if he has no health point
            if actor.get_python_tag("health_np")['value'] == 0:
                if actor.get_python_tag("generic_states")['is_alive']:
                    if actor.get_python_tag("generic_states")['is_idle']:
                        request.request("Death", actor, "Dying", "play")

        return task.cont
