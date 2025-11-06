"""Tests for animation system."""

import pytest
import pygame
from unittest.mock import Mock, MagicMock
from src.utils.animation import AnimationFrame, Animation, AnimationController


@pytest.fixture
def mock_pygame():
    """Mock pygame module."""
    # Initialize pygame for tests
    pygame.init()
    yield pygame
    pygame.quit()


@pytest.fixture
def sample_surface(mock_pygame):
    """Create sample pygame surface."""
    return pygame.Surface((64, 64))


@pytest.fixture
def sample_frames(sample_surface):
    """Create sample animation frames."""
    return [
        AnimationFrame(sample_surface, 0.1),
        AnimationFrame(sample_surface, 0.2),
        AnimationFrame(sample_surface, 0.15)
    ]


# AnimationFrame Tests

def test_animation_frame_creation(sample_surface):
    """Test creating an animation frame."""
    frame = AnimationFrame(sample_surface, 0.5)
    assert frame.surface == sample_surface
    assert frame.duration == 0.5


def test_animation_frame_negative_duration(sample_surface):
    """Test that negative duration raises error."""
    with pytest.raises(ValueError, match="Frame duration must be positive"):
        AnimationFrame(sample_surface, -0.1)


def test_animation_frame_zero_duration(sample_surface):
    """Test that zero duration raises error."""
    with pytest.raises(ValueError, match="Frame duration must be positive"):
        AnimationFrame(sample_surface, 0.0)


# Animation Tests - Initialization

def test_animation_creation_looping(sample_frames):
    """Test creating a looping animation."""
    anim = Animation(sample_frames, loop=True)
    assert anim.frames == sample_frames
    assert anim.loop is True
    assert anim.current_frame_index == 0
    assert anim.time_in_frame == 0.0
    assert anim.finished is False
    assert anim.paused is False


def test_animation_creation_nonlooping(sample_frames):
    """Test creating a non-looping animation."""
    anim = Animation(sample_frames, loop=False)
    assert anim.loop is False
    assert anim.finished is False


def test_animation_empty_frames():
    """Test that empty frames list raises error."""
    with pytest.raises(ValueError, match="Animation must have at least one frame"):
        Animation([])


def test_animation_with_callback(sample_frames):
    """Test animation with completion callback."""
    callback = Mock()
    anim = Animation(sample_frames, loop=False, on_complete=callback)
    assert anim.on_complete == callback


# Animation Tests - Update and Frame Advancement

def test_animation_update_advances_frame(sample_frames):
    """Test that update advances to next frame."""
    anim = Animation(sample_frames, loop=True)
    
    # Advance past first frame duration
    changed = anim.update(0.15)
    assert changed is True
    assert anim.current_frame_index == 1


def test_animation_update_accumulates_time(sample_frames):
    """Test that time accumulates within frame."""
    anim = Animation(sample_frames, loop=True)
    
    # Update with less than frame duration
    changed = anim.update(0.05)
    assert changed is False
    assert anim.current_frame_index == 0
    assert anim.time_in_frame == 0.05


def test_animation_update_multiple_frames(sample_frames):
    """Test advancing multiple frames in one update."""
    anim = Animation(sample_frames, loop=True)
    
    # Advance past first two frames (0.1 + 0.2 = 0.3)
    changed = anim.update(0.35)
    assert changed is True
    assert anim.current_frame_index == 2


def test_animation_looping_wraps_around(sample_frames):
    """Test that looping animation wraps to first frame."""
    anim = Animation(sample_frames, loop=True)
    
    # Advance past all frames (0.1 + 0.2 + 0.15 = 0.45)
    anim.update(0.5)
    assert anim.current_frame_index == 0
    assert anim.finished is False


def test_animation_nonlooping_stops_at_end(sample_frames):
    """Test that non-looping animation stops at last frame."""
    anim = Animation(sample_frames, loop=False)
    
    # Advance past all frames
    anim.update(0.5)
    assert anim.current_frame_index == 2  # Last frame
    assert anim.finished is True


def test_animation_nonlooping_calls_callback(sample_frames):
    """Test that non-looping animation calls completion callback."""
    callback = Mock()
    anim = Animation(sample_frames, loop=False, on_complete=callback)
    
    # Advance past all frames
    anim.update(0.5)
    callback.assert_called_once()


def test_animation_finished_doesnt_update(sample_frames):
    """Test that finished animation doesn't update."""
    anim = Animation(sample_frames, loop=False)
    
    # Finish the animation
    anim.update(0.5)
    assert anim.finished is True
    
    # Try to update again
    changed = anim.update(0.1)
    assert changed is False
    assert anim.current_frame_index == 2


# Animation Tests - Pause/Resume

def test_animation_pause(sample_frames):
    """Test pausing animation."""
    anim = Animation(sample_frames, loop=True)
    anim.pause()
    
    changed = anim.update(0.2)
    assert changed is False
    assert anim.current_frame_index == 0


def test_animation_resume(sample_frames):
    """Test resuming paused animation."""
    anim = Animation(sample_frames, loop=True)
    anim.pause()
    anim.resume()
    
    changed = anim.update(0.15)
    assert changed is True
    assert anim.current_frame_index == 1


# Animation Tests - Get Frame

def test_get_current_frame(sample_frames):
    """Test getting current frame surface."""
    anim = Animation(sample_frames, loop=True)
    surface = anim.get_current_frame()
    assert surface == sample_frames[0].surface


