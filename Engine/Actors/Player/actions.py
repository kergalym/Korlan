from Engine.FSM.player_ai import FsmPlayer, Idle
from Engine.collisions import Collisions
from direct.task.TaskManagerGlobal import taskMgr

from Engine.world import World
from Settings.Input.keyboard import Keyboard
from Settings.Input.mouse import Mouse
# from direct.interval.MetaInterval import Sequence
from direct.interval.IntervalGlobal import *


class Actions:

    def __init__(self):
        self.is_idle = True
        self.is_moving = False
        self.is_crouching = False
        self.is_standing = False
        self.is_jumping = False
        self.is_hitting = False
        self.is_h_kicking = False
        self.is_f_kicking = False
        self.is_using = False
        self.is_blocking = False
        self.has_sword = False
        self.has_bow = False
        self.has_tengri = False
        self.has_umai = False
        self.actor_play_rate = None
        self.walking_forward_action = "Walking"
        self.crouch_walking_forward_action = 'crouch_walking_forward'
        self.crouched_to_standing_action = "crouched_to_standing"
        self.standing_to_crouch_action = "standing_to_crouch"
        self.base = base
        self.base.korlan_is_idle = self.is_idle
        self.base.korlan_is_moving = self.is_moving
        self.base.korlan_is_crouching = self.is_crouching
        self.base.korlan_is_standing = self.is_standing
        self.base.korlan_is_jumping = self.is_jumping
        self.base.korlan_is_hitting = self.is_hitting
        self.base.korlan_is_h_kicking = self.is_h_kicking
        self.base.korlan_is_f_kicking = self.is_f_kicking
        self.base.korlan_is_using = self.is_using
        self.base.korlan_is_blocking = self.is_blocking
        self.base.korlan_has_sword = self.has_sword
        self.base.korlan_has_bow = self.has_bow
        self.base.korlan_has_tengri = self.has_tengri
        self.base.korlan_has_umai = self.has_umai
        self.render = render
        self.korlan = None
        self.taskMgr = taskMgr
        self.kbd = Keyboard()
        self.mouse = Mouse()
        self.col = Collisions()
        self.world = World()
        self.fsmplayer = FsmPlayer()
        self.idle_player = Idle()

    """ Sets current player position after action """

    def set_player_pos(self, player, pos_y):
        if (player and pos_y
                and isinstance(pos_y, float)):
            player.setY(player, pos_y)
            print("When is kicking: Current: ", player.getY())

    def set_player_state(self, player):
        pass

    """ Prepares actions for scene"""

    def scene_actions_init(self, player, anims):
        if (player
                and anims
                and isinstance(anims, dict)):
            self.kbd.kbd_init()
            self.kbd.kbd_init_released()

            taskMgr.add(self.player_init, "player_init",
                        extraArgs=[player, anims],
                        appendTask=True)

            # Set up the camera
            self.base.camera.setPos(player.getX(), player.getY() + 40, 2)

            self.col.set_inter_collision(player)

    """ Prepares the player for scene """

    def player_init(self, player, anims, task):
        # Save the player initial position so that we can restore it,
        # in case he falls off the map or runs into something.
        startpos = player.getPos()

        # Pass the player object to FSM
        self.fsmplayer.get_player(player=player)

        # TODO: change animation
        any_action = player.getAnimControl(anims['LookingAround'])

        if (any_action.isPlaying() is False
                and self.is_idle
                and self.is_moving is False
                and self.is_crouching is False):
            self.idle_player.enter_idle(player=player, action=anims['LookingAround'], state=self.is_idle)

        # Here we accept keys
        # TODO: change animation and implement state for actions
        #  except movement, crouch and jump action
        self.player_movement_action(player, anims)
        self.player_crouch_action(player, 'crouch', anims)
        self.player_jump_action(player, "jump", anims, "Jumping")
        self.player_use_action(player, "use", anims, "PickingUp")
        self.player_hit_action(player, "attack", anims, "Boxing")
        self.player_h_kick_action(player, "h_attack", anims, "Kicking_3")
        self.player_f_kick_action(player, "f_attack", anims, "Kicking_5")
        self.player_block_action(player, "block", anims, "center_blocking")
        self.player_sword_action(player, "sword", anims, "PickingUp")
        self.player_bow_action(player, "bow", anims, "PickingUp")
        self.player_tengri_action(player, "tengri", anims, "PickingUp")
        self.player_umai_action(player, "umai", anims, "PickingUp")

        print("Current Y: ", player.getY())

        # If the camera is too far from player, move it closer.
        # If the camera is too close to player, move it farther.
        camvec = player.getPos() - self.base.camera.getPos()
        camvec.setZ(0)
        camdist = camvec.length()
        camvec.normalize()
        if camdist > 10.0:
            self.base.camera.setPos(self.base.camera.getPos() + camvec * (camdist - 10))
            camdist = 10.0
        if camdist < 5.0:
            self.base.camera.setPos(self.base.camera.getPos() - camvec * (5 - camdist))
            camdist = 5.0

        # We would have to call traverse() to check for collisions.
        self.col.cTrav.traverse(self.render)

        # Adjust player's Z coordinate.  If player ray hit terrain,
        # update his Z. If it hit anything else, or didn't hit anything, put
        # him back where he was last frame.
        entries = list(self.col.korlanGroundHandler.getEntries())
        entries.sort(key=lambda x: x.getSurfacePoint(self.render).getZ())

        if len(entries) > 0 and entries[0].getIntoNode().getName() == 'mountain':
            player.setZ(0.0)
        else:
            player.setPos(startpos)

        # Keep the camera at one foot above the terrain,
        # or two feet above player, whichever is greater.

        entries = list(self.col.camGroundHandler.getEntries())
        entries.sort(key=lambda x: x.getSurfacePoint(self.render).getZ())

        if len(entries) > 0 and entries[0].getIntoNode().getName() == 'mountain':
            self.base.camera.setZ(entries[0].getSurfacePoint(self.render).getZ() + 1.0)
        if self.base.camera.getZ() < player.getZ() + 2.0:
            self.base.camera.setZ(player.getZ() + 2.0)

        # The camera should look in Korlan direction,
        # but it should also try to stay horizontal, so look at
        # a floater which hovers above Korlan's head.

        self.base.camera.lookAt(self.mouse.set_floater(player))

        return task.cont

    def player_movement_action(self, player, anims):
        if player and isinstance(anims, dict):
            # Get the time that elapsed since last frame.  We multiply this with
            # the desired speed in order to find out with which distance to move
            # in order to achieve that desired speed.
            dt = globalClock.getDt()
            # If a move-key is pressed, move the player in the specified direction.
            speed = 5

            if self.kbd.keymap["left"]:
                player.setH(player.getH() + 300 * dt)
            if self.kbd.keymap["right"]:
                player.setH(player.getH() - 300 * dt)
            if self.kbd.keymap["forward"]:
                player.setY(player, -speed * dt)
            if self.kbd.keymap["backward"]:
                player.setY(player, speed * dt)

            # If the player does action, loop the animation.
            # If it is standing still, stop the animation.
            if (self.kbd.keymap["forward"]
                    or self.kbd.keymap["backward"]
                    or self.kbd.keymap["left"]
                    or self.kbd.keymap["right"]):
                if self.is_moving is False and self.is_crouching is False:
                    player.loop(anims[self.walking_forward_action])
                    player.setPlayRate(self.base.actor_play_rate,
                                       anims[self.walking_forward_action])
                    self.is_idle = False
                    self.is_moving = True
                    self.is_crouching = False
                elif self.is_moving is False and self.is_crouching:
                    player.loop(anims[self.crouch_walking_forward_action])
                    player.setPlayRate(self.base.actor_play_rate,
                                       anims[self.crouch_walking_forward_action])
                    self.is_moving = True
                    self.is_crouching = True
                    self.is_idle = False
            else:
                if self.is_moving and self.is_crouching is False:
                    player.stop()
                    player.pose(anims[self.walking_forward_action], 0)
                    self.is_moving = False
                    self.is_idle = True
                    self.is_crouching = False
                elif self.is_moving and self.is_crouching:
                    player.stop()
                    player.pose(anims[self.crouch_walking_forward_action], 0)
                    self.is_moving = False
                    self.is_idle = True
                    self.is_crouching = False

            # Actor backward movement
            if self.kbd.keymap["backward"]:
                player.setPlayRate(-1.0,
                                   anims[self.walking_forward_action])

    def player_crouch_action(self, player, key, anims):
        if (player and isinstance(anims, dict)
                and isinstance(key, str)):

            crouched_to_standing = player.getAnimControl(anims[self.crouched_to_standing_action])
            standing_to_crouch = player.getAnimControl(anims[self.standing_to_crouch_action])

            # If the player does action, play the animation.
            if self.kbd.keymap[key]:
                self.is_idle = False

                if crouched_to_standing.isPlaying() is False and self.is_crouching is False:
                    player.play(anims[self.standing_to_crouch_action])
                    player.setPlayRate(self.base.actor_play_rate, anims[self.standing_to_crouch_action])
                    self.is_crouching = True
                    if (crouched_to_standing.isPlaying() is False
                            and self.is_crouching):
                        self.is_idle = False

                elif standing_to_crouch.isPlaying() is False and self.is_crouching:
                    any_action_seq = player.actorInterval(
                        anims[self.crouched_to_standing_action],
                        playRate=self.base.actor_play_rate)
                    Sequence(any_action_seq).start()
                    self.is_crouching = False
                    if (crouched_to_standing.isPlaying() is False
                            and self.is_crouching is False):
                        self.is_idle = True

    def player_jump_action(self, player, key, anims, action):
        if (player and isinstance(anims, dict)
                and isinstance(action, str)
                and isinstance(key, str)):
            crouched_to_standing = player.getAnimControl(anims[self.crouched_to_standing_action])
            any_action = player.getAnimControl(anims[action])

            if self.kbd.keymap[key]:
                self.is_idle = False

                if (self.is_jumping is False
                        and crouched_to_standing.isPlaying() is False
                        and self.is_crouching is True):
                    self.is_standing = False
                    self.is_jumping = True
                    # TODO: Use blending for smooth transition between animations
                    # Do an animation sequence if player is crouched.
                    crouch_to_stand_seq = player.actorInterval(anims[self.crouched_to_standing_action],
                                                               playRate=self.base.actor_play_rate)
                    any_action_seq = player.actorInterval(anims[action],
                                                          playRate=self.base.actor_play_rate)
                    Sequence(crouch_to_stand_seq, any_action_seq).start()
                    self.is_crouching = False
                    self.is_jumping = False
                    self.is_standing = True
                    if (any_action.isPlaying() is False
                            and self.is_crouching is False):
                        self.is_idle = True

                elif (self.is_jumping is False
                      and crouched_to_standing.isPlaying() is False
                      and self.is_crouching is False):
                    self.is_jumping = True
                    any_action_seq = player.actorInterval(anims[action],
                                                          playRate=self.base.actor_play_rate)
                    Sequence(any_action_seq).start()
                    self.is_crouching = False
                    self.is_jumping = False
                    if any_action.isPlaying() is False and self.is_jumping is False:
                        self.is_idle = True

    def player_use_action(self, player, key, anims, action):
        if (player and isinstance(anims, dict)
                and isinstance(action, str)
                and isinstance(key, str)):
            crouched_to_standing = player.getAnimControl(anims[self.crouched_to_standing_action])
            any_action = player.getAnimControl(anims[action])

            if self.kbd.keymap[key]:
                self.is_idle = False

                if (self.is_using is False
                        and crouched_to_standing.isPlaying() is False
                        and self.is_crouching is True):
                    self.is_standing = False
                    # TODO: Use blending for smooth transition between animations
                    # Do an animation sequence if player is crouched.
                    crouch_to_stand_seq = player.actorInterval(anims[self.crouched_to_standing_action],
                                                               playRate=self.base.actor_play_rate)
                    any_action_seq = player.actorInterval(anims[action],
                                                          playRate=self.base.actor_play_rate)
                    Sequence(crouch_to_stand_seq, any_action_seq).start()
                    self.is_crouching = False
                    self.is_using = False
                    if (any_action.isPlaying() is False
                            and self.is_crouching is False):
                        self.is_idle = True

                elif (self.is_using is False
                      and crouched_to_standing.isPlaying() is False
                      and self.is_crouching is False):
                    self.is_using = True
                    any_action_seq = player.actorInterval(anims[action], playRate=1.0)
                    Sequence(any_action_seq).start()
                    self.is_crouching = False
                    self.is_using = False
                    if any_action.isPlaying() is False and self.is_using is False:
                        self.is_idle = True

    def player_hit_action(self, player, key, anims, action):
        if (player and isinstance(anims, dict)
                and isinstance(action, str)
                and isinstance(key, str)):
            crouched_to_standing = player.getAnimControl(anims[self.crouched_to_standing_action])
            any_action = player.getAnimControl(anims[action])

            if self.kbd.keymap[key]:
                self.is_idle = False

                if (self.is_hitting is False
                        and crouched_to_standing.isPlaying() is False
                        and self.is_crouching is True):
                    self.is_standing = False
                    # TODO: Use blending for smooth transition between animations
                    # Do an animation sequence if player is crouched.
                    crouch_to_stand_seq = player.actorInterval(anims[self.crouched_to_standing_action],
                                                               playRate=self.base.actor_play_rate)
                    any_action_seq = player.actorInterval(anims[action],
                                                          playRate=self.base.actor_play_rate)
                    Sequence(crouch_to_stand_seq, any_action_seq).start()
                    self.is_crouching = False
                    self.is_hitting = False
                    if (any_action.isPlaying() is False
                            and self.is_crouching is False):
                        self.is_idle = True

                elif (self.is_hitting is False
                      and crouched_to_standing.isPlaying() is False
                      and self.is_crouching is False):
                    self.is_hitting = True
                    any_action_seq = player.actorInterval(anims[action],
                                                          playRate=self.base.actor_play_rate)
                    Sequence(any_action_seq).start()
                    self.is_crouching = False
                    self.is_hitting = False
                    if any_action.isPlaying() is False and self.is_hitting is False:
                        self.is_idle = True

    def player_h_kick_action(self, player, key, anims, action):
        if (player and isinstance(anims, dict)
                and isinstance(action, str)
                and isinstance(key, str)):
            crouched_to_standing = player.getAnimControl(anims[self.crouched_to_standing_action])
            any_action = player.getAnimControl(anims[action])

            if self.kbd.keymap[key]:
                self.is_idle = False

                if (self.is_h_kicking is False
                        and crouched_to_standing.isPlaying() is False
                        and self.is_crouching is True):
                    self.is_standing = False
                    # TODO: Use blending for smooth transition between animations
                    # Do an animation sequence if player is crouched.
                    crouch_to_stand_seq = player.actorInterval(anims[self.crouched_to_standing_action],
                                                               playRate=self.base.actor_play_rate)
                    any_action_seq = player.actorInterval(anims[action],
                                                          playRate=self.base.actor_play_rate)
                    Sequence(crouch_to_stand_seq, any_action_seq).start()

                    # TODO: TEST: Save player position
                    # self.set_player_pos(player, -1.5)

                    self.is_crouching = False
                    self.is_h_kicking = False
                    if (any_action.isPlaying() is False
                            and self.is_crouching is False):
                        self.is_idle = True

                elif (self.is_h_kicking is False
                      and crouched_to_standing.isPlaying() is False
                      and self.is_crouching is False):
                    self.is_h_kicking = True
                    any_action_seq = player.actorInterval(anims[action],
                                                          playRate=self.base.actor_play_rate)
                    Sequence(any_action_seq,
                             Func(player.setY, player, -0.5)).start()
                    print("When is pre-kicking: Current: ", player.getY())
                    # TODO: TEST: Save player position
                    # self.set_player_pos(player, -1.5)
                    print("When is kicked: Current: ", player.getY())
                    self.is_crouching = False
                    self.is_h_kicking = False
                    if any_action.isPlaying() is False and self.is_h_kicking is False:
                        self.is_idle = True

    def player_f_kick_action(self, player, key, anims, action):
        if (player and isinstance(anims, dict)
                and isinstance(action, str)
                and isinstance(key, str)):
            crouched_to_standing = player.getAnimControl(anims[self.crouched_to_standing_action])
            any_action = player.getAnimControl(anims[action])

            if self.kbd.keymap[key]:
                self.is_idle = False

                if (self.is_f_kicking is False
                        and crouched_to_standing.isPlaying() is False
                        and self.is_crouching is True):
                    self.is_standing = False
                    # TODO: Use blending for smooth transition between animations
                    # Do an animation sequence if player is crouched.
                    crouch_to_stand_seq = player.actorInterval(anims[self.crouched_to_standing_action],
                                                               playRate=self.base.actor_play_rate)
                    any_action_seq = player.actorInterval(anims[action],
                                                          playRate=self.base.actor_play_rate)
                    Sequence(crouch_to_stand_seq, any_action_seq).start()
                    self.is_crouching = False
                    self.is_f_kicking = False
                    if (any_action.isPlaying() is False
                            and self.is_crouching is False):
                        self.is_idle = True

                elif (self.is_f_kicking is False
                      and crouched_to_standing.isPlaying() is False
                      and self.is_crouching is False):
                    self.is_f_kicking = True
                    any_action_seq = player.actorInterval(anims[action],
                                                          playRate=self.base.actor_play_rate)
                    Sequence(any_action_seq).start()
                    self.is_crouching = False
                    self.is_f_kicking = False
                    if any_action.isPlaying() is False and self.is_f_kicking is False:
                        self.is_idle = True

    def player_block_action(self, player, key, anims, action):
        if (player and isinstance(anims, dict)
                and isinstance(action, str)
                and isinstance(key, str)):
            crouched_to_standing = player.getAnimControl(anims[self.crouched_to_standing_action])
            any_action = player.getAnimControl(anims[action])

            if self.kbd.keymap[key]:
                self.is_idle = False

                if (self.is_blocking is False
                        and crouched_to_standing.isPlaying() is False
                        and self.is_crouching is True):
                    self.is_standing = False
                    # TODO: Use blending for smooth transition between animations
                    # Do an animation sequence if player is crouched.
                    crouch_to_stand_seq = player.actorInterval(anims[self.crouched_to_standing_action],
                                                               playRate=self.base.actor_play_rate)
                    any_action_seq = player.actorInterval(anims[action],
                                                          playRate=self.base.actor_play_rate)
                    Sequence(crouch_to_stand_seq, any_action_seq).start()
                    self.is_crouching = False
                    self.is_blocking = False
                    if (any_action.isPlaying() is False
                            and self.is_crouching is False):
                        self.is_idle = True

                elif (self.is_blocking is False
                      and crouched_to_standing.isPlaying() is False
                      and self.is_crouching is False):
                    self.is_blocking = True
                    any_action_seq = player.actorInterval(anims[action],
                                                          playRate=self.base.actor_play_rate)
                    Sequence(any_action_seq).start()
                    self.is_crouching = False
                    self.is_blocking = False
                    if any_action.isPlaying() is False and self.is_blocking is False:
                        self.is_idle = True

    def player_sword_action(self, player, key, anims, action):
        if (player and isinstance(anims, dict)
                and isinstance(action, str)
                and isinstance(key, str)):
            crouched_to_standing = player.getAnimControl(anims[self.crouched_to_standing_action])
            any_action = player.getAnimControl(anims[action])

            if self.kbd.keymap[key]:
                self.is_idle = False

                if (self.has_sword is False
                        and crouched_to_standing.isPlaying() is False
                        and self.is_crouching is True):
                    self.is_standing = False
                    # TODO: Use blending for smooth transition between animations
                    # Do an animation sequence if player is crouched.
                    crouch_to_stand_seq = player.actorInterval(anims[self.crouched_to_standing_action],
                                                               playRate=self.base.actor_play_rate)
                    any_action_seq = player.actorInterval(anims[action],
                                                          playRate=self.base.actor_play_rate)
                    Sequence(crouch_to_stand_seq, any_action_seq).start()
                    self.is_crouching = False
                    self.has_sword = False
                    if (any_action.isPlaying() is False
                            and self.is_crouching is False):
                        self.is_idle = True

                elif (self.has_sword is False
                      and crouched_to_standing.isPlaying() is False
                      and self.is_crouching is False):
                    self.has_sword = True
                    any_action_seq = player.actorInterval(anims[action],
                                                          playRate=self.base.actor_play_rate)
                    Sequence(any_action_seq).start()
                    self.is_crouching = False
                    self.has_sword = False
                    if any_action.isPlaying() is False and self.has_sword is False:
                        self.is_idle = True

    def player_bow_action(self, player, key, anims, action):
        if (player and isinstance(anims, dict)
                and isinstance(action, str)
                and isinstance(key, str)):
            crouched_to_standing = player.getAnimControl(anims[self.crouched_to_standing_action])
            any_action = player.getAnimControl(anims[action])

            if self.kbd.keymap[key]:
                self.is_idle = False

                if (self.has_bow is False
                        and crouched_to_standing.isPlaying() is False
                        and self.is_crouching is True):
                    self.is_standing = False
                    # TODO: Use blending for smooth transition between animations
                    # Do an animation sequence if player is crouched.
                    crouch_to_stand_seq = player.actorInterval(anims[self.crouched_to_standing_action],
                                                               playRate=self.base.actor_play_rate)
                    any_action_seq = player.actorInterval(anims[action],
                                                          playRate=self.base.actor_play_rate)
                    Sequence(crouch_to_stand_seq, any_action_seq).start()
                    self.is_crouching = False
                    self.has_bow = False
                    if (any_action.isPlaying() is False
                            and self.is_crouching is False):
                        self.is_idle = True

                elif (self.has_bow is False
                      and crouched_to_standing.isPlaying() is False
                      and self.is_crouching is False):
                    self.has_bow = True
                    any_action_seq = player.actorInterval(anims[action],
                                                          playRate=self.base.actor_play_rate)
                    Sequence(any_action_seq).start()
                    self.is_crouching = False
                    self.has_bow = False
                    if any_action.isPlaying() is False and self.has_bow is False:
                        self.is_idle = True

    def player_tengri_action(self, player, key, anims, action):
        if (player and isinstance(anims, dict)
                and isinstance(action, str)
                and isinstance(key, str)):
            crouched_to_standing = player.getAnimControl(anims[self.crouched_to_standing_action])
            any_action = player.getAnimControl(anims[action])

            if self.kbd.keymap[key]:
                self.is_idle = False

                if (self.has_tengri is False
                        and crouched_to_standing.isPlaying() is False
                        and self.is_crouching is True):
                    self.is_standing = False
                    # TODO: Use blending for smooth transition between animations
                    # Do an animation sequence if player is crouched.
                    crouch_to_stand_seq = player.actorInterval(anims[self.crouched_to_standing_action],
                                                               playRate=self.base.actor_play_rate)
                    any_action_seq = player.actorInterval(anims[action],
                                                          playRate=self.base.actor_play_rate)
                    Sequence(crouch_to_stand_seq, any_action_seq).start()
                    self.is_crouching = False
                    self.has_tengri = False
                    if (any_action.isPlaying() is False
                            and self.is_crouching is False):
                        self.is_idle = True

                elif (self.has_tengri is False
                      and crouched_to_standing.isPlaying() is False
                      and self.is_crouching is False):
                    self.has_tengri = True
                    any_action_seq = player.actorInterval(anims[action],
                                                          playRate=self.base.actor_play_rate)
                    Sequence(any_action_seq).start()
                    self.is_crouching = False
                    self.has_tengri = False
                    if any_action.isPlaying() is False and self.has_tengri is False:
                        self.is_idle = True

    def player_umai_action(self, player, key, anims, action):
        if (player and isinstance(anims, dict)
                and isinstance(action, str)
                and isinstance(key, str)):
            crouched_to_standing = player.getAnimControl(anims[self.crouched_to_standing_action])
            any_action = player.getAnimControl(anims[action])

            if self.kbd.keymap[key]:
                self.is_idle = False

                if (self.has_umai is False
                        and crouched_to_standing.isPlaying() is False
                        and self.is_crouching is True):
                    self.is_standing = False
                    # TODO: Use blending for smooth transition between animations
                    # Do an animation sequence if player is crouched.
                    crouch_to_stand_seq = player.actorInterval(anims[self.crouched_to_standing_action],
                                                               playRate=self.base.actor_play_rate)
                    any_action_seq = player.actorInterval(anims[action],
                                                          playRate=self.base.actor_play_rate)
                    Sequence(crouch_to_stand_seq, any_action_seq).start()
                    self.is_crouching = False
                    self.has_umai = False
                    if (any_action.isPlaying() is False
                            and self.is_crouching is False):
                        self.is_idle = True

                elif (self.has_umai is False
                      and crouched_to_standing.isPlaying() is False
                      and self.is_crouching is False):
                    self.has_umai = True
                    any_action_seq = player.actorInterval(anims[action], playRate=self.base.actor_play_rate)
                    Sequence(any_action_seq).start()
                    self.is_crouching = False
                    self.has_umai = False
                    if any_action.isPlaying() is False and self.has_umai is False:
                        self.is_idle = True
