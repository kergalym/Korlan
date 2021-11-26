from direct.task.TaskManagerGlobal import taskMgr
from panda3d.core import *
from Engine.Actors.Player.korlan import Korlan
from Engine.Actors.Player.state import PlayerState
from Engine.AI.ai_setup import AI
from Engine.Render.render import RenderAttr
from Engine.Scenes.scene import SceneOne
from Engine.Physics.physics_setup import PhysicsAttr
from Settings.UI.stat_ui import StatUI
from Settings.UI.pause_menu_ui import PauseMenuUI
from Settings.Input.mouse import Mouse

from Engine.Scenes import py_npc_actor_classes
from Engine.Scenes import py_npc_fsm_classes
from Engine.Scenes import level_npc_assets
from Engine.Scenes import level_npc_axis


class LevelOne:

    def __init__(self):
        self.game_settings = base.game_settings
        self.game_mode = base.game_mode
        self.base = base
        self.render = render
        if hasattr(base, "render_pipeline") and base.render_pipeline:
            self.render_pipeline = base.render_pipeline
        self.loader = base.loader
        self.node_path = NodePath()
        self.render_attr = RenderAttr()
        self.scene_one = SceneOne()
        self.korlan = Korlan()
        self.pos_z = 0
        self.actor_classes = []
        self.actor_fsm_classes = []

        for npc_cls in py_npc_actor_classes:
            npc_cls_self = npc_cls()
            self.actor_classes.append(npc_cls_self)

        for npc_fsm_cls in py_npc_fsm_classes:
            npc_fsm_cls_self = npc_fsm_cls()
            self.actor_fsm_classes.append(npc_fsm_cls_self)

        self.stat_ui = StatUI()
        self.pause_game_ui = PauseMenuUI()
        self.player_state = PlayerState()
        self.physics_attr = PhysicsAttr()
        self.ai = AI()
        self.mouse = Mouse()
        self.base.npcs_actor_refs = {}
        self.base.npcs_actors_health = {}
        self.base.npcs_lbl_np = {}
        self.base.alive_actors = {}
        self.base.focused_actor = None
        self.actors_for_focus = None
        self.actor_focus_index = 1
        self.npcs_fsm_states = {}
        self.base.npcs_hits = {}
        self.assets = None
        self.envprobe = None

        self.base.lod = LODNode('LOD')
        self.base.lod_np = NodePath(self.base.lod)
        self.base.lod_np.reparentTo(render)
        self.base.lod.addSwitch(500.0, 0.0)

    def env_probe_task(self, task):
        if (hasattr(self.base, "physics_is_active")
                and self.base.physics_is_active == 1 and
                not render.find("**/lvl_one*").is_empty()):
            if hasattr(self, 'self.render_pipeline'):
                self.envprobe = self.render_pipeline.add_environment_probe()
                scene = render.find("**/lvl_one*")
                self.envprobe.set_pos(scene.get_pos())
                self.envprobe.set_scale(scene.get_scale())
                self.envprobe.set_hpr(scene.get_hpr())
                self.envprobe.border_smoothness = 0.05
                self.envprobe.parallax_correction = True
                self.render_attr.set_flame_particles(name="flame", empty_name="flame_empty_1")
            return task.done

        return task.cont

    def world_sfx_task(self, task):
        if (hasattr(self.base, 'sound_sfx_nature')
                and self.base.sound_sfx_nature):
            if hasattr(self.base, 'loading_is_done') and self.base.loading_is_done == 1:
                if self.base.sound_sfx_nature.status() != self.base.sound_sfx_nature.PLAYING:
                    self.base.sound_sfx_nature.play()

        if self.base.game_mode is False and self.base.menu_mode:
            self.base.sound_sfx_nature.stop()
            return task.done

        return task.cont

    def update_horse_trigger_task(self, task):
        if (hasattr(self.base, "loading_is_done")
                and self.base.loading_is_done == 1):
            player_bs = self.base.get_actor_bullet_shape_node(asset="Player",
                                                              type="Player")
            if player_bs:
                horse = render.find("Korlan_Horse")
                if horse:
                    if not horse.find("**/horserig_trigger").is_empty():
                        trigger = horse.find("**/horserig_trigger").node()
                        trigger_np = horse.find("**/horserig_trigger")
                        for node in trigger.getOverlappingNodes():
                            # ignore trigger itself and ground both
                            if node.get_name() != trigger.get_name() and node.get_name() != "Ground":
                                name = player_bs.get_child(0).get_name()
                                if node.get_name() == name:
                                    # if player close to horse
                                    if player_bs.get_distance(trigger_np) <= 2 \
                                            and player_bs.get_distance(trigger_np) >= 1:
                                        if not base.player_states["is_mounted"] and node.get_name() == name:
                                            base.player_states["horse_is_ready_to_be_used"] = True
                                        elif not base.player_states["is_mounted"] and node.get_name() == player_bs.get_name():
                                            base.player_states["horse_is_ready_to_be_used"] = True

        if self.base.game_mode is False and self.base.menu_mode:
            return task.done

        return task.cont

    def collect_actor_refs_task(self, task):
        if hasattr(base, "npc_is_loaded") and base.npc_is_loaded == 1:
            for npc_cls in self.actor_classes:
                if npc_cls and npc_cls.actor:
                    # Get only Actor, not a child of NodePath
                    name = npc_cls.actor.get_name()

                    base.npcs_actor_refs[name] = npc_cls.actor

                    self.base.alive_actors[name] = True

                if self.korlan.korlan:
                    base.player_ref = self.korlan.korlan

        if hasattr(base, "loading_is_done") and base.loading_is_done == 1:
            return task.done

        return task.cont

    def collect_actors_health_task(self, task):
        if hasattr(base, "npc_is_loaded") and base.npc_is_loaded == 1:
            for npc_cls in self.actor_classes:
                if npc_cls and npc_cls.actor:
                    name = npc_cls.actor.get_name()
                    self.base.npcs_actors_health[name] = npc_cls.npc_life_label

                if self.korlan.korlan:
                    base.player_health = self.korlan.korlan_life_perc

        if self.base.game_mode is False and self.base.menu_mode:
            return task.done

        return task.cont

    def show_actor_label(self, name):
        if name:
            enemy_npc_bs = self.base.get_actor_bullet_shape_node(asset=name, type="NPC")
            if enemy_npc_bs and not enemy_npc_bs.is_empty():  # is enemy here?
                if self.ai and self.ai.near_npc.get(name):
                    if (self.base.npcs_lbl_np.get(name)
                            and self.base.alive_actors[name]):

                        for i in self.base.npcs_lbl_np:
                            if name != i:
                                self.base.npcs_lbl_np[i].hide()

                        self.base.npcs_lbl_np[name].show()
                        self.base.camera.look_at(enemy_npc_bs)

    def select_by_mouse_wheel(self, actors):
        if (actors and isinstance(actors, dict)
                and self.ai and self.ai.near_npc):
            if self.mouse.keymap["wheel_up"]:
                if (self.actor_focus_index < len(actors)
                        and not self.actor_focus_index < 0
                        and self.actor_focus_index != 0):
                    self.actor_focus_index += 1
                    self.base.focused_actor = actors[self.actor_focus_index]
                    self.show_actor_label(name=self.base.focused_actor)
                    self.base.focused_actor = actors[self.actor_focus_index]
                self.mouse.keymap['wheel_up'] = False

            if self.mouse.keymap["wheel_down"]:
                if len(actors) - 1 > 1:
                    actors_num = len(actors) - 1
                else:
                    actors_num = len(actors)

                if (self.actor_focus_index != 0
                        and not self.actor_focus_index < actors_num
                        and not self.actor_focus_index > len(actors)):
                    self.actor_focus_index -= 1
                    self.base.focused_actor = actors[self.actor_focus_index]
                    self.show_actor_label(name=self.base.focused_actor)
                    self.base.focused_actor = actors[self.actor_focus_index]
                self.mouse.keymap['wheel_down'] = False

    def npc_focus_switch_task(self, task):
        self.select_by_mouse_wheel(actors=self.actors_for_focus)

        if self.base.game_mode is False and self.base.menu_mode:
            return task.done

        return task.cont

    def collect_npcs_label_nodepaths_task(self, enemies, task):
        if enemies and isinstance(enemies, dict):
            for npc in self.actor_classes:
                if npc.npc_label_np:
                    name = npc.npc_label_np.get_name()
                    self.base.npcs_lbl_np[name] = npc.npc_label_np

            # Drop item which is not NPC and indicate that collecting is done
            if len(enemies['name']) - 3 == len(self.base.npcs_lbl_np):
                taskMgr.add(self.npc_focus_switch_task,
                            "npc_focus_switch_task",
                            appendTask=True)

                return task.done

        return task.cont

    def hitbox_handling_task(self, task):
        # TODO: Use it to stop previous action animations
        if self.physics_attr.world:
            for hitboxes in self.physics_attr.world.get_ghosts():
                # Drop the HB suffix
                name = hitboxes.get_name().split(":")[0]
                # Reconstruct name with dropping joint suffix to be consistent with pure name
                if "NPC" in name:
                    name = name.split("_")
                    name = "{0}_{1}".format(name[0], name[1])
                elif "Player" in name:
                    name = name.split("_")[0]
                for node in hitboxes.get_overlapping_nodes():
                    if (node and node.is_active()
                            and "NPC" in node.get_name()
                            and "RightHand" in node.get_name()):
                        for hit in node.get_overlapping_nodes():
                            if hit and hit.is_active():
                                if ("Player" in hit.get_name()
                                        and "Hips" in hit.get_name()):
                                    # import pdb; pdb.set_trace()
                                    self.base.npcs_hits[name] = True
                                else:
                                    self.base.npcs_hits[name] = False
                                if ("NPC" in hit.get_name()
                                        and "Hips" in hit.get_name()):
                                    self.base.npcs_hits[name] = True
                                else:
                                    self.base.npcs_hits[name] = False

        if self.base.game_mode is False and self.base.menu_mode:
            return task.done

        return task.cont

    def unload_game_scene(self):
        if self.base.game_mode:
            self.base.game_mode = False
            self.base.menu_mode = True

            assets = self.base.assets_collector()
            self.assets = assets

            # Remove all flames
            self.render_attr.clear_flame()

            # Remove all lights
            if self.game_settings['Main']['postprocessing'] == 'off':
                render.clearLight()
                if not render.find("**/+Light").is_empty():
                    render.find("**/+Light").remove_node()
                    render.find("**/+Light").clear()
            elif (self.render_pipeline
                  and self.game_settings['Main']['postprocessing'] == 'on'):
                base.render_attr.clear_lighting()

            # Remove Collisions
            if not render.find("**/Collisions").is_empty():
                for i in range(render.find("**/Collisions").get_num_nodes()):
                    if not render.find("**/Collisions").is_empty():
                        render.find("**/Collisions").remove_node()
                        render.find("**/Collisions").clear()

            # Remove WaterNodePath
            if not render.find("**/WaterNodePath").is_empty():
                for i in range(render.find("**/WaterNodePath").get_num_nodes()):
                    if not render.find("**/WaterNodePath").is_empty():
                        render.find("**/WaterNodePath").remove_node()
                        render.find("**/WaterNodePath").clear()

            # Remove StateInitializer
            if not render.find("**/StateInitializer").is_empty():
                for i in range(render.find("**/StateInitializer").get_num_nodes()):
                    if not render.find("**/StateInitializer").is_empty():
                        render.find("**/StateInitializer").remove_node()
                        render.find("**/StateInitializer").clear()

            # Player and actor cleanup
            if self.korlan.korlan:
                self.korlan.korlan.delete()
                self.korlan.korlan.cleanup()

            for npc_cls in self.actor_classes:
                if npc_cls.actor:
                    npc_cls.npc_label_np.remove_node()
                    npc_cls.actor.delete()
                    npc_cls.actor.cleanup()

            # use pattern to remove nodes corresponding to asset names
            for i in render.findAllMatches("**/*:BS"):
                if not render.find("**/*:BS").is_empty():
                    render.find("**/*:BS").remove_node()
                    render.find("**/*:BS").clear()

            for key in assets:
                self.loader.unload_model(assets[key])

            self.player_state.clear_state()
            self.actor_focus_index = 1

            if hasattr(self.base, "mouse_control_is_activated"):
                self.base.mouse_control_is_activated = 0

    def unload_menu_scene(self):
        assets = self.base.assets_collector()

        # Remove all lights
        if self.game_settings['Main']['postprocessing'] == 'off':
            render.clearLight()
            if not render.find("**/+Light").is_empty():
                render.find("**/+Light").remove_node()
                render.find("**/+Light").clear()
        elif (self.render_pipeline
              and self.game_settings['Main']['postprocessing'] == 'on'):
            base.render_attr.clear_lighting()

        # Remove Collisions
        if not render.find("**/Collisions").is_empty():
            for i in range(render.find("**/Collisions").get_num_nodes()):
                if not render.find("**/Collisions").is_empty():
                    render.find("**/Collisions").remove_node()
                    render.find("**/Collisions").clear()

        # Remove WaterNodePath
        if not render.find("**/WaterNodePath").is_empty():
            for i in range(render.find("**/WaterNodePath").get_num_nodes()):
                if not render.find("**/WaterNodePath").is_empty():
                    render.find("**/WaterNodePath").remove_node()
                    render.find("**/WaterNodePath").clear()

        # Remove StateInitializer
        if not render.find("**/StateInitializer").is_empty():
            for i in range(render.find("**/StateInitializer").get_num_nodes()):
                if not render.find("**/StateInitializer").is_empty():
                    render.find("**/StateInitializer").remove_node()
                    render.find("**/StateInitializer").clear()

        # Player and actor cleanup
        if self.korlan.korlan:
            self.korlan.korlan.delete()
            self.korlan.korlan.cleanup()

        for npc_cls in self.actor_classes:
            if npc_cls.actor:
                npc_cls.npc_label_np.remove_node()
                npc_cls.actor.delete()
                npc_cls.actor.cleanup()

        # use pattern to remove nodes corresponding to asset names
        for i in render.findAllMatches("**/*:BS"):
            if not render.find("**/*:BS").is_empty():
                render.find("**/*:BS").remove_node()
                render.find("**/*:BS").clear()

        for key in assets:
            self.loader.unload_model(assets[key])

        self.actor_focus_index = 1

        base.game_mode = True
        base.menu_mode = False

        if hasattr(base, "menu_scene_vid") and base.menu_scene_vid:
            if "MENU_SCENE_VID" in base.menu_scene_vid.get_name():
                base.menu_scene_vid.stop()

    def load_new_game(self):
        self.unload_menu_scene()

        self.mouse.mouse_wheel_init()

        # We make any unload_game_scene() method accessible
        # to unload via UnloadingUI.set_parallel_unloading()
        self.base.unload_game_scene = self.unload_game_scene

        self.base.accept("escape", self.pause_game_ui.load_pause_menu)

        """ Set Time of Day """

        self.render_attr.set_time_of_day(duration=1800)  # 1800 sec == 30 min
        taskMgr.add(self.render_attr.set_time_of_day_clock_task,
                    "set_time_of_day_clock_task",
                    extraArgs=["16:00", 1800],  # 1800 sec == 30 min
                    appendTask=True)

        """ Assets """

        base.render_attr.set_lighting(name='plight',
                                      render=self.render,
                                      pos=[-7, 8, 8],
                                      hpr=[180, 130, 0],
                                      color=[0.4],
                                      task="attach")
        base.render_attr.set_lighting(name='plight',
                                      render=self.render,
                                      pos=[-12, 8, 8],
                                      hpr=[180, 130, 0],
                                      color=[0.4],
                                      task="attach")
        """base.render_attr.set_lighting(name='slight',
                                      render=self.render,
                                      pos=[0, 3, 10],
                                      hpr=[0, -20, 0],
                                      color=[0.5],
                                      task="attach")"""
        """self.render_attr.set_lighting(name='dlight',
                                      render=self.render,
                                      pos=[0, -40, 10],
                                      hpr=[0, -20, 0],
                                      color=[0.7],
                                      task="attach")
        self.render_attr.set_lighting(name='alight',
                                      render=self.render,
                                      pos=[0, 8.0, 10],
                                      hpr=[0, -20, 0],
                                      color=[0.8],
                                      task="attach")"""

        # assets is a dict containing paths + models
        # anims is a list containing two dicts.
        # anims[0] is a dict containing names of animations
        # anims[1] is a dict containing paths + animations
        assets = self.base.assets_collector()
        anims = self.base.asset_animations_collector()

        # List used by loading screen
        level_assets = {'name': ['lvl_one', 'Player'],
                        'type': ['env', 'player'],
                        'shape': ['auto', 'capsule'],
                        'class': ['env', 'hero']
                        }

        for actor, npc_fsm_cls in zip(level_npc_assets['name'], self.actor_fsm_classes):
            if "NPC" in actor and npc_fsm_cls:
                self.npcs_fsm_states[actor] = npc_fsm_cls

        # Join list values into one shared dict
        level_assets_joined = {}
        for a_key, b_key in zip(level_assets, level_npc_assets):
            if a_key == b_key:
                level_assets_joined[a_key] = level_assets[a_key] + level_npc_assets[a_key]

        base.level_assets = level_assets_joined

        self.actors_for_focus = {}
        for index, actor in enumerate(level_npc_assets['name'], 1):
            self.actors_for_focus[index] = actor

        taskMgr.add(self.collect_actor_refs_task,
                    "collect_actor_refs_task",
                    appendTask=True)

        self.scene_one.set_env(cloud_dimensions=[2000, 2000, 100],
                               cloud_speed=0.3,
                               cloud_size=20,
                               cloud_count=20,
                               cloud_color=(0.6, 0.6, 0.65, 1.0))

        """ Async Loading """
        suffix = ""
        if self.game_settings['Main']['postprocessing'] == 'on':
            suffix = "rp"
        elif self.game_settings['Main']['postprocessing'] == 'off':
            suffix = "p3d"
        taskMgr.add(self.scene_one.set_level(path=assets['lvl_one_{0}'.format(suffix)],
                                             name="lvl_one",
                                             axis=[0.0, 0.0, self.pos_z],
                                             rotation=[0, 0, 0],
                                             scale=[1.25, 1.25, 1.25],
                                             culling=False))

        taskMgr.add(self.korlan.set_actor(mode="game",
                                          name="Player",
                                          path=assets['Korlan_{0}'.format(suffix)],
                                          animation=anims,
                                          axis=[0, 15.0, self.pos_z],
                                          rotation=[0, 0, 0],
                                          scale=[1.25, 1.25, 1.25],
                                          culling=True))

        for actor, npc_cls, axis_actor in zip(level_npc_assets['name'],
                                              self.actor_classes,
                                              level_npc_axis):
            if actor == axis_actor:
                axis = level_npc_axis[axis_actor]
                taskMgr.add(npc_cls.set_actor(mode="game",
                                              name=actor,
                                              path=assets['{0}_{1}'.format(actor, suffix)],
                                              animation=anims,
                                              axis=axis,
                                              rotation=[0, 0, 0],
                                              scale=[1.25, 1.25, 1.25],
                                              culling=True))

        """ Task for Debug mode """
        if self.game_settings['Debug']['set_debug_mode'] == 'YES':
            if hasattr(self, "render_pipeline"):
                self.base.accept("r", self.render_pipeline.reload_shaders)
            taskMgr.add(self.stat_ui.show_game_stat_task,
                        "show_game_stat_task",
                        appendTask=True)

        self.physics_attr.set_physics_world(assets=level_assets_joined)

        if self.game_settings['Debug']['set_editor_mode'] == 'NO':
            self.ai.set_ai_world(assets=level_assets_joined,
                                 npcs_fsm_states=self.npcs_fsm_states,
                                 lvl_name="lvl_one")

        taskMgr.add(self.env_probe_task,
                    "env_probe_task",
                    appendTask=True)

        taskMgr.add(self.world_sfx_task,
                    "world_sfx_task",
                    appendTask=True)

        taskMgr.add(self.collect_actors_health_task,
                    "collect_actors_health_task",
                    appendTask=True)

        taskMgr.add(self.collect_npcs_label_nodepaths_task,
                    "collect_npcs_label_nodepaths_task",
                    extraArgs=[level_assets_joined],
                    appendTask=True)

        taskMgr.add(self.update_horse_trigger_task,
                    "update_horse_trigger_task",
                    appendTask=True)

        """taskMgr.add(self.hitbox_handling_task,
                    "hitbox_handling_task",
                    appendTask=True)"""

    def save_game(self):
        pass

    def load_saved_game(self):
        pass

    def load_free_game(self):
        pass
