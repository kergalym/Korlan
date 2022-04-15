class ManageJoints:

    def __init__(self, actor_name):
        self.base = base
        self.actor_name = actor_name
        self.actor = None
        self.actor_parts = {}

    def rotate_player_joint(self, heading, pitch):
        if isinstance(heading, float) and isinstance(pitch, float):
            name = ''
            if not self.actor:
                # Assign once
                if "Player" in self.actor_name:
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
                            self.actor_parts[part].set_r(pitch)

    def reset_rotated_player_joints(self):
        # Rotate by pitch all parts simultaneously
        for part in self.actor_parts:
            if self.actor_parts.get(part):
                if (self.actor_parts[part].get_h() != 0
                        or self.actor_parts[part].get_p() != 0
                        or self.actor_parts[part].get_r() != 0):
                    self.actor_parts[part].set_hpr(0, 0, 0)
