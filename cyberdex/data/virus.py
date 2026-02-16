"""
CyberDex - Virus Entity
Full RPG creature system.
"""

import math


class Virus:
    def __init__(self, name, virus_type, tier,
                 level=1,
                 max_hp=100,
                 attack=20,
                 defense=15,
                 speed=10):

        self.name = name
        self.virus_type = virus_type
        self.tier = tier

        self.level = level
        self.exp = 0
        self.exp_to_next = self._calculate_exp_needed()

        self.base_max_hp = max_hp
        self.base_attack = attack
        self.base_defense = defense
        self.base_speed = speed

        self.max_hp = self._scale_stat(max_hp)
        self.attack = self._scale_stat(attack)
        self.defense = self._scale_stat(defense)
        self.speed = self._scale_stat(speed)

        self.current_hp = self.max_hp

        # Status
        self.status = None

        # Corruption
        self.corruption = 0
        self.max_corruption = 100

        # Abilities (list of ability names)
        self.abilities = []

    # ===============================
    # STAT SCALING
    # ===============================

    def _scale_stat(self, base):
        return int(base + (self.level * 2.5))

    def _calculate_exp_needed(self):
        return int(50 * math.pow(self.level, 1.3))

    # ===============================
    # DAMAGE
    # ===============================

    def take_damage(self, amount):
        self.current_hp = max(0, self.current_hp - amount)
        self.add_corruption(amount * 0.3)

    def heal_full(self):
        self.current_hp = self.max_hp
        self.status = None
        self.corruption = 0

    def is_fainted(self):
        return self.current_hp <= 0

    # ===============================
    # EXPERIENCE
    # ===============================

    def gain_exp(self, amount):
        self.exp += amount
        leveled_up = False

        while self.exp >= self.exp_to_next:
            self.exp -= self.exp_to_next
            self.level += 1
            leveled_up = True
            self._level_up()

        return leveled_up

    def _level_up(self):
        self.exp_to_next = self._calculate_exp_needed()

        self.max_hp = self._scale_stat(self.base_max_hp)
        self.attack = self._scale_stat(self.base_attack)
        self.defense = self._scale_stat(self.base_defense)
        self.speed = self._scale_stat(self.base_speed)

        self.current_hp = self.max_hp

    # ===============================
    # CORRUPTION SYSTEM
    # ===============================

    def add_corruption(self, amount):
        self.corruption += amount
        if self.corruption > self.max_corruption:
            self.corruption = self.max_corruption

    def is_overclocked(self):
        return self.corruption >= self.max_corruption

    # ===============================
    # EVOLUTION HOOK
    # ===============================

    def can_evolve(self, evolution_data):
        if self.name not in evolution_data:
            return False
        required_level = evolution_data[self.name]["level"]
        return self.level >= required_level

    # ===============================
    # SAVE / LOAD SUPPORT
    # ===============================

    def to_dict(self):
        return {
            "name": self.name,
            "virus_type": self.virus_type,
            "tier": self.tier,
            "level": self.level,
            "exp": self.exp,
            "current_hp": self.current_hp,
            "corruption": self.corruption,
            "abilities": self.abilities
        }

    @staticmethod
    def from_dict(data):
        virus = Virus(
            data["name"],
            data["virus_type"],
            data["tier"],
            level=data["level"]
        )
        virus.exp = data["exp"]
        virus.current_hp = data["current_hp"]
        virus.corruption = data["corruption"]
        virus.abilities = data["abilities"]
        return virus
