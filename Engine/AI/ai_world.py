from direct.gui.OnscreenText import OnscreenText
from direct.interval.MetaInterval import Sequence
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

    def add_ai_char(self, actor):
        if actor:
            actor_name = actor.get_name()
            self._ai_chars[actor_name] = actor

    def set_actor_heading(self, actor, degree):
        if (actor and isinstance(degree, int)
                or isinstance(degree, float)):
            start = Point3(0, 0, 0)
            end = Point3(180, 0, 0)
            return actor.hprInterval(3, end,
                                     startHpr=start)

    def set_path_follow(self, actor, target, rotate):
        if (actor and target and isinstance(rotate, int)
                or isinstance(rotate, float)):
            actor_name = actor.get_name()
            self._ai_behaviors[actor_name] = {'path_follow': True}
            self._ai_targets[actor_name] = target
            dt = globalClock.getDt()

            if self.npc_fsm.npcs_xyz_vec:
                # import pdb; pdb.set_trace()
                # print(target.get_y() + 2, round(actor.get_y(), 1))
                if target.get_y() + 2 == round(actor.get_y(), 1):
                    # Target is reached
                    if rotate == round(actor.get_h()):
                        # self.set_path_follow(actor=actor, target=target, rotate=0)
                        pass
                    else:
                        actor.set_h(actor, rotate * dt)
                else:
                    actor.set_y(actor, 1 * dt)

    def set_evade(self, actor, target):
        if actor and target:
            actor_name = actor.get_name()
            self._ai_behaviors[actor_name] = {'evade': True}
            self._ai_targets[actor_name] = target
            target_vec_y = target.get_y()
            actor_vec_y = actor.get_y()
            start = Point3(0, target_vec_y, 0)
            end = Point3(0, -10, 0)
            return actor.pos_interval(10, end,
                                      startPos=start)

    def set_stealth(self, actor, target):
        if actor and target:
            actor_name = actor.get_name()
            self._ai_behaviors[actor_name] = {'stealth': True}
            self._ai_targets[actor_name] = target

    def remove_ai(self, actor_name, ai_name):
        if (actor_name and ai_name
                and isinstance(actor_name, str)
                and isinstance(ai_name, str)):
            if self._ai_behaviors.get(actor_name):
                self._ai_behaviors[actor_name][ai_name] = False
                self._ai_targets[actor_name] = None

    def get_all_behaviors(self):
        if self._ai_behaviors:
            print(self._ai_behaviors)

    def get_all_ai_chars(self):
        if self._ai_chars:
            print(self._ai_chars)

    def update_npc_states_task(self, task):
        if (self.player
                and hasattr(base, 'npcs_actor_refs')
                and base.npcs_actor_refs):
            for actor_name, fsm_name in zip(base.npcs_actor_refs, self.npcs_fsm_states):
                actor = base.npcs_actor_refs[actor_name]
                request = self.npcs_fsm_states[fsm_name]
                npc_class = self.npc_fsm.set_npc_class(actor=actor,
                                                       npc_classes=self.npc_classes)

                actor = self.base.get_actor_bullet_shape_node(asset=actor_name, type="NPC")
                if "Ernar" in actor.get_name():
                    self.set_path_follow(actor=actor, target=self.player, rotate=90)

                """if npc_class and self.npc_fsm.npcs_xyz_vec:
                    # TODO: Uncomment when I done with enemy
                    if npc_class == "friend":
                        self.npc_friend_logic(actor=actor, request=request, passive=False)
                    if npc_class == "neutral":
                        self.npc_neutral_logic(actor=actor, request=request, passive=True)
                    if npc_class == "enemy":
                        self.npc_enemy_logic(actor=actor, request=request, passive=False)"""

                # print(self.npc_fsm.npcs_xyz_vec, {self.player.get_name(): round(self.player.get_y(), 1)})

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

    def set_ai_world(self, assets, npcs_fsm_states, task):
        """ Function    : set_ai_world

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

                    taskMgr.add(self.npc_fsm.npc_distance_calculate_task,
                                "npc_distance_calculate_task",
                                extraArgs=[self.player],
                                appendTask=True)

                    self.base.ai_is_active = 1

                    return task.done

        return task.cont

    def remove_ai_world(self):
        # TODO Reset everything to None or to default state
        pass

    def npc_friend_logic(self, actor, request, passive):
        if (actor and request and self.npc_fsm.npcs_xyz_vec
                and isinstance(passive, bool)
                and isinstance(self.npc_fsm.npcs_xyz_vec, dict)):

            # Add :BS suffix since we'll get Bullet Shape NodePath here
            actor_bs_name = "{0}:BS".format(actor.get_name())
            actor_name = actor.get_name()
            actor_npc_bs = self.base.get_actor_bullet_shape_node(asset=actor_name, type="NPC")

            # actor.set_blend(frameBlend=True)

            vec_x = None
            if self.npc_fsm.npcs_xyz_vec.get(actor_bs_name):
                vec_x = self.npc_fsm.npcs_xyz_vec[actor_bs_name][0]

            if passive:
                # Just stay
                request.request("Idle", actor, "LookingAround", "loop")

            if passive is False:
                # Get required data about enemy to deal with it
                enemy_npc_ref = None
                for k in base.npcs_actor_refs:
                    if actor.get_name() not in k:
                        enemy_npc_ref = base.npcs_actor_refs[k]

                enemy_fsm_request = None
                for fsm_name in self.npcs_fsm_states:
                    if actor.get_name() not in fsm_name:
                        enemy_fsm_request = self.npcs_fsm_states[fsm_name]

                if enemy_npc_ref and enemy_fsm_request:
                    enemy_npc_ref_name = enemy_npc_ref.get_name()
                    enemy_npc_bs = self.base.get_actor_bullet_shape_node(asset=enemy_npc_ref_name, type="NPC")

                    # If NPC is far from enemy, do pursue enemy
                    if (self.ai_behaviors[actor_name].behavior_status("pursue") == "disabled"
                            or self.ai_behaviors[actor_name].behavior_status("pursue") == "active"):
                        request.request("Walk", actor, enemy_npc_bs, None,
                                        "", "Walking", None, "loop")

                    # If NPC is close to Enemy, do enemy attack
                    if (self.ai_behaviors[actor_name].behavior_status("pursue") == "done"
                            or self.ai_behaviors[actor_name].behavior_status("pursue") == "paused"):
                        request.request("Idle", actor, "LookingAround", "loop")

                        # Friendly NPC starts attacking the opponent when player first starts attacking it
                        if self.base.player_ref.get_current_frame("Boxing"):
                            request.request("Attack", actor, "Boxing", "play")
                            if (actor.get_current_frame("Boxing") >= 23
                                    and actor.get_current_frame("Boxing") <= 25):
                                self.base.npcs_hits[enemy_npc_ref.get_name()] = True
                                enemy_fsm_request.request("Attacked", enemy_npc_ref, "BigHitToHead", "Boxing", "play")

                            # NPC is attacked by enemy!
                            if (enemy_npc_ref.get_current_frame("Boxing")
                                    and enemy_npc_ref.get_current_frame("Boxing") >= 23
                                    and enemy_npc_ref.get_current_frame("Boxing") <= 25):
                                self.base.npcs_hits[actor_name] = True
                                if actor:
                                    request.request("Attacked", actor, "BigHitToHead", "Boxing", "play")

    def npc_neutral_logic(self, actor, request, passive):
        if (actor and request and self.npc_fsm.npcs_xyz_vec
                and isinstance(passive, bool)
                and isinstance(self.npc_fsm.npcs_xyz_vec, dict)):
            # Add :BS suffix since we'll get Bullet Shape NodePath here
            # actor_bs_name = "{0}:BS".format(actor.get_name())
            actor_name = actor.get_name()
            # actor.set_blend(frameBlend=True)

            # Leave it here for debugging purposes
            # self.get_npc_hits()

            # if self.npc_fsm.npcs_xyz_vec.get(actor_bs_name):
            # vec_x = self.npc_fsm.npcs_xyz_vec[actor_bs_name][0]

            if passive:
                # Just stay
                request.request("Idle", actor, "LookingAround", "loop")

            elif passive is False:
                # If NPC is far from Player, do pursue Player
                if (self.ai_behaviors[actor_name].behavior_status("pursue") == "disabled"
                        or self.ai_behaviors[actor_name].behavior_status("pursue") == "active"):
                    request.request("Walk", actor, self.player, None,
                                    "", "Walking", None, "loop")

                    # If NPC is close to Player, just stay
                    if self.ai_behaviors[actor_name].behavior_status("pursue") == "done":
                        # TODO: Change action to something more suitable
                        request.request("Idle", actor, "LookingAround", "loop")

    def npc_enemy_logic(self, actor, request, passive):
        if (actor and request and self.npc_fsm.npcs_xyz_vec
                and isinstance(passive, bool)
                and isinstance(self.npc_fsm.npcs_xyz_vec, dict)
                and hasattr(self.base, "alive_actors")
                and self.base.alive_actors):
            # Add :BS suffix since we'll get Bullet Shape NodePath here
            actor_bs_name = "{0}:BS".format(actor.get_name())
            actor_name = actor.get_name()
            actor_npc_bs = self.base.get_actor_bullet_shape_node(asset=actor_name, type="NPC")

            # actor.set_blend(frameBlend=True)

            # Leave it here for debugging purposes
            # self.get_npc_hits()

            vec_x = None
            if self.npc_fsm.npcs_xyz_vec.get(actor_bs_name):
                vec_x = self.npc_fsm.npcs_xyz_vec[actor_bs_name][0]

            # Just stay
            if passive and self.base.alive_actors[actor_name]:
                request.request("Idle", actor, "LookingAround", "loop")

            elif passive is False and self.base.alive_actors[actor_name]:
                # Get required data about enemy to deal with it
                enemy_npc_ref = None
                for k in base.npcs_actor_refs:
                    if actor.get_name() not in k:
                        if self.base.npcs_hits.get(k):
                            enemy_npc_ref = base.npcs_actor_refs[k]

                enemy_fsm_request = None
                for fsm_name in self.npcs_fsm_states:
                    if actor.get_name() not in fsm_name:
                        if self.base.npcs_hits.get(fsm_name):
                            enemy_fsm_request = self.npcs_fsm_states[fsm_name]

                enemy_npc_bs = None
                if enemy_npc_ref and enemy_fsm_request:
                    enemy_npc_ref_name = enemy_npc_ref.get_name()
                    enemy_npc_bs = self.base.get_actor_bullet_shape_node(asset=enemy_npc_ref_name, type="NPC")

                # print(self.base.npcs_hits)

                # If NPC is far from Player/NPC, do pursue Player/NPC
                if (self.ai_behaviors[actor_name].behavior_status("pursue") == "disabled"
                        or self.ai_behaviors[actor_name].behavior_status("pursue") == "active"):
                    if self.base.npcs_hits.get(actor_name):
                        request.request("Walk", actor, None, None,
                                        "", "Walking", None, "loop")
                    if not self.base.npcs_hits.get(actor_name):
                        request.request("Walk", actor, None, None,
                                        "", "Walking", None, "loop")

                # If NPC is close to Player/NPC, do enemy attack
                if self.ai_behaviors[actor_name].behavior_status("pursue") == "done":
                    if enemy_npc_ref:
                        self.near_npc[actor_name] = True
                        if hasattr(self.base, 'npcs_active_actions'):
                            self.base.npcs_active_actions[enemy_npc_ref.get_name()] = None
                            self.base.npcs_active_actions[actor_name] = "Boxing"
                        request.request("Attack", actor, "Boxing", "loop")
                    else:
                        self.near_npc[actor_name] = True
                        if hasattr(self.base, 'npcs_active_actions'):
                            self.base.npcs_active_actions[self.base.player_ref.get_name()] = None
                            self.base.npcs_active_actions[actor_name] = "Boxing"
                        request.request("Attack", actor, "Boxing", "loop")

                    # Player/NPC is attacked by enemy!
                    if (actor.get_current_frame("Boxing") >= 23
                            and actor.get_current_frame("Boxing") <= 25):
                        if enemy_npc_ref:
                            self.base.npcs_hits[enemy_npc_ref.get_name()] = True
                            self.player_fsm.request("Attacked", enemy_npc_ref, "BigHitToHead", "play")

                    if (actor.get_current_frame("Boxing") >= 23
                            and actor.get_current_frame("Boxing") <= 25
                            and self.base.player_states["is_blocking"] is False):
                        if not enemy_npc_ref:
                            for k in self.base.npcs_hits:
                                self.base.npcs_hits[k] = False
                            self.player_fsm.request("Attacked", self.base.player_ref, "BigHitToHead", "play")

                    # Enemy is attacked by player!
                    if (self.base.player_states["is_hitting"]
                            and self.base.alive_actors[actor_name]):
                        if (self.base.player_ref.get_current_frame("Boxing") >= 23
                                and self.base.player_ref.get_current_frame("Boxing") <= 25):
                            # Enemy does a block
                            request.request("Block", actor, "center_blocking", "Boxing", "play")

                        # Enemy health decreased when enemy miss a hits
                        if (actor.get_current_frame("center_blocking")
                                and actor.get_current_frame("center_blocking") == 1):
                            if hasattr(base, "npcs_actors_health") and base.npcs_actors_health:
                                if base.npcs_actors_health[actor_name].getPercent() != 0:
                                    base.npcs_actors_health[actor_name]['value'] -= 5
                            request.request("Attacked", actor, "BigHitToHead", "Boxing", "play")

                        # Temporary thing, leave it here
                        if (hasattr(base, "npcs_actors_health")
                                and base.npcs_actors_health):
                            value = base.npcs_actors_health[actor_name]['value']
                            self.dbg_text_npc_frame_hit.setText(str(value) + actor_name)

                        # Enemy will die if no health or flee:
                        if (hasattr(base, "npcs_actors_health")
                                and base.npcs_actors_health):
                            if base.npcs_actors_health[actor_name].getPercent() != 0:
                                # Evade or attack the player
                                if base.npcs_actors_health[actor_name].getPercent() == 50.0:
                                    self.near_npc[actor_name] = False
                                    self.ai_behaviors[actor_name].remove_ai("pursue")
                                    request.request("Walk", actor, None, None,
                                                    "evader", "Walking", None, "loop")
                                pass
                            else:
                                request.request("Death", actor, "Dying", "play")
                                self.base.alive_actors[actor_name] = False
                                self.ai_behaviors[actor_name].pause_ai("pursue")
                                self.near_npc[actor_name] = False

                    # Enemy is attacked by opponent!
                    if enemy_npc_ref and not self.base.player_states["is_hitting"]:
                        request.request("Attack", actor, "Boxing", "play")
                        if (actor.get_current_frame("Boxing") >= 23
                                and actor.get_current_frame("Boxing") <= 25):
                            if enemy_npc_ref:
                                self.base.npcs_hits[enemy_npc_ref.get_name()] = True
                                enemy_fsm_request.request("Attacked", enemy_npc_ref, "BigHitToHead", "Boxing", "play")

                            # Enemy does a block
                            request.request("Block", actor, "center_blocking", "Boxing", "play")

                        # Enemy health decreased when enemy miss a hits
                        if (actor.get_current_frame("center_blocking")
                                and actor.get_current_frame("center_blocking") == 1):
                            if hasattr(base, "npcs_actors_health") and base.npcs_actors_health:
                                if base.npcs_actors_health[actor_name].getPercent() != 0:
                                    base.npcs_actors_health[actor_name]['value'] -= 5
                            request.request("Attacked", actor, "BigHitToHead", "Boxing", "play")

                        # Enemy will die if no health or flee:
                        if (hasattr(base, "npcs_actors_health")
                                and base.npcs_actors_health):
                            if base.npcs_actors_health[actor_name].getPercent() != 0:
                                # Evade or attack the player
                                if base.npcs_actors_health[actor_name].getPercent() == 50.0:
                                    self.near_npc[actor_name] = False
                                    self.ai_behaviors[actor_name].remove_ai("pursue")
                                    request.request("Walk", actor, None, None,
                                                    "evader", "Walking", None, "loop")
                                pass
                            else:
                                request.request("Death", actor, "Dying", "play")
                                self.base.alive_actors[actor_name] = False
                                self.ai_behaviors[actor_name].pause_ai("pursue")
                                self.near_npc[actor_name] = False

                # Enemy returns back
                if base.npcs_actors_health[actor_name]:
                    if (base.npcs_actors_health[actor_name].getPercent() == 50.0
                            and vec_x == 10.0 or vec_x == -10.0
                            and self.ai_behaviors[actor_name].behavior_status("evade") == "paused"):
                        self.ai_behaviors[actor_name].remove_ai("evade")
                        # TODO: Change action to something more suitable
                        request.request("Idle", actor, "LookingAround", "loop")
