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
        self.menu_font_color = (0.8, 0.4, 0, 1)

        self.unloading_text = None
        self.base.game_instance['unloading_is_done'] = 0
        self.unloaded_items = 0

    def set_unloading_screen(self):
        # Disable game overlay
        if self.game_settings['Debug']['set_debug_mode'] == 'NO':
            if self.base.game_instance["game_overlay_np"]:
                self.base.game_instance["game_overlay_np"].destroy()

        self.unloading_text = OnscreenText(text="",
                                           pos=(-1.8, 0.9),
                                           scale=0.03,
                                           fg=self.menu_font_color,
                                           font=self.font.load_font(self.menu_font),
                                           align=TextNode.ALeft,
                                           mayChange=True)

        # set Loading Screen
        self.unloading_screen = DirectFrame(frameColor=(0, 0, 0, self.frm_opacity),
                                            frameSize=self.unloading_frame_size)
        self.unloading_screen.set_name("UnloadingScreen")
        self.unloading_text.reparent_to(self.unloading_screen)
        self.base.build_info.reparent_to(self.unloading_screen)

    def clear_unloading_screen(self):
        if self.unloading_screen:
            self.unloading_screen.hide()
            self.unloading_screen.destroy()
            self.base.build_info.reparent_to(aspect2d)
        if self.unloading_text:
            self.unloading_text.hide()
            self.unloading_text.destroy()

    def unloading_measure(self, task):
        self.base.game_instance['unloading_is_done'] = 0
        if self.base.game_instance['level_assets_np']:
            assets = self.base.game_instance['level_assets_np']
            for num, key in enumerate(assets['name'], start=1):
                if not render.find("**/{0}".format(key)):
                    self.unloaded_items = num

            if (self.unloaded_items == len(assets['name'])
                    and self.base.game_instance['ai_is_activated'] == 0):
                self.base.game_instance['unloading_is_done'] = 1
                self.clear_unloading_screen()
                return task.done

        return task.cont

    def start_unloading(self, type):
        if type and isinstance(type, str):
            if type == "exit_from_game":
                if self.base.shared_functions['unload_game_scene']:
                    unload_game_scene = self.base.shared_functions['unload_game_scene']
                    Sequence(Parallel(Func(unload_game_scene),
                                      Func(self.set_unloading_screen))
                             ).start()
                    taskMgr.add(self.unloading_measure,
                                "unloading_measure",
                                appendTask=True)
