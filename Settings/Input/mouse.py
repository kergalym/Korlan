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
        self.mousex = 0
        self.mousey = 0
        self.last = 0

    # Create a floater object, which floats 2 units above Korlan.
    # We use this as a target for the camera to look at.
    def set_floater(self, korlan):
        if korlan:
            self.korlan = korlan
            self.floater = NodePath(PandaNode("floater"))
            self.floater.reparentTo(self.korlan)
            self.floater.setZ(self.pos_z)
            return self.floater

    def mouse_look_cam(self, task):
        # figure out how much the mouse has moved (in pixels)
        if self.base.game_mode:
            md = self.base.win.getPointer(0)
            x = md.getX()
            y = md.getY()
            if self.base.win.movePointer(0, 100, 100):
                self.heading = self.heading - (x - 100) * 0.2
            # self.pitch = self.pitch - (y - 100) * 0.2

            self.base.camera.setHpr(self.heading, self.pitch, self.rotation)

            dir = self.base.camera.getMat().getRow3(1)
            self.base.camera.setPos(self.focus - (dir * 180))
            self.focus = self.base.camera.getPos() + (dir * 180)
            self.last = task.time

            return task.cont

    def set_mouse_mode(self, mode):
        if mode:
            wp = WindowProperties()
            wp.setMouseMode(mode)
            self.base.mouseMode = mode
            wp.setCursorHidden(True)
            self.base.win.requestProperties(wp)
