import math
from pathlib import Path
from random import uniform
from direct.gui.DirectGui import OnscreenText
from direct.task.TaskManagerGlobal import taskMgr
from panda3d.core import *
from panda3d.core import FontPool, TextNode
from Engine.Renderer.rpcore import PointLight as RP_PointLight
from Engine.Renderer.rpcore import SpotLight as RP_SpotLight
from direct.particles.ParticleEffect import ParticleEffect


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

        self.render = None
        self.particles = {}

        # Water and grass
        self.proj_water = None
        self.grass_np = None

        # Time of day
        self.time_of_day_np = None
        self.time_of_day_light = None
        self.elapsed_seconds = 0
        self.time_of_day_time = 0
        self.minutes = 0
        self.hour = 0
        self.day = 0

        # Light Energy
        self.flame_light_u_energy = 1.0
        self.flame_light_a_energy = 4.0
        self.flame_light_u_half_energy = 0.5
        self.flame_light_a_half_energy = 2.0

        # Flame flickering rate
        self.flame_rate = 3.0

        """ Texts & Fonts"""
        # self.menu_font = self.fonts['OpenSans-Regular']
        self.menu_font = self.fonts['JetBrainsMono-Regular']

        self.time_text_ui = OnscreenText(text="",
                                         pos=(0.0, 0.77),
                                         scale=0.04,
                                         fg=(255, 255, 255, 0.9),
                                         font=self.font.load_font(self.menu_font),
                                         align=TextNode.A_center,
                                         mayChange=True)

    def set_time_of_day_clock_task(self, time, duration, task):
        if (time and self.base.game_instance['loading_is_done'] == 0
                and self.base.game_instance["renderpipeline_np"]):
            self.base.game_instance["renderpipeline_np"].daytime_mgr.time = time

        if self.base.game_instance['loading_is_done'] == 1:
            if self.base.game_instance["renderpipeline_np"] and time and duration:
                self.base.game_instance["renderpipeline_np"].daytime_mgr.time = time
                self.elapsed_seconds = round(globalClock.getRealTime())
    
                # seconds floor divided by 60 are equal to 1 minute
                # 1800 seconds are equal to 30 minutes
                self.minutes = self.elapsed_seconds // 60
    
                if self.base.game_instance['inv_mode']:
                    self.hour = 15
                else:
                    hour = time.split(':')
                    hour = int(hour[0])
                    self.hour = hour
    
                # 30 minutes of duration
                if duration == 1800:
                    self.hour += self.minutes // 60
                    if self.minutes > 59:
                        self.minutes = 00

                # Seconds of duration
                elif duration < 1800:
                    self.hour += self.minutes
                    if self.elapsed_seconds > 59:
                        self.minutes = 00
    
                # Day counting
                if self.hour == 0 and self.elapsed_seconds == 00:
                    self.day += 1
    
                if self.minutes < 10:
                    text = "Day {0}    {1}:0{2}".format(self.day, self.hour, self.minutes)
                    self.time_text_ui.setText(text)
                    self.base.game_instance["renderpipeline_np"].daytime_mgr.time = "{0}:0{1}".format(self.hour,
                                                                                                      self.minutes)
                elif self.minutes > 9:
                    text = "Day {0}    {1}:{2}".format(self.day, self.hour, self.minutes)
                    self.time_text_ui.setText(text)
                    self.base.game_instance["renderpipeline_np"].daytime_mgr.time = "{0}:{1}".format(self.hour,
                                                                                                     self.minutes)
    
                self.base.game_instance["world_time"] = "{0}:{1}".format(self.hour, self.minutes)
    
                if not self.base.game_instance['ui_mode']:
                    if 7 <= self.hour < 19:
                        if self.base.game_instance['hud_np']:
                            self.base.game_instance['hud_np'].toggle_day_hud(time="light")
                    elif self.hour >= 19:
                        if self.base.game_instance['hud_np']:
                            self.base.game_instance['hud_np'].toggle_day_hud(time="night")
                    elif self.hour > 1 and self.hour < 7:
                        if self.base.game_instance['hud_np']:
                            self.base.game_instance['hud_np'].toggle_day_hud(time="night")
                else:
                    if self.base.game_instance['hud_np']:
                        self.base.game_instance['hud_np'].toggle_day_hud(time="off")

        return task.cont

    def set_projected_water(self, bool_):
        if self.base.game_instance["renderpipeline_np"] and bool_:
            from Engine.Renderer.rpcore.water.projected_water import ProjectedWater
            self.proj_water = ProjectedWater(WaterOptions)
            self.proj_water.setup_water(pipeline=self.base.game_instance["renderpipeline_np"],
                                        water_level=-3.0)

    def clear_projected_water(self):
        if self.proj_water:
            self.proj_water.clear_water()
            self.proj_water = None

    def set_grass(self, uv_offset, fogcenter=Vec3(0, 0, 0), adv_render=False):
        textures = self.base.textures_collector("{0}/Engine/Shaders/".format(self.game_dir))
        if self.base.game_instance["renderpipeline_np"] and textures:
            self.grass_np = render.find("**/Grass")
            self.grass_np.setTransparency(TransparencyAttrib.MBinary, 1)
            self.grass_np.reparent_to(self.grass_np.get_parent())
            self.grass_np.setInstanceCount(256)
            self.grass_np.node().setBounds(BoundingBox((0, 0, 0), (256, 256, 128)))
            self.grass_np.node().setFinal(1)
            if adv_render:
                self.base.game_instance["renderpipeline_np"].set_effect(self.grass_np,
                                                                        "{0}/Engine/Renderer/effects/grass.yaml".format(
                                                                            self.game_dir),
                                                                        {})
            self.grass_np.set_shader_input('height', self.base.loader.load_texture(textures["heightmap"]))
            self.grass_np.set_shader_input('grass', self.base.loader.load_texture(textures["grass"]))
            self.grass_np.set_shader_input('uv_offset', uv_offset)
            self.grass_np.set_shader_input('fogcenter', fogcenter)
            # fixme add light
            self.grass_np.set_shader_input('light_color', Vec3(0, 0, 0))
            self.grass_np.set_shader_input("light_pos", Vec3(0, 0, 0))
            self.grass_np.set_shader_input("num_lights", 3)
            self.grass_np.set_pos(0.0, 0.0, 0.0)

    def do_flame_light_flicker_task(self, light_a, light_u, task):
        if self.base.game_instance["menu_mode"]:
            return task.done

        frame_time = globalClock.getDt()

        # Sinusoid brightness values
        brightness = math.sin(self.flame_rate * frame_time)

        # Lights brightness with flickering speed included
        light_a_result = self.flame_light_a_half_energy / 2.0 + brightness * self.flame_light_a_energy
        light_u_result = self.flame_light_u_half_energy / 2.0 + brightness * self.flame_light_u_energy

        light_a.energy = uniform(self.flame_light_a_half_energy, light_a_result)
        light_u.energy = uniform(self.flame_light_u_half_energy, light_u_result)

        return task.cont

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

                    if self.base.game_instance["renderpipeline_np"] and adv_render:
                        # Put second light above hearth
                        light_a = RP_PointLight()
                        light_a.pos = Vec3(node_path.get_x(), node_path.get_y(), 1.7)
                        light_a.set_color_from_temperature(1000.0)
                        light_a.energy = self.flame_light_a_energy
                        light_a.ies_profile = self.base.game_instance["renderpipeline_np"].load_ies_profile("pear.ies")
                        light_a.casts_shadows = True
                        light_a.shadow_map_resolution = 512
                        light_a.near_plane = 0.2
                        light_a.radius = 3.0
                        # light_a.inner_radius = 0.2
                        self.base.game_instance['rp_lights']["flame"].append(light_a)
                        self.base.game_instance["renderpipeline_np"].add_light(light_a)

                        # Put first light under hearth
                        light_u = RP_PointLight()
                        light_u.pos = Vec3(node_path.get_x(), node_path.get_y(), 0.3)
                        light_u.set_color_from_temperature(1000.0)
                        light_u.energy = self.flame_light_u_energy
                        light_u.ies_profile = self.base.game_instance["renderpipeline_np"].load_ies_profile("pear.ies")
                        light_u.casts_shadows = True
                        light_u.shadow_map_resolution = 512
                        light_u.near_plane = 0.2
                        light_u.radius = 3.0
                        # light_u.inner_radius = 0.2
                        self.base.game_instance['rp_lights']["flame"].append(light_u)
                        self.base.game_instance["renderpipeline_np"].add_light(light_u)

                        taskMgr.add(self.do_flame_light_flicker_task,
                                    "do_flame_light_flicker_task",
                                    extraArgs=[light_a, light_u],
                                    appendTask=True)

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

                    if self.base.game_instance["renderpipeline_np"] and adv_render:
                        self.base.game_instance["renderpipeline_np"].set_effect(node_path,
                                                                                "{0}/Engine/Renderer/effects/flame.yaml".format(
                                                                                    self.game_dir),
                                                                                {"render_gbuffer": False,
                                                                                 "render_forward": True,
                                                                                 "render_shadow": False,
                                                                                 "alpha_testing": True,
                                                                                 "normal_mapping": False})

    def clear_flame(self):
        if self.particles:
            self.particles = {}
        self.base.disable_particles()

        if self.base.game_instance["renderpipeline_np"]:
            if (self.base.game_instance['rp_lights']
                    and self.base.game_instance["renderpipeline_np"].light_mgr.num_lights > 0):
                for i in range(self.base.game_instance["renderpipeline_np"].light_mgr.num_lights):
                    for light in self.base.game_instance['rp_lights']['flame']:
                        if light:
                            self.base.game_instance["renderpipeline_np"].remove_light(light)
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

                    if self.base.game_instance["renderpipeline_np"] and adv_render:
                        self.base.game_instance["renderpipeline_np"].set_effect(node_path,
                                                                                "{0}/Engine/Renderer/effects/flame.yaml".format(
                                                                                    self.game_dir),
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

                    if self.base.game_instance["renderpipeline_np"] and adv_render:
                        self.base.game_instance["renderpipeline_np"].set_effect(node_path,
                                                                                "{0}/Engine/Renderer/effects/smoke.yaml".format(
                                                                                    self.game_dir),
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
        if (self.base.game_instance["renderpipeline_np"]
                and render
                and name
                and isinstance(name, str)
                and isinstance(pos, list)
                and isinstance(hpr, list)
                and isinstance(color, list)
                and isinstance(task, str)):
            self.render = render
            if task == 'attach':
                if name == "slight":
                    # RP doesn't have nodegraph-like structure to find and remove lights,
                    # so we check self.rp_light before adding light
                    light = RP_SpotLight()
                    light.pos = (pos[0], pos[1], pos[2])
                    light.color = (color[0], color[0], color[0])
                    light.set_color_from_temperature(3000.0)
                    light.energy = 100
                    light.ies_profile = self.base.game_instance["renderpipeline_np"].load_ies_profile("x_arrow.ies")
                    light.casts_shadows = True
                    light.shadow_map_resolution = 128
                    light.near_plane = 0.2
                    light.radius = 0.5
                    light.fov = 10
                    light.direction = (hpr[0], hpr[1], hpr[2])
                    self.base.game_instance['rp_lights']["scene"].append(light)
                    self.base.game_instance["renderpipeline_np"].add_light(light)
                elif name == "plight":
                    # RP doesn't have nodegraph-like structure to find and remove lights,
                    # so we check self.rp_light before adding light
                    light = RP_PointLight()
                    light.pos = (pos[0], pos[1], pos[2])
                    light.color = (color[0], color[0], color[0])
                    light.set_color_from_temperature(3000.0)
                    light.energy = 100.0
                    light.ies_profile = self.base.game_instance["renderpipeline_np"].load_ies_profile("x_arrow.ies")
                    light.casts_shadows = True
                    light.shadow_map_resolution = 128
                    light.near_plane = 0.2
                    light.radius = 10.0
                    # light.inner_radius = 0.2
                    self.base.game_instance['rp_lights']["scene"].append(light)
                    self.base.game_instance["renderpipeline_np"].add_light(light)

    def clear_lighting(self):
        if (self.base.game_instance["renderpipeline_np"]
                and self.base.game_instance['rp_lights']
                and self.base.game_instance["renderpipeline_np"].light_mgr.num_lights > 0):
            for i in range(self.base.game_instance["renderpipeline_np"].light_mgr.num_lights):
                for light in self.base.game_instance['rp_lights']['scene']:
                    if light:
                        self.base.game_instance["renderpipeline_np"].remove_light(light)
                        self.base.game_instance['rp_lights']['scene'].remove(light)

    def set_inv_lighting(self, name, render, pos, hpr, color, task):
        if (self.base.game_instance["renderpipeline_np"]
                and render
                and name
                and isinstance(name, str)
                and isinstance(pos, list)
                and isinstance(hpr, list)
                and isinstance(color, list)
                and isinstance(task, str)):
            self.render = render
            if task == 'attach':
                if name == "slight":
                    # RP doesn't have nodegraph-like structure to find and remove lights,
                    # so we check self.rp_light before adding light
                    if not self.base.game_instance['rp_lights'].get("inventory"):
                        light = RP_SpotLight()
                    else:
                        light = self.base.game_instance['rp_lights']["inventory"]
                    light.pos = (pos[0], pos[1], pos[2])

                    player = render.find("**/Player:BS")
                    if player:
                        light.look_at(player.get_pos())

                    light.color = (color[0], color[0], color[0])
                    light.set_color_from_temperature(5000.0)
                    light.energy = 180
                    light.ies_profile = self.base.game_instance["renderpipeline_np"].load_ies_profile("pear.ies")
                    light.casts_shadows = True
                    light.shadow_map_resolution = 512
                    light.direction = (hpr[0], hpr[1], hpr[2])
                    self.base.game_instance['rp_lights']["inventory"] = light
                    self.base.game_instance["renderpipeline_np"].add_light(light)
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
                    light.energy = 180.0
                    light.ies_profile = self.base.game_instance["renderpipeline_np"].load_ies_profile("x_arrow.ies")
                    light.casts_shadows = True
                    light.shadow_map_resolution = 128
                    light.near_plane = 0.2
                    light.radius = 10.0
                    light.inner_radius = 0.2
                    self.base.game_instance['rp_lights']["inventory"] = light
                    self.base.game_instance["renderpipeline_np"].add_light(light)

    def clear_inv_lighting(self):
        if (self.base.game_instance["renderpipeline_np"] and self.base.game_instance['rp_lights']
                and self.base.game_instance["renderpipeline_np"].light_mgr.num_lights > 0):
            if self.base.game_instance['rp_lights']['inventory']:
                light = self.base.game_instance['rp_lights']['inventory']
                self.base.game_instance["renderpipeline_np"].remove_light(light)
                self.base.game_instance['rp_lights'].pop("inventory")

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
        if actor and isinstance(bool_, bool) and self.base.game_instance["renderpipeline_np"]:
            self.base.game_instance['hw_skinning'] = False
            self.base.game_instance["renderpipeline_np"].set_effect(actor,
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
            self.base.game_instance["renderpipeline_np"].set_effect(scene,
                                            "{0}/Engine/Renderer/effects/default.yaml".format(self.game_dir),
                                            {"render_gbuffer": True,
                                             "render_forward": False,
                                             "render_shadow": False,
                                             "alpha_testing": True,
                                             "normal_mapping": True})
            """
