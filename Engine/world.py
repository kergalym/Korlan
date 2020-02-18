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

    def set_lighting(self, name, render, pos, hpr, color, task):
        if (render
                and name
                and isinstance(name, str)
                and isinstance(pos, list)
                and isinstance(hpr, list)
                and isinstance(color, list)
                and isinstance(task, str)):

            self.render = render

            if task == 'attach':
                # Directional light 01
                directional_light = DirectionalLight(name)
                directional_light.set_color((color[0], color[0], color[0], 1))
                directional_light_np = self.render.attach_new_node(directional_light)
                # This light is facing backwards, towards the camera.
                directional_light_np.set_hpr(hpr[0], hpr[1], hpr[2])
                directional_light_np.set_z(pos[2])
                self.render.set_light(directional_light_np)

            if task == 'attach':
                # Add an ambient light
                alight = AmbientLight('ambientLight')
                alight.set_color((self.set_color, self.set_color, self.set_color, 1))
                alnp = self.render.attach_new_node(alight)
                self.render.set_light(alnp)
                if task == 'detach':
                    self.render.set_light_off(alnp)

    def set_ssao(self, obj):
        if obj:
            obj.set_shader(self.ssao)

    def set_physics(self):
        pass
