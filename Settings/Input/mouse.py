from panda3d.core import WindowProperties, LVector3, CompassEffect
from direct.showbase import DirectObject
from panda3d.core import NodePath, PandaNode


class Mouse:
    def __init__(self):
        self.game_settings = base.game_settings
        self.base = base
        self.d_object = DirectObject.DirectObject()
        self.floater = None
        self.pivot = None
        self.cam_area = None
        self.pos_z = 0.6
        # Set the current viewing target
        self.focus = LVector3(0, 0, 0)
        self.heading = 180
        self.pitch = 0
        self.rotation = 0
        self.mouse_sens = 0.2
        self.last = 0
        self.cam_y_back_pos = -4.6
        self.keymap = {
            'wheel_up': False,
            'wheel_down': False
        }
        self.base.game_instance['mouse_control_is_activated'] = 0

    def set_key(self, key, value):
        """ Function    : set_key

            Description : Set the state of the actions keys

            Input       : String, Boolean

            Output      : None

            Return      : None
        """
        if (key and isinstance(key, str)
                and isinstance(value, bool)):
            self.keymap[key] = value

    def mouse_wheel_init(self):
        self.base.accept("wheel_up", self.set_key, ['wheel_up', True])
        self.base.accept("wheel_down", self.set_key, ['wheel_down', True])

    def set_floater(self, player):
        """ Function    : set_floater

            Description : Create a floater object, which floats 2 units above the player.
                          We use this as a target for the camera pivot to look at.

            Input       :s Nodepath

            Output      : None

            Return      : Nodepath
        """
        if player and "Player" in player.get_name():
            # Make floater on top of the player to put camera pivot on it
            self.floater = NodePath("floater")
            self.floater.reparent_to(render)
            self.floater.set_pos(0, 0, 0)
            # camera area node for further distance checks
            self.cam_area = NodePath("area")
            self.cam_area.reparent_to(self.floater)
            self.cam_area.set_z(0)
            # camera pivot
            self.pivot = NodePath('pivot')
            self.pivot.reparent_to(self.floater)
            self.pivot.set_z(0.5)

            self.attach_floater(player)

            return self.floater

    def attach_floater(self, player):
        if player and self.floater and self.pivot:
            player.reparent_to(self.floater)
            # restore previous player's Z position
            player.set_z(-1.5)
            player.set_y(0)
            # player.get_child(0).set_pos(0, 0, -1)
            # camera setup
            base.camera.reparent_to(self.pivot)
            base.camera.set_pos(0, self.cam_y_back_pos, 0)

    def mouse_control(self):
        """ Function    : mouse_control

            Description : Mouse-rotation business for 3rd person view.

            Input       : None

            Output      : None

            Return      : None
        """
        if self.base.game_instance['mouse_control_is_activated'] == 0:
            self.base.game_instance['mouse_control_is_activated'] = 1

        if self.game_settings['Debug']['set_editor_mode'] == 'NO':
            # TPS Logic
            if self.pivot:
                mouse_direction = base.win.getPointer(0)
                x = mouse_direction.get_x()
                y = mouse_direction.get_y()
                heading = 0
                pitch = 0
                # Recentering the cursor and do mouse look
                if base.win.move_pointer(0, int(base.win.getXSize() / 2), int(base.win.getYSize() / 2)):
                    if not self.base.game_instance['is_aiming']:
                        # reset heading and pitch for floater
                        self.floater.set_h(0)
                        self.floater.set_p(0)
                        # apply heading and pitch
                        heading = self.pivot.get_h() - (x - int(base.win.getXSize() / 2)) * self.mouse_sens
                        pitch = self.pivot.get_p() - (y - int(base.win.getYSize() / 2)) * self.mouse_sens
                        self.pivot.set_h(heading)

                        if not pitch > 10.0 and not pitch < -50.0:
                            self.pivot.set_p(pitch)

                    elif self.base.game_instance['is_aiming']:
                        # world heading in aiming
                        heading = self.floater.get_h() - (x - int(base.win.getXSize() / 2)) * self.mouse_sens
                        # pitch = self.floater.get_p() - (y - int(base.win.getYSize() / 2)) * self.mouse_sens
                        self.floater.set_h(heading)

                        if self.base.game_instance['player_ref'].get_python_tag("is_on_horse"):
                            self.pivot.set_h(-160)
                        else:
                            self.pivot.set_h(100)

    def mouse_control_task(self, task):
        """ Function    : mouse_control_task

            Description : Mouse-looking camera for 3rd person view.

            Input       : Task

            Output      : None

            Return      : Task event
        """
        # Figure out how much the mouse has moved (in pixels)
        # print(self.base.game_instance['ui_mode'], self.base.game_instance['menu_mode'])
        if (not self.base.game_instance['ui_mode']
                and not self.base.game_instance['menu_mode']):
            self.mouse_control()

        return task.cont

    def set_mouse_mode(self, mode):
        """ Function    : set_mouse_mode

            Description : Set mouse mode.

            Input       : Object

            Output      : None

            Return      : None
        """
        if isinstance(mode, str):
            wp = WindowProperties()
            if mode == "absolute":
                wp.set_mouse_mode(WindowProperties.M_absolute)
            if mode == "relative":
                wp.set_mouse_mode(WindowProperties.M_relative)
            self.base.game_instance['mouse_mode'] = mode
            wp.set_cursor_hidden(True)
            self.base.win.request_properties(wp)
