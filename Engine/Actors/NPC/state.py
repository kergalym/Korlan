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
        self.damage_weapons = ['sword_BGN', 'arrow', 'spear_BGN', 'fireballs_BGN']

    def setup_npc_state(self, actor):
        if actor:
            generic_states = {
                "is_alive": True,
                "is_idle": True,
                "is_moving": False,
                "is_running": False,
                "is_crouch_moving": False,
                "is_crouching": False,
                "is_jumping": False,
                "is_attacked": False,
                "is_busy": False,
                "is_blocking": False,
                "is_using": False,
                "is_turning": False,
                "is_sitting": False,
                "is_laying": False
            }
            human_spec_states = {
                "has_sword": False,
                "has_bow": False,
                "horse_riding": False,
                "is_on_horse": False
            }
            horse_spec_states = {
                "is_mounted": False,
                "is_ready_to_be_used": False
            }

            actor.set_python_tag("generic_states", generic_states)

            npc_type = actor.get_python_tag("npc_type")

            if npc_type == "npc":
                actor.set_python_tag("human_states", human_spec_states)

            elif npc_type == "npc_animal" and "Horse" in actor.get_name():
                actor.set_python_tag("horse_spec_states", horse_spec_states)

            actor.set_python_tag("damage_weapons", self.damage_weapons)

    def set_npc_hud(self, actor):
        if actor:
            npc_name = actor.get_name()
            npc_hud_ui = DirectFrame(text="",
                                     frameColor=(0.0, 0.0, 0.0, 0.4),
                                     pos=(1.7, 0, -1.1),
                                     frameSize=self.npc_hud_ui_frame_size,
                                     scale=self.npc_hud_ui_scale)
            base.npc_hud_ui = npc_hud_ui
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
                                   pos=(-1.32, 0, 1.31),
                                   scale=(0.3, 0, 1.2),
                                   parent=npc_hud_ui)

            stamina = DirectWaitBar(text="",
                                    value=100,
                                    range=100,
                                    frameColor=(0, 0.1, 0.1, 1),
                                    barColor=(0.6, 0.5, 0, 1),
                                    pos=(-1.32, 0, 1.15),
                                    scale=(0.3, 0, 0.9),
                                    parent=npc_hud_ui)
            courage = DirectWaitBar(text="",
                                    value=100,
                                    range=100,
                                    frameColor=(0, 0.1, 0.1, 1),
                                    barColor=(0.6, 0.6, 0.7, 1),
                                    pos=(-1.32, 0, 1.01),
                                    scale=(0.3, 0, 0.9),
                                    parent=npc_hud_ui)
            npc_hud_ui.hide()

            actor.set_python_tag("npc_hud_np", npc_hud_ui)
            actor.set_python_tag("health_np", health)
            actor.set_python_tag("damage_level", 1)

            actor.set_python_tag("stamina_np", stamina)
            actor.set_python_tag("courage_np", courage)

    def clear_npc_hud(self, actor):
        if actor and actor.get_python_tag("npc_hud_np"):
            actor.get_python_tag("npc_hud_np").hide()
            actor.get_python_tag("npc_hud_np").destroy()
            actor.get_python_tag("npc_hud_np").remove_node()

    def set_npc_equipment(self, actor, bone_name):
        if actor and isinstance(bone_name, str):
            joint = actor.exposeJoint(None, "modelRoot", bone_name)

            weapons = actor.get_python_tag("allowed_weapons")
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
        if (actor and weapon_name and bone_name
                and isinstance(weapon_name, str)
                and isinstance(bone_name, str)):
            weapons = self.base.game_instance["weapons"]
            if weapons:
                for weapon in weapons:
                    if weapon != weapon_name:
                        self.remove_weapon(actor, weapon, "Korlan:Spine1")

            joint = actor.exposeJoint(None, "modelRoot", bone_name)
            if actor.find("**/{0}".format(weapon_name)):
                if "bow" not in weapon_name:
                    # get weapon collider
                    weapon = actor.find("**/{0}_BGN".format(weapon_name))
                    weapon.reparent_to(joint)
                    # rescale weapon because it's scale 100 times smaller than we need
                    weapon.set_scale(100)
                    weapon.set_pos(-20.0, 40.0, 1.0)
                    weapon.set_hpr(212.47, 0.0, 18.43)
                    if weapon.is_hidden():
                        weapon.show()

                elif "bow" in weapon_name:
                    weapon = actor.find("**/{0}".format(weapon_name))
                    weapon.reparent_to(joint)
                    # rescale weapon because it's scale 100 times smaller than we need
                    weapon.set_scale(100)
                    weapon.set_pos(0, 2.0, 2.0)
                    weapon.set_hpr(216.57, 293.80, 316.85)
                    if weapon.is_hidden():
                        weapon.show()

    def remove_weapon(self, actor, weapon_name, bone_name):
        if (actor and weapon_name and bone_name
                and isinstance(weapon_name, str)
                and isinstance(bone_name, str)):
            joint = actor.exposeJoint(None, "modelRoot", bone_name)
            if actor.find("**/{0}".format(weapon_name)):
                if "bow" not in weapon_name:
                    # get weapon collider
                    weapon = actor.find("**/{0}_BGN".format(weapon_name))
                    weapon.reparent_to(joint)
                    # self.clear_weapon_collider(weapon=weapon, joint=joint)
                    # rescale weapon because it's scale 100 times smaller than we need
                    weapon.set_scale(100)
                    weapon.set_pos(10, -14.90, -8)
                    weapon.set_hpr(0, 0, 0)
                elif "bow" in weapon_name:
                    weapon = actor.find("**/{0}".format(weapon_name))
                    weapon.reparent_to(joint)
                    # rescale weapon because it's scale 100 times smaller than we need
                    weapon.set_scale(100)
                    weapon.set_pos(0, 12, -12)
                    weapon.set_hpr(78.69, 99.46, 108.43)

    def pick_up_item(self, actor, joint):
        if (actor
                and joint
                and isinstance(joint, str)):
            item = actor.get_python_tag("used_item_np")
            exposed_joint = actor.expose_joint(None, "modelRoot", joint)
            # Get bullet shape node path
            if (item
                    and exposed_joint.find(item.get_name()).is_empty()):
                # We want to keep original scale of the item
                if hasattr(item, "set_python_tag"):
                    item.set_python_tag("orig_scale", item.get_scale())

                item.wrt_reparent_to(exposed_joint)
                item.set_scale(100)

                # Set kinematics to make item follow actor joint
                if hasattr(item.node(), "set_kinematic"):
                    item.node().set_kinematic(True)

                # Set item position and rotation
                for name, pos, hpr in zip(actor.get_python_tag("usable_item_list")["name"],
                                          actor.get_python_tag("usable_item_list")["pos"],
                                          actor.get_python_tag("usable_item_list")["hpr"]):
                    if name in item.get_name():
                        item.set_hpr(hpr)
                        item.set_pos(pos)

                # Prevent fast moving objects from passing through thin obstacles.
                if hasattr(item.node(), "set_ccd_motion_threshold"):
                    item.node().set_ccd_motion_threshold(1e-7)
                if hasattr(item.node(), "set_ccd_swept_sphere_radius"):
                    item.node().set_ccd_swept_sphere_radius(0.50)

                actor.set_python_tag("is_item_using", True)
                actor.set_python_tag("is_item_ready", False)

                item_prop = actor.get_python_tag("current_item_prop")
                if item_prop:
                    item_prop['in-use'] = True

                # TODO: Uncomment after pick_up_item() is debugged
                """
                add_item_to_inventory = self.base.shared_functions['add_item_to_inventory']
                if add_item_to_inventory:
                    item_prop = player.get_python_tag("current_item_prop")
                    item_prop['in-use'] = False
                    add_item_to_inventory(item=item.get_name(),
                                          count=1,
                                          inventory="INVENTORY_1",
                                          inventory_type="misc")
                    actor.set_python_tag("is_item_using", False)
                    actor.set_python_tag("used_item_np", None)
                    actor.set_python_tag("is_item_ready", False)
                    actor.set_python_tag("current_item_prop", None)
                """

    def drop_item(self, actor):
        if actor and not render.find('**/World').is_empty():
            item = actor.get_python_tag("used_item_np")
            if item:
                name = "{0}:BS".format(actor.get_name())
                actor_bs = self.base.game_instance["actors_np"][name]
                world = render.find('**/World')
                item.reparent_to(world)

                if hasattr(item, "get_python_tag"):
                    scale = item.get_python_tag("orig_scale")
                    item.set_scale(scale)
                    item.set_hpr(0, 0, 0)

                # Put the item near actor
                # If actor has the bullet shape
                if actor_bs:
                    pos = Vec3(actor_bs.get_x(), actor_bs.get_y(), 0.2)
                    item.set_pos(pos)

                if hasattr(item.node(), "set_kinematic"):
                    item.node().set_kinematic(False)

                actor.set_python_tag("is_item_using", False)
                actor.set_python_tag("used_item_np", None)
                actor.set_python_tag("is_item_ready", False)



