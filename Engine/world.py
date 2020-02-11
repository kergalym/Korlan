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
            self.obj.set_shader_auto()
            base.shaderenable = 1

    def set_lighting(self, render, obj):
        if render and obj:
            self.render = render
            self.obj = obj

            # Directional light 01
            directional_light = DirectionalLight('directionalLight')
            directional_light.set_color((self.set_color, self.set_color, self.set_color, 1))
            directional_light_np = render.attach_new_node(directional_light)
            # This light is facing backwards, towards the camera.
            directional_light_np.set_hpr(180, -20, 0)
            directional_light_np.set_z(10)
            render.set_light(directional_light_np)

            # Directional light 02
            directional_light = DirectionalLight('directionalLight')
            directional_light.set_color((self.set_color, self.set_color, self.set_color, 1))
            directional_light_np = render.attach_new_node(directional_light)
            # This light is facing forwards, away from the camera.
            directional_light_np.set_hpr(0, -20, 0)
            directional_light_np.set_z(10)
            render.set_light(directional_light_np)

            # Add an ambient light
            alight = AmbientLight('alight')
            alight.set_color((self.set_color, self.set_color, self.set_color, 1))
            alnp = render.attach_new_node(alight)
            render.set_light(alnp)

    def set_ssao(self, obj):
        if obj:
            obj.set_shader(self.ssao)

    def set_physics(self):
        pass
