from Engine.Collisions.collision_solids import BulletCollisionSolids
from panda3d.bullet import BulletCharacterControllerNode, BulletBoxShape, BulletSphereShape, BulletGhostNode
from direct.task.TaskManagerGlobal import taskMgr
from panda3d.core import Vec3, BitMask32
from panda3d.bullet import BulletWorld, BulletDebugNode, BulletRigidBodyNode, BulletPlaneShape
from direct.showbase.PhysicsManagerGlobal import physicsMgr


class PhysicsAttr:

    def __init__(self):
        self.physics_mgr = physicsMgr
        self.base = base
        self.world = None
        self.world_nodepath = None
        self.debug_nodepath = None
        self.render = render
        self.game_settings = base.game_settings
        self.game_dir = base.game_dir
        self.game_cfg = base.game_cfg
        self.game_cfg_dir = base.game_cfg_dir
        self.game_settings_filename = base.game_settings_filename
        self.cfg_path = self.game_cfg

        self.cam_cs = None
        self.cam_bs_nodepath = None
        self.cam_collider = None
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

    def collision_info(self, player, item):
        if player and item and self.world:

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
                self.set_static_object_colliders(obj=obj,
                                                 mask=self.mask1,
                                                 automatic=False)

            elif type == "item":
                self.set_dynamic_object_colliders(obj=obj,
                                                  mask=self.mask1,
                                                  automatic=False)

            elif type == "player":
                self.korlan = obj
                if hasattr(self.korlan, "set_tag"):
                    self.korlan.set_tag(key=obj.get_name(), value='1')
                self.set_actor_collider(actor=self.korlan,
                                        col_name='{0}:BS'.format(self.korlan.get_name()),
                                        shape=shape,
                                        mask=self.mask0,
                                        type="player")

            else:
                if hasattr(obj, "set_tag"):
                    obj.set_tag(key=obj.get_name(), value='1')
                self.set_actor_collider(actor=obj,
                                        col_name='{0}:BS'.format(obj.get_name()),
                                        shape=shape,
                                        mask=self.mask,
                                        type=type)

    def set_physics_world(self):
        """ Function    : set_physics_world

            Description : Enable Physics

            Input       : None

            Output      : None

            Return      : None
        """
        world = render.find("**/World")
        if world:
            # Show a visual representation of the collisions occuring
            self.debug_nodepath = world.attach_new_node(BulletDebugNode('Debug'))

            base.accept("f1", self.toggle_physics_debug)

            self.world = BulletWorld()
            self.world.set_gravity(Vec3(0, 0, -9.81))
            self.base.game_instance['physics_world_np'] = self.world

            if self.game_settings['Debug']['set_debug_mode'] == "YES":
                if hasattr(self.debug_nodepath, "node"):
                    self.world.set_debug_node(self.debug_nodepath.node())

            ground_shape = BulletPlaneShape(Vec3(0, 0, 1), 0)
            ground_nodepath = world.attach_new_node(BulletRigidBodyNode('Ground'))
            ground_nodepath.node().add_shape(ground_shape)
            ground_nodepath.set_pos(0, 0, 0.10)
            ground_nodepath.node().set_into_collide_mask(self.mask)
            self.world.attach_rigid_body(ground_nodepath.node())

            # Box
            shape = BulletBoxShape(Vec3(1, 1, 1))
            node = BulletRigidBodyNode('Box')
            node.set_mass(50.0)
            node.add_shape(shape)
            np = render.attach_new_node(node)
            np.set_pos(4, 2, 0)
            self.world.attach_rigid_body(node)
            model = base.loader.load_model('/home/galym/Korlan/tmp/box.egg')
            model.reparent_to(np)
            model.set_name('box')
            model.set_pos(0, 0, 0)
            model.set_hpr(np.get_hpr())

            # Disable colliding
            self.world.set_group_collision_flag(0, 0, False)
            # Enable colliding: player (0), static (1) and npc (2)
            self.world.set_group_collision_flag(0, 1, True)
            self.world.set_group_collision_flag(0, 2, True)

            taskMgr.add(self.update_physics_task,
                        "update_physics_task",
                        appendTask=True)

            self.base.game_instance['physics_is_activated'] = 1

    def toggle_physics_debug(self):
        if self.debug_nodepath:
            if self.debug_nodepath.is_hidden():
                self.debug_nodepath.show()
                # self.debug_nodepath.node().showBoundingBoxes(True)
            else:
                self.debug_nodepath.hide()
                # self.debug_nodepath.node().showBoundingBoxes(False)

    def add_bullet_collider(self, assets):
        """ Function    : add_bullet_collider

            Description : Adds bullet collider

            Input       : Task

            Output      : None

            Return      : None
        """
        if assets and isinstance(assets, dict):
            for name, type, shape in zip(assets['name'],
                                         assets['type'],
                                         assets['shape']):
                np = render.find("**/{0}".format(name))
                np_bs = render.find("**/{0}:BS".format(name))
                if np and not np_bs:
                    if type == 'player':
                        self.set_collision(obj=np,
                                           type=type,
                                           shape=shape)

                    elif type == 'actor':
                        self.set_collision(obj=np,
                                           type=type,
                                           shape=shape)
                    else:
                        self.set_collision(obj=np,
                                           type=type,
                                           shape=shape)

    def update_physics_task(self, task):
        """ Function    : update_physics_task

            Description : Update Physics

            Input       : Task

            Output      : None

            Return      : Task event
        """
        if self.base.game_instance["physics_is_activated"] == 1:
            if self.world:
                # Get the time that elapsed since last frame.
                dt = globalClock.getDt()
                self.world.do_physics(dt, 10, 1. / 30)

                # Do update RigidBodyNode parent node's position for every frame
                if hasattr(base, "close_item_name"):
                    name = base.close_item_name
                    if not render.find("**/{0}".format(name)).is_empty():
                        item = render.find("**/{0}".format(name))
                        if 'BS' in item.get_parent().get_name():
                            item.get_parent().node().set_transform_dirty()
        return task.cont

    def set_actor_collider(self, actor, col_name, shape, mask, type):
        if (actor
                and col_name
                and shape
                and mask
                and type
                and isinstance(col_name, str)
                and isinstance(shape, str)
                and isinstance(type, str)):
            world_np = render.find("**/World")
            if not self.base.game_instance['menu_mode'] and world_np:
                actor_bs = None
                actor_bs_np = None
                if shape == 'capsule':
                    actor_bs = self.bullet_solids.get_bs_capsule()
                if shape == 'sphere':
                    actor_bs = self.bullet_solids.get_bs_sphere()
                if type == 'player':
                    self.base.game_instance['player_controller_np'] = BulletCharacterControllerNode(actor_bs,
                                                                                                    0.4,
                                                                                                    col_name)
                    actor_bs_np = render.attach_new_node(self.base.game_instance['player_controller_np'])
                    actor_bs_np.set_collide_mask(mask)
                    self.world.attach_character(actor_bs_np.node())

                    if self.game_settings['Debug']['set_editor_mode'] == 'NO':
                        if render.find("**/floater"):
                            render.find("**/floater").reparent_to(actor_bs_np)
                    elif self.game_settings['Debug']['set_editor_mode'] == 'YES':
                        actor.reparent_to(actor_bs_np)

                    # Set actor down to make it
                    # at the same point as bullet shape
                    actor.set_z(-1)
                    # Set the bullet shape position same as actor position
                    actor_bs_np.set_x(actor.get_x())
                    actor_bs_np.set_y(actor.get_y())
                    # actor_bs_np.set_z(actor.get_z())
                    # Set actor position to zero
                    # after actor becomes a child of bullet shape.
                    # It should not get own position values.
                    actor.set_y(0)
                    actor.set_x(0)

                    # attach hitboxes and weapons
                    self.bullet_solids.get_bs_hitbox(actor=actor,
                                                     joints=["LeftHand", "RightHand", "Hips"],
                                                     mask=self.mask0,
                                                     world=self.world)
                    # hitboxes task
                    taskMgr.add(self.update_actor_hitbox_trace_task,
                                "update_{0}_hitboxes_task".format(col_name.lower()),
                                extraArgs=[actor], appendTask=True)

                elif type == 'npc':
                    actor_node = BulletRigidBodyNode(col_name)
                    actor_node.set_mass(1.0)
                    actor_node.add_shape(actor_bs)
                    actor_bs_np = world_np.attach_new_node(actor_node)
                    actor_bs_np.set_collide_mask(mask)
                    self.world.attach_rigid_body(actor_bs_np.node())

                    actor.reparent_to(actor_bs_np)
                    self.base.game_instance['actors_np'][col_name] = actor_bs_np

                    self.base.game_instance['actor_controllers_np'][col_name] = actor_node

                    # Set actor down to make it
                    # at the same point as bullet shape
                    actor.set_z(-1)
                    # Set the bullet shape position same as actor position
                    actor_bs_np.set_x(actor.get_x())
                    actor_bs_np.set_y(actor.get_y())
                    # Set actor position to zero
                    # after actor becomes a child of bullet shape.
                    # It should not get own position values.
                    actor.set_y(0)
                    actor.set_x(0)

                    # attach hitboxes and weapons
                    self.bullet_solids.get_bs_hitbox(actor=actor,
                                                     joints=["LeftHand", "RightHand", "Hips"],
                                                     mask=self.mask,
                                                     world=self.world)

                    # hitboxes task
                    taskMgr.add(self.update_actor_hitbox_trace_task,
                                "update_{0}_hitboxes_task".format(col_name.lower()),
                                extraArgs=[actor], appendTask=True)

                    actor_bs_np.node().set_kinematic(True)

                    # reparent bullet-shaped actor to LOD node
                    actor_bs_np.reparent_to(self.base.game_instance['lod_np'])
                    self.base.game_instance['lod_np'].node().add_switch(50.0, 0.0)

                    # attach trigger sphere
                    self.set_ghost_trigger(actor)
                    taskMgr.add(self.update_actor_area_trigger_task,
                                "update_{0}_area_trigger_task".format(col_name.lower()),
                                extraArgs=[actor], appendTask=True)

                elif type == 'npc_animal':
                    actor_bs_box = BulletBoxShape(Vec3(0.3, 1.5, 1))
                    actor_node = BulletRigidBodyNode(col_name)
                    actor_node.set_mass(1.0)
                    actor_node.add_shape(actor_bs_box)
                    actor_bs_np = world_np.attach_new_node(actor_node)
                    actor_bs_np.set_collide_mask(mask)
                    self.world.attach_rigid_body(actor_bs_np.node())

                    actor.reparent_to(actor_bs_np)

                    self.base.game_instance['actors_np'][col_name] = actor_bs_np
                    self.base.game_instance['actor_controllers_np'][col_name] = actor_node

                    # Set actor down to make it
                    # at the same point as bullet shape
                    actor.set_z(-1)
                    # Set the bullet shape position same as actor position
                    actor_bs_np.set_x(actor.get_x())
                    actor_bs_np.set_y(actor.get_y())
                    # Set actor position to zero
                    # after actor becomes a child of bullet shape.
                    # It should not get own position values.
                    actor.set_y(0)
                    actor.set_x(0)

                    actor_bs_np.node().set_kinematic(True)

                    # reparent bullet-shaped actor to LOD node
                    actor_bs_np.reparent_to(self.base.game_instance['lod_np'])
                    self.base.game_instance['lod_np'].node().add_switch(50.0, 0.0)

                    # attach trigger sphere
                    if "Horse" in col_name:
                        self.set_ghost_trigger(actor)
                        taskMgr.add(self.update_mountable_animal_area_trigger_task,
                                    "update_{0}_area_trigger_task".format(col_name.lower()),
                                    extraArgs=[actor], appendTask=True)
                    else:
                        self.set_ghost_trigger(actor)
                        taskMgr.add(self.update_actor_area_trigger_task,
                                    "update_{0}_area_trigger_task".format(col_name.lower()),
                                    extraArgs=[actor], appendTask=True)

    def set_static_object_colliders(self, obj, mask, automatic):
        if obj and mask and self.world:
            shape = None
            for child in obj.get_children():
                # Skip child which already has Bullet shape
                if ("BS" in child.get_name()
                        or "BS" in child.get_parent().get_name()):
                    continue
                # Skip unused mesh
                if "Ground" in child.get_name():
                    continue

                if "ground" in child.get_name():
                    continue

                if "Grass" in child.get_name():
                    continue

                if "tree" in child.get_name():
                    continue

                if "mountain" in child.get_name():
                    continue

                if automatic:
                    shape = self.bullet_solids.get_bs_auto(obj=child, type_="static")
                elif not automatic:
                    shape = self.bullet_solids.get_bs_predefined(obj=child, type_="static")

                if child.get_num_children() == 0:
                    if shape:
                        child_bs_name = "{0}:BS".format(child.get_name())
                        child_bs_np = obj.attach_new_node(BulletRigidBodyNode(child_bs_name))
                        child_bs_np.node().set_mass(0.0)
                        child_bs_np.node().add_shape(shape)
                        child_bs_np.node().set_into_collide_mask(self.mask1)

                        self.world.attach(child_bs_np.node())
                        child.reparent_to(child_bs_np)

                        child_bs_np.set_pos(child.get_pos())
                        child_bs_np.set_hpr(child.get_hpr())
                        child_bs_np.set_scale(child.get_scale())

                        # Make item position zero because now it's a child of bullet shape
                        child.set_pos(0, 0, 0)

                elif child.get_num_children() > 0:
                    self.set_static_object_colliders(child, mask, automatic)

    def set_dynamic_object_colliders(self, obj, mask, automatic):
        if obj and mask and self.world:
            shape = None
            for child in obj.get_children():
                # Skip child which already has Bullet shape
                if "BS" in child.get_name() or "BS" in child.get_parent().get_name():
                    continue

                if automatic:
                    shape = self.bullet_solids.get_bs_auto(obj=child, type_="dynamic")
                elif not automatic:
                    shape = self.bullet_solids.get_bs_predefined(obj=child, type_="dynamic")

                if child.get_num_children() == 0:
                    if shape:
                        child_bs_name = "{0}:BS".format(child.get_name())
                        child_bs_np = obj.attach_new_node(BulletRigidBodyNode(child_bs_name))
                        child_bs_np.node().set_mass(2.0)
                        child_bs_np.node().add_shape(shape)
                        child_bs_np.node().set_into_collide_mask(self.mask1)

                        self.world.attach(child_bs_np.node())
                        child.reparent_to(child_bs_np)

                        child_bs_np.set_pos(child.get_pos())
                        child_bs_np.set_hpr(child.get_hpr())
                        child_bs_np.set_scale(child.get_scale())

                        # Make item position zero because now it's a child of bullet shape
                        child.set_pos(0, 0, 0)

                elif child.get_num_children() > 0:
                    self.set_dynamic_object_colliders(child, mask, automatic)

    def set_ghost_trigger(self, actor):
        if actor:
            radius = 1.75 - 2 * 0.3
            sphere = BulletSphereShape(radius)
            trigger_bg = BulletGhostNode('{0}_trigger'.format(actor.get_name()))
            trigger_bg.add_shape(sphere)
            trigger_np = self.render.attach_new_node(trigger_bg)
            trigger_np.set_collide_mask(BitMask32(0x0f))
            self.world.attach_ghost(trigger_bg)
            trigger_np.reparent_to(actor)
            trigger_np.set_pos(0, 0, 1)

    def update_mountable_animal_area_trigger_task(self, animal_actor, task):
        if animal_actor:
            if animal_actor.find("**/{0}_trigger".format(animal_actor.get_name())):
                trigger = animal_actor.find("**/{0}_trigger".format(animal_actor.get_name())).node()
                trigger_np = animal_actor.find("**/{0}_trigger".format(animal_actor.get_name()))
                player = self.base.game_instance['player_ref']
                player_bs = self.base.get_actor_bullet_shape_node(asset="Player", type="Player")
                actor_bs_np = self.base.game_instance['actors_np']["{0}:BS".format(animal_actor.get_name())]

                for node in trigger.get_overlapping_nodes():
                    # ignore trigger itself and ground both
                    if "NPC" in node.get_name() or "Player" in node.get_name():
                        # if player close to horse
                        if self.base.game_instance['player_ref'] and player_bs:
                            if player_bs.get_distance(trigger_np) <= 2 \
                                    and player_bs.get_distance(trigger_np) >= 1:
                                if (not animal_actor.get_python_tag("is_mounted")
                                        and not player.get_python_tag("is_on_horse")
                                        and node.get_name() == player_bs.get_name()):
                                    # keep horse name if detected actor is the player
                                    # and player is not on horse and horse is free
                                    animal_actor.set_python_tag("is_ready_to_be_used", True)
                                    if hasattr(base, "player_states"):
                                        base.player_states["horse_is_ready_to_be_used"] = True
                                        base.game_instance['player_using_horse'] = animal_actor.get_name()
                                elif (not animal_actor.get_python_tag("is_mounted")
                                      and not player.get_python_tag("is_on_horse")
                                      and node.get_name() != player_bs.get_name()):
                                    # clear horse name if player is on horse, horse is not free
                                    # and detected actor is not player
                                    animal_actor.set_python_tag("is_ready_to_be_used", False)
                                    if hasattr(base, "player_states"):
                                        base.player_states["horse_is_ready_to_be_used"] = False

                                if animal_actor.get_python_tag("npc_hud_np"):
                                    animal_actor.get_python_tag("npc_hud_np").show()

                            elif (player_bs.get_distance(trigger_np) >= 2
                                  and player_bs.get_distance(trigger_np) <= 5):
                                if animal_actor.get_python_tag("npc_hud_np"):
                                    animal_actor.get_python_tag("npc_hud_np").hide()

                # keep actor_bs_np height while kinematic is active
                # because in kinematic it has no gravity impact and gets unwanted drop down
                if actor_bs_np and actor_bs_np.node().is_kinematic:
                    actor_bs_np.set_z(0.96)

        if self.base.game_instance['menu_mode']:
            return task.done

        return task.cont

    def update_actor_area_trigger_task(self, actor, task):
        if actor:
            if actor.find("**/{0}_trigger".format(actor.get_name())):
                trigger = actor.find("**/{0}_trigger".format(actor.get_name())).node()
                trigger_np = actor.find("**/{0}_trigger".format(actor.get_name()))
                player_bs = self.base.get_actor_bullet_shape_node(asset="Player", type="Player")
                actor_bs_np = self.base.game_instance['actors_np']["{0}:BS".format(actor.get_name())]

                for node in trigger.get_overlapping_nodes():
                    # ignore trigger itself and ground both
                    if "NPC" in node.get_name() or "Player" in node.get_name():
                        # if player close to horse
                        if self.base.game_instance['player_ref']:
                            if player_bs.get_distance(trigger_np) <= 2 \
                                    and player_bs.get_distance(trigger_np) >= 1:
                                if actor.get_python_tag("npc_hud_np"):
                                    actor.get_python_tag("npc_hud_np").show()
                            elif (player_bs.get_distance(trigger_np) >= 2
                                  and player_bs.get_distance(trigger_np) <= 5):
                                if actor.get_python_tag("npc_hud_np"):
                                    actor.get_python_tag("npc_hud_np").hide()

                # keep actor_bs_np height while kinematic is active
                # because in kinematic it has no gravity impact and gets unwanted drop down
                if actor_bs_np and actor_bs_np.node().is_kinematic:
                    actor_bs_np.set_z(0.96)

        if self.base.game_instance['menu_mode']:
            return task.done

        return task.cont

    def update_actor_hitbox_trace_task(self, actor, task):
        if actor and actor.find("**/**Hips:HB"):
            hips_node = actor.find("**/**Hips:HB").node()
            for node in hips_node.get_overlapping_nodes():
                damage_weapons = actor.get_python_tag("damage_weapons")
                for weapon in damage_weapons:
                    if weapon in node.get_name():
                        # actor.play("damage")
                        if "NPC" in actor.get_name():
                            if actor.get_python_tag("health_np"):
                                if actor.get_python_tag("health_np")['value'] > 0:
                                    actor.get_python_tag("health_np")['value'] -= 1
                                    health = actor.get_python_tag("health_np")['value']
                                    print("got damage from", node.get_name(), "decreases ", health, " of ", actor.get_name())

                        elif "Player" in actor.get_name():
                            if self.base.game_instance['hud_np']:
                                if self.base.game_instance['hud_np'].player_bar_ui_health['value'] > 0:
                                    self.base.game_instance['hud_np'].player_bar_ui_health['value'] -= 1
                                    health = actor.get_python_tag("health")
                                    health -= 1
                                    actor.set_python_tag("health", health)

        if self.base.game_instance['menu_mode']:
            return task.done

        return task.cont
