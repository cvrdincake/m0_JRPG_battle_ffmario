"""Enhanced move system for battle actions.

This module defines the battle move system with support for different timing
types, targeting options, and action command mechanics.
"""

from dataclasses import dataclass
from typing import Optional, Literal, List, Dict, Any
from enum import Enum


class TargetType(Enum):
    """Who can be targeted by a move."""
    SINGLE_ENEMY = "single_enemy"
    ALL_ENEMIES = "all_enemies"
    SINGLE_ALLY = "single_ally"
    ALL_ALLIES = "all_allies"
    SELF = "self"


class TimingType(Enum):
    """Type of timing-based action command."""
    SIMPLE = "simple"  # No timing required
    TIMED_PRESS = "timed_press"  # Press at right moment
    SEQUENCE = "sequence"  # Multiple presses in rhythm
    HOLD_RELEASE = "hold_release"  # Hold and release


@dataclass
class TimingWindow:
    """Timing window thresholds in milliseconds.
    
    Defines the acceptable input timing ranges for action commands.
    Windows are evaluated in order: perfect, good, early, then miss.
    
    Attributes:
        perfect_min: Start of perfect window (ms).
        perfect_max: End of perfect window (ms).
        good_min: Start of good window (ms).
        good_max: End of good window (ms).
        early_min: Start of early window (ms).
        early_max: End of early window (ms).
    """
    perfect_min: int
    perfect_max: int
    good_min: int
    good_max: int
    early_min: int
    early_max: int
    
    def evaluate(self, input_time_ms: int) -> Literal["miss", "early", "good", "perfect"]:
        """Evaluate input timing.
        
        Args:
            input_time_ms: Time of button press in milliseconds.
        
        Returns:
            Rating string: "miss", "early", "good", or "perfect".
        """
        if self.perfect_min <= input_time_ms <= self.perfect_max:
            return "perfect"
        elif self.good_min <= input_time_ms <= self.good_max:
            return "good"
        elif self.early_min <= input_time_ms <= self.early_max:
            return "early"
        else:
            return "miss"
    
    @classmethod
    def from_dict(cls, data: Dict[str, int]) -> 'TimingWindow':
        """Create TimingWindow from dictionary.
        
        Args:
            data: Dictionary with timing thresholds.
        
        Returns:
            New TimingWindow instance.
        
        Raises:
            ValueError: If required fields are missing.
        """
        required = ['perfect_min', 'perfect_max', 'good_min', 'good_max', 
                   'early_min', 'early_max']
        for field in required:
            if field not in data:
                raise ValueError(f"Missing required timing field: {field}")
        
        return cls(
            perfect_min=data['perfect_min'],
            perfect_max=data['perfect_max'],
            good_min=data['good_min'],
            good_max=data['good_max'],
            early_min=data['early_min'],
            early_max=data['early_max']
        )


@dataclass
class ActionCommand:
    """Defines the action command requirements for a move.
    
    Attributes:
        timing_type: Type of timing mechanic.
        timing_window: Optional timing windows for evaluation.
        sequence_buttons: Optional list of buttons for sequence timing.
        hold_duration_ms: Optional duration for hold_release timing.
    """
    timing_type: TimingType
    timing_window: Optional[TimingWindow] = None
    sequence_buttons: Optional[List[str]] = None
    hold_duration_ms: Optional[int] = None
    
    def requires_input(self) -> bool:
        """Check if action command requires player input.
        
        Returns:
            False for SIMPLE timing, True for all others.
        """
        return self.timing_type != TimingType.SIMPLE
    
    def get_multiplier(self, rating: str) -> float:
        """Get damage multiplier based on timing rating.
        
        Args:
            rating: Timing rating ("miss", "early", "good", "perfect").
        
        Returns:
            Damage multiplier (1.0 to 2.0).
        """
        multipliers = {
            "perfect": 2.0,
            "good": 1.5,
            "early": 1.2,
            "miss": 1.0
        }
        return multipliers.get(rating, 1.0)


