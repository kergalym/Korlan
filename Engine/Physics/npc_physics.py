from panda3d.core import BitMask32, Vec3, Vec2


class NpcPhysics:

    def __init__(self):
        self.base = base
        self.render = render

    def face_actor_to(self, actor, target_np):
        if actor and target_np:
            # Calculate NPC rotation vector
            rot_vector = Vec3(actor.get_pos() - target_np.get_pos())
            rot_vector_2d = rot_vector.get_xy()
            rot_vector_2d.normalize()
            heading = Vec3(Vec2(0, 1).signed_angle_deg(rot_vector_2d), 0).x
            actor.set_h(heading)

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
                            self.face_actor_to(actor_bs, npc_bs)

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

    def _find_any_weapon(self, actor, enemy):
        damage_weapons = actor.get_python_tag("damage_weapons")
        enemy_hitboxes = enemy.get_python_tag("actor_hitboxes")
        if enemy_hitboxes:
            for hand in enemy_hitboxes:
                hand_hb = enemy_hitboxes.get(hand)
                if hand_hb:
                    for weapon in damage_weapons:
                        hitbox_np = enemy.find("**/{0}".format(weapon))
                        if hitbox_np:
                            if hand in hitbox_np.get_parent().get_name():
                                return hitbox_np

    def _do_death(self, actor, request, task):
        if (actor.get_python_tag("health_np")['value'] < 2
                or actor.get_python_tag("health_np")['value'] < 1):
            if actor.get_python_tag("stamina_np")['value'] > 1:
                actor.get_python_tag("stamina_np")['value'] = 0

            if actor.get_python_tag("generic_states")['is_alive']:
                if actor.get_python_tag("generic_states")['is_idle']:
                    request.request("Death", actor, "Dying", "play")

        if not actor.get_python_tag("generic_states")['is_alive']:
            return task.done

    def actor_hitbox_trace_task(self, actor, actor_bs, hips, request, task):
        if self.base.game_instance['menu_mode']:
            return task.done

        name = actor.get_name()
        parent_node = hips.node()
        parent_np = hips
        node_np = None
        enemy_is_alive = False

        for node in parent_node.get_overlapping_nodes():
            # Accept only NPC or Player
            if "BS" not in node.get_name():
                continue

            if name in node.get_name():
                continue

            if "Crouch" in node.get_name():
                continue

            # Get enemy and its health and weapon state (equipped or not)
            for actor_name in self.base.game_instance["actors_ref"]:
                if node.get_name() == actor_name:
                    node_np = self.base.game_instance["actors_ref"][actor_name]
                    enemy_is_alive = node_np.get_python_tag("generic_states")['is_alive']
                else:
                    node_np = self.base.game_instance["player_ref"]
                    enemy_is_alive = base.player_states['is_alive']

            if enemy_is_alive:
                # Find active hitbox in the enemy actor node before doing damage
                hitbox_np = self._find_any_weapon(actor=actor, enemy=node_np)
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
        self._do_any_damage(actor, actor_bs, "Arrow_BRB", request)

        # NPC dies if it has no health
        self._do_death(actor, request, task)

        if not actor.get_python_tag("generic_states")['is_alive']:
            return task.done

        return task.cont
