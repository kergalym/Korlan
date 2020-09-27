from direct.fsm.FSM import FSM
from direct.task.TaskManagerGlobal import taskMgr
from Engine.Actors.NPC.state import NpcState
from Engine.Actors.NPC.Classes.npc_husband import Husband
from Engine.Actors.NPC.Classes.npc_mongol import Mongol


class NpcErnarFSM(FSM):
    def __init__(self):
        FSM.__init__(self, "NpcErnarFSM")
        self.base = base
        self.render = render
        self.taskMgr = taskMgr
        self.npc_state = NpcState()
        self.husband = Husband()
        self.mongol = Mongol()

        # TODO: Get classes from level asset, not npcs_classes
        self.npcs_classes = {
            self.husband.name: {'class': 'friend'},
            self.mongol.name: {'class': 'enemy'},
        }

        self.npcs_actor_refs = {}

        self.npcs_names = []
        self.npcs_xyz_vec = {}
        base.fsm = self

    def npc_distance_calculate_task(self, player, npcs_actor_refs, task):
        if (player and npcs_actor_refs and self.npcs_names
                and isinstance(npcs_actor_refs, dict)
                and isinstance(self.npcs_names, list)):
            for npc, ref in zip(self.npcs_names, npcs_actor_refs):
                # Drop :BS suffix since we'll get Bullet Shape NodePath here
                # by our special get_actor_bullet_shape_node()
                # npc = npc.split(":")[0]
                actor = self.base.get_actor_bullet_shape_node(asset=ref, type="NPC")
                xyz_vec = self.base.npc_distance_calculate(player=player, actor=actor)

                if xyz_vec:
                    tuple_xyz_vec = xyz_vec['vector']
                    # Here we put tuple xyz values to our class member npcs_xyz_vec
                    # for every actor name like 'NPC_Ernar:BS'
                    self.npcs_xyz_vec[actor.get_name()] = tuple_xyz_vec

        if base.game_mode is False and base.menu_mode:
            return task.done

        return task.cont

    def set_basic_npc_behaviors(self, actor, player, ai_behaviors, behavior):
        if (actor and player
                and not actor.is_empty()
                and not player.is_empty()
                and behavior
                and isinstance(behavior, str)
                and ai_behaviors):

            if ai_behaviors:
                vect = {"panic_dist": 5,
                        "relax_dist": 5,
                        "wander_radius": 5,
                        "plane_flag": 0,
                        "area_of_effect": 10}
                navmeshes = self.base.navmesh_collector()
                ai_behaviors.init_path_find(navmeshes["lvl_one"])
                if behavior == "obs_avoid":
                    ai_behaviors.path_find_to(player, "addPath")
                    ai_behaviors.add_dynamic_obstacle(player)
                elif behavior == "seek":
                    ai_behaviors.path_find_to(player, "addPath")
                    ai_behaviors.seek(player)
                elif behavior == "flee":
                    ai_behaviors.path_find_to(player, "addPath")
                    ai_behaviors.flee(actor,
                                      vect['panic_dist'],
                                      vect['relax_dist'])
                elif behavior == "pursuer":
                    ai_behaviors.path_find_to(player, "addPath")
                    ai_behaviors.pursue(player)
                elif behavior == "evader":
                    ai_behaviors.path_find_to(player, "addPath")
                    ai_behaviors.evade(player,
                                       vect['panic_dist'],
                                       vect['relax_dist'])
                elif behavior == "wanderer":
                    ai_behaviors.path_find_to(player, "addPath")
                    ai_behaviors.wander(vect["wander_radius"],
                                        vect["plane_flag"],
                                        vect["area_of_effect"])
                elif behavior == "path_finding":
                    ai_behaviors.path_find_to(player, "addPath")
                elif behavior == "path_follow":
                    ai_behaviors.path_follow(1)
                    ai_behaviors.add_to_path(player.get_pos())
                    ai_behaviors.start_follow()

                taskMgr.add(self.keep_actor_pitch_task,
                            "keep_actor_pitch",
                            appendTask=True)

    def keep_actor_pitch_task(self, task):
        for name in self.npcs_names:
            if not render.find("**/{0}".format(name)).is_empty():
                actor = render.find("**/{0}".format(name))
                # Prevent pitch changing
                actor.set_p(0)

        if base.game_mode is False and base.menu_mode:
            return task.done

        return task.done

    def set_npc_class(self, actor):
        if actor and not actor.is_empty():
            for actor_cls in self.npcs_classes:
                if actor_cls in actor.get_name():
                    return self.npcs_classes[actor_cls]

    def enterIdle(self, actor, action, task):
        if actor and action and task:
            any_action = actor.get_anim_control(action)

            if isinstance(task, str):
                if task == "play":
                    if not any_action.isPlaying():
                        actor.play(action)
                elif task == "loop":
                    if not any_action.isPlaying():
                        actor.loop(action)
                actor.set_play_rate(self.base.actor_play_rate, action)

    def enterWalk(self, actor, player, ai_behaviors, behavior, action, task):
        if actor and player and ai_behaviors and behavior and action and task:
            any_action = actor.get_anim_control(action)

            if isinstance(task, str):
                if task == "play":
                    if not any_action.isPlaying():
                        actor.play(action)
                elif task == "loop":
                    if not any_action.isPlaying():
                        actor.loop(action)
                actor.set_play_rate(self.base.actor_play_rate, action)

            # Get correct NodePath
            actor = render.find("**/{0}".format(actor.get_name()))

            self.set_basic_npc_behaviors(actor=actor,
                                         player=player,
                                         ai_behaviors=ai_behaviors,
                                         behavior=behavior)

    def enterAttack(self, actor, action, task):
        if actor and action and task:
            any_action = actor.get_anim_control(action)

            if isinstance(task, str):
                if task == "play":
                    if not any_action.isPlaying():
                        actor.play(action)
                elif task == "loop":
                    if not any_action.isPlaying():
                        actor.loop(action)
                actor.set_play_rate(self.base.actor_play_rate, action)

    """def exitIdle(self):
        actor_node = base.actor_node
        actor_node.stop("LookingAround")

    def exitWalk(self):
        actor_node = base.actor_node
        actor_node.stop("Walking")

    def exitAttack(self):
        actor_node = base.actor_node
        actor_node.stop("Boxing")"""

    def exitSwim(self):
        pass

    def exitStay(self):
        pass

    def exitCrouch(self):
        pass

    def exitJump(self):
        pass

    def exitLay(self):
        pass

    def enterHAttack(self):
        pass

    def enterFAttack(self):
        pass

    def enterBlock(self):
        pass

    def enterInteract(self):
        pass

    def enterLife(self):
        pass

    def enterDeath(self):
        pass

    def enterMiscAct(self):
        pass

    def enterCrouch(self):
        pass

    def enterSwim(self):
        pass

    def enterStay(self):
        pass

    def enterJump(self):
        pass

    def enterLay(self):
        pass

    def exitHAttack(self):
        pass

    def exitFAttack(self):
        pass

    def exitBlock(self):
        pass

    def exitInteract(self):
        pass

    def exitLife(self):
        pass

    def exitDeath(self):
        pass

    def exitMiscAct(self):
        pass

    def filterIdle(self, request, args):
        if request not in ['Idle']:
            return (request,) + args
        else:
            return None

    def filterWalk(self, request, args):
        if request not in ['Walk']:
            return (request,) + args
        else:
            return None
