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
from direct.actor.Actor import Actor


class NPC:

    def __init__(self):

        self.scale_x = 0.25
        self.scale_y = 0.25
        self.scale_z = 0.25
        self.pos_x = 0
        self.pos_y = 0
        self.pos_z = 1.9
        self.cam_pos_x = 0
        self.cam_pos_y = 4.8
        self.cam_pos_z = -1.7

    def model_load(self, path, loader, render):
        if (isinstance(path, str)
                and loader
                and render):
            # Load and transform the actor.
            npc = loader.Actor(path)
            npc.reparentTo(render)
            npc.setScale(self.scale_x, self.scale_y, self.scale_z)
            npc.setPos(self.pos_x, self.pos_y, self.pos_z)
            npc.lookAt(npc)

    def npc_move(self):
        pass

    def npc_stop(self):
        pass

    def npc_turn_left(self):
        pass

    def npc_turn_right(self):
        pass

    def npc_jump(self):
        pass
