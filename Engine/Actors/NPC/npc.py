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

from Engine.collisions import Collisions
from Engine import set_tex_transparency
from direct.actor.Actor import Actor
from direct.task.TaskManagerGlobal import taskMgr

from Engine.world import World
from Engine.FSM.fsm_for_npc import Idle


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
        self.anims = None

        self.game_settings = base.game_settings
        self.game_dir = base.game_dir
        self.col = Collisions()
        self.world = World()
        self.idle_player = Idle()
        self.actor_life_perc = None
        self.base.actor_is_dead = False
        self.base.actor_is_alive = False

    def actor_life(self, task):
        self.has_actor_life()
        return task.cont

    def has_actor_life(self):
        if (self.base.actor_is_dead is False
                and self.base.actor_is_alive is False):
            self.actor_life_perc = 100
            self.base.actor_is_alive = True
        else:
            return False

    def set_actor_task(self, animation, task):
        if animation:
            self.idle_player.enter_idle(player=self.actor, action=animation['LookingAround'])
            return task.cont

    def set_actor(self, mode, name, path, animation, axis, rotation, scale):

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

            self.actor = Actor(path, anims)

            self.actor.setName(name)
            self.actor.setScale(self.actor, self.scale_x, self.scale_y, self.scale_z)
            self.actor.setPos(self.pos_x, self.pos_y, self.pos_z)
            self.actor.setH(self.actor, self.rot_h)
            self.actor.setP(self.actor, self.rot_p)
            self.actor.setR(self.actor, self.rot_r)

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

            taskMgr.add(self.set_actor_task, 'actor_in_idle', extraArgs=[anim_values], appendTask=True)
