from panda3d.core import BitMask32
from Engine.Collisions.collision_solids import BulletCollisionSolids
from Engine.FSM.npc_ai import NpcAI
from panda3d.bullet import BulletCharacterControllerNode
from panda3d.bullet import BulletRigidBodyNode
from direct.task.TaskManagerGlobal import taskMgr
from panda3d.core import Vec3, BitMask32
from panda3d.bullet import BulletWorld, BulletDebugNode, BulletRigidBodyNode, BulletPlaneShape


class PhysicsAttr:

    def __init__(self):
        self.world = None
        self.world_nodepath = None
        self.debug_nodepath = None
        self.render = render
        self.game_settings = base.game_settings
        self.game_dir = base.game_dir
        self.game_cfg = base.game_cfg
        self.game_cfg_dir = base.game_cfg_dir
        self.game_settings_filename = base.game_settings_filename
        self.cfg_path = {"game_config_path": "{0}/{1}".format(self.game_cfg_dir,
                                                              self.game_settings_filename)}

        self.cam_cs = None
        self.cam_bs_nodepath = None
        self.cam_collider = None
        self.bs = BulletCollisionSolids()
        self.fsm_npc = NpcAI()

        self.korlan = None

        self.no_mask = BitMask32.allOff()
        self.mask = BitMask32.allOn()
        self.mask0 = BitMask32.bit(0)
        self.mask1 = BitMask32.bit(1)
        self.mask2 = BitMask32.bit(2)
        self.mask3 = BitMask32.bit(3)
        self.mask5 = BitMask32.bit(5)

    def update_physics_task(self, task):
        """ Function    : update_physics_task

            Description : Update Physics

            Input       : Task

            Output      : None

            Return      : Task event
        """
        if self.world:
            # Get the time that elapsed since last frame.
            dt = globalClock.getDt()
            self.world.do_physics(dt, 4, 1. / 240.)
            self.world.set_group_collision_flag(0, 0, False)
            # TODO: set group collision for colliding and non-colliding objects
            self.world.set_group_collision_flag(0, 1, True)
            # Do update RigidBodyNode parent node's position for every frame
            if hasattr(base, "close_item_name"):
                name = base.close_item_name
                if not render.find("**/{0}".format(name)).is_empty():
                    item = render.find("**/{0}".format(name))
                    if 'BS' in item.get_parent().get_name():
                        item.get_parent().node().set_transform_dirty()

        if base.game_mode is False and base.menu_mode:
            return task.done

        return task.cont

    def set_recursive_collision(self, obj):
        if obj and obj.get_num_children() > 0:
            if (not render.find("**/{0}".format(obj.get_name())).is_empty()
                    and render.find("**/{0}:BS".format(obj.get_name())).is_empty()):
                self.set_collision(obj=obj,
                                   type='env',
                                   shape='auto')
            for nested_child in obj.get_children():
                if (not render.find("**/{0}".format(nested_child.get_name())).is_empty()
                        and render.find("**/{0}:BS".format(nested_child.get_name())).is_empty()):
                    self.set_collision(obj=nested_child,
                                       type='env',
                                       shape='auto')
                if nested_child.get_num_children() > 0:
                    for nested_child_2 in nested_child.get_children():
                        if (not render.find("**/{0}".format(nested_child_2.get_name())).is_empty()
                                and render.find("**/{0}:BS".format(nested_child_2.get_name())).is_empty()):
                            self.set_collision(obj=nested_child_2,
                                               type='env',
                                               shape='auto')

    def update_asset_collision_task(self, assets, task):
        """ Function    : update_asset_collision_task

            Description : Update asset statistics

            Input       : Task

            Output      : None

            Return      : Task event
        """
        if isinstance(assets, dict):
            for name, type, shape in zip(assets['name'],
                                         assets['type'],
                                         assets['shape']):
                if (not render.find("**/{0}".format(name)).is_empty()
                        and render.find("**/{0}:BS".format(name)).is_empty()):
                    self.set_collision(obj=render.find("**/{0}".format(name)),
                                       type=type,
                                       shape=shape)

            if not render.find('**/yurt').is_empty() and render.find("**/yurt:BS").is_empty():
                self.set_collision(obj=render.find('**/yurt'), type="env", shape="auto")
                if render.find('**/yurt').get_num_children() > 0:
                    for nested_child in render.find('**/yurt').get_children():
                        if nested_child.get_num_children() > 0:
                            self.set_recursive_collision(nested_child)

        return task.cont

    def set_physics_world(self, assets):
        """ Function    : set_physics_world

            Description : Enable Physics for render_attr

            Input       : None

            Output      : None

            Return      : None
        """
        if render.find("**/World").is_empty():
            # The above code creates a new node,
            # and it sets the worlds gravity to a downward vector with length 9.81.
            # While Bullet is in theory independent from any particular units
            # it is recommended to stick with SI units (kilogram, meter, second).
            # In SI units 9.81 m/s² is the gravity on Earth’s surface.
            self.world_nodepath = self.render.attach_new_node('World')
        # Show a visual representation of the collisions occuring
        if self.game_settings['Debug']['set_debug_mode'] == "YES":
            self.debug_nodepath = self.world_nodepath.attach_new_node(BulletDebugNode('Debug'))
            self.debug_nodepath.show()

        self.world = BulletWorld()
        # Make bullet world instance global to use where it necessary
        # base.bullet_world = self.world
        self.world.set_gravity(Vec3(0, 0, -9.81))

        if self.game_settings['Debug']['set_debug_mode'] == "YES":
            if hasattr(self.debug_nodepath, "node"):
                self.world.set_debug_node(self.debug_nodepath.node())

        ground_shape = BulletPlaneShape(Vec3(0, 0, 1), 0)
        ground_nodepath = self.world_nodepath.attachNewNode(BulletRigidBodyNode('Ground'))
        ground_nodepath.node().addShape(ground_shape)
        ground_nodepath.set_pos(0, 0, 0.10)
        ground_nodepath.set_collide_mask(self.mask)
        self.world.attach_rigid_body(ground_nodepath.node())

        taskMgr.add(self.update_asset_collision_task,
                    "update_asset_stat",
                    extraArgs=[assets],
                    appendTask=True)

        taskMgr.add(self.update_physics_task,
                    "update_physics",
                    appendTask=True)

    def collision_info(self, player, item):
        if player and item and hasattr(base, "bullet_world"):

            query_all = base.bullet_world.ray_test_all(player.get_pos(),
                                                       item.get_pos())

            collision_info = {"hits": query_all.has_hits(),
                              "fraction": query_all.get_closest_hit_fraction(),
                              "num_hits": query_all.get_num_hits()}

            for query in query_all.get_hits():
                collision_info["hit_pos"] = query.get_hit_pos()
                collision_info["hit_normal"] = query.get_hit_normal()
                collision_info["hit_fraction"] = query.get_hit_fraction()
                collision_info["node"] = query.get_node()

            return collision_info

    def set_collision(self, obj, type, shape):
        if (obj and type and shape
                and isinstance(type, str)
                and isinstance(shape, str)):
            if type == "env":
                if hasattr(obj, "set_tag"):
                    obj.set_tag(key=obj.get_name(), value='1')
                self.set_object_collider(obj=obj,
                                         type='static',
                                         col_name='{0}:BS'.format(obj.get_name()),
                                         shape=shape,
                                         mask=self.mask1)

            if type == "item":
                if hasattr(obj, "set_tag"):
                    obj.set_tag(key=obj.get_name(), value='1')
                self.set_object_collider(obj=obj,
                                         type='dynamic',
                                         col_name='{0}:BS'.format(obj.get_name()),
                                         shape=shape,
                                         mask=self.mask0)
            if type == "player":
                self.korlan = obj
                if hasattr(self.korlan, "set_tag"):
                    self.korlan.set_tag(key=obj.get_name(), value='1')
                self.set_actor_collider(actor=self.korlan,
                                        col_name='{0}:BS'.format(self.korlan.get_name()),
                                        shape=shape,
                                        mask=self.mask0,
                                        type="player")
            if type == "npc":
                if hasattr(obj, "set_tag"):
                    obj.set_tag(key=obj.get_name(), value='1')
                self.set_actor_collider(actor=obj,
                                        col_name='{0}:BS'.format(obj.get_name()),
                                        shape=shape,
                                        mask=self.mask0,
                                        type="npc")

    def set_actor_collider(self, actor, col_name, shape, mask, type):
        if (actor
                and col_name
                and shape
                and mask
                and type
                and isinstance(col_name, str)
                and isinstance(shape, str)
                and isinstance(type, str)):
            if base.menu_mode is False and base.game_mode:
                actor_bs = None
                actor_bs_np = None
                if shape == 'capsule':
                    actor_bs = self.bs.set_bs_capsule()
                if shape == 'sphere':
                    actor_bs = self.bs.set_bs_sphere()
                if type == 'player':
                    if self.world_nodepath:
                        base.bullet_char_contr_node = BulletCharacterControllerNode(actor_bs,
                                                                                    0.4,
                                                                                    col_name)
                        actor_bs_np = self.world_nodepath.attach_new_node(base.bullet_char_contr_node)
                        actor_bs_np.set_collide_mask(mask)
                        self.world.attach(base.bullet_char_contr_node)
                        actor.reparent_to(actor_bs_np)
                elif type == 'npc':
                    if self.world_nodepath:
                        actor_contr_node = BulletCharacterControllerNode(actor_bs,
                                                                         0.4,
                                                                         col_name)
                        actor_bs_np = self.world_nodepath.attach_new_node(actor_contr_node)
                        actor_bs_np.set_collide_mask(mask)
                        self.world.attach(actor_contr_node)
                        actor.reparent_to(actor_bs_np)
                # Set actor down to make it
                # at the same point as bullet shape
                actor.set_z(-1)
                # Set the bullet shape position same as actor position
                if actor_bs_np:
                    actor_bs_np.set_x(actor.get_x())
                    actor_bs_np.set_y(actor.get_y())
                # Set actor position to zero
                # after actor becomes a child of bullet shape.
                # It should not get own position values.
                actor.set_y(0)
                actor.set_x(0)

    def set_object_collider(self, obj, type, col_name, shape, mask):
        if (obj
                and col_name
                and isinstance(type, str)
                and shape
                and mask
                and isinstance(col_name, str)
                and isinstance(shape, str)):
            if base.menu_mode is False and base.game_mode:
                if shape == 'convex':
                    object_bs = self.bs.set_bs_convex(obj=obj)

                    if self.world_nodepath:
                        obj_bs_np = self.world_nodepath.attach_new_node(BulletRigidBodyNode(col_name))
                        obj_bs_np.node().set_mass(1.0)
                        obj_bs_np.node().add_shape(object_bs)
                        obj_bs_np.set_collide_mask(mask)
                        self.world.attach(obj_bs_np.node())
                        obj.reparent_to(obj_bs_np)

                        obj_bs_np.set_pos(obj.get_pos())
                        obj_bs_np.set_scale(obj.get_scale())
                        # Make item position zero because now it's a child of bullet shape
                        obj.set_pos(0, 0, 0)
                if shape == 'auto':
                    object_bs = self.bs.set_bs_auto(obj=obj, type=type)
                    if self.world_nodepath and object_bs:
                        obj_bs_np = self.world_nodepath.attach_new_node(BulletRigidBodyNode(col_name))
                        if type == 'dynamic':
                            obj_bs_np.node().set_mass(1.0)
                        elif type == 'static':
                            obj_bs_np.node().set_mass(0)
                        obj_bs_np.node().add_shape(object_bs)
                        obj_bs_np.set_collide_mask(mask)
                        self.world.attach(obj_bs_np.node())
                        obj.reparent_to(obj_bs_np)

                        obj_bs_np.set_pos(obj.get_pos())
                        obj_bs_np.set_scale(obj.get_scale())
                        # Make item position zero because now it's a child of bullet shape
                        obj.set_pos(0, 0, 0)

