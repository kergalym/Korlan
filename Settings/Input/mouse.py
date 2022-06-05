from panda3d.core import WindowProperties, LVector3
from direct.showbase import DirectObject
from panda3d.core import NodePath


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
        self.base.game_instance["mouse_y_cam"] = self.cam_y_back_pos
        self.keymap = {
            'wheel_up': False,
            'wheel_down': False
        }
        self.base.game_instance['mouse_control_is_activated'] = 0
        self.actor = None
        self.actor_parts = {}

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
            # camera setup
            base.camera.reparent_to(self.pivot)
            base.camera.set_pos(0, self.cam_y_back_pos, 0)

    def rotate_player_joint(self, heading, pitch):
        if isinstance(heading, float) and isinstance(pitch, float):
            name = ''
            if not self.actor:
                # Assign once
                self.actor = self.base.game_instance['player_ref']
                name = "Korlan"

            if self.actor:
                parts = self.base.game_instance["player_parts"]
                # Assign once
                for part in parts:
                    if not self.actor_parts.get(part):
                        self.actor_parts[part] = self.actor.control_joint(None, part, "{0}:Spine".format(name))

                    # Actor joints have reversed axis,
                    # so set_h() works as for setting pitch
                    # and set_r() works as for setting heading
                    if self.actor_parts.get(part):
                        if not self.actor.get_python_tag("is_on_horse"):
                            self.actor_parts[part].set_h(pitch)
                        elif self.actor.get_python_tag("is_on_horse"):
                            dt = globalClock.getDt()
                            h = round(self.actor_parts[part].get_r(), 1)
                            p = round(self.actor_parts[part].get_p(), 1)
                            if self.base.game_instance["kbd_np"].keymap["t_up"]:
                                if not p > 10.0:
                                    self.actor_parts[part].set_p(p + 100 * dt)
                            if self.base.game_instance["kbd_np"].keymap["t_down"]:
                                if not p < -40.0:
                                    self.actor_parts[part].set_p(p - 100 * dt)
                            if self.base.game_instance["kbd_np"].keymap["t_left"]:
                                if not h > 40.0:
                                    self.actor_parts[part].set_r(h + 100 * dt)
                            if self.base.game_instance["kbd_np"].keymap["t_right"]:
                                if not h < -50.0:
                                    self.actor_parts[part].set_r(h - 100 * dt)

    def reset_rotated_player_joints(self):
        # Rotate by pitch all parts simultaneously
        for part in self.actor_parts:
            if self.actor_parts.get(part):
                if (self.actor_parts[part].get_h() != 0
                        or self.actor_parts[part].get_p() != 0
                        or self.actor_parts[part].get_r() != 0):
                    self.actor_parts[part].set_hpr(0, 0, 0)

    def on_mouse_rotate_in_aiming(self, x, y):
        """ Function    : on_mouse_rotate_in_aiming

            Description : Activates player rotation by mouse in aiming.

            Input       : Integer

            Output      : None

            Return      : None
        """
        # Do world heading in aiming
        # and rotate player's last spine bone before hips
        player_bs = self.base.get_actor_bullet_shape_node(asset="Player",
                                                          type="Player")
        if player_bs:
            heading = player_bs.get_h() - (x - int(base.win.get_x_size() / 2)) * self.mouse_sens
            pv_heading = self.pivot.get_h() - (y - int(base.win.get_x_size() / 2)) * self.mouse_sens
            pv_pitch = self.pivot.get_p() - (y - int(base.win.get_y_size() / 2)) * self.mouse_sens
            self.pivot.set_h(180)

            if self.base.game_instance['player_ref'].get_python_tag("is_on_horse"):
                # limit pitch by 60 angle
                self.rotate_player_joint(pv_heading, pv_pitch)
                self.pivot.set_p(0)
            elif not self.base.game_instance['player_ref'].get_python_tag("is_on_horse"):
                player_bs.set_h(heading)
                # limit pitch by 60 angle
                if not pv_pitch > 10.0 and not pv_pitch < -50.0:
                    self.rotate_player_joint(pv_heading, pv_pitch)
                    self.pivot.set_p(pv_pitch)

    def on_limit_camera_in_social_action(self):
        if self.base.game_instance["is_player_laying"]:
            player_bs = self.base.get_actor_bullet_shape_node(asset="Player",
                                                              type="Player")
            self.pivot.look_at(player_bs.get_pos())
            self.pivot.set_h(player_bs, 180)
            self.pivot.set_p(-35)

        elif self.base.game_instance["is_player_sitting"]:
            player_bs = self.base.get_actor_bullet_shape_node(asset="Player",
                                                              type="Player")
            self.pivot.look_at(player_bs.get_pos())
            self.pivot.set_h(player_bs, -360)
            self.pivot.set_p(-25)

    def on_mouse_look_around_player(self, x, y):
        """ Function    : on_mouse_look_around_player

            Description : Activates camera rotation by mouse.

            Input       : Integer

            Output      : None

            Return      : None
        """
        if (not self.base.game_instance["kbd_np"].keymap["forward"]
                and not self.base.game_instance["kbd_np"].keymap["backward"]):
            # reset heading and pitch for floater
            self.floater.set_h(0)
            self.floater.set_p(0)

            # Apply heading and pitch
            pv_heading = self.pivot.get_h() - (x - int(base.win.get_x_size() / 2)) * self.mouse_sens
            pv_pitch = self.pivot.get_p() - (y - int(base.win.get_y_size() / 2)) * self.mouse_sens

            # Limit camera heading while player is sitting or laying
            if (self.base.game_instance["is_player_sitting"]
                    or self.base.game_instance["is_player_laying"]):
                self.on_limit_camera_in_social_action()
            else:
                # Heading player in the regular way
                self.pivot.set_h(pv_heading)

                # limit pitch by 60 angle
                if not pv_pitch > 10.0 and not pv_pitch < -50.0:
                    self.pivot.set_p(pv_pitch)

    def on_mouse_rotate_player(self, x, y):
        """ Function    : on_mouse_rotate_player

            Description : Activates player rotation by mouse while walking.

            Input       : Integer

            Output      : None

            Return      : None
        """
        if (self.base.game_instance["kbd_np"].keymap["forward"]
                and not self.base.game_instance["kbd_np"].keymap["backward"]
                or self.base.game_instance["kbd_np"].keymap["backward"]
                and not self.base.game_instance["kbd_np"].keymap["forward"]):
            player_bs = self.base.get_actor_bullet_shape_node(asset="Player",
                                                              type="Player")
            horse_name = self.base.game_instance['player_using_horse']
            horse_bs = render.find("**/{0}:BS".format(horse_name))

            if player_bs and not self.base.game_instance['player_ref'].get_python_tag("is_on_horse"):
                # apply heading and pitch
                heading = player_bs.get_h() - (x - int(base.win.get_x_size() / 2)) * self.mouse_sens
                pv_pitch = self.pivot.get_p() - (y - int(base.win.get_y_size() / 2)) * self.mouse_sens

                player_bs.set_h(heading)

                # Show player only from back
                self.pivot.set_h(180)

                # limit pitch by 60 angle
                if not pv_pitch > 10.0 and not pv_pitch < -50.0:
                    self.pivot.set_p(pv_pitch)

            elif horse_bs and self.base.game_instance['player_ref'].get_python_tag("is_on_horse"):
                # apply heading and pitch
                heading = horse_bs.get_h() - (x - int(base.win.get_x_size() / 2)) * self.mouse_sens
                pv_pitch = self.pivot.get_p() - (y - int(base.win.get_y_size() / 2)) * self.mouse_sens
                horse_bs.set_h(heading)

                # Show player only from back
                self.pivot.set_h(180)

                # limit pitch by 60 angle
                if not pv_pitch > 10.0 and not pv_pitch < -50.0:
                    self.pivot.set_p(pv_pitch)

    def mouse_control(self):
        """ Function    : mouse_control

            Description : Mouse rotation controlling logic for 3rd person view.

            Input       : None

            Output      : None

            Return      : None
        """
        if self.base.game_instance['mouse_control_is_activated'] == 0:
            self.base.game_instance['mouse_control_is_activated'] = 1

        if self.game_settings['Debug']['set_editor_mode'] == 'NO':

            if self.base.game_instance['person_look_mode'] == 'first':
                self.base.camera.set_y(1)

            # TPS Logic
            if self.pivot:
                mouse_direction = base.win.getPointer(0)
                x = mouse_direction.get_x()
                y = mouse_direction.get_y()
                # Recentering the cursor and do mouse look
                if base.win.move_pointer(0, int(base.win.get_x_size() / 2), int(base.win.get_y_size() / 2)):
                    if not self.base.game_instance['is_aiming']:
                        self.reset_rotated_player_joints()
                        self.on_mouse_look_around_player(x, y)
                        self.on_mouse_rotate_player(x, y)

                    elif self.base.game_instance['is_aiming']:
                        if self.base.game_instance['arrow_count'] > 1:
                            self.on_mouse_rotate_in_aiming(x, y)

    def mouse_control_task(self, task):
        """ Function    : mouse_control_task

            Description : Mouse-looking camera task for 3rd person view.

            Input       : Task

            Output      : None

            Return      : Task event
        """
        # Figure out how much the mouse has moved (in pixels)
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
