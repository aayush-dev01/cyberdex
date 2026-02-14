import pygame
from engine.base_state import BaseState

class OverworldState(BaseState):
    def __init__(self, game):
        super().__init__(game)
        self.font = pygame.font.SysFont("arial", 40)

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # Import here to avoid circular import
                    from states.menu_state import MenuState
                    self.game.state_manager.change_state(MenuState(self.game))

    def update(self, dt):
        pass

    def render(self, screen):
        screen.fill((10, 40, 60))
        text = self.font.render("Overworld - Press ESC to return", True, (255, 255, 255))
        screen.blit(text, (300, 350))
