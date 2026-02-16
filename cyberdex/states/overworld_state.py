import pygame
import random
from engine.base_state import BaseState


class OverworldVirus:
    def __init__(self, zone_rect, walls):
        self.size = 32
        self.zone = zone_rect
        self.walls = walls
        self.speed = 100

        self.pos = pygame.Vector2(
            random.randint(zone_rect.left, zone_rect.right - self.size),
            random.randint(zone_rect.top, zone_rect.bottom - self.size)
        )

        self.point_a = pygame.Vector2(self.pos)
        self.point_b = pygame.Vector2(
            random.randint(zone_rect.left, zone_rect.right - self.size),
            random.randint(zone_rect.top, zone_rect.bottom - self.size)
        )

        self.target = self.point_b

    def update(self, dt):
        direction = self.target - self.pos
        if direction.length() > 0:
            direction = direction.normalize()

        self.pos += direction * self.speed * dt

        if self.pos.distance_to(self.target) < 5:
            self.target = self.point_a if self.target == self.point_b else self.point_b

        self.pos.x = max(self.zone.left, min(self.pos.x, self.zone.right - self.size))
        self.pos.y = max(self.zone.top, min(self.pos.y, self.zone.bottom - self.size))

    def draw(self, screen, camera):
        rect = pygame.Rect(
            self.pos.x - camera.x,
            self.pos.y - camera.y,
            self.size,
            self.size
        )
        pygame.draw.rect(screen, (150, 0, 150), rect)
        pygame.draw.rect(screen, (220, 50, 220), rect.inflate(-8, -8))

    def get_rect(self):
        return pygame.Rect(self.pos.x, self.pos.y, self.size, self.size)


class OverworldState(BaseState):
    def __init__(self, game):
        super().__init__(game)

        self.screen_width = 1280
        self.screen_height = 720

        self.world_width = 3000
        self.world_height = 2000

        self.player_size = 32
        self.player_pos = pygame.Vector2(1500, 1000)
        self.player_speed = 300

        self.camera = pygame.Vector2(0, 0)

        self.walls = []
        self.trees = []
        self.create_scenery()

        self.infected_zones = []
        self.create_infected_zones()

        self.viruses = []
        self.spawn_viruses()

        self.steps_in_zone = 0
        self.encounter_threshold = 200
        self.encounter_cooldown = 0

    def create_scenery(self):
        for _ in range(20):
            self.trees.append(
                pygame.Rect(random.randint(0, 2800), random.randint(0, 1800), 64, 64)
            )

    def create_infected_zones(self):
        self.infected_zones.append(pygame.Rect(800, 300, 400, 400))
        self.infected_zones.append(pygame.Rect(1800, 1200, 500, 300))

    def spawn_viruses(self):
        for zone in self.infected_zones:
            self.viruses.append(OverworldVirus(zone, self.walls))

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                from states.menu_state import MenuState
                self.game.state_manager.change_state(MenuState(self.game))

    def update(self, dt):
        keys = pygame.key.get_pressed()
        direction = pygame.Vector2(0, 0)

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            direction.y -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            direction.y += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            direction.x -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            direction.x += 1

        if direction.length() > 0:
            direction = direction.normalize()

        movement = direction * self.player_speed * dt
        self.player_pos += movement

        player_rect = pygame.Rect(self.player_pos.x, self.player_pos.y, self.player_size, self.player_size)

        for tree in self.trees:
            if player_rect.colliderect(tree):
                self.player_pos -= movement

        self.player_pos.x = max(0, min(self.player_pos.x, self.world_width - self.player_size))
        self.player_pos.y = max(0, min(self.player_pos.y, self.world_height - self.player_size))

        player_rect = pygame.Rect(self.player_pos.x, self.player_pos.y, self.player_size, self.player_size)

        in_zone = any(player_rect.colliderect(zone) for zone in self.infected_zones)

        if in_zone and movement.length() > 0:
            self.steps_in_zone += movement.length()
            if self.steps_in_zone >= self.encounter_threshold:
                self.steps_in_zone = 0
                from states.battle_state import BattleState
                self.game.state_manager.change_state(BattleState(self.game))
                return

        for virus in self.viruses:
            virus.update(dt)

        for virus in self.viruses:
            if player_rect.colliderect(virus.get_rect()):
                from states.battle_state import BattleState
                self.game.state_manager.change_state(BattleState(self.game))
                return

        self.camera.x = self.player_pos.x - self.screen_width // 2
        self.camera.y = self.player_pos.y - self.screen_height // 2

        self.camera.x = max(0, min(self.camera.x, self.world_width - self.screen_width))
        self.camera.y = max(0, min(self.camera.y, self.world_height - self.screen_height))

    def render(self, screen):
        screen.fill((20, 120, 60))

        for tree in self.trees:
            pygame.draw.rect(
                screen,
                (0, 80, 0),
                pygame.Rect(tree.x - self.camera.x, tree.y - self.camera.y, tree.width, tree.height)
            )

        for zone in self.infected_zones:
            pygame.draw.rect(
                screen,
                (100, 0, 100),
                pygame.Rect(zone.x - self.camera.x, zone.y - self.camera.y, zone.width, zone.height)
            )

        for virus in self.viruses:
            virus.draw(screen, self.camera)

        pygame.draw.rect(
            screen,
            (0, 0, 255),
            pygame.Rect(self.player_pos.x - self.camera.x,
                        self.player_pos.y - self.camera.y,
                        self.player_size,
                        self.player_size)
        )
