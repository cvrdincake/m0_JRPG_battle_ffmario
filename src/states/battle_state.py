"""Battle state with phase management.

This module implements the BattleState as a proper state machine with
distinct phases for battle flow control.
"""

import pygame
from typing import Optional, List, Tuple
from src.states.base_state import State
from src.battle.battle_phase import BattlePhase
from src.entities.party import Party
from src.entities.enemy_group import EnemyGroup
from src.entities.character import Character, Hero, Enemy
from src.battle.move import BattleMove
from src.battle.timing import TimingSystem


# Constants for phase durations (in seconds)
BATTLE_START_DURATION = 2.0
ACTION_ANIMATION_DURATION = 1.0
MIN_PHASE_DURATION = 0.0

# Colors
BACKGROUND_COLOR = (20, 20, 40)
TEXT_COLOR = (255, 255, 255)
MENU_HIGHLIGHT_COLOR = (255, 255, 0)


class BattleState(State):
    """Main battle state managing combat flow with phase system.
    
    Uses a state machine pattern with one method per phase. Phase transitions
    are explicit and controlled to prevent skipping or repeating phases.
    
    Attributes:
        party: Player's party of heroes.
        enemy_group: Enemy group.
        current_phase: Current battle phase.
        phase_timer: Timer for phase duration (delta time accumulation).
        active_character: Character whose turn it is currently.
        selected_move: Move selected for execution.
        selected_target: Target character for the move.
        timing_system: System for timing-based action commands.
        input_enabled: Whether input is currently allowed.
        selected_move_index: Index of currently selected move in menu.
        selected_target_index: Index of currently selected target.
        available_moves: List of moves available in battle.
        battle_message: Current message to display.
        message_timer: Timer for message display.
    """
    
    def __init__(self, party: Party, enemy_group: EnemyGroup, 
                 available_moves: List[BattleMove]) -> None:
        """Initialize the battle state.
        
        Args:
            party: Player's party of heroes.
            enemy_group: Group of enemy characters.
            available_moves: List of moves available in battle.
            
        Raises:
            ValueError: If party or enemy_group is empty.
        """
        if not party.members:
            raise ValueError("Party cannot be empty")
        if not enemy_group.enemies:
            raise ValueError("Enemy group cannot be empty")
        
        self.party: Party = party
        self.enemy_group: EnemyGroup = enemy_group
        self.current_phase: BattlePhase = BattlePhase.BATTLE_START
        self.phase_timer: float = 0.0
        
        self.active_character: Optional[Character] = None
        self.selected_move: Optional[BattleMove] = None
        self.selected_target: Optional[Character] = None
        self.timing_system: TimingSystem = TimingSystem()
        
        self.input_enabled: bool = False
        self.selected_move_index: int = 0
        self.selected_target_index: int = 0
        self.available_moves: List[BattleMove] = available_moves
        
        self.battle_message: str = "Battle Start!"
        self.message_timer: float = 0.0
    
    def enter(self) -> None:
        """Called when the state is entered."""
        self.current_phase = BattlePhase.BATTLE_START
        self.phase_timer = 0.0
        self.input_enabled = False
        self.battle_message = "Battle Start!"
        self.message_timer = 2.0
    
    def exit(self) -> None:
        """Called when the state is exited."""
        # Clean up resources if needed
        pass
    
    def pause(self) -> None:
        """Called when the state is paused."""
        self.input_enabled = False
    
    def resume(self) -> None:
        """Called when the state is resumed."""
        # Re-enable input if in appropriate phase
        if self.current_phase == BattlePhase.TURN_SELECT:
            self.input_enabled = True
    
    def update(self, dt: float) -> None:
        """Update the battle state logic.
        
        Args:
            dt: Delta time in seconds since last update.
        """
        # Accumulate phase timer
        self.phase_timer += dt
        
        # Update message timer
        if self.message_timer > 0.0:
            self.message_timer -= dt
        
        # Update ATB for all alive characters (unless in terminal phases)
        if self.current_phase not in (BattlePhase.VICTORY, BattlePhase.DEFEAT):
            self._update_atb(dt)
        
        # Dispatch to phase-specific update method
        if self.current_phase == BattlePhase.BATTLE_START:
            self._update_battle_start()
        elif self.current_phase == BattlePhase.TURN_SELECT:
            self._update_turn_select()
        elif self.current_phase == BattlePhase.EXECUTING_ACTION:
            self._update_executing_action(dt)
        elif self.current_phase == BattlePhase.ENEMY_TURN:
            self._update_enemy_turn()
        elif self.current_phase == BattlePhase.CHECK_VICTORY:
            self._update_check_victory()
        elif self.current_phase == BattlePhase.VICTORY:
            self._update_victory()
        elif self.current_phase == BattlePhase.DEFEAT:
            self._update_defeat()
    
    def render(self, screen: pygame.Surface) -> None:
        """Render the battle state to the screen.
        
        Args:
            screen: Pygame surface to render to.
        """
        # Clear screen
        screen.fill(BACKGROUND_COLOR)
        
        # Render party members
        for member in self.party.members:
            if member.is_alive:
                pos = self.party.get_member_position(member)
                if pos:
                    self._render_character(screen, member, pos)
        
        # Render enemies
        for enemy in self.enemy_group.enemies:
            if enemy.is_alive:
                pos = self.enemy_group.get_enemy_position(enemy)
                if pos:
                    self._render_character(screen, enemy, pos)
        
        # Render phase-specific UI
        if self.current_phase == BattlePhase.TURN_SELECT:
            self._render_turn_select_ui(screen)
        elif self.current_phase == BattlePhase.EXECUTING_ACTION:
            self._render_action_animation(screen)
        
        # Render battle message
        if self.message_timer > 0.0:
            self._render_message(screen)
    
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle a pygame event.
        
        Args:
            event: Pygame event to handle.
        """
        if not self.input_enabled or event.type != pygame.KEYDOWN:
            return
        
        if self.current_phase == BattlePhase.TURN_SELECT:
            self._handle_turn_select_input(event)
    
    # Phase update methods (one per phase)
    
    def _update_battle_start(self) -> None:
        """Update BATTLE_START phase (2 second intro)."""
        if self.phase_timer >= BATTLE_START_DURATION:
            self._transition_to_turn_select()
    
    def _update_turn_select(self) -> None:
        """Update TURN_SELECT phase (wait for player input)."""
        # Check if any character is ready for their turn
        if self.active_character is None:
            self._check_for_ready_character()
    
    def _update_executing_action(self, dt: float) -> None:
        """Update EXECUTING_ACTION phase (animation + damage calc).
        
        Args:
            dt: Delta time in seconds.
        """
        # Update timing system if move requires timing
        if self.selected_move and self.selected_move.action_command.requires_input():
            self.timing_system.update(dt)
        
        # Wait for animation to complete
        if self.phase_timer >= ACTION_ANIMATION_DURATION:
            self._transition_to_check_victory()
    
    def _update_enemy_turn(self) -> None:
        """Update ENEMY_TURN phase (AI turn execution)."""
        if self.active_character and isinstance(self.active_character, Enemy):
            self._execute_enemy_ai()
            self._transition_to_check_victory()
    
    def _update_check_victory(self) -> None:
        """Update CHECK_VICTORY phase (instant check)."""
        # Check win/loss conditions
        if self.party.all_dead():
            self._transition_to_defeat()
        elif self.enemy_group.all_dead():
            self._transition_to_victory()
        else:
            # Battle continues - go back to turn select
            self._transition_to_turn_select()
    
    def _update_victory(self) -> None:
        """Update VICTORY phase (show results)."""
        # Victory state - waiting for player to acknowledge
        pass
    
    def _update_defeat(self) -> None:
        """Update DEFEAT phase (show results)."""
        # Defeat state - waiting for player to acknowledge
        pass
    
    # Phase transition methods (explicit state changes)
    
    def _transition_to_turn_select(self) -> None:
        """Transition to TURN_SELECT phase."""
        self.current_phase = BattlePhase.TURN_SELECT
        self.phase_timer = 0.0
        self.active_character = None
        self.selected_move = None
        self.selected_target = None
        self.input_enabled = True
        self._check_for_ready_character()
    
    def _transition_to_executing_action(self) -> None:
        """Transition to EXECUTING_ACTION phase."""
        self.current_phase = BattlePhase.EXECUTING_ACTION
        self.phase_timer = 0.0
        self.input_enabled = False
    
    def _transition_to_enemy_turn(self) -> None:
        """Transition to ENEMY_TURN phase."""
        self.current_phase = BattlePhase.ENEMY_TURN
        self.phase_timer = 0.0
        self.input_enabled = False
    
    def _transition_to_check_victory(self) -> None:
        """Transition to CHECK_VICTORY phase."""
        self.current_phase = BattlePhase.CHECK_VICTORY
        self.phase_timer = 0.0
        self.input_enabled = False
    
    def _transition_to_victory(self) -> None:
        """Transition to VICTORY phase."""
        self.current_phase = BattlePhase.VICTORY
        self.phase_timer = 0.0
        self.input_enabled = False
        self.battle_message = "Victory!"
        self.message_timer = 5.0
    
    def _transition_to_defeat(self) -> None:
        """Transition to DEFEAT phase."""
        self.current_phase = BattlePhase.DEFEAT
        self.phase_timer = 0.0
        self.input_enabled = False
        self.battle_message = "Defeat..."
        self.message_timer = 5.0
    
    # Helper methods
    
    def _update_atb(self, dt: float) -> None:
        """Update ATB gauges for all living characters.
        
        Args:
            dt: Delta time in seconds.
        """
        for member in self.party.members:
            if member.is_alive:
                member.update_atb(dt)
        
        for enemy in self.enemy_group.enemies:
            if enemy.is_alive:
                enemy.update_atb(dt)
    
    def _check_for_ready_character(self) -> None:
        """Check for characters with full ATB gauges and assign turn."""
        # Check party members first (player priority)
        for member in self.party.members:
            if member.is_alive and member.is_atb_ready():
                self.active_character = member
                self.input_enabled = True
                self.battle_message = f"{member.name}'s turn!"
                self.message_timer = 1.0
                return
        
        # Check enemies
        for enemy in self.enemy_group.enemies:
            if enemy.is_alive and enemy.is_atb_ready():
                self.active_character = enemy
                self._transition_to_enemy_turn()
                return
    
    def _execute_enemy_ai(self) -> None:
        """Execute simple AI for enemy turn."""
        if not self.active_character or not isinstance(self.active_character, Enemy):
            return
        
        # Simple AI: Pick first offensive move that can be used
        move = None
        for m in self.available_moves:
            if m.targets_enemy() and m.can_use(self.active_character.current_mp):
                move = m
                break
        
        if not move:
            # No valid move, skip turn
            self.active_character.reset_atb()
            return
        
        # Pick random alive hero as target
        target = self.party.get_random_alive_member()
        if not target:
            return
        
        self.selected_move = move
        self.selected_target = target
        
        # Execute the action
        self._execute_selected_action()
        
        self.battle_message = f"{self.active_character.name} attacks {target.name}!"
        self.message_timer = 1.5
    
    def _execute_selected_action(self) -> None:
        """Execute the currently selected move on the target."""
        if not self.active_character or not self.selected_move or not self.selected_target:
            return
        
        # Consume MP
        self.active_character.use_mp(self.selected_move.mp_cost)
        
        # Calculate damage (simplified - no timing bonus for AI)
        if self.selected_move.is_offensive:
            damage = self.selected_move.calculate_damage(
                self.active_character.stats.attack,
                self.selected_target.stats.defense
            )
            self.selected_target.take_damage(damage)
        else:
            # Healing or buff
            self.selected_target.set_defending(True)
        
        # Reset ATB
        self.active_character.reset_atb()
        
        # Transition to action animation
        self._transition_to_executing_action()
    
    def _handle_turn_select_input(self, event: pygame.event.Event) -> None:
        """Handle input during TURN_SELECT phase.
        
        Args:
            event: Pygame keyboard event.
        """
        if event.key == pygame.K_UP:
            self.selected_move_index = max(0, self.selected_move_index - 1)
        elif event.key == pygame.K_DOWN:
            self.selected_move_index = min(
                len(self.available_moves) - 1,
                self.selected_move_index + 1
            )
        elif event.key == pygame.K_LEFT:
            self.selected_target_index = max(0, self.selected_target_index - 1)
        elif event.key == pygame.K_RIGHT:
            alive_enemies = self.enemy_group.get_alive_enemies()
            self.selected_target_index = min(
                len(alive_enemies) - 1,
                self.selected_target_index + 1
            )
        elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
            self._confirm_selection()
    
    def _confirm_selection(self) -> None:
        """Confirm the selected move and target."""
        if not self.active_character:
            return
        
        move = self.available_moves[self.selected_move_index]
        
        # Select target based on move type
        if move.targets_enemy():
            alive_enemies = self.enemy_group.get_alive_enemies()
            if not alive_enemies:
                return
            target = alive_enemies[min(self.selected_target_index, len(alive_enemies) - 1)]
        else:
            # Self-targeting or ally
            target = self.active_character
        
        # Check if move can be used
        if not move.can_use(self.active_character.current_mp):
            self.battle_message = "Not enough MP!"
            self.message_timer = 1.0
            return
        
        self.selected_move = move
        self.selected_target = target
        
        # Execute the action
        self._execute_selected_action()
        
        self.battle_message = f"{self.active_character.name} uses {move.name}!"
        self.message_timer = 1.5
    
    # Rendering helper methods
    
    def _render_character(self, screen: pygame.Surface, character: Character, 
                         pos: Tuple[int, int]) -> None:
        """Render a character at the given position.
        
        Args:
            screen: Pygame surface to render to.
            character: Character to render.
            pos: (x, y) position tuple.
        """
        # Simple placeholder rendering (colored circle)
        color = (50, 100, 255) if isinstance(character, Hero) else (255, 100, 50)
        pygame.draw.circle(screen, color, pos, 30)
        
        # Render name
        font = pygame.font.Font(None, 20)
        name_surf = font.render(character.name, True, TEXT_COLOR)
        name_rect = name_surf.get_rect(center=(pos[0], pos[1] + 50))
        screen.blit(name_surf, name_rect)
        
        # Render HP bar
        hp_percent = character.get_hp_percentage()
        bar_width = 60
        bar_height = 5
        bar_x = pos[0] - bar_width // 2
        bar_y = pos[1] + 40
        
        # Background
        pygame.draw.rect(screen, (100, 100, 100), 
                        (bar_x, bar_y, bar_width, bar_height))
        # HP fill
        hp_width = int(bar_width * hp_percent)
        pygame.draw.rect(screen, (0, 255, 0), 
                        (bar_x, bar_y, hp_width, bar_height))
    
    def _render_turn_select_ui(self, screen: pygame.Surface) -> None:
        """Render the move selection UI during TURN_SELECT phase.
        
        Args:
            screen: Pygame surface to render to.
        """
        font = pygame.font.Font(None, 24)
        
        # Render move list
        menu_x = 50
        menu_y = 200
        
        title = font.render("Select Move:", True, TEXT_COLOR)
        screen.blit(title, (menu_x, menu_y))
        
        for i, move in enumerate(self.available_moves[:5]):  # Show first 5 moves
            y = menu_y + 30 + i * 25
            color = MENU_HIGHLIGHT_COLOR if i == self.selected_move_index else TEXT_COLOR
            prefix = "> " if i == self.selected_move_index else "  "
            text = f"{prefix}{move.name} (MP: {move.mp_cost})"
            move_surf = font.render(text, True, color)
            screen.blit(move_surf, (menu_x, y))
    
    def _render_action_animation(self, screen: pygame.Surface) -> None:
        """Render action animation during EXECUTING_ACTION phase.
        
        Args:
            screen: Pygame surface to render to.
        """
        # Simple animation placeholder
        if self.active_character and self.selected_target:
            font = pygame.font.Font(None, 36)
            text = "Attacking..."
            surf = font.render(text, True, (255, 255, 0))
            rect = surf.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
            screen.blit(surf, rect)
    
    def _render_message(self, screen: pygame.Surface) -> None:
        """Render the current battle message.
        
        Args:
            screen: Pygame surface to render to.
        """
        font = pygame.font.Font(None, 36)
        
        # Render with shadow for better visibility
        shadow = font.render(self.battle_message, True, (0, 0, 0))
        text = font.render(self.battle_message, True, TEXT_COLOR)
        
        x = (screen.get_width() - text.get_width()) // 2
        y = 100
        
        screen.blit(shadow, (x + 2, y + 2))
        screen.blit(text, (x, y))
