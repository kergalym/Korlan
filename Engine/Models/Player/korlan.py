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
from panda3d.core import CollisionTraverser, CollisionNode, LPoint3f
from panda3d.core import CollisionHandlerQueue, CollisionRay
from panda3d.core import CollideMask
from pathlib import Path
from Engine.Collisions import Collisions
from Engine import set_tex_transparency
from direct.actor.Actor import Actor
from panda3d.core import WindowProperties, NodePath, PandaNode, MouseButton, Shader, Spotlight, DirectionalLight
from direct.task.TaskManagerGlobal import taskMgr
from direct.showbase import DirectObject
from direct.showbase.ShowBase import LODNode

from Engine.World import World


class Korlan:

    def __init__(self):
        self.scale_x = 1.25
        self.scale_y = 1.25
        self.scale_z = 1.25
        self.pos_x = -1.5
        self.pos_y = 9.8
        self.pos_z = -3.2
        self.rot_h = -0.10

        # Panda3D 1.10 and Blender 2.8 have different coordinate systems,
        # and the exporter does not convert them yet.
        # Fix the wrong position of the model to setting it to -180:
        self.rot_p = 0
        self.rot_r = 0

        self.cam_pos_x = 7.0
        self.cam_pos_y = 17.8
        self.cam_pos_z = 2.5
        self.scene = None
        self.korlan = None
        self.base = base
        self.taskMgr = taskMgr
        self.mmb = MouseButton()
        self.d_object = DirectObject.DirectObject()

        self.col = Collisions()
        self.isMoving = False
        self.world = World()

    def set_character(self, render_type, game_settings, model,
                      game_dir, player_path, cfg_path, render, anim):

        # Disable the camera trackball controls.
        self.base.disableMouse()

        # control mapping of mouse movement to character movement
        self.base.mouseMagnitude = 1

        self.base.rotateX = 0

        self.base.lastMouseX = None

        self.base.hideMouse = False

        self.set_mouse_mode(WindowProperties.M_absolute)
        self.base.manualRecenterMouse = True

        if (isinstance(player_path, str)
                and game_settings
                and isinstance(model, str)
                and game_dir
                and isinstance(render_type, str)
                and isinstance(cfg_path, str)
                and anim
                and isinstance(anim, str)
                and render):

            if render_type == 'menu':

                try:
                    game_settings.read(cfg_path)
                    self.pos_x = float(game_settings['Debug']['player_pos_x'])
                    self.pos_y = float(game_settings['Debug']['player_pos_y'])
                    self.pos_z = float(game_settings['Debug']['player_pos_z'])
                    self.rot_h = float(game_settings['Debug']['player_rot_h'])
                    self.rot_p = float(game_settings['Debug']['player_rot_p'])
                    self.rot_r = float(game_settings['Debug']['player_rot_r'])
                except KeyError:
                    game_settings.read("{}/Korlan/Configs/default_config.ini".format(str(Path.home())))
                    self.pos_x = float(game_settings['Debug']['player_pos_x'])
                    self.pos_y = float(game_settings['Debug']['player_pos_y'])
                    self.pos_z = float(game_settings['Debug']['player_pos_z'])
                    self.rot_h = float(game_settings['Debug']['player_rot_h'])
                    self.rot_p = float(game_settings['Debug']['player_rot_p'])
                    self.rot_r = float(game_settings['Debug']['player_rot_r'])
                except ValueError:
                    game_settings.read("{}/Korlan/Configs/default_config.ini".format(str(Path.home())))
                    self.pos_x = float(game_settings['Debug']['player_pos_x'])
                    self.pos_y = float(game_settings['Debug']['player_pos_y'])
                    self.pos_z = float(game_settings['Debug']['player_pos_z'])
                    self.rot_h = float(game_settings['Debug']['player_rot_h'])
                    self.rot_p = float(game_settings['Debug']['player_rot_p'])
                    self.rot_r = float(game_settings['Debug']['player_rot_r'])

                props = WindowProperties()
                props.setCursorHidden(False)
                base.win.requestProperties(props)

                model_dir = model
                self.scene = Actor(player_path,
                                   {anim: "{0}/Assets/Models/{1}/{2}".format(game_dir, model_dir, anim)})

                # TODO rename game_char to self.korlan for consistency.
                game_char = self.scene
                game_char.setName(model)
                game_char.setScale(game_char, self.scale_x, self.scale_y, self.scale_z)
                game_char.setPos(self.pos_x, self.pos_y, self.pos_z)
                game_char.setH(game_char, self.rot_h)
                game_char.setP(game_char, self.rot_p)
                game_char.setR(game_char, self.rot_r)
                self.korlan = game_char
                self.korlan.loop(anim)
                self.korlan.setPlayRate(8.0, anim)

                # Panda3D 1.10 doesn't enable alpha blending for textures by default
                set_tex_transparency(self.korlan)

                self.korlan.reparentTo(render)

                # Set lights and Shadows
                if game_settings['Main']['postprocessing'] == 'off':
                    # self.world.set_shadows(self.korlan, render)
                    self.world.set_lighting(render, self.korlan)
                # self.world.set_ssao(self.korlan)

                if game_settings['Debug']['set_debug_mode'] == "YES":
                    render.analyze()
                    render.explore()

                # TODO: LOD setup (move to Settings soon)
                lod = LODNode('LOD')
                lod_np = NodePath(lod)
                lod_np.reparentTo(render)
                lod.addSwitch(5.0, 0.0)

                # Collisions
                # self.col.player_col(self.korlan)

    def set_character_game(self, render_type, game_settings, model,
                           axis, rotation, scale, game_dir,
                           player_path, cfg_path, render, anim):

        # Disable the camera trackball controls.
        self.base.disableMouse()

        # control mapping of mouse movement to character movement
        self.base.mouseMagnitude = 1

        self.base.rotateX = 0

        self.base.lastMouseX = None

        self.base.hideMouse = False

        self.set_mouse_mode(WindowProperties.M_absolute)
        self.base.manualRecenterMouse = True

        if (isinstance(player_path, str)
                and isinstance(model, str)
                and isinstance(axis, list)
                and isinstance(rotation, list)
                and isinstance(scale, list)
                and isinstance(game_dir, str)
                and isinstance(render_type, str)
                and isinstance(cfg_path, dict)
                and isinstance(anim, str)
                and render):
            self.pos_x = axis[0]
            self.pos_y = axis[1]
            self.pos_z = axis[2]
            self.rot_h = rotation[0]
            self.rot_p = rotation[1]
            self.rot_r = rotation[2]
            self.scale_x = scale[0]
            self.scale_y = scale[1]
            self.scale_z = scale[2]

            props = WindowProperties()
            props.setCursorHidden(True)
            base.win.requestProperties(props)

            model_dir = model
            KorlanStartPos = LPoint3f(self.pos_x, self.pos_y, 0.0)
            self.scene = Actor(player_path,
                               {anim: "{0}/Assets/Models/{1}/{2}".format(game_dir, model_dir, anim)})

            # TODO rename game_char to self.korlan for consistency.
            game_char = self.scene
            game_char.setName(model)
            game_char.setScale(game_char, self.scale_x, self.scale_y, self.scale_z)
            game_char.setPos(KorlanStartPos + (0, 0, self.pos_z))
            game_char.setH(game_char, self.rot_h)
            game_char.setP(game_char, self.rot_p)
            game_char.setR(game_char, self.rot_r)
            self.korlan = game_char

            # Panda3D 1.10 doesn't enable alpha blending for textures by default
            set_tex_transparency(self.korlan)

            self.korlan.reparentTo(render)

            # Set lights and Shadows
            if game_settings['Main']['postprocessing'] == 'off':
                # self.world.set_shadows(self.korlan, render)
                self.world.set_lighting(render, self.korlan)
            # self.world.set_ssao(self.korlan)

            if game_settings['Debug']['set_debug_mode'] == "YES":
                render.analyze()
                render.explore()

            # TODO: LOD setup (move to Settings soon)
            lod = LODNode('LOD')
            lod_np = NodePath(lod)
            lod_np.reparentTo(render)
            lod.addSwitch(5.0, 0.0)

            # Collisions
            # self.col.player_col(self.korlan)

            taskMgr.add(self.mouse_task,
                        'mouse_task',
                        extraArgs=[self.korlan],
                        appendTask=True)

            # Taken from Roaming Ralph example:
            # Create a floater object, which floats 2 units above Korlan.  We
            # use this as a target for the camera to look at.

            self.floater = NodePath(PandaNode("floater"))
            self.floater.reparentTo(self.korlan)
            self.floater.setZ(2.0)

            self.keymap = {
                "left": 0,
                "right": 0,
                "forward": 0,
                "backward": 0,
                "cam-left": 0,
                "cam-right": 0
            }

            # Accept the control keys for movement and rotation
            self.base.accept("arrow_left", self.set_key, ["left", True])
            self.base.accept("arrow_right", self.set_key, ["right", True])
            self.base.accept("arrow_up", self.set_key, ["forward", True])
            self.base.accept("arrow_down", self.set_key, ["backward", True])
            self.base.accept("a", self.set_key, ["cam-left", True])
            self.base.accept("s", self.set_key, ["cam-right", True])
            self.base.accept("arrow_left-up", self.set_key, ["left", False])
            self.base.accept("arrow_right-up", self.set_key, ["right", False])
            self.base.accept("arrow_up-up", self.set_key, ["forward", False])
            self.base.accept("arrow_down-up", self.set_key, ["backward", False])
            self.base.accept("a-up", self.set_key, ["cam-left", False])
            self.base.accept("s-up", self.set_key, ["cam-right", False])

            # Game state variables
            self.isMoving = False

            taskMgr.add(self.player_move, "moveTask",
                        extraArgs=[anim],
                        appendTask=True)

            # Set up the camera
            self.base.camera.setPos(self.korlan.getX(), self.korlan.getY() + 10, 2)

            # We will detect the height of the terrain by creating a collision
            # ray and casting it downward toward the terrain.  One ray will
            # start above Korlan's head, and the other will start above the camera.
            # A ray may hit the terrain, or it may hit a rock or a tree.  If it
            # hits the terrain, we can detect the height.  If it hits anything
            # else, we rule that the move is illegal.
            self.cTrav = CollisionTraverser()
            self.korlanGroundRay = CollisionRay()
            self.korlanGroundRay.setOrigin(0, 0, 9)
            self.korlanGroundRay.setDirection(0, 0, -1)
            self.korlanGroundCol = CollisionNode('KorlanRay')
            self.korlanGroundCol.addSolid(self.korlanGroundRay)
            self.korlanGroundCol.setFromCollideMask(CollideMask.bit(0))
            self.korlanGroundCol.setIntoCollideMask(CollideMask.allOff())
            self.korlanGroundColNp = self.korlan.attachNewNode(self.korlanGroundCol)
            self.korlanGroundHandler = CollisionHandlerQueue()
            self.cTrav.addCollider(self.korlanGroundColNp, self.korlanGroundHandler)

            self.camGroundRay = CollisionRay()
            self.camGroundRay.setOrigin(0, 0, 9)
            self.camGroundRay.setDirection(0, 0, -1)
            self.camGroundCol = CollisionNode('camRay')
            self.camGroundCol.addSolid(self.camGroundRay)
            self.camGroundCol.setFromCollideMask(CollideMask.bit(0))
            self.camGroundCol.setIntoCollideMask(CollideMask.allOff())
            self.camGroundColNp = self.base.camera.attachNewNode(self.camGroundCol)
            self.camGroundHandler = CollisionHandlerQueue()
            self.cTrav.addCollider(self.camGroundColNp, self.camGroundHandler)

            # Uncomment this line to see the collision rays
            # self.korlanGroundColNp.show()
            # self.camGroundColNp.show()

            # Uncomment this line to show a visual representation of the
            # collisions occuring
            # self.cTrav.showCollisions(render)

    # Records the state of the arrow/actions keys
    def set_key(self, key, value):
        self.keymap[key] = value

    # Accepts arrow keys to move either the player or the menu cursor,
    # Also deals with grid checking and collision detection
    def player_move(self, anim, task):
        # Get the time that elapsed since last frame.  We multiply this with
        # the desired speed in order to find out with which distance to move
        # in order to achieve that desired speed.
        dt = globalClock.getDt()

        # If the camera-left key is pressed, move camera left.
        # If the camera-right key is pressed, move camera right.

        if self.keymap["cam-left"]:
            self.base.camera.setX(self.base.camera, -20 * dt)
        if self.keymap["cam-right"]:
            self.base.camera.setX(self.base.camera, +20 * dt)

        # Save the player initial position so that we can restore it,
        # in case he falls off the map or runs into something.

        startpos = self.korlan.getPos()

        # If a move-key is pressed, move the player in the specified direction.

        speed = 25

        if self.keymap["left"]:
            self.korlan.setH(self.korlan.getH() + 300 * dt)
            # self.korlan.setX(self.korlan, speed * dt)
        if self.keymap["right"]:
            self.korlan.setH(self.korlan.getH() - 300 * dt)
            # self.korlan.setX(self.korlan, -speed * dt)
        if self.keymap["forward"]:
            self.korlan.setY(self.korlan, -speed * dt)
        if self.keymap["backward"]:
            self.korlan.setY(self.korlan, speed * dt)

        # If the player is moving, loop the run animation.
        # If it is standing still, stop the animation.

        if self.keymap["forward"] or self.keymap["backward"] or self.keymap["left"] or self.keymap["right"]:
            if self.isMoving is False:
                self.korlan.loop(anim)
                self.korlan.setPlayRate(8.0, anim)
                self.isMoving = True
        else:
            if self.isMoving:
                self.korlan.stop()
                self.korlan.pose(anim, 0)
                self.isMoving = False

        # If the camera is too far from olayer, move it closer.
        # If the camera is too close to olayer, move it farther.

        camvec = self.korlan.getPos() - self.base.camera.getPos()
        camvec.setZ(0)
        camdist = camvec.length()
        camvec.normalize()
        if camdist > 10.0:
            self.base.camera.setPos(self.base.camera.getPos() + camvec * (camdist - 10))
            camdist = 10.0
        if camdist < 5.0:
            self.base.camera.setPos(self.base.camera.getPos() - camvec * (5 - camdist))
            camdist = 5.0

        # We would have to call traverse() to check for collisions.
        self.cTrav.traverse(render)

        # Adjust Korlan's Z coordinate.  If Korlan's ray hit terrain,
        # update his Z. If it hit anything else, or didn't hit anything, put
        # him back where he was last frame.
        entries = list(self.korlanGroundHandler.getEntries())
        entries.sort(key=lambda x: x.getSurfacePoint(render).getZ())

        if len(entries) > 0 and entries[0].getIntoNode().getName() == 'mountain':
            self.korlan.setZ(entries[0].getSurfacePoint(render).getZ())
        else:
            self.korlan.setPos(startpos)

        # Keep the camera at one foot above the terrain,
        # or two feet above Korlan, whichever is greater.

        entries = list(self.camGroundHandler.getEntries())
        entries.sort(key=lambda x: x.getSurfacePoint(render).getZ())

        if len(entries) > 0 and entries[0].getIntoNode().getName() == 'mountain':
            self.base.camera.setZ(entries[0].getSurfacePoint(render).getZ() + 1.0)
        if self.base.camera.getZ() < self.korlan.getZ() + 2.0:
            self.base.camera.setZ(self.korlan.getZ() + 2.0)

        # The camera should look in Korlan direction,
        # but it should also try to stay horizontal, so look at
        # a floater which hovers above Korlan's head.
        self.base.camera.lookAt(self.floater)

        return task.cont

    def set_mouse_mode(self, mode):
        self.base.mouseMode = mode

        wp = WindowProperties()
        wp.setMouseMode(mode)
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

    def recenter_mouse(self):
        self.base.win.movePointer(0,
                                  int(self.base.win.getProperties().getXSize() / 2),
                                  int(self.base.win.getProperties().getYSize() / 2))

    def toggle_recenter(self):
        self.base.manualRecenterMouse = not self.base.manualRecenterMouse

    def toggle_mouse(self):
        self.korlan.hideMouse = not base.hideMouse

        wp = WindowProperties()
        wp.setCursorHidden(self.korlan.hideMouse)
        self.korlan.win.requestProperties(wp)

    def mouse_task(self, korlan, task):
        if korlan:
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
                self.d_object.accept('mouse-1', korlan.setH, extraArgs=[self.base.rotateX])
                self.base.cam.setH(self.base.rotateX)

                return task.cont
