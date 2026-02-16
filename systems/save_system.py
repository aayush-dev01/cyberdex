"""
CyberDex - Save System
Handles saving and loading game data.
"""

import os
import json
from data.virus import Virus


class SaveSystem:

    def __init__(self, save_directory="saves"):
        self.save_directory = save_directory
        self._ensure_save_directory()

    # ==========================================================
    # DIRECTORY HANDLING
    # ==========================================================

    def _ensure_save_directory(self):
        if not os.path.exists(self.save_directory):
            os.makedirs(self.save_directory)

    def _get_save_path(self, slot):
        return os.path.join(self.save_directory, f"save_slot_{slot}.json")

    # ==========================================================
    # SAVE
    # ==========================================================

    def save_game(self, game_data, slot=1):
        """
        game_data structure expected:
        {
            "player_name": str,
            "virus_team": [Virus objects],
            "virus_storage": [Virus objects],
            "inventory": dict,
            "world_state": dict
        }
        """

        serializable_data = {
            "player_name": game_data.get("player_name", "Player"),
            "virus_team": [v.to_dict() for v in game_data.get("virus_team", [])],
            "virus_storage": [v.to_dict() for v in game_data.get("virus_storage", [])],
            "inventory": game_data.get("inventory", {}),
            "world_state": game_data.get("world_state", {})
        }

        save_path = self._get_save_path(slot)

        with open(save_path, "w") as f:
            json.dump(serializable_data, f, indent=4)

    # ==========================================================
    # LOAD
    # ==========================================================

    def load_game(self, slot=1):
        save_path = self._get_save_path(slot)

        if not os.path.exists(save_path):
            return None

        with open(save_path, "r") as f:
            data = json.load(f)

        # Rebuild Virus objects
        team = [Virus.from_dict(v) for v in data.get("virus_team", [])]
        storage = [Virus.from_dict(v) for v in data.get("virus_storage", [])]

        return {
            "player_name": data.get("player_name", "Player"),
            "virus_team": team,
            "virus_storage": storage,
            "inventory": data.get("inventory", {}),
            "world_state": data.get("world_state", {})
        }

    # ==========================================================
    # DELETE SAVE
    # ==========================================================

    def delete_save(self, slot=1):
        save_path = self._get_save_path(slot)
        if os.path.exists(save_path):
            os.remove(save_path)
