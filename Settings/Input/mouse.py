from panda3d.core import WindowProperties, LVector3
from direct.showbase import DirectObject
from panda3d.core import NodePath, PandaNode


class Mouse:
    def __init__(self):
        self.base = base
        self.d_object = DirectObject.DirectObject()
        self.korlan = None
        self.floater = None
        self.pos_z = 1.0
        # Set the current viewing target
        # self.focus = LVector3(55, -55, 20)
        self.focus = LVector3(0, 0, 0)
        self.heading = 180
        self.pitch = 150
        self.rotation = 0
        self.mouse_x = 0
        self.mouse_y = 0
        self.last = 0

    # Create a floater object, which floats 2 units above Korlan.
    # We use this as a target for the camera to look at.
    def set_floater(self, korlan):
        if korlan:
            self.korlan = korlan
            self.floater = NodePath(PandaNode("floater"))
            self.floater.reparent_to(self.korlan)
            self.floater.set_z(self.pos_z)
            return self.floater

    def mouse_look_cam(self, task):
        # figure out how much the mouse has moved (in pixels)
        if self.base.game_mode:
            md = self.base.win.getPointer(0)
            x = md.get_x()
            y = md.get_y()
            if self.base.win.move_pointer(0, 100, 100):
                self.heading = self.heading - (x - 100) * 0.2
            # self.pitch = self.pitch - (y - 100) * 0.2

            self.base.camera.set_hpr(self.heading, self.pitch, self.rotation)

            dir = self.base.camera.get_mat().getRow3(1)
            self.base.camera.set_pos(self.focus - (dir * 180))
            self.focus = self.base.camera.get_pos() + (dir * 180)
            self.last = task.time

            return task.cont

    def set_mouse_mode(self, mode):
        if mode:
            wp = WindowProperties()
            wp.set_mouse_mode(mode)
            self.base.mouse_mode = mode
            wp.set_cursor_hidden(True)
            self.base.win.request_properties(wp)
