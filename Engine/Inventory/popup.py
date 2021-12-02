from direct.gui.DirectFrame import DirectFrame
from direct.gui.OnscreenText import OnscreenText
from panda3d.core import TextNode


class Popup:
    """ Popup hint for items and slots
    """

    def __init__(self, bg_color, txt_color, font_file):
        self.font = base.loader.loadFont(font_file)
        self.back = DirectFrame(pos=(0, 0, 0),
                                frameColor=bg_color,
                                sortOrder=10000)
        self.back.set_scale(0.07)
        self.info_text = OnscreenText(text=' ',
                                      pos=(0, 0, 0),
                                      fg=txt_color,
                                      mayChange=True,
                                      align=TextNode.ALeft,
                                      font=self.font)
        self.info_text.reparent_to(self.back)
        self.info_text.set_scale(3.0)

        self.states = {
            "HIDDEN": False,
            "VISIBLE": True
        }

        self.current_state = False
        self.hide()

    def hide(self):
        self.back.hide()
        self.current_state = self.states['HIDDEN']

    def show(self, text=None, pos=None, bound=None):
        """ Show hint with 'text' in 'pos' position. 'bound' is bounding
        area to set where hint may be visible.
        """
        if text:
            self.info_text['text'] = text
            sy, sx = self.info_text.textNode.getHeight() * 0.07, self.info_text.textNode.getWidth() * 0.07
            card = self.info_text.textNode.getCardActual()
            card = (card[0] - 0.2, card[1] + 0.2, card[2] - 0.2, card[3] + 0.2)
            self.back['frameSize'] = card
            if pos:
                sy, sx = self.info_text.textNode.getHeight() * 0.07, self.info_text.textNode.getWidth() * 0.07
                x = pos[0] - card[0] * 0.07
                y = pos[2] - card[2] * 0.07
                if bound:
                    l, r, d, u = bound
                    if x + card[1] * 0.07 > r:
                        x = x - ((x + card[1] * 0.07) - r)
                    if x - card[0] * 0.07 < l:
                        x = x + (l - (x - card[0] * 0.07))
                    if y + card[3] * 0.07 > u:
                        y = y - ((y + card[3] * 0.07) - u)
                    if y - card[2] * 0.07 < d:
                        y = y + (d - (y - card[2] * 0.07))

                self.back.setPos((x, pos[1], y))
            self.back.show()

            self.current_state = self.states['VISIBLE']

    def get_size(self):
        sy, sx = self.info_text.textNode.getHeight() * 0.1, self.info_text.textNode.getWidth() * 0.1
        return sx, sy
