from direct.task.TaskManagerGlobal import taskMgr
from panda3d.bullet import BulletSphereShape, BulletGhostNode
from panda3d.core import BitMask32
from Engine.Quests.quest_logic import QuestLogic


class SocialQuests:
    def __init__(self):
        self.base = base
        self.render = render
        self.player = None
        self.player_bs = None
        self.player_name = ''
        self.rest_place_np = None
        self.game_dir = base.game_dir
        self.text_caps = self.base.ui_txt_geom_collector()
        self.render_pipeline = None
        if self.base.game_instance["renderpipeline_np"]:
            self.render_pipeline = self.base.game_instance["renderpipeline_np"]

        # Items lists and boolean
        self._is_items_info_collected = False
        self._usable_items = []
        self._usable_item_pos = []
        self._usable_item_hpr = []
        self._last_used_items = None

        self.static_indoor_targets = [render.find("**/yurt"),
                                      render.find("**/quest_empty_campfire"),
                                      render.find("**/quest_empty_rest_place"),
                                      render.find("**/quest_empty_hearth"),
                                      render.find("**/quest_empty_spring_water"),
                                      render.find("**/round_table"),
                                      ]
        self.base.game_instance["static_indoor_targets"] = self.static_indoor_targets
        self.quest_logic = QuestLogic()

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

    def _construct_usable_item_list(self, round_table):
        if round_table:
            for child in round_table.get_children():
                usable_item_list = self.player.get_python_tag("usable_item_list")
                name = child.get_name()
                # Exclude round table itself
                if round_table.get_name() not in name:
                    # Check if we didn't get any items yet which are same as we got
                    # when we come close to round table
                    if self._is_items_info_collected and len(usable_item_list["name"]) > 0:
                        if self._usable_items != self._last_used_items:
                            if self._is_items_info_collected:
                                # clean item lists first
                                if len(self._usable_items) > 0:
                                    self._usable_items = []
                                elif len(self._usable_item_pos) > 0:
                                    self._usable_item_pos = []
                                elif len(self._usable_item_hpr) > 0:
                                    self._usable_item_hpr = []

                                for i in range(len(usable_item_list["name"]) - 1):
                                    if name not in usable_item_list["name"][i]:
                                        # Eclude nodes with empty names
                                        if child.get_name():
                                            self._usable_items.append(name)
                                            self._usable_item_pos.append(child.get_pos())
                                            self._usable_item_hpr.append(child.get_hpr())

                                self._is_items_info_collected = False
                    else:
                        if not self._is_items_info_collected:
                            # Exclude nodes with empty names
                            if child.get_name():
                                # we didn't get any items yet for the first time, so, get the data about them
                                self._usable_items.append(name)
                                self._usable_item_pos.append(child.get_pos())
                                self._usable_item_hpr.append(child.get_hpr())
                                self._last_used_items = self._usable_items

            # Construct usable items list after they were collected
            if not self._is_items_info_collected:
                usable_item_list = {
                    "name": self._usable_items,
                    "pos": self._usable_item_pos,
                    "hpr": self._usable_item_hpr
                }

                # print(usable_item_list["name"], len(usable_item_list["name"]))
                self.player.set_python_tag("usable_item_list", usable_item_list)
                self.base.game_instance["round_table_np"] = round_table

                # Add item triggers
                taskMgr.add(self.set_item_trigger,
                            "set_item_trigger")

                self._is_items_info_collected = True

    def set_level_triggers(self, scene, task):
        if (self.base.game_instance['scene_is_loaded']
                and self.base.game_instance['player_actions_init_is_activated'] == 1
                and self.base.game_instance['physics_is_activated'] == 1
                and self.base.game_instance['ai_is_activated'] == 1):
            self.player = self.base.game_instance["player_ref"]
            self.player_bs = self.base.game_instance["player_np"]
            self.player_name = self.player_bs.get_name()

            # Add round table trigger.
            # We take list of usable items as children of round table node
            taskMgr.add(self.round_table_trigger_task,
                        "round_table_trigger_task")

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

                        # Set place state to check if it's free or busy
                        actor.set_python_tag("place_is_busy", False)

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
                    if round(self.player_bs.get_distance(place), 1) <= 1:
                        if (self.base.game_instance["kbd_np"].keymap["use"]
                                and not base.player_states['is_using']
                                and not base.player_states['is_moving']
                                and not self.base.game_instance['is_aiming']):
                            self.quest_logic.toggle_sitting_state(self.player,
                                                                  place,
                                                                  "standing_to_sit_turkic",
                                                                  "sitting_turkic",
                                                                  "loop")

                if ("NPC" in node.get_name()
                        and "trigger" not in node.get_name()
                        and "Hips" not in node.get_name()
                        and "Hand" not in node.get_name()):
                    name = node.get_name()
                    name = name.split(":")[0]
                    name_bs = node.get_name()
                    actor = self.base.game_instance["actors_ref"][name]
                    actor_bs = self.base.game_instance["actors_np"][name_bs]
                    if round(actor_bs.get_distance(place)) <= 1:
                        self.quest_logic.toggle_npc_sitting_state(actor,
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
            # Show 3d text
            self.toggle_dimensional_text_visibility(trigger_np=trigger_np, txt_label="txt_rest",
                                                    place=place, actor=node)
            if self.player_name in node.get_name():
                if not self.player.get_python_tag("is_on_horse"):
                    if round(self.player_bs.get_distance(place)) <= 1:
                        if (self.base.game_instance["kbd_np"].keymap["use"]
                                and not base.player_states['is_using']
                                and not base.player_states['is_moving']
                                and not self.base.game_instance['is_aiming']):
                            # todo: change to suitable standing_to_laying anim
                            self.quest_logic.toggle_laying_state(self.player,
                                                                 place,
                                                                 "standing_to_sit_turkic",
                                                                 "sleeping_idle",
                                                                 "loop")
            if ("NPC" in node.get_name()
                    and ":BS" in node.get_name()
                    and "Hips" not in node.get_name()
                    and "Hand" not in node.get_name()):
                name = node.get_name()
                name = name.split(":")[0]
                name_bs = node.get_name()
                actor = self.base.game_instance["actors_ref"][name]
                actor_bs = self.base.game_instance["actors_np"][name_bs]
                if round(actor_bs.get_distance(place)) <= 1:
                    # todo: change to suitable standing_to_laying anim
                    self.quest_logic.toggle_npc_laying_state(actor,
                                                             place,
                                                             "standing_to_sit_turkic",
                                                             "sleeping_idle",
                                                             "loop")

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
                    if round(self.player_bs.get_distance(place), 1) <= 1:
                        if (self.base.game_instance["kbd_np"].keymap["use"]
                                and not base.player_states['is_using']
                                and not base.player_states['is_moving']
                                and not self.base.game_instance['is_aiming']):
                            self.quest_logic.play_action_state(self.player, "spring_water", "play")

                if ("NPC" in node.get_name()
                        and "trigger" not in node.get_name()
                        and "Hips" not in node.get_name()
                        and "Hand" not in node.get_name()):
                    name = node.get_name()
                    name = name.split(":")[0]
                    name_bs = node.get_name()
                    actor = self.base.game_instance["actors_ref"][name]
                    actor_bs = self.base.game_instance["actors_np"][name_bs]
                    if round(actor_bs.get_distance(place)) <= 1:
                        self.quest_logic.play_action_state(actor, "spring_water", "play")

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
                    if round(self.player_bs.get_distance(place)) <= 1:
                        """
                        if (self.base.game_instance["kbd_np"].keymap["use"]
                                    and not base.player_states['is_using']
                                    and not base.player_states['is_moving']
                                    and not self.base.game_instance['is_aiming']):
                            self.base.accept("e", self.quest_logic.play_action_state, [player,
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
                    if round(actor_bs.get_distance(place)) <= 1:
                        self.quest_logic.play_action_state(actor, "cook_food", "loop")
                """

        return task.cont

    def round_table_trigger_task(self, task):
        if self.base.game_instance['menu_mode']:
            return task.done

        if self.base.game_instance["loading_is_done"] == 1:
            if not self.player.get_python_tag("is_on_horse"):
                player_cam_trigger_np = self.player_bs.find("**/player_cam_trigger")
                if player_cam_trigger_np:
                    for trigger_node in player_cam_trigger_np.node().get_overlapping_nodes():
                        if "indoor_empty_trigger" in trigger_node.get_name():
                            round_table = render.find("**/round_table")
                            if round_table:
                                for node in trigger_node.get_overlapping_nodes():
                                    if self.player_name in node.get_name():

                                        if self.player.get_python_tag("is_close_to_use_item"):
                                            self.player.set_python_tag("is_close_to_use_item", False)

                                        if round(self.player_bs.get_distance(round_table)) < 2:

                                            self._construct_usable_item_list(round_table)

                                            if not self.player.get_python_tag("is_close_to_use_item"):
                                                self.player.set_python_tag("is_close_to_use_item", True)
        return task.cont

    def item_trigger_task(self, trigger_np, actor, task):
        if self.base.game_instance['menu_mode']:
            return task.done

        if not self.player.get_python_tag("is_on_horse"):
            for node in trigger_np.node().get_overlapping_nodes():
                # Show 3d text if we closer to item trigger or close if we far from it
                self.toggle_dimensional_text_visibility(trigger_np=trigger_np, txt_label="txt_use",
                                                        place=actor, actor=node)
                if self.player_name in node.get_name():
                    # This logic is dedicated only for picking up the outdoor items
                    if not self.base.game_instance["is_indoor"]:

                        if not self.player.get_python_tag("is_item_using"):

                            if self.player.get_python_tag("is_close_to_use_item"):
                                self.player.set_python_tag("is_close_to_use_item", False)

                            # Construct the item properties which is near of the player
                            if round(self.player_bs.get_distance(actor)) < 2:

                                if not self.player.get_python_tag("is_close_to_use_item"):
                                    self.player.set_python_tag("is_close_to_use_item", True)

                                # Construct the item properties only once
                                item_np = self.player.get_python_tag("used_item_np")
                                if not item_np:
                                    self._construct_item_property(self.player, actor)
                            else:
                                # Wipe item properties if we didn't take item yet
                                item_prop = self.player.get_python_tag("current_item_prop")
                                if item_prop:
                                    if not item_prop['in-use']:
                                        if self.base.game_instance['item_state']:
                                            self.base.game_instance['item_state'].clear()
                                        if self.player.get_python_tag("used_item_np"):
                                            self.player.set_python_tag("used_item_np", None)

                # Fixme! Check the code
                elif ("NPC" in node.get_name()
                      and "trigger" not in node.get_name()
                      and "Hips" not in node.get_name()):
                    name = node.get_name()
                    name = name.split(":")[0]
                    name_bs = node.get_name()
                    actor_npc = self.base.game_instance["actors_ref"][name]
                    actor_npc_bs = self.base.game_instance["actors_np"][name_bs]
                    if not actor_npc.get_python_tag("is_item_using"):
                        if round(actor_npc_bs.get_distance(actor)) < 2:
                            actor_bs = actor.find("**/{0}:BS".format(actor.get_name()))
                            # Currently close item parameters
                            item_prop = {
                                'type': 'item',
                                'name': '{0}'.format(actor.get_name()),
                                'weight': '{0}'.format(1),
                                'in-use': False,
                            }
                            actor_npc.set_python_tag("current_item_prop", item_prop)
                            actor_npc.set_python_tag("used_item_np", actor_bs)
                            actor_npc.set_python_tag("is_item_ready", True)
                        else:
                            actor_npc.set_python_tag("used_item_np", None)
                            actor_npc.set_python_tag("is_item_ready", False)
                            actor_npc.set_python_tag("current_item_prop", None)

        return task.cont
