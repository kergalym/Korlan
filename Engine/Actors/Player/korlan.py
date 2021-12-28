from Engine.Actors.Player.actions import Actions
from Engine.Actors.Player.state import PlayerState
from direct.actor.Actor import Actor
from panda3d.core import WindowProperties
from panda3d.core import LPoint3f
from direct.task.TaskManagerGlobal import taskMgr

from Engine.Render.render import RenderAttr
from Settings.Input.keyboard import Keyboard
from Settings.Input.mouse import Mouse


class Korlan:

    def __init__(self):
        self.scale_x = None
        self.scale_y = None
        self.scale_z = None
        self.pos_x = None
        self.pos_y = None
        self.pos_z = None
        self.rot_h = None
        self.rot_p = None
        self.rot_r = None
        self.korlan = None
        self.korlan_bs = None
        self.korlan_start_pos = None
        self.korlan_life_perc = None
        self.base = base
        self.render = render
        self.render_attr = RenderAttr()
        self.anims = None

        self.game_settings = base.game_settings
        self.game_dir = base.game_dir
        self.game_cfg = base.game_cfg
        self.game_cfg_dir = base.game_cfg_dir
        self.game_settings_filename = base.game_settings_filename
        self.cfg_path = self.game_cfg

        self.taskMgr = taskMgr
        self.kbd = Keyboard()
        self.mouse = Mouse()
        self.actions = Actions()
        self.state = PlayerState()
        self.base.actor_is_dead = False
        self.base.actor_is_alive = False
        self.base.actor_play_rate = 1.0

    async def set_actor(self, mode, name, path, animation, axis, rotation, scale, culling):
        if mode == 'menu':
            # Disable the camera trackball controls.
            self.base.disable_mouse()
            props = WindowProperties()
            props.set_cursor_hidden(False)
            self.base.win.request_properties(props)

            if (isinstance(path, str)
                    and isinstance(name, str)
                    and isinstance(axis, list)
                    and isinstance(rotation, list)
                    and isinstance(scale, list)
                    and isinstance(mode, str)
                    and animation
                    and isinstance(animation, list)
                    and isinstance(culling, bool)):

                self.pos_x = axis[0]
                self.pos_y = axis[1]
                self.pos_z = axis[2]
                self.rot_h = rotation[0]
                self.rot_p = rotation[1]
                self.rot_r = rotation[2]
                self.scale_x = scale[0]
                self.scale_y = scale[1]
                self.scale_z = scale[2]
                anim_name = animation[0]
                anim_path = animation[1]

                self.korlan = self.base.loader.load_model(path, blocking=False)
                self.korlan = Actor(self.korlan, {anim_name: anim_path})

                self.korlan.set_name(name)
                self.korlan.set_scale(self.korlan, self.scale_x, self.scale_y, self.scale_z)
                self.korlan.set_pos(self.pos_x, self.pos_y, self.pos_z)
                self.korlan.set_h(self.korlan, self.rot_h)
                self.korlan.set_p(self.korlan, self.rot_p)
                self.korlan.set_r(self.korlan, self.rot_r)

                # Hardware skinning
                if self.game_settings['Main']['postprocessing'] == 'on':
                    self.render_attr.set_hardware_skinning(self.korlan, True)

                self.korlan.loop(animation)
                self.korlan.set_play_rate(self.base.actor_play_rate, animation)

                # Set two sided, since some model may be broken
                self.korlan.set_two_sided(culling)

                # Panda3D 1.10 doesn't enable alpha blending for textures by default
                self.korlan.set_transparency(True)

                self.korlan.reparent_to(self.base.lod_np)
                self.base.lod.addSwitch(50.0, 0.0)

                # Set lights and Shadows
                if self.game_settings['Main']['postprocessing'] == 'off':
                    # TODO: uncomment if character has normals
                    # self.render_attr.set_shadows(self.scene, self.render)
                    # self.render_attr.set_ssao(self.scene)
                    pass

                if self.game_settings['Debug']['set_debug_mode'] == "YES":
                    self.render.analyze()

        if mode == 'game':
            self.base.game_mode = True
            # Disable the camera trackball controls.

            if self.game_settings['Debug']['set_editor_mode'] == 'NO':
                self.base.disable_mouse()
                self.mouse.set_mouse_mode(mode="absolute")

            if (isinstance(path, str)
                    and isinstance(name, str)
                    and isinstance(axis, list)
                    and isinstance(rotation, list)
                    and isinstance(scale, list)
                    and isinstance(mode, str)
                    and isinstance(animation, list)
                    and isinstance(culling, bool)):

                self.pos_x = axis[0]
                self.pos_y = axis[1]
                self.pos_z = axis[2]
                self.rot_h = rotation[0]
                self.rot_p = rotation[1]
                self.rot_r = rotation[2]
                self.scale_x = scale[0]
                self.scale_y = scale[1]
                self.scale_z = scale[2]

                base.player_is_loaded = 0

                assets = self.base.assets_collector()

                actor_parts_dict = {}

                """actor_parts_dict = {
                    "modelRoot": assets["Korlan_body"],
                    "helmet": assets["Korlan_helmet"],
                    "armor": assets["Korlan_armor"],
                    "pants": assets["Korlan_pants"],
                    "boots": assets["Korlan_boots"]
                }"""

                anims_full_dict = {
                    "modelRoot": animation[1],
                    "helmet": animation[1],
                    "armor": animation[1],
                    "pants": animation[1],
                    "boots": animation[1]
                }

                # load player parts separately
                body = await self.base.loader.load_model(assets["Korlan_body"], blocking=False)
                helmet = await self.base.loader.load_model(assets["Korlan_helmet"], blocking=False)
                armor = await self.base.loader.load_model(assets["Korlan_armor"], blocking=False)
                pants = await self.base.loader.load_model(assets["Korlan_pants"], blocking=False)
                boots = await self.base.loader.load_model(assets["Korlan_boots"], blocking=False)

                actor_parts_dict['modelRoot'] = body
                actor_parts_dict['helmet'] = helmet
                actor_parts_dict['armor'] = armor
                actor_parts_dict['pants'] = pants
                actor_parts_dict['boots'] = boots

                # and compose them into one
                self.korlan = Actor(actor_parts_dict, anims_full_dict)

                # toggle texture compression for textures to compress them
                # before load into VRAM
                self.base.toggle_texture_compression(self.korlan)

                self.korlan.reparent_to(render)

                self.korlan.set_name(name)
                self.korlan.set_scale(self.korlan, self.scale_x, self.scale_y, self.scale_z)
                self.korlan_start_pos = LPoint3f(self.pos_x, self.pos_y, 0.0)
                self.korlan.set_pos(self.korlan_start_pos + (0, 0, self.pos_z))
                self.korlan.set_h(self.korlan, self.rot_h)
                self.korlan.set_p(self.korlan, self.rot_p)
                self.korlan.set_r(self.korlan, self.rot_r)

                # Get actor joints
                base.korlan_joints = self.korlan.get_joints()

                # Set two sided, since some model may be broken
                self.korlan.set_two_sided(culling)

                # Panda3D 1.10 doesn't enable alpha blending for textures by default
                self.korlan.set_transparency(True)

                # Hardware skinning
                self.render_attr.set_hardware_skinning(self.korlan, True)

                # self.base.set_textures_srgb(True)

                if self.game_settings['Main']['postprocessing'] == 'on':

                    self.render_attr.render_pipeline.prepare_scene(self.korlan)

                if self.game_settings['Main']['postprocessing'] == 'off':
                    # TODO: uncomment if character has normals
                    # Set Lights and Shadows
                    """if render.find("slight"):
                        light = render.find("slight")
                        self.render_attr.set_spotlight_shadows(obj=self.korlan, light=light, shadow_blur=0.2,
                                                               ambient_color=(1.0, 1.0, 1.0))"""
                    # self.render_attr.set_normal_mapping(self.korlan)

                    # self.render_attr.set_ssao(self.scene)
                    pass

                if self.game_settings['Debug']['set_debug_mode'] == "YES":
                    # Make actor global
                    base.player = self.korlan
                    self.render.analyze()

                self.actions.player_actions_init(self.korlan, animation[0])

                self.korlan_life_perc = 100

                taskMgr.add(self.state.actor_life,
                            "actor_life",
                            appendTask=True)

                base.player_is_loaded = 1


