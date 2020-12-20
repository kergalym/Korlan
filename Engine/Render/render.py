from os.path import exists
from pathlib import Path, PurePath
from os import walk

from direct.gui.DirectGui import OnscreenText
from direct.task.TaskManagerGlobal import taskMgr
from panda3d.core import *
from panda3d.core import FontPool, TextNode
from Engine.Render.rpcore import PointLight, SpotLight


class RenderAttr:

    def __init__(self):
        self.base = base
        self.game_dir = str(Path.cwd())
        self.fonts = base.fonts_collector()
        # instance of the abstract class
        self.font = FontPool
        self.texture = None
        self.game_settings = base.game_settings
        if hasattr(base, "render_pipeline") and base.render_pipeline:
            self.render_pipeline = base.render_pipeline
        self.world = None
        self.set_color = 0.2
        self.shadow_size = 1024
        self.render = None
        self.flame_np = None
        self.water_np = None
        self.water_camera = None
        self.water_buffer = None
        self.grass_np = None

        # Set time of day
        self.elapsed_seconds = 0
        self.minutes = 0
        self.hour = 0

        """ Texts & Fonts"""
        # self.menu_font = self.fonts['OpenSans-Regular']
        self.menu_font = self.fonts['JetBrainsMono-Regular']

        """if self.game_settings['Main']['postprocessing'] == 'on':
            if self.render_pipeline:
                # TODO: Remove the time declaration after Menu Scene is constructed
                self.render_pipeline.daytime_mgr.time = "8:45"""

        self.time_text_ui = OnscreenText(text="",
                                         pos=(-1.8, -0.7),
                                         scale=0.04,
                                         fg=(255, 255, 255, 0.9),
                                         font=self.font.load_font(self.menu_font),
                                         align=TextNode.ALeft,
                                         mayChange=True)

    def set_water(self, bool, water_lvl, adv_render):
        if bool:
            MASK_WATER = BitMask32.bit(1)
            MASK_SHADOW = BitMask32.bit(2)

            if not adv_render:
                if water_lvl > 0.0 and not render.find("**/water_plane").is_empty():
                    textures = self.base.textures_collector("{0}/Engine/Shaders/".format(self.game_dir))
                    self.water_np = render.find("**/water_plane")
                    self.water_np.setPos(0, 0, -2.0)
                    self.water_np.set_transparency(True)
                    self.water_np.setTransparency(TransparencyAttrib.MAlpha)
                    self.water_np.flattenLight()
                    self.water_np.setPos(0, 0, -2.0)
                    self.water_np.reparent_to(render)

                    # Add a buffer and camera that will render the reflection texture
                    self.water_buffer = base.win.make_texture_buffer("water", 512, 512)
                    self.water_buffer.setClearColorActive(True)
                    self.water_buffer.set_clear_color(base.win.get_clear_color())
                    self.water_buffer.set_sort(-1)
                    self.water_camera = base.make_camera(self.water_buffer)
                    self.water_camera.reparent_to(render)
                    self.water_camera.node().set_lens(base.camLens)
                    self.water_camera.node().set_camera_mask(MASK_WATER)

                    # Create this texture and apply settings
                    water_texture = self.water_buffer.get_texture()
                    water_texture.set_wrap_u(Texture.WMClamp)
                    water_texture.set_wrap_v(Texture.WMClamp)
                    water_texture.setMinfilter(Texture.FTLinearMipmapLinear)

                    # Create plane for clipping and for reflection matrix
                    water_plane = Plane(Vec3(0, 0, 1), Point3(0, 0, water_lvl))
                    water_plane_np = render.attachNewNode(PlaneNode("WaterNodePath", water_plane))

                    state_init = NodePath("StateInitializer")
                    state_init.set_clip_plane(water_plane_np)
                    state_init.setAttrib(CullFaceAttrib.makeReverse())
                    self.water_camera.node().set_initial_state(state_init.getState())

                    # reflect UV generated on the shader - faster(?)
                    self.water_np.set_shader_input('camera', self.water_camera)
                    self.water_np.set_shader_input("reflection", water_texture)
                    self.water_np.set_shader(Shader.load(Shader.SLGLSL,
                                                         vertex="{0}/Engine/Shaders/Water/water_v.glsl".format(
                                                             self.game_dir),
                                                         fragment="{0}/Engine/Shaders/Water/water_f.glsl".format(
                                                             self.game_dir)))
                    self.water_np.set_shader_input("water_norm",
                                                   self.base.loader.load_texture(textures["water"]))
                    self.water_np.set_shader_input("water_height",
                                                   self.base.loader.load_texture(textures["ocen3"]))
                    self.water_np.set_shader_input("height",
                                                   self.base.loader.load_texture(textures["heightmap"]))
                    self.water_np.set_shader_input("tile", 20.0)
                    self.water_np.set_shader_input("water_level", water_lvl)
                    self.water_np.set_shader_input("speed", 0.01)
                    self.water_np.set_shader_input("wave", Vec4(0.005, 0.002, 6.0, 1.0))
                    self.water_np.set_shader_input("camera_pos", base.camera.get_pos())
                    self.water_np.set_shader_input("light_color", VBase4(240, 248, 255, 0))
                    self.water_np.set_shader_input("light_pos", self.water_np.get_pos())
                    self.water_np.set_shader_input("num_lights", 3)

                    render.set_shader_input("fog", Vec4(0.3, 0.3, 0.3, 0.002))
                    render.set_shader_input("z_scale", 100.0)
                    self.water_np.set_shader_input("tex_scale", 30.0)
                    render.set_shader_input("ambient", Vec4(.001, .001, .001, 1))
                else:
                    self.water_np.hide(MASK_WATER)
                    self.water_np.hide(MASK_SHADOW)
                    # hide water by default
                    self.water_np.hide()
                    self.water_np.setDepthWrite(False)
                    self.water_np.set_bin("transparent", 31)
                    self.water_buffer.setActive(False)

            if adv_render:
                if water_lvl > 0.0 and not render.find("**/water_plane").is_empty():
                    # self.render_pipeline.reload_shaders()

                    # Set the water effect
                    """self.render_pipeline.set_effect(self.water_np, "effects/water.yaml",
                                                    {
                                                        'camera': self.water_camera,
                                                        "reflection": water_texture,
                                                        "water_norm":
                                                        self.base.loader.load_texture(textures["water"]),
                                                        "water_height":
                                                            self.base.loader.load_texture(textures["ocen3"]),
                                                        "height":
                                                            self.base.loader.load_texture(textures["heightmap"]),
                                                        "tile": 20.0,
                                                        "water_level": 30.0,
                                                        "speed": 0.01,
                                                        "wave": Vec4(0.005, 0.002, 6.0, 1.0),
                                                        "camera_pos": base.camera.get_pos(),
                                                        "light_color": Vec3(0.8, 0.8, 0.8),
                                                        "light_pos": self.water_np.get_pos(),
                                                        "num_lights": 3,
                                                    })
                    self.render_pipeline.set_effect(water_ground, "effects/water.yaml", {
                        "water_level": 1.0
                    })
                    
                    self.render_pipeline.set_effect(render, "effects/water.yaml", {
                        "fog": Vec4(0.8, 0.8, 0.8, 0.002),
                        "z_scale": 100.0,
                        
                    })
                    
                    self.render_pipeline.set_effect(water_ground, "effects/water.yaml", {
                        "tex_scale": 16.0
                    })"""

                    """self.render_pipeline.set_effect(self.water_np,
                                                    "{0}/Engine/Render/effects/water.yaml".format(self.game_dir),
                                                    {},
                                                    self.water_camera)"""

    def set_grass(self, bool, uv_offset, fogcenter=Vec3(0, 0, 0), adv_render=False):
        if bool:
            if not adv_render and not render.find("**/water_plane").is_empty():
                textures = self.base.textures_collector("{0}/Engine/Shaders/".format(self.game_dir))
                self.grass_np = render.find("**/Grass")
                self.grass_np.setTransparency(TransparencyAttrib.MBinary, 1)
                self.grass_np.reparentTo(self.grass_np.get_parent())
                self.grass_np.setInstanceCount(256)
                self.grass_np.node().setBounds(BoundingBox((0, 0, 0), (256, 256, 128)))
                self.grass_np.node().setFinal(1)
                self.grass_np.setShader(Shader.load(Shader.SLGLSL,
                                                    vertex="{0}/Engine/Shaders/Grass/grass_v.glsl".format(
                                                        self.game_dir),
                                                    fragment="{0}/Engine/Shaders/Grass/grass_f.glsl".format(
                                                        self.game_dir)))
                self.grass_np.setShaderInput('height', self.base.loader.load_texture(textures["heightmap"]))
                self.grass_np.setShaderInput('grass', self.base.loader.load_texture(textures["grass"]))
                self.grass_np.setShaderInput('uv_offset', uv_offset)
                self.grass_np.setShaderInput('fogcenter', fogcenter)
                self.grass_np.setPos(0.0, 0.0, 0.0)

            elif adv_render and not render.find("**/water_plane").is_empty():
                """self.render_pipeline.set_effect(self.grass,
                                                "{0}/Engine/Render/effects/grass.yaml".format(self.game_dir),
                                                {},
                                                self.water_camera)"""

    def set_flame(self, adv_render):
        if adv_render:
            if not render.find("**/flame").is_empty():
                self.flame_np = render.find("**/flame")

                # Set the flame effect
                self.render_pipeline.set_effect(self.flame_np,
                                                "{0}/Engine/Render/effects/flame.yaml".format(self.game_dir),
                                                {})
                taskMgr.add(self.flame_proc_shader_task,
                            "flame_proc_shader_task",
                            appendTask=True)

    def flame_proc_shader_task(self, task):
        if self.flame_np:
            time = task.time
            self.flame_np.set_shader_input("iTime", time)
        return task.cont

    def clear_flame(self):
        if self.flame_np and not render.find("**/flame_plane").is_empty():
            render.find("**/flame_plane").remove_node()
            taskMgr.remove("flame_proc_shader_task")

    def set_hardware_skinning(self, actor, bool_):
        if actor and isinstance(bool_, bool):
            self.render_pipeline.set_effect(actor,
                                            "{0}/Engine/Render/effects/hardware_skinning.yaml".format(self.game_dir),
                                            options={}, sort=25)
            sattrib = actor.get_attrib(ShaderAttrib)
            sattrib = sattrib.set_flag(ShaderAttrib.F_hardware_skinning, bool_)
            actor.set_attrib(sattrib)

    def set_daytime_clock_task(self, task):
        if (not base.game_mode
                and base.menu_mode):
            self.time_text_ui.hide()
            return task.done
        else:
            if self.time_text_ui:
                self.time_text_ui.show()

        if self.game_settings['Main']['postprocessing'] == 'on':
            if self.render_pipeline:
                time = str(self.game_settings['Misc']['daytime'])
                self.render_pipeline.daytime_mgr.time = time
                self.elapsed_seconds = round(globalClock.getRealTime())

                self.minutes = self.elapsed_seconds // 60

                hour = time.split(':')
                hour = int(hour[0])
                self.hour = hour
                self.hour += self.minutes // 60

                if self.minutes < 10:
                    self.time_text_ui.setText("{0}:0{1}".format(self.hour, self.minutes))
                    self.render_pipeline.daytime_mgr.time = "{0}:0{1}".format(self.hour, self.minutes)
                elif self.minutes > 9:
                    self.time_text_ui.setText("{0}:{1}".format(self.hour, self.minutes))
                    self.render_pipeline.daytime_mgr.time = "{0}:{1}".format(self.hour, self.minutes)

        return task.cont

    def shader_collector(self):
        """ Function    : shader_collector

            Description : Collect shader set.

            Input       : None

            Output      : None

            Return      : Dictionary
        """
        shader_path = str(PurePath(self.game_dir, "Engine", "Shaders"))
        shader_path = Filename.from_os_specific("{0}/".format(shader_path))
        shader_dirs = []
        shaders = {}

        if exists(shader_path):
            for root, dirs, files in walk(shader_path, topdown=True):
                # Get last directory to make it list key
                d = root.split("/").pop()
                shader_dirs.append(d)

            for root, dirs, files in walk(shader_path, topdown=True):
                for d in shader_dirs:
                    for file in files:
                        path = str(PurePath("{0}/".format(root), file))
                        path = Filename.from_os_specific(path).getFullpath()
                        if d in path:
                            if "frag" in file:
                                key = "{0}_{1}".format(d, "frag")
                                shaders[key] = path
                            if "vert" in file:
                                key = "{0}_{1}".format(d, "vert")
                                shaders[key] = path
                            else:
                                key = d
                                shaders[key] = path
            return shaders

    def get_all_shaders(self, shaders):
        """ Function    : get_all_shaders

            Description : Get loaded shader set.

            Input       : dict

            Output      : None

            Return      : Dictionary
        """
        if shaders and isinstance(shaders, dict):
            loaded_shaders = {}
            for k in shaders:
                # Find shader for vert and frag files
                # to construct a dict of the loaded shaders
                name = k.split("_")[0]
                shader = Shader.load(Shader.SL_GLSL,
                                     vertex=shaders["{0}_vert".format(name)],
                                     fragment=shaders["{0}_frag".format(name)])
                # Contains shader memory addresses
                loaded_shaders[name] = shader
            return loaded_shaders

    def set_shadows(self, obj, render):
        if obj and render:
            self.render = render
            # If you don't do this, none of the features
            # listed above will have any effect. Panda will
            # simply ignore normal maps, HDR, and so forth if
            # shader generation is not enabled. It would be reasonable
            # to enable shader generation for the entire game, using this call:
            # obj.set_shader_auto()
            base.shaderenable = 1

            # TODO Fix me!
            ready_shaders = self.get_all_shaders(self.shader_collector())
            obj.set_shader(ready_shaders['Shadows'])

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
                if name == "plight":
                    if self.game_settings['Main']['postprocessing'] == 'off':
                        pass

                    if self.game_settings['Main']['postprocessing'] == 'on':
                        # RP doesn't have nodegraph-like structure to find and remove lights,
                        # so we check self.rp_light before adding light
                        light = PointLight()
                        light.pos = (pos[0], pos[1], pos[2])
                        light.color = (color[0], color[0], color[0])
                        light.set_color_from_temperature(3000.0)
                        light.energy = 100.0
                        light.ies_profile = self.render_pipeline.load_ies_profile("x_arrow.ies")
                        light.casts_shadows = True
                        light.shadow_map_resolution = 1024
                        light.near_plane = 0.2
                        light.radius = 10.0
                        base.rp_lights.append(light)
                        self.render_pipeline.add_light(light)

                if name == 'slight':
                    if self.game_settings['Main']['postprocessing'] == 'off':
                        if render.find("**/{0}".format(name)).is_empty():
                            light = Spotlight(name)
                            light.set_color((color[0], color[0], color[0], 1))
                            lens = PerspectiveLens()
                            light.set_lens(lens)
                            light_np = self.render.attach_new_node(light)
                            # This light is facing backwards, towards the camera.
                            light_np.set_hpr(hpr[0], hpr[1], hpr[2])
                            light_np.set_pos(pos[0], pos[1], pos[2])
                            light_np.set_scale(100)
                            light.look_at(light_np)
                            self.render.set_light(light_np)
                        else:
                            render.clearLight()

                    if self.game_settings['Main']['postprocessing'] == 'on':
                        # RP doesn't have nodegraph-like structure to find and remove lights,
                        # so we check self.rp_light before adding light
                        light = SpotLight()
                        light.pos = (pos[0], pos[1], pos[2])
                        light.color = (color[0], color[0], color[0])
                        light.set_color_from_temperature(3000.0)
                        light.energy = 100
                        light.ies_profile = self.render_pipeline.load_ies_profile("x_arrow.ies")
                        light.casts_shadows = True
                        light.shadow_map_resolution = 512
                        light.near_plane = 0.2
                        light.radius = 0.5
                        light.fov = 10
                        light.direction = (hpr[0], hpr[1], hpr[2])
                        base.rp_lights.append(light)
                        self.render_pipeline.add_light(light)

                if name == 'dlight':
                    if self.game_settings['Main']['postprocessing'] == 'off':
                        if render.find("**/{0}".format(name)).is_empty():
                            light = DirectionalLight(name)
                            light.set_color((color[0], color[0], color[0], 1))
                            light_np = self.render.attach_new_node(light)
                            # This light is facing backwards, towards the camera.
                            light_np.set_hpr(hpr[0], hpr[1], hpr[2])
                            light_np.set_pos(pos[0], pos[1], pos[2])
                            light_np.set_scale(100)
                            self.render.set_light(light_np)
                        else:
                            render.clearLight()

                if name == 'alight':
                    if self.game_settings['Main']['postprocessing'] == 'off':
                        if render.find("**/{0}".format(name)).is_empty():
                            light = AmbientLight(name)
                            light.set_color((color[0], color[0], color[0], 1))
                            light_np = self.render.attach_new_node(light)
                            self.render.set_light(light_np)
                        else:
                            render.clearLight()

    def clear_lighting(self):
        if base.rp_lights and self.render_pipeline.light_mgr.num_lights > 0:
            for i in range(self.render_pipeline.light_mgr.num_lights):
                for light in base.rp_lights:
                    if light:
                        base.rp_lights.remove(light)
                        self.render_pipeline.remove_light(light)

    def get_light_attributes(self):
        pass

    def set_light_attributes(self):
        pass

    def transform_scene_lights(self):
        pass
