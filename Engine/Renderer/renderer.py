from pathlib import Path
from direct.filter.CommonFilters import CommonFilters
from direct.filter.FilterManager import FilterManager
from direct.gui.DirectGui import OnscreenText
from direct.interval.MetaInterval import Sequence
from direct.task.TaskManagerGlobal import taskMgr
from panda3d.core import *
from panda3d.core import FontPool, TextNode
from Engine.Renderer.rpcore import PointLight as RP_PointLight
from Engine.Renderer.rpcore import SpotLight as RP_SpotLight
from direct.particles.ParticleEffect import ParticleEffect
from Engine.Renderer.rpcore.water.projected_water import ProjectedWater
import random


class WaterOptions:
    """ This class stores all options required for the WaterDisplacement """
    size = 128

    wind_dir = Vec2(0.8, 0.6)
    wind_speed = 1600.0
    wind_dependency = 0.2
    choppy_scale = 1.3
    patch_length = 2000.0
    wave_amplitude = 0.35

    time_scale = 0.8
    normalization_factor = 150.0


class RenderAttr:

    def __init__(self):
        self.base = base
        self.game_dir = str(Path.cwd())
        self.fonts = base.fonts_collector()
        # instance of the abstract class
        self.font = FontPool
        self.game_settings = base.game_settings
        if hasattr(base, "render_pipeline") and base.render_pipeline:
            self.render_pipeline = base.render_pipeline
        self.render = None
        self.particles = {}

        self.flame_np = None
        self.proj_water = None
        self.grass_np = None

        # Skybox
        self.skybox_np = None
        self.sky = None
        self.sun = None
        self.offset = 0.0
        self.clouds = []
        self.cloud_x = 0
        self.cloud_y = 0
        self.cloud_z = 0
        self.cloud_speed = 0
        self.time = 0
        self.uv = Vec4(0, 0, 0, 0)

        # Water
        self.water_np = None
        self.water_camera = None
        self.water_buffer = None
        self.ground_mesh = None

        # Set time of day
        self.time_of_day_np = None
        self.time_of_day_light = None
        self.elapsed_seconds = 0
        self.time_of_day_time = 0
        self.minutes = 0
        self.hour = 0

        if self.game_settings['Main']['postprocessing'] == 'off':
            self.gfx_manager = FilterManager(base.win, base.cam)
            self.gfx_filters = CommonFilters(base.win, base.cam)

        # Time of day
        self.elapsed_seconds = 0
        self.minutes = 0
        self.hour = 0

        """ Texts & Fonts"""
        # self.menu_font = self.fonts['OpenSans-Regular']
        self.menu_font = self.fonts['JetBrainsMono-Regular']

        self.time_text_ui = OnscreenText(text="",
                                         pos=(0.0, 0.77),
                                         scale=0.03,
                                         fg=(255, 255, 255, 0.9),
                                         font=self.font.load_font(self.menu_font),
                                         align=TextNode.ALeft,
                                         mayChange=True)

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

    def set_sky_and_clouds(self, cloud_dimensions, cloud_speed, cloud_size, cloud_count, cloud_color):
        if (cloud_dimensions
                and cloud_speed
                and cloud_size
                and cloud_count
                and cloud_color
                and isinstance(cloud_dimensions, list)
                and isinstance(cloud_color, tuple)):
            if not self.skybox_np:
                self.skybox_np = render.attachNewNode('Skybox_P3D')
            cloud_lod = FadeLODNode('CloudLOD')
            cloud_np = NodePath(cloud_lod)
            cloud = render.find("cloud")
            if cloud:
                cloud.reparent_to(cloud_np)
            cloud_lod.addSwitch(1000, 0)

            ready_shaders = self.get_all_shaders(self.base.shader_collector())

            cloud_lod.setFadeTime(5.0)

            self.sky = render.find("sky")
            if self.sky:
                self.sky.reparent_to(self.skybox_np)
                self.sky.setBin('background', 1)
                self.sky.setDepthWrite(0)
                self.sky.setLightOff()
                self.sky.setScale(100)

                self.sun = render.find("sun")
                if self.sun:
                    self.sun.reparent_to(self.skybox_np)
                    self.sun.setBin('background', 1)
                    self.sun.setDepthWrite(0)
                    self.sun.setLightOff()
                    self.sun.setScale(100)
                    self.sun.setP(20)

                    # config here!
                    self.cloud_x = cloud_dimensions[0]
                    self.cloud_y = cloud_dimensions[1]
                    self.cloud_z = cloud_dimensions[2]
                    self.cloud_speed = cloud_speed
                    self.clouds = []
                    for i in range(cloud_count):
                        self.clouds.append(cloud.copyTo(self.skybox_np))
                        self.clouds[-1].getChild(0).setScale(cloud_size + random.random(),
                                                             cloud_size + random.random(),
                                                             cloud_size + random.random())
                        self.clouds[-1].set_pos(render, random.randrange(-self.cloud_x / 2, self.cloud_x / 2),
                                                random.randrange(-self.cloud_y / 2, self.cloud_y / 2),
                                                random.randrange(self.cloud_z) + self.cloud_z * 2)
                        self.clouds[-1].setShaderInput("offset",
                                                       Vec4(random.randrange(5) * 0.25, random.randrange(9) * 0.125, 0,
                                                            0))
                        self.clouds[-1].setShader(ready_shaders['Clouds'])
                        self.clouds[-1].setBillboardPointEye()
                        self.clouds[-1].setDepthWrite(0)
                        self.clouds[-1].setDepthTest(0)
                        # self.clouds[-1].setBin("fixed", 0)
                        self.clouds[-1].setBin('background', 1)

                    self.skybox_np.setColor(cloud_color)
                    self.sky.setColor(1, 1, 1, 1)
                    self.sun.setColor(1, 1, 1, 1)

                    self.time = 0
                    self.uv = Vec4(0, 0, 0.25, 0)
                    render.setShaderInput("time", self.time)
                    render.setShaderInput("uv", self.uv)
                    taskMgr.add(self.update_clouds_task, "update_clouds_task")

    def update_clouds_task(self, task):
        self.time += task.time * self.cloud_speed
        self.offset += task.time
        self.skybox_np.set_pos(base.camera.getPos(render))
        elapsed = task.time * self.cloud_speed
        for model in self.clouds:
            model.setY(model, -task.time * 10.0)
            if model.getY(self.skybox_np) < -self.cloud_y / 2:
                model.setY(self.skybox_np, self.cloud_y / 2)
        self.time += elapsed
        if self.time > 1.0:
            self.cloud_speed *= -1.0
            self.uv[0] += 0.5
            if self.uv[0] > 1.0:
                self.uv[0] = 0
                self.uv[1] += 0.125
                # if self.uv[1] > 1.0:
                #    self.uv = Vec4(0, 0, 0, 0)
        if self.time < 0.0:
            self.cloud_speed *= -1.0
            self.uv[2] += 0.5
            if self.uv[2] > 1.0:
                self.uv[2] = 0.25
                self.uv[3] += 0.125
                # if self.uv[3] > 1.0:
                #    self.uv = Vec4(0, 0, 0, 0)
        render.setShaderInput("time", self.time)
        render.setShaderInput("uv", self.uv)
        return task.again

    def set_time_of_day(self, duration):
        if self.game_settings['Main']['postprocessing'] == 'off':
            # node for the sun to rotate around and look at.
            if not self.time_of_day_np and duration:
                self.time_of_day_np = NodePath("TimeOfday")
            self.time_of_day_np.reparent_to(render)
            self.time_of_day_np.set_pos(0, 0, -10)

            # make the center of the world spin
            worldRotationInterval = self.time_of_day_np.hprInterval(duration, Point3(0, -180, 0),
                                                                    startHpr=Point3(0, 180, 0))
            spinWorld = Sequence(worldRotationInterval, name="spinWorld")
            spinWorld.loop()

            # Directional Light
            self.time_of_day_light = render.attach_new_node(Spotlight("SpotLight_ToD"))

            if self.sun:
                self.time_of_day_light.set_pos(self.sun.get_pos())
            else:
                self.time_of_day_light.set_pos(0, 0, 800)

            self.time_of_day_light.lookAt(self.time_of_day_np)
            render.setLight(self.time_of_day_light)
            self.time_of_day_light.reparent_to(self.time_of_day_np)

            self.time_of_day_light.node().setShadowCaster(True, 2048, 2048)
            self.time_of_day_light.node().showFrustum()
            self.time_of_day_light.node().getLens().setNearFar(80, 800)
            self.time_of_day_light.node().getLens().setFilmSize(800, 800)

            render.set_shader_auto()

            self.set_spotlight_shadows(obj=render, light=self.time_of_day_light, shadow_blur=0.2,
                                       ambient_color=(1.0, 1.0, 1.0))

    def set_time_of_day_clock_task(self, time, duration, task):
        if self.game_settings['Main']['postprocessing'] == 'on':
            if self.render_pipeline and time and duration:
                self.render_pipeline.daytime_mgr.time = time
                self.elapsed_seconds = round(globalClock.getRealTime())

                # seconds floor divided by 60 are equal to 1 minute
                # 1800 seconds are equal to 30 minutes
                self.minutes = self.elapsed_seconds // 60

                if self.base.game_instance['ui_mode']:
                    self.hour = 00
                else:
                    hour = time.split(':')
                    hour = int(hour[0])
                    self.hour = hour

                # 30 minutes of duration
                if duration == 1800:
                    if self.hour == 23:
                        self.hour = 0
                    else:
                        self.hour += self.minutes // 60
                        if self.minutes > 59:
                            self.minutes = 00
                # Seconds of duration
                elif duration < 1800:
                    if self.hour == 23:
                        self.hour = 0
                    else:
                        self.hour += self.minutes
                        if self.elapsed_seconds > 59:
                            self.minutes = 00

                if self.minutes < 10:
                    self.time_text_ui.setText("{0}:0{1}".format(self.hour, self.minutes))
                    self.render_pipeline.daytime_mgr.time = "{0}:0{1}".format(self.hour, self.minutes)
                elif self.minutes > 9:
                    self.time_text_ui.setText("{0}:{1}".format(self.hour, self.minutes))
                    self.render_pipeline.daytime_mgr.time = "{0}:{1}".format(self.hour, self.minutes)

                if not self.base.game_instance['ui_mode']:
                    if 7 <= self.hour < 19:
                        if self.base.game_instance['hud_np']:
                            self.base.game_instance['hud_np'].toggle_day_hud(time="light")
                    elif self.hour >= 19:
                        if self.base.game_instance['hud_np']:
                            self.base.game_instance['hud_np'].toggle_day_hud(time="night")
                else:
                    if self.base.game_instance['hud_np']:
                        self.base.game_instance['hud_np'].toggle_day_hud(time="off")

        elif self.game_settings['Main']['postprocessing'] == 'off':
            if time and duration:
                self.time_of_day_time = time
                self.elapsed_seconds = round(globalClock.getRealTime())

                # seconds floor divided by 60 are equal to 1 minute
                # 1800 seconds are equal to 30 minutes
                self.minutes = self.elapsed_seconds // 60

                hour = time.split(':')
                hour = int(hour[0])
                self.hour = hour

                # 30 minutes of duration
                if duration == 1800:
                    if self.hour == 23:
                        self.hour = 0
                    else:
                        self.hour += self.minutes // 60
                        if self.minutes > 59:
                            self.minutes = 00
                # Seconds of duration
                elif duration < 1800:
                    if self.hour == 23:
                        self.hour = 0
                    else:
                        self.hour += self.minutes
                        if self.elapsed_seconds > 59:
                            self.minutes = 00

                if self.minutes < 10:
                    self.time_text_ui.setText("{0}:0{1}".format(self.hour, self.minutes))
                    self.time_of_day_time = "{0}:0{1}".format(self.hour, self.minutes)
                elif self.minutes > 9:
                    self.time_text_ui.setText("{0}:{1}".format(self.hour, self.minutes))
                    self.time_of_day_time = "{0}:{1}".format(self.hour, self.minutes)

                if not self.base.game_instance['ui_mode']:
                    if 7 <= self.hour < 19:
                        if self.sky:
                            self.sky.setColor(1, 1, 1, 1)
                        if self.sun:
                            self.sun.setColor(1, 1, 1, 1)
                        if self.clouds:
                            self.clouds[-1].setColor(0.6, 0.6, 0.65, 1.0)
                        if self.base.game_instance['hud_np']:
                            self.base.game_instance['hud_np'].toggle_day_hud(time="light")
                    elif self.hour >= 19:
                        if self.sky:
                            self.sky.setColor(0, 0, 0, 0)
                        if self.sun:
                            self.sun.setColor(0, 0, 0, 0)
                        if self.clouds:
                            self.clouds[-1].setColor(0.8, 0.8, 0.85, 1.0)
                        if self.base.game_instance['hud_np']:
                            self.base.game_instance['hud_np'].toggle_day_hud(time="night")

        return task.cont

    def set_projected_water(self, bool_):
        if bool_:
            self.proj_water = ProjectedWater(WaterOptions)
            self.proj_water.setup_water(pipeline=self.render_pipeline, water_level=-3.0)

    def clear_projected_water(self):
        if self.proj_water:
            self.proj_water.clear_water()

    def set_water(self, water_lvl, adv_render):
        MASK_WATER = BitMask32.bit(1)
        MASK_SHADOW = BitMask32.bit(2)

        light = None
        if render.find("**/plight"):
            light = render.find("**/plight")

        if render.find("**/Ground"):
            self.ground_mesh = render.find("**/Ground")
        world = render.find("**/World")
        if world:
            if not adv_render:
                if water_lvl > 0.0 and not render.find("**/water_plane").is_empty():
                    textures = self.base.textures_collector("{0}/Engine/Shaders/".format(self.game_dir))
                    self.water_np = render.find("**/water_plane")
                    self.water_np.set_transparency(True)
                    self.water_np.setTransparency(TransparencyAttrib.MAlpha)
                    self.water_np.flattenLight()
                    self.water_np.reparent_to(world)
                    self.water_np.set_pos(0, 0, -2.0)

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
                    water_plane_np = world.attachNewNode(PlaneNode("WaterNodePath", water_plane))

                    state_init = NodePath("StateInitializer")
                    state_init.set_clip_plane(water_plane_np)
                    state_init.setAttrib(CullFaceAttrib.makeReverse())
                    self.water_camera.node().set_initial_state(state_init.getState())

                    # reflect UV generated on the shader - faster(?)
                    self.water_np.set_shader_input('camera', self.water_camera)
                    self.water_np.set_shader_input("reflection", water_texture)

                    ready_shaders = self.get_all_shaders(self.base.shader_collector())
                    self.water_np.set_shader(ready_shaders['Water'])

                    self.water_np.set_shader_input("water_norm",
                                                   self.base.loader.load_texture(textures["water"]))
                    self.water_np.set_shader_input("water_height",
                                                   self.base.loader.load_texture(textures["ocen3"]))
                    self.water_np.set_shader_input("height",
                                                   self.base.loader.load_texture(textures["heightmap"]))
                    self.water_np.set_shader_input("tile", 20.0)
                    self.water_np.set_shader_input("water_level", water_lvl)
                    self.water_np.set_shader_input("speed", 0.01)
                    self.water_np.set_shader_input("wave", Vec4(0.005, 0.002, 6, 1))

                    self.water_np.set_shader_input("camera_pos", base.camera.get_pos())

                    light_color = light.node().get_color()
                    light_pos = light.get_pos()
                    self.water_np.set_shader_input("light_color", light_color)
                    self.water_np.set_shader_input("light_pos", light_pos)
                    self.water_np.set_shader_input("num_lights", 1)

                    self.ground_mesh.set_shader_input("water_level", water_lvl)
                    render.set_shader_input("fog", Vec4(0.3, 0.3, 0.3, 0.002))  # check!
                    render.set_shader_input("z_scale", 100.0)
                    self.ground_mesh.set_shader_input("tex_scale", 30.0)
                    render.set_shader_input("ambient", Vec4(.001, .001, .001, 1))  # check!

                    taskMgr.add(self.update_water_reflections,
                                "update_water_reflections",
                                extraArgs=[water_plane], appendTask=True)

    def update_water_reflections(self, water_plane_np, task):
        if self.base.game_instance['menu_mode']:
            return task.done

        if self.water_camera and self.water_np:
            if self.water_np.get_z() > 0.0:
                ref_mat = base.cam.get_mat(render) * water_plane_np.get_reflection_mat()
                self.water_camera.set_mat(ref_mat)
                print(ref_mat)
        return task.cont

    def clear_water(self):
        self.water_np.hide()
        self.water_np.set_bin("transparent", 31)
        self.water_buffer.set_active(False)
        self.ground_mesh.set_shader_input("water_level", -1.0)

    def set_grass(self, uv_offset, fogcenter=Vec3(0, 0, 0), adv_render=False):
        if not adv_render and not render.find("**/water_plane").is_empty():
            textures = self.base.textures_collector("{0}/Engine/Shaders/".format(self.game_dir))
            self.grass_np = render.find("**/Grass")
            self.grass_np.setTransparency(TransparencyAttrib.MBinary, 1)
            self.grass_np.reparent_to(self.grass_np.get_parent())
            self.grass_np.setInstanceCount(256)
            self.grass_np.node().setBounds(BoundingBox((0, 0, 0), (256, 256, 128)))
            self.grass_np.node().setFinal(1)

            ready_shaders = self.get_all_shaders(self.base.shader_collector())
            self.grass_np.set_shader(ready_shaders['Grass'])

            self.grass_np.setShaderInput('height', self.base.loader.load_texture(textures["heightmap"]))
            self.grass_np.setShaderInput('grass', self.base.loader.load_texture(textures["grass"]))
            self.grass_np.setShaderInput('uv_offset', uv_offset)
            self.grass_np.setShaderInput('fogcenter', fogcenter)
            # fixme add light
            self.grass_np.setShaderInput('light_color', Vec3(0, 0, 0))
            self.grass_np.set_shader_input("light_pos", Vec3(0, 0, 0))
            self.grass_np.set_shader_input("num_lights", 3)
            self.grass_np.set_pos(0.0, 0.0, 0.0)

        elif adv_render and not render.find("**/water_plane").is_empty():
            textures = self.base.textures_collector("{0}/Engine/Shaders/".format(self.game_dir))
            self.grass_np = render.find("**/Grass")
            self.grass_np.setTransparency(TransparencyAttrib.MBinary, 1)
            self.grass_np.reparent_to(self.grass_np.get_parent())
            self.grass_np.setInstanceCount(256)
            self.grass_np.node().setBounds(BoundingBox((0, 0, 0), (256, 256, 128)))
            self.grass_np.node().setFinal(1)

            self.render_pipeline.set_effect(self.grass_np,
                                            "{0}/Engine/Renderer/effects/grass.yaml".format(self.game_dir),
                                            {},
                                            self.water_camera)

            self.grass_np.setShaderInput('height', self.base.loader.load_texture(textures["heightmap"]))
            self.grass_np.setShaderInput('grass', self.base.loader.load_texture(textures["grass"]))
            self.grass_np.setShaderInput('uv_offset', uv_offset)
            self.grass_np.setShaderInput('fogcenter', fogcenter)
            # fixme add light
            self.grass_np.setShaderInput('light_color', Vec3(0, 0, 0))
            self.grass_np.set_shader_input("light_pos", Vec3(0, 0, 0))
            self.grass_np.set_shader_input("num_lights", 3)
            self.grass_np.set_pos(0.0, 0.0, 0.0)

    def set_flame(self, adv_render):
        # empty_name is a name of NodePath which we use to attach particles to it
        # flame name (associated with .ptf name)
        if not render.find("**/flame_empty_1").is_empty():
            particles_assets = self.base.particles_collector()

            if not particles_assets.get("flame"):
                return

            node_path = render.find("**/{0}".format("flame_empty_1"))
            self.base.enable_particles()
            particles = ParticleEffect()
            particles.load_config(particles_assets["flame"])
            # Use empty geom to start
            particles.start(node_path)
            particles.set_pos(node_path.get_pos())
            # Add particles to keep them in list
            self.particles["flame_empty_1"] = particles

            if adv_render:
                self.render_pipeline.set_effect(node_path,
                                                "{0}/Engine/Renderer/effects/flame.yaml".format(self.game_dir),
                                                {"render_gbuffer": False,
                                                 "render_forward": True,
                                                 "render_shadow": False,
                                                 "alpha_testing": True,
                                                 "normal_mapping": False})

    def clear_flame(self):
        if self.particles:
            self.particles = {}
        self.base.disable_particles()

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
                if self.game_settings['Main']['postprocessing'] == 'off':
                    if name == "plight":
                        light = self.render.attach_new_node(PointLight(name))
                        light.node().set_shadow_caster(True, 512, 512)
                        light.node().set_color((color[0], color[0], color[0], 1))
                        self.render.setLight(light)
                        light.set_pos(pos[0], pos[1], pos[2])
                        self.base.game_instance['rp_lights']["scene"].append(light)
                    elif name == 'slight':
                        light = self.render.attach_new_node(Spotlight(name))
                        light.node().set_shadow_caster(True, 512, 512)
                        light.node().set_color((color[0], color[0], color[0], 1))
                        # light.node().showFrustum()
                        light.node().get_lens().set_fov(40)
                        light.node().get_lens().set_near_far(0.1, 30)
                        self.render.setLight(light)
                        light.set_pos(pos[0], pos[1], pos[2])
                        light.set_hpr(hpr[0], hpr[1], hpr[2])
                        light.attenuation = (1, 0, 1)
                        self.base.game_instance['rp_lights']["scene"].append(light)
                        self.set_spotlight_shadows(obj=self.render, light=light, shadow_blur=0.2,
                                                   ambient_color=(1.0, 1.0, 1.0))

                    elif name == 'dlight':
                        light = DirectionalLight(name)
                        light.set_color((color[0], color[0], color[0], 1))
                        light_np = self.render.attach_new_node(light)
                        # This light is facing backwards, towards the camera.
                        light_np.set_hpr(hpr[0], hpr[1], hpr[2])
                        light_np.set_pos(pos[0], pos[1], pos[2])
                        light_np.set_scale(100)
                        self.render.set_light(light_np)
                        self.base.game_instance['rp_lights']["scene"].append(light)
                        """self.set_spotlight_shadows(obj=self.render, light=light, shadow_blur=0.2,
                                                 ambient_color=(1.0, 1.0, 1.0))"""
                    elif name == 'alight':
                        light = AmbientLight(name)
                        light.set_color((color[0], color[0], color[0], 1))
                        light_np = self.render.attach_new_node(light)
                        self.render.set_light(light_np)
                        self.base.game_instance['rp_lights']["scene"].append(light)
                        """self.set_spotlight_shadows(obj=self.render, light=light, shadow_blur=0.2,
                                                 ambient_color=(1.0, 1.0, 1.0))"""

                if self.game_settings['Main']['postprocessing'] == 'on':
                    if name == "slight":
                        # RP doesn't have nodegraph-like structure to find and remove lights,
                        # so we check self.rp_light before adding light
                        light = RP_SpotLight()
                        light.pos = (pos[0], pos[1], pos[2])
                        light.color = (color[0], color[0], color[0])
                        light.set_color_from_temperature(3000.0)
                        light.energy = 100
                        light.ies_profile = self.render_pipeline.load_ies_profile("x_arrow.ies")
                        light.casts_shadows = True
                        light.shadow_map_resolution = 128
                        light.near_plane = 0.2
                        light.radius = 0.5
                        light.fov = 10
                        light.direction = (hpr[0], hpr[1], hpr[2])
                        self.base.game_instance['rp_lights']["scene"].append(light)
                        self.render_pipeline.add_light(light)
                    elif name == "plight":
                        # RP doesn't have nodegraph-like structure to find and remove lights,
                        # so we check self.rp_light before adding light
                        light = RP_PointLight()
                        light.pos = (pos[0], pos[1], pos[2])
                        light.color = (color[0], color[0], color[0])
                        light.set_color_from_temperature(3000.0)
                        light.energy = 100.0
                        light.ies_profile = self.render_pipeline.load_ies_profile("x_arrow.ies")
                        light.casts_shadows = True
                        light.shadow_map_resolution = 128
                        light.near_plane = 0.2
                        light.radius = 10.0
                        self.base.game_instance['rp_lights']["scene"].append(light)
                        self.render_pipeline.add_light(light)

    def clear_lighting(self):
        if self.base.game_instance['rp_lights'] and self.render_pipeline.light_mgr.num_lights > 0:
            for i in range(self.render_pipeline.light_mgr.num_lights):
                for light in self.base.game_instance['rp_lights']['scene']:
                    if light:
                        self.render_pipeline.remove_light(light)
                        self.base.game_instance['rp_lights']['scene'].remove(light)

    def set_inv_lighting(self, name, render, pos, hpr, color, task):
        if (render
                and name
                and isinstance(name, str)
                and isinstance(pos, list)
                and isinstance(hpr, list)
                and isinstance(color, list)
                and isinstance(task, str)):
            self.render = render
            if task == 'attach':
                if self.game_settings['Main']['postprocessing'] == 'off':
                    if name == "plight":
                        light = self.render.attach_new_node(PointLight(name))
                        light.node().set_shadow_caster(True, 512, 512)
                        light.node().set_color((color[0], color[0], color[0], 1))
                        self.render.setLight(light)
                        light.set_pos(pos[0], pos[1], pos[2])
                        light.attenuation = (1, 0, 1)
                        self.base.game_instance['rp_lights']["inventory"] = light
                    elif name == 'slight':
                        light = self.render.attach_new_node(Spotlight(name))
                        light.node().set_shadow_caster(True, 512, 512)
                        light.node().set_color((color[0], color[0], color[0], 1))
                        # light.node().showFrustum()
                        light.node().get_lens().set_fov(40)
                        light.node().get_lens().set_near_far(0.1, 30)
                        self.render.setLight(light)
                        light.set_pos(pos[0], pos[1], pos[2])
                        light.set_hpr(hpr[0], hpr[1], hpr[2])
                        # light.attenuation = (1, 0, 1)
                        self.base.game_instance['rp_lights']["inventory"] = light

                if self.game_settings['Main']['postprocessing'] == 'on':
                    if name == "slight":
                        # RP doesn't have nodegraph-like structure to find and remove lights,
                        # so we check self.rp_light before adding light
                        if not self.base.game_instance['rp_lights'].get("inventory"):
                            light = RP_SpotLight()
                        else:
                            light = self.base.game_instance['rp_lights']["inventory"]
                        light.pos = (pos[0], pos[1], pos[2])
                        light.color = (color[0], color[0], color[0])
                        light.set_color_from_temperature(5000.0)
                        light.energy = 180
                        light.ies_profile = self.render_pipeline.load_ies_profile("x_arrow.ies")
                        light.casts_shadows = True
                        light.shadow_map_resolution = 512
                        light.direction = (hpr[0], hpr[1], hpr[2])
                        self.base.game_instance['rp_lights']["inventory"] = light
                        self.render_pipeline.add_light(light)
                    elif name == "plight":
                        # RP doesn't have nodegraph-like structure to find and remove lights,
                        # so we check self.rp_light before adding light
                        if not self.base.game_instance['rp_lights'].get("inventory"):
                            light = RP_PointLight()
                        else:
                            light = self.base.game_instance['rp_lights']["inventory"]
                        light.pos = (pos[0], pos[1], pos[2])
                        light.color = (color[0], color[0], color[0])
                        light.set_color_from_temperature(5000.0)
                        light.energy = 100.0
                        light.ies_profile = self.render_pipeline.load_ies_profile("x_arrow.ies")
                        light.casts_shadows = True
                        light.shadow_map_resolution = 128
                        light.near_plane = 0.2
                        light.radius = 10.0
                        self.base.game_instance['rp_lights']["inventory"] = light
                        self.render_pipeline.add_light(light)

    def clear_inv_lighting(self):
        if self.game_settings['Main']['postprocessing'] == 'on':
            if self.base.game_instance['rp_lights'] and self.render_pipeline.light_mgr.num_lights > 0:
                if self.base.game_instance['rp_lights']['inventory']:
                    light = self.base.game_instance['rp_lights']['inventory']
                    self.render_pipeline.remove_light(light)
                    self.base.game_instance['rp_lights'].pop("inventory")
        else:
            if self.base.game_instance['rp_lights']:
                if self.base.game_instance['rp_lights'].get('inventory'):
                    light = self.base.game_instance['rp_lights']['inventory']
                    render.clearLight(light)
                    self.base.game_instance['rp_lights'].pop("inventory")

    def get_light_attributes(self):
        pass

    def set_light_attributes(self):
        pass

    def transform_scene_lights(self):
        pass

    def set_spotlight_shadows(self, obj, light, shadow_blur, ambient_color):
        if obj and light and shadow_blur and ambient_color:
            # If you don't do this, none of the features
            # listed above will have any effect. Panda will
            # simply ignore normal maps, HDR, and so forth if
            # shader generation is not enabled. It would be reasonable
            # to enable shader generation for the entire game, using this call:
            # obj.set_shader_auto()
            base.shaderenable = 1

            ready_shaders = self.get_all_shaders(self.base.shader_collector())
            obj.set_shader(ready_shaders['SpotLightShadows'])
            obj.set_shader_input('my_light', light)
            obj.set_shader_input('shadow_blur', shadow_blur)  # 0.2
            obj.set_shader_input('ambient_color', ambient_color)  # Vec3(1.0, 1.0, 1.0)

    def set_normal_mapping(self, obj, light, shadow_blur, ambient_color):
        if (obj and light
                and isinstance(shadow_blur, int)
                and isinstance(ambient_color, Vec3)):
            ready_shaders = self.get_all_shaders(self.base.shader_collector())
            obj.set_shader(ready_shaders['Normalmapping'])
            obj.set_shader_input('my_light', light)
            obj.set_shader_input('shadow_blur', shadow_blur)  # 0.2
            obj.set_shader_input('ambient_color', ambient_color)  # Vec3(1.0, 1.0, 1.0)

    def set_weather(self, weather):
        if weather and isinstance(weather, str):
            if weather == "wind":
                pass
            elif weather == "rain":
                pass
            elif weather == "storm":
                pass
            elif weather == "day":
                pass
            elif weather == "night":
                pass

    def set_hardware_skinning(self, actor, bool_):
        # Perform hardware skinning on GPU.
        if actor and isinstance(bool_, bool):
            self.base.game_instance['hw_skinning'] = False

            if self.game_settings['Main']['postprocessing'] == 'on' and bool_:
                self.render_pipeline.set_effect(actor,
                                                "{0}/Engine/Renderer/effects/hardware_skinning.yaml".format(
                                                    self.game_dir),
                                                options={}, sort=25)
                attrib = actor.get_attrib(ShaderAttrib)
                attrib = attrib.set_flag(ShaderAttrib.F_hardware_skinning, bool_)
                actor.set_attrib(attrib)
                self.base.game_instance['hw_skinning'] = True

            elif self.game_settings['Main']['postprocessing'] == 'off' and bool_:
                ready_shaders = self.get_all_shaders(self.base.shader_collector())
                actor.set_shader(ready_shaders['HardwareSkinning'])
                attrib = actor.get_attrib(ShaderAttrib)
                attrib = attrib.set_flag(ShaderAttrib.F_hardware_skinning, bool_)
                actor.set_attrib(attrib)
                self.base.game_instance['hw_skinning'] = True

    def setup_native_renderer(self, bool_, task):
        if isinstance(bool_, bool) and bool_:
            if self.base.game_instance['loading_is_done'] == 1:
                """depth_tex = Texture()
                normal_tex = Texture()
                quad = self.gfx_manager.renderSceneInto(textures={'depth': depth_tex,
                                                                  'aux0': normal_tex})
                vs_cam_pos = base.camera.get_pos()
                name = "{0}:BS".format(self.base.game_instance['player_ref'].get_name())
                player_pos = render.find("**/{0}".format(name)).get_pos()
                ready_shaders = self.get_all_shaders(self.base.shader_collector())
                quad.set_shader(ready_shaders['SSAO'])
                quad.set_shader_input('g_screen_size', Vec2(1920, 1080))
                quad.set_shader_input('normal_map', normal_tex)
                quad.set_shader_input('depth_map', depth_tex)
                quad.set_shader_input('texpad_depth', Vec4(1, 1, 1, 1))
                quad.set_shader_input('vs_cam_pos', vs_cam_pos)
                quad.set_shader_input('vs_model_pos', player_pos)"""

                """ NATIVE SSAO """
                self.gfx_filters.set_ambient_occlusion(numsamples=16,
                                                       radius=2.2,
                                                       amount=2.0,
                                                       strength=0.01,
                                                       falloff=0.000002)
                self.gfx_filters.set_bloom()

                """if self.time_of_day_light:
                    self.gfx_filters.set_volumetric_lighting(caster=self.time_of_day_light,
                                                             numsamples=32,
                                                             density=1.0,
                                                             decay=0.98,
                                                             exposure=0.2)"""
                """self.set_spotlight_shadows(obj=self.render, light=light, shadow_blur=0.2,
                                           ambient_color=(1.0, 1.0, 1.0))"""
                # self.gfx_filters.set_gamma_adjust(1.5)

                return task.done

        return task.cont
