from panda3d.ai import AIWorld
from panda3d.ai import AICharacter
from direct.task.TaskManagerGlobal import taskMgr

from Engine.FSM.player_fsm import PlayerFSM
from Engine.AI.npc_ai_logic import NpcAILogic
from Settings.UI.cmd_dialogus_ui import CmdDialogusUI
from Engine.Dialogs import dialogs_multi_lng


class AI:
    def __init__(self, world):
        self.base = base
        self.render = render
        self.taskMgr = taskMgr
        self.ai_world = AIWorld(world)
        self.base.game_instance['ai_world_np'] = self.ai_world
        self.player_fsm = PlayerFSM()
        self.npc_classes = {}
        self.ai_behaviors = {}
        self.npcs_fsm_states = None
        self.ai_char = None
        self.ai_chars = {}
        self.ai_chars_bs = {}
        self.player = None
        self.dialogus = CmdDialogusUI()
        self.near_npc = {}
        self.npcs_names = []
        self.npcs_xyz_vec = {}
        self.navmeshes = self.base.navmesh_collector()

    def update_ai_world_task(self, task):
        if self.ai_world:
            # Oh... Workaround for evil assertion error, again!
            try:
                self.ai_world.update()
            except AssertionError:
                # self.ai_world.update()
                pass
        return task.cont

    def set_ai_world(self, assets, npcs_fsm_states, lvl_name):
        """ Function    : set_ai_world

            Description : Enable AI

            Input       : None

            Output      : None

            Return      : None
        """
        self.base.game_instance['ai_is_activated'] = 0

        taskMgr.add(self.set_ai_world_task,
                    "set_ai_world_task",
                    extraArgs=[assets, npcs_fsm_states, lvl_name],
                    appendTask=True)

    def set_ai_world_task(self, assets, npcs_fsm_states, lvl_name, task):
        """ Function    : set_ai_world_task

            Description : Enable AI Task

            Input       : None

            Output      : None

            Return      : None
        """
        if (self.base.game_instance['actors_are_loaded']
                and self.base.game_instance['physics_is_activated'] == 1
                and self.base.game_instance['ai_is_activated'] == 0):
            if (assets and isinstance(assets, dict)
                    and npcs_fsm_states
                    and isinstance(npcs_fsm_states, dict)
                    and self.base.game_instance['actors_ref']
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

                    if self.player and self.ai_world:
                        for actor_cls in assets["class"]:
                            if actor_cls:
                                if "env" in actor_cls:
                                    continue
                                elif "hero" in actor_cls:
                                    continue

                                for ref_name in self.base.game_instance['actors_ref']:
                                    if "NPC" in ref_name:
                                        actor = self.base.get_actor_bullet_shape_node(asset=ref_name, type="NPC")
                                        self.ai_chars_bs[ref_name] = actor

                                    if actor:
                                        speed = 6

                                        # Do not duplicate if name is exist
                                        if actor.get_name() not in self.npcs_names:
                                            self.npcs_names.append(actor.get_name())

                                        self.ai_char = AICharacter(actor_cls, actor, 100, 0.05, speed)

                                        child_name = actor.get_child(0).get_name()
                                        self.ai_chars[child_name] = self.ai_char

                                        self.ai_world.add_ai_char(self.ai_char)

                                        self.ai_behaviors[child_name] = self.ai_char.get_ai_behaviors()
                                        self.ai_behaviors[child_name].init_path_find(self.navmeshes[lvl_name])

                                        for i in render.findAllMatches("**/World/*:BS"):
                                            if not render.find("**/World/*:BS").is_empty():
                                                node = render.find("**/World/*:BS")
                                                if "NPC" not in node.get_name():
                                                    self.ai_behaviors[child_name].add_static_obstacle(node)

                        taskMgr.add(self.update_ai_world_task,
                                    "update_ai_world",
                                    appendTask=True)

                        self.base.game_instance['ai_is_activated'] = 1

                        # Start NPC Logics
                        NpcAILogic(self.ai_world, self.ai_behaviors, self.ai_chars, self.ai_chars_bs, self.player,
                                   self.player_fsm, self.npcs_fsm_states, self.npc_classes)

                        return task.done

        return task.cont


