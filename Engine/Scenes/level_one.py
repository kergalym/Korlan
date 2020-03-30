from direct.task.TaskManagerGlobal import taskMgr
from panda3d.core import *
from Engine.Actors.Player.korlan import Korlan
from Engine.Actors.Player.state import PlayerState
from Engine.Actors.NPC.npc import NPC
from Engine.Physics.physics import PhysicsAttr
from Engine.Collisions.collisions import Collisions
from Engine.FSM.env_ai import EnvAI
from Engine.FSM.npc_ai import NpcAI
from Engine.Scenes.scene_one import SceneOne
from Engine.Render.render import RenderAttr
from Settings.UI.stat_ui import StatUI
from Settings.UI.hud_ui import HuDUI


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
        self.hud = HuDUI()
        self.ui_stat = StatUI()
        self.player_state = PlayerState()
        self.physics_attr = PhysicsAttr()
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

            base.game_mode = False
            base.menu_mode = True

    def unload_menu_scene(self):
        self.base.accept("escape", self.unload_game_scene)
        assets = self.base.assets_collector()

        # Remove all lights
        render.clearLight()

        # Remove Bullet World
        if not render.find("**/World").is_empty():
            render.find("**/World").remove_node()

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

    def prepare_assets_task(self, loaded_assets, task):
        if loaded_assets and isinstance(loaded_assets, dict):
            if loaded_assets["Korlan"]:
                self.col.set_collision(obj=loaded_assets["Korlan"],
                                       type="player",
                                       shape="capsule")
            if loaded_assets["NPC"]:
                self.col.set_collision(obj=loaded_assets["NPC"],
                                       type="actor",
                                       shape="capsule")
            if loaded_assets["Box"]:
                self.col.set_collision(obj=loaded_assets["Box"],
                                       type="item",
                                       shape="cube")

            self.fsm_env.set_ai_world()

            if "BS" in loaded_assets["NPC"].get_parent().get_name():
                actor = loaded_assets["NPC"].get_parent()
                # self.fsm_npc.set_npc_ai(actor=actor, behavior="seek")
                # self.fsm_npc.set_npc_ai(actor=actor, behavior="flee")
                # self.fsm_npc.set_npc_ai(actor=actor, behavior="pursuer")
                # self.fsm_npc.set_npc_ai(actor=actor, behavior="evader")
                self.fsm_npc.set_npc_ai(actor=actor, behavior="wanderer")
                # self.fsm_npc.set_npc_ai(actor=actor, behavior="obs_avoid")
                # self.fsm_npc.set_npc_ai(actor=actor, behavior="path_follow")
            return task.done
        return task.cont

    def load_new_game(self):
        self.unload_menu_scene()

        """ Assets """
        self.render_attr.set_lighting(name='directionalLight',
                                      render=self.render,
                                      pos=[0, 0, 10],
                                      hpr=[180, -20, 0],
                                      color=[0.2],
                                      task="attach")
        self.render_attr.set_lighting(name='directionalLight',
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

        box = self.scene_one.asset_load(path=assets['Box'],
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

        player = self.korlan.set_actor(mode="game",
                                       name="Korlan",
                                       path=assets['Korlan'],
                                       animation=anims,
                                       axis=[0, 8.0, self.pos_z],
                                       rotation=[0, 0, 0],
                                       scale=[1.25, 1.25, 1.25])

        npc = self.npc.set_actor(mode="game",
                                 name="NPC",
                                 path=assets['NPC'],
                                 animation=anims,
                                 axis=[-4.0, 9.0, self.pos_z],
                                 rotation=[0, 0, 0],
                                 scale=[1.25, 1.25, 1.25])

        loaded_assets = {
            "Korlan": player,
            "NPC": npc,
            "Box": box
        }

        taskMgr.add(self.prepare_assets_task,
                    "prepare_assets",
                    extraArgs=[loaded_assets],
                    appendTask=True)

        """ Task for Debug mode """
        taskMgr.add(self.ui_stat.show_game_stat_task,
                    "show_game_stat",
                    appendTask=True)
