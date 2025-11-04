"""Asset manager for loading and caching game assets.

This module provides a singleton AssetManager that handles loading sprites,
fonts, and other assets with caching and placeholder generation for missing files.
"""

import pygame
import os
from typing import Dict, Optional, Tuple


class AssetManager:
    """Singleton manager for loading and caching game assets.
    
    The AssetManager implements lazy loading and caching to prevent loading
    the same asset multiple times. It automatically converts surfaces for
    optimal rendering performance and generates placeholders for missing files.
    
    Attributes:
        _instance: Singleton instance reference.
        _initialized: Whether the instance has been initialized.
        _sprites: Cache of loaded sprite surfaces.
        _fonts: Cache of loaded fonts.
        sprite_path: Base path for sprite files.
    """
    
    _instance: Optional['AssetManager'] = None
    
    def __new__(cls):
        """Create or return the singleton instance.
        
        Returns:
            The single AssetManager instance.
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self) -> None:
        """Initialize the asset manager.
        
        Only initializes once due to singleton pattern.
        """
        if self._initialized:
            return
        self._initialized = True
        self._sprites: Dict[str, pygame.Surface] = {}
        self._fonts: Dict[Tuple[Optional[str], int], pygame.font.Font] = {}
        self.sprite_path = "assets/sprites"
    
    def load_sprite(self, filename: str, use_alpha: bool = True) -> pygame.Surface:
        """Load sprite from file or return cached version.
        
        Args:
            filename: Name of sprite file (e.g., "hero.png").
            use_alpha: If True, use convert_alpha() for transparency.
        
        Returns:
            Loaded and converted pygame Surface.
        """
        if filename in self._sprites:
            return self._sprites[filename]
        
        filepath = os.path.join(self.sprite_path, filename)
        
        try:
            surface = pygame.image.load(filepath)
            if use_alpha:
                surface = surface.convert_alpha()
            else:
                surface = surface.convert()
            self._sprites[filename] = surface
            return surface
        except (pygame.error, FileNotFoundError) as e:
            print(f"Warning: Could not load {filepath}, using placeholder: {e}")
            # Generate placeholder
            placeholder = self._generate_placeholder(64, 64, (255, 0, 255), filename)
            self._sprites[filename] = placeholder
            return placeholder
    
    def get_font(self, size: int, font_name: Optional[str] = None) -> pygame.font.Font:
        """Get font, creating and caching if needed.
        
        Args:
            size: Font size in pixels.
            font_name: Font file name, or None for default.
        
        Returns:
            Pygame Font object.
        """
        key = (font_name, size)
        if key not in self._fonts:
            try:
                self._fonts[key] = pygame.font.Font(font_name, size)
            except (pygame.error, FileNotFoundError):
                # Fallback to system font if specified font fails
                self._fonts[key] = pygame.font.Font(None, size)
        return self._fonts[key]
    
    def _generate_placeholder(self, width: int, height: int, 
                             color: Tuple[int, int, int], label: str) -> pygame.Surface:
        """Generate placeholder surface.
        
        Args:
            width: Width in pixels.
            height: Height in pixels.
            color: RGB tuple.
            label: Text to display on placeholder.
        
        Returns:
            Generated Surface with label.
        """
        surface = pygame.Surface((width, height))
        surface.fill(color)
        
        # Draw border
        pygame.draw.rect(surface, (0, 0, 0), surface.get_rect(), 2)
        
        # Draw label (truncate if too long)
        font = pygame.font.Font(None, 20)
        display_label = label[:10] + "..." if len(label) > 10 else label
        try:
            text = font.render(display_label, True, (0, 0, 0))
            text_rect = text.get_rect(center=(width // 2, height // 2))
            surface.blit(text, text_rect)
        except pygame.error:
            # If rendering fails, just use the colored rectangle
            pass
        
        return surface.convert_alpha()
    
    def clear_cache(self) -> None:
        """Clear all cached assets. Useful for reloading during development."""
        self._sprites.clear()
        self._fonts.clear()
