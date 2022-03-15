from direct.interval.FunctionInterval import Func
from direct.interval.MetaInterval import Sequence
from direct.task.TaskManagerGlobal import taskMgr
from panda3d.bullet import BulletSphereShape, BulletGhostNode
from panda3d.core import BitMask32


class Quests:
    def __init__(self):
        self.base = base
        self.render = render
        self.seq = None

    def set_action_state(self, bool_):
        if isinstance(bool_, bool):
            self.base.player_states["is_busy"] = bool_

    def toggle_action_state(self, actor, anim, anim_next, task):
        any_action_seq = actor.actor_interval(anim, loop=0)
        any_action_next_seq = actor.actor_interval(anim_next, loop=1)

        if self.seq and self.base.game_instance["is_player_sitting"]:
            self.base.game_instance["is_player_sitting"] = False
            self.base.camera.set_z(0.0)
            self.base.camera.set_y(-1)
            self.seq.finish()
            # Reverse play for standing_to_sit animation
            any_action_seq = actor.actor_interval(anim, loop=0, playRate=-1.0)
            Sequence(any_action_seq, Func(self.set_action_state, False)).start()
        else:
            self.base.game_instance["is_player_sitting"] = True
            self.base.camera.set_z(-0.5)
            self.base.camera.set_y(-2.5)
            if task == "loop":
                self.seq = Sequence(Func(self.set_action_state, True),
                                    any_action_seq, any_action_next_seq)
                self.seq.start()
            elif task == "play":
                Sequence(Func(self.set_action_state, True), any_action_seq).start()

    def set_quest_trigger(self, scene, task):
        if self.base.game_instance["loading_is_done"] == 1:
            if (self.render.find("**/World")
                    and self.base.game_instance["physics_world_np"]):
                world_np = self.render.find("**/World")
                ph_world = self.base.game_instance["physics_world_np"]
                radius = 0.7

                for actor in scene.get_children():
                    if "quest_" in actor.get_name():  # quest_empty_campfire
                        sphere = BulletSphereShape(radius)
                        trigger_bg = BulletGhostNode('{0}_trigger'.format(actor.get_name()))
                        trigger_bg.add_shape(sphere)
                        trigger_np = world_np.attach_new_node(trigger_bg)
                        trigger_np.set_collide_mask(BitMask32(0x0f))
                        ph_world.attach_ghost(trigger_bg)
                        trigger_np.reparent_to(actor)
                        trigger_np.set_pos(0, 0, 1)

                        if "campfire" in actor.get_name():
                            taskMgr.add(self.quest_yurt_campfire_task, "quest_yurt_campfire_task",
                                        extraArgs=[trigger_np, actor],
                                        appendTask=True)

                        elif "spring_water" in actor.get_name():
                            taskMgr.add(self.quest_spring_water_task, "quest_spring_water_task",
                                        extraArgs=[trigger_np, actor],
                                        appendTask=True)

                        return task.done

        return task.cont

    def quest_yurt_campfire_task(self, trigger_np, actor, task):
        if self.base.game_instance['menu_mode']:
            self.base.game_instance["is_player_sitting"] = False
            return task.done

        for node in trigger_np.node().get_overlapping_nodes():
            if "Player" in node.get_name():
                player_bs = render.find("**/{0}".format(node.get_name()))
                player = self.base.game_instance['player_ref']
                if player_bs and int(actor.get_distance(player_bs)) == 1:
                    if not self.base.game_instance['is_player_sitting']:
                        self.base.accept("e", self.toggle_action_state, [player,
                                                                         "standing_to_sit_turkic",
                                                                         "sitting_turkic",
                                                                         "loop"])

        return task.cont

    def quest_spring_water_task(self, trigger_np, actor, task):
        if self.base.game_instance['menu_mode']:
            return task.done

        for node in trigger_np.node().get_overlapping_nodes():
            if "Player" in node.get_name():
                player_bs = render.find("**/{0}".format(node.get_name()))
                player = self.base.game_instance['player_ref']
                if player_bs and int(actor.get_distance(player_bs)) == 1:
                    self.base.accept("e", self.toggle_action_state, [player,
                                                                     "standing_to_sit",
                                                                     "spring_water",
                                                                     "loop"])

        return task.cont
