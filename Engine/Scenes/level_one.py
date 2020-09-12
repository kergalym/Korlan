from direct.task.TaskManagerGlobal import taskMgr
from panda3d.core import *
from Engine.Actors.Player.korlan import Korlan
from Engine.Actors.Player.state import PlayerState
from Engine.Actors.NPC.npc import NPC
from Engine.FSM.npc_ai import NpcAI
from Engine.Render.render import RenderAttr
from Engine.Scenes.scene import SceneOne
from Engine.Physics.physics import PhysicsAttr
from Settings.UI.stat_ui import StatUI
from Engine.Actors.NPC.state import NpcState


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
        self.npc = NPC()
        self.stat_ui = StatUI()
        self.npc_state = NpcState()
        self.player_state = PlayerState()
        self.physics_attr = PhysicsAttr()
        self.fsm_npc = NpcAI()
        self.pos_x = None
        self.pos_y = None
        self.pos_z = 0
        self.anim = None

    def get_npc_bullet_shape_nodes(self, assets, type):
        if (assets and type
                and isinstance(assets, dict)
                and isinstance(type, dict)):
            lvl_npcs = []
            for k in assets:
                if k == 'name':
                    if type == "NPC":
                        if "NPC" in assets[k]:
                            name = assets[k]
                            if not render.find("**/{0}:BS".format(name)).is_empty():
                                lvl_npcs = render.find("**/{0}:BS".format(name))

                    elif type == "Player":
                        if "Player" in assets[k]:
                            name = assets[k]
                            if not render.find("**/{0}:BS".format(name)).is_empty():
                                lvl_npcs = render.find("**/{0}:BS".format(name))
            if lvl_npcs:
                return lvl_npcs

    def unload_game_scene(self):
        if self.base.game_mode:
            self.base.game_mode = False
            self.base.menu_mode = True
            assets = self.base.assets_collector()

            # Remove all lights
            if self.game_settings['Main']['postprocessing'] == 'off':
                render.clearLight()
                if not render.find("**/+Light").is_empty():
                    render.find("**/+Light").remove_node()
            elif (self.render_pipeline
                  and self.game_settings['Main']['postprocessing'] == 'on'):
                base.render_attr.clear_lighting()

            # Remove Bullet World
            if not render.find("**/World").is_empty():
                for i in range(render.find("**/World").get_num_nodes()):
                    if not render.find("**/World").is_empty():
                        render.find("**/World").remove_node()

            # Remove Collisions
            if not render.find("**/Collisions").is_empty():
                for i in range(render.find("**/Collisions").get_num_nodes()):
                    if not render.find("**/Collisions").is_empty():
                        render.find("**/Collisions").remove_node()

            # make pattern list from assets dict
            pattern = [key for key in assets]
            # use pattern to remove nodes corresponding to asset names
            for node in pattern:
                if not render.find("**/{0}".format(node)).is_empty():
                    # Player and actor cleanup
                    if self.korlan.korlan:
                        self.korlan.korlan.cleanup()
                    if self.npc.actor:
                        self.npc.actor.cleanup()

                    render.find("**/{0}".format(node)).remove_node()

            for key in assets:
                self.loader.unload_model(assets[key])

            self.player_state.clear_state()

            base.game_mode = False
            base.menu_mode = True

    def unload_menu_scene(self):
        self.base.accept("escape", self.unload_game_scene)
        assets = self.base.assets_collector()

        # Remove all lights
        if self.game_settings['Main']['postprocessing'] == 'off':
            render.clearLight()
            if not render.find("**/+Light").is_empty():
                render.find("**/+Light").remove_node()
        elif (self.render_pipeline
              and self.game_settings['Main']['postprocessing'] == 'on'):
            base.render_attr.clear_lighting()

        # Remove Bullet World
        if not render.find("**/World").is_empty():
            for i in range(render.find("**/World").get_num_nodes()):
                if not render.find("**/World").is_empty():
                    render.find("**/World").remove_node()

        # Remove Collisions
        if not render.find("**/Collisions").is_empty():
            for i in range(render.find("**/Collisions").get_num_nodes()):
                if not render.find("**/Collisions").is_empty():
                    render.find("**/Collisions").remove_node()

        # make pattern list from assets dict
        pattern = [key for key in assets]
        # use pattern to remove nodes corresponding to asset names
        for node in pattern:
            if not render.find("**/{0}".format(node)).is_empty():
                # Player and actor cleanup
                if self.korlan.korlan:
                    self.korlan.korlan.cleanup()
                if self.npc.actor:
                    self.npc.actor.cleanup()

                render.find("**/{0}".format(node)).remove_node()

        for key in assets:
            self.loader.unload_model(assets[key])

        base.game_mode = True
        base.menu_mode = False

    def load_new_game(self):
        self.unload_menu_scene()

        taskMgr.add(self.render_attr.set_daytime_clock_task,
                    "set_daytime_clock_task",
                    appendTask=True)

        """ Assets """

        """base.render_attr.set_lighting(name='light',
                                      render=self.render,
                                      pos=[-7, 8, 8],
                                      hpr=[180, 130, 0],
                                      color=[0.4],
                                      task="attach")
        base.render_attr.set_lighting(name='light',
                                      render=self.render,
                                      pos=[-12, 8, 8],
                                      hpr=[180, 130, 0],
                                      color=[0.4],
                                      task="attach")
        base.render_attr.set_lighting(name='light',
                                      render=self.render,
                                      pos=[0, 3, 10],
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

        # List used by loading screen
        level_assets = {'name': ['Sky', 'lvl_one', 'Player', 'NPC'],
                        'type': [None, 'env', 'player', 'npc'],
                        'shape': [None, 'auto', 'capsule', 'capsule']
                        }
        base.level_assets = level_assets

        """ Async Loading """
        taskMgr.add(self.scene_one.set_env(path=assets['Sky'],
                                           mode="game",
                                           name="Sky",
                                           axis=[0.0, 10.0, self.pos_z],
                                           rotation=[0, 0, 0],
                                           scale=[1.25, 1.25, 1.25],
                                           type='skybox',
                                           culling=False))

        taskMgr.add(self.scene_one.set_level(path=assets['lvl_one'],
                                             name="lvl_one",
                                             axis=[0.0, 0.0, self.pos_z],
                                             rotation=[0, 0, 0],
                                             scale=[1.25, 1.25, 1.25],
                                             culling=True))

        taskMgr.add(self.korlan.set_actor(mode="game",
                                          name="Player",
                                          path=assets['Korlan'],
                                          animation=anims,
                                          axis=[0, 15.0, self.pos_z],
                                          rotation=[0, 0, 0],
                                          scale=[1.25, 1.25, 1.25],
                                          culling=True))

        taskMgr.add(self.npc.set_actor(mode="game",
                                       name="NPC",
                                       path=assets['NPC'],
                                       animation=anims,
                                       axis=[-15.0, 15.0, self.pos_z],
                                       rotation=[0, 0, 0],
                                       scale=[1.25, 1.25, 1.25],
                                       culling=True))

        """ Task for Debug mode """
        taskMgr.add(self.stat_ui.show_game_stat_task,
                    "show_game_stat",
                    appendTask=True)

        self.physics_attr.set_physics_world(assets=level_assets)

        actors = self.get_npc_bullet_shape_nodes(assets=level_assets, type="NPC")
        player = self.get_npc_bullet_shape_nodes(assets=level_assets, type="Player")

        self.fsm_npc.set_ai_world(actors=actors, player=player, actor_cls="enemy")

        self.npc_state.set_actor_state(actors=actors)

        taskMgr.add(self.fsm_npc.update_npc_ai_stat,
                    "update_npc_ai_stat",
                    extraArgs=[actors],
                    appendTask=True)

    def save_game(self):
        pass

    def load_saved_game(self):
        pass

    def load_free_game(self):
        pass
