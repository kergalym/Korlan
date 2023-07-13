from Engine import anim_names


class StoryQuests:
    def __init__(self, social_quests):
        self.base = base
        self.render = render
        self.player = None
        self.player_rb_np = None
        self.game_dir = base.game_dir
        self.render_pipeline = None
        if self.base.game_instance["renderpipeline_np"]:
            self.render_pipeline = self.base.game_instance["renderpipeline_np"]
        self._social_quests = social_quests

        self._started_quest_inside_yurt = False

    def start_story_mode_task(self, task):
        if self.base.game_instance['menu_mode']:
            return task.done

        if self.base.game_instance['loading_is_done'] == 1:
            if not self._started_quest_inside_yurt:
                self.start_quest_inside_yurt()
        return task.cont

    def init(self):
        self.player = self.base.game_instance["player_ref"]
        self.player_rb_np = self.base.game_instance["player_np"]

    def start_quest_inside_yurt(self):
        """ Korlan wakes up inside yurt and see... """
        self._started_quest_inside_yurt = True

        yurt_quest_hearth = self.render.find("**/quest_empty_rest_place")
        trigger_np = self.render.find("**/quest_empty_rest_place_trigger")

        if yurt_quest_hearth is None:
            self._started_quest_inside_yurt = False

        if trigger_np is None:
            self._started_quest_inside_yurt = False

        if yurt_quest_hearth is not None:
            self.player_rb_np.set_x(yurt_quest_hearth.get_x())
            self.player_rb_np.set_y(yurt_quest_hearth.get_y())
            self.player_rb_np.set_z(self.player_rb_np.get_z()+7)
            self.base.game_instance["is_indoor"] = True

            if (not base.player_states['is_using']
                    and not base.player_states['is_moving']
                    and not self.base.game_instance['is_aiming']):
                # todo: change to suitable standing_to_laying anim
                if trigger_np is not None:
                    self._social_quests.quest_logic.toggle_laying_state(self.player,
                                                                        yurt_quest_hearth,
                                                                        anim_names.a_anim_stand_lay,
                                                                        anim_names.a_anim_sleeping,
                                                                        "loop")
