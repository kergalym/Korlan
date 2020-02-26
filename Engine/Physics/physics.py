from panda3d.core import Vec3
from panda3d.bullet import BulletWorld


class PhysicsAttr:

    def __init__(self):
        self.world = None
        self.render = render

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
        self.world = BulletWorld()
        self.world.set_gravity(Vec3(0, 0, -9.81))

    def update_physics_task(self, task):
        """ Function    : update_physics_task

            Description : Update Physics for render_attr

            Input       : Task

            Output      : None

            Return      : Task event
        """
        if self.world:
            dt = globalClock.getDt()
            self.world.doPhysics(dt)
        if base.game_mode is False and base.menu_mode:
            return task.done
        return task.cont
