from direct.interval.FunctionInterval import Func
from direct.interval.MetaInterval import Sequence
from direct.task.TaskManagerGlobal import taskMgr
from panda3d.bullet import BulletSphereShape, BulletGhostNode, BulletRigidBodyNode
from panda3d.core import BitMask32, Vec3


class SocialQuests:
    def __init__(self):
        self.base = base
        self.render = render
        self.player = None
        self.player_bs = None
        self.player_name = ''
        self.rest_place_np = None
        self.actor_geom_pos_z = 0
        self.cam_p = 0
        self.game_dir = base.game_dir
        self.text_caps = self.base.ui_txt_geom_collector()
        self.render_pipeline = None
        if self.base.game_instance["renderpipeline_np"]:
            self.render_pipeline = self.base.game_instance["renderpipeline_np"]

        # Triggers
        self.trig_range = [0.0, 0.5]
        self.item_range = [0.0, 0.7]

    def set_level_triggers(self, scene, task):
        if (self.base.game_instance['scene_is_loaded']
                and self.base.game_instance['player_actions_init_is_activated'] == 1
                and self.base.game_instance['physics_is_activated'] == 1
                and self.base.game_instance['ai_is_activated'] == 1):
            self.player = self.base.game_instance["player_ref"]
            self.player_bs = render.find("**/{0}".format(self.player.get_name()))
            self.player_name = self.player_bs.get_name()

            # Add item triggers
            taskMgr.add(self.set_item_trigger,
                        "set_item_trigger")

            # Add quest triggers
            taskMgr.add(self.set_quest_trigger,
                        "set_quest_trigger",
                        extraArgs=[scene],
                        appendTask=True)
            return task.done

        return task.cont

    def _set_dimensional_text(self, txt_cap, obj):
        if txt_cap and isinstance(txt_cap, str) and obj:
            if self.text_caps and self.text_caps.get(txt_cap):
                txt_cap_np = self.base.loader.load_model(self.text_caps[txt_cap])
                txt_cap_np.reparent_to(obj)
                txt_cap_np.set_two_sided(True)
                txt_cap_np.set_name(txt_cap)
                pos = obj.get_pos()
                txt_cap_np.set_pos(pos[0], pos[1], -0.5)
                txt_cap_np.set_scale(0.07)
                base.txt_cap_np = txt_cap_np
                if hasattr(self, "render_pipeline") and self.render_pipeline:
                    self.render_pipeline.set_effect(txt_cap_np,
                                                    "{0}/Engine/Renderer/effects/dim_text.yaml".format(self.game_dir),
                                                    {"render_gbuffer": True,
                                                     "render_shadow": False,
                                                     "alpha_testing": True,
                                                     "normal_mapping": False})
                txt_cap_np.set_billboard_point_eye()

    def toggle_dimensional_text_visibility(self, trigger_np, txt_label, place, actor):
        if trigger_np and place and txt_label and actor:
            if trigger_np.find(txt_label):
                txt_cap = trigger_np.find(txt_label)

                if self.player_name not in actor.get_name():
                    txt_cap.hide()

                if self.player_name in actor.get_name():
                    if (not self.base.game_instance['is_player_sitting']
                            or not self.base.game_instance['is_player_laying']):
                        if txt_cap.is_hidden():
                            # Show only non-used item txt cap
                            used_item = self.player.get_python_tag("used_item_np")
                            if used_item:
                                if used_item.get_name() != place.get_name():
                                    txt_cap.show()
                            else:
                                txt_cap.show()

                    elif (self.base.game_instance['is_player_sitting']
                          or self.base.game_instance['is_player_laying']):
                        if not txt_cap.is_hidden():
                            txt_cap.hide()

    def set_action_state(self, actor, bool_):
        if actor and isinstance(bool_, bool):
            if self.player_name in actor.get_name():
                self.base.player_states["is_busy"] = bool_
            if "NPC" in actor.get_name():
                actor.get_python_tag("generic_states")["is_busy"] = bool_

    def set_do_once_key(self, key, value):
        """ Function    : set_do_once_key

            Description : Set the state of the do once keys

            Input       : String, Boolean

            Output      : None

            Return      : None
        """
        if (key and isinstance(key, str)
                and isinstance(value, bool)):
            base.do_key_once[key] = value

    def _toggle_sitting_state(self, actor, place, anim, anim_next, task):
        any_action_seq = actor.actor_interval(anim, loop=0)
        any_action_next_seq = actor.actor_interval(anim_next, loop=1)

        txt_cap = render.find("**/txt_sit")

        if (self.base.game_instance["is_player_sitting"]
                and self.base.game_instance["is_indoor"]
                and self.base.player_states["is_busy"]):
            if txt_cap:
                txt_cap.hide()
            if self.player_name in actor.get_name():
                self.base.game_instance["is_player_sitting"] = False
                self.base.camera.set_z(0.0)
                self.base.camera.set_y(-1)
            elif "NPC" in actor.get_name():
                actor.set_python_tag("is_sitting", False)
            # Reverse play for standing_to_sit animation
            any_action_seq = actor.actor_interval(anim, loop=0, playRate=-1.0)
            Sequence(any_action_seq,
                     Func(self.set_do_once_key, "use", False),
                     Func(self.set_action_state, actor, False)
                     ).start()
        elif (not self.base.game_instance["is_player_sitting"]
              and self.base.game_instance["is_indoor"]
              and not self.base.player_states["is_busy"]):
            if self.player_name in actor.get_name():
                self.base.game_instance["is_player_sitting"] = True
                self.base.camera.set_z(-0.5)
                self.base.camera.set_y(-3.0)
                actor_name = actor.get_name()
                actor_bs = self.base.get_actor_bullet_shape_node(asset=actor_name, type="Player")
                heading = place.get_h() - 180
                actor_bs.set_h(heading)
                place_pos = place.get_pos()
                actor_bs.set_x(place_pos[0])
                actor_bs.set_y(place_pos[1])
            elif "NPC" in actor.get_name():
                actor.set_python_tag("is_sitting", True)
                actor_name = actor.get_name()
                actor_bs = self.base.get_actor_bullet_shape_node(asset=actor_name, type="NPC")
                heading = place.get_h() - 180
                actor_bs.set_h(heading)
                place_pos = place.get_pos()
                actor_bs.set_x(place_pos[0])
                actor_bs.set_y(place_pos[1])

            if task == "loop":
                Sequence(any_action_seq,
                         Func(self.set_action_state, actor, True),
                         any_action_next_seq,
                         ).start()
            elif task == "play":
                Sequence(any_action_seq,
                         Func(self.set_action_state, actor, True)).start()

    def _toggle_laying_state(self, actor, place, anim, anim_next, task):
        any_action_seq = actor.actor_interval(anim, loop=0)
        any_action_next_seq = actor.actor_interval(anim_next, loop=1)

        txt_cap = render.find("**/txt_rest")

        if (self.base.game_instance["is_player_laying"]
                and self.base.game_instance["is_indoor"]
                and self.base.player_states["is_busy"]):
            if txt_cap:
                txt_cap.show()
            # Stop having rest
            actor_bs = None
            if self.player_name in actor.get_name():
                self.base.game_instance["is_player_laying"] = False
                self.base.camera.set_z(0.0)
                self.base.camera.set_p(self.cam_p)
                self.base.camera.set_y(-1)
                actor.set_z(self.actor_geom_pos_z)
                actor_name = actor.get_name()
                actor_bs = self.base.get_actor_bullet_shape_node(asset=actor_name, type="Player")
            elif "NPC" in actor.get_name():
                actor.set_python_tag("is_laying", False)
                actor.set_z(self.actor_geom_pos_z)
                actor_name = actor.get_name()
                actor_bs = self.base.get_actor_bullet_shape_node(asset=actor_name, type="NPC")
            # Reverse play for standing_to_sit animation
            any_action_seq = actor.actor_interval(anim, loop=0, playRate=-1.0)
            Sequence(Func(actor_bs.set_z, 0),
                     any_action_seq,
                     Func(self.set_do_once_key, "use", False),
                     Func(self.set_action_state, actor, False)).start()
        if (not self.base.game_instance["is_player_laying"]
                and self.base.game_instance["is_indoor"]
                and not self.base.player_states["is_busy"]):
            if txt_cap:
                txt_cap.hide()
            # Start having rest
            actor_bs = None
            if self.player_name in actor.get_name():
                self.base.game_instance["is_player_laying"] = True
                self.base.camera.set_z(-1.3)
                self.base.camera.set_y(-4.2)
                self.base.camera.set_h(0)
                self.cam_p = self.base.camera.get_p()
                self.base.camera.set_p(10)
                actor_name = actor.get_name()
                actor_bs = self.base.get_actor_bullet_shape_node(asset=actor_name, type="Player")
                self.actor_geom_pos_z = actor.get_z()
                actor.set_z(-0.75)
                heading = place.get_h() - 170
                pos = actor_bs.get_pos() - Vec3(-0.3, -0.1, 0)
                actor_bs.set_h(heading)
                actor_bs.set_pos(pos)
                place_pos = place.get_pos()
                actor_bs.set_x(place_pos[0])
                actor_bs.set_y(place_pos[1])
            elif "NPC" in actor.get_name():
                actor.set_python_tag("is_laying", True)
                actor_name = actor.get_name()
                actor_bs = self.base.get_actor_bullet_shape_node(asset=actor_name, type="NPC")
                heading = place.get_h() - 170
                pos = actor_bs.get_pos() - Vec3(-0.3, -0.1, 0)
                actor_bs.set_h(heading)
                actor_bs.set_pos(pos)
                place_pos = place.get_pos()
                actor_bs.set_x(place_pos[0])
                actor_bs.set_y(place_pos[1])

            if task == "loop":
                Sequence(any_action_seq,
                         Func(self.set_action_state, actor, True),
                         any_action_next_seq,
                         ).start()
            elif task == "play":
                Sequence(any_action_seq,
                         Func(self.set_action_state, actor, True)).start()

    def play_action_state(self, actor, anim, task):
        if actor and anim and task:
            any_action = actor.get_anim_control(anim)
            any_action_seq = actor.actor_interval(anim, loop=0)

            if any_action.is_playing():
                actor.stop(anim)
                self.set_action_state(actor, False)
            else:
                if task == "loop":
                    Sequence(Func(self.set_action_state, actor, True),
                             any_action_seq).start()
                elif task == "play":
                    Sequence(Func(self.set_action_state, actor, True), any_action_seq).start()

    def set_item_trigger(self, task):
        if self.base.game_instance["loading_is_done"] == 1:
            if (self.render.find("**/World")
                    and self.base.game_instance["physics_world_np"]):
                world_np = self.render.find("**/World")
                ph_world = self.base.game_instance["physics_world_np"]
                radius = 0.3

                for name in self.player.get_python_tag("usable_item_list")["name"]:
                    actor = render.find("**/{0}".format(name))
                    if actor:

                        # Set item collider
                        """sphere = BulletSphereShape(0.2)
                        item_bs = BulletRigidBodyNode('{0}:BS'.format(actor.get_name()))
                        item_bs_np = actor.attach_new_node(item_bs)
                        item_bs.set_mass(2.0)
                        item_bs.add_shape(sphere)
                        item_bs.set_into_collide_mask(BitMask32.allOn())
                        ph_world.attach(item_bs)
                        item_bs_np.reparent_to(actor)"""

                        # Set item trigger
                        sphere = BulletSphereShape(radius)
                        trigger_bg = BulletGhostNode('{0}_trigger'.format(actor.get_name()))
                        trigger_bg.add_shape(sphere)
                        trigger_np = world_np.attach_new_node(trigger_bg)
                        trigger_np.set_collide_mask(BitMask32(0x0f))
                        ph_world.attach_ghost(trigger_bg)
                        trigger_np.reparent_to(actor)
                        trigger_np.set_pos(0, 0, 1)

                        self._set_dimensional_text(txt_cap="txt_use", obj=trigger_np)

                        taskMgr.add(self.item_trigger_task,
                                    "{0}_trigger_task".format(actor.get_name()),
                                    extraArgs=[trigger_np, actor],
                                    appendTask=True)

                return task.done

        return task.cont

    def set_quest_trigger(self, scene, task):
        if self.base.game_instance["loading_is_done"] == 1:
            if (self.render.find("**/World")
                    and self.base.game_instance["physics_world_np"]):
                world_np = self.render.find("**/World")
                ph_world = self.base.game_instance["physics_world_np"]
                radius = 0.3

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
                            self._set_dimensional_text(txt_cap="txt_sit", obj=trigger_np)
                            taskMgr.add(self.quest_yurt_campfire_task,
                                        "quest_yurt_campfire_task",
                                        extraArgs=[trigger_np, actor],
                                        appendTask=True)
                        elif "rest_place" in actor.get_name():
                            self._set_dimensional_text(txt_cap="txt_rest", obj=trigger_np)
                            taskMgr.add(self.quest_yurt_rest_task,
                                        "quest_yurt_rest_task",
                                        extraArgs=[trigger_np, actor],
                                        appendTask=True)

                        elif "hearth" in actor.get_name():
                            self._set_dimensional_text(txt_cap="txt_use", obj=trigger_np)
                            taskMgr.add(self.quest_cook_food_hearth_task,
                                        "quest_cook_food_hearth_task",
                                        extraArgs=[trigger_np, actor],
                                        appendTask=True)

                        elif "spring_water" in actor.get_name():
                            self._set_dimensional_text(txt_cap="txt_use", actor=trigger_np)
                            taskMgr.add(self.quest_spring_water_task,
                                        "quest_spring_water_task",
                                        extraArgs=[trigger_np, actor],
                                        appendTask=True)

                return task.done

        return task.cont

    def quest_yurt_campfire_task(self, trigger_np, place, task):
        if self.base.game_instance['menu_mode']:
            self.base.game_instance["is_player_sitting"] = False
            return task.done

        if not self.player.get_python_tag("is_on_horse"):
            for node in trigger_np.node().get_overlapping_nodes():
                # Show 3d text
                self.toggle_dimensional_text_visibility(trigger_np=trigger_np, txt_label="txt_sit",
                                                        place=place, actor=node)
                if self.player_name in node.get_name():
                    if (round(self.player_bs.get_distance(place), 1) >= self.trig_range[0]
                            and round(self.player_bs.get_distance(place), 1) <= self.trig_range[1]):
                        if (self.base.game_instance["kbd_np"].keymap["use"]
                                and not base.player_states['is_using']
                                and not base.player_states['is_moving']
                                and not self.base.game_instance['is_aiming']):
                            self._toggle_sitting_state(self.player,
                                                       place,
                                                       "standing_to_sit_turkic",
                                                       "sitting_turkic",
                                                       "loop")
                # TODO: Uncomment first to debug
                """
                elif ("NPC" in node.get_name()
                      and "trigger" not in node.get_name()
                      and "Hips" not in node.get_name()):
                    name = node.get_name()
                    name = name.split(":")[0]
                    name_bs = node.get_name()
                    actor = self.base.game_instance["actors_ref"][name]
                    actor_bs = self.base.game_instance["actors_np"][name_bs]
                    if (round(place.get_distance(actor_bs), 1) >= self.trig_range[0]
                            and round(place.get_distance(actor_bs), 1) <= self.trig_range[1]):
                        if not actor.get_python_tag('is_sitting'):
                            self._toggle_laying_state(actor,
                                                      place,
                                                      "standing_to_sit_turkic",
                                                      "sitting_turkic",
                                                      "loop")
                """

        return task.cont

    def quest_yurt_rest_task(self, trigger_np, place, task):
        if self.base.game_instance['menu_mode']:
            self.base.game_instance['is_player_laying'] = False
            return task.done

        if not self.player.get_python_tag("is_on_horse"):
            for node in trigger_np.node().get_overlapping_nodes():
                # Show 3d text
                self.toggle_dimensional_text_visibility(trigger_np=trigger_np, txt_label="txt_rest",
                                                        place=place, actor=node)
                if self.player_name in node.get_name():
                    if (round(self.player_bs.get_distance(place), 1) >= self.trig_range[0]
                            and round(self.player_bs.get_distance(place), 1) <= self.trig_range[1]):
                        if (self.base.game_instance["kbd_np"].keymap["use"]
                                and not base.player_states['is_using']
                                and not base.player_states['is_moving']
                                and not self.base.game_instance['is_aiming']):
                            self._toggle_laying_state(self.player,
                                                      place,
                                                      "standing_to_sit_turkic",
                                                      "sleeping_idle",
                                                      "loop")
                # TODO: Uncomment first to debug
                """
                elif ("NPC" in node.get_name()
                      and "trigger" not in node.get_name()
                      and "Hips" not in node.get_name()):
                    name = node.get_name()
                    name = name.split(":")[0]
                    name_bs = node.get_name()
                    actor = self.base.game_instance["actors_ref"][name]
                    actor_bs = self.base.game_instance["actors_np"][name_bs]
                    if (round(place.get_distance(actor_bs), 1) >= self.trig_range[0]
                            and round(place.get_distance(actor_bs), 1) <= self.trig_range[1]):
                        if not actor.get_python_tag('generic_states')["is_laying"]:
                            # todo: change to suitable standing_to_laying anim
                            self._toggle_laying_state(actor,
                                                      place,
                                                      "standing_to_sit_turkic",
                                                      "sleeping_idle",
                                                      "loop")
                """

        return task.cont

    def quest_spring_water_task(self, trigger_np, place, task):
        if self.base.game_instance['menu_mode']:
            return task.done

        if not self.player.get_python_tag("is_on_horse"):
            for node in trigger_np.node().get_overlapping_nodes():
                # Show 3d text
                self.toggle_dimensional_text_visibility(trigger_np=trigger_np, txt_label="txt_use",
                                                        place=place, actor=node)
                if self.player_name in node.get_name():
                    if (round(self.player_bs.get_distance(place), 1) >= self.trig_range[0]
                            and round(self.player_bs.get_distance(place), 1) <= self.trig_range[1]):
                        if (self.base.game_instance["kbd_np"].keymap["use"]
                                and not base.player_states['is_using']
                                and not base.player_states['is_moving']
                                and not self.base.game_instance['is_aiming']):
                            self.play_action_state(self.player, "spring_water", "play")
                # TODO: Uncomment first to debug
                """
                elif ("NPC" in node.get_name()
                      and "trigger" not in node.get_name()
                      and "Hips" not in node.get_name()):
                    name = node.get_name()
                    name = name.split(":")[0]
                    name_bs = node.get_name()
                    actor = self.base.game_instance["actors_ref"][name]
                    actor_bs = self.base.game_instance["actors_np"][name_bs]
                    if (round(place.get_distance(actor_bs), 1) >= self.trig_range[0]
                            and round(place.get_distance(actor_bs), 1) <= self.trig_range[1]):
                        self.play_action_state(actor, "spring_water", "play")
                """

        return task.cont

    def quest_cook_food_hearth_task(self, trigger_np, place, task):
        if self.base.game_instance['menu_mode']:
            return task.done

        if not self.player.get_python_tag("is_on_horse"):
            # TODO: Uncomment task when cook_food anim will be ready
            for node in trigger_np.node().get_overlapping_nodes():
                # Show 3d text
                self.toggle_dimensional_text_visibility(trigger_np=trigger_np, txt_label="txt_use",
                                                        place=place, actor=node)
                if self.player_name in node.get_name():
                    if (round(self.player_bs.get_distance(place), 1) >= self.trig_range[0]
                            and round(self.player_bs.get_distance(place), 1) <= self.trig_range[1]):

                        """
                        if (round(place.get_distance(player_bs), 1) >= self.trig_range[0]
                                and round(place.get_distance(player_bs), 1) <= self.trig_range[1]):
                            if (self.base.game_instance["kbd_np"].keymap["use"]
                                    and not base.player_states['is_using']
                                    and not base.player_states['is_moving']
                                    and not self.base.game_instance['is_aiming']):
                            self.base.accept("e", self.play_action_state, [player,
                                                                           "cook_food",
                                                                           "loop"])
                        """
                # TODO: Uncomment first to debug
                """
                elif ("NPC" in node.get_name()
                      and "trigger" not in node.get_name()
                      and "Hips" not in node.get_name()):
                    name = node.get_name()
                    name = name.split(":")[0]
                    name_bs = node.get_name()
                    actor = self.base.game_instance["actors_ref"][name]
                    actor_bs = self.base.game_instance["actors_np"][name_bs]
                    if (round(place.get_distance(actor_bs), 1) >= self.trig_range[0]
                            and round(place.get_distance(actor_bs), 1) <= self.trig_range[1]):
                        self.play_action_state(actor, "cook_food", "loop")
                """

        return task.cont

    def _items_by_distance_sort(self):
        for name in self.player.get_python_tag("usable_item_list")["name"]:
            nodepath = render.find("**/{0}".format(name))
            # todo: sort items for trigger_np attached to item, not empty shit!!!
            if nodepath:
                if (round(self.player_bs.get_distance(nodepath), 1) >= self.item_range[0]
                        and round(self.player_bs.get_distance(nodepath), 1) <= self.item_range[1]):
                    return nodepath

    def _construct_item_property(self, player, item_np):
        if player and item_np:
            # Currently close item parameters
            self.base.game_instance['item_state'] = {
                'type': 'item',
                'name': '{0}'.format(item_np.get_name()),
                'weight': '{0}'.format(1),
                'in-use': False,
            }
            player.set_python_tag("used_item_np", item_np)
            player.set_python_tag("is_item_ready", True)
            item_prop = self.base.game_instance['item_state']
            player.set_python_tag("current_item_prop", item_prop)

    def item_trigger_task(self, trigger_np, actor, task):
        if self.base.game_instance['menu_mode']:
            return task.done

        if not self.player.get_python_tag("is_on_horse"):
            for node in trigger_np.node().get_overlapping_nodes():
                # Show 3d text if we closer to item trigger or close if we far from it
                self.toggle_dimensional_text_visibility(trigger_np=trigger_np, txt_label="txt_use",
                                                        place=actor, actor=node)
                if self.player_name in node.get_name():
                    if not self.player.get_python_tag("is_item_using"):
                        if (round(self.player_bs.get_distance(actor), 1) >= self.item_range[0]
                                and round(self.player_bs.get_distance(actor), 1) <= self.item_range[1]):
                            item_np = self.player.get_python_tag("used_item_np")

                            # Construct the item properties only once
                            # if we didn't move closer to item yet
                            # or we moved closer to different item

                            # Get item for first time, we didn't pick it up
                            if item_np and not self.player.get_python_tag("used_item_np"):
                                self._construct_item_property(self.player, item_np)
                            # Get item for second time, we had picked up previous item,
                            # but we alter it with picking another one
                            elif (item_np and self.player.get_python_tag("used_item_np")
                                  and self.player.get_python_tag("used_item_np").get_name() != item_np.get_name()):
                                self._construct_item_property(self.player, item_np)

                # TODO: Uncomment first to debug
                """
                elif ("NPC" in node.get_name()
                      and "trigger" not in node.get_name()
                      and "Hips" not in node.get_name()):
                    name = node.get_name()
                    name = name.split(":")[0]
                    name_bs = node.get_name()
                    actor_npc = self.base.game_instance["actors_ref"][name]
                    actor_npc_bs = self.base.game_instance["actors_np"][name_bs]
                    if not actor_npc.get_python_tag("is_item_using"):
                        if (round(actor.get_distance(actor_npc_bs), 1) >= self.trig_range[0]
                                and round(actor.get_distance(actor_npc_bs), 1) <= self.trig_range[1]):
                            actor_bs = actor.find("**/{0}:BS".format(actor.get_name()))
                            # Currently close item parameters
                            self.base.game_instance['item_state'] = {
                                'type': 'item',
                                'name': '{0}'.format(actor.get_name()),
                                'weight': '{0}'.format(1),
                                'in-use': False,
                            }
                            actor_npc.set_python_tag("used_item_np", actor_bs)
                            actor_npc.set_python_tag("is_item_ready", True)
                        else:
                            actor_npc.set_python_tag("used_item_np", None)
                            actor_npc.set_python_tag("is_item_ready", False)
                    else:
                        item_prop = self.base.game_instance['item_state']
                        actor_npc.set_python_tag("current_item_prop", item_prop)
                """

        return task.cont
