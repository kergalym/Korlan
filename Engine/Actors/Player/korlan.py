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
import re
from pathlib import Path
from Engine.collisions import Collisions
from Engine import set_tex_transparency
from direct.actor.Actor import Actor
from panda3d.core import WindowProperties
from panda3d.core import LPoint3f
from direct.task.TaskManagerGlobal import taskMgr

from Engine.world import World
from Settings.Input.keyboard import Keyboard
from Settings.Input.mouse import Mouse
from Engine.Actors.Player.actions import Actions


class Korlan:

    def __init__(self):
        self.scale_x = None
        self.scale_y = None
        self.scale_z = None
        self.pos_x = None
        self.pos_y = None
        self.pos_z = None
        self.rot_h = None
        self.rot_p = None
        self.rot_r = None
        self.korlan = None
        self.base = base
        self.render = render

        self.game_settings = base.game_settings
        self.game_dir = base.game_dir
        self.game_cfg = base.game_cfg
        self.game_cfg_dir = base.game_cfg_dir
        self.game_settings_filename = base.game_settings_filename
        self.cfg_path = {"game_config_path":
                         "{0}/{1}".format(self.game_cfg_dir, self.game_settings_filename)}

        self.taskMgr = taskMgr
        self.kbd = Keyboard()
        self.mouse = Mouse()
        self.col = Collisions()
        self.world = World()
        self.act = Actions()

    def actor_life(self, task):
        pass
        return task.cont

    def set_actor(self, mode, name, path, animation, axis, rotation, scale):

        if mode == 'menu':

            # Disable the camera trackball controls.
            self.base.disableMouse()
            props = WindowProperties()
            props.setCursorHidden(False)
            self.base.win.requestProperties(props)

            if (isinstance(path, str)
                    and isinstance(name, str)
                    and isinstance(axis, list)
                    and isinstance(rotation, list)
                    and isinstance(scale, list)
                    and isinstance(mode, str)
                    and animation
                    and isinstance(animation, str)):
                self.pos_x = axis[0]
                self.pos_y = axis[1]
                self.pos_z = axis[2]
                self.rot_h = rotation[0]
                self.rot_p = rotation[1]
                self.rot_r = rotation[2]
                self.scale_x = scale[0]
                self.scale_y = scale[1]
                self.scale_z = scale[2]

            self.korlan = Actor(path,
                                {animation: "{0}/Assets/Actors/Animations/{1}.egg".format(self.game_dir, animation)})

            self.korlan.setName(name)
            self.korlan.setScale(self.korlan, self.scale_x, self.scale_y, self.scale_z)
            self.korlan.setPos(self.pos_x, self.pos_y, self.pos_z)
            self.korlan.setH(self.korlan, self.rot_h)
            self.korlan.setP(self.korlan, self.rot_p)
            self.korlan.setR(self.korlan, self.rot_r)
            self.korlan.loop(animation)
            self.korlan.setPlayRate(1.0, animation)

            # Panda3D 1.10 doesn't enable alpha blending for textures by default
            set_tex_transparency(self.korlan)

            self.korlan.reparentTo(render)

            # Set lights and Shadows
            if self.game_settings['Main']['postprocessing'] == 'off':
                # TODO: uncomment if character has normals
                # self.world.set_shadows(self.korlan, self.render)
                # self.world.set_ssao(self.korlan)
                self.world.set_lighting(self.render, self.korlan)

            if self.game_settings['Debug']['set_debug_mode'] == "YES":
                self.render.analyze()
                self.render.explore()

            self.col.set_inter_collision(self.korlan)

        if mode == 'game':

            self.base.game_mode = True
            wp = WindowProperties()
            wp.setCursorHidden(True)
            self.base.win.requestProperties(wp)

            # Disable the camera trackball controls.
            self.base.disableMouse()

            # control mapping of mouse movement to character movement
            self.base.mouseMagnitude = 1

            self.base.rotateX = 0

            self.base.lastMouseX = None

            self.base.hideMouse = False

            self.base.manualRecenterMouse = True

            self.mouse.set_mouse_mode(WindowProperties.M_absolute)

            if (isinstance(path, str)
                    and isinstance(name, str)
                    and isinstance(axis, list)
                    and isinstance(rotation, list)
                    and isinstance(scale, list)
                    and isinstance(mode, str)
                    and isinstance(animation, list)):

                self.pos_x = axis[0]
                self.pos_y = axis[1]
                self.pos_z = axis[2]
                self.rot_h = rotation[0]
                self.rot_p = rotation[1]
                self.rot_r = rotation[2]
                self.scale_x = scale[0]
                self.scale_y = scale[1]
                self.scale_z = scale[2]

                # Make animations dict containing full path and pass it to Actor
                anims = {}
                anim_values = {}
                anim_path = "{0}/Assets/Actors/Animations/".format(self.game_dir)
                for a in animation:
                    anims[a] = "{0}{1}".format(anim_path, a)
                    key = re.sub('Korlan-', '', a)
                    key = re.sub('.egg', '', key)
                    anim_values[key] = a

                self.korlan = Actor(path, anims)

                self.korlan.setName(name)
                self.korlan.setScale(self.korlan, self.scale_x, self.scale_y, self.scale_z)
                self.KorlanStartPos = LPoint3f(self.pos_x, self.pos_y, 0.0)
                self.korlan.setPos(self.KorlanStartPos + (0, 0, self.pos_z))
                self.korlan.setH(self.korlan, self.rot_h)
                self.korlan.setP(self.korlan, self.rot_p)
                self.korlan.setR(self.korlan, self.rot_r)

                # Panda3D 1.10 doesn't enable alpha blending for textures by default
                set_tex_transparency(self.korlan)

                self.korlan.reparentTo(render)

                # Set lights and Shadows
                if self.game_settings['Main']['postprocessing'] == 'off':
                    # TODO: uncomment if character has normals
                    # self.world.set_shadows(self.korlan, self.render)
                    # self.world.set_ssao(self.korlan)
                    self.world.set_lighting(render, self.korlan)

                if self.game_settings['Debug']['set_debug_mode'] == "YES":
                    self.render.analyze()
                    self.render.explore()

                taskMgr.add(self.mouse.mouse_look_cam,
                            "mouse-look",
                            appendTask=True)

                self.act.scene_actions_init(self.korlan, anim_values)

                taskMgr.add(self.actor_life, "actor_life")
