import pygame
from engine.base_state import BaseState

class MenuState(BaseState):
    def __init__(self, game):
        super().__init__(game)
        self.font = pygame.font.SysFont("arial", 50)

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    # Import here to avoid circular import
                    from states.overworld_state import OverworldState
                    self.game.state_manager.change_state(OverworldState(self.game))

    def update(self, dt):
        pass

    def render(self, screen):
        screen.fill((15, 15, 25))
        text = self.font.render("Press ENTER to Start", True, (0, 255, 255))
        screen.blit(text, (400, 350))
