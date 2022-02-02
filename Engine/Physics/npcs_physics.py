from panda3d.bullet import BulletSphereShape, BulletGhostNode
from panda3d.core import BitMask32


class NpcsPhysics:

    def __init__(self):
        self.base = base
        self.render = render

    def collision_info(self, player, item):
        if player and item and self.base.game_instance['physics_world_np']:

            query_all = self.base.game_instance['physics_world_np'].ray_test_all(player.get_pos(),
                                                                                 item.get_pos())

            collision_info = {"hits": query_all.has_hits(),
                              "fraction": query_all.get_closest_hit_fraction(),
                              "num_hits": query_all.get_num_hits()}

            for query in query_all.get_hits():
                collision_info["hit_pos"] = query.get_hit_pos()
                collision_info["hit_normal"] = query.get_hit_normal()
                collision_info["hit_fraction"] = query.get_hit_fraction()
                collision_info["node"] = query.get_node()

            return collision_info

    def set_ghost_trigger(self, actor, world):
        if actor:
            radius = 1.75 - 2 * 0.3
            sphere = BulletSphereShape(radius)
            trigger_bg = BulletGhostNode('{0}_trigger'.format(actor.get_name()))
            trigger_bg.add_shape(sphere)
            trigger_np = self.render.attach_new_node(trigger_bg)
            trigger_np.set_collide_mask(BitMask32(0x0f))
            world.attach_ghost(trigger_bg)
            trigger_np.reparent_to(actor)
            trigger_np.set_pos(0, 0, 1)

    def mountable_animal_area_trigger_task(self, animal_actor, task):
        if self.base.game_instance['menu_mode']:
            if animal_actor and animal_actor.get_python_tag("npc_hud_np"):
                animal_actor.get_python_tag("npc_hud_np").hide()
                animal_actor.get_python_tag("npc_hud_np").destroy()
                animal_actor.get_python_tag("npc_hud_np").remove_node()
            return task.done

        if animal_actor:
            if animal_actor.find("**/{0}_trigger".format(animal_actor.get_name())):
                trigger = animal_actor.find("**/{0}_trigger".format(animal_actor.get_name())).node()
                trigger_np = animal_actor.find("**/{0}_trigger".format(animal_actor.get_name()))
                player = self.base.game_instance['player_ref']
                player_bs = self.base.get_actor_bullet_shape_node(asset="Player", type="Player")
                actor_bs_np = self.base.game_instance['actors_np']["{0}:BS".format(animal_actor.get_name())]

                for node in trigger.get_overlapping_nodes():
                    # ignore trigger itself and ground both
                    if "NPC" in node.get_name() or "Player" in node.get_name():
                        # if player close to horse
                        if self.base.game_instance['player_ref'] and player_bs:
                            if player_bs.get_distance(trigger_np) <= 2 \
                                    and player_bs.get_distance(trigger_np) >= 1:
                                if (not animal_actor.get_python_tag("is_mounted")
                                        and not player.get_python_tag("is_on_horse")
                                        and node.get_name() == player_bs.get_name()):
                                    # keep horse name if detected actor is the player
                                    # and player is not on horse and horse is free
                                    animal_actor.set_python_tag("is_ready_to_be_used", True)
                                    if hasattr(base, "player_states"):
                                        base.player_states["horse_is_ready_to_be_used"] = True
                                        base.game_instance['player_using_horse'] = animal_actor.get_name()
                                elif (not animal_actor.get_python_tag("is_mounted")
                                      and not player.get_python_tag("is_on_horse")
                                      and node.get_name() != player_bs.get_name()):
                                    # clear horse name if player is on horse, horse is not free
                                    # and detected actor is not player
                                    animal_actor.set_python_tag("is_ready_to_be_used", False)
                                    if hasattr(base, "player_states"):
                                        base.player_states["horse_is_ready_to_be_used"] = False

                                if animal_actor.get_python_tag("npc_hud_np"):
                                    animal_actor.get_python_tag("npc_hud_np").show()

                            elif (player_bs.get_distance(trigger_np) >= 2
                                  and player_bs.get_distance(trigger_np) <= 5):
                                if animal_actor.get_python_tag("npc_hud_np"):
                                    animal_actor.get_python_tag("npc_hud_np").hide()

                # keep actor_bs_np height while kinematic is active
                # because in kinematic it has no gravity impact and gets unwanted drop down
                if actor_bs_np and actor_bs_np.node().is_kinematic:
                    actor_bs_np.set_z(0.96)

        return task.cont

    def actor_area_trigger_task(self, actor, task):
        if self.base.game_instance['menu_mode']:
            if actor and actor.get_python_tag("npc_hud_np"):
                actor.get_python_tag("npc_hud_np").hide()
                actor.get_python_tag("npc_hud_np").destroy()
                actor.get_python_tag("npc_hud_np").remove_node()
            return task.done

        if actor:
            if actor.find("**/{0}_trigger".format(actor.get_name())):
                trigger = actor.find("**/{0}_trigger".format(actor.get_name())).node()
                trigger_np = actor.find("**/{0}_trigger".format(actor.get_name()))
                player_bs = self.base.get_actor_bullet_shape_node(asset="Player", type="Player")
                actor_bs_np = self.base.game_instance['actors_np']["{0}:BS".format(actor.get_name())]

                for node in trigger.get_overlapping_nodes():
                    # ignore trigger itself and ground both
                    if "NPC" in node.get_name() or "Player" in node.get_name():
                        # if player close to horse
                        if self.base.game_instance['player_ref']:
                            if player_bs.get_distance(trigger_np) <= 2 \
                                    and player_bs.get_distance(trigger_np) >= 1:
                                if actor.get_python_tag("npc_hud_np"):
                                    actor.get_python_tag("npc_hud_np").show()
                            elif (player_bs.get_distance(trigger_np) >= 2
                                  and player_bs.get_distance(trigger_np) <= 5):
                                if actor.get_python_tag("npc_hud_np"):
                                    actor.get_python_tag("npc_hud_np").hide()

                # keep actor_bs_np height while kinematic is active
                # because in kinematic it has no gravity impact and gets unwanted drop down
                if actor_bs_np and actor_bs_np.node().is_kinematic:
                    actor_bs_np.set_z(0.96)

        return task.cont

    def player_hitbox_trace_task(self, actor, task):
        if self.base.game_instance['menu_mode']:
            return task.done

        if actor and actor.find("**/**Hips:HB"):
            parent_node = actor.find("**/**Hips:HB").node()
            for node in parent_node.get_overlapping_nodes():
                damage_weapons = actor.get_python_tag("damage_weapons")
                for weapon in damage_weapons:
                    if weapon in node.get_name():
                        node.set_into_collide_mask(BitMask32.allOff())
                        base.player_states['is_attacked'] = True
                        if self.base.game_instance['hud_np']:
                            if self.base.game_instance['hud_np'].player_bar_ui_health['value'] > 0:
                                self.base.game_instance['hud_np'].player_bar_ui_health['value'] -= 1
                                health = actor.get_python_tag("health")
                                health -= 1
                                actor.set_python_tag("health", health)
                            else:
                                base.player_states['is_alive'] = False
        return task.cont

    def actor_hitbox_trace_task(self, actor, task):
        if self.base.game_instance['menu_mode']:
            return task.done

        if actor and actor.find("**/**Hips:HB"):
            parent_node = actor.find("**/**Hips:HB").node()
            for node in parent_node.get_overlapping_nodes():
                damage_weapons = actor.get_python_tag("damage_weapons")
                for weapon in damage_weapons:
                    if weapon in node.get_name():
                        node.set_into_collide_mask(BitMask32.allOff())
                        actor.get_python_tag("generic_states")['is_attacked'] = True
                        if actor.get_python_tag("health_np"):
                            if actor.get_python_tag("health_np")['value'] > 0:
                                actor.get_python_tag("health_np")['value'] -= 1
                            else:
                                actor.get_python_tag("generic_states")['is_alive'] = False
        return task.cont
