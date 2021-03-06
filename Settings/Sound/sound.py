import logging


class Sound:
    def __init__(self):
        self.base = base
        self.game_dir = base.game_dir
        self.logging = logging
        self.logging.basicConfig(filename="critical.log", level=logging.CRITICAL)

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

