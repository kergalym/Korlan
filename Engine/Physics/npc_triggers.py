from panda3d.bullet import BulletSphereShape, BulletGhostNode
from panda3d.core import BitMask32, Vec3


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

    def _clear_forces(self, actor_rb_np):
        # Keep NPC from being hardly pushed if it has stayed
        force_y_vec = actor_rb_np.node().get_total_force()[1]
        force_z_vec = actor_rb_np.node().get_total_force()[2]
        imp_z_vec = actor_rb_np.node().get_total_torque()[2]
        lin_vec_z = actor_rb_np.node().get_linear_velocity()[2]
        ang_vec_z = actor_rb_np.node().get_angular_velocity()[2]

        actor_rb_np.node().apply_central_force(Vec3(0, force_y_vec, force_z_vec))
        actor_rb_np.node().apply_central_impulse(Vec3(0, 0, imp_z_vec))
        actor_rb_np.node().apply_torque_impulse(Vec3(0, 0, imp_z_vec))
        actor_rb_np.node().set_linear_velocity(Vec3(0, 0, lin_vec_z))
        actor_rb_np.node().set_angular_velocity(Vec3(0, 0, ang_vec_z))

        # Disabling movement and rotation forces
        actor_rb_np.node().set_angular_factor(Vec3(0, 1, 0))  # disables rotation
        actor_rb_np.node().set_linear_factor(Vec3(1, 0, 1))  # disables rotation

        actor_rb_np.node().apply_torque(Vec3(0, 0, 0))
        actor_rb_np.node().clearForces()
        actor_rb_np.node().set_angular_damping(0)  # stop sliding vertically
        actor_rb_np.node().set_linear_damping(0)  # stop sliding horizontally
        actor_rb_np.node().set_linear_sleep_threshold(0)
        actor_rb_np.node().set_angular_sleep_threshold(0)
        actor_rb_np.node().set_deactivation_time(0.01)

        actor_rb_np.node().set_restitution(0.01)

    def _clear_forces_mounted_animal(self, actor_rb_np):
        # Keep Player from being hardly pushed if it has stayed
        ang_vec_z = actor_rb_np.node().get_angular_velocity()[2]
        imp_z_vec = actor_rb_np.node().get_total_torque()[2]
        actor_rb_np.node().apply_central_impulse(Vec3(0, 0, imp_z_vec))
        actor_rb_np.node().set_angular_velocity(Vec3(0, 0, ang_vec_z))

        # Disabling movement and rotation forces
        actor_rb_np.node().set_angular_factor(Vec3(0, 1, 0))  # disables rotation

        actor_rb_np.node().set_angular_damping(0.2)  # stop sliding vertically
        actor_rb_np.node().set_linear_damping(0.2)  # stop sliding horizontally

        actor_rb_np.node().set_restitution(0.001)
        # actor_rb_np.node().set_friction(0.010)

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
                player_rb_np = self.base.game_instance["player_np"]
                actor_rb_np = self.base.game_instance['actors_np']["{0}:BS".format(animal_actor.get_name())]

                # Fix me: Dirty hack for path finding issue
                # when actor's pitch changes for reasons unknown for me xD
                # Prevent pitch changing
                self.base.game_instance['actors_ref'][animal_actor.get_name()].set_p(0)
                self.base.game_instance['actors_ref'][animal_actor.get_name()].get_parent().set_p(0)
                # Prevent from falling while collided
                actor_rb_np.set_p(0)
                actor_rb_np.set_r(0)

                # Keep NPC from being hardly pushed if it has stayed
                if str(actor_rb_np.node().type) != "BulletCharacterControllerNode":
                    if animal_actor.get_python_tag("is_mounted"):
                        self._clear_forces_mounted_animal(actor_rb_np)
                    elif not animal_actor.get_python_tag("is_mounted"):
                        self._clear_forces(actor_rb_np)

                for node in trigger.get_overlapping_nodes():
                    # ignore trigger itself and ground both
                    if "Player" in node.get_name():
                        # if player close to horse
                        if self.base.game_instance['player_ref'] and player_rb_np:
                            if round(player_rb_np.get_distance(trigger_np)) <= 2 \
                                    and round(player_rb_np.get_distance(trigger_np)) >= 1:

                                if "Korlan" in animal_actor.get_name():
                                    if (not animal_actor.get_python_tag("is_mounted")
                                            and not player.get_python_tag("is_on_horse")):
                                        # keep horse name if detected actor is the player
                                        # and player is not on horse and horse is free
                                        animal_actor.set_python_tag("is_ready_to_be_used", True)
                                        base.player_states["horse_is_ready_to_be_used"] = True
                                        base.game_instance['player_using_horse'] = animal_actor.get_name()

                                        # Hide Horse HUD if player is mounted
                                        if animal_actor.get_python_tag("npc_hud_np"):
                                            if (not self.base.game_instance['ui_mode']
                                                    and self.base.player_states["is_mounted"]):
                                                animal_actor.get_python_tag("npc_hud_np").hide()

                            elif (round(player_rb_np.get_distance(trigger_np)) >= 2
                                  and round(player_rb_np.get_distance(trigger_np)) <= 5):

                                if "Korlan" in animal_actor.get_name():
                                    if (not animal_actor.get_python_tag("is_mounted")
                                            and not player.get_python_tag("is_on_horse")):
                                        if animal_actor.get_python_tag("is_ready_to_be_used"):
                                            name = base.game_instance['player_using_horse']
                                            if render.find("**/{0}".format(name)):
                                                animal_actor_ = render.find("**/{0}".format(name))
                                                animal_actor_.set_python_tag("is_ready_to_be_used", False)
                                                base.player_states["horse_is_ready_to_be_used"] = False

                # Hide Horse HUD while Inventory or menu is opening
                if self.base.game_instance['ui_mode']:
                    if (animal_actor.get_python_tag("npc_hud_np")
                            and not animal_actor.get_python_tag("npc_hud_np").is_hidden()):
                        animal_actor.get_python_tag("npc_hud_np").hide()

        return task.cont

    def actor_area_trigger_task(self, actor, task):
        if self.base.game_instance['menu_mode']:
            if actor and actor.get_python_tag("npc_hud_np"):
                actor.get_python_tag("npc_hud_np").hide()
                actor.get_python_tag("npc_hud_np").destroy()
                actor.get_python_tag("npc_hud_np").remove_node()
            return task.done

        if actor:
            actor_rb_np = self.base.game_instance['actors_np']["{0}:BS".format(actor.get_name())]
            # Fix me: Dirty hack for path finding issue
            # when actor's pitch changes for reasons unknown for me xD
            # Prevent pitch changing
            self.base.game_instance['actors_ref'][actor.get_name()].set_p(0)
            self.base.game_instance['actors_ref'][actor.get_name()].get_parent().set_p(0)
            # Prevent from falling while collided
            actor_rb_np.set_p(0)
            actor_rb_np.set_r(0)

            # Prevent from move through walls
            if str(actor_rb_np.node().type) != "BulletCharacterControllerNode":
                actor_rb_np.node().setCcdMotionThreshold(1e-7)
                actor_rb_np.node().setCcdSweptSphereRadius(0.50)

                # Keep NPC from being hardly pushed if it has stayed
                self._clear_forces(actor_rb_np)

            # keep hide npc hud while inventory or menu is opening
            if self.base.game_instance['ui_mode']:
                if (actor.get_python_tag("npc_hud_np") is not None
                        and not actor.get_python_tag("npc_hud_np").is_hidden()):
                    actor.get_python_tag("npc_hud_np").hide()

        return task.cont

