from panda3d.core import BitMask32, Vec3, Vec2


class NpcDamages:

    def __init__(self):
        self.base = base
        self.render = render
        self.npc_controller = self.base.game_instance["npc_controller_cls"]

    def _do_damage(self, actor, actor_bs, node, hitbox_np, parent_np, request):
        if actor.get_python_tag("enemy_hitbox_distance") != 0:
            actor.set_python_tag("enemy_hitbox_distance", 0)
        # Deactivate enemy weapon if we got hit
        if str(hitbox_np.get_collide_mask()) != " 0000 0000 0000 0000 0000 0000 0000 0000\n":
            distance = round(hitbox_np.get_distance(parent_np), 1)
            actor.set_python_tag("enemy_hitbox_distance", distance)

            if distance >= 0.5 and distance <= 1.8:
                # Enemy Prediction for facing
                if node:
                    name = node.get_name()
                    name_bs = "{0}:BS".format(name)
                    if name in actor.get_name():
                        npc_ref = self.base.game_instance["actors_np"][name]
                        npc_bs = self.base.game_instance["actors_np"][name_bs]
                        if npc_ref:
                            if not actor.get_python_tag("enemy_npc_ref"):
                                actor.set_python_tag("enemy_npc_ref", npc_ref)
                            if not actor.get_python_tag("enemy_npc_bs"):
                                actor.set_python_tag("enemy_npc_bs", npc_bs)
                            self.npc_controller.face_actor_to(actor_bs, npc_bs)

                hitbox_np.set_collide_mask(BitMask32.allOff())
                if (actor.get_python_tag("health_np")
                        and not actor.get_python_tag("generic_states")['is_blocking']):
                    # NPC gets damage if he has health point
                    if actor.get_python_tag("health_np")['value'] > 1:
                        request.request("Attacked", actor, "HitToBody", "play")
                        actor.get_python_tag("health_np")['value'] -= 6

                    if actor.get_python_tag("stamina_np")['value'] > 1:
                        actor.get_python_tag("stamina_np")['value'] -= 3

                    if actor.get_python_tag("courage_np")['value'] > 1:
                        actor.get_python_tag("courage_np")['value'] -= 3

    def _do_any_damage(self, actor, actor_bs, pattern, request):
        colliders = render.find_all_matches("**/{0}*".format(pattern))
        if colliders:
            for collider in colliders:
                # Skip actor owned object
                if actor.get_name() not in collider.get_name():
                    if "render" in collider.get_parent().get_name():
                        distance = round(actor_bs.get_distance(collider), 1)
                        if distance >= 0.1 and distance <= 0.3:
                            if (actor.get_python_tag("health_np")
                                    and not actor.get_python_tag("generic_states")['is_blocking']):
                                # NPC gets damage if he has health point
                                if actor.get_python_tag("health_np")['value'] > 1:
                                    request.request("Attacked", actor, "HitToBody", "play")
                                    actor.get_python_tag("health_np")['value'] -= 6

                                if actor.get_python_tag("stamina_np")['value'] > 1:
                                    actor.get_python_tag("stamina_np")['value'] -= 3

                                if actor.get_python_tag("courage_np")['value'] > 1:
                                    actor.get_python_tag("courage_np")['value'] -= 3

    def _find_any_weapon(self, enemy):
        if enemy.get_python_tag("current_hitbox") is not None:
            hitbox_np = enemy.get_python_tag("current_hitbox")
            if hitbox_np:
                return hitbox_np

    def _do_death(self, actor, request):
        if (actor.get_python_tag("health_np")['value'] < 2
                or actor.get_python_tag("health_np")['value'] < 1):
            if actor.get_python_tag("stamina_np")['value'] > 1:
                actor.get_python_tag("stamina_np")['value'] = 0

            if actor.get_python_tag("generic_states")['is_alive']:
                if actor.get_python_tag("generic_states")['is_idle']:
                    request.request("Death", actor, "Dying", "play")

    def actor_hitbox_trace_task(self, actor, actor_bs, hips, request, task):
        if self.base.game_instance['menu_mode']:
            return task.done

        name_bs = actor_bs.get_name()
        parent_node = hips.node()
        parent_np = hips
        node_np = None
        enemy_is_alive = False

        for node in parent_node.get_overlapping_nodes():
            # Accept only NPC or Player
            if "BS" not in node.get_name():
                continue

            if "Crouch" in node.get_name():
                continue

            if name_bs in node.get_name():
                continue

            # Get enemy based on its health and weapon state (equipped or not)
            if base.player_states['is_alive']:
                node_np = self.base.game_instance["player_ref"]
                enemy_is_alive = base.player_states['is_alive']
            else:
                if node is not None and node.get_name().endswith(":BS"):
                    node_name = node.get_name().split(":")[0]
                    if self.base.game_instance["actors_ref"].get(node_name) is not None:
                        node_np = self.base.game_instance["actors_ref"][node_name]
                        enemy_is_alive = node_np.get_python_tag("generic_states")['is_alive']

            if enemy_is_alive:
                # Find active hitbox in the enemy actor node before doing damage
                hitbox_np = self._find_any_weapon(enemy=node_np)
                if hitbox_np:
                    self._do_damage(actor, actor_bs, node, hitbox_np, parent_np, request)
                else:
                    hitboxes = node_np.get_python_tag("actor_hitboxes")
                    if hitboxes:
                        for hitbox in hitboxes:
                            if hitboxes.get(hitbox):
                                hitbox_np = hitboxes[hitbox]
                                self._do_damage(actor, actor_bs, node, hitbox_np, parent_np, request)

        # Arrow Damage
        if actor.get_python_tag("npc_type") == "npc":
            if actor.get_python_tag("human_states")["has_bow"]:
                self._do_any_damage(actor, actor_bs, "Arrow_BRB", request)
        else:
            self._do_any_damage(actor, actor_bs, "Arrow_BRB", request)

        # NPC dies if it has no health
        self._do_death(actor, request)

        if not actor.get_python_tag("generic_states")['is_alive']:
            return task.done

        return task.cont
