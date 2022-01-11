from Settings.menu_settings import MenuSettings
from Settings.UI.unloading_ui import UnloadingUI


class ExitGame(MenuSettings):
    def __init__(self):
        MenuSettings.__init__(self)
        self.base = base
        self.unloading_ui = UnloadingUI()

    def do_accepted_event(self):
        """ Function    : do_accepted_event

            Description : Do accepted event of exiting from game

            Input       : None

            Output      : None

            Return      : None
        """
        self.unloading_ui.start_unloading(type="exit_from_game")
        if self.base.shared_functions['unload_pause_menu']:
            unload_pause_menu = self.base.shared_functions['unload_pause_menu']
            unload_pause_menu()
