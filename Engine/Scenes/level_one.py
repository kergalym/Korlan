from direct.task.TaskManagerGlobal import taskMgr
from panda3d.core import *
from Engine.Actors.Player.korlan import Korlan
from Engine.Actors.NPC.npc import NPC
from Engine.Scenes.scene_one import SceneOne
from Engine.world import World
from Settings.UI.ui_stat import UIStat
from Settings.UI.hud import HUD


class LevelOne:

    def __init__(self):
        self.game_settings = base.game_settings
        self.game_mode = base.game_mode
        self.base = base
        self.render = render
        self.loader = base.loader
        self.node_path = NodePath()
        self.scene_one = SceneOne()
        self.world = World()
        self.korlan = Korlan()
        self.npc = NPC()
        self.hud = HUD()
        self.ui_stat = UIStat()
        self.pos_x = None
        self.pos_y = None
        self.pos_z = 0.0
        self.anim = None

    def reload_menu_scene(self):
        if self.base.game_mode:
            self.base.game_mode = False
            self.base.menu_mode = True
            assets = self.base.collect_assets()

            # Remove all lights
            render.clearLight()

            # Remove all tasks except system
            tasks = ["player_init",
                     "player_state",
                     "actor_life",
                     "mouse_look"]
            for t in tasks:
                taskMgr.remove(t)

            # make pattern list from assets dict
            pattern = [key for key in assets]
            # use pattern to remove nodes corresponding to asset names
            for node in pattern:
                if render.find("**/{0}".format(node)).is_empty() is False:
                    render.find("**/{0}".format(node)).remove_node()

            for key in assets:
                self.loader.unload_model(assets[key])

            wp = WindowProperties()
            wp.set_cursor_hidden(False)
            self.base.win.request_properties(wp)

            # Disable the camera trackball controls.
            self.base.disable_mouse()

            # Disable mouse camera
            self.base.mouse_magnitude = 0
            self.base.rotate_x = 0
            self.base.last_mouse_x = None
            self.base.hide_mouse = False
            self.base.manual_recenter_Mouse = False
            self.base.camera.set_pos(0, 0, 0)
            self.base.camera.set_hpr(0, 0, 0)
            self.base.cam.set_pos(0, 0, 0)
            self.base.cam.set_hpr(0, 0, 0)
            self.base.menu_scene_load()
            self.base.frame.show()

            base.game_mode = False
            base.menu_mode = True

    def load_new_game(self):
        self.base.accept("escape", self.reload_menu_scene)
        assets = self.base.collect_assets()

        # Remove all lights
        render.clearLight()

        # Remove all tasks except system
        tasks = ["player_init",
                 "player_state",
                 "actor_life",
                 "mouse_look"]
        for t in tasks:
            taskMgr.remove(t)

        base.game_mode = True
        base.menu_mode = False

        # make pattern list from assets dict
        pattern = [key for key in assets]
        # use pattern to remove nodes corresponding to asset names
        for node in pattern:
            if render.find("**/{0}".format(node)).is_empty() is False:
                render.find("**/{0}".format(node)).remove_node()

        for key in assets:
            self.loader.unload_model(assets[key])

        """ Assets """
        self.world.set_lighting(name='directionalLight',
                                render=self.render,
                                pos=[0, 0, 10],
                                hpr=[180, -20, 0],
                                color=[0.2],
                                task="attach")
        self.world.set_lighting(name='directionalLight',
                                render=self.render,
                                pos=[0, 0, 10],
                                hpr=[0, -20, 0],
                                color=[0.2],
                                task="attach")

        # assets is a dict containing paths + models
        # anims is a list containing two dicts.
        # anims[0] is a dict containing names of animations
        # anims[1] is a dict containing paths + animations
        assets = self.base.collect_assets()
        anims = self.base.collect_anims()

        self.scene_one.env_load(path=assets['Sky'],
                                mode="game",
                                name="Sky",
                                axis=[0.0, 10.0, self.pos_z],
                                rotation=[0, 0, 0],
                                scale=[1.25, 1.25, 1.25],
                                type='skybox')

        self.scene_one.asset_load(path=assets['Grass'],
                                  mode="game",
                                  name="Grass",
                                  axis=[20.0, 10.0, self.pos_z],
                                  rotation=[0, 0, 0],
                                  scale=[1.25, 1.25, 1.25])

        self.scene_one.asset_load(path=assets['Nomad_house'],
                                  mode="game",
                                  name="Nomad_house",
                                  axis=[0.0, 20.0, self.pos_z],
                                  rotation=[65, 0, 0],
                                  scale=[1.25, 1.25, 1.25])

        self.scene_one.asset_load(path=assets['Box'],
                                  mode="game",
                                  name="Box",
                                  axis=[0.0, -9.0, self.pos_z],
                                  rotation=[65, 0, 0],
                                  scale=[1.25, 1.25, 1.25])

        self.scene_one.env_load(path=assets['Ground'],
                                mode="game",
                                name="Ground",
                                axis=[0.0, 10.0, self.pos_z],
                                rotation=[0, 0, 0],
                                scale=[1.25, 1.25, 1.25],
                                type='ground')

        self.scene_one.env_load(path=assets['Mountains_octree'],
                                mode="game",
                                name="Mountains",
                                axis=[0.0, 20.0, self.pos_z],
                                rotation=[0, 0, 0],
                                scale=[1.25, 1.25, 1.25],
                                type='mountains')

        self.korlan.set_actor(mode="game",
                              name="Korlan",
                              path=assets['Korlan'],
                              animation=anims,
                              axis=[0, 8.0, self.pos_z],
                              rotation=[0, 0, 0],
                              scale=[1.25, 1.25, 1.25])

        self.npc.set_actor(mode="game",
                           name="NPC",
                           path=assets['NPC'],
                           animation=[anims[0]['LookingAround'], anims[1]['LookingAround']],
                           axis=[-2.0, 8.0, self.pos_z],
                           rotation=[0, 0, 0],
                           scale=[1.25, 1.25, 1.25])

        """ Task for Debug mode """
        taskMgr.add(self.ui_stat.show_game_stat_task,
                    "show_game_stat",
                    appendTask=True)
