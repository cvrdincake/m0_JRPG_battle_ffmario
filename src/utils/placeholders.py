"""Placeholder sprite generator for game assets.

This module generates placeholder sprites programmatically when actual
art assets are not available. All sprites are saved as PNG files.
"""

import pygame
import os
from typing import Tuple


def generate_character_sprite(width: int, height: int, 
                              color: Tuple[int, int, int], label: str, 
                              save_path: str) -> None:
    """Generate and save character placeholder sprite.
    
    Args:
        width: Sprite width in pixels.
        height: Sprite height in pixels.
        color: RGB color tuple.
        label: Text label for sprite.
        save_path: Full path where PNG will be saved.
    """
    surface = pygame.Surface((width, height), pygame.SRCALPHA)
    
    # Draw body (rounded rectangle effect with circles)
    body_rect = pygame.Rect(width // 4, height // 4, width // 2, height // 2)
    pygame.draw.ellipse(surface, color, body_rect)
    
    # Draw head
    head_radius = width // 6
    head_center = (width // 2, height // 3)
    pygame.draw.circle(surface, color, head_center, head_radius)
    
    # Draw border
    pygame.draw.rect(surface, (0, 0, 0), surface.get_rect(), 2)
    
    # Draw label
    font = pygame.font.Font(None, 16)
    text = font.render(label, True, (255, 255, 255))
    text_rect = text.get_rect(center=(width // 2, height - 10))
    
    # Text background for readability
    bg_rect = text_rect.inflate(4, 2)
    pygame.draw.rect(surface, (0, 0, 0), bg_rect)
    surface.blit(text, text_rect)
    
    # Save
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    pygame.image.save(surface, save_path)


def generate_enemy_sprite(width: int, height: int, 
                         color: Tuple[int, int, int], label: str, 
                         save_path: str) -> None:
    """Generate and save enemy placeholder sprite (more angular).
    
    Args:
        width: Sprite width in pixels.
        height: Sprite height in pixels.
        color: RGB color tuple.
        label: Text label for sprite.
        save_path: Full path where PNG will be saved.
    """
    surface = pygame.Surface((width, height), pygame.SRCALPHA)
    
    # Draw angular body (triangle-ish)
    points = [
        (width // 2, height // 6),  # Top
        (width // 6, height * 5 // 6),  # Bottom left
        (width * 5 // 6, height * 5 // 6)  # Bottom right
    ]
    pygame.draw.polygon(surface, color, points)
    pygame.draw.polygon(surface, (0, 0, 0), points, 2)
    
    # Draw eyes (menacing)
    eye_size = width // 12
    left_eye = (width // 3, height // 3)
    right_eye = (width * 2 // 3, height // 3)
    pygame.draw.circle(surface, (255, 0, 0), left_eye, eye_size)
    pygame.draw.circle(surface, (255, 0, 0), right_eye, eye_size)
    
    # Label
    font = pygame.font.Font(None, 16)
    text = font.render(label, True, (255, 255, 255))
    text_rect = text.get_rect(center=(width // 2, height - 10))
    bg_rect = text_rect.inflate(4, 2)
    pygame.draw.rect(surface, (0, 0, 0), bg_rect)
    surface.blit(text, text_rect)
    
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    pygame.image.save(surface, save_path)


def generate_ui_panel(width: int, height: int, save_path: str) -> None:
    """Generate semi-transparent UI panel.
    
    Args:
        width: Panel width in pixels.
        height: Panel height in pixels.
        save_path: Full path where PNG will be saved.
    """
    surface = pygame.Surface((width, height), pygame.SRCALPHA)
    
    # Semi-transparent background
    background = pygame.Surface((width, height))
    background.fill((20, 20, 40))
    background.set_alpha(200)
    surface.blit(background, (0, 0))
    
    # Border
    pygame.draw.rect(surface, (100, 100, 150), surface.get_rect(), 3)
    
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    pygame.image.save(surface, save_path)


def generate_all_placeholders() -> None:
    """Generate all placeholder assets for the game."""
    pygame.init()
    pygame.display.set_mode((1, 1))  # Minimal display for rendering
    
    # Characters
    generate_character_sprite(64, 64, (50, 100, 255), "HERO", "assets/sprites/hero.png")
    generate_character_sprite(64, 64, (100, 255, 100), "MAGE", "assets/sprites/mage.png")
    generate_character_sprite(64, 64, (255, 200, 50), "ROGUE", "assets/sprites/rogue.png")
    
    # Enemies
    generate_enemy_sprite(80, 80, (255, 100, 100), "SLIME", "assets/sprites/slime.png")
    generate_enemy_sprite(96, 96, (150, 75, 50), "GOBLIN", "assets/sprites/goblin.png")
    generate_enemy_sprite(120, 120, (200, 50, 50), "DRAGON", "assets/sprites/dragon.png")
    
    # UI
    generate_ui_panel(300, 600, "assets/sprites/party_panel.png")
    generate_ui_panel(600, 120, "assets/sprites/message_log.png")
    
    print("All placeholders generated successfully!")


if __name__ == "__main__":
    generate_all_placeholders()
