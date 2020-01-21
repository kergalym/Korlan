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
            player_asset_path = "{0}/Assets/Actors/Korlan/{1}.egg".format(self.path,
                                                                          self.set_player(self.player_asset_name))
            if exists(player_asset_path) and isfile(player_asset_path):
                return player_asset_path
            else:
                logging.critical("\nI'm trying to load Korlan player, but there is no suitable player asset. "
                                 "\nNo suitable player asset found!"
                                 "\nPlayer path: {0}/Assets/Actors/Korlan/".format(self.path))
                sys_exit("\nSomething is getting wrong. Please, check the game log first")

    def set_player(self, player_asset_name):
        if (isinstance(player_asset_name, str) and
                player_asset_name == 'Korlan'):
            self.player_asset_name = player_asset_name
            return self.player_asset_name
