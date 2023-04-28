from direct.gui.DirectGui import *
from direct.interval.FunctionInterval import Wait, Func
from direct.interval.MetaInterval import Parallel, Sequence
from direct.showbase.ShowBaseGlobal import aspect2d
from panda3d.core import FontPool, TextNode, TransparencyAttrib
from Engine.Scenes.level_one import LevelOne
from direct.task.TaskManagerGlobal import taskMgr
from Settings.UI.rp_lights_manager_ui import RPLightsMgrUI
from Editor.editor import Editor
from Settings.UI.hud_ui import HUD
from Settings.UI.round_table_menu_ui import RoundTableMenu
from Engine.ChestInventory.chest_ui import ChestUI
from Settings.UI.stat_ui import StatUI


class LoadingUI:

    def __init__(self):
        self.base = base
        self.hud = None
        self.round_table_menu = None
        self.chest_inventory = None
        self.level_one = LevelOne()
        self.editor = None
        self.rp_lights_mgr_ui = RPLightsMgrUI()
        self.game_settings = base.game_settings
        self.game_dir = base.game_dir
        self.images = base.textures_collector(path="Settings/UI")
        self.fonts = base.fonts_collector()
        # instance of the abstract class
        self.font = FontPool

        """ Frames & Bars """
        self.fadeout_sequence_is_done = False
        self.fadeout_sequence = None
        self.fadeout_screen = None
        self.loading_screen = None
        self.loading_frame = None
        self.loading_bar = None
        self.loading_bar_image = None
        self.media = None

        """ Frame Sizes """
        # Left, right, bottom, top
        self.loading_frame_size = [-2, 2, -1, 1]

        """ Frame Colors """
        self.frm_opacity = 1

        """ Logo & Ornament Scaling, Positioning """
        self.loading_bar_image_pos = (0, 0.4, -0.90)

        """ Texts & Fonts"""
        self.menu_font = self.fonts['OpenSans-Regular']
        self.menu_font_color = (0.8, 0.4, 0, 1)

        self.title_loading_text = None
        self.base.game_instance['loading_is_done'] = 0
        self.base.game_instance['unloading_is_done'] = 0
        self.base.game_instance["projected_water_is_ready"] = 0

        self.stat_ui = StatUI()

    def set_loading_bar(self):
        self.fadeout_sequence = Sequence()
        self.fadeout_sequence_is_done = False
        self.base.win_props.set_cursor_hidden(True)
        self.base.win.request_properties(self.base.win_props)

        # Enable game overlay
        if self.game_settings['Debug']['set_debug_mode'] == 'NO':
            game_overlay = DirectFrame(frameColor=(0, 0, 0, 0.1),
                                       frameSize=(-2, 2, -1, 1))
            self.base.game_instance["game_overlay_np"] = game_overlay

        assets = base.assets_collector()
        self.title_loading_text = OnscreenText(text="",
                                               pos=(-0.8, -0.73),
                                               scale=0.03,
                                               fg=self.menu_font_color,
                                               font=self.font.load_font(self.menu_font),
                                               align=TextNode.ALeft,
                                               mayChange=True)

        self.loading_bar = DirectWaitBar(text="",
                                         value=0,
                                         range=100,
                                         frameColor=(0.1, 0, 0, self.frm_opacity),
                                         barTexture=self.images['loading_bar_thumb_ui'],
                                         pos=(0, 0.4, -0.90))

        self.loading_screen = DirectFrame(frameColor=(0, 0, 0, self.frm_opacity),
                                          frameSize=self.loading_frame_size,
                                          image=self.images['loading_layout'],
                                          image_scale=(1.9, 1, 1))
        self.loading_screen.set_name("LoadingScreen")
        self.loading_screen.set_transparency(TransparencyAttrib.MAlpha)

        self.loading_bar_image = OnscreenImage(image=self.images['loading_bar_ui'],
                                               pos=self.loading_bar_image_pos)
        self.loading_bar_image.set_scale(0.9, 0, 0.1)
        self.loading_bar_image.set_transparency(TransparencyAttrib.MDual)

        if self.loading_screen:
            self.media = base.load_video(file="circle", type="loading_menu")
            if self.media:
                self.media.set_loop_count(0)
                self.media.play()
                self.media.set_play_rate(0.5)

        self.loading_bar.set_scale(0.76, 0, 0.3)
        self.loading_bar.set_transparency(TransparencyAttrib.MAlpha)
        self.loading_bar.reparent_to(self.loading_screen)
        self.title_loading_text.reparent_to(self.loading_screen)

        if assets:
            self.loading_bar['range'] = len(assets)

    def clear_loading_bar(self):
        if self.loading_bar:
            self.loading_bar.hide()
            self.loading_bar.destroy()
        if self.loading_screen:
            self.loading_screen.hide()
            self.loading_screen.destroy()
            self.base.build_info.reparent_to(aspect2d)
        if self.loading_bar_image:
            self.loading_bar_image.hide()
            self.loading_bar_image.destroy()
        if self.title_loading_text:
            self.title_loading_text.hide()
            self.title_loading_text.destroy()
        if self.media:
            self.media.stop()

    def prepare_to_game(self):
        if self.base.game_instance['loading_is_done'] == 0:
            self.clear_loading_bar()
            if self.game_settings['Debug']['set_editor_mode'] == 'NO':
                self.hud = HUD()
                self.base.game_instance['hud_np'] = self.hud
                self.hud.set_aim_crosshair()
                self.hud.set_day_hud()
                self.hud.set_player_bar()
                self.hud.set_weapon_ui()
                self.round_table_menu = RoundTableMenu()
                self.chest_inventory = ChestUI()
                self.base.game_instance['round_table_menu_np'] = self.round_table_menu
                self.base.game_instance['chest_inventory_np'] = self.chest_inventory
                self.chest_inventory.chest_init()

            if self.game_settings['Debug']['set_debug_mode'] == 'YES':
                self.stat_ui.set_game_stat()

            if self.game_settings['Debug']['set_editor_mode'] == 'YES':
                self.base.win_props.set_cursor_hidden(False)
                self.base.win.request_properties(self.base.win_props)
                self.editor = Editor()
                self.editor.set_editor()

            self.base.game_instance['loading_is_done'] = 1

            self.base.messenger.send("setup_foliage")

            # Remove collider meshes, not needed anymore
            if not render.find("**/Collisions").is_empty():
                render.find("**/Collisions").remove_node()
                render.find("**/Collisions").clear()

            self.set_fadeout_screen()
            taskMgr.add(self.fadeout_task,
                        "fadeout_task",
                        appendTask=True)

    def set_fadeout_screen(self):
        self.fadeout_screen = DirectFrame(frameColor=(0, 0, 0, 1),
                                          frameSize=(-2, 2, -1, 1))

    def decrement_fade(self):
        if self.fadeout_screen:
            alpha = self.fadeout_screen['frameColor'][3]

            if alpha > 0:
                alpha -= 0.1
                self.fadeout_screen['frameColor'] = (0, 0, 0, alpha)
            else:
                self.fadeout_screen.destroy()
                self.fadeout_sequence.finish()
                self.fadeout_sequence = None
                self.fadeout_sequence_is_done = True

    def fadeout_task(self, task):
        if self.fadeout_screen:
            if not self.fadeout_sequence.is_playing():
                par = Parallel(Wait(0.1),
                               Func(self.decrement_fade)
                               )
                self.fadeout_sequence.append(par)
                self.fadeout_sequence.start()

        if self.fadeout_sequence_is_done:
            return task.done

        return task.cont

    def get_loading_queue_list(self, names):
        if isinstance(names, list) and names:
            queue = {}
            num = 0
            for name in names:
                if not render.find("**/{0}".format(name)).is_empty():
                    matched_name = render.find("**/{0}".format(names))
                    queue[name] = matched_name
                    num += 1
            return [queue, num]

    def loading_measure(self, task):
        self.base.game_instance['loading_is_done'] = 0
        if self.base.game_instance['level_assets_np']:
            assets = self.base.game_instance['level_assets_np']
            matched = self.get_loading_queue_list(assets['name'])

            if matched:
                num = matched[1]
                asset_num = len(assets['name'])
                if self.game_settings['Debug']['set_debug_mode'] == "YES":
                    # Exclude game level scene asset
                    asset_num = len(assets['name']) - 1
                self.loading_bar['range'] = asset_num - 1

                if num < asset_num:
                    if self.loading_bar:
                        self.loading_bar['value'] = num
                        # Set loading progress text
                        txt = ''
                        if num <= 1:
                            txt = "Loading asset: {0}\n".format(assets['name'][num])
                        elif num > 1:
                            txt = "Loading asset: {0}\n Loaded: {1}".format(assets['name'][num],
                                                                            assets['name'][num - 1])
                        self.title_loading_text.setText(txt)

                elif num == asset_num:
                    if (self.base.game_instance['player_actions_init_is_activated'] == 1
                            and self.base.game_instance['physics_is_activated'] == 1):
                        last_np = assets['name'][asset_num - 1]
                        if render.find("**/{0}".format(last_np)):
                            self.loading_bar.hide()
                            self.loading_bar_image.hide()

                            txt = "Press Enter to continue..."
                            self.title_loading_text.setText(txt)
                            self.title_loading_text.setScale(0.05)
                            self.title_loading_text['align'] = TextNode.A_center
                            self.title_loading_text['pos'] = (0.0, -0.8)

                            self.base.game_instance["projected_water_is_ready"] = 1

                            self.base.accept('enter', self.prepare_to_game)

                            if self.game_settings['Debug']['set_light_editor_mode'] == 'YES':
                                self.rp_lights_mgr_ui.set_ui_rpmgr()

                            return task.done

        return task.cont

    def start_loading(self, type):
        if type and isinstance(type, str):
            if type == "new_game":
                self.set_loading_bar()
                self.level_one.load_new_game()

                taskMgr.add(self.loading_measure,
                            "loading_measure",
                            appendTask=True)

            elif type == "load_game":
                self.level_one.load_saved_game()
            elif type == "load_free_game":
                self.level_one.load_free_game()
