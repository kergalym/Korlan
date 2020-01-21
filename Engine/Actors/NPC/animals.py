from direct.actor.Actor import Actor


class Animals:

    def __init__(self):

        self.scale_x = 0.25
        self.scale_y = 0.25
        self.scale_z = 0.25
        self.pos_x = 0
        self.pos_y = 0
        self.pos_z = 1.9
        self.cam_pos_x = 0
        self.cam_pos_y = 4.8
        self.cam_pos_z = -1.7

    def model_load(self, path, loader, render):
        if (isinstance(path, str)
                and loader
                and render):
            # Load and transform the actor.
            npc = loader.Actor(path)
            npc.reparentTo(render)
            npc.setScale(self.scale_x, self.scale_y, self.scale_z)
            npc.setPos(self.pos_x, self.pos_y, self.pos_z)
            npc.lookAt(npc)


class Cat(Animals):

    def __init__(self):
        pass

        Animals.__init__(self)

    def npc_move(self):
        pass

    def npc_stop(self):
        pass

    def npc_turn_left(self):
        pass

    def npc_turn_right(self):
        pass

    def npc_jump(self):
        pass
