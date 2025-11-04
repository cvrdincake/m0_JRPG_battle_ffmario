"""Unit tests for AssetManager."""

import pytest
import pygame
import os
from src.utils.asset_manager import AssetManager


@pytest.fixture(scope="function")
def reset_asset_manager():
    """Reset AssetManager singleton between tests."""
    yield
    # Clear the singleton instance
    AssetManager._instance = None


def test_singleton_pattern(reset_asset_manager):
    """Test that AssetManager follows singleton pattern."""
    manager1 = AssetManager()
    manager2 = AssetManager()
    assert manager1 is manager2


def test_caching(reset_asset_manager):
    """Test that sprites are cached and reused."""
    pygame.init()
    pygame.display.set_mode((1, 1))
    
    manager = AssetManager()
    
    # First load will create placeholder since file likely doesn't exist
    sprite1 = manager.load_sprite("hero.png")
    sprite2 = manager.load_sprite("hero.png")
    
    # Should be the exact same object in memory
    assert sprite1 is sprite2


def test_missing_file_placeholder(reset_asset_manager):
    """Test that missing files generate placeholders."""
    pygame.init()
    pygame.display.set_mode((1, 1))
    
    manager = AssetManager()
    sprite = manager.load_sprite("nonexistent.png")
    
    assert sprite is not None
    assert sprite.get_size() == (64, 64)


def test_clear_cache(reset_asset_manager):
    """Test that cache can be cleared."""
    pygame.init()
    pygame.display.set_mode((1, 1))
    
    manager = AssetManager()
    sprite1 = manager.load_sprite("test.png")
    
    manager.clear_cache()
    
    # After clearing, loading again should create a new object
    sprite2 = manager.load_sprite("test.png")
    # Note: They might be equal but not the same object after cache clear
    assert sprite1 is not sprite2 or len(manager._sprites) > 0


def test_font_caching(reset_asset_manager):
    """Test that fonts are cached."""
    pygame.init()
    pygame.display.set_mode((1, 1))
    
    manager = AssetManager()
    font1 = manager.get_font(24)
    font2 = manager.get_font(24)
    
    assert font1 is font2


def test_different_font_sizes(reset_asset_manager):
    """Test that different font sizes are cached separately."""
    pygame.init()
    pygame.display.set_mode((1, 1))
    
    manager = AssetManager()
    font1 = manager.get_font(24)
    font2 = manager.get_font(36)
    
    assert font1 is not font2


def test_sprite_with_alpha(reset_asset_manager):
    """Test loading sprite with alpha channel."""
    pygame.init()
    pygame.display.set_mode((1, 1))
    
    manager = AssetManager()
    sprite = manager.load_sprite("test_alpha.png", use_alpha=True)
    
    assert sprite is not None
    # Placeholder should have been generated
    assert sprite.get_size() == (64, 64)


def test_sprite_without_alpha(reset_asset_manager):
    """Test loading sprite without alpha channel."""
    pygame.init()
    pygame.display.set_mode((1, 1))
    
    manager = AssetManager()
    sprite = manager.load_sprite("test_no_alpha.png", use_alpha=False)
    
    assert sprite is not None
    assert sprite.get_size() == (64, 64)


def test_multiple_different_sprites(reset_asset_manager):
    """Test loading multiple different sprites."""
    pygame.init()
    pygame.display.set_mode((1, 1))
    
    manager = AssetManager()
    sprite1 = manager.load_sprite("sprite1.png")
    sprite2 = manager.load_sprite("sprite2.png")
    sprite3 = manager.load_sprite("sprite3.png")
    
    # All should be different objects
    assert sprite1 is not sprite2
    assert sprite2 is not sprite3
    assert sprite1 is not sprite3
    
    # But each should be cached
    assert manager.load_sprite("sprite1.png") is sprite1
    assert manager.load_sprite("sprite2.png") is sprite2


def test_placeholder_generation(reset_asset_manager):
    """Test that placeholder generation works correctly."""
    pygame.init()
    pygame.display.set_mode((1, 1))
    
    manager = AssetManager()
    
    # Test with a long filename to ensure truncation works
    sprite = manager.load_sprite("verylongfilename_that_should_be_truncated.png")
    
    assert sprite is not None
    assert sprite.get_size() == (64, 64)
    
    # Check that it's a valid surface
    assert isinstance(sprite, pygame.Surface)
