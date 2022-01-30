from direct.gui.DirectLabel import DirectLabel
from direct.gui.DirectWaitBar import DirectWaitBar
from direct.gui.DirectGui import DirectFrame
from direct.gui.OnscreenImage import OnscreenImage
from panda3d.core import TransparencyAttrib, FontPool

from panda3d.bullet import BulletBoxShape, BulletRigidBodyNode, BulletGhostNode
from panda3d.core import NodePath, BitMask32, Vec3


class NpcState:

    def __init__(self):
        self.base = base
        self.fonts = base.fonts_collector()
        self.menu_font = self.fonts['OpenSans-Regular']
        # instance of the abstract class
        self.font = FontPool
        self.images = base.textures_collector(path="Settings/UI")

        # Left, right, bottom, top
        self.npc_hud_ui_frame_size = [-1.85, -1, 1.99, 0.88]
        self.npc_hud_ui_scale = (1.2, 0, 0.20)

    def setup_npc_state(self, actor):
        if actor:
            generic_states = {
                "is_alive": True,
                "is_idle": True,
                "is_moving": False,
                "is_running": False,
                "is_crouch_moving": False,
                "is_crouching": False,
                "is_standing": False,
                "is_jumping": False,
                "is_attacked": False,
                "is_busy": False,
                "is_turning": False,
                "is_mounted": False,
                "horse_riding": False,
                "is_on_horse": False
            }
            human_spec_states = {
                "is_hitting": False,
                "is_h_kicking": False,
                "is_f_kicking": False,
                "is_using": False,
                "is_blocking": False,
                "has_sword": False,
                "has_bow": False
            }
            horse_spec_states = {
                "is_mounted": False,
                "is_ready_to_be_used": False
            }

            for key in generic_states:
                value = generic_states[key]
                actor.set_python_tag(key, value)

            if "Human" in actor.get_name():
                for key in human_spec_states:
                    value = human_spec_states[key]
                    actor.set_python_tag(key, value)

            elif "Horse" in actor.get_name():
                for key in horse_spec_states:
                    value = horse_spec_states[key]
                    actor.set_python_tag(key, value)

    def set_npc_hud(self, actor):
        if actor:
            npc_name = actor.get_name()
            npc_hud_ui = DirectFrame(text="",
                                     frameColor=(0.0, 0.0, 0.0, 0.4),
                                     pos=(0.35, 0, 0.57),
                                     frameSize=self.npc_hud_ui_frame_size,
                                     scale=self.npc_hud_ui_scale)
            # logo
            logo = OnscreenImage(image=self.images['{0}_logo_ui'.format(npc_name.lower())],
                                 pos=(-1.73, 0, 1.45),
                                 scale=(0.1, 0, 0.47),
                                 parent=npc_hud_ui)
            logo.set_transparency(TransparencyAttrib.MAlpha)
            # text
            DirectLabel(text=npc_name,
                        text_fg=(255, 255, 255, 1),
                        text_font=self.font.load_font(self.menu_font),
                        frameColor=(255, 255, 255, 0),
                        pos=(-1.4, 0, 1.7),
                        scale=(0.03, 0, 0.2),
                        borderWidth=(0, 0),
                        parent=npc_hud_ui)
            # bar
            health = DirectWaitBar(text="",
                                   value=100,
                                   range=100,
                                   frameColor=(0, 0.1, 0.1, 1),
                                   barColor=(0.6, 0, 0, 1),
                                   pos=(-1.32, 0, 1.2),
                                   scale=(0.3, 0, 1.7),
                                   parent=npc_hud_ui)

            # todo: add stamina and courage
            """
            stamina = DirectWaitBar(text="",
                                    value=100,
                                    range=100,
                                    frameColor=(0, 0.1, 0.1, 1),
                                    barColor=(0.6, 0, 0, 1),
                                    pos=(-1.32, 0, 1.2),
                                    scale=(0.3, 0, 1.7),
                                    parent=npc_hud_ui)
            courage = DirectWaitBar(text="",
                                    value=100,
                                    range=100,
                                    frameColor=(0, 0.1, 0.1, 1),
                                    barColor=(0.6, 0, 0, 1),
                                    pos=(-1.32, 0, 1.2),
                                    scale=(0.3, 0, 1.7),
                                    parent=npc_hud_ui)
            """
            npc_hud_ui.hide()

            actor.set_python_tag("npc_hud_np", npc_hud_ui)
            actor.set_python_tag("npc_health_np", health)

            # todo: add stamina and courage
            # actor.set_python_tag("npc_stamina_np", courage)
            # actor.set_python_tag("npc_courage_np", courage)

    def clear_npc_hud(self, actor):
        if actor and actor.get_python_tag("npc_hud_np"):
            actor.get_python_tag("npc_hud_np").hide()
            actor.get_python_tag("npc_hud_np").destroy()
            actor.get_python_tag("npc_hud_np").remove_node()

    def set_npc_equipment(self, actor, bone_name):
        # fixme
        if actor and isinstance(bone_name, str):
            joint = actor.exposeJoint(None, "modelRoot", bone_name)

            weapons = self.base.game_instance["weapons"]
            if weapons:
                for name in weapons:
                    weapon = base.loader.loadModel(base.assets_collector()[name])
                    weapon.set_name(name)
                    if "bow" not in name:
                        weapon.reparent_to(joint)
                        weapon.set_pos(10, 20, -8)
                        weapon.set_hpr(325.30, 343.30, 7.13)
                        weapon.set_scale(100)
                        self.set_weapon_collider(weapon=weapon, joint=joint)
                    if "bow" in name:
                        weapon.reparent_to(joint)
                        weapon.set_pos(0, 12, -12)
                        weapon.set_hpr(78.69, 99.46, 108.43)
                        weapon.set_scale(100)

    def set_weapon_collider(self, weapon, joint):
        if weapon and joint:
            # Create weapon collider
            name = weapon.get_name()
            min_, max_ = weapon.get_tight_bounds()
            size = max_ - min_
            shape = BulletBoxShape(Vec3(0.05, 0.55, 0.05))
            body = BulletGhostNode('{0}_BGN'.format(name))
            weapon_rb_np = NodePath(body)
            weapon_rb_np.wrt_reparent_to(joint)
            weapon_rb_np.set_pos(10, -14.90, -8)
            weapon_rb_np.set_hpr(0, 0, 0)
            weapon_rb_np.set_scale(weapon.get_scale())
            weapon.wrt_reparent_to(weapon_rb_np)
            weapon.set_hpr(325, 343, 0)
            weapon.set_pos(0, 0.3, 0)
            weapon_rb_np.node().add_shape(shape)
            # weapon_rb_np.node().set_mass(2.0)

            # Player and its owning arrow won't collide with each other
            weapon_rb_np.set_collide_mask(BitMask32.bit(0x0f))

            # Enable CCD
            # weapon_rb_np.node().set_ccd_motion_threshold(1e-7)
            # weapon_rb_np.node().set_ccd_swept_sphere_radius(0.50)
            # weapon_rb_np.node().set_kinematic(True)

            self.base.game_instance['physics_world_np'].attach_ghost(weapon_rb_np.node())

    def clear_weapon_collider(self, weapon, joint):
        if weapon and joint:
            if "BRB" in weapon.get_parent().get_name():
                weapon_rb_np = weapon.get_parent()
                weapon.reparent_to(joint)
                self.base.game_instance['physics_world_np'].remove_rigid_body(weapon_rb_np.node())

    def get_weapon(self, actor, weapon_name, bone_name):
        # fixme
        if (actor and weapon_name and bone_name
                and isinstance(weapon_name, str)
                and isinstance(bone_name, str)):
            weapons = self.base.game_instance["weapons"]
            if weapons:
                for weapon in weapons:
                    if weapon != weapon_name:
                        self.remove_weapon(actor, weapon, "Korlan:Spine1")

            joint = actor.exposeJoint(None, "modelRoot", bone_name)
            if render.find("**/{0}".format(weapon_name)):
                if "bow" not in weapon_name:
                    # get weapon collider
                    weapon = render.find("**/{0}_BGN".format(weapon_name))
                    weapon.reparent_to(joint)
                    # rescale weapon because it's scale 100 times smaller than we need
                    weapon.set_scale(100)
                    weapon.set_pos(-20.0, 40.0, 1.0)
                    weapon.set_hpr(212.47, 0.0, 18.43)
                    if weapon.is_hidden():
                        weapon.show()

                elif "bow" in weapon_name:
                    weapon = render.find("**/{0}".format(weapon_name))
                    weapon.reparent_to(joint)
                    # rescale weapon because it's scale 100 times smaller than we need
                    weapon.set_scale(100)
                    weapon.set_pos(0, 2.0, 2.0)
                    weapon.set_hpr(216.57, 293.80, 316.85)
                    if weapon.is_hidden():
                        weapon.show()

                base.player_state_unarmed = False
                base.player_state_armed = True
                base.player_state_magic = False

    def remove_weapon(self, actor, weapon_name, bone_name):
        # fixme
        if (actor and weapon_name and bone_name
                and isinstance(weapon_name, str)
                and isinstance(bone_name, str)):
            joint = actor.exposeJoint(None, "modelRoot", bone_name)
            if render.find("**/{0}".format(weapon_name)):
                if "bow" not in weapon_name:
                    # get weapon collider
                    weapon = render.find("**/{0}_BGN".format(weapon_name))
                    weapon.reparent_to(joint)
                    # self.clear_weapon_collider(weapon=weapon, joint=joint)
                    # rescale weapon because it's scale 100 times smaller than we need
                    weapon.set_scale(100)
                    weapon.set_pos(10, -14.90, -8)
                    weapon.set_hpr(0, 0, 0)
                elif "bow" in weapon_name:
                    weapon = render.find("**/{0}".format(weapon_name))
                    weapon.reparent_to(joint)
                    # rescale weapon because it's scale 100 times smaller than we need
                    weapon.set_scale(100)
                    weapon.set_pos(0, 12, -12)
                    weapon.set_hpr(78.69, 99.46, 108.43)

    def drop_item(self, player):
        pass

    def pick_up_item(self, player, joint, items_dist_vect):
        pass

    def take_item(self, player, joint, items_dist_vect):
        pass


