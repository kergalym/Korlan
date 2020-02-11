import logging


class Sound:
    def __init__(self):
        self.base = base
        self.game_dir = base.game_dir
        self.logging = logging
        self.logging.basicConfig(filename="critical.log", level=logging.CRITICAL)

    def openal_mgr(self):
        self.base.enable_all_audio()
        self.base.enable_music(True)
        self.base.enable_sound_effects(True)

        sounds = self.base.collect_sounds()

        if sounds and isinstance(sounds, dict):
            print(sounds)
            m_sound = self.base.loader.load_sfx(sounds["theme"])
            # TODO: do something with them
            sfx_mgr = self.base.sfx_manager_list[0]
            music_mgr = self.base.music_manager

            if m_sound.status() != m_sound.PLAYING:
                m_sound.play()
        else:
            self.logging.critical("CRITICAL: Sound files not found")

