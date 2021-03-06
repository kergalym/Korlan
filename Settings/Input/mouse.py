from panda3d.core import WindowProperties, LVector3, CompassEffect
from direct.showbase import DirectObject
from panda3d.core import NodePath, PandaNode


class Mouse:
    def __init__(self):
        self.game_settings = base.game_settings
        self.base = base
        self.d_object = DirectObject.DirectObject()
        self.player = None
        self.floater = None
        self.pos_z = 0.6
        # Set the current viewing target
        self.focus = LVector3(0, 0, 0)
        self.heading = 180
        self.pitch = 0
        self.rotation = 0
        self.mouse_sens = 0.2
        self.last = 0
        self.keymap = {
            'wheel_up': False,
            'wheel_down': False
        }
        self.base.mouse_control_is_activated = 0

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
                          We use this as a target for the camera to look at.

            Input       : Nodepath

            Output      : None

            Return      : Nodepath
        """
        # Remove floater node before assigning a node
        # to prevent object duplicating
        # and further in-game performance degradation
        if player:
            flt_name = 'player_floater'
            if player.find("**/{0}".format(flt_name)).is_empty():
                self.player = player
                self.floater = NodePath(PandaNode(flt_name))
                self.floater.reparent_to(self.player)
            elif not player.find("**/{0}".format(flt_name)).is_empty():
                player.find("**/{0}".format(flt_name)).remove_node()
                self.player = player
                self.floater = NodePath(PandaNode(flt_name))
                self.floater.reparent_to(self.player)

            self.floater.set_z(self.pos_z)
            return self.floater

    def mouse_control_setup(self, player):
        if player:
            # If the camera is too far from player, move it closer.
            # If the camera is too close to player, move it farther.
            camvec = player.get_pos() - self.base.camera.get_pos()
            camvec.set_z(0)
            camdist = camvec.length()
            camvec.normalize()
            if camdist > 7.0:
                self.base.camera.set_pos(self.base.camera.get_pos() + camvec * (camdist - 7))
                camdist = 7.0
            if camdist < 0:
                self.base.camera.set_pos(self.base.camera.get_pos() - camvec * (7 - camdist))

            if self.base.camera.get_z() < player.get_z() + 1.0:
                self.base.camera.set_z(player.get_z() + 1.0)
            elif self.base.camera.get_z() > player.get_z() + 7.0:
                self.base.camera.set_z(player.get_z() + 7.0)

    def mouse_control(self):
        """ Function    : mouse_control

            Description : Mouse-rotation business for 3rd person view.

            Input       : None

            Output      : None

            Return      : None
        """
        if self.base.mouse_control_is_activated == 0:
            self.base.mouse_control_is_activated = 1

        if self.game_settings['Debug']['set_editor_mode'] == 'NO':
            mouse_direction = self.base.win.getPointer(0)
            x = mouse_direction.get_x()
            y = mouse_direction.get_y()

            # Recentering the cursor and do mouse look
            if self.base.win.move_pointer(0, int(base.win.getXSize() / 2), int(base.win.getYSize() / 2)):
                self.heading = self.heading - (x - int(base.win.getXSize() / 2)) * self.mouse_sens
                # self.pitch = self.pitch - (y - int(base.win.getYSize() / 2)) * self.mouse_sens

            self.base.camera.set_h(self.heading)
            self.base.camera.set_p(self.pitch)
            self.base.camera.set_r(self.rotation)

            direction = self.base.camera.get_mat().getRow3(1)
            self.base.camera.set_pos(self.focus - (direction * 180))
            self.focus = self.base.camera.get_pos() + (direction * 180)

    def mouse_control_task(self, task):
        """ Function    : mouse_control_task

            Description : Mouse-looking camera for 3rd person view.

            Input       : Task

            Output      : None

            Return      : Task event
        """
        # Figure out how much the mouse has moved (in pixels)
        if (hasattr(base, "is_ui_active") is False
                and self.base.game_mode):
            self.mouse_control()

        elif (hasattr(base, "is_ui_active")
                and base.is_ui_active is False
                and self.base.game_mode):
            self.mouse_control()

        if base.game_mode is False and base.menu_mode:
            return task.done

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
            self.base.mouse_mode = mode
            wp.set_cursor_hidden(True)
            self.base.win.request_properties(wp)
