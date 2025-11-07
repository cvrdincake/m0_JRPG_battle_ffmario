"""Immutable stats system for game entities.

This module defines the Stats dataclass which holds immutable base statistics
for characters and enemies. All stat values are validated and frozen to prevent
accidental modification.
"""

from dataclasses import dataclass
from typing import ClassVar


@dataclass(frozen=True)
class Stats:
    """Immutable stats container for entities.
    
    Using frozen=True ensures stats cannot be modified after creation,
    preventing accidental bugs from stat modification.
    
    Attributes:
        max_hp: Maximum health points.
        max_mp: Maximum magic points.
        attack: Physical attack power.
        defense: Physical defense.
        magic: Magical power.
        speed: Turn order priority (higher = faster).
    """
    max_hp: int
    max_mp: int
    attack: int
    defense: int
    magic: int
    speed: int
    
    def __post_init__(self) -> None:
        """Validate all stats are non-negative.
        
        Raises:
            ValueError: If any stat is negative.
        """
        for field_name in self.__dataclass_fields__:
            value = getattr(self, field_name)
            if value < 0:
                raise ValueError(f"{field_name} cannot be negative: {value}")
    
    @staticmethod
    def calculate_physical_damage(attacker_stats: 'Stats', 
                                   defender_stats: 'Stats', 
                                   move_power: int) -> int:
        """Calculate physical damage using attack vs defense formula.
        
        This formula ensures deterministic damage calculation for testing.
        The formula balances attack and defense using a ratio that prevents
        defense from completely negating damage while still being meaningful.
        
        Formula:
            raw_damage = move_power * (attacker.attack / (attacker.attack + defender.defense))
            final_damage = max(1, int(raw_damage))
        
        Args:
            attacker_stats: Stats of attacking entity.
            defender_stats: Stats of defending entity.
            move_power: Base power of the move.
        
        Returns:
            Final damage value (minimum 1).
        """
        # Prevent division by zero
        denominator = attacker_stats.attack + defender_stats.defense
        if denominator == 0:
            return 1
        
        # Calculate damage using attack/(attack+defense) ratio
        attack_ratio = attacker_stats.attack / denominator
        raw_damage = move_power * attack_ratio
        
        # Always deal at least 1 damage
        final_damage = max(1, int(raw_damage))
        
        return final_damage
    
    @staticmethod
    def calculate_magical_damage(attacker_stats: 'Stats',
                                 defender_stats: 'Stats',
                                 move_power: int) -> int:
        """Calculate magical damage using magic vs defense formula.
        
        Similar to physical damage but uses magic stat instead of attack.
        
        Args:
            attacker_stats: Stats of attacking entity.
            defender_stats: Stats of defending entity.
            move_power: Base power of the move.
        
        Returns:
            Final damage value (minimum 1).
        """
        # Prevent division by zero
        denominator = attacker_stats.magic + defender_stats.defense
        if denominator == 0:
            return 1
        
        # Calculate damage using magic/(magic+defense) ratio
        magic_ratio = attacker_stats.magic / denominator
        raw_damage = move_power * magic_ratio
        
        # Always deal at least 1 damage
        final_damage = max(1, int(raw_damage))
        
        return final_damage
