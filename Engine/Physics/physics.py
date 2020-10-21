from Engine.Collisions.geom_collector import GeomCollector
from Engine.Collisions.collision_solids import BulletCollisionSolids
from panda3d.bullet import BulletCharacterControllerNode
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
        self.geom_collector = GeomCollector()
        self.bullet_solids = BulletCollisionSolids()

        self.korlan = None

        self.no_mask = BitMask32.allOff()
        self.mask = BitMask32.allOn()
        self.mask0 = BitMask32.bit(0)
        self.mask1 = BitMask32.bit(1)
        self.mask2 = BitMask32.bit(2)
        self.mask3 = BitMask32.bit(3)
        self.mask5 = BitMask32.bit(5)
        self.ghost_mask = BitMask32.bit(1)

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
            self.world.do_physics(dt, 10, 1. / 30)

            # Disable colliding
            self.world.set_group_collision_flag(0, 0, False)
            # Enable colliding: player (0), static (1) and npc (2)
            self.world.set_group_collision_flag(0, 1, True)
            self.world.set_group_collision_flag(0, 2, True)

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

    def update_lod_nodes_parent_task(self, task):
        if (not render.find("**/Level_LOD").is_empty()
                and render.find('**/Level_LOD').get_num_nodes() > 0):
            for node in range(render.find('**/Level_LOD').get_num_nodes()):
                # Check if LOD node isn't in World
                if (not render.find('**/World').is_empty()
                        and render.find('**/World').find("**/Level_LOD").is_empty()):
                    render.find('**/Level_LOD').reparent_to(render.find('**/World'))

        if base.game_mode is False and base.menu_mode:
            return task.done

        return task.cont

    def add_asset_collision_task(self, assets, task):
        """ Function    : add_asset_collision_task

            Description : Add asset collision

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
                    if type == 'player' or 'actor':
                        self.set_collision(obj=render.find("**/{0}".format(name)),
                                           type=type,
                                           shape=shape)

                    else:
                        self.set_collision(obj=render.find("**/{0}".format(name)),
                                           type=type,
                                           shape=shape)

        if base.game_mode is False and base.menu_mode:
            return task.done

        return task.cont

    def toggle_physics_debug(self):
        if self.debug_nodepath:
            if self.debug_nodepath.is_hidden():
                self.debug_nodepath.show()
            else:
                self.debug_nodepath.hide()

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

            base.accept("f1", self.toggle_physics_debug)

        self.world = BulletWorld()
        self.world.set_gravity(Vec3(0, 0, -9.81))

        if self.game_settings['Debug']['set_debug_mode'] == "YES":
            if hasattr(self.debug_nodepath, "node"):
                self.world.set_debug_node(self.debug_nodepath.node())

        ground_shape = BulletPlaneShape(Vec3(0, 0, 1), 0)
        ground_nodepath = self.world_nodepath.attachNewNode(BulletRigidBodyNode('Ground'))
        ground_nodepath.node().addShape(ground_shape)
        ground_nodepath.set_pos(0, 0, 0.10)
        ground_nodepath.node().set_into_collide_mask(self.mask)
        self.world.attach_rigid_body(ground_nodepath.node())

        taskMgr.add(self.update_lod_nodes_parent_task,
                    "update_lod_nodes_parent_task",
                    appendTask=True)

        taskMgr.add(self.add_asset_collision_task,
                    "add_asset_collision_task",
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
                self.set_object_colliders(type='static',
                                          shape=shape,
                                          mask=self.mask1)

            # TODO: move item to and use in /Korlan/Engine/Items/items.py:
            if type == "item":
                self.set_object_colliders(type='dynamic',
                                          shape=shape,
                                          mask=self.mask1)

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
                                        mask=self.mask2,
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
            if not base.menu_mode and base.game_mode:
                actor_bs = None
                actor_bs_np = None
                if shape == 'capsule':
                    actor_bs = self.bullet_solids.set_bs_capsule()
                if shape == 'sphere':
                    actor_bs = self.bullet_solids.set_bs_sphere()
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
                
                self.bullet_solids.set_bs_hitbox(actor=actor,
                                                 joints=["LeftHand", "RightHand", "Hips"],
                                                 world=self.world)

    def set_object_colliders(self, type, shape, mask):
        if not (isinstance(type, str)
                and shape
                and mask
                and isinstance(shape, str)):
            return

        if not (not base.menu_mode and base.game_mode):
            return

        base.shaped_objects = []
        geoms = self.geom_collector.geom_collector()

        object_bs_multi = self.bullet_solids.set_bs_auto_multi(objects=geoms, type='static')

        if object_bs_multi:
            for obj, object_bs in zip(object_bs_multi[0], object_bs_multi[1]):
                bs = object_bs_multi[1][object_bs]
                obj = object_bs_multi[0][obj]

                if shape == 'auto':
                    # Save parent before attaching mesh to collider
                    # top_parent = obj.get_parent()
                    top_parent_name = obj.get_parent().get_name()
                    obj_bs_name = "{0}:BS".format(obj.get_name())

                    # TODO: Check if object usable by tag
                    # TODO: Fix double
                    if "Box:BS" in obj_bs_name or "Box:BS" in top_parent_name:
                        type = 'dynamic'

                    # Prevent bullet shape duplication
                    if obj_bs_name not in top_parent_name:
                        if self.world_nodepath:
                            obj_bs_np = self.world_nodepath.attach_new_node(BulletRigidBodyNode(obj_bs_name))
                            if type == 'static':
                                obj_bs_np.node().set_mass(0.0)
                                obj_bs_np.node().add_shape(bs)
                                obj_bs_np.node().set_into_collide_mask(mask)
                            elif type == 'dynamic':
                                obj_bs_np.node().set_mass(0.2)
                                obj_bs_np.node().add_shape(bs)
                                obj_bs_np.node().set_into_collide_mask(self.mask)

                            self.world.attach(obj_bs_np.node())
                            obj.reparent_to(obj_bs_np)

                            obj_bs_np.set_pos(obj.get_pos())
                            obj_bs_np.set_scale(obj.get_scale())
                            # Make item position zero because now it's a child of bullet shape
                            obj.set_pos(0, 0, 0)

                            # Reparent the root node of the level to the World of Physics
                            if not render.find("**/Collisions/lvl*coll/lvl_*").is_empty():
                                render.find("**/Collisions/lvl*coll/lvl_*").reparent_to(render.find("**/World"))

                            base.shaped_objects.append(obj_bs_name)

