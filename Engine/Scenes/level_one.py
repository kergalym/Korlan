from pathlib import Path

from direct.task.TaskManagerGlobal import taskMgr
from panda3d.core import *
from Engine.Actors.Player.korlan import Korlan
from Engine.Actors.NPC.npc import NPC
from Engine.Scenes.scene_one import SceneOne
from Engine.world import World
from os.path import isfile, exists, join
from os import listdir, walk
import configparser
from sys import exit as sys_exit


class LevelOne:

    def __init__(self):
        self.game_mode = base.game_mode
        self.game_settings = base.game_settings
        self.game_dir = base.game_dir
        self.game_cfg = base.game_cfg
        self.game_cfg_dir = base.game_cfg_dir
        self.game_settings_filename = base.game_settings_filename
        self.cfg_path = {"game_config_path":
                         "{0}/{1}".format(self.game_cfg_dir, self.game_settings_filename)}
        self.base = base
        self.loader = base.loader
        self.node_path = NodePath()
        self.scene_one = SceneOne()
        self.world = World()
        self.korlan = Korlan()
        self.npc = NPC()
        self.pos_x = None
        self.pos_y = None
        self.pos_z = 0.0
        self.anim = None

    def reload_menu_scene(self):
        if self.base.game_mode:
            self.base.game_mode = False
            self.base.menu_mode = True
            assets = self.base.collect_assets()

            # TODO: make taskMgr list with task names strings
            taskMgr.remove("player_init")
            taskMgr.remove("mouse-look")
            taskMgr.remove("actor_life")

            # make pattern list from assets dict
            pattern = [key for key in assets]

            # use pattern to remove nodes corresponding to asset names
            for node in pattern:
                if render.find("**/{0}".format(node)).isEmpty() is False:
                    render.find("**/{0}".format(node)).removeNode()

            for key in assets:
                self.loader.unloadModel(assets[key])

            wp = WindowProperties()
            wp.setCursorHidden(False)
            self.base.win.requestProperties(wp)

            # Disable the camera trackball controls.
            self.base.disableMouse()

            # Disable mouse camera
            self.base.mouseMagnitude = 0
            self.base.rotateX = 0
            self.base.lastMouseX = None
            self.base.hideMouse = False
            self.base.manualRecenterMouse = False
            self.base.camera.setPos(0, 0, 0)
            self.base.camera.setHpr(0, 0, 0)
            self.base.cam.setPos(0, 0, 0)
            self.base.cam.setHpr(0, 0, 0)
            self.base.menu_scene_load()
            self.base.frame.show()

    def load_new_game(self):
        self.game_mode = True
        self.base.accept("escape", self.reload_menu_scene)
        assets = self.base.collect_assets()

        # TODO: make taskMgr list with task names strings
        taskMgr.remove("player_init")
        taskMgr.remove("mouse-look")
        taskMgr.remove("actor_life")

        # make pattern list from assets dict
        pattern = [key for key in assets]

        # use pattern to remove nodes corresponding to asset names
        for node in pattern:
            if render.find("**/{0}".format(node)).isEmpty() is False:
                render.find("**/{0}".format(node)).removeNode()

        for key in assets:
            self.loader.unloadModel(assets[key])

        if isfile("{0}/{1}".format(self.game_cfg_dir,
                                   self.game_settings_filename)):

            try:
                self.game_settings.read("{}/{}".format(self.game_cfg_dir,
                                                       self.game_settings_filename))
            except configparser.MissingSectionHeaderError:
                sys_exit("\nFile contains no section headers. Exiting...")
                sys_exit("\nFile: {0}/{1}".format(self.game_cfg_dir,
                                                  self.game_settings_filename))

        """ Assets """
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

        self.scene_one.env_load(path=assets['Ground'],
                                mode="game",
                                name="Ground",
                                axis=[0.0, 10.0, self.pos_z],
                                rotation=[0, 0, 0],
                                scale=[1.25, 1.25, 1.25],
                                type='ground')

        self.scene_one.env_load(path=assets['Mountains'],
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
