from panda3d.core import BitMask32


class PlayerDamages:

    def __init__(self):
        self.base = base
        self.render = render
        self.player_hips = {}

    def _do_damage(self, actor, hitbox_np, parent_np, request):
        # Deactivate enemy weapon if we got hit
        if str(hitbox_np.get_collide_mask()) != " 0000 0000 0000 0000 0000 0000 0000 0000\n":
            distance = round(hitbox_np.get_distance(parent_np), 1)
            if distance >= 0.5 and distance <= 1.8:
                hitbox_np.set_collide_mask(BitMask32.allOff())
                if self.base.game_instance['hud_np']:
                    # Player gets damage if he has health point
                    if self.base.game_instance['hud_np'].player_bar_ui_health['value'] > 1:

                        # Play damage if Player doesn't move
                        if not base.player_states['is_moving']:
                            request.request("Attacked", actor, "play")

                        self.base.game_instance['hud_np'].player_bar_ui_health['value'] -= 5
                        if actor.get_python_tag("health") > 1:
                            health = actor.get_python_tag("health")
                            health -= 5
                            actor.set_python_tag("health", health)

    def _do_any_damage(self, actor, actor_rb_np, pattern, request):
        colliders = render.find_all_matches("**/{0}*".format(pattern))
        if colliders:
            for collider in colliders:
                # Skip actor owned object
                if actor.get_name() not in collider.get_name():
                    if "render" in collider.get_parent().get_name():
                        distance = round(actor_rb_np.get_distance(collider), 1)
                        if distance >= 0.1 and distance <= 0.3:
                            if self.base.game_instance['hud_np']:
                                # Player gets damage if he has health point
                                if self.base.game_instance['hud_np'].player_bar_ui_health['value'] > 1:

                                    # Play damage if Player doesn't move
                                    if not base.player_states['is_moving']:
                                        request.request("Attacked", actor, "play")

                                    self.base.game_instance['hud_np'].player_bar_ui_health['value'] -= 5
                                    if actor.get_python_tag("health") > 1:
                                        health = actor.get_python_tag("health")
                                        health -= 5
                                        actor.set_python_tag("health", health)

    def _find_any_weapon(self, enemy):
        if enemy.get_python_tag("current_hitbox") is not None:
            hitbox_np = enemy.get_python_tag("current_hitbox")
            if hitbox_np:
                return hitbox_np

    def _do_death(self, actor, request):
        if actor.get_python_tag("health") == 0:
            actor.set_python_tag("first_attack", False)
            if base.player_states['is_alive']:
                if base.player_states['is_idle']:
                    request.request("Death", actor, "Dying", "play")

    def player_hitbox_trace_task(self, actor, actor_rb_np, request, task):
        if self.base.game_instance['menu_mode']:
            return task.done

        name = actor.get_name()
        parent_node = self.player_hips[name].node()
        parent_np = self.player_hips[name]

        for node in parent_node.get_overlapping_nodes():
            # Accept only NPC
            if "BS" not in node.get_name():
                continue

            if "Crouch" in node.get_name():
                continue

            if name in node.get_name():
                continue

            # Get enemy based on its health and weapon state (equipped or not)
            if node is not None and node.get_name().endswith(":BS"):
                node_name = node.get_name().split(":")[0]
                if self.base.game_instance["actors_ref"].get(node_name) is not None:
                    enemy_ref = self.base.game_instance["actors_ref"][node_name]
                    if enemy_ref is not None:
                        if enemy_ref.get_python_tag("generic_states")['is_alive']:
                            # Find active hitbox in the enemy actor node before doing damage
                            hitbox_np = self._find_any_weapon(enemy=enemy_ref)
                            if hitbox_np:
                                self._do_damage(actor, hitbox_np, parent_np, request)
                            else:
                                hitboxes = enemy_ref.get_python_tag("actor_hitboxes")
                                if hitboxes:
                                    for hitbox in hitboxes:
                                        if hitboxes.get(hitbox):
                                            hitbox_np = hitboxes[hitbox]
                                            self._do_damage(actor, hitbox_np, parent_np, request)

        # Arrow Damage
        if base.player_states["has_bow"]:
            self._do_any_damage(actor, actor_rb_np, "Arrow_BRB", request)

        # Player dies if he has no health point
        self._do_death(actor, request)

        if not base.player_states['is_alive']:
            return task.done

        return task.cont
