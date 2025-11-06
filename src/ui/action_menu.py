"""Action menu system for player battle interactions.

This module provides the action menu UI with smooth cursor lerping, nested submenu
support, and frame-perfect input response for battle commands.
"""

import pygame
from typing import List, Callable, Optional, Tuple
from enum import Enum


class MenuOption:
    """Single menu option.
    
    Attributes:
        text: Display text for the option.
        enabled: Whether option can be selected.
        callback: Function to call when selected.
        submenu: Optional submenu to open when selected.
    """
    
    def __init__(self, text: str, callback: Optional[Callable] = None, 
                 enabled: bool = True, submenu: Optional['ActionMenu'] = None):
        """Initialize menu option.
        
        Args:
            text: Display text for the option.
            callback: Function to call when selected (returns None).
            enabled: Whether option is selectable (default True).
            submenu: Submenu to open when selected (default None).
            
        Raises:
            ValueError: If both callback and submenu are provided.
        """
        if callback is not None and submenu is not None:
            raise ValueError("Cannot have both callback and submenu")
            
        self.text = text
        self.callback = callback
        self.enabled = enabled
        self.submenu = submenu


class ActionMenu:
    """Menu for selecting battle actions.
    
    Provides smooth cursor animation, nested submenu support, and responsive input
    handling for battle commands. Supports both keyboard and gamepad input.
    
    Attributes:
        options: List of menu options.
        selected_index: Currently selected option index.
        position: (x, y) screen position of top-left corner.
        visible: Whether menu is currently shown.
        parent_menu: Parent menu for back navigation.
    """
    
    # Visual constants
    WIDTH = 300
    HEIGHT = 200
    OPTION_HEIGHT = 40
    PADDING = 20
    
    # Color constants (RGBA for semi-transparency)
    COLOR_BG = (20, 20, 40, 220)  # Semi-transparent dark blue
    COLOR_BORDER = (100, 100, 150)  # Light border
    COLOR_TEXT_NORMAL = (255, 255, 255)  # White text
    COLOR_TEXT_SELECTED = (255, 255, 100)  # Yellow highlight
    COLOR_TEXT_DISABLED = (100, 100, 100)  # Gray for disabled
    COLOR_CURSOR = (255, 200, 50, 180)  # Semi-transparent gold cursor
    
    # Animation constants
    CURSOR_LERP_SPEED = 12.0  # Higher = faster cursor movement
    INPUT_COOLDOWN = 0.15  # Seconds between inputs (prevents double-taps)
    
    def __init__(self, options: List[MenuOption], position: Tuple[int, int] = (50, 50),
                 parent_menu: Optional['ActionMenu'] = None):
        """Initialize action menu.
        
        Args:
            options: List of MenuOption objects to display.
            position: (x, y) screen position for top-left corner.
            parent_menu: Parent menu for back button navigation (default None).
            
        Raises:
            ValueError: If options list is empty.
        """
        if not options:
            raise ValueError("Menu must have at least one option")
            
        self.options = options
        self.position = position
        self.parent_menu = parent_menu
        self.visible = True
        
        # Find first enabled option
        self.selected_index = 0
        for i, opt in enumerate(options):
            if opt.enabled:
                self.selected_index = i
                break
        
        # Smooth cursor animation
        self.cursor_y_target = self._calculate_cursor_y()
        self.cursor_y_current = self.cursor_y_target
        
        # Input management
        self.input_cooldown_timer = 0.0
        
        # Create surface for semi-transparent background
        self.surface = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
    
    def _calculate_cursor_y(self) -> float:
        """Calculate target Y position for cursor based on selected index.
        
        Returns:
            Y coordinate for cursor position.
        """
        return (self.position[1] + self.PADDING + 
                self.selected_index * self.OPTION_HEIGHT + self.OPTION_HEIGHT // 2)
    
    def update(self, dt: float) -> None:
        """Update menu state with delta time.
        
        Handles cursor lerping animation and input cooldown timing.
        
        Args:
            dt: Delta time in seconds since last frame.
        """
        # Update input cooldown
        if self.input_cooldown_timer > 0:
            self.input_cooldown_timer -= dt
        
        # Smooth cursor movement (lerp)
        self.cursor_y_target = self._calculate_cursor_y()
        diff = self.cursor_y_target - self.cursor_y_current
        self.cursor_y_current += diff * self.CURSOR_LERP_SPEED * dt
        
        # Snap to target if very close (prevents jitter)
        if abs(diff) < 0.5:
            self.cursor_y_current = self.cursor_y_target
    
    def handle_input(self, event: pygame.event.Event) -> Optional[str]:
        """Handle keyboard and gamepad input events.
        
        Frame-perfect input response with cooldown to prevent double-taps.
        Supports both keyboard (WASD/Arrows) and gamepad (D-pad/Left stick).
        
        Args:
            event: Pygame event to process.
        
        Returns:
            Action string: "select", "back", or None if no action taken.
        """
        if not self.visible or self.input_cooldown_timer > 0:
            return None
        
        if event.type == pygame.KEYDOWN:
            # Movement keys - up
            if event.key in (pygame.K_UP, pygame.K_w):
                return self._move_cursor_up()
            
            # Movement keys - down
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                return self._move_cursor_down()
            
            # Select keys
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_z):
                return self._handle_select()
            
            # Back keys
            elif event.key in (pygame.K_ESCAPE, pygame.K_x, pygame.K_BACKSPACE):
                return self._handle_back()
        
        # Gamepad support (D-pad and left stick)
        elif event.type == pygame.JOYHATMOTION:
            if event.value[1] == 1:  # D-pad up
                return self._move_cursor_up()
            elif event.value[1] == -1:  # D-pad down
                return self._move_cursor_down()
        
        elif event.type == pygame.JOYBUTTONDOWN:
            # A button (button 0) = select
            if event.button == 0:
                return self._handle_select()
            # B button (button 1) = back
            elif event.button == 1:
                return self._handle_back()
        
        return None
    
    def _move_cursor_up(self) -> Optional[str]:
        """Move cursor to previous enabled option.
        
        Returns:
            None (movement action).
        """
        original_index = self.selected_index
        
        # Search backwards for enabled option
        for _ in range(len(self.options)):
            self.selected_index = (self.selected_index - 1) % len(self.options)
            if self.options[self.selected_index].enabled:
                if self.selected_index != original_index:
                    self.input_cooldown_timer = self.INPUT_COOLDOWN
                return None
        
        # No enabled options found, stay at current
        self.selected_index = original_index
        return None
    
    def _move_cursor_down(self) -> Optional[str]:
        """Move cursor to next enabled option.
        
        Returns:
            None (movement action).
        """
        original_index = self.selected_index
        
        # Search forwards for enabled option
        for _ in range(len(self.options)):
            self.selected_index = (self.selected_index + 1) % len(self.options)
            if self.options[self.selected_index].enabled:
                if self.selected_index != original_index:
                    self.input_cooldown_timer = self.INPUT_COOLDOWN
                return None
        
        # No enabled options found, stay at current
        self.selected_index = original_index
        return None
    
    def _handle_select(self) -> str:
        """Handle selection of current menu option.
        
        Executes callback or opens submenu if option is enabled.
        
        Returns:
            "select" action string.
        """
        current_option = self.options[self.selected_index]
        
        if not current_option.enabled:
            return None  # Cannot select disabled option
        
        # Execute callback if present
        if current_option.callback is not None:
            current_option.callback()
        
        # Open submenu if present
        if current_option.submenu is not None:
            current_option.submenu.visible = True
            self.visible = False  # Hide current menu
        
        self.input_cooldown_timer = self.INPUT_COOLDOWN
        return "select"
    
    def _handle_back(self) -> str:
        """Handle back button to return to parent menu.
        
        Returns:
            "back" action string.
        """
        if self.parent_menu is not None:
            self.visible = False
            self.parent_menu.visible = True
        
        self.input_cooldown_timer = self.INPUT_COOLDOWN
        return "back"
    
    def render(self, screen: pygame.Surface) -> None:
        """Render menu to screen.
        
        Draws semi-transparent background, border, options, and animated cursor.
        
        Args:
            screen: Pygame surface to render onto.
        """
        if not self.visible:
            return
        
        # Clear surface
        self.surface.fill((0, 0, 0, 0))
        
        # Draw background
        pygame.draw.rect(self.surface, self.COLOR_BG, 
                        (0, 0, self.WIDTH, self.HEIGHT))
        
        # Draw border
        pygame.draw.rect(self.surface, self.COLOR_BORDER, 
                        (0, 0, self.WIDTH, self.HEIGHT), 2)
        
        # Draw cursor (smooth animated)
        cursor_x = self.PADDING // 2
        cursor_y_relative = (self.cursor_y_current - self.position[1] - 
                            self.OPTION_HEIGHT // 4)
        cursor_width = self.WIDTH - self.PADDING
        cursor_height = self.OPTION_HEIGHT - 4
        
        pygame.draw.rect(self.surface, self.COLOR_CURSOR,
                        (cursor_x, cursor_y_relative, cursor_width, cursor_height),
                        border_radius=5)
        
        # Draw options
        font = pygame.font.Font(None, 32)
        
        for i, option in enumerate(self.options):
            # Determine text color based on state
            if not option.enabled:
                color = self.COLOR_TEXT_DISABLED
            elif i == self.selected_index:
                color = self.COLOR_TEXT_SELECTED
            else:
                color = self.COLOR_TEXT_NORMAL
            
            # Render text
            text_surface = font.render(option.text, True, color)
            text_x = self.PADDING
            text_y = (self.PADDING + i * self.OPTION_HEIGHT + 
                      (self.OPTION_HEIGHT - text_surface.get_height()) // 2)
            
            self.surface.blit(text_surface, (text_x, text_y))
        
        # Blit menu surface to screen
        screen.blit(self.surface, self.position)
    
    def get_selected_option(self) -> Optional[MenuOption]:
        """Get currently selected menu option.
        
        Returns:
            Currently selected MenuOption, or None if menu empty.
        """
        if 0 <= self.selected_index < len(self.options):
            return self.options[self.selected_index]
        return None
    
    def set_option_enabled(self, index: int, enabled: bool) -> None:
        """Enable or disable a menu option.
        
        Useful for dynamically disabling options (e.g., insufficient MP).
        
        Args:
            index: Index of option to modify.
            enabled: Whether option should be enabled.
            
        Raises:
            IndexError: If index is out of range.
        """
        if index < 0 or index >= len(self.options):
            raise IndexError(f"Option index {index} out of range")
        
        self.options[index].enabled = enabled
        
        # If current selection becomes disabled, move to next enabled
        if index == self.selected_index and not enabled:
            self._move_cursor_down()
    
    def show(self) -> None:
        """Show the menu."""
        self.visible = True
    
    def hide(self) -> None:
        """Hide the menu."""
        self.visible = False
