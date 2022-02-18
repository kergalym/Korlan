from pathlib import Path
from direct.gui.DirectGui import OnscreenText
from direct.task.TaskManagerGlobal import taskMgr
from panda3d.core import *
from panda3d.core import FontPool, TextNode
from Engine.Renderer.rpcore import PointLight as RP_PointLight
from Engine.Renderer.rpcore import SpotLight as RP_SpotLight
from direct.particles.ParticleEffect import ParticleEffect
from Engine.Renderer.rpcore.water.projected_water import ProjectedWater


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
        if self.base.game_instance['rp_lights'] and self.render_pipeline.light_mgr.num_lights > 0:
            if self.base.game_instance['rp_lights']['inventory']:
                light = self.base.game_instance['rp_lights']['inventory']
                self.render_pipeline.remove_light(light)
                self.base.game_instance['rp_lights'].pop("inventory")

    def get_light_attributes(self):
        pass

    def set_light_attributes(self):
        pass

    def transform_scene_lights(self):
        pass

    def set_time_of_day_clock_task(self, time, duration, task):
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

            if bool_:
                self.render_pipeline.set_effect(actor,
                                                "{0}/Engine/Renderer/effects/hardware_skinning.yaml".format(
                                                    self.game_dir),
                                                options={}, sort=25)
                attrib = actor.get_attrib(ShaderAttrib)
                attrib = attrib.set_flag(ShaderAttrib.F_hardware_skinning, bool_)
                actor.set_attrib(attrib)
                self.base.game_instance['hw_skinning'] = True

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
            self.grass_np.reparentTo(self.grass_np.get_parent())
            self.grass_np.setInstanceCount(256)
            self.grass_np.node().setBounds(BoundingBox((0, 0, 0), (256, 256, 128)))
            self.grass_np.node().setFinal(1)

            self.render_pipeline.set_effect(self.grass_np,
                                            "{0}/Engine/Renderer/effects/grass.yaml".format(self.game_dir),
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

    def set_flame(self, adv_render):
        if not render.find("**/flame").is_empty():
            self.flame_np = render.find("**/flame")

            # Set the flame effect
            if adv_render:
                self.render_pipeline.set_effect(self.flame_np,
                                                "{0}/Engine/Renderer/effects/flame2.yaml".format(self.game_dir), {})

            taskMgr.add(self.flame_proc_shader_task,
                        "flame_proc_shader_task",
                        appendTask=True)

    def flame_proc_shader_task(self, task):
        if self.flame_np:
            time = task.time
            self.flame_np.set_shader_input("iTime", time)

        if self.base.game_instance['menu_mode']:
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
                                                "{0}/Engine/Renderer/effects/default.yaml".format(self.game_dir),
                                                {"render_gbuffer": True,
                                                 "render_shadow": False,
                                                 "alpha_testing": True,
                                                 "normal_mapping": True})

    def clear_flame_particles(self):
        if self.particles:
            self.particles = {}
        self.base.disable_particles()

