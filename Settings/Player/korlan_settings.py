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
from os.path import isfile, exists
from sys import exit as sys_exit


class Player:
    def __init__(self):
        self.path = None
        self.player_asset_name = None

        self.logging = logging
        self.logging.basicConfig(filename="critical.log", level=logging.CRITICAL)

    def set_player_path(self, path):
        if path:
            self.path = path
            player_asset_path = "{0}/Assets/Models/Korlan/{1}.egg".format(self.path,
                                                                          self.set_player(self.player_asset_name))
            if exists(player_asset_path) and isfile(player_asset_path):
                return player_asset_path
            else:
                logging.critical("\nI'm trying to load Korlan player, but there is no suitable player asset. "
                                 "\nNo suitable player asset found!"
                                 "\nPlayer path: {0}/Assets/Models/Korlan/".format(self.path))
                sys_exit("\nSomething is getting wrong. Please, check the game log first")

    def set_player(self, player_asset_name):
        if (isinstance(player_asset_name, str) and
                player_asset_name == 'Korlan'):
            self.player_asset_name = player_asset_name
            return self.player_asset_name
