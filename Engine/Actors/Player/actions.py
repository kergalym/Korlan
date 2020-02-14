from Engine.Actors.Player.state import PlayerState
from Engine.FSM.player_ai import FsmPlayer, Idle
from Engine.Items.items import Items
from Engine.Collisions.collisions import Collisions
from direct.task.TaskManagerGlobal import taskMgr

from Engine.world import World
from Settings.Input.keyboard import Keyboard
from Settings.Input.mouse import Mouse
from direct.interval.IntervalGlobal import *


class Actions:

    def __init__(self):
        self.base = base
        base.is_idle = True
        base.is_moving = False
        base.is_crouch_moving = False
        base.is_crouching = False
        base.is_standing = False
        base.is_jumping = False
        base.is_hitting = False
        base.is_h_kicking = False
        base.is_f_kicking = False
        base.is_using = False
        base.is_blocking = False
        base.has_sword = False
        base.has_bow = False
        base.has_tengri = False
        base.has_umai = False
        self.actor_play_rate = None
        self.walking_forward_action = "Walking"
        self.crouch_walking_forward_action = 'crouch_walking_forward'
        self.crouched_to_standing_action = "crouched_to_standing"
        self.standing_to_crouch_action = "standing_to_crouch"
        self.render = render
        self.korlan = None
        self.taskMgr = taskMgr
        self.kbd = Keyboard()
        self.mouse = Mouse()
        self.world = World()
        self.fsmplayer = FsmPlayer()
        self.idle_player = Idle()
        self.item_cls = Items()
        self.state = PlayerState()
        self.col = Collisions()

    """ Sets current player position after action """
    
    def seq_kick_played_wrapper(self):
        base.is_crouching = False
        base.is_h_kicking = False

    def set_player_pos(self, player, pos_y):
        if (player and pos_y
                and isinstance(pos_y, float)):
            player.setY(player, pos_y)
    
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
            self.base.camera.set_pos(player.getX(), player.get_y() + 40, 2)

            self.col.set_inter_collision(player=player)

    """ Prepares the player for scene """

    def player_init(self, player, anims, task):
        # Pass the player object to FSM
        self.fsmplayer.get_player(player=player)

        # TODO: change animation
        any_action = player.get_anim_control(anims['LookingAround'])

        # print(base.is_idle)

        if (any_action.is_playing() is False
                and base.is_idle
                and base.is_moving is False):
            self.idle_player.enter_idle(player=player, action=anims['LookingAround'], state=True)

        # Here we accept keys
        # TODO: change animation and implement state for actions
        #  except movement, crouch and jump action
        if base.player_state_unarmed:
            self.player_movement_action(player, anims)
            self.player_crouch_action(player, 'crouch', anims)
            self.player_jump_action(player, "jump", anims, "Jumping")
            self.player_use_action(player, "use", anims, "PickingUp")
            self.player_hit_action(player, "attack", anims, "Boxing")
            self.player_h_kick_action(player, "h_attack", anims, "Kicking_3")
            self.player_f_kick_action(player, "f_attack", anims, "Kicking_5")
            self.player_block_action(player, "block", anims, "center_blocking")
        if base.player_state_armed:
            self.player_movement_action(player, anims)
            self.player_crouch_action(player, 'crouch', anims)
            self.player_jump_action(player, "jump", anims, "Jumping")
            self.player_use_action(player, "use", anims, "PickingUp")
            # self.player_hit_action(player, "attack", anims, "Boxing")
            # self.player_h_kick_action(player, "h_attack", anims, "Kicking_3")
            # self.player_f_kick_action(player, "f_attack", anims, "Kicking_5")
            # self.player_block_action(player, "block", anims, "center_blocking")
            # self.player_sword_action(player, "sword", anims, "PickingUp")
            # self.player_bow_action(player, "bow", anims, "PickingUp")
        if base.player_state_magic:
            self.player_movement_action(player, anims)
            self.player_crouch_action(player, 'crouch', anims)
            self.player_jump_action(player, "jump", anims, "Jumping")
            self.player_use_action(player, "use", anims, "PickingUp")
            self.player_hit_action(player, "attack", anims, "Boxing")
            self.player_h_kick_action(player, "h_attack", anims, "Kicking_3")
            self.player_f_kick_action(player, "f_attack", anims, "Kicking_5")
            self.player_block_action(player, "block", anims, "center_blocking")
            self.player_tengri_action(player, "tengri", anims, "PickingUp")
            self.player_umai_action(player, "umai", anims, "PickingUp")

        # If the camera is too far from player, move it closer.
        # If the camera is too close to player, move it farther.
        camvec = player.get_pos() - self.base.camera.get_pos()
        camvec.set_z(0)
        camdist = camvec.length()
        camvec.normalize()
        if camdist > 10.0:
            self.base.camera.set_pos(self.base.camera.get_pos() + camvec * (camdist - 10))
            camdist = 10.0
        if camdist < 5.0:
            self.base.camera.set_pos(self.base.camera.get_pos() - camvec * (5 - camdist))
            camdist = 5.0

        if self.base.camera.get_z() < player.get_z() + 2.0:
            self.base.camera.set_z(player.get_z() + 2.0)

        self.col.c_trav.traverse(self.render)

        # The camera should look in Korlan direction,
        # but it should also try to stay horizontal, so look at
        # a floater which hovers above Korlan's head.
        self.base.camera.look_at(self.mouse.set_floater(player))

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
            if self.kbd.keymap["forward"] and base.is_moving:
                player.setY(player, -speed * dt)
            if self.kbd.keymap["backward"] and base.is_moving:
                player.setY(player, speed * dt)

            # If the player does action, loop the animation.
            # If it is standing still, stop the animation.
            if (self.kbd.keymap["forward"]
                    or self.kbd.keymap["backward"]
                    or self.kbd.keymap["left"]
                    or self.kbd.keymap["right"]):
                if base.is_moving is False and base.is_crouching is False:
                    player.loop(anims[self.walking_forward_action])
                    player.set_play_rate(self.base.actor_play_rate,
                                         anims[self.walking_forward_action])
                    base.is_moving = True
                    base.is_crouching = False
                    self.state.set_player_idle_state(False)
                elif base.is_moving is False and base.is_crouching:
                    player.loop(anims[self.crouch_walking_forward_action])
                    player.set_play_rate(self.base.actor_play_rate,
                                         anims[self.crouch_walking_forward_action])
                    base.is_moving = True
                    base.is_crouching = True
                    self.state.set_player_idle_state(False)

            else:
                if base.is_moving and base.is_crouching is False:
                    player.stop()
                    player.pose(anims[self.walking_forward_action], 0)
                    base.is_moving = False
                    base.is_crouching = False
                    self.state.set_player_idle_state(True)
                elif base.is_moving and base.is_crouching:
                    player.stop()
                    player.pose(anims[self.crouch_walking_forward_action], 0)
                    base.is_moving = False
                    base.is_crouching = False
                    self.state.set_player_idle_state(True)

            # Actor backward movement
            if self.kbd.keymap["backward"]:
                player.set_play_rate(-1.0,
                                     anims[self.walking_forward_action])

    def player_crouch_action(self, player, key, anims):
        if (player and isinstance(anims, dict)
                and isinstance(key, str)):

            crouched_to_standing = player.get_anim_control(anims[self.crouched_to_standing_action])
            standing_to_crouch = player.get_anim_control(anims[self.standing_to_crouch_action])

            # If the player does action, play the animation.
            if self.kbd.keymap[key]:
                if (crouched_to_standing.is_playing() is False
                        and base.is_crouching is False):
                    player.play(anims[self.standing_to_crouch_action])
                    player.set_play_rate(self.base.actor_play_rate,
                                         anims[self.standing_to_crouch_action])
                    base.is_crouching = True
                    if (crouched_to_standing.is_playing() is False
                            and base.is_crouching):
                        self.state.set_player_idle_state(False)

                elif standing_to_crouch.is_playing() is False and base.is_crouching:
                    any_action_seq = player.actor_interval(anims[self.crouched_to_standing_action],
                                                           playRate=self.base.actor_play_rate)
                    Sequence(any_action_seq,
                             Func(self.state.set_player_idle_state, True)
                             ).start()
                    base.is_crouching = False

    def player_jump_action(self, player, key, anims, action):
        if (player and isinstance(anims, dict)
                and isinstance(action, str)
                and isinstance(key, str)):
            crouched_to_standing = player.get_anim_control(anims[self.crouched_to_standing_action])
            any_action = player.get_anim_control(anims[action])

            if self.kbd.keymap[key]:
                base.is_idle = False

                if (base.is_jumping is False
                        and crouched_to_standing.is_playing() is False
                        and base.is_crouching is True):
                    base.is_standing = False
                    # TODO: Use blending for smooth transition between animations
                    # Do an animation sequence if player is crouched.
                    crouch_to_stand_seq = player.actor_interval(anims[self.crouched_to_standing_action],
                                                                playRate=self.base.actor_play_rate)
                    any_action_seq = player.actor_interval(anims[action],
                                                           playRate=self.base.actor_play_rate)
                    Sequence(crouch_to_stand_seq, any_action_seq).start()
                    base.is_crouching = False
                    base.is_jumping = False
                    if (any_action.is_playing() is False
                            and base.is_crouching is False):
                        base.is_idle = True

                elif (base.is_jumping is False
                      and crouched_to_standing.is_playing() is False
                      and base.is_crouching is False):
                    base.is_jumping = True
                    any_action_seq = player.actor_interval(anims[action],
                                                           playRate=self.base.actor_play_rate)
                    Sequence(any_action_seq,
                             Func(self.state.set_player_idle_state, True)
                             ).start()
                    base.is_crouching = False
                    base.is_jumping = False

    def player_use_action(self, player, key, anims, action):
        if (player and isinstance(anims, dict)
                and isinstance(action, str)
                and isinstance(key, str)):
            crouched_to_standing = player.get_anim_control(anims[self.crouched_to_standing_action])
            any_action = player.get_anim_control(anims[action])

            if self.kbd.keymap[key]:
                base.is_idle = False

                if (base.is_using is False
                        and crouched_to_standing.is_playing() is False
                        and base.is_crouching is True):
                    base.is_standing = False
                    # TODO: Use blending for smooth transition between animations
                    # Do an animation sequence if player is crouched.
                    crouch_to_stand_seq = player.actor_interval(anims[self.crouched_to_standing_action],
                                                                playRate=self.base.actor_play_rate)
                    any_action_seq = player.actor_interval(anims[action],
                                                           playRate=self.base.actor_play_rate)
                    Sequence(crouch_to_stand_seq, any_action_seq).start()
                    base.is_crouching = False
                    base.is_using = False
                    if (any_action.is_playing() is False
                            and base.is_crouching is False):
                        base.is_idle = True

                elif (base.is_using is False
                      and crouched_to_standing.is_playing() is False
                      and base.is_crouching is False):
                    base.is_using = True
                    if base.is_using:
                        self.item_cls.item_selector(actor=player,
                                                    joint="Korlan:LeftHand")

                    any_action_seq = player.actor_interval(anims[action],
                                                           playRate=self.base.actor_play_rate)
                    Sequence(any_action_seq).start()
                    base.player_state_armed = True
                    base.is_crouching = False
                    base.is_using = False
                    if any_action.is_playing() is False and base.is_using is False:
                        base.is_idle = True

    def player_hit_action(self, player, key, anims, action):
        if (player and isinstance(anims, dict)
                and isinstance(action, str)
                and isinstance(key, str)):
            crouched_to_standing = player.get_anim_control(anims[self.crouched_to_standing_action])
            any_action = player.get_anim_control(anims[action])

            if self.kbd.keymap[key]:
                base.is_idle = False

                if (base.is_hitting is False
                        and crouched_to_standing.is_playing() is False
                        and base.is_crouching is True):
                    base.is_standing = False
                    # TODO: Use blending for smooth transition between animations
                    # Do an animation sequence if player is crouched.
                    crouch_to_stand_seq = player.actor_interval(anims[self.crouched_to_standing_action],
                                                                playRate=self.base.actor_play_rate)
                    any_action_seq = player.actor_interval(anims[action],
                                                           playRate=self.base.actor_play_rate)
                    Sequence(crouch_to_stand_seq, any_action_seq).start()
                    base.is_crouching = False
                    base.is_hitting = False
                    if (any_action.is_playing() is False
                            and base.is_crouching is False):
                        base.is_idle = True

                elif (base.is_hitting is False
                      and crouched_to_standing.is_playing() is False
                      and base.is_crouching is False):
                    base.is_hitting = True
                    any_action_seq = player.actor_interval(anims[action],
                                                           playRate=self.base.actor_play_rate)
                    Sequence(any_action_seq).start()
                    base.is_crouching = False
                    base.is_hitting = False
                    if any_action.is_playing() is False and base.is_hitting is False:
                        base.is_idle = True

    def player_h_kick_action(self, player, key, anims, action):
        if (player and isinstance(anims, dict)
                and isinstance(action, str)
                and isinstance(key, str)):
            crouched_to_standing = player.get_anim_control(anims[self.crouched_to_standing_action])
            any_action = player.get_anim_control(anims[action])

            if self.kbd.keymap[key]:
                base.is_idle = False

                if (base.is_h_kicking is False
                        and crouched_to_standing.is_playing() is False
                        and base.is_crouching is True):
                    base.is_standing = False
                    # TODO: Use blending for smooth transition between animations
                    # Do an animation sequence if player is crouched.
                    crouch_to_stand_seq = player.actor_interval(anims[self.crouched_to_standing_action],
                                                                playRate=self.base.actor_play_rate)
                    any_action_seq = player.actor_interval(anims[action],
                                                           playRate=self.base.actor_play_rate)
                    Sequence(crouch_to_stand_seq,
                             any_action_seq,
                             Func(self.set_player_pos, player, -1.5)).start()

                    base.is_crouching = False
                    base.is_h_kicking = False
                    if (any_action.is_playing() is False
                            and base.is_crouching is False):
                        base.is_idle = True

                elif (base.is_h_kicking is False
                      and crouched_to_standing.is_playing() is False
                      and base.is_crouching is False):
                    base.is_h_kicking = True
                    any_action_seq = player.actor_interval(anims[action],
                                                           playRate=self.base.actor_play_rate)
                    Sequence(any_action_seq,
                             Func(self.seq_kick_played_wrapper),
                             Func(self.set_player_pos, player, -1.5),
                             Func(self.state.set_player_idle_state, False)
                             ).start()

    def player_f_kick_action(self, player, key, anims, action):
        if (player and isinstance(anims, dict)
                and isinstance(action, str)
                and isinstance(key, str)):
            crouched_to_standing = player.get_anim_control(anims[self.crouched_to_standing_action])
            any_action = player.get_anim_control(anims[action])

            if self.kbd.keymap[key]:
                base.is_idle = False

                if (base.is_f_kicking is False
                        and crouched_to_standing.is_playing() is False
                        and base.is_crouching is True):
                    base.is_standing = False
                    # TODO: Use blending for smooth transition between animations
                    # Do an animation sequence if player is crouched.
                    crouch_to_stand_seq = player.actor_interval(anims[self.crouched_to_standing_action],
                                                                playRate=self.base.actor_play_rate)
                    any_action_seq = player.actor_interval(anims[action],
                                                           playRate=self.base.actor_play_rate)
                    Sequence(crouch_to_stand_seq, any_action_seq).start()
                    base.is_crouching = False
                    base.is_f_kicking = False
                    if (any_action.is_playing() is False
                            and base.is_crouching is False):
                        base.is_idle = True

                elif (base.is_f_kicking is False
                      and crouched_to_standing.is_playing() is False
                      and base.is_crouching is False):
                    base.is_f_kicking = True
                    any_action_seq = player.actor_interval(anims[action],
                                                           playRate=self.base.actor_play_rate)
                    Sequence(any_action_seq).start()
                    base.is_crouching = False
                    base.is_f_kicking = False
                    if any_action.is_playing() is False and base.is_f_kicking is False:
                        base.is_idle = True

    def player_block_action(self, player, key, anims, action):
        if (player and isinstance(anims, dict)
                and isinstance(action, str)
                and isinstance(key, str)):
            crouched_to_standing = player.get_anim_control(anims[self.crouched_to_standing_action])
            any_action = player.get_anim_control(anims[action])

            if self.kbd.keymap[key]:
                base.is_idle = False

                if (base.is_blocking is False
                        and crouched_to_standing.is_playing() is False
                        and base.is_crouching is True):
                    base.is_standing = False
                    # TODO: Use blending for smooth transition between animations
                    # Do an animation sequence if player is crouched.
                    crouch_to_stand_seq = player.actor_interval(anims[self.crouched_to_standing_action],
                                                                playRate=self.base.actor_play_rate)
                    any_action_seq = player.actor_interval(anims[action],
                                                           playRate=self.base.actor_play_rate)
                    Sequence(crouch_to_stand_seq, any_action_seq).start()
                    base.is_crouching = False
                    base.is_blocking = False
                    if (any_action.is_playing() is False
                            and base.is_crouching is False):
                        base.is_idle = True

                elif (base.is_blocking is False
                      and crouched_to_standing.is_playing() is False
                      and base.is_crouching is False):
                    base.is_blocking = True
                    any_action_seq = player.actor_interval(anims[action],
                                                           playRate=self.base.actor_play_rate)
                    Sequence(any_action_seq).start()
                    base.is_crouching = False
                    base.is_blocking = False
                    if any_action.is_playing() is False and base.is_blocking is False:
                        base.is_idle = True

    def player_sword_action(self, player, key, anims, action):
        if (player and isinstance(anims, dict)
                and isinstance(action, str)
                and isinstance(key, str)):
            crouched_to_standing = player.get_anim_control(anims[self.crouched_to_standing_action])
            any_action = player.get_anim_control(anims[action])

            if self.kbd.keymap[key]:
                base.is_idle = False

                if (base.has_sword is False
                        and crouched_to_standing.is_playing() is False
                        and base.is_crouching is True):
                    base.is_standing = False
                    # TODO: Use blending for smooth transition between animations
                    # Do an animation sequence if player is crouched.
                    crouch_to_stand_seq = player.actor_interval(anims[self.crouched_to_standing_action],
                                                                playRate=self.base.actor_play_rate)
                    any_action_seq = player.actor_interval(anims[action],
                                                           playRate=self.base.actor_play_rate)
                    Sequence(crouch_to_stand_seq, any_action_seq).start()
                    base.is_crouching = False
                    base.has_sword = False
                    if (any_action.is_playing() is False
                            and base.is_crouching is False):
                        base.is_idle = True

                elif (base.has_sword is False
                      and crouched_to_standing.is_playing() is False
                      and base.is_crouching is False):
                    base.has_sword = True
                    any_action_seq = player.actor_interval(anims[action],
                                                           playRate=self.base.actor_play_rate)
                    Sequence(any_action_seq).start()
                    base.is_crouching = False
                    base.has_sword = False
                    if any_action.is_playing() is False and base.has_sword is False:
                        base.is_idle = True

    def player_bow_action(self, player, key, anims, action):
        if (player and isinstance(anims, dict)
                and isinstance(action, str)
                and isinstance(key, str)):
            crouched_to_standing = player.get_anim_control(anims[self.crouched_to_standing_action])
            any_action = player.get_anim_control(anims[action])

            if self.kbd.keymap[key]:
                base.is_idle = False

                if (base.has_bow is False
                        and crouched_to_standing.is_playing() is False
                        and base.is_crouching is True):
                    base.is_standing = False
                    # TODO: Use blending for smooth transition between animations
                    # Do an animation sequence if player is crouched.
                    crouch_to_stand_seq = player.actor_interval(anims[self.crouched_to_standing_action],
                                                                playRate=self.base.actor_play_rate)
                    any_action_seq = player.actor_interval(anims[action],
                                                           playRate=self.base.actor_play_rate)
                    Sequence(crouch_to_stand_seq, any_action_seq).start()
                    base.is_crouching = False
                    base.has_bow = False
                    if (any_action.is_playing() is False
                            and base.is_crouching is False):
                        base.is_idle = True

                elif (base.has_bow is False
                      and crouched_to_standing.is_playing() is False
                      and base.is_crouching is False):
                    base.has_bow = True
                    any_action_seq = player.actor_interval(anims[action],
                                                           playRate=self.base.actor_play_rate)
                    Sequence(any_action_seq).start()
                    base.is_crouching = False
                    base.has_bow = False
                    if any_action.is_playing() is False and base.has_bow is False:
                        base.is_idle = True

    def player_tengri_action(self, player, key, anims, action):
        if (player and isinstance(anims, dict)
                and isinstance(action, str)
                and isinstance(key, str)):
            crouched_to_standing = player.get_anim_control(anims[self.crouched_to_standing_action])
            any_action = player.get_anim_control(anims[action])

            if self.kbd.keymap[key]:
                base.is_idle = False

                if (base.has_tengri is False
                        and crouched_to_standing.is_playing() is False
                        and base.is_crouching is True):
                    base.is_standing = False
                    # TODO: Use blending for smooth transition between animations
                    # Do an animation sequence if player is crouched.
                    crouch_to_stand_seq = player.actor_interval(anims[self.crouched_to_standing_action],
                                                                playRate=self.base.actor_play_rate)
                    any_action_seq = player.actor_interval(anims[action],
                                                           playRate=self.base.actor_play_rate)
                    Sequence(crouch_to_stand_seq, any_action_seq).start()
                    base.is_crouching = False
                    base.has_tengri = False
                    if (any_action.is_playing() is False
                            and base.is_crouching is False):
                        base.is_idle = True

                elif (base.has_tengri is False
                      and crouched_to_standing.is_playing() is False
                      and base.is_crouching is False):
                    base.has_tengri = True
                    any_action_seq = player.actor_interval(anims[action],
                                                           playRate=self.base.actor_play_rate)
                    Sequence(any_action_seq).start()
                    base.is_crouching = False
                    base.has_tengri = False
                    if any_action.is_playing() is False and base.has_tengri is False:
                        base.is_idle = True

    def player_umai_action(self, player, key, anims, action):
        if (player and isinstance(anims, dict)
                and isinstance(action, str)
                and isinstance(key, str)):
            crouched_to_standing = player.get_anim_control(anims[self.crouched_to_standing_action])
            any_action = player.get_anim_control(anims[action])

            if self.kbd.keymap[key]:
                base.is_idle = False

                if (base.has_umai is False
                        and crouched_to_standing.is_playing() is False
                        and base.is_crouching is True):
                    base.is_standing = False
                    # TODO: Use blending for smooth transition between animations
                    # Do an animation sequence if player is crouched.
                    crouch_to_stand_seq = player.actor_interval(anims[self.crouched_to_standing_action],
                                                                playRate=self.base.actor_play_rate)
                    any_action_seq = player.actor_interval(anims[action],
                                                           playRate=self.base.actor_play_rate)
                    Sequence(crouch_to_stand_seq, any_action_seq).start()
                    base.is_crouching = False
                    base.has_umai = False
                    if (any_action.is_playing() is False
                            and base.is_crouching is False):
                        base.is_idle = True

                elif (base.has_umai is False
                      and crouched_to_standing.is_playing() is False
                      and base.is_crouching is False):
                    base.has_umai = True
                    any_action_seq = player.actor_interval(anims[action], playRate=self.base.actor_play_rate)
                    Sequence(any_action_seq).start()
                    base.is_crouching = False
                    base.has_umai = False
                    if any_action.is_playing() is False and base.has_umai is False:
                        base.is_idle = True
