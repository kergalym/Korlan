from direct.interval.IntervalGlobal import Sequence, Wait
from direct.interval.IntervalGlobal import Parallel
from direct.interval.IntervalGlobal import Func
from direct.gui.DirectGui import *
from direct.showbase.ShowBaseGlobal import aspect2d
from panda3d.core import FontPool, TextNode
from direct.task.TaskManagerGlobal import taskMgr


class UnloadingUI:

    def __init__(self):
        self.base = base
        self.game_settings = base.game_settings
        self.game_dir = base.game_dir
        self.fonts = base.fonts_collector()
        # instance of the abstract class
        self.font = FontPool

        """ Frames & Bars """
        self.unloading_screen = None
        self.unloading_frame = None
        """ Frame Sizes """
        # Left, right, bottom, top
        self.unloading_frame_size = [-2, 2, -1, 1]

        """ Frame Colors """
        self.frm_opacity = 1
        """ Texts & Fonts"""
        self.menu_font = self.fonts['OpenSans-Regular']

        self.unloading_text = None
        self.base.unloading_is_done = 0

    def set_unloading_screen(self):
        if (self.unloading_text
                and self.unloading_screen):
            self.unloading_text.show()
            self.unloading_screen.show()
        else:
            self.unloading_text = OnscreenText(text="",
                                               pos=(-1.8, 0.9),
                                               scale=0.03,
                                               fg=(255, 255, 255, 0.9),
                                               font=self.font.load_font(self.menu_font),
                                               align=TextNode.ALeft,
                                               mayChange=True)
            # remove HUD elements
            if hasattr(base, "hud") and base.hud:
                base.hud.clear_aim_cursor()
                base.hud.clear_day_hud()
                base.hud.clear_player_bar()
                base.hud.clear_weapon_ui()

            # set Loading Screen
            self.unloading_screen = DirectFrame(frameColor=(0, 0, 0, self.frm_opacity),
                                                frameSize=self.unloading_frame_size)
            self.unloading_screen.set_name("UnloadingScreen")
            self.unloading_text.reparent_to(self.unloading_screen)
            self.base.build_info.reparent_to(self.unloading_screen)

    def clear_unloading_screen(self):
        if self.unloading_screen:
            self.unloading_screen.hide()
            self.base.build_info.reparent_to(aspect2d)
        if self.unloading_text:
            self.unloading_text.hide()

    def unloading_measure(self, task):
        self.base.unloading_is_done = 0
        if (base.game_mode is False and base.menu_mode
                and hasattr(self.base, "mouse_control_is_activated")
                and self.base.mouse_control_is_activated == 0):
            self.clear_unloading_screen()
            self.base.unloading_is_done = 1
            return task.done

        return task.cont

    def set_parallel_unloading(self, type):
        if type and isinstance(type, str):
            if type == "exit_from_game":

                # Remove all remained nodes
                if not render.find('**/*').is_empty():
                    render.find('**/*').remove_node()

                if (hasattr(base, 'unload_game_scene')
                        and self.base.unload_game_scene):
                    Sequence(Parallel(Func(self.set_unloading_screen),
                                      Func(self.base.unload_game_scene))
                             ).start()
                    taskMgr.add(self.unloading_measure,
                                "unloading_measure",
                                appendTask=True)
