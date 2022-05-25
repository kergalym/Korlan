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
        if self.base.game_instance["renderpipeline_np"]:
            self.render_pipeline = self.base.game_instance["renderpipeline_np"]
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

        return task.cont

    def set_projected_water(self, bool_):
        if bool_:
            self.proj_water = ProjectedWater(WaterOptions)
            self.proj_water.setup_water(pipeline=self.render_pipeline, water_level=-3.0)

    def clear_projected_water(self):
        if self.proj_water:
            self.proj_water.clear_water()

    def set_grass(self, uv_offset, fogcenter=Vec3(0, 0, 0), adv_render=False):
        if adv_render and not render.find("**/water_plane").is_empty():
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

    def set_flame(self, adv_render, scene_np, flame_scale):
        # empty_name is a name of NodePath which we use to attach particles to it
        # flame name (associated with .ptf name)
        particles_assets = self.base.particles_collector()

        if scene_np and particles_assets.get("flame"):
            for node_path in scene_np.get_children():
                if "flame_empty" in node_path.get_name():
                    # RP doesn't have nodegraph-like structure to find and remove lights,
                    # so we check self.rp_light before adding light
                    light = RP_PointLight()
                    light.pos = node_path.get_pos() + Vec3(0, 0, 1.5)
                    light.set_color_from_temperature(2400.0)
                    light.energy = 5.0
                    light.ies_profile = self.render_pipeline.load_ies_profile("x_arrow.ies")
                    light.casts_shadows = True
                    light.shadow_map_resolution = 128
                    light.near_plane = 0.2
                    light.radius = 1.9
                    # light.inner_radius = 10.0
                    self.base.game_instance['rp_lights']["flame"].append(light)
                    self.render_pipeline.add_light(light)

                    self.base.enable_particles()
                    particles = ParticleEffect()
                    particles.load_config(particles_assets["flame"])
                    # Use empty geom to start
                    particles.start(node_path)

                    if flame_scale and isinstance(flame_scale, float):
                        node_path.set_scale(flame_scale)

                    # Add particles to keep them in list
                    self.particles[node_path.get_name()] = particles

                    if adv_render:
                        self.render_pipeline.set_effect(node_path,
                                                        "{0}/Engine/Renderer/effects/flame.yaml".format(self.game_dir),
                                                        {"render_gbuffer": True,
                                                         "render_forward": False,
                                                         "render_shadow": False,
                                                         "alpha_testing": True,
                                                         "normal_mapping": False})

    def set_flame_hearth(self, adv_render, scene_np, flame_scale):
        # empty_name is a name of NodePath which we use to attach particles to it
        # flame name (associated with .ptf name)
        particles_assets = self.base.particles_collector()

        if (scene_np
                and particles_assets.get("flame_l")
                and particles_assets.get("flame_r")):

            for node_path in scene_np.get_children():
                if "light_empty_hearth" in node_path.get_name():
                    # RP doesn't have nodegraph-like structure to find and remove lights,
                    # so we check self.rp_light before adding light

                    # Put first light under hearth
                    light_u = RP_PointLight()
                    light_u.pos = Vec3(node_path.get_x(), node_path.get_y(), 0.3)
                    light_u.set_color_from_temperature(1000.0)
                    light_u.energy = 2.0
                    light_u.ies_profile = self.render_pipeline.load_ies_profile("x_arrow.ies")
                    light_u.casts_shadows = True
                    light_u.shadow_map_resolution = 128
                    light_u.near_plane = 0.2
                    light_u.radius = 3.0
                    # light.inner_radius = 10.0
                    self.base.game_instance['rp_lights']["flame"].append(light_u)
                    self.render_pipeline.add_light(light_u)

                    # Put second light above hearth
                    light_a = RP_PointLight()
                    light_a.pos = Vec3(node_path.get_x(), node_path.get_y(), 1.7)
                    light_a.set_color_from_temperature(1000.0)
                    light_a.energy = 5.0
                    light_a.ies_profile = self.render_pipeline.load_ies_profile("x_arrow.ies")
                    light_a.casts_shadows = True
                    light_a.shadow_map_resolution = 128
                    light_a.near_plane = 0.2
                    light_a.radius = 3.0
                    # light.inner_radius = 10.0
                    self.base.game_instance['rp_lights']["flame"].append(light_a)
                    self.render_pipeline.add_light(light_a)

                    # base.h_light = light
                if "flame_empty_hearth" in node_path.get_name():
                    self.base.enable_particles()
                    particles_l = ParticleEffect()
                    particles_l.load_config(particles_assets["flame_l"])
                    # Use empty geom to start
                    particles_l.start(node_path)

                    if flame_scale and isinstance(flame_scale, float):
                        node_path.set_scale(flame_scale)

                    # Add particles to keep them in list
                    self.particles[node_path.get_name()] = particles_l

                    particles_r = ParticleEffect()
                    particles_r.load_config(particles_assets["flame_r"])
                    # Use empty geom to start
                    particles_r.start(node_path)

                    if flame_scale and isinstance(flame_scale, float):
                        node_path.set_scale(flame_scale)

                    # Add particles to keep them in list
                    self.particles[node_path.get_name()] = particles_r

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

        if self.base.game_instance['rp_lights'] and self.render_pipeline.light_mgr.num_lights > 0:
            for i in range(self.render_pipeline.light_mgr.num_lights):
                for light in self.base.game_instance['rp_lights']['flame']:
                    if light:
                        self.render_pipeline.remove_light(light)
                        self.base.game_instance['rp_lights']['flame'].remove(light)

        if taskMgr.hasTaskNamed("dynamic_lighting_task"):
            taskMgr.remove("dynamic_lighting_task")

    def set_smoke(self, adv_render, scene_np, smoke_scale):
        # empty_name is a name of NodePath which we use to attach particles to it
        # flame name (associated with .ptf name)
        particles_assets = self.base.particles_collector()

        if scene_np and particles_assets.get("flame"):
            for node_path in scene_np.get_children():
                if "smoke_empty" in node_path.get_name():
                    self.base.enable_particles()
                    particles = ParticleEffect()
                    particles.load_config(particles_assets["flame"])
                    # Use empty geom to start
                    particles.start(node_path)

                    if smoke_scale and isinstance(smoke_scale, float):
                        node_path.set_scale(smoke_scale)

                    # Add particles to keep them in list
                    self.particles[node_path.get_name()] = particles

                    if adv_render:
                        self.render_pipeline.set_effect(node_path,
                                                        "{0}/Engine/Renderer/effects/flame.yaml".format(self.game_dir),
                                                        {"render_gbuffer": False,
                                                         "render_forward": True,
                                                         "render_shadow": False,
                                                         "alpha_testing": True,
                                                         "normal_mapping": False})
                        node_path.set_shader_input("colorA", Vec3(0.149, 0.141, 0.912))
                        node_path.set_shader_input("colorB", Vec3(1.000, 0.833, 0.224))

    def set_smoke_hearth(self, adv_render, scene_np, smoke_scale):
        # empty_name is a name of NodePath which we use to attach particles to it
        # flame name (associated with .ptf name)
        particles_assets = self.base.particles_collector()

        if (scene_np
                and particles_assets.get("flame_l")
                and particles_assets.get("flame_r")):

            for node_path in scene_np.get_children():
                if "smoke_empty_hearth" in node_path.get_name():
                    self.base.enable_particles()
                    particles_l = ParticleEffect()
                    particles_l.load_config(particles_assets["flame_l"])
                    # Use empty geom to start
                    particles_l.start(node_path)

                    if smoke_scale and isinstance(smoke_scale, float):
                        node_path.set_scale(smoke_scale)

                    # Add particles to keep them in list
                    self.particles[node_path.get_name()] = particles_l

                    particles_r = ParticleEffect()
                    particles_r.load_config(particles_assets["flame_r"])
                    # Use empty geom to start
                    particles_r.start(node_path)

                    if smoke_scale and isinstance(smoke_scale, float):
                        node_path.set_scale(smoke_scale)

                    # Add particles to keep them in list
                    self.particles[node_path.get_name()] = particles_r

                    if adv_render:
                        self.render_pipeline.set_effect(node_path,
                                                        "{0}/Engine/Renderer/effects/smoke.yaml".format(self.game_dir),
                                                        {"render_gbuffer": False,
                                                         "render_forward": True,
                                                         "render_shadow": False,
                                                         "alpha_testing": True,
                                                         "normal_mapping": False})
                        node_path.set_shader_input("colorA", Vec3(0.149, 0.141, 0.912))
                        node_path.set_shader_input("colorB", Vec3(1.000, 0.833, 0.224))

    def clear_smoke(self):
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
        if self.game_settings['Main']['postprocessing'] == 'on':
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

    def apply_lightmap_to_scene(self, scene, lightmap):
        """
        if scene and isinstance(lightmap, str) and lightmap:
            ts = TextureStage("lightmap")
            path = "{0}/Assets/Lightmaps/{1}.png".format(self.game_dir, lightmap)
            lightmap = base.loader.load_texture(path)
            ts.set_texcoord_name("lightmap")
            scene.set_texture(ts, lightmap)
            self.render_pipeline.set_effect(scene,
                                            "{0}/Engine/Renderer/effects/default.yaml".format(self.game_dir),
                                            {"render_gbuffer": True,
                                             "render_forward": False,
                                             "render_shadow": False,
                                             "alpha_testing": True,
                                             "normal_mapping": True})
            """

