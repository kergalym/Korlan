from panda3d.bullet import BulletSphereShape, BulletGhostNode
from panda3d.core import BitMask32


class NpcTriggers:

    def __init__(self):
        self.base = base
        self.render = render

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

                # Fix me: Dirty hack for path finding issue
                # when actor's pitch changes for reasons unknown for me xD
                # Prevent pitch changing
                self.base.game_instance['actors_ref'][animal_actor.get_name()].set_p(0)
                self.base.game_instance['actors_ref'][animal_actor.get_name()].get_parent().set_p(0)
                # Prevent from falling while collided
                actor_bs_np.set_p(0)
                actor_bs_np.set_r(0)

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
                                    if not self.base.game_instance['ui_mode']:
                                        animal_actor.get_python_tag("npc_hud_np").show()

                            elif (player_bs.get_distance(trigger_np) >= 2
                                  and player_bs.get_distance(trigger_np) <= 5):
                                if animal_actor.get_python_tag("npc_hud_np"):
                                    animal_actor.get_python_tag("npc_hud_np").hide()
                                animal_actor.set_python_tag("is_ready_to_be_used", False)
                                if hasattr(base, "player_states"):
                                    base.player_states["horse_is_ready_to_be_used"] = False

                # keep hide npc hud while inventory or menu is opening
                if self.base.game_instance['ui_mode']:
                    animal_actor.get_python_tag("npc_hud_np").hide()

                # keep actor_bs_np height while kinematic is active
                # because in kinematic it has no gravity impact and gets unwanted drop down
                if (actor_bs_np and hasattr(actor_bs_np.node(), 'is_kinematic')
                        and actor_bs_np.node().is_kinematic):
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

                # Fix me: Dirty hack for path finding issue
                # when actor's pitch changes for reasons unknown for me xD
                # Prevent pitch changing
                self.base.game_instance['actors_ref'][actor.get_name()].set_p(0)
                self.base.game_instance['actors_ref'][actor.get_name()].get_parent().set_p(0)
                # Prevent from falling while collided
                actor_bs_np.set_p(0)
                actor_bs_np.set_r(0)

                for node in trigger.get_overlapping_nodes():
                    # ignore trigger itself and ground both
                    if "NPC" in node.get_name() or "Player" in node.get_name():
                        # if player close to horse
                        if player_bs and self.base.game_instance['player_ref']:
                            if player_bs.get_distance(trigger_np) <= 2 \
                                    and player_bs.get_distance(trigger_np) >= 1:
                                if actor.get_python_tag("npc_hud_np"):
                                    if not self.base.game_instance['ui_mode']:
                                        actor.get_python_tag("npc_hud_np").show()
                            elif (player_bs.get_distance(trigger_np) >= 2
                                  and player_bs.get_distance(trigger_np) <= 5):
                                if actor.get_python_tag("npc_hud_np"):
                                    actor.get_python_tag("npc_hud_np").hide()

                # keep hide npc hud while inventory or menu is opening
                if self.base.game_instance['ui_mode']:
                    actor.get_python_tag("npc_hud_np").hide()

                # keep actor_bs_np height while kinematic is active
                # because in kinematic it has no gravity impact and gets unwanted drop down
                if (actor_bs_np and hasattr(actor_bs_np.node(), 'is_kinematic')
                        and actor_bs_np.node().is_kinematic):
                    actor_bs_np.set_z(0.96)

        return task.cont

