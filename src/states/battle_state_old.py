"""Battle state module.

This module manages the battle scene, including rendering, input handling,
and coordinating the battle system with the UI.
"""

import pygame
import random
from typing import List, Optional
from src.entities.character import Hero, Enemy
from src.entities.move import Move
from src.battle.battle_system import BattleSystem, BattleState
from src.ui.battle_ui import CharacterInfoPanel, TimingIndicator
from src.utils.data_loader import load_characters, load_enemies, load_moves


# Constants
BACKGROUND_COLOR = (20, 20, 40)
TEXT_COLOR = (255, 255, 255)
HERO_Y_POSITION = 450
ENEMY_Y_POSITION = 200
PANEL_SPACING = 20


class BattleScene:
    """Manages the battle scene and rendering.
    
    Attributes:
        screen: Pygame display surface.
        config: Game configuration dictionary.
        battle_system: Battle system managing combat logic.
        heroes: List of hero characters.
        enemies: List of enemy characters.
        moves: List of available moves.
        hero_panels: UI panels for heroes.
        enemy_panels: UI panels for enemies.
        timing_indicator: Timing indicator for action commands.
        selected_move_index: Index of selected move.
        selected_target_index: Index of selected target.
        message: Current battle message.
        message_timer: Timer for message display.
    """
    
    def __init__(self, screen: pygame.Surface, config: dict) -> None:
        """Initialize the battle scene.
        
        Args:
            screen: Pygame display surface.
            config: Game configuration dictionary.
            
        Raises:
            RuntimeError: If data loading fails.
        """
        self.screen: pygame.Surface = screen
        self.config: dict = config
        
        # Load data
        try:
            data_path = config.get('paths', {}).get('data', 'assets/data')
            char_data = load_characters(f"{data_path}/characters.json")
            enemy_data = load_enemies(f"{data_path}/enemies.json")
            move_data = load_moves(f"{data_path}/moves.json")
        except Exception as e:
            raise RuntimeError(f"Failed to load battle data: {e}")
        
        # Create characters
        self.heroes: List[Hero] = [Hero(data) for data in char_data[:2]]
        self.enemies: List[Enemy] = [Enemy(enemy_data[0])]  # Start with one Goomba
        
        # Create moves
        self.moves: List[Move] = [Move(data) for data in move_data]
        
        # Initialize battle system
        self.battle_system: BattleSystem = BattleSystem(self.heroes, self.enemies)
        
        # Create UI components
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        
        # Hero panels (bottom of screen)
        self.hero_panels: List[CharacterInfoPanel] = []
        panel_y = screen_height - 120
        panel_spacing = (screen_width - 250 * len(self.heroes)) // (len(self.heroes) + 1)
        for i, hero in enumerate(self.heroes):
            panel_x = panel_spacing + i * (250 + panel_spacing)
            self.hero_panels.append(CharacterInfoPanel(panel_x, panel_y))
        
        # Enemy panels (top of screen)
        self.enemy_panels: List[CharacterInfoPanel] = []
        panel_y = 20
        enemy_spacing = (screen_width - 250 * len(self.enemies)) // (len(self.enemies) + 1)
        for i, enemy in enumerate(self.enemies):
            panel_x = enemy_spacing + i * (250 + enemy_spacing)
            self.enemy_panels.append(CharacterInfoPanel(panel_x, panel_y))
        
        # Timing indicator (center of screen)
        indicator_x = (screen_width - 400) // 2
        indicator_y = screen_height // 2 - 20
        self.timing_indicator: TimingIndicator = TimingIndicator(indicator_x, indicator_y)
        
        # UI state
        self.selected_move_index: int = 0
        self.selected_target_index: int = 0
        self.message: str = "Battle Start!"
        self.message_timer: float = 2.0
        
        # Font
        try:
            self.font: Optional[pygame.font.Font] = pygame.font.Font(None, 36)
            self.small_font: Optional[pygame.font.Font] = pygame.font.Font(None, 24)
        except pygame.error:
            self.font = None
            self.small_font = None
    
    def update(self, dt: float) -> bool:
        """Update the battle scene.
        
        Args:
            dt: Delta time in seconds.
            
        Returns:
            True if battle should continue, False if it's over.
        """
        # Update message timer
        if self.message_timer > 0.0:
            self.message_timer -= dt
        
        # Update battle system
        self.battle_system.update(dt)
        
        # Handle AI turns
        if self.battle_system.state == BattleState.ENEMY_TURN:
            self._execute_enemy_turn()
        
        # Check if battle is over
        if self.battle_system.is_battle_over():
            if self.battle_system.state == BattleState.VICTORY:
                self.message = "Victory!"
                exp, gold = self.battle_system.get_battle_rewards()
                print(f"Battle won! Gained {exp} EXP and {gold} Gold")
            else:
                self.message = "Defeat..."
            self.message_timer = 3.0
            return False
        
        return True
    
    def handle_input(self, event: pygame.event.Event) -> None:
        """Handle input events.
        
        Args:
            event: Pygame event to handle.
        """
        if event.type != pygame.KEYDOWN:
            return
        
        # Handle timing input
        if self.battle_system.state == BattleState.TIMING_COMMAND:
            if event.key == pygame.K_SPACE:
                result = self.battle_system.execute_timing_input()
                self.message = f"Timing: {result.value.upper()}!"
                self.message_timer = 1.0
        
        # Handle player turn input
        elif self.battle_system.state == BattleState.PLAYER_TURN:
            if event.key == pygame.K_UP:
                self.selected_move_index = max(0, self.selected_move_index - 1)
            elif event.key == pygame.K_DOWN:
                self.selected_move_index = min(len(self.moves) - 1, 
                                              self.selected_move_index + 1)
            elif event.key == pygame.K_LEFT:
                self.selected_target_index = max(0, self.selected_target_index - 1)
            elif event.key == pygame.K_RIGHT:
                alive_enemies = self.battle_system.get_alive_enemies()
                self.selected_target_index = min(len(alive_enemies) - 1,
                                                self.selected_target_index + 1)
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                self._confirm_action()
    
    def _confirm_action(self) -> None:
        """Confirm and execute the selected action."""
        if self.battle_system.active_character is None:
            return
        
        move = self.moves[self.selected_move_index]
        
        # Select target
        if move.is_offensive():
            alive_enemies = self.battle_system.get_alive_enemies()
            if not alive_enemies:
                return
            target = alive_enemies[min(self.selected_target_index, len(alive_enemies) - 1)]
        else:
            # Defend targets self
            target = self.battle_system.active_character
        
        # Execute action
        if self.battle_system.select_move_and_target(move, target):
            self.message = f"{self.battle_system.active_character.name} uses {move.name}!"
            self.message_timer = 1.5
        else:
            self.message = "Cannot use that move!"
            self.message_timer = 1.0
    
    def _execute_enemy_turn(self) -> None:
        """Execute an enemy's turn with simple AI."""
        if self.battle_system.active_character is None:
            return
        
        # Simple AI: Pick a random offensive move and target
        offensive_moves = [m for m in self.moves if m.is_offensive()]
        if not offensive_moves:
            return
        
        move = random.choice(offensive_moves)
        alive_heroes = self.battle_system.get_alive_heroes()
        if not alive_heroes:
            return
        
        target = random.choice(alive_heroes)
        
        self.battle_system.select_move_and_target(move, target)
        self.message = f"{self.battle_system.active_character.name} attacks!"
        self.message_timer = 1.5
    
    def render(self) -> None:
        """Render the battle scene."""
        # Clear screen
        self.screen.fill(BACKGROUND_COLOR)
        
        # Render hero panels
        for i, hero in enumerate(self.heroes):
            if i < len(self.hero_panels):
                self.hero_panels[i].render(self.screen, hero)
        
        # Render enemy panels
        for i, enemy in enumerate(self.enemies):
            if i < len(self.enemy_panels):
                self.enemy_panels[i].render(self.screen, enemy)
        
        # Render timing indicator if active
        if self.battle_system.state == BattleState.TIMING_COMMAND:
            progress = self.battle_system.timing_system.get_progress()
            optimal = self.battle_system.timing_system.get_optimal_progress()
            self.timing_indicator.render(self.screen, progress, optimal)
        
        # Render move selection UI
        if self.battle_system.state == BattleState.PLAYER_TURN:
            self._render_move_selection()
        
        # Render battle message
        self._render_message()
    
    def _render_move_selection(self) -> None:
        """Render move selection menu."""
        if self.font is None or self.small_font is None:
            return
        
        menu_x = 50
        menu_y = 200
        
        # Render title
        try:
            title = "Select Move:"
            title_surface = self.font.render(title, True, TEXT_COLOR)
            if title_surface is not None:
                self.screen.blit(title_surface, (menu_x, menu_y))
        except pygame.error:
            pass
        
        # Render moves
        for i, move in enumerate(self.moves[:5]):  # Show first 5 moves
            y = menu_y + 40 + i * 30
            color = (255, 255, 0) if i == self.selected_move_index else TEXT_COLOR
            
            try:
                text = f"> {move.name} (MP: {move.mp_cost})" if i == self.selected_move_index else f"  {move.name} (MP: {move.mp_cost})"
                move_surface = self.small_font.render(text, True, color)
                if move_surface is not None:
                    self.screen.blit(move_surface, (menu_x, y))
            except pygame.error:
                pass
    
    def _render_message(self) -> None:
        """Render battle message."""
        if self.font is None or self.message_timer <= 0.0:
            return
        
        try:
            # Render with shadow for better visibility
            shadow_surface = self.font.render(self.message, True, (0, 0, 0))
            text_surface = self.font.render(self.message, True, TEXT_COLOR)
            
            if shadow_surface is not None and text_surface is not None:
                screen_width = self.screen.get_width()
                x = (screen_width - text_surface.get_width()) // 2
                y = 300
                
                self.screen.blit(shadow_surface, (x + 2, y + 2))
                self.screen.blit(text_surface, (x, y))
        except pygame.error:
            pass
