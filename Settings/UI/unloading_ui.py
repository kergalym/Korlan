from direct.interval.IntervalGlobal import Sequence, Wait
from direct.interval.IntervalGlobal import Parallel
from direct.interval.IntervalGlobal import Func
from direct.gui.DirectGui import *
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
        self.unloading_bar = None
        """ Frame Sizes """
        # Left, right, bottom, top
        self.unloading_frame_size = [-2, 2, -1, 1]

        """ Frame Colors """
        self.frm_opacity = 1
        """ Texts & Fonts"""
        self.menu_font = self.fonts['OpenSans-Regular']

        self.title_unloading_text = None
        self.base.unloading_is_done = 0

    def set_unloading_bar(self):
        if (self.unloading_bar
                and self.title_unloading_text
                and self.unloading_screen):
            self.unloading_bar.show()
            self.title_unloading_text.show()
            self.unloading_screen.show()
        else:
            self.title_unloading_text = OnscreenText(text="",
                                                     pos=(-1.8, 0.9),
                                                     scale=0.03,
                                                     fg=(255, 255, 255, 0.9),
                                                     font=self.font.load_font(self.menu_font),
                                                     align=TextNode.ALeft,
                                                     mayChange=True)

            self.unloading_bar = DirectWaitBar(text="",
                                               value=0,
                                               range=100,
                                               pos=(0, 0.4, -0.95))

            self.unloading_screen = DirectFrame(frameColor=(0, 0, 0, self.frm_opacity),
                                                frameSize=self.unloading_frame_size)
            self.unloading_screen.set_name("LoadingScreen")

            if self.unloading_screen:
                media = base.load_video(file="circle",
                                        type="loading_menu")
                if media:
                    media.set_loop_count(0)
                    media.play()
                    media.set_play_rate(0.5)

            self.unloading_bar.set_scale(0.9, 0, 0.1)
            self.unloading_bar.reparent_to(self.unloading_screen)
            self.title_unloading_text.reparent_to(self.unloading_screen)
            self.unloading_bar['range'] = 1

    def clear_unloading_bar(self):
        if self.unloading_bar:
            self.unloading_bar.hide()
            self.unloading_bar['value'] = 0
        if self.unloading_screen:
            self.unloading_screen.hide()
        if self.title_unloading_text:
            self.title_unloading_text.hide()

    def unloading_measure(self, task):
        self.base.unloading_is_done = 0
        if base.game_mode is False and base.menu_mode:
            if self.unloading_bar:
                Wait(1.0)
                self.unloading_bar['value'] += 1
                self.clear_unloading_bar()
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
                    Sequence(Parallel(Func(self.base.unload_game_scene),
                                      Func(self.set_unloading_bar))
                             ).start()
                    taskMgr.add(self.unloading_measure,
                                "unloading_measure",
                                appendTask=True)
