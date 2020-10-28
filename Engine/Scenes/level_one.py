from direct.task.TaskManagerGlobal import taskMgr
from panda3d.core import *
from Engine.Actors.Player.korlan import Korlan
from Engine.Actors.Player.state import PlayerState
from Engine.Actors.NPC.npc_ernar import NpcErnar
from Engine.Actors.NPC.npc_mongol import NpcMongol
from Engine.FSM.npc_ernar_fsm import NpcErnarFSM
from Engine.FSM.npc_mongol_fsm import NpcMongolFSM
from Engine.AI.ai import AI
from Engine.Render.render import RenderAttr
from Engine.Scenes.scene import SceneOne
from Engine.Physics.physics import PhysicsAttr
from Settings.UI.stat_ui import StatUI
from Settings.UI.pause_menu_ui import PauseMenuUI


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
        self.npc_ernar_fsm = NpcErnarFSM()
        self.npc_mongol_fsm = NpcMongolFSM()
        self.stat_ui = StatUI()
        self.pause_game_ui = PauseMenuUI()
        self.player_state = PlayerState()
        self.physics_attr = PhysicsAttr()
        self.ai = AI()
        self.base.npcs_actor_refs = {}
        self.base.npcs_actors_health = {}
        self.base.npcs_lbl_np = {}
        self.base.alive_actors = {}
        self.base.focused_actor = None
        self.npcs_fsm_states = {}
        self.pos_x = None
        self.pos_y = None
        self.pos_z = 0
        self.anim = None
        self.base.npcs_active_actions = {}
        self.base.npcs_hits = {}
        self.base.npcs_hits_pos = {}

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

    def collect_actor_refs_task(self, task):
        if hasattr(base, "npc_is_loaded") and base.npc_is_loaded == 1:
            if (self.npc_ernar.actor
                    and self.npc_mongol.actor):
                # Get only Actor, not a child of NodePath
                ernar_name = self.npc_ernar.actor.get_name()
                mongol_name = self.npc_mongol.actor.get_name()

                base.npcs_actor_refs[ernar_name] = self.npc_ernar.actor
                base.npcs_actor_refs[mongol_name] = self.npc_mongol.actor

                self.base.alive_actors[ernar_name] = True
                self.base.alive_actors[mongol_name] = True

                if self.korlan.korlan:
                    base.player_ref = self.korlan.korlan

        if hasattr(base, "loading_is_done") and base.loading_is_done == 1:
            return task.done

        return task.cont

    def collect_actors_health_task(self, task):
        if hasattr(base, "npc_is_loaded") and base.npc_is_loaded == 1:
            if (self.npc_ernar.actor
                    and self.npc_mongol.actor):
                ernar_name = self.npc_ernar.actor.get_name()
                mongol_name = self.npc_mongol.actor.get_name()

                self.base.npcs_actors_health[ernar_name] = self.npc_ernar.npc_life_label
                self.base.npcs_actors_health[mongol_name] = self.npc_mongol.npc_life_label

                if self.korlan.korlan:
                    base.player_health = self.korlan.korlan_life_perc

        if self.base.game_mode is False and self.base.menu_mode:
            return task.done

        return task.cont

    def npc_focus_switch_task(self, enemies, task):
        if enemies and isinstance(enemies, dict):
            for name in enemies['name']:
                print(self.base.npcs_lbl_np)

                if name == "NPC":
                    if self.base.npcs_lbl_np[name]:
                        self.base.npcs_lbl_np[name].hide()

                        enemy_npc_bs = self.base.get_actor_bullet_shape_node(asset=name, type="NPC")
                        if enemy_npc_bs and not enemy_npc_bs.is_empty():  # is enemy here?
                            vec_x = enemy_npc_bs.get_x()  # get its x vector
                            if base.camera.get_h() == vec_x:
                                if self.base.npcs_lbl_np[name]:
                                    self.base.npcs_lbl_np[name].show()

        if self.base.game_mode is False and self.base.menu_mode:
            return task.done

        return task.cont

    def collect_npcs_label_nodepaths_task(self, enemies, task):
        for name in enemies['name']:
            if name == "NPC":
                if self.npc_ernar.npc_label_np and self.npc_ernar.npc_label_np:
                    if name in self.npc_ernar.npc_label_np.get_name():
                        self.base.npcs_lbl_np[name] = self.npc_ernar.npc_label_np
                    elif name in self.npc_mongol.npc_label_np.get_name():
                        self.base.npcs_lbl_np[name] = self.npc_mongol.npc_label_np

                    return task.done

        return task.cont

    def hitbox_handling_task(self, task):
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
                # is_hips_overlapped = 0
                for node in hitboxes.get_overlapping_nodes():
                    # if is_hips_overlapped == 0:
                    #  continue

                    if (node and node.is_active()
                            and "NPC" in node.get_name()
                            and "RightHand" in node.get_name()):
                        for hit in node.get_overlapping_nodes():
                            if hit and hit.is_active():
                                if ("Player" in hit.get_name()
                                        and "Hips" in hit.get_name()):
                                    # is_hips_overlapped = 1
                                    self.base.npcs_hits[name] = True
                                else:
                                    self.base.npcs_hits[name] = False
                                    # self.base.npcs_hits[name] = hit_zone.get_tag(key=name_hb)

        if self.base.game_mode is False and self.base.menu_mode:
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
                        self.npc_ernar.npc_label_np = None
                        self.npc_ernar.actor.delete()
                        self.npc_ernar.actor.cleanup()
                    if self.npc_mongol.actor:
                        self.npc_mongol.npc_label_np = None
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
                    self.npc_ernar.npc_label_np = None
                    self.npc_ernar.actor.delete()
                    self.npc_ernar.actor.cleanup()
                if self.npc_mongol.actor:
                    self.npc_mongol.npc_label_np = None
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

        # We make any unload_game_scene() method accessible
        # to unload via UnloadingUI.set_parallel_unloading()
        self.base.unload_game_scene = self.unload_game_scene

        self.base.accept("escape", self.pause_game_ui.load_pause_menu)

        taskMgr.add(self.render_attr.set_daytime_clock_task,
                    "set_daytime_clock_task",
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
                                      task="attach")
        self.render_attr.set_lighting(name='dlight',
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
        level_assets = {'name': ['Sky', 'lvl_one', 'Player', 'NPC_Ernar', 'NPC_Mongol'],
                        'type': [None, 'env', 'player', 'npc', 'npc'],
                        'shape': [None, 'auto', 'capsule', 'capsule', 'capsule'],
                        'class': [None, 'env', 'hero', 'friend', 'enemy']
                        }

        for actor in level_assets['name']:
            if "NPC_Ernar" in actor:
                self.npcs_fsm_states[actor] = self.npc_ernar_fsm
            if "NPC_Mongol" in actor:
                self.npcs_fsm_states[actor] = self.npc_mongol_fsm

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
                                              axis=[-25.0, 15.0, self.pos_z],
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
                    extraArgs=[level_assets, self.npcs_fsm_states],
                    appendTask=True)

        taskMgr.add(self.ai.update_ai_world_task,
                    "update_ai_world",
                    appendTask=True)

        taskMgr.add(self.ai.update_npc_states_task,
                    "update_npc_states_task",
                    appendTask=True)

        taskMgr.add(self.world_sfx_task,
                    "world_sfx_task",
                    appendTask=True)

        taskMgr.add(self.collect_actors_health_task,
                    "collect_actors_health_task",
                    appendTask=True)

        taskMgr.add(self.collect_npcs_label_nodepaths_task,
                    "collect_npcs_label_nodepaths_task",
                    extraArgs=[level_assets],
                    appendTask=True)

        taskMgr.add(self.npc_focus_switch_task,
                    "npc_focus_switch_task",
                    extraArgs=[level_assets],
                    appendTask=True)

        taskMgr.add(self.hitbox_handling_task,
                    "hitbox_handling_task",
                    appendTask=True)

    def save_game(self):
        pass

    def load_saved_game(self):
        pass

    def load_free_game(self):
        pass
