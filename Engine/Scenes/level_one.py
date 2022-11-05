from os.path import exists

from direct.task.TaskManagerGlobal import taskMgr
from panda3d.core import *

from Engine.Actors.Player.state import PlayerState
from Engine.async_level_load import AsyncLevelLoad
from Engine.Physics.physics_attr import PhysicsAttr
from Settings.UI.pause_menu_ui import PauseMenuUI
from Engine.AI.npc_controller import NpcController

from Engine.FSM.npc_fsm import NpcFSM

# List used by loading screen
from Engine.Scenes.npc_list_level1 import LEVEL_NPC_ASSETS
from Engine.Scenes.npc_list_level1 import LEVEL_NPC_AXIS

py_npc_fsm_classes = []

for i in range(len(LEVEL_NPC_ASSETS['name'])):
    py_npc_fsm_classes.append(NpcFSM)


class LevelOne:

    def __init__(self):
        self.game_settings = base.game_settings
        self.game_dir = base.game_dir
        self.base = base
        self.render = render
        self.loader = base.loader
        self.node_path = NodePath()
        self.async_level_load = AsyncLevelLoad()
        self.pos_z = 0
        self.actor_fsm_classes = []
        self.pause_game_ui = PauseMenuUI()
        self.player_state = PlayerState()
        self.physics_attr = PhysicsAttr()
        self.base.focused_actor = None
        self.actors_for_focus = None
        self.actor_focus_index = 1
        self.assets = None
        self.envprobe = None

    def game_instance_diagnostic_task(self, task):
        if (self.base.game_instance['hud_np']
                and self.base.game_instance['ai_is_activated'] == 1):
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
        if (self.base.game_instance['physics_is_activated'] == 1
                and self.base.game_instance['scene_np']):
            if self.base.game_instance["renderpipeline_np"]:
                # Set Environment Probe
                self.envprobe = self.base.game_instance["renderpipeline_np"].add_environment_probe()
                scene = self.base.game_instance['scene_np']
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

    def npc_controller_init(self, task):
        if (self.base.game_instance["loading_is_done"] == 1
                and self.base.game_instance['physics_is_activated'] == 1
                and self.base.game_instance['actors_are_loaded']):
            for name in self.base.game_instance["actors_ref"]:
                actor = self.base.game_instance["actors_ref"][name]

                # TODO: Keep it tempo!
                if actor.get_python_tag("npc_class") == "enemy":
                    actor.get_python_tag("generic_states")['is_alive'] = False
                if actor.get_python_tag("npc_class") == "neutral":
                    actor.get_python_tag("generic_states")['is_alive'] = False

                NpcController(actor)

            self.base.game_instance["ai_is_activated"] = 1
            return task.done

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
                self.base.game_instance['hud_np'] = None
            taskMgr.remove("cursor_state_task")

            # Remove day time task
            base.game_instance['render_attr_cls'].time_text_ui.hide()
            taskMgr.remove("set_time_of_day_clock_task")

            # Remove all flames
            base.game_instance['render_attr_cls'].clear_flame()

            # Remove all lights
            base.render_attr.clear_lighting()

            # Remove Collisions
            if not render.find("**/Collisions").is_empty():
                for i in range(render.find("**/Collisions").get_num_nodes()):
                    if not render.find("**/Collisions").is_empty():
                        render.find("**/Collisions").remove_node()
                        render.find("**/Collisions").clear()

            # Unload Physics
            if self.physics_attr and self.physics_attr.world:
                taskMgr.remove("update_rigid_physics_task")

            if self.physics_attr and self.physics_attr.soft_world:
                taskMgr.remove("update_soft_physics_task")

            # Player and NPC cleanup
            if self.async_level_load.korlan:
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
                self.async_level_load.korlan.delete()
                self.async_level_load.korlan.cleanup()

            for name in self.base.game_instance['actors_np']:
                if self.base.game_instance['actors_np'].get(name):
                    self.base.game_instance['actors_np'][name].remove_node()
                    self.base.game_instance['actors_np'][name].clear()

            # Clean Level World
            if render.find("**/World"):
                render.find("**/World").remove_node()
                render.find("**/World").clear()
                self.base.game_instance['scene_np'].remove_node()
                self.base.game_instance['scene_np'].clear()
                self.base.game_instance['player_ref'].remove_node()
                self.base.game_instance['player_ref'].clear()

            # Clean level Navmesh
            if self.base.game_instance["level_navmesh_np"]:
                self.base.game_instance["level_navmesh_np"].remove_node()

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
        self.base.game_instance['menu_mode'] = False

        if self.base.game_instance['menu_scene_video']:
            if "MENU_SCENE_VID" in self.base.game_instance['menu_scene_video'].get_name():
                self.base.game_instance['menu_scene_video'].stop()

    def load_new_game(self):
        self.unload_menu_scene()

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

        self.base.game_instance['render_attr_cls'].time_text_ui.show()
        taskMgr.add(self.base.game_instance['render_attr_cls'].set_time_of_day_clock_task,
                    "set_time_of_day_clock_task",
                    extraArgs=["10:00", 1800],  # 1800 sec == 30 min
                    appendTask=True)

        """ Assets """

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

        # Construct and pass NPC_FSM classes
        for actor, npc_fsm_cls in zip(LEVEL_NPC_ASSETS['name'], py_npc_fsm_classes):
            npc_fsm_cls_self = npc_fsm_cls(actor)
            self.actor_fsm_classes.append(npc_fsm_cls_self)

        for actor, npc_fsm_cls in zip(LEVEL_NPC_ASSETS['name'], self.actor_fsm_classes):
            if "NPC" in actor and npc_fsm_cls:
                self.base.game_instance["npcs_fsm_states"][actor] = npc_fsm_cls

        # Join list values into one shared dict
        level_assets_joined = {}
        for a_key, b_key in zip(level_assets, LEVEL_NPC_ASSETS):
            if a_key == b_key:
                level_assets_joined[a_key] = level_assets[a_key] + LEVEL_NPC_ASSETS[a_key]

        self.base.game_instance['level_assets_np'] = level_assets_joined

        self.actors_for_focus = {}
        for index, actor in enumerate(LEVEL_NPC_ASSETS['name'], 1):
            self.actors_for_focus[index] = actor

        """ Setup Physics """
        self.physics_attr.set_physics_world(self.base.game_instance["npcs_fsm_states"])

        self.physics_attr.set_soft_physics_world(True)

        self.base.game_instance["physics_attr_cls"] = self.physics_attr

        """ Async Loading """

        suffix = "rp"

        # Combined async loading of the scene, player and non-playable_characters
        taskMgr.add(self.async_level_load.async_load_level(scene_name="lvl_one",
                                                           player_name="Player",
                                                           player_pos=[-8, 15, 0],
                                                           scale=1.0,
                                                           culling=False,
                                                           level_npc_assets=LEVEL_NPC_ASSETS,
                                                           level_npc_axis=LEVEL_NPC_AXIS,
                                                           assets=assets,
                                                           suffix=suffix,
                                                           animation=anims))

        """ Task for Debug mode """
        if self.game_settings['Debug']['set_debug_mode'] == 'YES':
            if hasattr(self, "render_pipeline"):
                self.base.accept("r", self.render_pipeline.reload_shaders)

        """ Setup AI """
        if self.game_settings['Debug']['set_editor_mode'] == 'NO':
            taskMgr.add(self.npc_controller_init,
                        "npc_controller_init",
                        appendTask=True)

        taskMgr.add(self.env_probe_task,
                    "env_probe_task",
                    appendTask=True)

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
