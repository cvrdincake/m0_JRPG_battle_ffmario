"""Battle system core module.

This module manages the battle flow, turn order, and combat mechanics
combining ATB and timing systems.
"""

from typing import List, Optional, Tuple
from enum import Enum
from src.entities.character import Character, Hero, Enemy
from src.entities.move import Move
from src.battle.timing import TimingSystem, TimingResult


# Constants
MIN_COMBATANTS = 1


class BattleState(Enum):
    """Enumeration of battle states."""
    ACTIVE = "active"
    PLAYER_TURN = "player_turn"
    ENEMY_TURN = "enemy_turn"
    TIMING_COMMAND = "timing_command"
    ANIMATING = "animating"
    VICTORY = "victory"
    DEFEAT = "defeat"


class BattleSystem:
    """Manages the battle system and combat flow.
    
    Attributes:
        heroes: List of hero characters in battle.
        enemies: List of enemy characters in battle.
        state: Current battle state.
        active_character: Character whose turn it is.
        selected_move: Move selected for execution.
        selected_target: Target character for the move.
        timing_system: System for timing-based action commands.
        animation_timer: Timer for battle animations.
    """
    
    def __init__(self, heroes: List[Hero], enemies: List[Enemy]) -> None:
        """Initialize the battle system.
        
        Args:
            heroes: List of hero characters.
            enemies: List of enemy characters.
            
        Raises:
            ValueError: If heroes or enemies list is empty.
        """
        if not heroes:
            raise ValueError("Battle must have at least one hero")
        if not enemies:
            raise ValueError("Battle must have at least one enemy")
        
        self.heroes: List[Hero] = heroes
        self.enemies: List[Enemy] = enemies
        self.state: BattleState = BattleState.ACTIVE
        self.active_character: Optional[Character] = None
        self.selected_move: Optional[Move] = None
        self.selected_target: Optional[Character] = None
        self.timing_system: TimingSystem = TimingSystem()
        self.animation_timer: float = 0.0
    
    def update(self, dt: float) -> None:
        """Update the battle system.
        
        Args:
            dt: Delta time in seconds since last update.
        """
        if self.state == BattleState.ACTIVE:
            self._update_atb(dt)
            self._check_ready_characters()
        elif self.state == BattleState.TIMING_COMMAND:
            self.timing_system.update(dt)
        elif self.state == BattleState.ANIMATING:
            self._update_animation(dt)
        
        # Check win/loss conditions
        self._check_battle_end()
    
    def _update_atb(self, dt: float) -> None:
        """Update ATB gauges for all living characters.
        
        Args:
            dt: Delta time in seconds.
        """
        for hero in self.heroes:
            if hero.is_alive:
                hero.update_atb(dt)
        
        for enemy in self.enemies:
            if enemy.is_alive:
                enemy.update_atb(dt)
    
    def _check_ready_characters(self) -> None:
        """Check for characters with full ATB gauges."""
        # Check heroes first (player priority)
        for hero in self.heroes:
            if hero.is_alive and hero.is_atb_ready():
                self._start_character_turn(hero)
                self.state = BattleState.PLAYER_TURN
                return
        
        # Check enemies
        for enemy in self.enemies:
            if enemy.is_alive and enemy.is_atb_ready():
                self._start_character_turn(enemy)
                self.state = BattleState.ENEMY_TURN
                return
    
    def _start_character_turn(self, character: Character) -> None:
        """Start a turn for a character.
        
        Args:
            character: Character whose turn is starting.
        """
        self.active_character = character
        character.set_defending(False)  # Clear defend status
    
    def select_move_and_target(self, move: Move, target: Character) -> bool:
        """Select a move and target for the active character.
        
        Args:
            move: Move to execute.
            target: Target character.
            
        Returns:
            True if selection is valid, False otherwise.
        """
        if self.active_character is None:
            return False
        
        if not move.can_use(self.active_character.current_mp):
            return False
        
        if not target.is_alive and move.is_offensive():
            return False
        
        self.selected_move = move
        self.selected_target = target
        
        # Start timing window if move requires it
        if move.requires_timing():
            self.timing_system.start_timing_window(move.timing_window)
            self.state = BattleState.TIMING_COMMAND
        else:
            self._execute_move(TimingResult.NORMAL)
        
        return True
    
    def execute_timing_input(self) -> TimingResult:
        """Execute timing input and process the move.
        
        Returns:
            The timing result.
        """
        result = self.timing_system.check_input()
        self._execute_move(result)
        return result
    
    def _execute_move(self, timing_result: TimingResult) -> None:
        """Execute the selected move with timing result.
        
        Args:
            timing_result: Result of the timing input.
        """
        if self.active_character is None or self.selected_move is None or self.selected_target is None:
            return
        
        # Consume MP
        self.active_character.use_mp(self.selected_move.mp_cost)
        
        # Handle defend move specially
        if not self.selected_move.is_offensive():
            self.active_character.set_defending(True)
        else:
            # Calculate damage with timing bonus
            timing_multiplier = self.timing_system.get_timing_multiplier(
                timing_result, self.selected_move.timing_bonus
            )
            damage = self.selected_move.calculate_damage(
                self.active_character.attack,
                self.selected_target.defense,
                timing_multiplier
            )
            self.selected_target.take_damage(damage)
        
        # Reset ATB and end turn
        self.active_character.reset_atb()
        self.animation_timer = 0.5  # 0.5 second animation
        self.state = BattleState.ANIMATING
    
    def _update_animation(self, dt: float) -> None:
        """Update battle animation timer.
        
        Args:
            dt: Delta time in seconds.
        """
        self.animation_timer -= dt
        if self.animation_timer <= 0.0:
            self._end_turn()
    
    def _end_turn(self) -> None:
        """End the current turn and reset state."""
        self.active_character = None
        self.selected_move = None
        self.selected_target = None
        self.state = BattleState.ACTIVE
    
    def _check_battle_end(self) -> None:
        """Check if battle has ended in victory or defeat."""
        all_heroes_dead = all(not hero.is_alive for hero in self.heroes)
        all_enemies_dead = all(not enemy.is_alive for enemy in self.enemies)
        
        if all_heroes_dead:
            self.state = BattleState.DEFEAT
        elif all_enemies_dead:
            self.state = BattleState.VICTORY
    
    def get_alive_heroes(self) -> List[Hero]:
        """Get list of living heroes.
        
        Returns:
            List of heroes that are still alive.
        """
        return [hero for hero in self.heroes if hero.is_alive]
    
    def get_alive_enemies(self) -> List[Enemy]:
        """Get list of living enemies.
        
        Returns:
            List of enemies that are still alive.
        """
        return [enemy for enemy in self.enemies if enemy.is_alive]
    
    def is_battle_over(self) -> bool:
        """Check if battle has ended.
        
        Returns:
            True if battle is in victory or defeat state.
        """
        return self.state in (BattleState.VICTORY, BattleState.DEFEAT)
    
    def get_battle_rewards(self) -> Tuple[int, int]:
        """Calculate battle rewards (exp and gold).
        
        Returns:
            Tuple of (total_exp, total_gold).
        """
        if self.state != BattleState.VICTORY:
            return (0, 0)
        
        total_exp = sum(enemy.exp_reward for enemy in self.enemies)
        total_gold = sum(enemy.gold_reward for enemy in self.enemies)
        return (total_exp, total_gold)
