import logging


class Sound:
    def __init__(self):
        self.base = base
        self.game_dir = base.game_dir
        self.logging = logging
        self.logging.basicConfig(filename="critical.log", level=logging.CRITICAL)

        """ Walking and Attacking sounds """
        self._sound_walking = None
        self._sound_jumping = None

        self._sound_melee_01 = None
        self._sound_melee_02 = None
        self._sound_melee_deep_wound = None
        self._sound_melee_swing = None
        self._sound_melee_swish = None

        self._sound_kicking_01 = None
        self._sound_kicking_02 = None
        self._sound_kicking_03 = None
        self._sound_kicking_04 = None
        self._sound_kicking_05 = None
        self._sound_kicking_06 = None
        self._sound_kicking_07 = None
        self._sound_kicking_08 = None
        self._sound_kicking_09 = None

        self._sound_punching_01 = None
        self._sound_punching_02 = None
        self._sound_punching_03 = None
        self._sound_punching_04 = None
        self._sound_punching_05 = None
        self._sound_punching_06 = None
        self._sound_punching_07 = None
        self._sound_punching_08 = None
        self._sound_punching_09 = None

        self._sound_using_item = None
        self._sound_picking_item = None

        """ Bow and Arrows sounds """
        self._sound_bow_charge = None
        self._sound_bow_release = None
        self._sound_arrow_hit = None
        self._sound_arrow_hit_metal = None
        self._sound_arrow_hit_rock = None

        """ Female sounds """
        self._sound_female_voice_hurting_01 = None
        self._sound_female_voice_hurting_02 = None
        self._sound_female_voice_hurting_03 = None

        self._sound_female_voice_attacking = None
        self._sound_female_voice_dying_01 = None
        self._sound_female_voice_dying_02 = None
        self._sound_female_voice_dying_03 = None

        """ Male sounds """
        self._sound_male_voice_hurting_01 = None
        self._sound_male_voice_hurting_02 = None
        self._sound_male_voice_hurting_03 = None

        self._sound_male_voice_attacking = None
        self._sound_male_voice_dying_01 = None
        self._sound_male_voice_dying_02 = None
        self._sound_male_voice_dying_03 = None

        """ Misc interacting sounds """

    def openal_mgr(self):
        """ Function    : openal_mgr

            Description : OpenAL manager

            Input       : None

            Output      : None

            Return      : None
        """
        self.base.enable_all_audio()
        self.base.enable_music(True)
        self.base.enable_sound_effects(True)

        sounds = self.base.sounds_collector()

        if sounds and isinstance(sounds, dict):
            self.base.sound_gui_click = self.base.loader.load_sfx(sounds.get('zapsplat_button_click'))
            self.base.sound_sfx_nature = self.base.loader.load_sfx(sounds.get('forest birds'))

            # TODO: do something with them
            # m_sound = self.base.loader.load_sfx(sounds["theme"])
            # sfx_mgr = self.base.sfx_manager_list[0]
            # music_mgr = self.base.music_manager

            # if m_sound.status() != m_sound.PLAYING:
                # m_sound.play()
        else:
            self.logging.critical("CRITICAL: Sound files not found")

    def load_sounds(self):
        sounds = self.base.sounds_collector()

        self._sound_walking = self.base.loader.load_sfx(sounds["walking_leather_armour"])
        self._sound_jumping = self.base.loader.load_sfx(sounds["jumping"])

        self._sound_melee_01 = self.base.loader.load_sfx(sounds["melee_sword_1"])
        self._sound_melee_02 = self.base.loader.load_sfx(sounds["melee_sword_2"])
        self._sound_melee_deep_wound = self.base.loader.load_sfx(sounds["melee_deep_wound"])
        self._sound_melee_swing = self.base.loader.load_sfx(sounds["melee_swing"])
        self._sound_melee_swish = self.base.loader.load_sfx(sounds["melee_swish"])

        self._sound_bow_charge = self.base.loader.load_sfx(sounds["bow_charge"])
        self._sound_bow_release = self.base.loader.load_sfx(sounds["bow_release"])
        self._sound_arrow_hit = self.base.loader.load_sfx(sounds["arrow_hit"])
        self._sound_arrow_hit_metal = self.base.loader.load_sfx(sounds["arrow_metal"])
        self._sound_arrow_hit_rock = self.base.loader.load_sfx(sounds["arrow_rock"])

        self._sound_kicking_01 = self.base.loader.load_sfx(sounds["kick_01"])
        self._sound_kicking_02 = self.base.loader.load_sfx(sounds["kick_02"])
        self._sound_kicking_03 = self.base.loader.load_sfx(sounds["kick_03"])
        self._sound_kicking_04 = self.base.loader.load_sfx(sounds["kick_04"])
        self._sound_kicking_05 = self.base.loader.load_sfx(sounds["kick_05"])
        self._sound_kicking_06 = self.base.loader.load_sfx(sounds["kick_06"])
        self._sound_kicking_07 = self.base.loader.load_sfx(sounds["kick_07"])
        self._sound_kicking_08 = self.base.loader.load_sfx(sounds["kick_08"])
        self._sound_kicking_09 = self.base.loader.load_sfx(sounds["kick_09"])

        self._sound_punching_01 = self.base.loader.load_sfx(sounds["punch_01"])
        self._sound_punching_02 = self.base.loader.load_sfx(sounds["punch_02"])
        self._sound_punching_03 = self.base.loader.load_sfx(sounds["punch_03"])
        self._sound_punching_04 = self.base.loader.load_sfx(sounds["punch_04"])
        self._sound_punching_05 = self.base.loader.load_sfx(sounds["punch_05"])
        self._sound_punching_06 = self.base.loader.load_sfx(sounds["punch_06"])
        self._sound_punching_07 = self.base.loader.load_sfx(sounds["punch_07"])
        self._sound_punching_08 = self.base.loader.load_sfx(sounds["punch_08"])
        self._sound_punching_09 = self.base.loader.load_sfx(sounds["punch_09"])

        self._sound_using_item = self.base.loader.load_sfx(sounds["grab_pickup"])
        self._sound_picking_item = self.base.loader.load_sfx(sounds["grab_pickup"])

        self._sound_female_voice_hurting_01 = self.base.loader.load_sfx(sounds["voice_female_pain_01"])
        self._sound_female_voice_hurting_02 = self.base.loader.load_sfx(sounds["voice_female_pain_02"])
        self._sound_female_voice_hurting_03 = self.base.loader.load_sfx(sounds["voice_female_pain_03"])

        self._sound_female_voice_attacking = self.base.loader.load_sfx(sounds["voice_female_attack_01"])

        self._sound_female_voice_dying_01 = self.base.loader.load_sfx(sounds["walk_new2"])
        self._sound_female_voice_dying_02 = self.base.loader.load_sfx(sounds["walk_new2"])
        self._sound_female_voice_dying_03 = self.base.loader.load_sfx(sounds["walk_new2"])

        self._sound_male_voice_hurting_01 = self.base.loader.load_sfx(sounds["voice_male_pain_01"])
        self._sound_male_voice_hurting_02 = self.base.loader.load_sfx(sounds["voice_male_pain_02"])
        self._sound_male_voice_hurting_03 = self.base.loader.load_sfx(sounds["voice_male_pain_03"])

        self._sound_male_voice_attacking = self.base.loader.load_sfx(sounds["voice_male_battle_shout_short_01"])

        self._sound_male_voice_dying_01 = self.base.loader.load_sfx(sounds["walk_new2"])
        self._sound_male_voice_dying_02 = self.base.loader.load_sfx(sounds["walk_new2"])
        self._sound_male_voice_dying_03 = self.base.loader.load_sfx(sounds["walk_new2"])

    def play_walking(self):
        self._sound_walking.set_play_rate(1.3)
        self._sound_walking.set_loop(True)
        self._sound_walking.play()

    def stop_walking(self):
        self._sound_walking.set_loop(False)
        self._sound_walking.stop()

    def play_turning(self):
        self._sound_walking.set_play_rate(1.3)
        self._sound_walking.set_loop(True)
        self._sound_walking.play()

    def stop_turning(self):
        self._sound_walking.set_loop(False)
        self._sound_walking.stop()

    def play_running(self):
        self._sound_walking.set_play_rate(1.5)
        self._sound_walking.set_loop(True)
        self._sound_walking.play()

    def stop_running(self):
        self._sound_walking.set_loop(False)
        self._sound_walking.stop()

    def play_jump(self):
        if self._sound_jumping.status() != self._sound_jumping.PLAYING:
            self._sound_jumping.play()
        else:
            self._sound_jumping.stop()

    def play_melee(self):
        if self._sound_melee_01.status() != self._sound_melee_01.PLAYING:
            self._sound_melee_01.play()
        else:
            self._sound_melee_01.stop()

    def play_bow_charge(self):
        self._sound_bow_charge.play()

    def stop_bow_charge(self):
        self._sound_bow_charge.stop()

    def play_bow_release(self):
        if self._sound_bow_release.status() != self._sound_bow_release.PLAYING:
            self._sound_bow_release.play()
        else:
            self._sound_bow_release.stop()

    def play_arrow_hit(self):
        if self._sound_arrow_hit.status() != self._sound_arrow_hit.PLAYING:
            self._sound_arrow_hit.play()
        else:
            self._sound_arrow_hit.stop()

        if self._sound_arrow_hit_metal.status() != self._sound_arrow_hit_metal.PLAYING:
            self._sound_arrow_hit_metal.play()
        else:
            self._sound_arrow_hit_metal.stop()

        if self._sound_arrow_hit_rock.status() != self._sound_arrow_hit_rock.PLAYING:
            self._sound_arrow_hit_rock.play()
        else:
            self._sound_arrow_hit_rock.stop()

    def play_kicking(self):
        if self._sound_kicking_01.status() != self._sound_kicking_01.PLAYING:
            self._sound_kicking_01.play()
        else:
            self._sound_kicking_01.stop()

        if self._sound_kicking_02.status() != self._sound_kicking_02.PLAYING:
            self._sound_kicking_02.play()
        else:
            self._sound_kicking_02.stop()

        if self._sound_kicking_03.status() != self._sound_kicking_03.PLAYING:
            self._sound_kicking_03.play()
        else:
            self._sound_kicking_03.stop()

        if self._sound_kicking_04.status() != self._sound_kicking_04.PLAYING:
            self._sound_kicking_04.play()
        else:
            self._sound_kicking_04.stop()

        if self._sound_kicking_05.status() != self._sound_kicking_05.PLAYING:
            self._sound_kicking_05.play()
        else:
            self._sound_kicking_05.stop()

        if self._sound_kicking_06.status() != self._sound_kicking_06.PLAYING:
            self._sound_kicking_06.play()
        else:
            self._sound_kicking_06.stop()

        if self._sound_kicking_07.status() != self._sound_kicking_07.PLAYING:
            self._sound_kicking_07.play()
        else:
            self._sound_kicking_07.stop()

        if self._sound_kicking_08.status() != self._sound_kicking_08.PLAYING:
            self._sound_kicking_08.play()
        else:
            self._sound_kicking_08.stop()

        if self._sound_kicking_09.status() != self._sound_kicking_09.PLAYING:
            self._sound_kicking_09.play()
        else:
            self._sound_kicking_09.stop()

    def play_punching(self):
        if self._sound_punching_01.status() != self._sound_punching_01.PLAYING:
            self._sound_punching_01.play()
        else:
            self._sound_punching_01.stop()

        if self._sound_punching_02.status() != self._sound_punching_02.PLAYING:
            self._sound_punching_02.play()
        else:
            self._sound_punching_02.stop()

        if self._sound_punching_03.status() != self._sound_punching_03.PLAYING:
            self._sound_punching_03.play()
        else:
            self._sound_punching_03.stop()

        if self._sound_punching_04.status() != self._sound_punching_04.PLAYING:
            self._sound_punching_04.play()
        else:
            self._sound_punching_04.stop()

        if self._sound_punching_05.status() != self._sound_punching_05.PLAYING:
            self._sound_punching_05.play()
        else:
            self._sound_punching_05.stop()

        if self._sound_punching_06.status() != self._sound_punching_06.PLAYING:
            self._sound_punching_06.play()
        else:
            self._sound_punching_06.stop()

        if self._sound_punching_07.status() != self._sound_punching_07.PLAYING:
            self._sound_punching_07.play()
        else:
            self._sound_punching_07.stop()

        if self._sound_punching_08.status() != self._sound_punching_08.PLAYING:
            self._sound_punching_08.play()
        else:
            self._sound_punching_08.stop()

        if self._sound_punching_09.status() != self._sound_punching_09.PLAYING:
            self._sound_punching_09.play()
        else:
            self._sound_punching_09.stop()

    def play_female_hurting(self):
        if self._sound_female_voice_hurting_01.status() != self._sound_female_voice_hurting_01.PLAYING:
            self._sound_female_voice_hurting_01.play()
        else:
            self._sound_female_voice_hurting_01.stop()

        if self._sound_female_voice_hurting_02.status() != self._sound_female_voice_hurting_02.PLAYING:
            self._sound_female_voice_hurting_02.play()
        else:
            self._sound_female_voice_hurting_02.stop()

        if self._sound_female_voice_hurting_03.status() != self._sound_female_voice_hurting_03.PLAYING:
            self._sound_female_voice_hurting_03.play()
        else:
            self._sound_female_voice_hurting_03.stop()

    def play_female_attacking(self):
        if self._sound_female_voice_attacking.status() != self._sound_female_voice_attacking.PLAYING:
            self._sound_female_voice_attacking.play()
        else:
            self._sound_female_voice_attacking.stop()

    def play_male_hurting(self):
        if self._sound_male_voice_hurting_01.status() != self._sound_male_voice_hurting_01.PLAYING:
            self._sound_male_voice_hurting_01.play()
        else:
            self._sound_male_voice_hurting_01.stop()

        if self._sound_male_voice_hurting_02.status() != self._sound_male_voice_hurting_02.PLAYING:
            self._sound_male_voice_hurting_02.play()
        else:
            self._sound_male_voice_hurting_02.stop()

        if self._sound_male_voice_hurting_03.status() != self._sound_male_voice_hurting_03.PLAYING:
            self._sound_male_voice_hurting_03.play()
        else:
            self._sound_male_voice_hurting_03.stop()

    def play_male_attacking(self):
        if self._sound_male_voice_attacking.status() != self._sound_male_voice_attacking.PLAYING:
            self._sound_male_voice_attacking.play()
        else:
            self._sound_male_voice_attacking.stop()

    def play_female_dying(self):
        if self._sound_female_voice_dying_01.status() != self._sound_female_voice_dying_01.PLAYING:
            self._sound_female_voice_dying_01.play()
        else:
            self._sound_female_voice_dying_01.stop()

        if self._sound_female_voice_dying_02.status() != self._sound_female_voice_dying_02.PLAYING:
            self._sound_female_voice_dying_02.play()
        else:
            self._sound_female_voice_dying_02.stop()

        if self._sound_female_voice_dying_03.status() != self._sound_female_voice_dying_03.PLAYING:
            self._sound_female_voice_dying_03.play()
        else:
            self._sound_female_voice_dying_03.stop()

    def play_male_dying(self):
        if self._sound_male_voice_dying_01.status() != self._sound_male_voice_dying_01.PLAYING:
            self._sound_male_voice_dying_01.play()
        else:
            self._sound_male_voice_dying_01.stop()

        if self._sound_male_voice_dying_02.status() != self._sound_male_voice_dying_02.PLAYING:
            self._sound_male_voice_dying_02.play()
        else:
            self._sound_male_voice_dying_02.stop()

        if self._sound_male_voice_dying_03.status() != self._sound_male_voice_dying_03.PLAYING:
            self._sound_male_voice_dying_03.play()
        else:
            self._sound_male_voice_dying_03.stop()

