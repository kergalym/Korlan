"""
BSD 3-Clause License

Copyright (c) 2019, Galym Kerimbekov
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its
   contributors may be used to endorse or promote products derived from
   this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
import logging
from os import listdir
from os.path import isdir, join


class Sound:
    def __init__(self):
        self.theme = "Assets/Sounds/Misc/theme.ogg"
        self.logging = logging.basicConfig(filename="critical.log", level=logging.CRITICAL)

    def assets_database_constructor(self, path, parent_path, sounds):
        if (path and parent_path and sounds
                and isdir(path) and isdir(parent_path)
                and isinstance(sounds, dict)):
            assets_dir = listdir(path)

            for i, v in enumerate(assets_dir):
                j = join(path, v)

                sounds[i] = j

            for key, val in sounds:
                with open("{}/Sounds.prc".format(parent_path), 'w') as f:
                    f.write("{}{}".format(sounds[key], val))

            return 0
        else:
            return 1

    def openal_mgr(self, sh_base, path):
        if sh_base and isinstance(path, str):
            sh_base.enableAllAudio()
            sh_base.enableMusic(True)
            sh_base.enableSoundEffects(True)

            misc_sounds = {}
            player_sounds = {}
            world_sounds = {}

            if isdir(path):
                self.assets_database_constructor('Sounds/Misc', path, misc_sounds)
                self.assets_database_constructor('Sounds/Player_sounds', path, player_sounds)
                self.assets_database_constructor('Sounds/World', path, world_sounds)
            else:
                self.logging.critical("CRITICAL: {} not found".format(path))

        m_sound = sh_base.loader.loadSfx("{}/{}".format(path, self.theme))
        # TODO: do something with them
        sfxMgr = sh_base.sfxManagerList[0]
        musicMgr = sh_base.musicManager

        if m_sound.status() == m_sound.PLAYING:
            m_sound.stop()
