import re

from Engine.Actors.Player.actions import Actions
from Engine.collisions import Collisions
from Engine import set_tex_transparency
from direct.actor.Actor import Actor
from panda3d.core import WindowProperties
from panda3d.core import LPoint3f
from direct.task.TaskManagerGlobal import taskMgr

from Engine.world import World
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
        self.world = World()
        self.act = Actions()
        self.actor_life_perc = None
        self.base.actor_is_dead = False
        self.base.actor_is_alive = False
        self.base.actor_play_rate = 1.0

    def actor_life(self, task):
        self.has_actor_life()
        return task.cont

    def has_actor_life(self):
        if (self.base.actor_is_dead is False
                and self.base.actor_is_alive is False):
            self.actor_life_perc = 100
            self.base.actor_is_alive = True
        else:
            return False

    def set_actor(self, mode, name, path, animation, axis, rotation, scale):

        if mode == 'menu':

            # Disable the camera trackball controls.
            self.base.disableMouse()
            props = WindowProperties()
            props.setCursorHidden(False)
            self.base.win.requestProperties(props)

            if (isinstance(path, str)
                    and isinstance(name, str)
                    and isinstance(axis, list)
                    and isinstance(rotation, list)
                    and isinstance(scale, list)
                    and isinstance(mode, str)
                    and animation
                    and isinstance(animation, str)):
                self.pos_x = axis[0]
                self.pos_y = axis[1]
                self.pos_z = axis[2]
                self.rot_h = rotation[0]
                self.rot_p = rotation[1]
                self.rot_r = rotation[2]
                self.scale_x = scale[0]
                self.scale_y = scale[1]
                self.scale_z = scale[2]

            self.korlan = Actor(path,
                                {animation: "{0}/Assets/Actors/Animations/{1}.egg".format(self.game_dir, animation)})

            self.korlan.setName(name)
            self.korlan.setScale(self.korlan, self.scale_x, self.scale_y, self.scale_z)
            self.korlan.setPos(self.pos_x, self.pos_y, self.pos_z)
            self.korlan.setH(self.korlan, self.rot_h)
            self.korlan.setP(self.korlan, self.rot_p)
            self.korlan.setR(self.korlan, self.rot_r)
            self.korlan.loop(animation)
            self.korlan.setPlayRate(self.base.actor_play_rate, animation)

            # Panda3D 1.10 doesn't enable alpha blending for textures by default
            set_tex_transparency(self.korlan)

            self.korlan.reparentTo(render)

            # Set lights and Shadows
            if self.game_settings['Main']['postprocessing'] == 'off':
                # TODO: uncomment if character has normals
                # self.world.set_shadows(self.korlan, self.render)
                # self.world.set_ssao(self.korlan)
                self.world.set_lighting(self.render, self.korlan)

            if self.game_settings['Debug']['set_debug_mode'] == "YES":
                self.render.analyze()
                self.render.explore()

            self.col.set_inter_collision(self.korlan)

        if mode == 'game':

            self.base.game_mode = True
            wp = WindowProperties()
            wp.setCursorHidden(True)
            self.base.win.requestProperties(wp)

            # Disable the camera trackball controls.
            self.base.disableMouse()

            # control mapping of mouse movement to character movement
            self.base.mouseMagnitude = 1

            self.base.rotateX = 0

            self.base.lastMouseX = None

            self.base.hideMouse = False

            self.base.manualRecenterMouse = True

            self.mouse.set_mouse_mode(WindowProperties.M_absolute)

            if (isinstance(path, str)
                    and isinstance(name, str)
                    and isinstance(axis, list)
                    and isinstance(rotation, list)
                    and isinstance(scale, list)
                    and isinstance(mode, str)
                    and isinstance(animation, list)):

                self.pos_x = axis[0]
                self.pos_y = axis[1]
                self.pos_z = axis[2]
                self.rot_h = rotation[0]
                self.rot_p = rotation[1]
                self.rot_r = rotation[2]
                self.scale_x = scale[0]
                self.scale_y = scale[1]
                self.scale_z = scale[2]

                # Make animations dict containing full path and pass it to Actor
                anims = {}
                anim_values = {}
                anim_path = "{0}/Assets/Actors/Animations/".format(self.game_dir)
                for a in animation:
                    anims[a] = "{0}{1}".format(anim_path, a)
                    key = re.sub('Korlan-', '', a)
                    if '.egg' and '.egg.bam' not in key:
                        key = re.sub('.egg', '', key)
                    elif '.egg.bam' in key:
                        key = re.sub('.egg.bam', '', key)
                    anim_values[key] = a

                base.anims = anims
                self.anims = base.anims

                self.korlan = Actor(path, anims)

                self.korlan.setName(name)
                self.korlan.setScale(self.korlan, self.scale_x, self.scale_y, self.scale_z)
                self.KorlanStartPos = LPoint3f(self.pos_x, self.pos_y, 0.0)
                self.korlan.setPos(self.KorlanStartPos + (0, 0, self.pos_z))
                self.korlan.setH(self.korlan, self.rot_h)
                self.korlan.setP(self.korlan, self.rot_p)
                self.korlan.setR(self.korlan, self.rot_r)

                # Panda3D 1.10 doesn't enable alpha blending for textures by default
                set_tex_transparency(self.korlan)

                self.korlan.reparentTo(render)

                # Set lights and Shadows
                if self.game_settings['Main']['postprocessing'] == 'off':
                    # TODO: uncomment if character has normals
                    # self.world.set_shadows(self.korlan, self.render)
                    # self.world.set_ssao(self.korlan)
                    self.world.set_lighting(render, self.korlan)

                if self.game_settings['Debug']['set_debug_mode'] == "YES":
                    self.render.analyze()
                    self.render.explore()

                taskMgr.add(self.mouse.mouse_look_cam,
                            "mouse-look",
                            appendTask=True)

                self.act.scene_actions_init(self.korlan, anim_values)

                taskMgr.add(self.actor_life, "actor_life")
