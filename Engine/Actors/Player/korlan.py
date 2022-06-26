from Engine.Actors.Player.player_controller import PlayerController
from Engine.Actors.Player.state import PlayerState
from direct.actor.Actor import Actor
from panda3d.core import WindowProperties, Vec3
from panda3d.core import LPoint3f
from direct.task.TaskManagerGlobal import taskMgr

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
        self.controller = PlayerController()
        self.state = PlayerState()
        self.base.actor_is_dead = False
        self.base.actor_is_alive = False
        self.base.actor_play_rate = 1.0

    def save_player_parts(self, parts):
        if self.korlan and isinstance(self.base.game_instance["player_parts"], list):
            for name in parts:
                self.base.game_instance["player_parts"].append(name)

    async def set_actor(self, mode, name, animation, axis, rotation, scale, culling):
        if mode == 'menu':
            # Disable the camera trackball controls.
            self.base.disable_mouse()
            props = WindowProperties()
            props.set_cursor_hidden(False)
            self.base.win.request_properties(props)

            if (isinstance(name, str)
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

                self.base.game_instance['player_is_loaded'] = False

                # Korlan_empty is the first asset containing only skeleton (armature).
                # Next ones are Korlan_body, Korlan_armor, Korlan_pants and Korlan_boots,
                # all of them contain armature with weighted meshes.
                # Each of them follows the previous one and assembles in this order.
                # This allows to avoid unwanted shifting of the meshes while playing the animation.
                assets = self.base.assets_collector()

                part_names = ["modelRoot", "body", "helmet", "armor", "pants", "boots"]
                asset_names = ["Korlan_empty", "Korlan_body", "Korlan_helmet",
                               "Korlan_armor", "Korlan_pants", "Korlan_boots"]

                actor_parts_dict = {}

                anims_full_dict = {
                    part_names[0]: animation[1],
                    part_names[1]: animation[1],
                    part_names[2]: animation[1],
                    part_names[3]: animation[1],
                    part_names[4]: animation[1],
                    part_names[5]: animation[1]
                }

                # load player parts separately
                empty = await self.base.loader.load_model(assets[asset_names[0]], blocking=False)
                body = await self.base.loader.load_model(assets[asset_names[1]], blocking=False)
                helmet = await self.base.loader.load_model(assets[asset_names[2]], blocking=False)
                armor = await self.base.loader.load_model(assets[asset_names[3]], blocking=False)
                pants = await self.base.loader.load_model(assets[asset_names[4]], blocking=False)
                boots = await self.base.loader.load_model(assets[asset_names[5]], blocking=False)

                actor_parts_dict[part_names[0]] = empty
                actor_parts_dict[part_names[1]] = body
                actor_parts_dict[part_names[2]] = helmet
                actor_parts_dict[part_names[3]] = armor
                actor_parts_dict[part_names[4]] = pants
                actor_parts_dict[part_names[5]] = boots

                # and compose them into one
                self.korlan = Actor(actor_parts_dict, anims_full_dict)

                # toggle texture compression for textures to compress them
                # before load into VRAM
                self.base.toggle_texture_compression(self.korlan)

                self.korlan.reparent_to(render)

                self.base.game_instance['player_is_loaded'] = True

                self.korlan.set_name(name)
                self.korlan.set_scale(self.korlan, self.scale_x, self.scale_y, self.scale_z)
                self.korlan_start_pos = LPoint3f(self.pos_x, self.pos_y, 0.0)
                self.korlan.set_pos(self.korlan_start_pos + (0, 0, self.pos_z))
                self.korlan.set_h(self.korlan, self.rot_h)
                self.korlan.set_p(self.korlan, self.rot_p)
                self.korlan.set_r(self.korlan, self.rot_r)

                # Save actor parts
                self.save_player_parts(part_names)
                # base.korlan_joints = self.korlan.get_joints()

                # Set two sided, since some model may be broken
                self.korlan.set_two_sided(culling)

                # Panda3D 1.10 doesn't enable alpha blending for textures by default
                self.korlan.set_transparency(True)

                # Hardware skinning
                base.game_instance['render_attr_cls'].set_hardware_skinning(self.korlan, True)

                # Make actor global
                self.base.game_instance['player_ref'] = self.korlan

                if self.game_settings['Main']['postprocessing'] == 'on':
                    base.game_instance['render_attr_cls'].render_pipeline.prepare_scene(self.korlan)

                if self.game_settings['Debug']['set_debug_mode'] == "YES":
                    self.render.analyze()

        if mode == 'game':
            # Disable the camera trackball controls.

            if self.game_settings['Debug']['set_editor_mode'] == 'NO':
                self.base.disable_mouse()
                self.mouse.set_mouse_mode(mode="absolute")

            if (isinstance(name, str)
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

                self.base.game_instance['player_is_loaded'] = False

                # Korlan_empty is the first asset containing only skeleton (armature).
                # Next ones are Korlan_body, Korlan_armor, Korlan_pants and Korlan_boots,
                # all of them contain armature with weighted meshes.
                # Each of them follows the previous one and assembles in this order.
                # This allows to avoid unwanted shifting of the meshes while playing the animation.
                assets = self.base.assets_collector()

                part_names = ["modelRoot", "body", "helmet", "armor", "pants", "boots"]
                asset_names = ["Korlan_empty", "Korlan_body", "Korlan_helmet",
                               "Korlan_armor", "Korlan_pants", "Korlan_boots"]

                actor_parts_dict = {}

                anims_full_dict = {
                    part_names[0]: animation[1],
                    part_names[1]: animation[1],
                    part_names[2]: animation[1],
                    part_names[3]: animation[1],
                    part_names[4]: animation[1],
                    part_names[5]: animation[1]
                }

                # load player parts separately
                empty = await self.base.loader.load_model(assets[asset_names[0]], blocking=False)
                body = await self.base.loader.load_model(assets[asset_names[1]], blocking=False)
                helmet = await self.base.loader.load_model(assets[asset_names[2]], blocking=False)
                armor = await self.base.loader.load_model(assets[asset_names[3]], blocking=False)
                pants = await self.base.loader.load_model(assets[asset_names[4]], blocking=False)
                boots = await self.base.loader.load_model(assets[asset_names[5]], blocking=False)

                actor_parts_dict[part_names[0]] = empty
                actor_parts_dict[part_names[1]] = body
                actor_parts_dict[part_names[2]] = helmet
                actor_parts_dict[part_names[3]] = armor
                actor_parts_dict[part_names[4]] = pants
                actor_parts_dict[part_names[5]] = boots

                # and compose them into one
                self.korlan = Actor(actor_parts_dict, anims_full_dict)

                # toggle texture compression for textures to compress them
                # before load into VRAM
                self.base.toggle_texture_compression(self.korlan)

                self.korlan.reparent_to(render)

                self.base.game_instance['player_is_loaded'] = True

                self.korlan.set_name(name)
                self.korlan.set_scale(self.korlan, self.scale_x, self.scale_y, self.scale_z)
                self.korlan_start_pos = LPoint3f(self.pos_x, self.pos_y, 0.0)
                self.korlan.set_pos(self.korlan_start_pos + (0, 0, self.pos_z))
                self.korlan.set_h(self.korlan, self.rot_h)
                self.korlan.set_p(self.korlan, self.rot_p)
                self.korlan.set_r(self.korlan, self.rot_r)

                # Save actor parts
                self.save_player_parts(part_names)

                # Enable blending to fix cloth poking
                self.korlan.set_blend(frameBlend=True)

                # Set sRGB
                self.base.set_textures_srgb(self.korlan, True)

                # Set two sided, since some model may be broken
                self.korlan.set_two_sided(culling)

                # Panda3D 1.10 doesn't enable alpha blending for textures by default
                self.korlan.set_transparency(True)

                # Hardware skinning
                base.game_instance['render_attr_cls'].set_hardware_skinning(self.korlan, True)

                # Make actor global
                self.base.game_instance['player_ref'] = self.korlan

                if self.game_settings['Main']['postprocessing'] == 'on':
                    base.game_instance['render_attr_cls'].render_pipeline.prepare_scene(self.korlan)

                # Set allowed weapons list
                self.base.game_instance["weapons"] = [
                    "sword",
                    "bow_kazakh",
                ]

                # Usable Items List
                _items = ["big_plate",
                          "piala",
                          "dombra",
                          "torsyk"]

                _pos = [Vec3(0.4, 8.0, 5.2),
                        Vec3(0.4, 8.0, 5.2),
                        Vec3(0.4, 8.0, 5.2),
                        Vec3(0.4, 8.0, 5.2)]

                _hpr = [Vec3(0, 0, 0),
                        Vec3(0, 0, 0),
                        Vec3(0, 0, 0),
                        Vec3(0, 0, 0)]

                usable_item_list = {
                    "name": _items,
                    "pos": _pos,
                    "hpr": _hpr
                }

                self.korlan.set_python_tag("usable_item_list", usable_item_list)

                # Set Used Item Record
                self.korlan.set_python_tag("used_item_np", None)
                self.korlan.set_python_tag("is_item_ready", False)
                self.korlan.set_python_tag("is_item_using", False)
                self.korlan.set_python_tag("current_item_prop", None)

                # Set Player Parameters
                self.state.set_state(actor=self.korlan)

                # Initialize Player Controller
                self.controller.player_actions_init(self.korlan, animation[0])






