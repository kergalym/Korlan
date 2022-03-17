from os.path import exists

from direct.task.TaskManagerGlobal import taskMgr
from panda3d.core import *
from Engine.Actors.Player.korlan import Korlan
from Engine.Actors.Player.state import PlayerState
from Engine.AI.ai_setup import AI
from Engine.Renderer.renderer import RenderAttr
from Engine.Scenes.scene import SceneOne
from Engine.Physics.physics_setup import PhysicsAttr
from Settings.UI.pause_menu_ui import PauseMenuUI
from Settings.Input.mouse import Mouse

from Engine.Actors.NPC.npc_generic import NpcGeneric
from Engine.FSM.npc_fsm import NpcFSM

py_npc_actor_classes = []
py_npc_fsm_classes = []

# List used by loading screen
level_npc_assets = {'name': ['NPC_Ernar', 'NPC_Mongol', 'NPC_Mongol2', 'NPC_Korlan_Horse', 'NPC_Horse'],
                    'type': ['npc', 'npc', 'npc', 'npc_animal', 'npc_animal'],
                    'shape': ['capsule', 'capsule', 'capsule', 'capsule', 'capsule'],
                    'class': ['friend', 'enemy', 'enemy', 'friend', 'enemy']
                    }

level_npc_axis = {'NPC_Ernar': [-3.0, 17.0, 0],
                  'NPC_Mongol': [-7.0, 20.0, 0],
                  'NPC_Mongol2': [-10.0, 27.0, 0],
                  'NPC_Korlan_Horse': [-9.0, 5.0, 0],
                  'NPC_Horse': [9.0, 5.0, 0]
                  }

for i in range(len(level_npc_assets['name'])):
    py_npc_actor_classes.append(NpcGeneric)
    py_npc_fsm_classes.append(NpcFSM)

"""
level_npc_assets = {'name': [],
                    'type': [],
                    'shape': [],
                    'class': []
                    }
level_npc_axis = {}
"""


