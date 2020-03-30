from direct.interval.IntervalGlobal import Parallel
from direct.interval.IntervalGlobal import Func
from direct.gui.DirectGui import *
from panda3d.core import FontPool, TextNode


class LoadingUI:

    def __init__(self):
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

    def gen_loading_items(self):
        pass

    def set_loading_items(self):
        pass
