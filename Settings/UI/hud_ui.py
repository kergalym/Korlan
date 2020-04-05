from direct.gui.DirectGui import *
from direct.gui.OnscreenImage import TransparencyAttrib
from panda3d.core import FontPool, TextNode


class HudUI:
    def __init__(self):
        self.game_settings = base.game_settings
        self.game_dir = base.game_dir
        self.images = base.textures_collector(path="{0}/Settings/UI".format(self.game_dir))
        self.fonts = base.fonts_collector()
        # instance of the abstract class
        self.font = FontPool

        """ Frames & Bars """
        self.hud_avatar = None
        self.hud_row_frame_1 = None
        self.hud_row_frame_2 = None
        self.hud_row_frame_3 = None
        self.hud_row_frame_4 = None
        self.hud_row_frame_5 = None
        self.hud_row_frame_6 = None

        """ Frame Sizes """
        # Left, right, bottom, top
        self.hud_row_frame_size = [-0.5, 0.5, -0.5, 0.5]

        """ Scales """
        self.hud_row_frame_scale = (0.15, 0, 0.15)

        """ Frame Colors """
        self.frm_opacity = 1
        """ Texts & Fonts"""
        # self.menu_font = self.fonts['OpenSans-Regular']
        self.menu_font = self.fonts['JetBrainsMono-Regular']

    def gen_hud_data(self):
        pass

    def set_hud(self):
        if (self.hud_avatar
                and self.hud_row_frame_1
                and self.hud_row_frame_2
                and self.hud_row_frame_3
                and self.hud_row_frame_4
                and self.hud_row_frame_5
                and self.hud_row_frame_6):
            self.hud_avatar.show()
            self.hud_row_frame_1.show()
            self.hud_row_frame_2.show()
            self.hud_row_frame_3.show()
            self.hud_row_frame_4.show()
            self.hud_row_frame_5.show()
            self.hud_row_frame_6.show()
        else:
            self.hud_avatar = OnscreenImage(image=self.images["player_avatar"])

            self.hud_row_frame_1 = DirectFrame(frameColor=(0, 0, 0, self.frm_opacity),
                                               frameSize=self.hud_row_frame_size)
            self.hud_row_frame_2 = DirectFrame(frameColor=(0, 0, 0, self.frm_opacity),
                                               frameSize=self.hud_row_frame_size)
            self.hud_row_frame_3 = DirectFrame(frameColor=(0, 0, 0, self.frm_opacity),
                                               frameSize=self.hud_row_frame_size)
            self.hud_row_frame_4 = DirectFrame(frameColor=(0, 0, 0, self.frm_opacity),
                                               frameSize=self.hud_row_frame_size)
            self.hud_row_frame_5 = DirectFrame(frameColor=(0, 0, 0, self.frm_opacity),
                                               frameSize=self.hud_row_frame_size)
            self.hud_row_frame_6 = DirectFrame(frameColor=(0, 0, 0, self.frm_opacity),
                                               frameSize=self.hud_row_frame_size)

            hud_row_text_1 = OnscreenText(text="",
                                          pos=(0.20, 0, 0.90),
                                          scale=0.2,
                                          fg=(255, 255, 255, 0.9),
                                          font=self.font.load_font(self.menu_font),
                                          align=TextNode.ALeft,
                                          mayChange=True)
            hud_row_text_2 = OnscreenText(text="",
                                          pos=(0.40, 0, 0.90),
                                          scale=0.2,
                                          fg=(255, 255, 255, 0.9),
                                          font=self.font.load_font(self.menu_font),
                                          align=TextNode.ALeft,
                                          mayChange=True)
            hud_row_text_3 = OnscreenText(text="",
                                          pos=(0.52, 0, 0.90),
                                          scale=0.2,
                                          fg=(255, 255, 255, 0.9),
                                          font=self.font.load_font(self.menu_font),
                                          align=TextNode.ALeft,
                                          mayChange=True)
            hud_row_text_4 = OnscreenText(text="",
                                          pos=(-0.52, 0, 0.90),
                                          scale=0.2,
                                          fg=(255, 255, 255, 0.9),
                                          font=self.font.load_font(self.menu_font),
                                          align=TextNode.ALeft,
                                          mayChange=True)
            hud_row_text_5 = OnscreenText(text="",
                                          pos=(-0.40, 0, 0.90),
                                          scale=0.2,
                                          fg=(255, 255, 255, 0.9),
                                          font=self.font.load_font(self.menu_font),
                                          align=TextNode.ALeft,
                                          mayChange=True)
            hud_row_text_6 = OnscreenText(text="",
                                          pos=(-0.20, 0, 0.90),
                                          scale=0.2,
                                          fg=(255, 255, 255, 0.9),
                                          font=self.font.load_font(self.menu_font),
                                          align=TextNode.ALeft,
                                          mayChange=True)

            self.hud_avatar.set_transparency(TransparencyAttrib.MAlpha)
            self.hud_avatar.set_name("player_avatar")
            self.hud_avatar.set_pos(0, 0.4, -0.83)
            self.hud_avatar.set_scale(0.3, 0.3, 0.15)

            self.hud_row_frame_1.set_pos(0.28, 0.4, -0.90)
            self.hud_row_frame_2.set_pos(0.45, 0.4, -0.90)

            self.hud_row_frame_3.set_pos(0.62, 0.4, -0.90)
            self.hud_row_frame_4.set_pos(-0.62, 0.4, -0.90)

            self.hud_row_frame_5.set_pos(-0.45, 0.4, -0.90)
            self.hud_row_frame_6.set_pos(-0.28, 0.4, -0.90)

            self.hud_row_frame_1.set_name("hud_row_1")
            self.hud_row_frame_2.set_name("hud_row_2")
            self.hud_row_frame_3.set_name("hud_row_3")
            self.hud_row_frame_4.set_name("hud_row_4")
            self.hud_row_frame_5.set_name("hud_row_5")
            self.hud_row_frame_6.set_name("hud_row_6")

            self.hud_row_frame_1.set_scale(self.hud_row_frame_scale)
            self.hud_row_frame_2.set_scale(self.hud_row_frame_scale)
            self.hud_row_frame_3.set_scale(self.hud_row_frame_scale)
            self.hud_row_frame_4.set_scale(self.hud_row_frame_scale)
            self.hud_row_frame_5.set_scale(self.hud_row_frame_scale)
            self.hud_row_frame_6.set_scale(self.hud_row_frame_scale)

            hud_row_text_1.setText("Skill 1")
            hud_row_text_2.setText("Skill 2")
            hud_row_text_3.setText("Skill 3")
            hud_row_text_4.setText("Skill 4")
            hud_row_text_5.setText("Skill 5")
            hud_row_text_6.setText("Skill 6")

            hud_row_text_1.reparent_to(self.hud_row_frame_1)
            hud_row_text_2.reparent_to(self.hud_row_frame_2)
            hud_row_text_3.reparent_to(self.hud_row_frame_3)
            hud_row_text_4.reparent_to(self.hud_row_frame_4)
            hud_row_text_5.reparent_to(self.hud_row_frame_5)
            hud_row_text_6.reparent_to(self.hud_row_frame_6)

            hud_row_text_1.set_pos(-0.59, 0.4, -0.30)
            hud_row_text_2.set_pos(-0.76, 0.4, -0.30)

            hud_row_text_3.set_pos(-0.92, 0.4, -0.30)
            hud_row_text_4.set_pos(0.18, 0.4, -0.30)

            hud_row_text_5.set_pos(-0.10, 0.4, -0.30)
            hud_row_text_6.set_pos(-0.20, 0.4, -0.30)

    def clear_hud(self):
        if (self.hud_avatar
                and self.hud_row_frame_1
                and self.hud_row_frame_2
                and self.hud_row_frame_3
                and self.hud_row_frame_4
                and self.hud_row_frame_5
                and self.hud_row_frame_6):
            self.hud_avatar.hide()
            self.hud_row_frame_1.hide()
            self.hud_row_frame_2.hide()
            self.hud_row_frame_3.hide()
            self.hud_row_frame_4.hide()
            self.hud_row_frame_5.hide()
            self.hud_row_frame_6.hide()
        else:
            # if hud rows aren't part of HudUI class, but exist,
            # then find them and hide
            if (not render2d.find("**/hud_row_1").is_empty()
                    and not render2d.find("**/hud_row_2").is_empty()
                    and not render2d.find("**/hud_row_3").is_empty()
                    and not render2d.find("**/hud_row_4").is_empty()
                    and not render2d.find("**/hud_row_5").is_empty()
                    and not render2d.find("**/hud_row_6").is_empty()):
                render2d.find("**/hud_row_1").hide()
                render2d.find("**/hud_row_2").hide()
                render2d.find("**/hud_row_3").hide()
                render2d.find("**/hud_row_4").hide()
                render2d.find("**/hud_row_5").hide()
                render2d.find("**/hud_row_6").hide()

            if not render2d.find("**/player_avatar").is_empty():
                render2d.find("**/player_avatar").hide()
