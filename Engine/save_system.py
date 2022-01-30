class SaveSystem:

    def __init__(self):
        self.base = base

    def get_game_data(self):
        pass

    def get_actor_state(self):
        pass

    def save_game(self):
        game_data = self.get_game_data()
        actor_states = self.get_actor_state()

        # todo: save all it to the file
