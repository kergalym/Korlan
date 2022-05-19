from direct.actor.Actor import Actor
from Engine.Renderer.renderer import RenderAttr
from Engine.Actors.NPC.state import NpcState


class NpcGeneric:
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
        self.render_attr = RenderAttr()
        self.npc_state = NpcState()

        self.actor = None
        self.game_settings = base.game_settings

    async def set_actor(self, mode, name, type, cls, path, animation, axis, rotation, scale, culling):
        if (isinstance(path, str)
                and isinstance(name, str)
                and isinstance(type, str)
                and isinstance(cls, str)
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

            self.actor = await self.base.loader.load_model(path, blocking=False)
            self.actor = Actor(self.actor, animation[1])

            self.actor.set_name(name)
            self.actor.set_scale(self.actor, self.scale_x, self.scale_y, self.scale_z)
            self.actor.set_pos(self.pos_x, self.pos_y, self.pos_z)
            self.actor.set_h(self.actor, self.rot_h)
            self.actor.set_p(self.actor, self.rot_p)
            self.actor.set_r(self.actor, self.rot_r)

            # Hardware skinning
            self.render_attr.set_hardware_skinning(self.actor, True)

            # Get actor joints
            base.actor_joints = self.actor.get_joints()

            # Set two sided, since some model may be broken
            self.actor.set_two_sided(culling)

            # Panda3D 1.10 doesn't enable alpha blending for textures by default
            self.actor.set_transparency(True)

            # toggle texture compression for textures to compress them
            # before load into VRAM
            self.base.toggle_texture_compression(self.actor)

            self.actor.reparent_to(self.base.game_instance['lod_np'])

            # LOD quality preset
            for lod_qk in self.base.game_instance["lod_quality"]:
                if self.game_settings['Main']['details'] == lod_qk:
                    lod_qv = self.base.game_instance["lod_quality"][lod_qk]
                    self.base.game_instance['lod_np'].node().add_switch(lod_qv[0],
                                                                        lod_qv[1])

            # Make actor global
            self.base.game_instance['actors_ref'][name] = self.actor

            if self.game_settings['Main']['postprocessing'] == 'on':
                self.render_attr.render_pipeline.prepare_scene(self.actor)

            # Add Bullet collider for this actor
            self.base.messenger.send("add_bullet_collider")

            if self.game_settings['Debug']['set_debug_mode'] == "YES":
                self.render.analyze()

            self.base.game_instance["npc_state_cls"] = self.npc_state

            # Set HUD and tags
            self.npc_state.set_npc_hud(actor=self.actor)

            # Set NPC type
            self.actor.set_python_tag("npc_type", type)

            # Set NPC class
            self.actor.set_python_tag("npc_class", cls)

            # Set NPC Parameters
            self.npc_state.setup_npc_state(actor=self.actor)


