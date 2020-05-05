from Engine.Actors.Player.actions import Actions
from Engine.Actors.Player.state import PlayerState

from Engine.Collisions.collisions import Collisions
from Engine import set_tex_transparency
from direct.actor.Actor import Actor
from panda3d.core import WindowProperties, Texture
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
        self.korlan_start_pos = None
        self.base = base
        self.render = render
        self.anims = None

        self.game_settings = base.game_settings
        self.game_dir = base.game_dir
        self.game_cfg = base.game_cfg
        self.game_cfg_dir = base.game_cfg_dir
        self.game_settings_filename = base.game_settings_filename
        self.cfg_path = {"game_config_path":
                         "{0}/{1}".format(self.game_cfg_dir, self.game_settings_filename)}

        self.taskMgr = taskMgr
        self.kbd = Keyboard()
        self.mouse = Mouse()
        self.col = Collisions()
        self.render_attr = RenderAttr()
        self.act = Actions()
        self.state = PlayerState()
        self.col = Collisions()
        self.actor_life_perc = None
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

                self.korlan = self.base.loader.load_model(path, blocking=True)
                self.korlan = Actor(self.korlan, {anim_name: anim_path})

                self.korlan.set_name(name)
                self.korlan.set_scale(self.korlan, self.scale_x, self.scale_y, self.scale_z)
                self.korlan.set_pos(self.pos_x, self.pos_y, self.pos_z)
                self.korlan.set_h(self.korlan, self.rot_h)
                self.korlan.set_p(self.korlan, self.rot_p)
                self.korlan.set_r(self.korlan, self.rot_r)
                self.korlan.loop(animation)
                self.korlan.set_play_rate(self.base.actor_play_rate, animation)

                # Set two sided, since some model may be broken
                self.korlan.set_two_sided(culling)

                # Panda3D 1.10 doesn't enable alpha blending for textures by default
                self.korlan.set_transparency(True)

                self.korlan.reparent_to(render)

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
            wp = WindowProperties()
            wp.set_cursor_hidden(True)
            self.base.win.request_properties(wp)

            # Disable the camera trackball controls.
            self.base.disable_mouse()

            # control mapping of mouse movement to character movement
            self.base.mouse_magnitude = 1

            self.base.rotate_x = 0

            self.base.last_mouse_x = None

            self.base.hide_mouse = False

            self.base.manual_recenter_mouse = True

            self.mouse.set_mouse_mode(WindowProperties.M_absolute)

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

                self.korlan = await self.base.loader.load_model(path, blocking=False)
                self.korlan = Actor(self.korlan, animation[1])

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

                self.korlan.reparent_to(render)

                # Set lights and Shadows
                if self.game_settings['Main']['postprocessing'] == 'off':
                    # TODO: uncomment if character has normals
                    # self.render_attr.set_shadows(self.scene, self.render)
                    # self.render_attr.set_ssao(self.scene)
                    pass

                if self.game_settings['Debug']['set_debug_mode'] == "YES":
                    # Make actor global
                    base.player = self.korlan
                    self.render.analyze()
                    # self.render.explore()

                taskMgr.add(self.mouse.mouse_look_cam,
                            "mouse_look",
                            appendTask=True)
                taskMgr.add(self.state.set_player_equip_state,
                            "player_state",
                            appendTask=True)

                self.act.scene_actions_init(self.korlan, animation[0])

                taskMgr.add(self.state.actor_life,
                            "actor_life",
                            appendTask=True)

                self.col.set_collision(obj=self.korlan,
                                       type="player",
                                       shape="capsule")
