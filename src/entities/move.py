"""Move system for battle actions.

This module defines moves/skills that can be used in battle,
including the timing-based action command system.
"""

from typing import Dict, Any
from enum import Enum


# Constants
MIN_POWER = 0
MIN_TIMING_WINDOW = 0.0


class MoveType(Enum):
    """Enumeration of move types."""
    PHYSICAL = "physical"
    MAGIC = "magic"
    DEFEND = "defend"
    ITEM = "item"


class Move:
    """Represents a battle move/skill.
    
    Attributes:
        id: Unique identifier for the move.
        name: Display name of the move.
        move_type: Type of move (physical, magic, defend, item).
        mp_cost: MP required to use the move.
        base_power: Base damage/healing power.
        timing_window: Window in seconds for timing-based bonus.
        timing_bonus: Damage multiplier for successful timing.
        description: Description text for the move.
    """
    
    def __init__(self, data: Dict[str, Any]) -> None:
        """Initialize a move from data dictionary.
        
        Args:
            data: Dictionary containing move data.
            
        Raises:
            ValueError: If required fields are missing or invalid.
        """
        required_fields = ['id', 'name', 'type', 'mp_cost', 'base_power', 
                          'timing_window', 'timing_bonus', 'description']
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")
        
        self.id: str = data['id']
        self.name: str = data['name']
        
        # Parse move type
        try:
            self.move_type: MoveType = MoveType(data['type'])
        except ValueError:
            raise ValueError(f"Invalid move type: {data['type']}")
        
        self.mp_cost: int = max(0, data['mp_cost'])
        self.base_power: int = max(MIN_POWER, data['base_power'])
        self.timing_window: float = max(MIN_TIMING_WINDOW, data['timing_window'])
        self.timing_bonus: float = max(1.0, data['timing_bonus'])
        self.description: str = data['description']
    
    def calculate_damage(self, attacker_attack: int, defender_defense: int, 
                        timing_multiplier: float = 1.0) -> int:
        """Calculate damage for this move.
        
        Args:
            attacker_attack: Attack stat of the attacker.
            defender_defense: Defense stat of the defender.
            timing_multiplier: Multiplier from timing-based input (1.0 to timing_bonus).
            
        Returns:
            Final damage value after all calculations.
        """
        if self.move_type == MoveType.DEFEND:
            return 0
        
        # Clamp timing multiplier
        timing_multiplier = max(1.0, min(self.timing_bonus, timing_multiplier))
        
        # Basic damage formula: (base_power + attack - defense/2) * timing
        raw_damage = self.base_power + attacker_attack - (defender_defense // 2)
        final_damage = int(raw_damage * timing_multiplier)
        
        # Ensure minimum damage of 1 for offensive moves
        if self.base_power > MIN_POWER:
            final_damage = max(1, final_damage)
        else:
            final_damage = max(0, final_damage)
        
        return final_damage
    
    def can_use(self, user_mp: int) -> bool:
        """Check if move can be used with current MP.
        
        Args:
            user_mp: Current MP of the user.
            
        Returns:
            True if user has enough MP to use the move.
        """
        return user_mp >= self.mp_cost
    
    def is_offensive(self) -> bool:
        """Check if move is offensive (deals damage).
        
        Returns:
            True if move is physical or magic type.
        """
        return self.move_type in (MoveType.PHYSICAL, MoveType.MAGIC)
    
    def requires_timing(self) -> bool:
        """Check if move uses timing-based action commands.
        
        Returns:
            True if move has a timing window greater than 0.
        """
        return self.timing_window > MIN_TIMING_WINDOW
