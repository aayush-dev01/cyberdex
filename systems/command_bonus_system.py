"""
CyberDex - Command Bonus System
Parses typed commands for hybrid combat bonuses.
"""

import re


class CommandBonusSystem:
    """
    Parses command strings and returns combat bonuses.

    Example valid commands:
        exec pulse -fast
        inject payload --burst
        propagate worm --rapid
    """

    def __init__(self):
        # Command keywords mapped by ability type
        self.type_keywords = {
            "ai": ["exec", "compute", "predict"],
            "worm": ["propagate", "spread", "replicate"],
            "malware": ["inject", "payload", "corrupt"],
            "ransomware": ["encrypt", "lock", "ransom"],
            "spyware": ["scan", "monitor", "trace"]
        }

    # ==========================================================
    # MAIN PARSER
    # ==========================================================

    def parse_command(self, command_string, ability_name):
        """
        Returns:
            {
                damage_multiplier,
                crit_boost,
                status_boost
            }
        OR
            None (invalid command)
        """

        if not command_string:
            return None

        command_string = command_string.strip().lower()

        # Basic syntax rule:
        # Must start with keyword + ability-related word
        words = command_string.split()

        if len(words) < 2:
            return None

        ability_type = self._infer_ability_type(ability_name)

        if ability_type not in self.type_keywords:
            return None

        valid_keywords = self.type_keywords[ability_type]

        # Check first word matches ability type category
        if words[0] not in valid_keywords:
            return None

        # Optional modifiers
        damage_bonus = 1.0
        crit_bonus = 0.0
        status_bonus = 0.0

        if "--burst" in words or "-fast" in words:
            damage_bonus += 0.25

        if "--precision" in words:
            crit_bonus += 0.15

        if "--infect" in words or "--overload" in words:
            status_bonus += 0.2

        return {
            "damage_multiplier": damage_bonus,
            "crit_boost": crit_bonus,
            "status_boost": status_bonus
        }

    # ==========================================================
    # HELPERS
    # ==========================================================

    def _infer_ability_type(self, ability_name):
        """
        Attempts to infer ability type from name.
        This assumes naming convention:
        data_pulse → ai
        packet_storm → worm
        corrupt_burst → malware
        """

        name = ability_name.lower()

        if "data" in name or "pulse" in name:
            return "ai"

        if "packet" in name or "storm" in name:
            return "worm"

        if "corrupt" in name or "inject" in name:
            return "malware"

        if "encrypt" in name or "lock" in name:
            return "ransomware"

        return None

    # ==========================================================
    # COMMAND HINT
    # ==========================================================

    def get_command_hint(self, ability_name):
        ability_type = self._infer_ability_type(ability_name)

        if ability_type not in self.type_keywords:
            return "exec <ability> --burst"

        example_keyword = self.type_keywords[ability_type][0]
        return f"{example_keyword} <target> --burst"
