"""UI components for rendering battle elements.

This module provides UI components for rendering health bars, ATB gauges,
character info, and other battle UI elements.
"""

import pygame
from typing import Tuple, Optional
from src.entities.character import Character


# Constants
HP_BAR_COLOR = (0, 200, 0)
MP_BAR_COLOR = (0, 100, 255)
ATB_BAR_COLOR = (255, 200, 0)
BAR_BACKGROUND_COLOR = (50, 50, 50)
BAR_BORDER_COLOR = (255, 255, 255)
TEXT_COLOR = (255, 255, 255)
SHADOW_COLOR = (0, 0, 0)


class UIBar:
    """Renders a status bar (HP, MP, ATB, etc.).
    
    Attributes:
        x: X position of the bar.
        y: Y position of the bar.
        width: Width of the bar in pixels.
        height: Height of the bar in pixels.
        color: RGB color tuple for the filled portion.
        bg_color: RGB color tuple for the background.
        border_color: RGB color tuple for the border.
        show_border: Whether to draw a border.
    """
    
    def __init__(self, x: int, y: int, width: int, height: int,
                 color: Tuple[int, int, int] = HP_BAR_COLOR,
                 bg_color: Tuple[int, int, int] = BAR_BACKGROUND_COLOR,
                 border_color: Tuple[int, int, int] = BAR_BORDER_COLOR,
                 show_border: bool = True) -> None:
        """Initialize a UI bar.
        
        Args:
            x: X position of the bar.
            y: Y position of the bar.
            width: Width of the bar in pixels.
            height: Height of the bar in pixels.
            color: RGB color for the filled portion.
            bg_color: RGB color for the background.
            border_color: RGB color for the border.
            show_border: Whether to draw a border.
        """
        self.x: int = x
        self.y: int = y
        self.width: int = width
        self.height: int = height
        self.color: Tuple[int, int, int] = color
        self.bg_color: Tuple[int, int, int] = bg_color
        self.border_color: Tuple[int, int, int] = border_color
        self.show_border: bool = show_border
    
    def render(self, surface: pygame.Surface, percentage: float) -> None:
        """Render the bar to a surface.
        
        Args:
            surface: Pygame surface to render to.
            percentage: Fill percentage (0.0 to 1.0).
        """
        if surface is None:
            return
        
        # Clamp percentage
        percentage = max(0.0, min(1.0, percentage))
        
        # Draw background
        bg_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(surface, self.bg_color, bg_rect)
        
        # Draw filled portion
        if percentage > 0.0:
            fill_width = int(self.width * percentage)
            fill_rect = pygame.Rect(self.x, self.y, fill_width, self.height)
            pygame.draw.rect(surface, self.color, fill_rect)
        
        # Draw border
        if self.show_border:
            pygame.draw.rect(surface, self.border_color, bg_rect, 2)


