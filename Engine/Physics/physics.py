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
        self.cfg_path = {"game_config_path":
                         "{0}/{1}".format(self.game_cfg_dir, self.game_settings_filename)}

    def update_physics_task(self, task):
        """ Function    : update_physics_task

            Description : Update Physics for render_attr

            Input       : Task

            Output      : None

            Return      : Task event
        """
        if self.world:
            # Get the time that elapsed since last frame.
            dt = globalClock.getDt()
            self.world.do_physics(dt, 4, 1. / 240.)
            self.world.set_group_collision_flag(0, 0, False)
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

    def set_physics(self):
        """ Function    : set_physics

            Description : Enable Physics for render_attr

            Input       : None

            Output      : None

            Return      : None
        """
        # The above code creates a new render_attr,
        # and it sets the worlds gravity to a downward vector with length 9.81.
        # While Bullet is in theory independent from any particular units
        # it is recommended to stick with SI units (kilogram, meter, second).
        # In SI units 9.81 m/s² is the gravity on Earth’s surface.
        self.world_nodepath = self.render.attach_new_node('World')
        # World
        # Show a visual representation of the collisions occuring
        if self.game_settings['Debug']['set_debug_mode'] == "YES":
            self.debug_nodepath = self.world_nodepath.attach_new_node(BulletDebugNode('Debug'))
            self.debug_nodepath.show()
        self.world = BulletWorld()
        # Make bullet world instance global to use where it necessary
        base.bullet_world = self.world
        self.world.set_gravity(Vec3(0, 0, -9.81))

        if hasattr(self.debug_nodepath, "node"):
            self.world.set_debug_node(self.debug_nodepath.node())

        ground_shape = BulletPlaneShape(Vec3(0, 0, 1), 0)
        ground_nodepath = self.world_nodepath.attachNewNode(BulletRigidBodyNode('Ground'))
        ground_nodepath.node().addShape(ground_shape)
        ground_nodepath.set_pos(0, 0, 0.10)
        ground_nodepath.set_collide_mask(BitMask32.allOn())
        self.world.attach_rigid_body(ground_nodepath.node())

        taskMgr.add(self.update_physics_task,
                    "update_physics",
                    appendTask=True)

