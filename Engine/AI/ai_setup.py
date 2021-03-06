from direct.gui.OnscreenText import OnscreenText
from panda3d.ai import AIWorld
from panda3d.ai import AICharacter
from direct.task.TaskManagerGlobal import taskMgr

from Engine.FSM.player_fsm import PlayerFSM
from Engine.FSM.npc_fsm import NpcFSM
from Engine.AI.npcs_ai import NpcsAI
from Settings.UI.cmd_dialogus_ui import CmdDialogusUI
from Engine.Dialogs import dialogs_multi_lng


class AI:
    def __init__(self):
        self.base = base
        self.render = render
        self.taskMgr = taskMgr
        self.ai_world = AIWorld(render)
        self.player_fsm = PlayerFSM()
        self.npc_fsm = NpcFSM()
        self.npc_ai = NpcsAI()
        self.npc_classes = {}
        self.ai_behaviors = {}
        self.npcs_fsm_states = None
        self.ai_char = None
        self.ai_chars = {}
        self.base.ai_chars_bs = {}
        self.player = None
        self.dialogus = CmdDialogusUI()
        self.near_npc = {}
        self.navmeshes = self.base.navmesh_collector()

        self.dbg_text_npc_frame_hit = OnscreenText(text="",
                                                   pos=(0.5, 0.0),
                                                   scale=0.2,
                                                   fg=(255, 255, 255, 0.9),
                                                   mayChange=True)

        self.dbg_text_plr_frame_hit = OnscreenText(text="",
                                                   pos=(0.5, -0.2),
                                                   scale=0.2,
                                                   fg=(255, 255, 255, 1.1),
                                                   mayChange=True)
        self.integer = 0

    def keep_actor_pitch_task(self, task):
        # Fix me: Dirty hack for path finding issue
        # when actor's pitch changes for reasons unknown for me xD
        if hasattr(self.base, "npcs_actor_refs") and base.npcs_actor_refs:
            for actor in base.npcs_actor_refs:
                if not base.npcs_actor_refs[actor].is_empty():
                    # Prevent pitch changing
                    base.npcs_actor_refs[actor].set_p(0)
                    base.npcs_actor_refs[actor].get_parent().set_p(0)

        if self.base.game_mode is False and self.base.menu_mode:
            return task.done

        return task.cont

    def set_actor_heading(self, actor, opponent, dt):
        if actor and opponent and dt:
            vec_h = 2 * actor.get_h() - opponent.get_h()
            actor.set_h(actor, vec_h * dt)

    def set_actor_heading_once(self, actor, degree, dt):
        if actor and degree and dt:
            if actor.get_h() - degree != actor.get_h():
                actor.set_h(actor, degree * dt)

    def update_pathfinding_task(self, task):
        if self.base.ai_chars_bs and self.ai_world and self.ai_behaviors:
            for actor_name in self.ai_behaviors:
                self.ai_chars[actor_name].set_max_force(7)

                for name in self.base.ai_chars_bs:
                    # Add actors as obstacles except actor that avoids them
                    if name != actor_name:
                        ai_char_bs = self.base.ai_chars_bs[name]
                        if ai_char_bs:
                            self.ai_behaviors[actor_name].path_find_to(ai_char_bs, "addPath")
                            # self.ai_behaviors[actor_name].add_dynamic_obstacle(ai_char_bs)

                            # Obstacle avoidance behavior
                            # self.ai_behaviors[actor_name].obstacle_avoidance(1.0)
                            # self.ai_world.add_obstacle(ai_char_bs)

            return task.done

        if self.base.game_mode is False and self.base.menu_mode:
            return task.done

    def update_ai_world_task(self, task):
        if self.ai_world:
            # Oh... Workaround for evil assertion error, again!
            try:
                self.ai_world.update()
            except AssertionError:
                # self.ai_world.update()
                pass

            # Debug: delete soon
            # self.ai_world.print_list()

        if base.game_mode is False and base.menu_mode:
            return task.done

        return task.cont

    def update_npc_states_task(self, task):
        if (self.player
                and hasattr(base, 'npcs_actor_refs')
                and base.npcs_actor_refs):
            for actor_name, fsm_name in zip(base.npcs_actor_refs, self.npcs_fsm_states):
                actor = base.npcs_actor_refs[actor_name]
                request = self.npcs_fsm_states[fsm_name]
                npc_class = self.npc_fsm.set_npc_class(actor=actor,
                                                       npc_classes=self.npc_classes)

                if npc_class and self.npc_fsm.npcs_xyz_vec:
                    if npc_class == "friend":
                        self.npc_ai.npc_friend_logic(actor=actor,
                                                     player=self.player,
                                                     player_fsm=self.player_fsm,
                                                     request=request,
                                                     ai_behaviors=self.ai_behaviors,
                                                     npcs_xyz_vec=self.npc_fsm.npcs_xyz_vec,
                                                     npcs_fsm_states=self.npcs_fsm_states,
                                                     near_npc=self.near_npc,
                                                     passive=False)
                    if npc_class == "neutral":
                        self.npc_ai.npc_neutral_logic(actor=actor,
                                                      player=self.player,
                                                      player_fsm=self.player_fsm,
                                                      request=request,
                                                      ai_behaviors=self.ai_behaviors,
                                                      npcs_xyz_vec=self.npc_fsm.npcs_xyz_vec,
                                                      npcs_fsm_states=self.npcs_fsm_states,
                                                      near_npc=self.near_npc,
                                                      passive=True)
                    if npc_class == "enemy":
                        self.npc_ai.npc_enemy_logic(actor=actor,
                                                    player=self.player,
                                                    player_fsm=self.player_fsm,
                                                    request=request,
                                                    ai_behaviors=self.ai_behaviors,
                                                    npcs_xyz_vec=self.npc_fsm.npcs_xyz_vec,
                                                    npcs_fsm_states=self.npcs_fsm_states,
                                                    near_npc=self.near_npc,
                                                    passive=False)

        if base.game_mode is False and base.menu_mode:
            return task.done

        return task.cont

    def set_weather(self, weather):
        if weather and isinstance(weather, str):
            if weather == "wind":
                pass
            elif weather == "rain":
                pass
            elif weather == "storm":
                pass
            elif weather == "day":
                pass
            elif weather == "night":
                pass

    def set_ai_world_task(self, assets, npcs_fsm_states, lvl_name, task):
        """ Function    : set_ai_world_task

            Description : Enable AI Task

            Input       : None

            Output      : None

            Return      : None
        """
        if hasattr(base, "physics_is_active") and self.base.physics_is_active == 1:
            if (assets and isinstance(assets, dict)
                    and npcs_fsm_states
                    and isinstance(npcs_fsm_states, dict)
                    and hasattr(base, "npcs_actor_refs")
                    and base.npcs_actor_refs
                    and lvl_name and isinstance(lvl_name, str)):
                self.npcs_fsm_states = npcs_fsm_states

                for npc in npcs_fsm_states:
                    if npcs_fsm_states.get(npc):
                        npcs_fsm_states[npc].state = "Off"

                if assets.get("name") and assets.get("class"):
                    actor = None

                    for name, cls in zip(assets.get("name"), assets.get("class")):
                        if cls:
                            if "env" in cls:
                                continue
                            elif "hero" in cls:
                                continue
                            self.npc_classes[name] = cls

                    self.player = self.base.get_actor_bullet_shape_node(asset="Player", type="Player")

                    if self.player:
                        for actor_cls in assets["class"]:
                            if actor_cls:
                                if "env" in actor_cls:
                                    continue
                                elif "hero" in actor_cls:
                                    continue

                                for ref_name in base.npcs_actor_refs:
                                    if "NPC" in ref_name:
                                        actor = self.base.get_actor_bullet_shape_node(asset=ref_name, type="NPC")
                                        self.base.ai_chars_bs[ref_name] = actor

                                    if actor:
                                        speed = 6

                                        # Do not duplicate if name is exist
                                        if actor.get_name() not in self.npc_fsm.npcs_names:
                                            self.npc_fsm.npcs_names.append(actor.get_name())

                                        self.ai_char = AICharacter(actor_cls, actor, 100, 0.05, speed)
                                        self.ai_world.add_ai_char(self.ai_char)

                                        child_name = actor.get_child(0).get_name()
                                        self.ai_chars[child_name] = self.ai_char
                                        self.ai_behaviors[child_name] = self.ai_char.get_ai_behaviors()
                                        self.ai_behaviors[child_name].init_path_find(self.navmeshes[lvl_name])

                                        for i in render.findAllMatches("**/*:BS"):
                                            if not render.find("**/*:BS").is_empty():
                                                node = render.find("**/*:BS")
                                                if "NPC" not in node.get_name():
                                                    self.ai_behaviors[child_name].add_static_obstacle(node)

                        self.npc_fsm.get_npcs(actors=base.npcs_actor_refs)

                        taskMgr.add(self.update_ai_world_task,
                                    "update_ai_world",
                                    appendTask=True)

                        taskMgr.add(self.keep_actor_pitch_task,
                                    "keep_actor_pitch_task",
                                    appendTask=True)

                        """taskMgr.add(self.update_pathfinding_task,
                                    "update_pathfinding_task",
                                    appendTask=True)"""

                        taskMgr.add(self.update_npc_states_task,
                                    "update_npc_states_task",
                                    appendTask=True)

                        taskMgr.add(self.npc_fsm.npc_distance_calculate_task,
                                    "npc_distance_calculate_task",
                                    extraArgs=[self.player],
                                    appendTask=True)

                        return task.done

        return task.cont

    def set_ai_world(self, assets, npcs_fsm_states, lvl_name):
        """ Function    : set_ai_world

            Description : Enable AI

            Input       : None

            Output      : None

            Return      : None
        """
        self.base.ai_is_active = 0

        taskMgr.add(self.set_ai_world_task,
                    "set_ai_world_task",
                    extraArgs=[assets, npcs_fsm_states, lvl_name],
                    appendTask=True)

        self.base.ai_is_active = 1
