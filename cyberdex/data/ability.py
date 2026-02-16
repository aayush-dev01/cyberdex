"""
CyberDex - Ability System
Defines all battle abilities and combat logic.
"""

import random


class Ability:
    def __init__(self,
                 name,
                 power,
                 ability_type,
                 accuracy=1.0,
                 crit_rate=0.1,
                 status_effect=None,
                 status_chance=0.0):
        """
        :param name: Display name
        :param power: Base damage power
        :param ability_type: Type string (malware, worm, ai, etc.)
        :param accuracy: 0.0 - 1.0
        :param crit_rate: Base critical chance
        :param status_effect: Optional status name
        :param status_chance: 0.0 - 1.0
        """
        self.name = name
        self.power = power
        self.ability_type = ability_type
        self.accuracy = accuracy
        self.crit_rate = crit_rate
        self.status_effect = status_effect
        self.status_chance = status_chance

    # ==========================================================
    # CORE DAMAGE CALCULATION
    # ==========================================================

    def calculate_damage(self,
                         attacker,
                         defender,
                         command_bonus=None):
        """
        Calculates final damage including:
        - Base formula
        - Critical
        - Type bonus
        - Corruption overclock
        - Command multiplier
        """

        # Base damage formula
        base = ((attacker.attack / defender.defense) * self.power)

        # Random variance
        variance = random.uniform(0.9, 1.1)
        base *= variance

        # Critical hit
        crit_chance = self.crit_rate
        if command_bonus:
            crit_chance += command_bonus.get("crit_boost", 0)

        is_critical = random.random() < crit_chance
        if is_critical:
            base *= 1.5

        # Type bonus
        if attacker.virus_type == self.ability_type:
            base *= 1.2  # Same-type bonus

        # Corruption overclock bonus
        if attacker.is_overclocked():
            base *= 1.25

        # Command bonus damage multiplier
        if command_bonus:
            base *= command_bonus.get("damage_multiplier", 1.0)

        return int(base), is_critical

    # ==========================================================
    # STATUS APPLICATION
    # ==========================================================

    def try_apply_status(self, defender, command_bonus=None):
        if not self.status_effect:
            return False

        chance = self.status_chance

        if command_bonus:
            chance += command_bonus.get("status_boost", 0)

        if random.random() < chance:
            defender.status = self.status_effect
            return True

        return False


# ==========================================================
# ABILITY DATABASE
# ==========================================================

ABILITY_DATABASE = {
    "data_pulse": Ability(
        name="Data Pulse",
        power=25,
        ability_type="ai",
        accuracy=0.95,
        crit_rate=0.1
    ),

    "packet_storm": Ability(
        name="Packet Storm",
        power=35,
        ability_type="worm",
        accuracy=0.85,
        crit_rate=0.15
    ),

    "corrupt_burst": Ability(
        name="Corrupt Burst",
        power=30,
        ability_type="malware",
        accuracy=0.9,
        crit_rate=0.1,
        status_effect="corrupted",
        status_chance=0.2
    ),

    "lag_spike": Ability(
        name="Lag Spike",
        power=20,
        ability_type="worm",
        accuracy=0.95,
        crit_rate=0.05,
        status_effect="lagged",
        status_chance=0.25
    ),

    "overheat_injection": Ability(
        name="Overheat Injection",
        power=40,
        ability_type="ransomware",
        accuracy=0.8,
        crit_rate=0.2,
        status_effect="burned",
        status_chance=0.3
    )
}


# ==========================================================
# HELPER
# ==========================================================

def get_ability(name):
    """
    Safe ability fetch.
    Accepts:
        "data_pulse"
        "Data Pulse"
    """
    key = name.lower().replace(" ", "_")
    return ABILITY_DATABASE.get(key)

