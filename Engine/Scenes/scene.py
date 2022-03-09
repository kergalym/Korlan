from panda3d.core import *
from Engine.Renderer.renderer import RenderAttr


class SceneOne:

    def __init__(self):
        self.path = None
        self.loader = None
        self.game_settings = None
        self.render_type = None
        self.render_pipeline = None
        self.model = None
        self.axis = None
        self.rotation = None
        self.scale_x = None
        self.scale_y = None
        self.scale_z = None
        self.type = None
        self.node_path = NodePath()
        self.render_attr = RenderAttr()
        self.base = base
        self.render = render
        self.game_settings = base.game_settings
        self.game_dir = base.game_dir
        self.game_cfg = base.game_cfg
        self.game_cfg_dir = base.game_cfg_dir
        self.game_settings_filename = base.game_settings_filename
        self.cfg_path = self.game_cfg

    def set_env(self, cloud_dimensions, cloud_speed, cloud_size, cloud_count, cloud_color):
        if self.game_settings['Main']['postprocessing'] == 'off':
            # Load the skybox
            assets = self.base.assets_collector()
            sky = self.base.loader.load_model(assets['sky'])
            sun = self.base.loader.load_model(assets['sun'])
            cloud = self.base.loader.load_model(assets['cloud'])
            sky.set_name("sky")
            sky.reparent_to(render)
            sun.set_name("sun")
            sun.reparent_to(render)
            cloud.set_name("cloud")
            cloud.reparent_to(render)
            self.render_attr.set_sky_and_clouds(cloud_dimensions, cloud_speed, cloud_size, cloud_count, cloud_color)
            # If you don't do this, none of the features
            # listed above will have any effect. Panda will
            # simply ignore normal maps, HDR, and so forth if
            # shader generation is not enabled. It would be reasonable
            # to enable shader generation for the entire game, using this call:
            # scene.set_shader_auto()
            # self.render_attr.set_shadows(scene, render)
            render.set_attrib(LightRampAttrib.make_hdr1())

    async def set_level(self, path, name, axis, rotation, scale, culling):
        if (isinstance(path, str)
                and isinstance(name, str)
                and isinstance(axis, list)
                and isinstance(rotation, list)
                and isinstance(scale, list)
                and isinstance(culling, bool)):

            self.path = "{0}{1}".format(self.game_dir, path)
            self.game_settings = self.game_settings
            self.model = name
            pos_x = axis[0]
            pos_y = axis[1]
            pos_z = axis[2]
            rot_h = rotation[0]
            self.scale_x = scale[0]
            self.scale_y = scale[1]
            self.scale_z = scale[2]

            self.base.game_instance['scene_is_loaded'] = False

            # Load the scene.
            scene = await self.base.loader.load_model(path, blocking=False)
            world = render.find("**/World")
            if world:

                # toggle texture compression for textures to compress them
                # before load into VRAM
                self.base.toggle_texture_compression(scene)

                scene.reparent_to(self.base.game_instance['lod_np'])
                self.base.game_instance['lod_np'].node().add_switch(1000.0, 0.0)
                # scene.reparent_to(world)
                # scene.flatten_strong()
                # scene.hide()
                base.accept("f2", self.scene_toggle, [scene])

                scene.set_name(name)
                scene.set_scale(self.scale_x, self.scale_y, self.scale_z)
                scene.set_pos(pos_x, pos_y, pos_z)
                scene.set_hpr(scene, rot_h, 0, 0)

                # Make scene global
                self.base.game_instance['scene_np'] = scene

            if self.game_settings['Main']['postprocessing'] == 'on':
                self.render_attr.render_pipeline.prepare_scene(scene)

            if not render.find("**/Grass").is_empty():
                grass = render.find("**/Grass")
                grass.set_two_sided(True)

            # TODO: Get Lightmap from Texture Collector
            """ts = TextureStage("lightmap")
            lightmap = base.loader.load_texture("/tmp/tex/ligtmap.png")
            ts.setTexcoordName("lightmap")

            scene.set_texture(ts, lightmap)"""

            # Set two sided, since some model may be broken
            scene.set_two_sided(culling)

            # Panda3D 1.10 doesn't enable alpha blending for textures by default
            scene.set_transparency(True)

            # render.set_attrib(LightRampAttrib.make_hdr1())

            if self.game_settings['Main']['postprocessing'] == 'off':
                # Set Lights and Shadows
                if render.find("SpotLight_ToD"):
                    light = render.find("SpotLight_ToD")
                    self.render_attr.set_spotlight_shadows(obj=scene, light=light, shadow_blur=0.2,
                                                           ambient_color=(1.0, 1.0, 1.0))

                # If you don't do this, none of the features
                # listed above will have any effect. Panda will
                # simply ignore normal maps, HDR, and so forth if
                # shader generation is not enabled. It would be reasonable
                # to enable shader generation for the entire game, using this call:
                # scene.set_shader_auto()
                # Enable water
                self.render_attr.set_water(adv_render=False, water_lvl=30.0)
                # Enable flame
                # todo: attach to empties in the loop
                self.render_attr.set_flame_hearth(adv_render=False, scene_np=scene, flame_scale=0.2)
                # self.render_attr.set_smoke_hearth(adv_render=False, scene_np=scene, smoke_scale=0.2)
                # Enable grass
                # self.render_attr.set_grass(adv_render=False, fogcenter=Vec3(256, 256, 0), uv_offset=Vec2(0, 0))
            else:
                # Enable water
                self.render_attr.set_projected_water(True)

                # Enable flame
                self.render_attr.set_flame_hearth(adv_render=True, scene_np=scene, flame_scale=0.2)
                # self.render_attr.set_smoke_hearth(adv_render=True, scene_np=scene, smoke_scale=0.2)
                # Enable grass
                # self.render_attr.set_grass(adv_render=True, fogcenter=Vec3(256, 256, 0), uv_offset=Vec2(0, 0))

                # Enable flare
                # self.render_attr.set_flare(True, adv_render=False)

            self.base.game_instance['scene_is_loaded'] = True

            # Add Bullet colliders for this scene
            self.base.messenger.send("add_bullet_collider")

            # Load collisions for a level
            colliders_dict = base.assets_collider_collector()
            coll_scene_name = '{0}_coll'.format(name)
            coll_path = colliders_dict[coll_scene_name]
            coll_scene = await self.base.loader.load_model(coll_path, blocking=False)
            coll_scene.set_name(coll_scene_name)

            coll_scene_np = NodePath("Collisions")
            coll_scene_np.reparent_to(world)

            coll_scene.reparent_to(coll_scene_np)

            coll_scene.hide()

            if self.game_settings['Debug']['set_debug_mode'] == "YES":
                scene.hide()

    def scene_toggle(self, scene):
        if scene.is_hidden():
            scene.show()
        else:
            scene.hide()
