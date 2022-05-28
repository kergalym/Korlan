from direct.interval.FunctionInterval import Func
from direct.interval.MetaInterval import Sequence
from direct.task.TaskManagerGlobal import taskMgr
from panda3d.bullet import BulletSphereShape, BulletGhostNode
from panda3d.core import BitMask32, Vec3


class Quests:
    def __init__(self):
        self.base = base
        self.render = render
        self.game_settings = base.game_settings
        self.k_use_lo = self.game_settings['Keymap']['use'].lower()
        self.seq = None
        self.player_bs = None
        self.rest_place_np = None
        self.actor_geom_pos_z = 0
        self.cam_p = 0
        self.game_dir = base.game_dir
        self.text_caps = self.base.ui_txt_geom_collector()
        if self.base.game_instance["renderpipeline_np"]:
            self.render_pipeline = self.base.game_instance["renderpipeline_np"]
        self.trig_range = [0.1, 1.5]

    def set_action_state(self, actor, bool_):
        if actor and isinstance(bool_, bool):
            if "Player" in actor.get_name():
                self.base.player_states["is_busy"] = bool_
            if "NPC" in actor.get_name():
                actor.get_python_tag("generic_states")["is_busy"] = bool_

    def _toggle_sitting_state(self, actor, place, anim, anim_next, task):
        any_action_seq = actor.actor_interval(anim, loop=0)
        any_action_next_seq = actor.actor_interval(anim_next, loop=1)

        txt_cap = render.find("**/txt_sit")

        if (self.base.game_instance["is_player_sitting"]
                and self.base.player_states["is_busy"]):
            if txt_cap:
                txt_cap.hide()
            if "Player" in actor.get_name():
                self.base.game_instance["is_player_sitting"] = False
                self.base.camera.set_z(0.0)
                self.base.camera.set_y(-1)
            elif "NPC" in actor.get_name():
                actor.set_python_tag("is_sitting", False)
            # Reverse play for standing_to_sit animation
            any_action_seq = actor.actor_interval(anim, loop=0, playRate=-1.0)
            Sequence(any_action_seq, Func(self.set_action_state, actor, False)).start()
        elif (not self.base.game_instance["is_player_sitting"]
                and not self.base.player_states["is_busy"]):
            if "Player" in actor.get_name():
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
                Sequence(Func(self.set_action_state, actor, True),
                         any_action_seq,
                         any_action_next_seq).start()
            elif task == "play":
                Sequence(Func(self.set_action_state, actor, True),
                         any_action_seq).start()

    def _toggle_laying_state(self, actor, place, anim, anim_next, task):
        any_action_seq = actor.actor_interval(anim, loop=0)
        any_action_next_seq = actor.actor_interval(anim_next, loop=1)

        txt_cap = render.find("**/txt_rest")

        if (self.base.game_instance["is_player_laying"]
                and self.base.player_states["is_busy"]):
            if txt_cap:
                txt_cap.show()
            # Stop having rest
            actor_bs = None
            if "Player" in actor.get_name():
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
                     Func(self.set_action_state, actor, False)).start()
        if (not self.base.game_instance["is_player_laying"]
                and not self.base.player_states["is_busy"]):
            if txt_cap:
                txt_cap.hide()
            # Start having rest
            actor_bs = None
            if "Player" in actor.get_name():
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
                         Func(actor_bs.set_z, 1.9),
                         any_action_next_seq,
                         Func(self.set_action_state, actor, True)).start()
            elif task == "play":
                Sequence(Func(actor_bs.set_z, 1.9),
                         any_action_seq,
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
                    self.seq = Sequence(Func(self.set_action_state, actor, True),
                                        any_action_seq)
                    self.seq.start()
                elif task == "play":
                    Sequence(Func(self.set_action_state, actor, True), any_action_seq).start()

    def _set_dimensional_txt(self, txt_cap, obj):
        if txt_cap and isinstance(txt_cap, str) and obj:
            if self.text_caps[txt_cap]:
                txt_cap_np = self.base.loader.load_model(self.text_caps[txt_cap])
                txt_cap_np.reparent_to(obj)
                txt_cap_np.set_two_sided(True)
                txt_cap_np.set_name(txt_cap)
                pos = obj.get_pos()
                txt_cap_np.set_pos(pos[0], pos[1], -0.5)
                txt_cap_np.set_scale(0.07)
                base.txt_cap_np = txt_cap_np
                if self.render_pipeline:
                    self.render_pipeline.set_effect(txt_cap_np,
                                                    "{0}/Engine/Renderer/effects/dim_text.yaml".format(self.game_dir),
                                                    {"render_gbuffer": True,
                                                     "render_shadow": False,
                                                     "alpha_testing": True,
                                                     "normal_mapping": False})
                txt_cap_np.set_billboard_point_eye()

    def toggle_3d_text_vis(self, trigger_np, txt_label, place, actor):
        if trigger_np and place and txt_label and actor:
            if (not self.base.game_instance['is_player_sitting']
                    or not self.base.game_instance['is_player_laying']):
                if trigger_np.find(txt_label):
                    txt_cap = trigger_np.find(txt_label)
                    if txt_cap:
                        if (round(place.get_distance(actor), 1) >= self.trig_range[0]
                                and round(place.get_distance(actor), 1) <= self.trig_range[1]):
                            txt_cap.show()
                        elif round(place.get_distance(actor), 1) == 0.0:
                            txt_cap.hide()
                        elif round(place.get_distance(actor), 1) > self.trig_range[1]:
                            txt_cap.hide()

    def set_item_trigger(self, scene, task):
        if self.base.game_instance["loading_is_done"] == 1:
            if (self.render.find("**/World")
                    and self.base.game_instance["physics_world_np"]):
                world_np = self.render.find("**/World")
                ph_world = self.base.game_instance["physics_world_np"]
                radius = 0.3

                # TODO: DEBUG ME!
                for actor in scene.get_children():
                    if "item_" in actor.get_name():  # yurt_item_empty_trigger
                        sphere = BulletSphereShape(radius)
                        trigger_bg = BulletGhostNode('{0}_trigger'.format(actor.get_name()))
                        trigger_bg.add_shape(sphere)
                        trigger_np = world_np.attach_new_node(trigger_bg)
                        trigger_np.set_collide_mask(BitMask32(0x0f))
                        ph_world.attach_ghost(trigger_bg)
                        trigger_np.reparent_to(actor)
                        trigger_np.set_pos(0, 0, 1)

                        self._set_dimensional_txt(txt_cap="txt_use", obj=trigger_np)

                        taskMgr.add(self.item_trigger_task,
                                    "{0}_trigger_task".format(actor.get_name()),
                                    extraArgs=[trigger_np, actor],
                                    appendTask=True)

                return task.done

        return task.cont

    def item_trigger_task(self, trigger_np, actor, task):
        if self.base.game_instance['menu_mode']:
            # self.base.game_instance["is_player_sitting"] = False
            return task.done

        # TODO: DEBUG ME!
        for node in trigger_np.node().get_overlapping_nodes():
            if "Player" in node.get_name():
                if not self.player_bs:
                    self.player_bs = render.find("**/{0}".format(node.get_name()))
                player = self.base.game_instance['player_ref']

                # Show 3d text
                self.toggle_3d_text_vis(trigger_np=trigger_np, txt_label="txt_use",
                                        place=actor, actor=self.player_bs)

                if not player.get_python_tag("is_item_using"):
                    if (round(actor.get_distance(self.player_bs), 1) >= self.trig_range[0]
                            and round(actor.get_distance(self.player_bs), 1) <= self.trig_range[1]):
                        actor_bs = actor.find("**/{0}:BS".format(actor.get_name()))
                        # Currently close item parameters
                        self.base.game_instance['item_state'] = {
                            'type': 'item',
                            'name': '{0}'.format(actor.get_name()),
                            'weight': '{0}'.format(1),
                            'in-use': False,
                        }
                        player.set_python_tag("used_item_np", actor_bs)
                        player.set_python_tag("is_item_ready", True)
                    else:
                        player.set_python_tag("used_item_np", None)
                        player.set_python_tag("is_item_ready", False)
                else:
                    item_prop = self.base.game_instance['item_state']
                    player.set_python_tag("current_item_prop", item_prop)
            elif "NPC" in node.get_name():
                name = node.get_name()
                actor_npc = self.base.game_instance["actors_ref"][name]
                actor_npc_bs = self.base.game_instance["actors_np"][name]
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
                            self._set_dimensional_txt(txt_cap="txt_sit", obj=trigger_np)
                            taskMgr.add(self.quest_yurt_campfire_task,
                                        "quest_yurt_campfire_task",
                                        extraArgs=[trigger_np, actor],
                                        appendTask=True)
                        elif "rest_place" in actor.get_name():
                            self._set_dimensional_txt(txt_cap="txt_rest", obj=trigger_np)
                            taskMgr.add(self.quest_yurt_rest_task,
                                        "quest_yurt_rest_task",
                                        extraArgs=[trigger_np, actor],
                                        appendTask=True)

                        elif "hearth" in actor.get_name():
                            self._set_dimensional_txt(txt_cap="txt_use", obj=trigger_np)
                            taskMgr.add(self.quest_cook_food_hearth_task,
                                        "quest_cook_food_hearth_task",
                                        extraArgs=[trigger_np, actor],
                                        appendTask=True)

                        elif "spring_water" in actor.get_name():
                            self._set_dimensional_txt(txt_cap="txt_use", actor=trigger_np)
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

        for node in trigger_np.node().get_overlapping_nodes():
            if "Player" in node.get_name():
                if not self.player_bs:
                    self.player_bs = render.find("**/{0}".format(node.get_name()))
                player = self.base.game_instance['player_ref']

                # Show 3d text
                self.toggle_3d_text_vis(trigger_np=trigger_np, txt_label="txt_sit",
                                        place=place, actor=self.player_bs)

                if (round(place.get_distance(self.player_bs), 1) >= self.trig_range[0]
                        and round(place.get_distance(self.player_bs), 1) <= self.trig_range[1]):
                    if (self.base.game_instance["kbd_np"].keymap["use"]
                            and not base.player_states['is_using']
                            and not base.player_states['is_moving']
                            and not self.base.game_instance['is_aiming']):
                        self._toggle_sitting_state(player,
                                                   place,
                                                   "standing_to_sit_turkic",
                                                   "sitting_turkic",
                                                   "loop")
            elif "NPC" in node.get_name():
                name = node.get_name()
                actor = self.base.game_instance["actors_ref"][name]
                actor_bs = self.base.game_instance["actors_np"][name]
                if (round(place.get_distance(actor_bs), 1) >= self.trig_range[0]
                        and round(place.get_distance(actor_bs), 1) <= self.trig_range[1]):
                    if not actor.get_python_tag('is_sitting'):
                        self._toggle_laying_state(actor,
                                                  place,
                                                  "standing_to_sit_turkic",
                                                  "sitting_turkic",
                                                  "loop")
        return task.cont

    def quest_yurt_rest_task(self, trigger_np, place, task):
        if self.base.game_instance['menu_mode']:
            self.base.game_instance['is_player_laying'] = False
            return task.done

        for node in trigger_np.node().get_overlapping_nodes():
            if "Player" in node.get_name():
                if not self.player_bs:
                    self.player_bs = render.find("**/{0}".format(node.get_name()))
                player = self.base.game_instance['player_ref']

                # Show 3d text
                self.toggle_3d_text_vis(trigger_np=trigger_np, txt_label="txt_rest",
                                        place=place, actor=self.player_bs)

                if (round(place.get_distance(self.player_bs), 1) >= self.trig_range[0]
                        and round(place.get_distance(self.player_bs), 1) <= self.trig_range[1]):
                    # todo: change to suitable standing_to_laying anim
                    if (self.base.game_instance["kbd_np"].keymap["use"]
                            and not base.player_states['is_using']
                            and not base.player_states['is_moving']
                            and not self.base.game_instance['is_aiming']):
                        self._toggle_laying_state(player,
                                                  place,
                                                  "standing_to_sit_turkic",
                                                  "sleeping_idle",
                                                  "loop")
            elif "NPC" in node.get_name():
                name = node.get_name()
                actor = self.base.game_instance["actors_ref"][name]
                actor_bs = self.base.game_instance["actors_np"][name]
                if (round(place.get_distance(actor_bs), 1) >= self.trig_range[0]
                        and round(place.get_distance(actor_bs), 1) <= self.trig_range[1]):
                    if not actor.get_python_tag('generic_states')["is_laying"]:
                        # todo: change to suitable standing_to_laying anim
                        self._toggle_laying_state(actor,
                                                  place,
                                                  "standing_to_sit_turkic",
                                                  "sleeping_idle",
                                                  "loop")

        return task.cont

    def quest_spring_water_task(self, trigger_np, place, task):
        if self.base.game_instance['menu_mode']:
            return task.done

        for node in trigger_np.node().get_overlapping_nodes():
            if "Player" in node.get_name():
                player_bs = render.find("**/{0}".format(node.get_name()))
                player = self.base.game_instance['player_ref']

                # Show 3d text
                self.toggle_3d_text_vis(trigger_np=trigger_np, txt_label="txt_use",
                                        place=place, actor=self.player_bs)

                if (round(place.get_distance(player_bs), 1) >= self.trig_range[0]
                        and round(place.get_distance(player_bs), 1) <= self.trig_range[1]):
                    if (self.base.game_instance["kbd_np"].keymap["use"]
                            and not base.player_states['is_using']
                            and not base.player_states['is_moving']
                            and not self.base.game_instance['is_aiming']):
                        self.play_action_state(player, "spring_water", "play")
            elif "NPC" in node.get_name():
                name = node.get_name()
                actor = self.base.game_instance["actors_ref"][name]
                actor_bs = self.base.game_instance["actors_np"][name]
                if (round(place.get_distance(actor_bs), 1) >= self.trig_range[0]
                        and round(place.get_distance(actor_bs), 1) <= self.trig_range[1]):
                    self.play_action_state(actor, "spring_water", "play")
        return task.cont

    def quest_cook_food_hearth_task(self, trigger_np, place, task):
        if self.base.game_instance['menu_mode']:
            return task.done

        # TODO: Uncomment task when cook_food anim will be ready
        for node in trigger_np.node().get_overlapping_nodes():
            if "Player" in node.get_name():
                player_bs = render.find("**/{0}".format(node.get_name()))
                player = self.base.game_instance['player_ref']

                # Show 3d text
                self.toggle_3d_text_vis(trigger_np=trigger_np, txt_label="txt_use",
                                        place=place, actor=player_bs)

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
            elif "NPC" in node.get_name():
                name = node.get_name()
                actor = self.base.game_instance["actors_ref"][name]
                actor_bs = self.base.game_instance["actors_np"][name]
                if (round(place.get_distance(actor_bs), 1) >= self.trig_range[0]
                        and round(place.get_distance(actor_bs), 1) <= self.trig_range[1]):
                    self.play_action_state(actor, "cook_food", "loop")

        return task.cont