class CharacterInfoPanel:
    """Renders character information panel.
    
    Displays character name, HP, MP, and ATB gauge.
    
    Attributes:
        x: X position of the panel.
        y: Y position of the panel.
        width: Width of the panel.
        font: Pygame font for text rendering.
        hp_bar: HP bar component.
        mp_bar: MP bar component.
        atb_bar: ATB bar component.
    """
    
    def __init__(self, x: int, y: int, width: int = 250) -> None:
        """Initialize character info panel.
        
        Args:
            x: X position of the panel.
            y: Y position of the panel.
            width: Width of the panel in pixels.
        """
        self.x: int = x
        self.y: int = y
        self.width: int = width
        
        try:
            self.font: pygame.font.Font = pygame.font.Font(None, 24)
        except pygame.error:
            self.font = None
        
        bar_width = width - 10
        self.hp_bar: UIBar = UIBar(x + 5, y + 25, bar_width, 15, HP_BAR_COLOR)
        self.mp_bar: UIBar = UIBar(x + 5, y + 45, bar_width, 15, MP_BAR_COLOR)
        self.atb_bar: UIBar = UIBar(x + 5, y + 65, bar_width, 20, ATB_BAR_COLOR)
    
    def render(self, surface: pygame.Surface, character: Character) -> None:
        """Render character info to surface.
        
        Args:
            surface: Pygame surface to render to.
            character: Character to display info for.
        """
        if surface is None or character is None:
            return
        
        # Render name
        if self.font is not None:
            name_text = f"{character.name}"
            try:
                name_surface = self.font.render(name_text, True, TEXT_COLOR)
                if name_surface is not None:
                    surface.blit(name_surface, (self.x + 5, self.y))
            except pygame.error:
                pass
        
        # Render HP bar
        self.hp_bar.render(surface, character.get_hp_percentage())
        
        # Render HP text
        if self.font is not None:
            hp_text = f"HP: {character.current_hp}/{character.max_hp}"
            try:
                hp_surface = self.font.render(hp_text, True, TEXT_COLOR)
                if hp_surface is not None:
                    surface.blit(hp_surface, (self.x + self.width - 100, self.y + 24))
            except pygame.error:
                pass
        
        # Render MP bar (if character has MP)
        if character.max_mp > 0:
            self.mp_bar.render(surface, character.get_mp_percentage())
            
            if self.font is not None:
                mp_text = f"MP: {character.current_mp}/{character.max_mp}"
                try:
                    mp_surface = self.font.render(mp_text, True, TEXT_COLOR)
                    if mp_surface is not None:
                        surface.blit(mp_surface, (self.x + self.width - 100, self.y + 44))
                except pygame.error:
                    pass
        
        # Render ATB bar
        self.atb_bar.render(surface, character.get_atb_percentage())


class TimingIndicator:
    """Renders timing indicator for action commands.
    
    Displays a progress bar with an optimal timing marker for the player
    to execute timed button presses.
    
    Attributes:
        x: X position of the indicator.
        y: Y position of the indicator.
        width: Width of the indicator.
        height: Height of the indicator.
    """
    
    def __init__(self, x: int, y: int, width: int = 400, height: int = 40) -> None:
        """Initialize timing indicator.
        
        Args:
            x: X position of the indicator.
            y: Y position of the indicator.
            width: Width in pixels.
            height: Height in pixels.
        """
        self.x: int = x
        self.y: int = y
        self.width: int = width
        self.height: int = height
        
        try:
            self.font: pygame.font.Font = pygame.font.Font(None, 32)
        except pygame.error:
            self.font = None
    
    def render(self, surface: pygame.Surface, progress: float, 
               optimal_progress: float) -> None:
        """Render timing indicator to surface.
        
        Args:
            surface: Pygame surface to render to.
            progress: Current progress (0.0 to 1.0).
            optimal_progress: Optimal timing point (0.0 to 1.0).
        """
        if surface is None:
            return
        
        # Clamp values
        progress = max(0.0, min(1.0, progress))
        optimal_progress = max(0.0, min(1.0, optimal_progress))
        
        # Draw background
        bg_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(surface, BAR_BACKGROUND_COLOR, bg_rect)
        
        # Draw optimal zone (larger area around optimal point)
        zone_width = 40
        zone_x = self.x + int(self.width * optimal_progress) - zone_width // 2
        zone_rect = pygame.Rect(zone_x, self.y, zone_width, self.height)
        pygame.draw.rect(surface, (100, 200, 100), zone_rect)
        
        # Draw optimal line
        optimal_x = self.x + int(self.width * optimal_progress)
        pygame.draw.line(surface, (0, 255, 0), 
                        (optimal_x, self.y), 
                        (optimal_x, self.y + self.height), 3)
        
        # Draw progress indicator
        indicator_x = self.x + int(self.width * progress)
        indicator_rect = pygame.Rect(indicator_x - 3, self.y - 5, 6, self.height + 10)
        pygame.draw.rect(surface, (255, 255, 0), indicator_rect)
        
        # Draw border
        pygame.draw.rect(surface, BAR_BORDER_COLOR, bg_rect, 2)
        
        # Draw instruction text
        if self.font is not None:
            text = "Press SPACE at the right moment!"
            try:
                text_surface = self.font.render(text, True, TEXT_COLOR)
                if text_surface is not None:
                    text_x = self.x + (self.width - text_surface.get_width()) // 2
                    surface.blit(text_surface, (text_x, self.y - 40))
            except pygame.error:
                pass
