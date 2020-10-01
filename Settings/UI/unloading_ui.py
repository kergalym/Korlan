from direct.interval.IntervalGlobal import Sequence
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
        self.loading_screen = None
        self.loading_frame = None
        self.loading_bar = None
        """ Frame Sizes """
        # Left, right, bottom, top
        self.loading_frame_size = [-2, 2, -1, 1]

        """ Frame Colors """
        self.frm_opacity = 1
        """ Texts & Fonts"""
        self.menu_font = self.fonts['OpenSans-Regular']

        self.title_loading_text = None
        self.base.loading_is_done = 0
        self.base.unloading_is_done = 0

    def set_loading_bar(self):
        if (self.loading_bar
                and self.title_loading_text
                and self.loading_screen):
            self.loading_bar.show()
            self.title_loading_text.show()
            self.loading_screen.show()
        else:
            assets = base.assets_collector()
            self.title_loading_text = OnscreenText(text="",
                                                   pos=(-1.8, 0.9),
                                                   scale=0.03,
                                                   fg=(255, 255, 255, 0.9),
                                                   font=self.font.load_font(self.menu_font),
                                                   align=TextNode.ALeft,
                                                   mayChange=True)

            self.loading_bar = DirectWaitBar(text="",
                                             value=0,
                                             range=100,
                                             pos=(0, 0.4, -0.95))

            self.loading_screen = DirectFrame(frameColor=(0, 0, 0, self.frm_opacity),
                                              frameSize=self.loading_frame_size)
            self.loading_screen.set_name("LoadingScreen")

            if self.loading_screen:
                media = base.load_video(file="circle",
                                        type="loading_menu")
                if media:
                    media.set_loop_count(0)
                    media.play()
                    media.set_play_rate(0.5)

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

    def unloading_measure(self, task):
        self.base.unloading_is_done = 0
        if hasattr(base, "level_assets"):
            assets = base.level_assets
            matched = self.get_loading_queue_list(assets['name'])  # unload

            # TODO: Debug
            if matched:
                num = matched[1]
                asset_num = len(assets['name'])

                if num < asset_num:
                    if self.loading_bar:
                        self.loading_bar['value'] += num

                if num == 0:
                    self.clear_loading_bar()

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
                                      Func(self.set_loading_bar))
                             ).start()
                    taskMgr.add(self.unloading_measure,
                                "unloading_measure",
                                appendTask=True)
