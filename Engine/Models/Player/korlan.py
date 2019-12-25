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
from Engine.Models.Player.player_movement import Movement


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
        self.taskMgr = taskMgr
        self.kbd = Keyboard()
        self.mouse = Mouse()
        self.col = Collisions()
        self.world = World()
        self.movement = Movement()

    def set_character(self, render_type, game_settings, model_dir,
                      game_dir, player_path, cfg_path, render, anim):

        # Disable the camera trackball controls.
        self.base.disableMouse()
        props = WindowProperties()
        props.setCursorHidden(False)
        base.win.requestProperties(props)

        if (isinstance(player_path, str)
                and game_settings
                and isinstance(model_dir, str)
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

                self.korlan = Actor(player_path,
                                    {anim: "{0}/Assets/Models/{1}/{2}".format(game_dir, model_dir, anim)})

                self.korlan.setName(model_dir)
                self.korlan.setScale(self.korlan, self.scale_x, self.scale_y, self.scale_z)
                self.korlan.setPos(self.pos_x, self.pos_y, self.pos_z)
                self.korlan.setH(self.korlan, self.rot_h)
                self.korlan.setP(self.korlan, self.rot_p)
                self.korlan.setR(self.korlan, self.rot_r)
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

                self.col.set_inter_collision(self.korlan)

    def set_character_game(self, render_type, game_settings, model_dir,
                           axis, rotation, scale, game_dir,
                           player_path, cfg_path, render, anim):

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

            self.korlan = Actor(player_path,
                                {anim: "{0}/Assets/Models/{1}/{2}".format(game_dir, model_dir, anim)})

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
            if game_settings['Main']['postprocessing'] == 'off':
                # self.world.set_shadows(self.korlan, render)
                self.world.set_lighting(render, self.korlan)
            # self.world.set_ssao(self.korlan)

            if game_settings['Debug']['set_debug_mode'] == "YES":
                render.analyze()
                render.explore()

            taskMgr.add(self.mouse.mouse_task,
                        'mouse_task',
                        extraArgs=[self.korlan],
                        appendTask=True)

            self.movement.movement_init(self.korlan, anim)
