from direct.task.TaskManagerGlobal import taskMgr
from panda3d.core import *
from Engine.Actors.Player.korlan import Korlan
from Engine.Actors.Player.state import PlayerState
from Engine.Actors.NPC.npc_ernar import NpcErnar
from Engine.Actors.NPC.npc_mongol import NpcMongol
from Engine.AI.ai import AI
from Engine.Render.render import RenderAttr
from Engine.Scenes.scene import SceneOne
from Engine.Physics.physics import PhysicsAttr
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
        self.render_attr = RenderAttr()
        self.scene_one = SceneOne()
        self.korlan = Korlan()
        self.npc_ernar = NpcErnar()
        self.npc_mongol = NpcMongol()
        self.stat_ui = StatUI()
        self.player_state = PlayerState()
        self.physics_attr = PhysicsAttr()
        self.ai = AI()
        self.pos_x = None
        self.pos_y = None
        self.pos_z = 0
        self.anim = None
        self.base.npcs_actor_refs = {}

    # TODO: FIXME!
    def collect_actor_refs_task(self, task):
        if hasattr(base, "npc_is_loaded") and base.npc_is_loaded == 1:
            if (self.npc_ernar.actor
                    and self.npc_mongol.actor):
                # Get only Actor, not a child of NodePath
                base.npcs_actor_refs[self.npc_ernar.actor.get_name()] = self.npc_ernar.actor

                base.npcs_actor_refs[self.npc_mongol.actor.get_name()] = self.npc_mongol.actor

        if hasattr(base, "loading_is_done") and base.loading_is_done == 1:
            return task.done

        return task.cont

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
                    render.find("**/+Light").clear()
            elif (self.render_pipeline
                  and self.game_settings['Main']['postprocessing'] == 'on'):
                base.render_attr.clear_lighting()

            # Remove Bullet World
            if not render.find("**/World").is_empty():
                for i in range(render.find("**/World").get_num_nodes()):
                    if not render.find("**/World").is_empty():
                        render.find("**/World").remove_node()
                        render.find("**/World").clear()

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

            # make pattern list from assets dict
            pattern = [key for key in assets]
            # use pattern to remove nodes corresponding to asset names
            for node in pattern:
                if not render.find("**/{0}".format(node)).is_empty():
                    # Player and actor cleanup
                    if self.korlan.korlan:
                        self.korlan.korlan.delete()
                        self.korlan.korlan.cleanup()
                    if self.npc_ernar.actor:
                        self.npc_ernar.actor.delete()
                        self.npc_ernar.actor.cleanup()
                    if self.npc_mongol.actor:
                        self.npc_mongol.actor.delete()
                        self.npc_mongol.actor.cleanup()

                    render.find("**/{0}".format(node)).remove_node()
                    render.find("**/{0}".format(node)).clear()

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
                render.find("**/+Light").clear()
        elif (self.render_pipeline
              and self.game_settings['Main']['postprocessing'] == 'on'):
            base.render_attr.clear_lighting()

        # Remove Bullet World
        if not render.find("**/World").is_empty():
            for i in range(render.find("**/World").get_num_nodes()):
                if not render.find("**/World").is_empty():
                    render.find("**/World").remove_node()
                    render.find("**/World").clear()

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

        # make pattern list from assets dict
        pattern = [key for key in assets]
        # use pattern to remove nodes corresponding to asset names
        for node in pattern:
            if not render.find("**/{0}".format(node)).is_empty():
                # Player and actor cleanup
                if self.korlan.korlan:
                    self.korlan.korlan.delete()
                    self.korlan.korlan.cleanup()
                if self.npc_ernar.actor:
                    self.npc_ernar.actor.delete()
                    self.npc_ernar.actor.cleanup()
                if self.npc_mongol.actor:
                    self.npc_mongol.actor.delete()
                    self.npc_mongol.actor.cleanup()

                render.find("**/{0}".format(node)).remove_node()
                render.find("**/{0}".format(node)).clear()

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
        level_assets = {'name': ['Sky', 'lvl_one', 'Player', 'NPC_Ernar', 'NPC_Mongol'],
                        'type': [None, 'env', 'player', 'npc', 'npc'],
                        'shape': [None, 'auto', 'capsule', 'capsule', 'capsule'],
                        'class': [None, 'env', 'hero', 'friend', 'enemy']
                        }
        base.level_assets = level_assets

        taskMgr.add(self.collect_actor_refs_task,
                    "collect_actor_refs_task",
                    appendTask=True)

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

        taskMgr.add(self.npc_ernar.set_actor(mode="game",
                                             name="NPC_Ernar",
                                             path=assets['NPC_Ernar'],
                                             animation=anims,
                                             axis=[-15.0, 15.0, self.pos_z],
                                             rotation=[0, 0, 0],
                                             scale=[1.25, 1.25, 1.25],
                                             culling=True))

        taskMgr.add(self.npc_mongol.set_actor(mode="game",
                                              name="NPC_Mongol",
                                              path=assets['NPC_Mongol'],
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

        taskMgr.add(self.ai.set_ai_world,
                    "set_ai_world",
                    extraArgs=[level_assets],
                    appendTask=True)

        taskMgr.add(self.ai.update_ai_world_task,
                    "update_ai_world",
                    appendTask=True)

        taskMgr.add(self.ai.update_npc_states_task,
                    "update_npc_states_task",
                    appendTask=True)

    def save_game(self):
        pass

    def load_saved_game(self):
        pass

    def load_free_game(self):
        pass
