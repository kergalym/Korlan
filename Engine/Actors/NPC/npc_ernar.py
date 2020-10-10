from direct.actor.Actor import Actor
from direct.gui.DirectWaitBar import DirectWaitBar
from direct.gui.OnscreenText import OnscreenText
from direct.task.TaskManagerGlobal import taskMgr
from panda3d.core import TextNode


class NpcErnar:
    def __init__(self):
        self.scale_x = 1.25
        self.scale_y = 1.25
        self.scale_z = 1.25
        self.pos_x = -1.5
        self.pos_y = 9.8
        self.pos_z = -3.2
        self.rot_h = -0.10
        self.rot_p = 0
        self.rot_r = 0
        self.base = base
        self.render = render
        self.actor = None
        self.anims = None
        self.game_settings = base.game_settings
        self.game_dir = base.game_dir
        self.actor_life_perc = None
        self.actor_is_dead = False
        self.actor_is_alive = False
        self.npc_life_label = None

    def actor_life(self, task):
        if self.actor:
            actor_bs = self.base.get_actor_bullet_shape_node(asset=self.actor.get_name(), type="NPC")
            if actor_bs:
                self.set_actor_label(name=actor_bs.get_name(), actor_bs=actor_bs)
                self.set_actor_life(actor_bs=actor_bs)
                return task.done
        # self.has_actor_life()
        return task.cont

    def has_actor_life(self):
        if (self.actor_is_dead is False
                and self.actor_is_alive is False):
            self.actor_is_alive = True
            self.actor_life_perc = 150
        else:
            return False

    def set_actor_life(self, actor_bs):
        if actor_bs:
            self.actor_life_perc = 150
            self.npc_life_label = DirectWaitBar(text="", value=self.actor_life_perc,
                                                range=self.actor_life_perc,
                                                pos=(0.0, 0.0, 0.85), scale=.10)
            self.npc_life_label.reparent_to(actor_bs)
            self.npc_life_label.set_billboard_point_eye()
            self.npc_life_label.set_bin("fixed", 0)

    def set_actor_label(self, name, actor_bs):
        if actor_bs and name and isinstance(name, str):
            if "_" in name and ":BS" in name:
                name_to_disp = name.split("_")[1]
                name_to_disp = name_to_disp.split(":")[0]
                npc_label = OnscreenText(text=name_to_disp, pos=(0.0, 0.9),
                                         fg=(255, 255, 255, 1), scale=.10)
                npc_label.reparent_to(actor_bs)
                npc_label.set_billboard_point_eye()
                npc_label.set_bin("fixed", 0)

    async def set_actor(self, mode, name, path, animation, axis, rotation, scale, culling):

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

            base.npc_is_loaded = 0

            self.actor = await self.base.loader.load_model(path, blocking=False)
            self.actor = Actor(self.actor, animation[1])

            base.npc_is_loaded = 1

            self.actor.set_name(name)
            self.actor.set_scale(self.actor, self.scale_x, self.scale_y, self.scale_z)
            self.actor.set_pos(self.pos_x, self.pos_y, self.pos_z)
            self.actor.set_h(self.actor, self.rot_h)
            self.actor.set_p(self.actor, self.rot_p)
            self.actor.set_r(self.actor, self.rot_r)

            # Get actor joints
            base.actor_joints = self.actor.get_joints()

            # Set two sided, since some model may be broken
            self.actor.set_two_sided(culling)

            # Panda3D 1.10 doesn't enable alpha blending for textures by default
            self.actor.set_transparency(True)

            self.actor.reparentTo(self.render)

            # self.base.level_of_details(obj=self.actor)

            self.base.set_textures_srgb(True)

            # Set lights and Shadows
            if self.game_settings['Main']['postprocessing'] == 'off':
                # TODO: uncomment if character has normals
                # self.render_attr.set_shadows(self.actor, self.render)
                # self.render_attr.set_ssao(self.actor)
                pass

            if self.game_settings['Debug']['set_debug_mode'] == "YES":
                self.render.analyze()

            taskMgr.add(self.actor_life,
                        "actor_life")