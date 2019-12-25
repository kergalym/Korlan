"""
BSD 3-Clause License

Copyright (c) 2019, Galym Kerimbekov
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its
   contributors may be used to endorse or promote products derived from
   this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

from panda3d.core import WindowProperties
from direct.showbase import DirectObject
from panda3d.core import NodePath, PandaNode


class Mouse:
    def __init__(self):
        self.base = base
        self.d_object = DirectObject.DirectObject()
        self.korlan = None
        self.floater = None
        self.pos_z = 2.0

    # Create a floater object, which floats 2 units above Korlan.
    # We use this as a target for the camera to look at.
    def set_floater(self, korlan):
        if korlan:
            self.korlan = korlan
            self.floater = NodePath(PandaNode("floater"))
            self.floater.reparentTo(self.korlan)
            self.floater.setZ(self.pos_z)
            return self.floater

    def set_mouse_mode(self, mode):
        if mode:
            wp = WindowProperties()
            wp.setMouseMode(mode)
            self.base.mouseMode = mode
            wp.setCursorHidden(True)
            self.base.win.requestProperties(wp)

            # These changes may require a tick to apply
            self.base.taskMgr.doMethodLater(0, self.resolve_mouse, "Resolve mouse setting")

    def resolve_mouse(self, t):
        wp = self.base.win.getProperties()

        actualMode = wp.getMouseMode()
        if self.base.mouseMode != actualMode:
            self.base.mouseMode = actualMode

        self.base.rotateX, self.base.rotateY = -.5, -.5
        self.base.lastMouseX, self.base.lastMouseY = None, None
        self.recenter_mouse()

        # return task.cont

    def recenter_mouse(self):
        self.base.win.movePointer(0,
                                  int(self.base.win.getProperties().getXSize() / 2),
                                  int(self.base.win.getProperties().getYSize() / 2))

    def toggle_recenter(self):
        self.base.manualRecenterMouse = not self.base.manualRecenterMouse

    def toggle_mouse(self, korlan):
        if korlan:
            self.korlan = korlan
            self.korlan.hideMouse = not base.hideMouse

            wp = WindowProperties()
            wp.setCursorHidden(self.korlan.hideMouse)
            self.korlan.win.requestProperties(wp)

    def mouse_task(self, korlan, task):
        if korlan:
            self.korlan = korlan
            mw = self.base.mouseWatcherNode

            hasMouse = mw.hasMouse()
            if hasMouse:
                # get the window manager's idea of the mouse position
                x, y = mw.getMouseX(), mw.getMouseY()

                if self.base.lastMouseX is not None:
                    # get the delta
                    if self.base.manualRecenterMouse:
                        # when recentering, the position IS the delta
                        # since the center is reported as 0, 0
                        dx, dy = x, y
                    else:
                        dx, dy = x - self.base.lastMouseX, y - self.base.lastMouseY
                else:
                    # no data to compare with yet
                    dx, dy = 0, 0

                self.base.lastMouseX, self.base.lastMouseY = x, y

            else:
                x, y, dx, dy = 0, 0, 0, 0

            if self.base.manualRecenterMouse:
                # move mouse back to center
                self.recenter_mouse()
                self.base.lastMouseX, self.base.lastMouseY = 0, 0

                # scale position and delta to pixels for user
                w, h = self.base.win.getSize()

                # rotate player by delta
                self.base.rotateX += dx * 10 * self.base.mouseMagnitude
                self.base.rotateY += dy * 10 * self.base.mouseMagnitude

                """ enable it only for accept('mouse-3', command=self.korlan.setH(self.base.rotateX))"""
                self.d_object.accept('mouse-1', self.korlan.setH, extraArgs=[self.base.rotateX])
                self.base.cam.setH(self.base.rotateX)

                return task.cont