def test_get_current_frame_after_update(sample_frames):
    """Test getting frame after update."""
    anim = Animation(sample_frames, loop=True)
    anim.update(0.15)
    surface = anim.get_current_frame()
    assert surface == sample_frames[1].surface


# Animation Tests - Reset

def test_animation_reset(sample_frames):
    """Test resetting animation to start."""
    anim = Animation(sample_frames, loop=True)
    
    # Advance animation (0.1 + 0.2 = 0.3 for first two frames)
    anim.update(0.35)
    # Should be in frame 2 after 0.35 seconds
    assert anim.current_frame_index == 2
    
    # Reset
    anim.reset()
    assert anim.current_frame_index == 0
    assert anim.time_in_frame == 0.0
    assert anim.finished is False


def test_animation_reset_finished(sample_frames):
    """Test resetting finished animation."""
    anim = Animation(sample_frames, loop=False)
    
    # Finish animation
    anim.update(0.5)
    assert anim.finished is True
    
    # Reset
    anim.reset()
    assert anim.finished is False
    assert anim.current_frame_index == 0


# Animation Tests - Progress

def test_animation_progress_start(sample_frames):
    """Test progress at start of animation."""
    anim = Animation(sample_frames, loop=True)
    assert anim.get_progress() == 0.0


def test_animation_progress_middle(sample_frames):
    """Test progress in middle of animation."""
    anim = Animation(sample_frames, loop=True)
    # Total duration: 0.1 + 0.2 + 0.15 = 0.45
    # After 0.225 seconds, we're at 50%
    anim.update(0.225)
    progress = anim.get_progress()
    assert 0.49 < progress < 0.51  # Allow small floating point error


def test_animation_progress_end(sample_frames):
    """Test progress at end of animation."""
    anim = Animation(sample_frames, loop=False)
    # Total duration: 0.1 + 0.2 + 0.15 = 0.45
    # Advance past all frames to reach 100%
    anim.update(0.45)
    progress = anim.get_progress()
    assert progress >= 0.99  # Allow for floating point precision


# AnimationController Tests

def test_controller_creation():
    """Test creating animation controller."""
    controller = AnimationController()
    assert controller.is_empty() is True


def test_controller_add_animation(sample_frames):
    """Test adding animation to controller."""
    controller = AnimationController()
    anim = Animation(sample_frames, loop=True)
    
    controller.add_animation("test", anim)
    assert controller.has_animation("test") is True
    assert controller.get_animation("test") == anim


def test_controller_add_duplicate_name(sample_frames):
    """Test that adding duplicate name raises error."""
    controller = AnimationController()
    anim1 = Animation(sample_frames, loop=True)
    anim2 = Animation(sample_frames, loop=True)
    
    controller.add_animation("test", anim1)
    with pytest.raises(ValueError, match="Animation 'test' already exists"):
        controller.add_animation("test", anim2)


def test_controller_remove_animation(sample_frames):
    """Test removing animation from controller."""
    controller = AnimationController()
    anim = Animation(sample_frames, loop=True)
    
    controller.add_animation("test", anim)
    result = controller.remove_animation("test")
    
    assert result is True
    assert controller.has_animation("test") is False


def test_controller_remove_nonexistent():
    """Test removing nonexistent animation returns False."""
    controller = AnimationController()
    result = controller.remove_animation("nonexistent")
    assert result is False


def test_controller_update_all(sample_frames):
    """Test updating all animations in controller."""
    controller = AnimationController()
    anim1 = Animation(sample_frames, loop=True)
    anim2 = Animation(sample_frames, loop=True)
    
    controller.add_animation("anim1", anim1)
    controller.add_animation("anim2", anim2)
    
    controller.update(0.15)
    
    assert anim1.current_frame_index == 1
    assert anim2.current_frame_index == 1


def test_controller_removes_finished_animations(sample_frames):
    """Test that finished animations are auto-removed."""
    controller = AnimationController()
    anim = Animation(sample_frames, loop=False)
    
    controller.add_animation("test", anim)
    controller.update(0.5)  # Finish the animation
    
    # Next update should remove it
    controller.update(0.01)
    assert controller.has_animation("test") is False


def test_controller_get_nonexistent():
    """Test getting nonexistent animation returns None."""
    controller = AnimationController()
    anim = controller.get_animation("nonexistent")
    assert anim is None


def test_controller_clear(sample_frames):
    """Test clearing all animations."""
    controller = AnimationController()
    controller.add_animation("anim1", Animation(sample_frames, loop=True))
    controller.add_animation("anim2", Animation(sample_frames, loop=True))
    
    controller.clear()
    assert controller.is_empty() is True


def test_controller_multiple_simultaneous(sample_frames):
    """Test multiple animations running simultaneously."""
    controller = AnimationController()
    
    # Add multiple animations with different progress
    for i in range(5):
        anim = Animation(sample_frames, loop=True)
        controller.add_animation(f"anim{i}", anim)
    
    # Update all
    controller.update(0.15)
    
    # All should have advanced
    for i in range(5):
        anim = controller.get_animation(f"anim{i}")
        assert anim.current_frame_index == 1


def test_controller_memory_efficiency(sample_frames):
    """Test that multiple animations can share same frame data."""
    controller = AnimationController()
    
    # Create multiple animations using same frames
    anim1 = Animation(sample_frames, loop=True)
    anim2 = Animation(sample_frames, loop=True)
    
    controller.add_animation("anim1", anim1)
    controller.add_animation("anim2", anim2)
    
    # Both should reference same frame data
    assert anim1.frames is sample_frames
    assert anim2.frames is sample_frames
    assert anim1.frames is anim2.frames
