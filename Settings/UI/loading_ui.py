from direct.interval.IntervalGlobal import Sequence
from direct.interval.IntervalGlobal import Parallel
from direct.interval.IntervalGlobal import Func
from direct.gui.DirectGui import *
from panda3d.core import FontPool, TextNode
from Engine.Scenes.level_one import LevelOne
from Settings.UI.hud_ui import HudUI
from direct.task.TaskManagerGlobal import taskMgr


class LoadingUI:

    def __init__(self):
        self.level_one = LevelOne()
        self.game_settings = base.game_settings
        self.game_dir = base.game_dir
        self.fonts = base.fonts_collector()
        self.hud = HudUI()
        # instance of the abstract class
        self.font = FontPool

        """ Frames & Bars """
        self.loading_screen = None
        self.loading_frame = None
        self.loading_bar = None
        """ Frame Sizes """
        # Left, right, bottom, top
        self.loading_frame_size = [-2, 2, -1, 1]

        """ Frame Colors """
        self.frm_opacity = 1
        """ Texts & Fonts"""
        # self.menu_font = self.fonts['OpenSans-Regular']
        self.menu_font = self.fonts['JetBrainsMono-Regular']
        self.title_loading_text = None

    def gen_loading_items(self):
        if hasattr(base, "assets_collector"):
            data = base.assets_collector()
            text = None
            for obj in data:
                text = "{0}\n".format(obj)
                text += "{0}\n".format(obj)
            return text

    def set_loading_bar(self):
        if (self.loading_bar
                and self.title_loading_text
                and self.loading_screen):
            self.loading_bar.show()
            self.title_loading_text.show()
            self.loading_screen.show()
        else:
            assets = base.assets_collector()
            data = self.gen_loading_items()
            self.title_loading_text = OnscreenText(text="",
                                                   pos=(-1.8, 0.9),
                                                   scale=0.03,
                                                   fg=(255, 255, 255, 0.9),
                                                   font=self.font.load_font(self.menu_font),
                                                   align=TextNode.ALeft,
                                                   mayChange=True)

            self.loading_bar = DirectWaitBar(
                                             text="",
                                             value=0,
                                             range=100,
                                             pos=(0, 0.4, -0.95))

            self.loading_screen = DirectFrame(frameColor=(0, 0, 0, self.frm_opacity),
                                              frameSize=self.loading_frame_size)
            self.loading_bar.set_scale(0.9, 0, 0.1)
            self.loading_bar.reparent_to(self.loading_screen)
            self.title_loading_text.reparent_to(self.loading_screen)
            self.loading_bar['range'] = len(assets)

    def clear_loading_bar(self):
        if self.loading_bar:
            self.loading_bar.hide()
        if self.loading_screen:
            self.loading_screen.hide()
        if self.title_loading_text:
            self.title_loading_text.hide()

    def loading_measure(self, task):
        assets = base.assets_collector()
        nodes = base.asset_nodes_collector()

        # TODO: Fixme. Make nodes equal to assets without using +2 hack
        for node, asset in zip(nodes, assets):
            if hasattr(node, "get_name"):
                if len(nodes) < len(assets):
                    result = len(nodes)
                    if self.loading_bar:
                        self.loading_bar['value'] += result

                if len(nodes)+2 == len(assets):
                    # self.title_loading_text.setText("Loading finished")
                    self.clear_loading_bar()
                    self.hud.set_hud()
                    return task.done

        return task.cont

    def set_parallel_loading(self, type):
        if type and isinstance(type, str):
            if type == "new_game":
                Sequence(Parallel(Func(self.set_loading_bar),
                                  Func(self.level_one.load_new_game))
                         ).start()
                taskMgr.add(self.loading_measure,
                            "loading_measure",
                            appendTask=True)

            elif type == "load_game":
                self.level_one.load_saved_game()
            elif type == "load_free_game":
                self.level_one.load_free_game()
