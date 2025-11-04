"""Character entity module for heroes and enemies.

This module defines the base Character class and specific implementations
for heroes and enemies in the battle system.
"""

from typing import Dict, Any, Optional


# Constants
MIN_STAT_VALUE = 0
MAX_ATB_VALUE = 100
DEFENDING_DAMAGE_MULTIPLIER = 0.5


class Character:
    """Base class for all battle characters (heroes and enemies).
    
    Attributes:
        id: Unique identifier for the character.
        name: Display name of the character.
        max_hp: Maximum health points.
        current_hp: Current health points.
        max_mp: Maximum magic points (0 for enemies).
        current_mp: Current magic points.
        attack: Attack stat for damage calculation.
        defense: Defense stat for damage reduction.
        speed: Speed stat (affects turn order).
        atb_speed: Rate at which ATB gauge fills.
        atb_value: Current ATB gauge value (0-100).
        is_defending: Whether character is in defend state.
        is_alive: Whether character has HP > 0.
    """
    
    def __init__(self, data: Dict[str, Any]) -> None:
        """Initialize a character from data dictionary.
        
        Args:
            data: Dictionary containing character stats.
            
        Raises:
            ValueError: If required stats are missing or invalid.
        """
        required_fields = ['id', 'name', 'max_hp', 'attack', 'defense', 'speed', 'atb_speed']
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")
        
        self.id: str = data['id']
        self.name: str = data['name']
        self.max_hp: int = max(MIN_STAT_VALUE, data['max_hp'])
        self.current_hp: int = self.max_hp
        self.max_mp: int = max(MIN_STAT_VALUE, data.get('max_mp', 0))
        self.current_mp: int = self.max_mp
        self.attack: int = max(MIN_STAT_VALUE, data['attack'])
        self.defense: int = max(MIN_STAT_VALUE, data['defense'])
        self.speed: int = max(MIN_STAT_VALUE, data['speed'])
        self.atb_speed: int = max(MIN_STAT_VALUE, data['atb_speed'])
        self.atb_value: float = 0.0
        self.is_defending: bool = False
        self.is_alive: bool = True
    
    def update_atb(self, dt: float) -> None:
        """Update the ATB gauge based on delta time.
        
        Args:
            dt: Delta time in seconds since last update.
        """
        if self.is_alive and self.atb_value < MAX_ATB_VALUE:
            self.atb_value = min(MAX_ATB_VALUE, self.atb_value + self.atb_speed * dt)
    
    def reset_atb(self) -> None:
        """Reset ATB gauge to zero after taking a turn."""
        self.atb_value = 0.0
    
    def is_atb_ready(self) -> bool:
        """Check if character's ATB gauge is full.
        
        Returns:
            True if ATB gauge is at maximum value.
        """
        return self.atb_value >= MAX_ATB_VALUE
    
    def take_damage(self, damage: int) -> int:
        """Apply damage to character.
        
        Args:
            damage: Amount of damage to apply.
            
        Returns:
            Actual damage dealt after clamping.
        """
        actual_damage = max(MIN_STAT_VALUE, damage)
        if self.is_defending:
            actual_damage = int(actual_damage * DEFENDING_DAMAGE_MULTIPLIER)
        
        self.current_hp = max(MIN_STAT_VALUE, self.current_hp - actual_damage)
        
        if self.current_hp <= MIN_STAT_VALUE:
            self.is_alive = False
            self.current_hp = MIN_STAT_VALUE
        
        return actual_damage
    
    def heal(self, amount: int) -> int:
        """Heal character's HP.
        
        Args:
            amount: Amount of HP to restore.
            
        Returns:
            Actual HP restored after clamping.
        """
        if not self.is_alive:
            return 0
        
        old_hp = self.current_hp
        self.current_hp = min(self.max_hp, self.current_hp + max(MIN_STAT_VALUE, amount))
        return self.current_hp - old_hp
    
    def use_mp(self, amount: int) -> bool:
        """Consume MP for a skill.
        
        Args:
            amount: Amount of MP to consume.
            
        Returns:
            True if character had enough MP, False otherwise.
        """
        if self.current_mp >= amount:
            self.current_mp = max(MIN_STAT_VALUE, self.current_mp - amount)
            return True
        return False
    
    def restore_mp(self, amount: int) -> int:
        """Restore character's MP.
        
        Args:
            amount: Amount of MP to restore.
            
        Returns:
            Actual MP restored after clamping.
        """
        old_mp = self.current_mp
        self.current_mp = min(self.max_mp, self.current_mp + max(MIN_STAT_VALUE, amount))
        return self.current_mp - old_mp
    
    def set_defending(self, defending: bool) -> None:
        """Set character's defending state.
        
        Args:
            defending: Whether character should be defending.
        """
        self.is_defending = defending
    
    def get_hp_percentage(self) -> float:
        """Get current HP as a percentage of max HP.
        
        Returns:
            HP percentage (0.0 to 1.0).
        """
        if self.max_hp <= MIN_STAT_VALUE:
            return 0.0
        return self.current_hp / self.max_hp
    
    def get_mp_percentage(self) -> float:
        """Get current MP as a percentage of max MP.
        
        Returns:
            MP percentage (0.0 to 1.0).
        """
        if self.max_mp <= MIN_STAT_VALUE:
            return 0.0
        return self.current_mp / self.max_mp
    
    def get_atb_percentage(self) -> float:
        """Get current ATB value as a percentage.
        
        Returns:
            ATB percentage (0.0 to 1.0).
        """
        return self.atb_value / MAX_ATB_VALUE


class Hero(Character):
    """Hero character controlled by the player.
    
    Extends Character with hero-specific functionality.
    """
    
    def __init__(self, data: Dict[str, Any]) -> None:
        """Initialize a hero from data dictionary.
        
        Args:
            data: Dictionary containing hero stats.
            
        Raises:
            ValueError: If required stats are missing or invalid.
        """
        super().__init__(data)


class Enemy(Character):
    """Enemy character controlled by AI.
    
    Attributes:
        exp_reward: Experience points awarded when defeated.
        gold_reward: Gold awarded when defeated.
    """
    
    def __init__(self, data: Dict[str, Any]) -> None:
        """Initialize an enemy from data dictionary.
        
        Args:
            data: Dictionary containing enemy stats.
            
        Raises:
            ValueError: If required stats are missing or invalid.
        """
        super().__init__(data)
        self.exp_reward: int = max(MIN_STAT_VALUE, data.get('exp_reward', 0))
        self.gold_reward: int = max(MIN_STAT_VALUE, data.get('gold_reward', 0))
