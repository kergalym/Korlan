# from Engine import set_tex_transparency
from direct.actor.Actor import Actor
from Engine.Physics.physics import PhysicsAttr
# from Engine.Collisions.collisions import Collisions
from direct.task.TaskManagerGlobal import taskMgr
from Engine.Render.render import RenderAttr
from Engine.Actors.NPC.state import NpcState
from Engine.FSM.env_ai import EnvAI
from Engine.FSM.npc_ai import NpcAI


class NPC:
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
        self.actor = None
        self.base = base
        self.render = render
        self.anims = None
        self.game_settings = base.game_settings
        self.game_dir = base.game_dir
        self.render_attr = RenderAttr()
        self.npc_state = NpcState()
        self.physics_attr = PhysicsAttr()
        self.fsm_env = EnvAI()
        self.fsm_npc = NpcAI()
        self.actor_life_perc = None
        self.base.actor_is_dead = False
        self.base.actor_is_alive = False

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

    def update_npc_ai_stat(self, task):
        if "BS" in self.actor.get_parent().get_name():
            actor = self.actor.get_parent()
            # self.fsm_npc.set_npc_ai(actor=actor, behavior="seek")
            # self.fsm_npc.set_npc_ai(actor=actor, behavior="flee")
            # self.fsm_npc.set_npc_ai(actor=actor, behavior="pursuer")
            # self.fsm_npc.set_npc_ai(actor=actor, behavior="evader")
            self.fsm_npc.set_npc_ai(actor=actor, behavior="wanderer")
            # self.fsm_npc.set_npc_ai(actor=actor, behavior="obs_avoid")
            # self.fsm_npc.set_npc_ai(actor=actor, behavior="path_follow")
            # self.fsm_npc.set_npc_ai(actor=actor, behavior="path_finding")
            # self.fsm_npc.request("Walk")
            return task.done
        return task.cont

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

            # Set lights and Shadows
            if self.game_settings['Main']['postprocessing'] == 'off':
                # TODO: uncomment if character has normals
                # self.render_attr.set_shadows(self.actor, self.render)
                # self.render_attr.set_ssao(self.actor)
                pass

            if self.game_settings['Debug']['set_debug_mode'] == "YES":
                self.render.analyze()

            base.npc_is_loaded = 1

            taskMgr.add(self.actor_life,
                        "actor_life")

            self.npc_state.set_actor_state(actor=self.actor)

            self.fsm_env.set_ai_world()

            taskMgr.add(self.update_npc_ai_stat,
                        "update_npc_ai_stat")

