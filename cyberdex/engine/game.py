import pygame
from engine.state_manager import StateManager
from states.menu_state import MenuState

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((1280, 720))
        pygame.display.set_caption("CyberDex: Infected Protocol")
        self.clock = pygame.time.Clock()
        self.running = True

        self.state_manager = StateManager(MenuState(self))

    def run(self):
        while self.running:
            dt = self.clock.tick(60) / 1000
            events = pygame.event.get()

            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False

            self.state_manager.handle_events(events)
            self.state_manager.update(dt)
            self.state_manager.render(self.screen)

            pygame.display.flip()

        pygame.quit()
