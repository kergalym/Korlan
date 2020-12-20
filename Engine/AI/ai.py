from direct.gui.OnscreenText import OnscreenText
from panda3d.ai import AIWorld
from panda3d.ai import AICharacter
from direct.task.TaskManagerGlobal import taskMgr
from panda3d.core import LVecBase3f

from Engine.FSM.player_fsm import PlayerFSM
from Engine.FSM.npc_fsm import NpcFSM
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
        self.npc_classes = {}
        self.ai_behaviors = {}
        self.npcs_fsm_states = None
        self.ai_char = None
        self.ai_chars = {}
        self.player = None
        self.dialogus = CmdDialogusUI()
        self.near_npc = {}

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

    def set_actor_heading(self, actor, opponent, dt):
        if actor and opponent and dt:
            vec_h = 2 * actor.get_h() - opponent.get_h()
            actor.set_h(actor, vec_h * dt)

    def set_actor_heading_once(self, actor, degree, dt):
        if actor and degree and dt:
            if actor.get_h() - degree != actor.get_h():
                actor.set_h(actor, degree * dt)

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
                    # TODO: Uncomment when I done with enemy
                    if npc_class == "friend":
                        self.npc_friend_logic(actor=actor, request=request, passive=False)
                    if npc_class == "neutral":
                        self.npc_neutral_logic(actor=actor, request=request, passive=True)
                    if npc_class == "enemy":
                        self.npc_enemy_logic(actor=actor, request=request, passive=False)

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
                and base.npcs_actor_refs):
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
                                    speed = 6

                                    # Do not duplicate if name is exist
                                    if actor.get_name() not in self.npc_fsm.npcs_names:
                                        self.npc_fsm.npcs_names.append(actor.get_name())

                                    self.ai_char = AICharacter(actor_cls, actor, 100, 0.05, speed)
                                    self.ai_world.add_ai_char(self.ai_char)

                                    child_name = actor.get_child(0).get_name()
                                    self.ai_chars[child_name] = self.ai_char
                                    self.ai_behaviors[child_name] = self.ai_char.get_ai_behaviors()

                    taskMgr.add(self.npc_fsm.npc_distance_calculate_task,
                                "npc_distance_calculate_task",
                                extraArgs=[self.player],
                                appendTask=True)

                    self.base.ai_is_active = 1

                    return task.done

        return task.cont

    def npc_friend_logic(self, actor, request, passive):
        if (actor and request and self.npc_fsm.npcs_xyz_vec
                and isinstance(passive, bool)
                and isinstance(self.npc_fsm.npcs_xyz_vec, dict)):

            # Get the time that elapsed since last frame
            dt = globalClock.getDt()

            vect = {"panic_dist": 5,
                    "relax_dist": 5,
                    "wander_radius": 5,
                    "plane_flag": 0,
                    "area_of_effect": 10}

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
                        request.request("Walk", actor, enemy_npc_bs,
                                        self.ai_behaviors[actor_name],
                                        "pursuer", "Walking", vect, "loop")

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
            vect = {"panic_dist": 5,
                    "relax_dist": 5,
                    "wander_radius": 5,
                    "plane_flag": 0,
                    "area_of_effect": 10}

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
                    request.request("Walk", actor, self.player, self.ai_behaviors[actor_name],
                                    "pursuer", "Walking", vect, "loop")

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

            # Get the time that elapsed since last frame
            dt = globalClock.getDt()

            vect = {"panic_dist": 5,
                    "relax_dist": 5,
                    "wander_radius": 5,
                    "plane_flag": 0,
                    "area_of_effect": 10}

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
                if self.ai_behaviors.get(actor_name):
                    if (self.ai_behaviors[actor_name].behavior_status("pursue") == "disabled"
                            or self.ai_behaviors[actor_name].behavior_status("pursue") == "active"):
                        if self.base.npcs_hits.get(actor_name):
                            request.request("Walk", actor, enemy_npc_bs, self.ai_behaviors[actor_name],
                                            "pursuer", "Walking", vect, "loop")
                        if not self.base.npcs_hits.get(actor_name):
                            request.request("Walk", actor, self.player, self.ai_behaviors[actor_name],
                                            "pursuer", "Walking", vect, "loop")

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
                            """if (hasattr(base, "npcs_actors_health")
                                    and base.npcs_actors_health):
                                value = base.npcs_actors_health[actor_name]['value']
                                self.dbg_text_npc_frame_hit.setText(str(value) + actor_name)"""

                            # Enemy will die if no health or flee:
                            if (hasattr(base, "npcs_actors_health")
                                    and base.npcs_actors_health):
                                if base.npcs_actors_health[actor_name].getPercent() != 0:
                                    # Evade or attack the player
                                    if base.npcs_actors_health[actor_name].getPercent() == 50.0:
                                        self.near_npc[actor_name] = False
                                        self.ai_behaviors[actor_name].remove_ai("pursue")
                                        request.request("Walk", actor, self.player, self.ai_behaviors[actor_name],
                                                        "evader", "Walking", vect, "loop")
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
                                        request.request("Walk", actor, enemy_npc_bs, self.ai_behaviors[actor_name],
                                                        "evader", "Walking", vect, "loop")
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
