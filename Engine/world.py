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

from panda3d.core import *


class World:

    def __init__(self):
        self.set_color = 0.2
        self.shadow_size = 1024
        self.obj = None
        self.render = None
        self.shadows = Shader.load(Shader.SL_GLSL, vertex="Engine/Shaders/Shadows/vertex.vert",
                                   fragment="Engine/Shaders/Shadows/fragment.frag")
        self.ssao = Shader.load(Shader.SL_GLSL, vertex="Engine/Shaders/SSAO/base.vert",
                                fragment="Engine/Shaders/SSAO/ssao.frag")

    def set_shadows(self, obj, render):
        if obj and render:
            self.obj = obj
            self.render = render
            # If you don't do this, none of the features
            # listed above will have any effect. Panda will
            # simply ignore normal maps, HDR, and so forth if
            # shader generation is not enabled. It would be reasonable
            # to enable shader generation for the entire game, using this call:
            self.obj.setShaderAuto()
            base.shaderenable = 1

    def set_lighting(self, render, obj):
        if render and obj:
            self.render = render
            self.obj = obj

            # Directional light 01
            directionalLight = DirectionalLight('directionalLight')
            directionalLight.setColor((self.set_color, self.set_color, self.set_color, 1))
            directionalLightNP = render.attachNewNode(directionalLight)
            # This light is facing backwards, towards the camera.
            directionalLightNP.setHpr(180, -20, 0)
            directionalLightNP.setZ(10)
            render.setLight(directionalLightNP)

            # Directional light 02
            directionalLight = DirectionalLight('directionalLight')
            directionalLight.setColor((self.set_color, self.set_color, self.set_color, 1))
            directionalLightNP = render.attachNewNode(directionalLight)
            # This light is facing forwards, away from the camera.
            directionalLightNP.setHpr(0, -20, 0)
            directionalLightNP.setZ(10)
            render.setLight(directionalLightNP)

            # Add an ambient light
            alight = AmbientLight('alight')
            alight.setColor((self.set_color, self.set_color, self.set_color, 1))
            alnp = render.attachNewNode(alight)
            render.setLight(alnp)

    def set_ssao(self, obj):
        if obj:
            obj.setShader(self.ssao)

    def set_physics(self):
        pass
