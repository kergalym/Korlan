from direct.task.TaskManagerGlobal import taskMgr
from panda3d.core import *
from Engine.Actors.Player.korlan import Korlan
from Engine.Actors.Player.state import PlayerState
from Engine.Actors.NPC.npc import NPC
from Engine.Collisions.collisions import Collisions
from Engine.FSM.env_ai import EnvAI
from Engine.FSM.npc_ai import NpcAI
from Engine.Scenes.scene import SceneOne
from Engine.Render.render import RenderAttr
from Settings.UI.stat_ui import StatUI


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
        self.scene_one = SceneOne()
        self.render_attr = RenderAttr()
        self.korlan = Korlan()
        self.npc = NPC()
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
        if self.game_settings['Main']['postprocessing'] == 'off':
            render.clearLight()
        elif (self.render_pipeline
              and self.game_settings['Main']['postprocessing'] == 'on'):
            self.render_attr.clear_lighting()

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
        self.render_attr.set_lighting(name='light',
                                      render=self.render,
                                      pos=[0, 15.0, 0],
                                      hpr=[180, -20, 0],
                                      color=[0.5],
                                      task="attach")
        """self.render_attr.set_lighting(name='light',
                                      render=self.render,
                                      pos=[0, 20, 10],
                                      hpr=[0, -20, 0],
                                      color=[0.5],
                                      task="attach")
        self.render_attr.set_lighting(name='light',
                                      render=self.render,
                                      pos=[0, -40, 10],
                                      hpr=[0, -20, 0],
                                      color=[0.7],
                                      task="attach")
        self.render_attr.set_lighting(name='light',
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

        """ Async Loading """
        taskMgr.add(self.scene_one.set_env(path=assets['Sky'],
                                           mode="game",
                                           name="Sky",
                                           axis=[0.0, 10.0, self.pos_z],
                                           rotation=[0, 0, 0],
                                           scale=[1.25, 1.25, 1.25],
                                           type='skybox',
                                           culling=False))

        taskMgr.add(self.scene_one.set_asset(path=assets['Grass'],
                                             mode="game",
                                             name="Grass",
                                             axis=[20.0, 10.0, self.pos_z],
                                             rotation=[0, 0, 0],
                                             scale=[1.25, 1.25, 1.25],
                                             culling=False))

        taskMgr.add(self.scene_one.set_asset(path=assets['Nomad_house'],
                                             mode="game",
                                             name="Nomad_house",
                                             axis=[9.0, 8.0, self.pos_z],
                                             rotation=[16.70, 0, 0],
                                             scale=[1.25, 1.25, 1.25],
                                             culling=True))

        taskMgr.add(self.scene_one.set_asset(path=assets['Box'],
                                             mode="game",
                                             name="Box",
                                             axis=[0.0, -9.0, self.pos_z],
                                             rotation=[65, 0, 0],
                                             scale=[1.25, 1.25, 1.25],
                                             culling=False))

        taskMgr.add(self.scene_one.set_env(path=assets['Ground'],
                                           mode="game",
                                           name="Ground",
                                           axis=[0.0, 10.0, self.pos_z],
                                           rotation=[0, 0, 0],
                                           scale=[1.25, 1.25, 1.25],
                                           type='ground',
                                           culling=False))

        taskMgr.add(self.scene_one.set_env(path=assets['Mountains'],
                                           mode="game",
                                           name="Mountains",
                                           axis=[0.0, 20.0, self.pos_z],
                                           rotation=[0, 0, 0],
                                           scale=[1.25, 1.25, 1.25],
                                           type='mountains',
                                           culling=False))

        taskMgr.add(self.korlan.set_actor(mode="game",
                                          name="Korlan",
                                          path=assets['Korlan'],
                                          animation=anims,
                                          axis=[0, 8.0, self.pos_z],
                                          rotation=[0, 0, 0],
                                          scale=[1.25, 1.25, 1.25],
                                          culling=True))

        taskMgr.add(self.npc.set_actor(mode="game",
                                       name="NPC",
                                       path=assets['NPC'],
                                       animation=anims,
                                       axis=[-4.0, 9.0, self.pos_z],
                                       rotation=[0, 0, 0],
                                       scale=[1.25, 1.25, 1.25],
                                       culling=True))

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
