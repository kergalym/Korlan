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
from Engine.collisions import Collisions
from Engine import set_tex_transparency
from direct.actor.Actor import Actor
from direct.task.TaskManagerGlobal import taskMgr

from Engine.world import World


class NPC:

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
        self.actor = None
        self.base = base
        self.render = render

        self.game_settings = base.game_settings
        self.game_dir = base.game_dir
        self.col = Collisions()
        self.world = World()

    def actor_life(self, task):
        pass
        return task.cont

    def set_actor(self, mode, name, path, anim):

        if (isinstance(path, str)
                and isinstance(name, str)
                and isinstance(mode, str)
                and anim
                and isinstance(anim, str)):

            self.actor = Actor(path,
                               {anim: "{0}/Assets/Actors/Animations/{1}".format(self.game_dir, anim)})

            self.actor.setName(name)
            self.actor.setScale(self.actor, self.scale_x, self.scale_y, self.scale_z)
            self.actor.setPos(self.pos_x, self.pos_y, self.pos_z)
            self.actor.setH(self.actor, self.rot_h)
            self.actor.setP(self.actor, self.rot_p)
            self.actor.setR(self.actor, self.rot_r)
            self.actor.loop(anim)
            self.actor.setPlayRate(1.0, anim)

            # Panda3D 1.10 doesn't enable alpha blending for textures by default
            set_tex_transparency(self.actor)

            self.actor.reparentTo(self.render)

            # Set lights and Shadows
            if self.game_settings['Main']['postprocessing'] == 'off':
                # TODO: uncomment if character has normals
                # self.world.set_shadows(self.actor, self.render)
                # self.world.set_ssao(self.actor)
                self.world.set_lighting(self.render, self.actor)

            if self.game_settings['Debug']['set_debug_mode'] == "YES":
                self.render.analyze()
                self.render.explore()

            self.col.set_inter_collision(self.actor)

            taskMgr.add(self.actor_life, "actor_life")
