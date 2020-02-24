from direct.gui.DirectGui import *
from panda3d.core import FontPool, TextNode


class UIStat:
    def __init__(self):
        self.game_settings = base.game_settings
        self.game_dir = base.game_dir
        # instance of the abstract class
        self.font = FontPool
        self.menu_font = '{0}/Settings/UI/JetBrainsMono-1.0.2/ttf/JetBrainsMono-Regular.ttf'.format(self.game_dir)
        if self.game_settings['Debug']['set_debug_mode'] == "YES":
            self.title_dbg_mode_obj_pos = OnscreenText(text="",
                                                       pos=(-1.8, 0.9),
                                                       scale=0.03,
                                                       fg=(255, 255, 255, 0.9),
                                                       font=self.font.load_font(self.menu_font),
                                                       align=TextNode.ALeft,
                                                       mayChange=True)

            self.title_item_name = OnscreenText(text="",
                                                pos=(-1.8, 0.85),
                                                scale=0.03,
                                                fg=(255, 255, 255, 0.9),
                                                font=self.font.load_font(self.menu_font),
                                                align=TextNode.ALeft,
                                                mayChange=True)

            self.title_item_coord = OnscreenText(text="",
                                                 pos=(-1.35, 0.85),
                                                 scale=0.03,
                                                 fg=(255, 255, 255, 0.9),
                                                 font=self.font.load_font(self.menu_font),
                                                 align=TextNode.ALeft,
                                                 mayChange=True)

            self.text_stat_h = OnscreenText(text="",
                                            pos=(-1.8, 0.8),
                                            scale=0.03,
                                            fg=(255, 255, 255, 0.9),
                                            font=self.font.load_font(self.menu_font),
                                            align=TextNode.ALeft,
                                            mayChange=True)

            self.text_stat_p = OnscreenText(text="",
                                            pos=(-1.4, 0.8),
                                            scale=0.03,
                                            fg=(255, 255, 255, 0.9),
                                            font=self.font.load_font(self.menu_font),
                                            align=TextNode.ALeft,
                                            mayChange=True)

            self.title_dbg_mode_obj_state = OnscreenText(text="",
                                                         pos=(-0.6, 0.9),
                                                         scale=0.03,
                                                         fg=(255, 255, 255, 0.9),
                                                         font=self.font.load_font(self.menu_font),
                                                         align=TextNode.ALeft,
                                                         mayChange=True)

            self.title_inuse_item_name = OnscreenText(text="",
                                                      pos=(-0.6, 0.85),
                                                      scale=0.03,
                                                      fg=(255, 255, 255, 0.9),
                                                      font=self.font.load_font(self.menu_font),
                                                      align=TextNode.ALeft,
                                                      mayChange=True)

            self.title_item_state = OnscreenText(text="",
                                                 pos=(-0.2, 0.85),
                                                 scale=0.03,
                                                 fg=(255, 255, 255, 0.9),
                                                 font=self.font.load_font(self.menu_font),
                                                 align=TextNode.ALeft,
                                                 mayChange=True)

            self.text_obj_stat_h = OnscreenText(text="",
                                                pos=(-0.6, 0.8),
                                                scale=0.03,
                                                fg=(255, 255, 255, 0.9),
                                                font=self.font.load_font(self.menu_font),
                                                align=TextNode.ALeft,
                                                mayChange=True)

            self.text_obj_stat_p = OnscreenText(text="",
                                                pos=(-0.2, 0.8),
                                                scale=0.03,
                                                fg=(255, 255, 255, 0.9),
                                                font=self.font.load_font(self.menu_font),
                                                align=TextNode.ALeft,
                                                mayChange=True)

            self.title_dbg_mode_player_state = OnscreenText(text="",
                                                            pos=(0.4, 0.9),
                                                            scale=0.03,
                                                            fg=(255, 255, 255, 0.9),
                                                            font=self.font.load_font(self.menu_font),
                                                            align=TextNode.ALeft,
                                                            mayChange=True)

            self.text_player_action_stat_p = OnscreenText(text="",
                                                          pos=(0.4, 0.8),
                                                          scale=0.03,
                                                          fg=(255, 255, 255, 0.9),
                                                          font=self.font.load_font(self.menu_font),
                                                          align=TextNode.ALeft,
                                                          mayChange=True)

    def stat_text_h(self, records):
        if records and isinstance(records, dict):
            records_designed = ''
            for state in records:
                text_h = "{0}: \n".format(state)
                records_designed += text_h
            return records_designed

    def stat_text_p(self, records):
        if records and isinstance(records, dict):
            records_designed = ''
            for state in records:
                text_x = "  X: {0} ".format(records[state][0])
                text_y = "  Y: {0} ".format(records[state][1])
                text_z = "  Z: {0} \n".format(records[state][2])
                records_designed += text_x
                records_designed += text_y
                records_designed += text_z
            return records_designed

    def stat_obj_text_h(self):
        records_designed = ''
        if hasattr(base, "in_use_item_name"):
            text_h = "{0}: \n".format(base.in_use_item_name)
            records_designed += text_h
            return records_designed

    def stat_obj_text_p(self):
        if (hasattr(base, "is_item_close_to_use")
                and hasattr(base, "is_item_far_to_use")
                and hasattr(base, "is_item_in_use")
                and hasattr(base, "is_item_in_use_long")):
            records_designed = ''
            if hasattr(base, "close_item_name"):
                text_in_use = "IN-USE: {0}: \n".format(base.is_item_in_use)
                text_in_use_long = "LONG IN-USE: {0}: \n".format(base.is_item_in_use_long)
                text_near_item = "IS ITEM CLOSE?: {0}: \n".format(base.is_item_close_to_use)
                records_designed += text_in_use
                records_designed += text_in_use_long
                records_designed += text_near_item
                return records_designed

    def stat_player_action_text_p(self):
        if hasattr(base, "states"):
            records_designed = ''
            for key in base.states:
                records_designed += "{0}: {1}\n".format(key, base.states[key])
            return records_designed

    def set_stat_text(self, records_h, records_p, set_mode):
        if (records_h and records_p
                and isinstance(records_h, str)
                and isinstance(records_p, str)
                and isinstance(set_mode, str)):
            if self.game_settings['Debug']['set_debug_mode'] == "YES":
                if (base.game_mode
                        and base.menu_mode is False
                        and set_mode == 'show'):

                    self.title_dbg_mode_obj_pos.setText("DEBUG MODE: Objects Position")
                    self.title_item_name.setText("ITEM NAME")
                    self.title_item_coord.setText("ITEM COORDINATES")
                    self.text_stat_h.setText(records_h)
                    self.text_stat_p.setText(records_p)

                    self.title_dbg_mode_obj_pos.show()
                    self.title_item_name.show()
                    self.title_item_coord.show()
                    self.text_stat_h.show()
                    self.text_stat_p.show()
                elif (base.game_mode is False
                      and base.menu_mode is True
                      and set_mode == 'hide'):
                    self.title_dbg_mode_obj_pos.hide()
                    self.title_item_name.hide()
                    self.title_item_coord.hide()
                    self.text_stat_h.hide()
                    self.text_stat_p.hide()

    def set_obj_stat_text(self, records_h, records_p, set_mode):
        if (records_h and records_p
                and isinstance(records_h, str)
                and isinstance(records_p, str)
                and isinstance(set_mode, str)):
            if self.game_settings['Debug']['set_debug_mode'] == "YES":
                if (base.game_mode
                        and base.menu_mode is False
                        and set_mode == 'show'):
                    self.title_dbg_mode_obj_state.setText("DEBUG MODE: Character State")
                    self.title_inuse_item_name.setText("IN-USE ITEM NAME")
                    self.title_item_state.setText("ITEM STATE")
                    self.text_obj_stat_h.setText(records_h)
                    self.text_obj_stat_p.setText(records_p)

                    self.title_dbg_mode_obj_state.show()
                    self.title_inuse_item_name.show()
                    self.title_item_state.show()
                    self.text_obj_stat_h.show()
                    self.text_obj_stat_p.show()

                elif (base.game_mode is False
                      and base.menu_mode is True
                      and set_mode == 'hide'):
                    self.title_dbg_mode_obj_state.hide()
                    self.title_inuse_item_name.hide()
                    self.title_item_state.hide()
                    self.text_obj_stat_h.hide()
                    self.text_obj_stat_p.hide()

    def set_player_action_stat_text(self, records_p, set_mode):
        if (records_p
                and isinstance(records_p, str)
                and isinstance(set_mode, str)):
            if self.game_settings['Debug']['set_debug_mode'] == "YES":
                if (base.game_mode
                        and base.menu_mode is False
                        and set_mode == 'show'):
                    self.title_dbg_mode_player_state.setText("DEBUG MODE: Character Actions")
                    self.text_player_action_stat_p.setText(records_p)

                    self.title_dbg_mode_player_state.show()
                    self.text_player_action_stat_p.show()

                elif (base.game_mode is False
                      and base.menu_mode is True
                      and set_mode == 'hide'):
                    self.title_dbg_mode_player_state.hide()
                    self.text_player_action_stat_p.hide()

    def show_game_stat_task(self, task):
        if hasattr(base, "player"):
            exclude = ['Sky', 'Mountains', 'Grass', 'Ground', 'NPC']
            dist_vec = base.distance_calculate(
                base.assets_pos_collector_no_actor(base.player, exclude), base.player)
            if (dist_vec and base.game_mode is True
                    and base.menu_mode is False):
                dist_vec_fmt_h = self.stat_text_h(dist_vec)
                dist_vec_fmt_p = self.stat_text_p(dist_vec)
                stat_obj_fmt_h = self.stat_obj_text_h()
                stat_obj_fmt_p = self.stat_obj_text_p()
                stat_player_action_fmt_p = self.stat_player_action_text_p()
                self.set_stat_text(dist_vec_fmt_h, dist_vec_fmt_p, set_mode='show')
                self.set_obj_stat_text(stat_obj_fmt_h, stat_obj_fmt_p, set_mode='show')
                self.set_player_action_stat_text(stat_player_action_fmt_p, set_mode='show')
            if (dist_vec and base.game_mode is False
                    and base.menu_mode is True):
                dist_vec_fmt_h = self.stat_text_h(dist_vec)
                dist_vec_fmt_p = self.stat_text_p(dist_vec)
                stat_obj_fmt_h = self.stat_obj_text_h()
                stat_obj_fmt_p = self.stat_obj_text_p()
                stat_player_action_fmt_p = self.stat_player_action_text_p()
                self.set_stat_text(dist_vec_fmt_h, dist_vec_fmt_p, set_mode='hide')
                self.set_obj_stat_text(stat_obj_fmt_h, stat_obj_fmt_p, set_mode='hide')
                self.set_player_action_stat_text(stat_player_action_fmt_p, set_mode='hide')
                return task.done
        return task.cont