class BattleMove:
    """Enhanced battle move with comprehensive action command support.
    
    Attributes:
        id: Unique identifier.
        name: Display name.
        description: Move description.
        base_power: Base damage/healing power.
        mp_cost: MP required to use.
        target_type: Who can be targeted.
        action_command: Timing and input requirements.
        is_offensive: Whether move deals damage.
    """
    
    def __init__(self, data: Dict[str, Any]) -> None:
        """Initialize move from data dictionary.
        
        Args:
            data: Dictionary containing move configuration.
        
        Raises:
            ValueError: If required fields are missing or invalid.
        """
        required = ['id', 'name', 'description', 'base_power', 'mp_cost', 
                   'target_type', 'timing_type']
        for field in required:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")
        
        self.id: str = data['id']
        self.name: str = data['name']
        self.description: str = data['description']
        self.base_power: int = max(0, data['base_power'])
        self.mp_cost: int = max(0, data['mp_cost'])
        
        # Parse target type
        try:
            self.target_type: TargetType = TargetType(data['target_type'])
        except ValueError:
            raise ValueError(f"Invalid target type: {data['target_type']}")
        
        # Parse timing type
        try:
            timing_type = TimingType(data['timing_type'])
        except ValueError:
            raise ValueError(f"Invalid timing type: {data['timing_type']}")
        
        # Create action command
        timing_window = None
        if 'timing_window' in data and data['timing_window'] is not None:
            timing_window = TimingWindow.from_dict(data['timing_window'])
        
        self.action_command = ActionCommand(
            timing_type=timing_type,
            timing_window=timing_window,
            sequence_buttons=data.get('sequence_buttons'),
            hold_duration_ms=data.get('hold_duration_ms')
        )
        
        self.is_offensive: bool = data.get('is_offensive', True)
    
    def can_use(self, user_mp: int) -> bool:
        """Check if move can be used with current MP.
        
        Args:
            user_mp: Current MP of the user.
        
        Returns:
            True if user has enough MP.
        """
        return user_mp >= self.mp_cost
    
    def calculate_damage(self, attacker_attack: int, defender_defense: int,
                        timing_rating: str = "miss") -> int:
        """Calculate final damage with timing bonus.
        
        Args:
            attacker_attack: Attacker's attack stat.
            defender_defense: Defender's defense stat.
            timing_rating: Timing rating from action command.
        
        Returns:
            Final damage value.
        """
        if not self.is_offensive or self.base_power == 0:
            return 0
        
        # Use new deterministic damage formula from Stats class
        # For now, use simplified version until Stats integration
        denominator = attacker_attack + defender_defense
        if denominator == 0:
            base_damage = 1
        else:
            attack_ratio = attacker_attack / denominator
            base_damage = int(self.base_power * attack_ratio)
        
        # Apply timing multiplier
        multiplier = self.action_command.get_multiplier(timing_rating)
        final_damage = int(base_damage * multiplier)
        
        # Ensure minimum 1 damage
        return max(1, final_damage)
    
    def targets_enemy(self) -> bool:
        """Check if move targets enemies.
        
        Returns:
            True if move targets enemy/enemies.
        """
        return self.target_type in (TargetType.SINGLE_ENEMY, TargetType.ALL_ENEMIES)
    
    def targets_ally(self) -> bool:
        """Check if move targets allies.
        
        Returns:
            True if move targets ally/allies or self.
        """
        return self.target_type in (TargetType.SINGLE_ALLY, TargetType.ALL_ALLIES, 
                                   TargetType.SELF)
    
    def is_multi_target(self) -> bool:
        """Check if move targets multiple entities.
        
        Returns:
            True if move targets all enemies or all allies.
        """
        return self.target_type in (TargetType.ALL_ENEMIES, TargetType.ALL_ALLIES)


# Default timing windows for different move types (in milliseconds)
DEFAULT_TIMING_WINDOWS = {
    TimingType.TIMED_PRESS: TimingWindow(
        perfect_min=450, perfect_max=550,  # 100ms perfect window
        good_min=350, good_max=650,        # 300ms good window
        early_min=200, early_max=800,      # 600ms early window
    ),
    TimingType.SEQUENCE: TimingWindow(
        perfect_min=475, perfect_max=525,  # 50ms perfect window (harder)
        good_min=400, good_max=600,        # 200ms good window
        early_min=300, early_max=700,      # 400ms early window
    ),
    TimingType.HOLD_RELEASE: TimingWindow(
        perfect_min=480, perfect_max=520,  # 40ms perfect window (very tight)
        good_min=420, good_max=580,        # 160ms good window
        early_min=350, early_max=650,      # 300ms early window
    ),
}
