class ManageJoints:

    def __init__(self, player):
        self.base = base
        self.joint_is_rotated = False
        self.j_mroot = None
        self.j_helmet = None
        self.j_armor = None
        self.j_pants = None
        self.j_boots = None

        if player:
            name = player.get_name()
            self.j_mroot = player.control_joint(None, "modelRoot", "{0}:Spine".format(name))
            self.j_helmet = player.control_joint(None, "helmet", "{0}:Spine".format(name))
            self.j_armor = player.control_joint(None, "armor", "{0}:Spine".format(name))
            self.j_pants = player.control_joint(None, "pants", "{0}:Spine".format(name))
            self.j_boots = player.control_joint(None, "boots", "{0}:Spine".format(name))

    def rotate_joint(self, heading, pitch):
        if isinstance(heading, float) and isinstance(pitch, float):

            if not self.joint_is_rotated:
                self.joint_is_rotated = True

            # Rotate all parts simultaneously
            if self.joint_is_rotated:
                if self.j_mroot:
                    self.j_mroot.set_h(heading)
                    self.j_mroot.set_p(pitch)
                elif self.j_helmet:
                    self.j_helmet.set_h(heading)
                    self.j_helmet.set_p(pitch)
                elif self.j_armor:
                    self.j_armor.set_h(heading)
                    self.j_armor.set_p(pitch)
                elif self.j_pants:
                    self.j_pants.set_h(heading)
                    self.j_pants.set_p(pitch)
                elif self.j_boots:
                    self.j_boots.set_h(heading)
                    self.j_boots.set_p(pitch)

    def reset_rotated_joints(self):
        # Rotate by pitch all parts simultaneously
        if self.joint_is_rotated:
            if self.j_mroot:
                if self.j_mroot.get_h() != 0 and self.j_mroot.get_p() != 0:
                    self.j_mroot.set_hpr(0, 0, 0)
            elif self.j_helmet:
                if self.j_helmet.get_h() != 0 and self.j_helmet.get_p() != 0:
                    self.j_helmet.set_hpr(0, 0, 0)
            elif self.j_armor:
                if self.j_armor.get_h() != 0 and self.j_armor.get_p() != 0:
                    self.j_armor.set_hpr(0, 0, 0)
            elif self.j_pants:
                if self.j_pants.get_h() != 0 and self.j_pants.get_p() != 0:
                    self.j_pants.set_hpr(0, 0, 0)
            elif self.j_boots:
                if self.j_boots.get_h() != 0 and self.j_boots.get_p() != 0:
                    self.j_boots.set_hpr(0, 0, 0)

            if self.joint_is_rotated:
                self.joint_is_rotated = False
