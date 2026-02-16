"""
CyberDex - Battle State
Turn-based battle system with command bonuses.
"""

import pygame
import random
from config import *
from engine.base_state import BaseState
from engine.animation import FloatingText, ScreenShake
from systems.battle_system import BattleSystem
from systems.capture_system import CaptureSystem
from systems.command_bonus_system import CommandBonusSystem
from systems.save_system import SaveSystem
from data.ability import get_ability


class BattleState(BaseState):
    """Turn-based battle state."""

    def __init__(self):
        super().__init__()

        self.battle_system = BattleSystem()
        self.capture_system = CaptureSystem()
        self.command_system = CommandBonusSystem()

        # Battle data
        self.player_virus = None
        self.enemy_virus = None
        self.zone_id = None
        self.virus_entity = None
        self.is_random_encounter = False

        # State
        self.phase = "intro"
        self.selected_action = 0
        self.selected_ability = 0
        self.command_input = ""

        # Visual
        self.transition_timer = 0
        self.flash_timer = 0
        self.background = None

        # HP animation
        self.player_display_hp = 0
        self.enemy_display_hp = 0

        # Effects
        self.floating_texts = []
        self.screen_shake = None

        # Log
        self.battle_messages = []

    # ==========================================================
    # ENTER / EXIT
    # ==========================================================

    def enter(self, **kwargs):
        self.enemy_virus = kwargs.get("enemy_virus")
        self.zone_id = kwargs.get("zone_id")
        self.virus_entity = kwargs.get("virus_entity")
        self.is_random_encounter = kwargs.get("is_random", False)

        game_data = self.get_game_data()
        team = game_data.get("virus_team", [])

        if not team or not self.enemy_virus:
            self.state_manager.change_state("overworld")
            return

        # Pick first healthy virus
        for virus in team:
            if not virus.is_fainted():
                self.player_virus = virus
                break

        if not self.player_virus:
            self.state_manager.change_state("overworld")
            return

        self.player_display_hp = self.player_virus.current_hp
        self.enemy_display_hp = self.enemy_virus.current_hp

        self.transition_timer = BATTLE_TRANSITION_DURATION
        self.flash_timer = BATTLE_FLASH_DURATION
        self.phase = "intro"

        self._generate_background()
        self._add_message(f"Wild {self.enemy_virus.species.name} appeared!")

    # ==========================================================
    # UPDATE
    # ==========================================================

    def update(self, dt, events):

        # Transition phase
        if self.transition_timer > 0:
            self.transition_timer -= dt
            return

        if self.flash_timer > 0:
            self.flash_timer -= dt
            if self.flash_timer <= 0:
                self.phase = "select_action"
            return

        self._update_hp_animation(dt)
        self._update_effects(dt)

        if self.phase == "select_action":
            self._handle_action_selection(events)
        elif self.phase == "select_ability":
            self._handle_ability_selection(events)
        elif self.phase == "command_input":
            self._handle_command_input(events)
        elif self.phase == "execute":
            self._execute_player_turn()
        elif self.phase == "enemy_turn":
            self._execute_enemy_turn()
        elif self.phase == "victory":
            self._handle_victory(events)
        elif self.phase == "defeat":
            self._handle_defeat(events)

    # ==========================================================
    # ACTION SELECTION
    # ==========================================================

    def _handle_action_selection(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:

                if event.key in (pygame.K_UP, pygame.K_w):
                    self.selected_action = (self.selected_action - 1) % 4

                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    self.selected_action = (self.selected_action + 1) % 4

                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self._select_action()

    def _select_action(self):
        if self.selected_action == 0:
            self.phase = "select_ability"
            self.selected_ability = 0

        elif self.selected_action == 1:
            self._attempt_capture()

        elif self.selected_action == 2:
            self._add_message("Switch not implemented yet.")

        elif self.selected_action == 3:
            if self.is_random_encounter:
                self.state_manager.change_state("overworld")
            else:
                self._add_message("Cannot run from contact battle!")

    # ==========================================================
    # ABILITY
    # ==========================================================

    def _handle_ability_selection(self, events):
        abilities = self.player_virus.species.abilities

        for event in events:
            if event.type == pygame.KEYDOWN:

                if event.key in (pygame.K_UP, pygame.K_w):
                    self.selected_ability = (self.selected_ability - 1) % len(abilities)

                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    self.selected_ability = (self.selected_ability + 1) % len(abilities)

                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self.phase = "command_input"
                    self.command_input = ""

                elif event.key == pygame.K_ESCAPE:
                    self.phase = "select_action"

    # ==========================================================
    # COMMAND INPUT
    # ==========================================================

    def _handle_command_input(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_RETURN:
                    self.phase = "execute"

                elif event.key == pygame.K_ESCAPE:
                    self.command_input = ""
                    self.phase = "execute"

                elif event.key == pygame.K_BACKSPACE:
                    self.command_input = self.command_input[:-1]

                elif event.unicode.isprintable():
                    self.command_input += event.unicode

    # ==========================================================
    # PLAYER TURN
    # ==========================================================

    def _execute_player_turn(self):

        ability_name = self.player_virus.species.abilities[self.selected_ability]
        ability = get_ability(ability_name)

        if not ability:
            self.phase = "select_action"
            return

        command_bonus = None
        if self.command_input:
            command_bonus = self.command_system.parse_command(
                self.command_input, ability.name
            )

        is_critical = self.battle_system.check_critical_hit()

        damage = self.battle_system.calculate_damage(
            self.player_virus,
            self.enemy_virus,
            ability,
            is_critical,
        )

        self.enemy_virus.take_damage(damage)

        self._add_message(
            f"{self.player_virus.get_display_name()} used {ability.name}!"
        )

        if is_critical:
            self.screen_shake = ScreenShake()
            self._add_message("Critical hit!")

        if self.enemy_virus.is_fainted():
            self.phase = "victory"
            return

        self.phase = "enemy_turn"

    # ==========================================================
    # ENEMY TURN
    # ==========================================================

    def _execute_enemy_turn(self):

        ability_name = random.choice(self.enemy_virus.species.abilities)
        ability = get_ability(ability_name)

        if not ability:
            self.phase = "select_action"
            return

        damage = self.battle_system.calculate_damage(
            self.enemy_virus,
            self.player_virus,
            ability,
            False,
        )

        self.player_virus.take_damage(damage)

        self._add_message(
            f"Enemy {self.enemy_virus.species.name} used {ability.name}!"
        )

        if self.player_virus.is_fainted():
            self.phase = "defeat"
            return

        self.phase = "select_action"

    # ==========================================================
    # CAPTURE
    # ==========================================================

    def _attempt_capture(self):
        if self.capture_system.attempt_capture(self.enemy_virus):
            self._add_message("Capture successful!")
            self.phase = "victory"
        else:
            self._add_message("Capture failed!")
            self.phase = "enemy_turn"

    # ==========================================================
    # VICTORY / DEFEAT
    # ==========================================================

    def _handle_victory(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                self.state_manager.change_state("overworld")

    def _handle_defeat(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                self.state_manager.change_state("overworld")

    # ==========================================================
    # HELPERS
    # ==========================================================

    def _update_hp_animation(self, dt):
        speed = HP_BAR_ANIMATION_SPEED * dt

        if self.player_display_hp < self.player_virus.current_hp:
            self.player_display_hp = min(
                self.player_virus.current_hp,
                self.player_display_hp + speed,
            )
        elif self.player_display_hp > self.player_virus.current_hp:
            self.player_display_hp = max(
                self.player_virus.current_hp,
                self.player_display_hp - speed,
            )

        if self.enemy_display_hp < self.enemy_virus.current_hp:
            self.enemy_display_hp = min(
                self.enemy_virus.current_hp,
                self.enemy_display_hp + speed,
            )
        elif self.enemy_display_hp > self.enemy_virus.current_hp:
            self.enemy_display_hp = max(
                self.enemy_virus.current_hp,
                self.enemy_display_hp - speed,
            )

    def _update_effects(self, dt):
        for ft in self.floating_texts:
            ft.update(dt)
        self.floating_texts = [ft for ft in self.floating_texts if ft.alive]

        if self.screen_shake:
            self.screen_shake.update(dt)
            if not self.screen_shake.is_active():
                self.screen_shake = None

    def _add_message(self, message):
        self.battle_messages.append(message)
        if len(self.battle_messages) > 5:
            self.battle_messages.pop(0)

    # ==========================================================
    # RENDER
    # ==========================================================

    def render(self, screen):
        screen.blit(self.background, (0, 0))

        for ft in self.floating_texts:
            ft.render(screen)

        self._render_log(screen)

    def _generate_background(self):
        self.background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.background.fill((20, 10, 40))

    def _render_log(self, screen):
        y = 20
        for msg in self.battle_messages[-3:]:
            text = pygame.font.Font(None, 28).render(msg, True, COLOR_WHITE)
            screen.blit(text, (20, y))
            y += 30
