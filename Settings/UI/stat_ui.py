from direct.gui.DirectGui import *
from direct.task.TaskManagerGlobal import taskMgr
from panda3d.core import FontPool, TextNode


class StatUI:
    def __init__(self):
        self.game_settings = base.game_settings
        self.game_dir = base.game_dir
        self.fonts = base.fonts_collector()
        # instance of the abstract class
        self.font = FontPool
        self.actions_ui_np = []

        """ Texts & Fonts"""
        # self.menu_font = self.fonts['OpenSans-Regular']
        self.menu_font = self.fonts['JetBrainsMono-Regular']

        if self.game_settings['Debug']['set_debug_mode'] == "YES":
            self.stat_overlay = None
            self.title_dbg_mode_obj_pos = None
            self.title_item_name = None
            self.title_item_dist = None
            self.text_stat_h = None
            self.text_stat_p = None
            self.text_toggle_col = None
            self.title_dbg_mode_obj_state = None
            self.title_inuse_item_name = None
            self.title_item_state = None
            self.text_obj_stat_h = None
            self.text_obj_stat_p = None
            self.title_dbg_mode_player_state = None
            self.text_player_action_stat_p = None
            self.title_dbg_mode_npc_state = None
            self.text_npc_action_stat_p = None

    def set_stat_ui(self):
        self.stat_overlay = DirectFrame(frameColor=(0, 0, 0, 0.5),
                                        frameSize=(-2, 2, -1, 1))

        self.title_dbg_mode_obj_pos = OnscreenText(text="",
                                                   pos=(-1.8, 0.9),
                                                   scale=0.03,
                                                   fg=(0.9, 1, 0, 0.9),
                                                   font=self.font.load_font(self.menu_font),
                                                   align=TextNode.ALeft,
                                                   mayChange=True)

        self.title_item_name = OnscreenText(text="",
                                            pos=(-1.8, 0.85),
                                            scale=0.03,
                                            fg=(0.9, 1, 0, 0.9),
                                            font=self.font.load_font(self.menu_font),
                                            align=TextNode.ALeft,
                                            mayChange=True)

        self.title_item_dist = OnscreenText(text="",
                                            pos=(-1.35, 0.85),
                                            scale=0.03,
                                            fg=(0.9, 1, 0, 0.9),
                                            font=self.font.load_font(self.menu_font),
                                            align=TextNode.ALeft,
                                            mayChange=True)

        self.text_stat_h = OnscreenText(text="",
                                        pos=(-1.8, 0.8),
                                        scale=0.03,
                                        fg=(0.9, 1, 0, 0.9),
                                        font=self.font.load_font(self.menu_font),
                                        align=TextNode.ALeft,
                                        mayChange=True)

        self.text_stat_p = OnscreenText(text="",
                                        pos=(-1.4, 0.8),
                                        scale=0.03,
                                        fg=(0.9, 1, 0, 0.9),
                                        font=self.font.load_font(self.menu_font),
                                        align=TextNode.ALeft,
                                        mayChange=True)

        self.text_toggle_col = OnscreenText(text="",
                                            pos=(-1.8, -0.8),
                                            scale=0.03,
                                            fg=(0.9, 1, 0, 0.9),
                                            font=self.font.load_font(self.menu_font),
                                            align=TextNode.ALeft,
                                            mayChange=True)

        self.title_dbg_mode_obj_state = OnscreenText(text="",
                                                     pos=(-0.6, 0.9),
                                                     scale=0.03,
                                                     fg=(0.9, 1, 0, 0.9),
                                                     font=self.font.load_font(self.menu_font),
                                                     align=TextNode.ALeft,
                                                     mayChange=True)

        self.title_inuse_item_name = OnscreenText(text="",
                                                  pos=(-0.6, 0.85),
                                                  scale=0.03,
                                                  fg=(0.9, 1, 0, 0.9),
                                                  font=self.font.load_font(self.menu_font),
                                                  align=TextNode.ALeft,
                                                  mayChange=True)

        self.title_item_state = OnscreenText(text="",
                                             pos=(-0.2, 0.85),
                                             scale=0.03,
                                             fg=(0.9, 1, 0, 0.9),
                                             font=self.font.load_font(self.menu_font),
                                             align=TextNode.ALeft,
                                             mayChange=True)

        self.text_obj_stat_h = OnscreenText(text="",
                                            pos=(-0.6, 0.8),
                                            scale=0.03,
                                            fg=(0.9, 1, 0, 0.9),
                                            font=self.font.load_font(self.menu_font),
                                            align=TextNode.ALeft,
                                            mayChange=True)

        self.text_obj_stat_p = OnscreenText(text="",
                                            pos=(-0.2, 0.8),
                                            scale=0.03,
                                            fg=(0.9, 1, 0, 0.9),
                                            font=self.font.load_font(self.menu_font),
                                            align=TextNode.ALeft,
                                            mayChange=True)

        self.title_dbg_mode_player_state = OnscreenText(text="",
                                                        pos=(0.5, 0.9),
                                                        scale=0.03,
                                                        fg=(0.9, 1, 0, 0.9),
                                                        font=self.font.load_font(self.menu_font),
                                                        align=TextNode.ALeft,
                                                        mayChange=True)

        self.text_player_action_stat_p = OnscreenText(text="",
                                                      pos=(0.5, 0.8),
                                                      scale=0.03,
                                                      fg=(0.9, 1, 0, 0.9),
                                                      font=self.font.load_font(self.menu_font),
                                                      align=TextNode.ALeft,
                                                      mayChange=True)

        self.title_dbg_mode_npc_state = OnscreenText(text="",
                                                     pos=(0.5, -0.2),
                                                     scale=0.03,
                                                     fg=(0.9, 1, 0, 0.9),
                                                     font=self.font.load_font(self.menu_font),
                                                     align=TextNode.ALeft,
                                                     mayChange=True)

        self.text_npc_action_stat_p = OnscreenText(text="",
                                                   pos=(0.5, -0.3),
                                                   scale=0.03,
                                                   fg=(0.9, 1, 0, 0.9),
                                                   font=self.font.load_font(self.menu_font),
                                                   align=TextNode.ALeft,
                                                   mayChange=True)

    def clear_stat_ui(self):
        self.stat_overlay.destroy()
        self.title_dbg_mode_obj_pos.destroy()
        self.title_item_name.destroy()
        self.title_item_dist.destroy()
        self.text_stat_h.destroy()
        self.text_stat_p.destroy()
        self.text_toggle_col.destroy()
        self.title_dbg_mode_obj_state.destroy()
        self.title_inuse_item_name.destroy()
        self.title_item_state.destroy()
        self.text_obj_stat_h.destroy()
        self.text_obj_stat_p.destroy()
        self.title_dbg_mode_player_state.destroy()
        self.text_player_action_stat_p.destroy()
        self.title_dbg_mode_npc_state.destroy()
        self.text_npc_action_stat_p.destroy()

    def gen_stat_text_h(self, records):
        """ Function    : gen_stat_text_h

            Description : Generate stat text

            Input       : None

            Output      : None

            Return      : String
        """
        if records and isinstance(records, dict):
            records_designed = ''
            for state in records:
                text_h = "{0}: \n".format(state)
                records_designed += text_h
            return records_designed

    def gen_stat_text_p(self, records):
        """ Function    : gen_stat_text_p

            Description : Generate stat text

            Input       : None

            Output      : None

            Return      : String
        """
        if records and isinstance(records, dict):
            records_designed = ''
            for key in records:
                text_dist = "   {0} \n".format(records[key])
                records_designed += text_dist
            return records_designed

    def gen_stat_obj_text_h(self):
        """ Function    : gen_stat_obj_text_h

            Description : Generate stat text

            Input       : None

            Output      : None

            Return      : String
        """
        records_designed = ''
        if hasattr(base, "in_use_item_name"):
            text_h = "{0}: \n".format(base.in_use_item_name)
            records_designed += text_h
            return records_designed

    def gen_stat_obj_text_p(self):
        """ Function    : gen_stat_obj_text_p

            Description : Generate stat text

            Input       : None

            Output      : None

            Return      : String
        """
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

    def gen_stat_npc_action_text_p(self):
        """ Function    : gen_stat_npc_action_text_p

            Description : Generate stat text

            Input       : None

            Output      : None

            Return      : String
        """
        if hasattr(base, "fsm"):
            if base.fsm:
                return "State: {0}\n".format(base.fsm.state)

    def set_stat_text(self, records_h, records_p, set_mode):
        """ Function    : set_stat_text

            Description : Set stat text

            Input       : String

            Output      : None

            Return      : None
        """
        if (records_h and records_p
                and isinstance(records_h, str)
                and isinstance(records_p, str)
                and isinstance(set_mode, str)):
            if self.game_settings['Debug']['set_debug_mode'] == "YES":
                if (not base.game_instance['menu_mode']
                        and set_mode == 'show'):
                    self.stat_overlay.show()
                    self.title_dbg_mode_obj_pos.setText("DEBUG MODE: Objects Position")
                    self.title_item_name.setText("OBJECT NAME")
                    self.title_item_dist.setText("OBJECT DISTANCE (units)")
                    self.text_stat_h.setText(records_h)
                    self.text_stat_p.setText(records_p)
                    msg = "Press F1 to toggle a collision representation"
                    self.text_toggle_col.setText(msg)

                    self.title_dbg_mode_obj_pos.show()
                    self.title_item_name.show()
                    self.title_item_dist.show()
                    self.text_stat_h.show()
                    self.text_stat_p.show()
                    self.text_toggle_col.show()
                elif (base.game_instance['menu_mode']
                      and set_mode == 'hide'):
                    self.stat_overlay.hide()
                    self.title_dbg_mode_obj_pos.hide()
                    self.title_item_name.hide()
                    self.title_item_dist.hide()
                    self.text_stat_h.hide()
                    self.text_stat_p.hide()
                    self.text_toggle_col.hide()

    def set_obj_stat_text(self, records_h, records_p, set_mode):
        """ Function    : set_obj_stat_text

            Description : Set stat text

            Input       : String

            Output      : None

            Return      : None
        """
        if (records_h and records_p
                and isinstance(records_h, str)
                and isinstance(records_p, str)
                and isinstance(set_mode, str)):
            if self.game_settings['Debug']['set_debug_mode'] == "YES":
                if (not base.game_instance['menu_mode']
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

                elif (base.game_instance['menu_mode']
                      and set_mode == 'hide'):
                    self.title_dbg_mode_obj_state.hide()
                    self.title_inuse_item_name.hide()
                    self.title_item_state.hide()
                    self.text_obj_stat_h.hide()
                    self.text_obj_stat_p.hide()

    def set_player_action_stat_text(self, set_mode):
        """ Function    : set_player_action_stat_text

            Description : Generate stat text

            Input       : String

            Output      : None

            Return      : None
        """
        if self.actions_ui_np and isinstance(set_mode, str):
            if self.game_settings['Debug']['set_debug_mode'] == "YES":
                if (not base.game_instance['menu_mode']
                        and set_mode == 'show'):
                    self.title_dbg_mode_player_state.setText("DEBUG MODE: Player State")

                    if hasattr(base, "player_states"):
                        for key, node in zip(base.player_states, self.actions_ui_np):
                            item = "{0}: {1}\n".format(key, base.player_states[key])
                            color = (0.9, 1, 0, 1)
                            if base.player_states[key]:
                                color = (1, 0.1, 0, 1)

                            node.setText(item)
                            node['fg'] = color

                    self.title_dbg_mode_player_state.show()
                    self.text_player_action_stat_p.show()

                elif (base.game_instance['menu_mode']
                      and set_mode == 'hide'):
                    self.title_dbg_mode_player_state.hide()
                    self.text_player_action_stat_p.hide()

    def set_npc_action_stat_text(self, records_p, set_mode):
        """ Function    : set_npc_action_stat_text

            Description : Generate stat text

            Input       : String

            Output      : None

            Return      : None
        """
        if (records_p
                and isinstance(records_p, str)
                and isinstance(set_mode, str)):
            if self.game_settings['Debug']['set_debug_mode'] == "YES":
                if (not base.game_instance['menu_mode']
                        and set_mode == 'show'):
                    self.title_dbg_mode_npc_state.setText("DEBUG MODE: NPC States")
                    self.text_npc_action_stat_p.setText(records_p)
                    self.title_dbg_mode_npc_state.show()
                    self.text_npc_action_stat_p.show()

                elif (base.game_instance['menu_mode']
                      and set_mode == 'hide'):
                    self.title_dbg_mode_npc_state.hide()
                    self.text_npc_action_stat_p.hide()

    def get_actors_distance(self):
        actors = base.game_instance['actors_np']
        player = base.game_instance['player_ref']
        npcs = {}

        for name in actors:
            if actors[name]:
                actor = actors[name]
                dist_vec = actor.get_distance(player)
                npcs[name] = round(dist_vec)

        return npcs

    def show_game_stat_task(self, task):
        """ Function    : show_game_stat_task

            Description : Show the game stat every frame

            Input       : Task

            Output      : None

            Return      : Task event
        """
        if not base.game_instance['menu_mode']:
            dist_vec = self.get_actors_distance()
            dist_vec_fmt_h = self.gen_stat_text_h(dist_vec)
            dist_vec_fmt_p = self.gen_stat_text_p(dist_vec)
            stat_obj_fmt_h = self.gen_stat_obj_text_h()
            stat_obj_fmt_p = self.gen_stat_obj_text_p()
            stat_npc_action_fmt_p = self.gen_stat_npc_action_text_p()
            self.set_stat_text(dist_vec_fmt_h, dist_vec_fmt_p, set_mode='show')
            self.set_obj_stat_text(stat_obj_fmt_h, stat_obj_fmt_p, set_mode='show')
            self.set_player_action_stat_text(set_mode='show')
            self.set_npc_action_stat_text(stat_npc_action_fmt_p, set_mode='show')
            self.text_toggle_col.show()

        elif base.game_instance['menu_mode']:
            self.clear_game_stat()
            return task.done

        return task.cont

    def set_game_stat(self):
        self.set_stat_ui()
        if len(self.actions_ui_np) > 0:
            self.actions_ui_np.clear()
        pos_y = 0.9

        for i in range(len(base.player_states)):
            if i >= 0:
                pos_y -= 0.04

            item = OnscreenText(text="",
                                pos=(0.5, pos_y),
                                scale=0.03,
                                fg=(255, 255, 255, 0.9),
                                font=self.font.load_font(self.menu_font),
                                align=TextNode.ALeft,
                                mayChange=True,
                                parent=self.text_player_action_stat_p)
            self.actions_ui_np.append(item)

        taskMgr.add(self.show_game_stat_task,
                    "show_game_stat_task",
                    appendTask=True)

    def clear_game_stat(self):
        self.clear_stat_ui()
