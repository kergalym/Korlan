from direct.task.TaskManagerGlobal import taskMgr
from panda3d.bullet import BulletSphereShape, BulletGhostNode
from panda3d.core import BitMask32, Point3, Vec3


class PlayerTrigger:

    def __init__(self):
        self.base = base
        self.render = render
        self._trig_radius = 1.75 - 2 * 0.3

    def set_ghost_trigger(self, actor, world):
        if actor and world:
            sphere = BulletSphereShape(self._trig_radius)
            trigger_bg = BulletGhostNode('player_cam_trigger')
            trigger_bg.add_shape(sphere)
            trigger_np = self.render.attach_new_node(trigger_bg)
            trigger_np.set_collide_mask(BitMask32(0x0f))
            world.attach_ghost(trigger_bg)
            trigger_np.reparent_to(actor)
            player_rb_np = self.base.game_instance["player_np"]
            taskMgr.add(self._npc_hud_switcher_task,
                        "npc_hud_switcher_task",
                        extraArgs=[trigger_np, player_rb_np],
                        appendTask=True)

            # Keep NPC from being hardly pushed if it has stayed
            if str(player_rb_np.node().type) != "BulletCharacterControllerNode":
                taskMgr.add(self._clear_forces, "clear_forces_player",
                            extraArgs=[player_rb_np],
                            appendTask=True)

    def _clear_forces(self, actor_rb_np, task):
        if self.base.game_instance['menu_mode']:
            return task.done

        # Keep NPC from being hardly pushed if it has stayed
        force_z_vec = actor_rb_np.node().get_total_force()[2]
        imp_z_vec = actor_rb_np.node().get_total_torque()[2]
        lin_vec_z = actor_rb_np.node().get_linear_velocity()[2]
        ang_vec_z = actor_rb_np.node().get_angular_velocity()[2]

        actor_rb_np.node().apply_central_force(Vec3(0, 0, force_z_vec))
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

        # Disable shape pitching and rotating
        actor_rb_np.set_p(0)
        actor_rb_np.set_r(0)

        return task.cont

    def _npc_hud_switcher_task(self, trigger_np, player_rb_np, task):
        if self.base.game_instance['menu_mode']:
            return task.done

        if (not self.base.game_instance["ui_mode"]
                and not self.base.game_instance["inv_mode"]
                and self.base.player_states["is_alive"]):

            trigger = trigger_np.node()
            if trigger:
                for node in trigger.get_overlapping_nodes():
                    if node and "NPC" in node.get_name():
                        node_np = self.base.game_instance["actors_np"].get(node.get_name())
                        # Toggling NPC HUD
                        self.toggle_npc_hud(player_rb_np, node_np)

        return task.cont

    def toggle_npc_hud(self, player_rb_np, node_np):
        if self.base.game_instance['loading_is_done'] == 1:
            if player_rb_np and not node_np:
                # Hide NPCs HUD if nothing is found
                for k in self.base.game_instance["actors_ref"]:
                    _actor = self.base.game_instance["actors_ref"][k]
                    if _actor.has_python_tag("npc_hud_np"):
                        if _actor.get_python_tag("npc_hud_np") is not None:
                            if not _actor.get_python_tag("npc_hud_np").is_hidden():
                                _actor.get_python_tag("npc_hud_np").hide()

            if player_rb_np and node_np:
                # If I have any bow weapon
                if base.player_states["has_bow"]:
                    # Show enemy HUD starting from 100 meters
                    if (player_rb_np.get_distance(node_np) > 1
                            and player_rb_np.get_distance(node_np) < 100):
                        for k in self.base.game_instance["actors_ref"]:
                            # Hide all other NPC HUDs if visible
                            if k not in node_np.get_name():
                                _actor = self.base.game_instance["actors_ref"][k]
                                if _actor.has_python_tag("npc_hud_np"):
                                    if _actor.get_python_tag("npc_hud_np") is not None:
                                        if not _actor.get_python_tag("npc_hud_np").is_hidden():
                                            _actor.get_python_tag("npc_hud_np").hide()
                            else:
                                # Show NPC HUD if it's close
                                _actor = self.base.game_instance["actors_ref"][k]
                                if _actor.has_python_tag("npc_hud_np"):
                                    if _actor.get_python_tag("npc_hud_np") is not None:
                                        _actor.get_python_tag("npc_hud_np").show()
                    elif player_rb_np.get_distance(node_np) >= 25:
                        # Hide NPCs HUD if it's far
                        for k in self.base.game_instance["actors_ref"]:
                            _actor = self.base.game_instance["actors_ref"][k]
                            if _actor.has_python_tag("npc_hud_np"):
                                if _actor.get_python_tag("npc_hud_np") is not None:
                                    if not _actor.get_python_tag("npc_hud_np").is_hidden():
                                        _actor.get_python_tag("npc_hud_np").hide()

                # If I have any melee weapon instead of bow
                # Show enemy HUD starting from 2 meters
                elif not base.player_states["has_bow"]:
                    if player_rb_np.get_distance(node_np) > 2:
                        # Hide NPCs HUD if it's far
                        for k in self.base.game_instance["actors_ref"]:
                            _actor = self.base.game_instance["actors_ref"][k]
                            if _actor.has_python_tag("npc_hud_np"):
                                if _actor.get_python_tag("npc_hud_np") is not None:
                                    if not _actor.get_python_tag("npc_hud_np").is_hidden():
                                        _actor.get_python_tag("npc_hud_np").hide()
                    else:
                        for k in self.base.game_instance["actors_ref"]:
                            # Hide all other NPC HUDs if visible
                            if k not in node_np.get_name():
                                _actor = self.base.game_instance["actors_ref"][k]
                                if _actor.has_python_tag("npc_hud_np"):
                                    if _actor.get_python_tag("npc_hud_np") is not None:
                                        if not _actor.get_python_tag("npc_hud_np").is_hidden():
                                            _actor.get_python_tag("npc_hud_np").hide()
                            else:
                                # Show NPC HUD if it's close
                                _actor = self.base.game_instance["actors_ref"][k]
                                if _actor.has_python_tag("npc_hud_np"):
                                    if _actor.get_python_tag("npc_hud_np") is not None:
                                        _actor.get_python_tag("npc_hud_np").show()
