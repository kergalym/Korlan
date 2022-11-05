from panda3d.core import Vec3
from direct.task.TaskManagerGlobal import taskMgr

""" ANIMATIONS"""
from Engine import anim_names


class Animator:
    """ Animator class handles Idle/Walk/Run/Jump states based on actor's velocity
    """
    def __init__(self, actor, actor_rb_np, request):
        self.base = base
        self.actor = actor
        self.actor_rb_np = actor_rb_np
        self.request = request

        taskMgr.add(self._update_npc_anim_state_task,
                    "update_npc_anim_state_task",
                    extraArgs=[self.actor, self.actor_rb_np, self.request],
                    appendTask=True)

    def _update_npc_anim_state_task(self, actor, actor_rb_np, request, task):
        if self.base.game_instance["menu_mode"]:
            return task.done

        if actor.get_python_tag("ai_controller_state"):
            if actor.get_python_tag("generic_states")['is_alive']:
                if actor.get_python_tag("npc_type") == "npc":
                    if not actor.get_python_tag("human_states")['is_on_horse']:
                        if not actor.get_python_tag("generic_states")['is_moving']:
                            self._idle_anim_logic(actor, request)
                        elif actor.get_python_tag("generic_states")['is_moving']:
                            self._walking_anim_logic(actor, request)
                        if actor.get_python_tag("generic_states")['is_jumping']:
                            self._jumping_logic(actor, actor_rb_np, request)
                    elif actor.get_python_tag("human_states")['is_on_horse']:
                        parent_rb_np = actor.get_python_tag("mounted_horse")
                        parent_name = parent_rb_np.get_child(0).get_name()
                        parent = self.base.game_instance["actors_ref"][parent_name]
                        if not parent.get_python_tag("generic_states")['is_moving']:
                            self._idle_anim_logic(parent, request)
                        elif parent.get_python_tag("generic_states")['is_moving']:
                            self._walking_anim_logic(parent, request)
                        if parent.get_python_tag("generic_states")['is_jumping']:
                            self._jumping_logic(parent, parent_rb_np, request)

                elif actor.get_python_tag("npc_type") == "npc_animal":
                    if not actor.get_python_tag("generic_states")['is_moving']:
                        self._idle_anim_logic(actor, request)
                    elif actor.get_python_tag("generic_states")['is_moving']:
                        self._walking_anim_logic(actor, request)
                    if actor.get_python_tag("generic_states")['is_jumping']:
                        self._jumping_logic(actor, actor_rb_np, request)

        return task.cont

    def _decrease_stamina(self, actor):
        if actor.get_python_tag("stamina_np"):
            if actor.get_python_tag("stamina_np")['value'] > 1:
                actor.get_python_tag("stamina_np")['value'] -= 1

    def _decrease_courage(self, actor):
        if actor.get_python_tag("courage_np"):
            if actor.get_python_tag("courage_np")['value'] > 1:
                actor.get_python_tag("courage_np")['value'] -= 1

    def _increase_stamina(self, actor):
        if actor.get_python_tag("stamina_np"):
            if actor.get_python_tag("stamina_np")['value'] < 100:
                actor.get_python_tag("stamina_np")['value'] += 0.5

    def _increase_courage(self, actor):
        if actor.get_python_tag("courage_np"):
            if actor.get_python_tag("courage_np")['value'] < 100:
                actor.get_python_tag("courage_np")['value'] += 0.5

    def _idle_anim_logic(self, actor, request):
        if actor and request:
            if actor.get_python_tag("npc_type") == "npc":
                if not actor.get_python_tag("human_states")['is_on_horse']:
                    anim_action = anim_names.a_anim_idle

                    if actor.get_python_tag("generic_states")['is_crouch_moving']:
                        anim_action = anim_names.a_anim_crouch_idle

                    if actor.get_python_tag("generic_states")['is_idle']:
                        if actor.get_python_tag("generic_states")['is_crouch_moving']:
                            request.request("Idle", actor, anim_action, "loop")
                        elif not actor.get_python_tag("generic_states")['is_crouch_moving']:
                            request.request("Idle", actor, anim_action, "loop")

                    # Stamina increases in idle
                    self._increase_stamina(actor)

                elif actor.get_python_tag("human_states")['is_on_horse']:
                    parent_rb_np = actor.get_python_tag("mounted_horse")
                    parent_name = parent_rb_np.get_child(0).get_name()
                    parent = self.base.game_instance["actors_ref"][parent_name]
                    anim_action = anim_names.a_anim_horse_idle
                    if parent.get_python_tag("generic_states")['is_idle']:
                        request.request("Idle", parent, anim_action, "loop")

                    # Stamina increases in idle
                    self._increase_stamina(parent)

            elif actor.get_python_tag("npc_type") == "npc_animal":
                anim_action = anim_names.a_anim_horse_idle
                if actor.get_python_tag("generic_states")['is_crouch_moving']:
                    anim_action = anim_names.a_anim_horse_crouch_idle

                if actor.get_python_tag("generic_states")['is_idle']:
                    if actor.get_python_tag("generic_states")['is_crouch_moving']:
                        request.request("Idle", actor, anim_action, "loop")
                    elif not actor.get_python_tag("generic_states")['is_crouch_moving']:
                        request.request("Idle", actor, anim_action, "loop")

                # Stamina increases in idle
                self._increase_stamina(actor)

    def _walking_anim_logic(self, actor, request):
        if actor and request:
            if actor.get_python_tag("npc_type") == "npc":
                if not actor.get_python_tag("human_states")['is_on_horse']:
                    if actor.get_python_tag("move_type") == "walk":
                        anim_action = anim_names.a_anim_walking
                        if actor.get_python_tag("generic_states")['is_crouch_moving']:
                            anim_action = anim_names.a_anim_crouch_walking
                        request.request("Walk", actor, anim_action, "loop")
                    elif actor.get_python_tag("move_type") == "run":
                        if actor.get_python_tag("stamina_np"):
                            if actor.get_python_tag("stamina_np")['value'] > 10:
                                run_anim = anim_names.a_anim_run
                                request.request("Walk", actor, run_anim, "loop")

                    # Stamina decreases while walking
                    self._decrease_stamina(actor)

            elif actor.get_python_tag("npc_type") == "npc_animal":
                if actor.get_python_tag("move_type") == "walk":
                    anim_action = anim_names.a_anim_horse_walking
                    request.request("Walk", actor, anim_action, "loop")
                elif actor.get_python_tag("move_type") == "run":
                    if actor.get_python_tag("stamina_np"):
                        if actor.get_python_tag("stamina_np")['value'] > 10:
                            run_anim = anim_names.a_anim_horse_run
                            request.request("Walk", actor, run_anim, "loop")

                # Stamina decreases while walking
                self._decrease_stamina(actor)

    def _jumping_logic(self, actor, actor_rb_np, request):
        if (actor.get_python_tag("generic_states")['is_idle']
                and not actor.get_python_tag("generic_states")['is_attacked']
                and not actor.get_python_tag("generic_states")['is_busy']
                and not actor.get_python_tag("generic_states")['is_moving']):
            if (actor.get_python_tag("generic_states")
                    and not actor.get_python_tag("generic_states")['is_crouch_moving']):
                if actor.get_python_tag("npc_type") == "npc_animal":
                    # todo add horse jump anim
                    # request.request("Jump", actor, anim_names.a_anim_horse_jumping, "play")
                    pass
                elif actor.get_python_tag("npc_type") == "npc":
                    request.request("Jump", actor, actor_rb_np, anim_names.a_anim_jumping, "play")

            # Stamina and courage decrease while jumping
            self._decrease_stamina(actor)
            self._decrease_courage(actor)
