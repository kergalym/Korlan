from os.path import exists
from pathlib import Path, PurePath
from os import walk

from direct.gui.DirectGui import OnscreenText
from direct.interval.MetaInterval import Sequence
from direct.task.TaskManagerGlobal import taskMgr
from panda3d.core import *
from panda3d.core import FontPool, TextNode
from Engine.Render.rpcore import PointLight, SpotLight
from direct.particles.ParticleEffect import ParticleEffect
import random


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
        self.particles = {}
        self.base.particles_emis = None

        self.flame_np = None
        self.water_np = None
        self.water_camera = None
        self.water_buffer = None
        self.grass_np = None

        # Set time of day
        self.time_of_day_np = None
        self.time_of_day_light = None
        self.elapsed_seconds = 0
        self.time_of_day_time = 0
        self.minutes = 0
        self.hour = 0

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
                cloud.reparentTo(cloud_np)
            cloud_lod.addSwitch(1000, 0)

            ready_shaders = self.get_all_shaders(self.shader_collector())

            cloud_lod.setFadeTime(5.0)

            self.sky = render.find("sky")
            if self.sky:
                self.sky.reparentTo(self.skybox_np)
                self.sky.setBin('background', 1)
                self.sky.setDepthWrite(0)
                self.sky.setLightOff()
                self.sky.setScale(100)

                self.sun = render.find("sun")
                if self.sun:
                    self.sun.reparentTo(self.skybox_np)
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
                        self.clouds[-1].setPos(render, random.randrange(-self.cloud_x / 2, self.cloud_x / 2),
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
        self.skybox_np.setPos(base.camera.getPos(render))
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
            self.time_of_day_np.reparentTo(render)
            self.time_of_day_np.setPos(0, 0, -10)

            # make the center of the world spin
            worldRotationInterval = self.time_of_day_np.hprInterval(duration, Point3(0, -180, 0),
                                                                    startHpr=Point3(0, 180, 0))
            spinWorld = Sequence(worldRotationInterval, name="spinWorld")
            spinWorld.loop()

            # Directional Light
            self.time_of_day_light = render.attachNewNode(Spotlight("SpotLight_ToD"))

            if self.sun:
                self.time_of_day_light.setPos(self.sun.get_pos())
            else:
                self.time_of_day_light.setPos(0, 0, 800)

            self.time_of_day_light.lookAt(self.time_of_day_np)
            render.setLight(self.time_of_day_light)
            self.time_of_day_light.reparentTo(self.time_of_day_np)

            self.time_of_day_light.node().setShadowCaster(True, 2048, 2048)
            self.time_of_day_light.node().showFrustum()
            self.time_of_day_light.node().getLens().setNearFar(80, 800)
            self.time_of_day_light.node().getLens().setFilmSize(800, 800)

            render.set_shader_auto()

            self.set_spotlight_shadows(obj=render, light=self.time_of_day_light, shadow_blur=0.2,
                                       ambient_color=(1.0, 1.0, 1.0))

    def set_time_of_day_clock_task(self, time, duration, task):
        if (not base.game_mode
                and base.menu_mode):
            self.time_text_ui.hide()
            return task.done
        else:
            if self.time_text_ui:
                self.time_text_ui.show()

        if self.game_settings['Main']['postprocessing'] == 'on':
            if self.render_pipeline and time and duration:
                self.render_pipeline.daytime_mgr.time = time
                self.elapsed_seconds = round(globalClock.getRealTime())

                # seconds floor divided by 60 are equal to 1 minute
                # 1800 seconds are equal to 30 minutes
                self.minutes = self.elapsed_seconds // 60

                if base.is_ui_active:
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

                if (not hasattr(base, "is_ui_active")
                        or hasattr(base, "is_ui_active")
                        and not base.is_ui_active):
                    if 7 <= self.hour < 19:
                        if hasattr(base, "hud") and base.hud:
                            base.hud.toggle_day_hud(time="light")
                    elif self.hour >= 19:
                        if hasattr(base, "hud") and base.hud:
                            base.hud.toggle_day_hud(time="night")
                else:
                    if hasattr(base, "hud") and base.hud:
                        base.hud.toggle_day_hud(time="off")

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

                if (not hasattr(base, "is_ui_active")
                        or hasattr(base, "is_ui_active")
                        and not base.is_ui_active):
                    if 7 <= self.hour < 19:
                        if self.sky:
                            self.sky.setColor(1, 1, 1, 1)
                        if self.sun:
                            self.sun.setColor(1, 1, 1, 1)
                        if self.clouds:
                            self.clouds[-1].setColor(0.6, 0.6, 0.65, 1.0)
                        if hasattr(base, "hud") and base.hud:
                            base.hud.toggle_day_hud(time="light")
                    elif self.hour >= 19:
                        if self.sky:
                            self.sky.setColor(0, 0, 0, 0)
                        if self.sun:
                            self.sun.setColor(0, 0, 0, 0)
                        if self.clouds:
                            self.clouds[-1].setColor(0.8, 0.8, 0.85, 1.0)
                        if hasattr(base, "hud") and base.hud:
                            base.hud.toggle_day_hud(time="night")

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
                            if "frag.glsl" in file:
                                key = "{0}_{1}".format(d, "frag")
                                shaders[key] = path
                            if "vert.glsl" in file:
                                key = "{0}_{1}".format(d, "vert")
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

    def set_hardware_skinning(self, actor, bool_):
        # Perform hardware skinning on GPU.
        if actor and isinstance(bool_, bool):
            if self.game_settings['Main']['postprocessing'] == 'on' and bool_:
                self.render_pipeline.set_effect(actor,
                                                "{0}/Engine/Render/effects/hardware_skinning.yaml".format(
                                                    self.game_dir),
                                                options={}, sort=25)
                attrib = actor.get_attrib(ShaderAttrib)
                attrib = attrib.set_flag(ShaderAttrib.F_hardware_skinning, bool_)
                actor.set_attrib(attrib)

            elif self.game_settings['Main']['postprocessing'] == 'off' and bool_:
                ready_shaders = self.get_all_shaders(self.shader_collector())
                actor.set_shader(ready_shaders['HardwareSkinning'])
                attrib = actor.get_attrib(ShaderAttrib)
                attrib = attrib.set_flag(ShaderAttrib.F_hardware_skinning, bool_)
                actor.set_attrib(attrib)

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

                    ready_shaders = self.get_all_shaders(self.shader_collector())
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

                ready_shaders = self.get_all_shaders(self.shader_collector())
                self.grass_np.set_shader(ready_shaders['Grass'])

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

        if base.game_mode is False and base.menu_mode:
            return task.done

        return task.cont

    def clear_flame(self):
        if self.flame_np and not render.find("**/flame").is_empty():
            render.find("**/flame").remove_node()
            taskMgr.remove("flame_proc_shader_task")

    def set_flame_particles(self, name, empty_name):
        # empty_name is a name of NodePath which we use to attach particles to it
        # name is flame name (associated with .ptf name)
        if (isinstance(name, str)
                and isinstance(empty_name, str)
                and not render.find("**/{0}".format(empty_name)).is_empty()):
            # Collected emissive geoms
            self.base.particles_emis = self.base.assets_collector()
            # Collected .ptf files
            particles_assets = self.base.particles_collector()

            if not particles_assets.get(name):
                return

            if not self.base.particles_emis.get('emi'):
                return

            node_path = render.find("**/{0}".format(empty_name))
            self.base.enable_particles()
            particles = ParticleEffect()
            particles.load_config(particles_assets[name])
            # Sets particles to birth relative to the teapot, but to render at
            # toplevel
            particles.start(node_path)
            particles.set_pos(node_path.get_pos())
            # Add particles to keep them in list
            self.particles[empty_name] = particles

            # Disable shading for particles emission
            emi = render.find("**/emi")
            if emi:
                self.render_pipeline.set_effect(emi,
                                                "{0}/Engine/Render/effects/default.yaml".format(self.game_dir),
                                                {"render_gbuffer": True,
                                                 "render_shadow": False,
                                                 "alpha_testing": True,
                                                 "normal_mapping": True})

    def clear_flame_particles(self):
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
                        light.attenuation = (1, 0, 1)
                        base.rp_lights["scene"].append(light)
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
                        base.rp_lights["scene"].append(light)
                        self.set_spotlight_shadows(obj=self.render, light=light, shadow_blur=0.2,
                                                   ambient_color=(1.0, 1.0, 1.0))

                    elif name == 'dlight':
                        if self.game_settings['Main']['postprocessing'] == 'off':
                            light = DirectionalLight(name)
                            light.set_color((color[0], color[0], color[0], 1))
                            light_np = self.render.attach_new_node(light)
                            # This light is facing backwards, towards the camera.
                            light_np.set_hpr(hpr[0], hpr[1], hpr[2])
                            light_np.set_pos(pos[0], pos[1], pos[2])
                            light_np.set_scale(100)
                            self.render.set_light(light_np)
                            base.rp_lights["scene"].append(light)
                            """self.set_spotlight_shadows(obj=self.render, light=light, shadow_blur=0.2,
                                                 ambient_color=(1.0, 1.0, 1.0))"""
                    elif name == 'alight':
                        if self.game_settings['Main']['postprocessing'] == 'off':
                            light = AmbientLight(name)
                            light.set_color((color[0], color[0], color[0], 1))
                            light_np = self.render.attach_new_node(light)
                            self.render.set_light(light_np)
                            base.rp_lights["scene"].append(light)
                            """self.set_spotlight_shadows(obj=self.render, light=light, shadow_blur=0.2,
                                                 ambient_color=(1.0, 1.0, 1.0))"""

                if self.game_settings['Main']['postprocessing'] == 'on':
                    if name == "slight":
                        # RP doesn't have nodegraph-like structure to find and remove lights,
                        # so we check self.rp_light before adding light
                        light = SpotLight()
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
                        base.rp_lights["scene"].append(light)
                        self.render_pipeline.add_light(light)
                    elif name == "plight":
                        # RP doesn't have nodegraph-like structure to find and remove lights,
                        # so we check self.rp_light before adding light
                        light = PointLight()
                        light.pos = (pos[0], pos[1], pos[2])
                        light.color = (color[0], color[0], color[0])
                        light.set_color_from_temperature(3000.0)
                        light.energy = 100.0
                        light.ies_profile = self.render_pipeline.load_ies_profile("x_arrow.ies")
                        light.casts_shadows = True
                        light.shadow_map_resolution = 128
                        light.near_plane = 0.2
                        light.radius = 10.0
                        base.rp_lights["scene"].append(light)
                        self.render_pipeline.add_light(light)

    def clear_lighting(self):
        if base.rp_lights and self.render_pipeline.light_mgr.num_lights > 0:
            for i in range(self.render_pipeline.light_mgr.num_lights):
                for light in base.rp_lights['scene']:
                    if light:
                        self.render_pipeline.remove_light(light)
                        base.rp_lights['scene'].remove(light)

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
                        base.rp_lights["inventory"] = light
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
                        base.rp_lights["inventory"] = light
                        self.set_spotlight_shadows(obj=self.render, light=light, shadow_blur=0.2,
                                                   ambient_color=(1.0, 1.0, 1.0))

                if self.game_settings['Main']['postprocessing'] == 'on':
                    if name == "slight":
                        # RP doesn't have nodegraph-like structure to find and remove lights,
                        # so we check self.rp_light before adding light
                        if not base.rp_lights.get("inventory"):
                            light = SpotLight()
                        else:
                            light = base.rp_lights["inventory"]
                        light.pos = (pos[0], pos[1], pos[2])
                        light.color = (color[0], color[0], color[0])
                        light.set_color_from_temperature(6000.0)
                        light.energy = 100
                        light.ies_profile = self.render_pipeline.load_ies_profile("x_arrow.ies")
                        light.casts_shadows = True
                        light.shadow_map_resolution = 512
                        light.direction = (hpr[0], hpr[1], hpr[2])
                        base.rp_lights["inventory"] = light
                        self.render_pipeline.add_light(light)
                    elif name == "plight":
                        # RP doesn't have nodegraph-like structure to find and remove lights,
                        # so we check self.rp_light before adding light
                        if not base.rp_lights.get("inventory"):
                            light = PointLight()
                        else:
                            light = base.rp_lights["inventory"]
                        light.pos = (pos[0], pos[1], pos[2])
                        light.color = (color[0], color[0], color[0])
                        light.set_color_from_temperature(6000.0)
                        light.energy = 100.0
                        light.ies_profile = self.render_pipeline.load_ies_profile("x_arrow.ies")
                        light.casts_shadows = True
                        light.shadow_map_resolution = 128
                        light.near_plane = 0.2
                        light.radius = 10.0
                        base.rp_lights["inventory"] = light
                        self.render_pipeline.add_light(light)

    def clear_inv_lighting(self):
        if self.game_settings['Main']['postprocessing'] == 'on':
            if base.rp_lights and self.render_pipeline.light_mgr.num_lights > 0:
                if base.rp_lights['inventory']:
                    light = base.rp_lights['inventory']
                    self.render_pipeline.remove_light(light)
                    base.rp_lights.pop("inventory")
        else:
            if base.rp_lights:
                if base.rp_lights.get('inventory'):
                    light = base.rp_lights['inventory']
                    render.clearLight(light)
                    base.rp_lights.pop("inventory")

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

            ready_shaders = self.get_all_shaders(self.shader_collector())
            obj.set_shader(ready_shaders['SpotLightShadows'])
            obj.set_shader_input('my_light', light)
            obj.set_shader_input('shadow_blur', shadow_blur)  # 0.2
            obj.set_shader_input('ambient_color', ambient_color)  # Vec3(1.0, 1.0, 1.0)

    def set_normal_mapping(self, obj):
        if obj:
            ready_shaders = self.get_all_shaders(self.shader_collector())
            obj.set_shader(ready_shaders['Normalmapping'])
            """obj.set_shader_input('my_light', light)
            obj.set_shader_input('shadow_blur', shadow_blur)  # 0.2
            obj.set_shader_input('ambient_color', ambient_color)  # Vec3(1.0, 1.0, 1.0)"""
