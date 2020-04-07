from direct.task.TaskManagerGlobal import taskMgr
from panda3d.core import *
from Engine.Actors.Player.korlan import Korlan
from Engine.Actors.Player.state import PlayerState
from Engine.Actors.NPC.npc import NPC
from Engine.Collisions.collisions import Collisions
from Engine.FSM.env_ai import EnvAI
from Engine.FSM.npc_ai import NpcAI
from Engine.Scenes.scene_one import SceneOne
from Engine.Render.render import RenderAttr
from Settings.UI.stat_ui import StatUI
from Settings.UI.hud_ui import HudUI


class LevelOne:

    def __init__(self):
        self.game_settings = base.game_settings
        self.game_mode = base.game_mode
        self.base = base
        self.render = render
        self.loader = base.loader
        self.node_path = NodePath()
        self.scene_one = SceneOne()
        self.render_attr = RenderAttr()
        self.korlan = Korlan()
        self.npc = NPC()
        self.hud = HudUI()
        self.stat_ui = StatUI()
        self.player_state = PlayerState()
        self.col = Collisions()
        self.fsm_env = EnvAI()
        self.fsm_npc = NpcAI()
        self.pos_x = None
        self.pos_y = None
        self.pos_z = 0.0
        self.anim = None

    def unload_game_scene(self):
        if self.base.game_mode:
            self.base.game_mode = False
            self.base.menu_mode = True

            self.hud.clear_hud()
            self.hud.clear_hud_avatar()
            self.player_state.clear_state()

            # Remove Bullet World
            if not render.find("**/World").is_empty():
                for i in range(render.find("**/World").get_num_nodes()):
                    render.find("**/World").remove_node()

            base.game_mode = False
            base.menu_mode = True

    def unload_menu_scene(self):
        self.base.accept("escape", self.unload_game_scene)
        assets = self.base.assets_collector()

        # Remove all lights
        render.clearLight()

        # Remove Bullet World
        if not render.find("**/World").is_empty():
            for i in range(render.find("**/World").get_num_nodes()):
                render.find("**/World").remove_node()

        # make pattern list from assets dict
        pattern = [key for key in assets]
        # use pattern to remove nodes corresponding to asset names
        for node in pattern:
            if render.find("**/{0}".format(node)).is_empty() is False:
                render.find("**/{0}".format(node)).remove_node()

        for key in assets:
            self.loader.unload_model(assets[key])

        base.game_mode = True
        base.menu_mode = False

    def load_new_game(self):
        self.unload_menu_scene()

        """ Assets """
        self.render_attr.set_lighting(name='pointLight',
                                      render=self.render,
                                      pos=[0, 0, 10],
                                      hpr=[180, -20, 0],
                                      color=[0.2],
                                      task="attach")
        self.render_attr.set_lighting(name='pointLight',
                                      render=self.render,
                                      pos=[0, 0, 10],
                                      hpr=[0, -20, 0],
                                      color=[0.2],
                                      task="attach")

        # assets is a dict containing paths + models
        # anims is a list containing two dicts.
        # anims[0] is a dict containing names of animations
        # anims[1] is a dict containing paths + animations
        assets = self.base.assets_collector()
        anims = self.base.asset_animations_collector()

        """ Async Loading """
        taskMgr.add(self.scene_one.set_env(path=assets['Sky'],
                                           mode="game",
                                           name="Sky",
                                           axis=[0.0, 10.0, self.pos_z],
                                           rotation=[0, 0, 0],
                                           scale=[1.25, 1.25, 1.25],
                                           type='skybox'))

        taskMgr.add(self.scene_one.set_asset(path=assets['Grass'],
                                             mode="game",
                                             name="Grass",
                                             axis=[20.0, 10.0, self.pos_z],
                                             rotation=[0, 0, 0],
                                             scale=[1.25, 1.25, 1.25]))

        taskMgr.add(self.scene_one.set_asset(path=assets['Nomad_house'],
                                             mode="game",
                                             name="Nomad_house",
                                             axis=[0.0, 20.0, self.pos_z],
                                             rotation=[65, 0, 0],
                                             scale=[1.25, 1.25, 1.25]))

        taskMgr.add(self.scene_one.set_asset(path=assets['Box'],
                                             mode="game",
                                             name="Box",
                                             axis=[0.0, -9.0, self.pos_z],
                                             rotation=[65, 0, 0],
                                             scale=[1.25, 1.25, 1.25]))

        taskMgr.add(self.scene_one.set_env(path=assets['Ground'],
                                           mode="game",
                                           name="Ground",
                                           axis=[0.0, 10.0, self.pos_z],
                                           rotation=[0, 0, 0],
                                           scale=[1.25, 1.25, 1.25],
                                           type='ground'))

        taskMgr.add(self.scene_one.set_env(path=assets['Mountains_octree'],
                                           mode="game",
                                           name="Mountains",
                                           axis=[0.0, 20.0, self.pos_z],
                                           rotation=[0, 0, 0],
                                           scale=[1.25, 1.25, 1.25],
                                           type='mountains'))

        taskMgr.add(self.korlan.set_actor(mode="game",
                                          name="Korlan",
                                          path=assets['Korlan'],
                                          animation=anims,
                                          axis=[0, 8.0, self.pos_z],
                                          rotation=[0, 0, 0],
                                          scale=[1.25, 1.25, 1.25]))

        taskMgr.add(self.npc.set_actor(mode="game",
                                       name="NPC",
                                       path=assets['NPC'],
                                       animation=anims,
                                       axis=[-4.0, 9.0, self.pos_z],
                                       rotation=[0, 0, 0],
                                       scale=[1.25, 1.25, 1.25]))

        """ Task for Debug mode """
        taskMgr.add(self.stat_ui.show_game_stat_task,
                    "show_game_stat",
                    appendTask=True)

    def save_game(self):
        pass

    def load_saved_game(self):
        pass

    def load_free_game(self):
        pass
