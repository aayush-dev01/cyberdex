import pygame
from engine.base_state import BaseState

class OverworldState(BaseState):
    def __init__(self, game):
        super().__init__(game)

        self.font = pygame.font.SysFont("arial", 30)

        # Screen size
        self.screen_width = 1280
        self.screen_height = 720

        # Tile settings
        self.tile_size = 64
        self.grid_color = (30, 50, 70)

        # Player properties
        self.player_size = 40
        self.player_color = (0, 255, 200)
        self.player_pos = pygame.Vector2(640, 360)
        self.player_speed = 300  # pixels per second

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    from states.menu_state import MenuState
                    self.game.state_manager.change_state(MenuState(self.game))

    def update(self, dt):
        keys = pygame.key.get_pressed()
        direction = pygame.Vector2(0, 0)

        # Vertical movement
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            direction.y -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            direction.y += 1

        # Horizontal movement
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            direction.x -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            direction.x += 1

        if direction.length() > 0:
            direction = direction.normalize()

        self.player_pos += direction * self.player_speed * dt

        # Screen boundaries
        self.player_pos.x = max(0, min(self.player_pos.x, self.screen_width - self.player_size))
        self.player_pos.y = max(0, min(self.player_pos.y, self.screen_height - self.player_size))

    def render(self, screen):
        screen.fill((15, 30, 45))

        # Draw tile grid
        for x in range(0, self.screen_width, self.tile_size):
            pygame.draw.line(screen, self.grid_color, (x, 0), (x, self.screen_height))
        for y in range(0, self.screen_height, self.tile_size):
            pygame.draw.line(screen, self.grid_color, (0, y), (self.screen_width, y))

        # Draw player
        pygame.draw.rect(
            screen,
            self.player_color,
            (self.player_pos.x, self.player_pos.y, self.player_size, self.player_size)
        )

        # Instruction text
        text = self.font.render("WASD / Arrows to Move | ESC to Menu", True, (255, 255, 255))
        screen.blit(text, (20, 20))


