from panda3d.core import BitMask32


class PlayerPhysics:

    def __init__(self):
        self.base = base
        self.render = render

    def player_hitbox_trace_task(self, actor, request, task):
        if self.base.game_instance['menu_mode']:
            return task.done

        if actor and actor.find("**/**Hips:HB") and request:
            parent_node = actor.find("**/**Hips:HB").node()
            parent_np = actor.find("**/**Hips:HB")
            actor_ref = self.base.game_instance['player_ref']

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
                                    if self.base.game_instance['hud_np']:
                                        # Player gets damage if he has health point
                                        if self.base.game_instance['hud_np'].player_bar_ui_health['value'] > 1:
                                            if (not base.player_states['is_busy']
                                                    and not base.player_states['is_using']):
                                                request.request("Attacked", actor_ref, "HitToBody", "play")
                                                self.base.game_instance['hud_np'].player_bar_ui_health['value'] -= 5
                                                if actor.get_python_tag("health") > 1:
                                                    health = actor.get_python_tag("health")
                                                    health -= 5
                                                    actor.set_python_tag("health", health)

            # Player dies if he has no health point
            if actor.get_python_tag("health") == 0:
                if base.player_states['is_alive']:
                    if base.player_states['is_idle']:
                        request.request("Death", actor_ref, "Dying", "play")
                    
        return task.cont
