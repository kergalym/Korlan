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

from pathlib import Path
from Engine.Collisions import Collisions
from Engine import set_tex_transparency
from direct.actor.Actor import Actor
from panda3d.core import WindowProperties
from panda3d.core import LPoint3f
from direct.task.TaskManagerGlobal import taskMgr

from Engine.World import World
from Settings.Input.keyboard import Keyboard
from Settings.Input.mouse import Mouse
from Engine.Actors.Player.pl_actions import Actions


class Korlan:

    def __init__(self):
        self.scale_x = 1.25
        self.scale_y = 1.25
        self.scale_z = 1.25
        self.pos_x = -1.5
        self.pos_y = 9.8
        self.pos_z = -3.2
        self.rot_h = -0.10
        self.rot_p = 0
        self.rot_r = 0
        self.korlan = None
        self.base = base
        self.render = render

        self.game_settings = base.game_settings
        self.game_dir = base.game_dir
        self.game_cfg = base.game_cfg
        self.game_cfg_dir = base.game_cfg_dir
        self.game_settings_filename = base.game_settings_filename
        self.cfg_path = {"game_config_path": "{0}/{1}".format(self.game_cfg_dir, self.game_settings_filename)}

        self.taskMgr = taskMgr
        self.kbd = Keyboard()
        self.mouse = Mouse()
        self.col = Collisions()
        self.world = World()
        self.act = Actions()

    def set_character(self, render_type, model_dir, player_path, anim):

        # Disable the camera trackball controls.
        self.base.disableMouse()
        props = WindowProperties()
        props.setCursorHidden(False)
        self.base.win.requestProperties(props)

        if (isinstance(player_path, str)
                and isinstance(model_dir, str)
                and isinstance(render_type, str)
                and anim
                and isinstance(anim, str)):

            if render_type == 'menu':

                try:
                    self.game_settings.read(self.cfg_path)
                    self.pos_x = float(self.game_settings['Debug']['player_pos_x'])
                    self.pos_y = float(self.game_settings['Debug']['player_pos_y'])
                    self.pos_z = float(self.game_settings['Debug']['player_pos_z'])
                    self.rot_h = float(self.game_settings['Debug']['player_rot_h'])
                    self.rot_p = float(self.game_settings['Debug']['player_rot_p'])
                    self.rot_r = float(self.game_settings['Debug']['player_rot_r'])
                except KeyError:
                    self.game_settings.read("{}/Korlan/Configs/default_config.ini".format(str(Path.home())))
                    self.pos_x = float(self.game_settings['Debug']['player_pos_x'])
                    self.pos_y = float(self.game_settings['Debug']['player_pos_y'])
                    self.pos_z = float(self.game_settings['Debug']['player_pos_z'])
                    self.rot_h = float(self.game_settings['Debug']['player_rot_h'])
                    self.rot_p = float(self.game_settings['Debug']['player_rot_p'])
                    self.rot_r = float(self.game_settings['Debug']['player_rot_r'])
                except ValueError:
                    self.game_settings.read("{}/Korlan/Configs/default_config.ini".format(str(Path.home())))
                    self.pos_x = float(self.game_settings['Debug']['player_pos_x'])
                    self.pos_y = float(self.game_settings['Debug']['player_pos_y'])
                    self.pos_z = float(self.game_settings['Debug']['player_pos_z'])
                    self.rot_h = float(self.game_settings['Debug']['player_rot_h'])
                    self.rot_p = float(self.game_settings['Debug']['player_rot_p'])
                    self.rot_r = float(self.game_settings['Debug']['player_rot_r'])

                self.korlan = Actor(player_path,
                                    {anim: "{0}/Assets/Actors/Animations/{1}".format(self.game_dir, anim)})

                self.korlan.setName(model_dir)
                self.korlan.setScale(self.korlan, self.scale_x, self.scale_y, self.scale_z)
                self.korlan.setPos(self.pos_x, self.pos_y, self.pos_z)
                self.korlan.setH(self.korlan, self.rot_h)
                self.korlan.setP(self.korlan, self.rot_p)
                self.korlan.setR(self.korlan, self.rot_r)
                self.korlan.loop(anim)
                self.korlan.setPlayRate(1.0, anim)

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

    def set_character_game(self, render_type, model_dir,
                           axis, rotation, scale, player_path, anim):

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

        if (isinstance(player_path, str)
                and isinstance(model_dir, str)
                and isinstance(axis, list)
                and isinstance(rotation, list)
                and isinstance(scale, list)
                and isinstance(render_type, str)
                and isinstance(anim, list)
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

            # Make animations dict containing full path and pass it to Actor
            anims = {}
            anim_values = {}
            anim_path = "{0}/Assets/Actors/Animations/".format(self.game_dir)
            for a in anim:
                anims[a] = "{0}{1}".format(anim_path, a)
                anim_values[a] = a

            self.korlan = Actor(player_path, anims)

            self.korlan.setName(model_dir)
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
                        "camera-task",
                        appendTask=True)

            self.act.scene_actions_init(self.korlan, anim_values)
