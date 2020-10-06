from panda3d.ai import AIWorld
from panda3d.ai import AICharacter
from direct.task.TaskManagerGlobal import taskMgr
from Engine.FSM.player_fsm import PlayerFSM
from Engine.FSM.npc_fsm import NpcFSM


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
        self.player = None
        self.npcs_hits = {
            'great_sword_kick': 0,
            'great_sword_slash_3': 0,
            'great_sword_slash_2': 0,
            'Kicking': 0,
            'great_sword_slash_4': 0,
            'BigHitToHead': 0,
            'Kicking_4': 0,
            'great_sword_slash_5': 0,
            'great_sword_kick_fix': 0,
            'great_sword_slash_fixed': 0,
            'great_sword_kick_2': 0,
            'Kicking_5': 0,
            'Kicking_3': 0,
            'Boxing': 23,
            'PunchToElbowCombo': 0,
            'HitToBody': 0,
            'great_sword_slash': 0,
            'KickingAtThePlace': 0
        }

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

    def get_npc_hits(self):
        anims = self.base.asset_animations_collector()[0]
        hits = {}

        if anims:
            for anim in anims:
                if ("Hit" in anim
                        or "Punch" in anim
                        or "Boxing" in anim
                        or "Kicking" in anim
                        or "Kick" in anim
                        or "kick" in anim
                        or "slash" in anim):
                    hits[anim] = 0

        if hits:
            return hits

    def set_actor_accurate_heading(self, master_name, slave):
        # Oops, these words are not SJW-approved
        if master_name and slave and isinstance(master_name, str):
            master = render.find("**/{0}".format(master_name))
            master_heading = master.get_h()
            if not master.is_empty():
                if master_heading > 0:
                    slave.set_h(-master_heading)
                elif master_heading < 0:
                    slave.set_h(master_heading)

    def set_ai_world(self, assets, npcs_fsm_states, task):
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

                                if actor and self.player:
                                    speed = 6

                                    # Do not duplicate if name is exist
                                    if actor.get_name() not in self.npc_fsm.npcs_names:
                                        self.npc_fsm.npcs_names.append(actor.get_name())

                                    self.ai_char = AICharacter(actor_cls, actor, 100, 0.05, speed)
                                    self.ai_world.add_ai_char(self.ai_char)

                                    child_name = actor.get_child(0).get_name()
                                    self.ai_behaviors[child_name] = self.ai_char.get_ai_behaviors()

                    taskMgr.add(self.npc_fsm.npc_distance_calculate_task,
                                "npc_distance_calculate_task",
                                extraArgs=[self.player],
                                appendTask=True)
                    return task.done

        return task.cont

    def npc_friend_logic(self, actor, request, passive):
        if (actor and request and self.npc_fsm.npcs_xyz_vec
                and isinstance(passive, bool)
                and isinstance(self.npc_fsm.npcs_xyz_vec, dict)):

            # Add :BS suffix since we'll get Bullet Shape NodePath here
            actor_bs_name = "{0}:BS".format(actor.get_name())

            if actor_bs_name and self.npc_fsm.npcs_xyz_vec.get(actor_bs_name):
                vec_x = self.npc_fsm.npcs_xyz_vec[actor_bs_name][0]

                if passive:
                    # Just stay
                    # TODO: Change action to something more suitable
                    # request.request("Idle", actor, "LookingAround", "loop")

                    # If NPC is far from Player, do pursue player
                    if vec_x > 1.0 or vec_x < -1.0:
                        request.request("Walk", actor, self.player,
                                        self.ai_behaviors[actor.get_name()],
                                        "pursuer", "Walking", "loop")

                    # If NPC is close to Player, just stay
                    if self.ai_behaviors[actor.get_name()].behavior_status("pursue") == "done":
                        # TODO: Change action to something more suitable
                        request.request("Idle", actor, "LookingAround", "loop")

                if passive is False:
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
                        if vec_x > 1.0 or vec_x < -1.0:
                            request.request("Walk", actor, enemy_npc_bs,
                                            self.ai_behaviors[actor.get_name()],
                                            "pursuer", "Walking", "loop")

                        # If NPC is close to Enemy, do enemy attack
                        if self.ai_behaviors[actor.get_name()].behavior_status("pursue") == "done":

                            # Head the enemy for NPC
                            self.set_actor_accurate_heading(master_name=actor_bs_name,
                                                            slave=enemy_npc_bs)
                            request.request("Attack", actor, "Boxing", "loop")

                            # Enemy is attacked!
                            if actor.get_current_frame("Boxing") == self.npcs_hits["Boxing"]:
                                enemy_fsm_request.request("Attacked", enemy_npc_ref, "BigHitToHead", "play")

    def npc_neutral_logic(self, actor, request, passive):
        if (actor and request and self.npc_fsm.npcs_xyz_vec
                and isinstance(passive, bool)
                and isinstance(self.npc_fsm.npcs_xyz_vec, dict)):

            # Add :BS suffix since we'll get Bullet Shape NodePath here
            actor_bs_name = "{0}:BS".format(actor.get_name())

            # Leave it here for debugging purposes
            # self.get_npc_hits()

            if actor_bs_name and self.npc_fsm.npcs_xyz_vec.get(actor_bs_name):
                vec_x = self.npc_fsm.npcs_xyz_vec[actor_bs_name][0]

                if passive:
                    # Just stay
                    request.request("Idle", actor, "LookingAround", "loop")

                elif passive is False:
                    # If NPC is far from Player, do pursue Player
                    if vec_x > 1.0 or vec_x < -1.0:
                        request.request("Walk", actor, self.player, self.ai_behaviors[actor.get_name()],
                                        "pursuer", "Walking", "loop")

                        # If NPC is close to Player, just stay
                        if self.ai_behaviors[actor.get_name()].behavior_status("pursue") == "done":
                            # TODO: Change action to something more suitable
                            request.request("Idle", actor, "LookingAround", "loop")

    def npc_enemy_logic(self, actor, request, passive):
        if (actor and request and self.npc_fsm.npcs_xyz_vec
                and isinstance(passive, bool)
                and isinstance(self.npc_fsm.npcs_xyz_vec, dict)):

            # Add :BS suffix since we'll get Bullet Shape NodePath here
            actor_bs_name = "{0}:BS".format(actor.get_name())
            actor_name = actor.get_name()

            # Leave it here for debugging purposes
            # self.get_npc_hits()

            if actor_bs_name and self.npc_fsm.npcs_xyz_vec.get(actor_bs_name):
                vec_x = self.npc_fsm.npcs_xyz_vec[actor_bs_name][0]

                # Just stay
                if passive:
                    request.request("Idle", actor, "LookingAround", "loop")

                elif passive is False:
                    # If NPC is far from Player, do pursue Player
                    if vec_x > 1.0 or vec_x < -1.0:
                        request.request("Walk", actor, self.player, self.ai_behaviors[actor.get_name()],
                                        "pursuer", "Walking", "loop")

                    # If NPC is close to Player, do enemy attack
                    if self.ai_behaviors[actor.get_name()].behavior_status("pursue") == "done":
                        request.request("Attack", actor, "Boxing", "loop")

                        # Head the player for enamy
                        self.set_actor_accurate_heading(master_name=actor_bs_name, slave=self.player)

                        # Player is attacked by enemy!
                        if actor.get_current_frame("Boxing") == self.npcs_hits["Boxing"]:
                            self.player_fsm.request("Attacked", self.base.player_ref, "BigHitToHead", "play")

                        # Enemy is attacked by player!
                        if self.base.player_states["is_hitting"]:
                            if self.base.player_ref.get_current_frame("Boxing") == self.npcs_hits["Boxing"]:
                                request.request("Attacked", actor, "BigHitToHead", "Boxing", "play")

                            if hasattr(base, "npcs_actors_health") and base.npcs_actors_health:
                                if base.npcs_actors_health[actor_name].getPercent() != 0:
                                    base.npcs_actors_health[actor_name]['value'] -= 5
                                else:
                                    request.request("Death", actor, "Dying", "play")

