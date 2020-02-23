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

            OnscreenText(text="DEBUG MODE: Object Position",
                         pos=(-1.8, 0.9),
                         scale=0.03,
                         fg=(255, 255, 255, 0.9),
                         font=self.font.load_font(self.menu_font),
                         align=TextNode.ALeft,
                         mayChange=False)

            OnscreenText(text="ITEM NAME",
                         pos=(-1.8, 0.85),
                         scale=0.03,
                         fg=(255, 255, 255, 0.9),
                         font=self.font.load_font(self.menu_font),
                         align=TextNode.ALeft,
                         mayChange=False)

            OnscreenText(text="ITEM COORDINATES",
                         pos=(-1.35, 0.85),
                         scale=0.03,
                         fg=(255, 255, 255, 0.9),
                         font=self.font.load_font(self.menu_font),
                         align=TextNode.ALeft,
                         mayChange=False)

            self.text_stat_h = OnscreenText(text="_DEBUG_TEXT_",
                                            pos=(-1.8, 0.8),
                                            scale=0.03,
                                            fg=(255, 255, 255, 0.9),
                                            font=self.font.load_font(self.menu_font),
                                            align=TextNode.ALeft,
                                            mayChange=True)

            self.text_stat_p = OnscreenText(text="_DEBUG_TEXT_",
                                            pos=(-1.4, 0.8),
                                            scale=0.03,
                                            fg=(255, 255, 255, 0.9),
                                            font=self.font.load_font(self.menu_font),
                                            align=TextNode.ALeft,
                                            mayChange=True)

            OnscreenText(text="DEBUG MODE: Object State",
                         pos=(-0.6, 0.9),
                         scale=0.03,
                         fg=(255, 255, 255, 0.9),
                         font=self.font.load_font(self.menu_font),
                         align=TextNode.ALeft,
                         mayChange=False)

            OnscreenText(text="IN-USE ITEM NAME",
                         pos=(-0.6, 0.85),
                         scale=0.03,
                         fg=(255, 255, 255, 0.9),
                         font=self.font.load_font(self.menu_font),
                         align=TextNode.ALeft,
                         mayChange=False)

            OnscreenText(text="ITEM STATE",
                         pos=(-0.2, 0.85),
                         scale=0.03,
                         fg=(255, 255, 255, 0.9),
                         font=self.font.load_font(self.menu_font),
                         align=TextNode.ALeft,
                         mayChange=False)

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
                text_far_item = "IS ITEM FAR?: {0}: \n".format(base.is_item_far_to_use)
                records_designed += text_in_use
                records_designed += text_in_use_long
                records_designed += text_near_item
                records_designed += text_far_item
                return records_designed

    def set_stat_text(self, records_h, records_p):
        if (records_h and records_p
                and isinstance(records_h, str)
                and isinstance(records_p, str)):
            if self.game_settings['Debug']['set_debug_mode'] == "YES":
                if base.game_mode and base.menu_mode is False:
                    self.text_stat_h.setText(records_h)
                    self.text_stat_p.setText(records_p)
                elif base.game_mode is False and base.menu_mode is True:
                    self.text_stat_h.destroy()
                    self.text_stat_p.destroy()

    def set_obj_stat_text(self, records_h, records_p):
        if (records_h and records_p
                and isinstance(records_h, str)
                and isinstance(records_p, str)):
            if self.game_settings['Debug']['set_debug_mode'] == "YES":
                if base.game_mode and base.menu_mode is False:
                    self.text_obj_stat_h.setText(records_h)
                    self.text_obj_stat_p.setText(records_p)
                elif base.game_mode is False and base.menu_mode is True:
                    self.text_obj_stat_h.destroy()
                    self.text_obj_stat_p.destroy()

    def show_game_stat_task(self, task):
        if hasattr(base, "player"):
            exclude = ['Sky', 'Mountains', 'Grass', 'Ground', 'NPC']
            dist_vec = base.distance_calculate(
                base.assets_pos_collector_no_actor(base.player, exclude), base.player)
            if dist_vec and base.game_mode:
                dist_vec_fmt_h = self.stat_text_h(dist_vec)
                dist_vec_fmt_p = self.stat_text_p(dist_vec)
                stat_obj_fmt_h = self.stat_obj_text_h()
                stat_obj_fmt_p = self.stat_obj_text_p()
                self.set_stat_text(dist_vec_fmt_h, dist_vec_fmt_p)
                self.set_obj_stat_text(stat_obj_fmt_h, stat_obj_fmt_p)

        return task.cont