class LevelOne:

    def __init__(self):
        self.game_settings = base.game_settings
        self.game_dir = base.game_dir
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

        self.pause_game_ui = PauseMenuUI()
        self.player_state = PlayerState()
        self.physics_attr = PhysicsAttr()
        self.ai = None
        self.mouse = Mouse()
        self.base.focused_actor = None
        self.actors_for_focus = None
        self.actor_focus_index = 1
        self.npcs_fsm_states = {}
        self.assets = None
        self.envprobe = None

    def game_instance_diagnostic_task(self, task):
        if self.base.game_instance['hud_np'] and self.base.game_instance['ai_is_activated'] == 1:
            text = ''
            for key in self.base.game_instance:
                text += "{0}:  {1}\n".format(key, self.base.game_instance[key])

            if not exists("{0}/game_state_report_first_new_game.log".format(self.game_dir)):
                with open("{0}/game_state_report_first_new_game.log".format(self.game_dir), "w") as f:
                    f.write(text)
            else:
                with open("{0}/game_state_report_new_game.log".format(self.game_dir), "w") as f:
                    f.write(text)

            return task.done
        return task.cont

    def env_probe_task(self, task):
        if (self.base.game_instance['physics_is_activated'] == 1 and
                not render.find("**/lvl_one*").is_empty()):
            if hasattr(self, 'render_pipeline'):
                self.envprobe = self.render_pipeline.add_environment_probe()
                scene = render.find("**/lvl_one*")
                self.envprobe.set_pos(scene.get_pos())
                self.envprobe.set_scale(scene.get_scale())
                self.envprobe.set_hpr(scene.get_hpr())
                self.envprobe.border_smoothness = 0.05
                self.envprobe.parallax_correction = True
            return task.done

        return task.cont

    def world_sfx_task(self, task):
        if (hasattr(self.base, 'sound_sfx_nature')
                and self.base.sound_sfx_nature):
            if self.base.game_instance['loading_is_done'] == 1:
                if self.base.sound_sfx_nature.status() != self.base.sound_sfx_nature.PLAYING:
                    self.base.sound_sfx_nature.play()
        return task.cont

    def unload_game_scene(self):
        if not self.base.game_instance['menu_mode']:
            self.base.game_instance['menu_mode'] = True

            assets = self.base.assets_collector()
            self.assets = assets

            # Stop sounds
            self.base.sound_sfx_nature.stop()
            taskMgr.remove("world_sfx_task")

            # Remove HUD elements
            if self.base.game_instance['hud_np']:
                self.base.game_instance['hud_np'].clear_aim_cursor()
                self.base.game_instance['hud_np'].clear_day_hud()
                self.base.game_instance['hud_np'].clear_player_bar()
                self.base.game_instance['hud_np'].clear_weapon_ui()
            taskMgr.remove("cursor_state_task")

            # Remove day time task
            self.render_attr.time_text_ui.hide()
            taskMgr.remove("set_time_of_day_clock_task")

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

            # Unload Physics
            if self.physics_attr and self.physics_attr.world:
                taskMgr.remove("update_physics_task")

            # Unload AI
            if self.ai and self.ai.ai_world:
                taskMgr.remove("npc_distance_calculate_task")
                taskMgr.remove("update_npc_states_task")
                taskMgr.remove("update_pathfinding_task")
                taskMgr.remove("update_ai_world")

                for key in level_npc_assets['class']:
                    self.ai.ai_world.removeAiChar(key)

                self.ai.ai_char = None
                self.ai.ai_chars = {}

            # Player and actors cleanup
            if self.korlan.korlan:
                # Remove all remained nodes
                if not render.find('**/Player:BS').is_empty():
                    render.find('**/Player:BS').remove_node()

                taskMgr.remove("calculate_arrow_trajectory_task")
                taskMgr.remove("arrow_hit_check_task")
                taskMgr.remove("charge_arrow_task")
                taskMgr.remove("arrow_fly_task")

                taskMgr.remove("player_actions_task")
                taskMgr.remove("mouse_control_task")
                taskMgr.remove("collect_actors_health_task")
                taskMgr.remove("update_horse_trigger_task")
                self.korlan.korlan.delete()
                self.korlan.korlan.cleanup()

            for npc_cls in self.actor_classes:
                if npc_cls.actor:
                    npc_cls.actor.delete()
                    npc_cls.actor.cleanup()

            # Clean Level World
            if render.find("**/World"):
                render.find("**/World").remove_node()
                render.find("**/World").clear()
                self.base.game_instance['scene_np'].remove_node()
                self.base.game_instance['scene_np'].clear()
                self.base.game_instance['player_ref'].remove_node()
                self.base.game_instance['player_ref'].clear()

            for key in assets:
                self.loader.unload_model(assets[key])

            self.player_state.clear_state()
            self.actor_focus_index = 1

            self.base.game_instance['mouse_control_is_activated'] = 0
            self.base.game_instance['physics_is_activated'] = 0
            self.base.game_instance['ai_is_activated'] = 0

            self.base.game_instance['scene_is_loaded'] = False
            self.base.game_instance['player_is_loaded'] = False
            self.base.game_instance['actors_are_loaded'] = False
            self.base.game_instance['is_ready_for_game'] = False

            if self.game_settings['Debug']['set_debug_mode'] == 'YES':
                taskMgr.remove("game_instance_diagnostic_task")

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
                npc_cls.actor.delete()
                npc_cls.actor.cleanup()

        # Clean Level World
        if render.find("**/World"):
            render.find("**/World").remove_node()
            render.find("**/World").clear()

        for key in assets:
            self.loader.unload_model(assets[key])

        self.actor_focus_index = 1

        self.base.game_instance['menu_mode'] = False

        if self.base.game_instance['menu_scene_video']:
            if "MENU_SCENE_VID" in self.base.game_instance['menu_scene_video'].get_name():
                self.base.game_instance['menu_scene_video'].stop()

    def load_new_game(self):
        self.unload_menu_scene()

        self.mouse.mouse_wheel_init()

        # We make any unload_game_scene() method accessible global
        # in UnloadingUI.start_unloading()
        self.base.shared_functions['unload_game_scene'] = self.unload_game_scene

        self.base.accept("escape", self.pause_game_ui.load_pause_menu)

        """ Set Time of Day """

        world_np = NodePath("World")
        world_np.reparent_to(render)

        lod = LODNode('LOD')
        self.base.game_instance['lod_np'] = NodePath(lod)
        self.base.game_instance['lod_np'].reparentTo(world_np)

        # set native render effects
        if self.game_settings['Main']['postprocessing'] == 'off':
            taskMgr.add(self.render_attr.setup_native_renderer,
                        "setup_native_renderer_task",
                        extraArgs=[True], appendTask=True)

        self.render_attr.set_time_of_day(duration=1800)  # 1800 sec == 30 min
        self.render_attr.time_text_ui.show()
        taskMgr.add(self.render_attr.set_time_of_day_clock_task,
                    "set_time_of_day_clock_task",
                    extraArgs=["16:00", 1800],  # 1800 sec == 30 min
                    appendTask=True)

        """ Assets """

        """self.render_attr.set_lighting(name='plight',
                                      render=self.render,
                                      pos=[-7, 8, 8],
                                      hpr=[180, 130, 0],
                                      color=[0.4],
                                      task="attach")
        self.render_attr.set_lighting(name='plight',
                                      render=self.render,
                                      pos=[-12, 8, 8],
                                      hpr=[180, 130, 0],
                                      color=[0.4],
                                      task="attach")
        self.render_attr.set_lighting(name='slight',
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

        self.base.game_instance['level_assets_np'] = level_assets_joined

        self.actors_for_focus = {}
        for index, actor in enumerate(level_npc_assets['name'], 1):
            self.actors_for_focus[index] = actor

        self.scene_one.set_env(cloud_dimensions=[2000, 2000, 100],
                               cloud_speed=0.3,
                               cloud_size=20,
                               cloud_count=20,
                               cloud_color=(0.6, 0.6, 0.65, 1.0))

        """ Setup Physics """
        self.physics_attr.set_physics_world(self.npcs_fsm_states)

        self.base.accept("add_bullet_collider", self.physics_attr.add_bullet_collider, [level_assets_joined])

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
                                             scale=[1.0, 1.0, 1.0],
                                             culling=False))

        taskMgr.add(self.korlan.set_actor(mode="game",
                                          name="Player",
                                          path=assets['Korlan_{0}'.format(suffix)],
                                          animation=anims,
                                          axis=[0, 15.0, self.pos_z],
                                          rotation=[0, 0, 0],
                                          scale=[1.0, 1.0, 1.0],
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
                                              scale=[1.0, 1.0, 1.0],
                                              culling=True))
                self.base.game_instance['actors_are_loaded'] = True

        """ Task for Debug mode """
        if self.game_settings['Debug']['set_debug_mode'] == 'YES':
            if hasattr(self, "render_pipeline"):
                self.base.accept("r", self.render_pipeline.reload_shaders)

        """ Setup AI """
        if self.game_settings['Debug']['set_editor_mode'] == 'NO':
            # To avoid nullptr assertion error initialize AI World only if it has not been initialized yet

            if not self.ai:
                self.ai = AI(world_np)
            self.ai.set_ai_world(assets=level_assets_joined,
                                 npcs_fsm_states=self.npcs_fsm_states,
                                 lvl_name="lvl_one")

        """
        taskMgr.add(self.env_probe_task,
                    "env_probe_task",
                    appendTask=True)
        """

        taskMgr.add(self.world_sfx_task,
                    "world_sfx_task",
                    appendTask=True)

        if self.game_settings['Debug']['set_debug_mode'] == 'YES':
            taskMgr.add(self.game_instance_diagnostic_task,
                        "game_instance_diagnostic_task")

    def save_game(self):
        pass

    def load_saved_game(self):
        pass

    def load_free_game(self):
        pass
