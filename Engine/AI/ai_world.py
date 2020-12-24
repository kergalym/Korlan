from direct.gui.OnscreenText import OnscreenText
from direct.interval.IntervalGlobal import Sequence, Func
from direct.task.TaskManagerGlobal import taskMgr
from panda3d.core import Point3

from Engine.FSM.player_fsm import PlayerFSM
from Engine.FSM.npc_fsm import NpcFSM
from Settings.UI.cmd_dialogus_ui import CmdDialogusUI
from Engine.Dialogs import dialogs_multi_lng


class AIWorld:

    def __init__(self):
        self.base = base
        self.player_fsm = PlayerFSM()
        self.npc_fsm = NpcFSM()
        self.dialogus = CmdDialogusUI()
        self.player = None
        self._ai_chars = {}
        self._ai_behaviors = {}
        self._ai_targets = {}
        self._previous_path = {}
        self._previous_heading = {}
        # self.move_sequences = []
        self.npcs_fsm_states = None
        self.npc_classes = {}
        self.near_npc = {}
        self.is_target_reached = {}
        self.npcs_registered_path = {}
        self.npcs_behaviors_seqs = {}
        self.npcs_self_protect_seqs = {}

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

    def add_ai_char(self, actor):
        if actor:
            actor_name = actor.get_name()
            self._ai_chars[actor_name] = actor

    def remove_ai(self, actor_name, ai_name):
        if (actor_name and ai_name
                and isinstance(actor_name, str)
                and isinstance(ai_name, str)):
            if self._ai_behaviors.get(actor_name):
                self._ai_behaviors[actor_name][ai_name] = False
                self._ai_targets[actor_name] = None

    def get_all_behaviors(self):
        if self._ai_behaviors:
            return self._ai_behaviors

    def get_all_ai_chars(self):
        if self._ai_chars:
            return self._ai_chars

    def behavior_sequence(self, passive):
        if isinstance(passive, bool):
            actors = self.get_all_ai_chars()
            if actors and not passive:
                for k, ref in zip(actors, base.npcs_actor_refs):
                    # Get only name without any suffix
                    actor_name = k.split(":")[0]
                    request = self.npcs_fsm_states[actor_name]

                    actor_bs = actors[k]
                    actor_ref = base.npcs_actor_refs[ref]
                    pos = actor_bs.get_pos()
                    posInterval1 = actor_bs.posInterval(13,
                                                        Point3(pos[0], -pos[1], pos[2]),
                                                        startPos=Point3(pos[0], pos[1], pos[2]))
                    posInterval2 = actor_bs.posInterval(13,
                                                        Point3(pos[0], pos[1], pos[2]),
                                                        startPos=Point3(pos[0], -pos[1], pos[2]))
                    hprInterval1 = actor_bs.hprInterval(1,
                                                        Point3(180, 0, 0),
                                                        startHpr=Point3(0, 0, 0))
                    hprInterval2 = actor_bs.hprInterval(1,
                                                        Point3(0, 0, 0),
                                                        startHpr=Point3(180, 0, 0))

                    # Create and play the sequence that coordinates the intervals.
                    actor_seq = Sequence(
                        Func(request.request, "Bow", actor_ref, "archer_standing_draw_arrow_2", "play"),
                        Func(request.request, "Walk", actor_ref, "Walking", "loop"), posInterval1,
                        Func(request.request, "Bow", actor_ref, "archer_standing_draw_arrow_2", "play"),
                        hprInterval1,
                        Func(request.request, "Walk", actor_ref, "Walking", "loop"), posInterval2,
                        Func(request.request, "Bow", actor_ref, "archer_standing_draw_arrow_2", "play"),
                        hprInterval2,
                        name="{0}_seq".format(actor_name))

                    self.npcs_behaviors_seqs[actor_name] = actor_seq
                    self.npcs_behaviors_seqs[actor_name].loop()

    def sequence_once(self, fsm_state, anim):
        for k, ref in zip(self.get_all_ai_chars(), base.npcs_actor_refs):
            actor_name = k.split(":")[0]
            request = self.npcs_fsm_states[actor_name]
            actor_ref = base.npcs_actor_refs[ref]
            actor_seq = Sequence(
                Func(request.request, fsm_state, actor_ref, anim, "play"))
            self.npcs_self_protect_seqs[ref] = actor_seq

    def set_ai_world_task(self, assets, npcs_fsm_states, task):
        """ Function    : set_ai_world_astk

            Description : Enable AI

            Input       : None

            Output      : None

            Return      : None
        """
        self.base.ai_is_active = 0

        if (assets and isinstance(assets, dict)
                and npcs_fsm_states
                and isinstance(npcs_fsm_states, dict)
                and hasattr(base, "npcs_actor_refs")
                and base.npcs_actor_refs
                and not render.find("**/World").is_empty()):
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

                                if actor:
                                    # Do not duplicate if name is exist
                                    if actor.get_name() not in self.npc_fsm.npcs_names:
                                        self.npc_fsm.npcs_names.append(actor.get_name())

                                    self.add_ai_char(actor=actor)

                    self.npc_fsm.get_npcs(actors=base.npcs_actor_refs)
                    self.behavior_sequence(passive=False)
                    self.sequence_once(fsm_state="Bow", anim="archer_standing_draw_arrow_2")

                    taskMgr.add(self.npc_fsm.npc_distance_calculate_task,
                                "npc_distance_calculate_task",
                                extraArgs=[self.player],
                                appendTask=True)

                    taskMgr.add(self.follow_player_task,
                                "follow_player_task",
                                appendTask=True)

                    """taskMgr.add(self.npcs_state_register_task,
                                "hits_and_damages_task",
                                appendTask=True)"""

                    self.base.ai_is_active = 1

                    return task.done

        return task.cont

    def remove_ai_world(self):
        # TODO Reset everything to None or to default state
        pass

    def npcs_state_register_task(self, task):
        # TODO: Use self.npc_fsm.npcs_xyz_vec
        # self.npc_fsm.npcs_xyz_vec
        if self.npcs_behaviors_seqs:
            for k in base.npcs_actor_refs:
                actor = base.npcs_actor_refs[k]
                actor_name = actor.get_name()
                if (self.near_npc.get(actor_name)
                        and actor.get_current_frame("Boxing")
                        and actor.get_current_frame("Boxing") >= 23
                        and actor.get_current_frame("Boxing") <= 25):
                    self.npcs_behaviors_seqs[k].pause()
                    self.npcs_self_protect_seqs[k].play()
                else:
                    self.near_npc[actor_name] = False
                    # self.base.npcs_hits[enemy_npc_ref.get_name()] = True

        if base.game_mode is False and base.menu_mode:
            return task.done

        return task.cont

    def follow_player_task(self, task):
        # Get the time that elapsed since last frame
        dt = globalClock.getDt()
        if (hasattr(self.base, "npcs_xyz_vec")
                and self.base.npcs_xyz_vec):
            for node in self.base.npcs_xyz_vec:
                vec_y = self.base.npcs_xyz_vec[node][1]
                if vec_y != 1.0 or vec_y != -1.0:
                    node.set_y(node, vec_y * (dt * 12))

        if base.game_mode is False and base.menu_mode:
            return task.done

        return task.cont

