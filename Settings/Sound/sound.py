import logging


class Sound:
    def __init__(self):
        self.base = base
        self.game_dir = base.game_dir
        self.logging = logging
        self.logging.basicConfig(filename="critical.log", level=logging.CRITICAL)

    def openal_mgr(self):
        self.base.enableAllAudio()
        self.base.enableMusic(True)
        self.base.enableSoundEffects(True)

        sounds = self.base.collect_sounds()

        if sounds and isinstance(sounds, dict):
            print(sounds)
            m_sound = self.base.loader.loadSfx(sounds["theme"])
            # TODO: do something with them
            sfxMgr = self.base.sfxManagerList[0]
            musicMgr = self.base.musicManager

            if m_sound.status() != m_sound.PLAYING:
                m_sound.play()
        else:
            self.logging.critical("CRITICAL: Sound files not found")

