class StateManager:
    def __init__(self, initial_state):
        self.current_state = initial_state

    def change_state(self, new_state):
        self.current_state = new_state

    def handle_events(self, events):
        self.current_state.handle_events(events)

    def update(self, dt):
        self.current_state.update(dt)

    def render(self, screen):
        self.current_state.render(screen)
