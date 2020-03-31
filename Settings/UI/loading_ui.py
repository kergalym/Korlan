from direct.interval.IntervalGlobal import Sequence
from direct.interval.IntervalGlobal import Parallel
from direct.interval.IntervalGlobal import Func
from direct.gui.DirectGui import *
from panda3d.core import FontPool, TextNode
from Engine.Scenes.level_one import LevelOne
from direct.task.TaskManagerGlobal import taskMgr


class LoadingUI:

    def __init__(self):
        self.level_one = LevelOne()
        self.game_settings = base.game_settings
        self.game_dir = base.game_dir
        self.fonts = base.fonts_collector()
        # instance of the abstract class
        self.font = FontPool

        """ Texts & Fonts"""
        # self.menu_font = self.fonts['OpenSans-Regular']
        self.menu_font = self.fonts['JetBrainsMono-Regular']
        self.title_loading_text = OnscreenText(text="",
                                               pos=(-1.8, 0.9),
                                               scale=0.03,
                                               fg=(255, 255, 255, 0.9),
                                               font=self.font.load_font(self.menu_font),
                                               align=TextNode.ALeft,
                                               mayChange=True)
        self.bar = None

    def gen_loading_items(self):
        if hasattr(base, "assets_collector"):
            data = base.assets_collector()
            text = None
            for obj in data:
                text = "{0}\n".format(obj)
                text += "{0}\n".format(obj)
            return text

    def set_loading_bar(self):
        if self.bar:
            self.bar.show()
        else:
            data = self.gen_loading_items()
            self.bar = DirectWaitBar(text="", value=50, pos=(0, .4, .4))
            # self.bar['value'] += data
            text = data
            self.bar.setText(text)

    def clear_loading_bar(self):
        if self.bar:
            self.bar.hide()

    def set_parallel_loading(self, type):
        if type and isinstance(type, str):
            if type == "new_game":
                # TODO: Debug
                Sequence(Parallel(Func(self.set_loading_bar),
                                  Func(self.level_one.load_new_game)),
                         # Func(self.clear_loading_bar)
                         ).start()
            elif type == "load_game":
                self.level_one.load_saved_game()
            elif type == "load_free_game":
                self.level_one.load_free_game()

