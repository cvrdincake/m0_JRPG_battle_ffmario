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
    """Test that adding duplicate name overwrites (no longer raises error)."""
    controller = AnimationController()
    anim1 = Animation(sample_frames, loop=True)
    anim2 = Animation(sample_frames, loop=True)
    
    controller.add_animation("test", anim1)
    # Second add should overwrite
    controller.add_animation("test", anim2)
    assert controller.get_animation("test") == anim2


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


# AnimationController Tests - Single Animation Mode

def test_controller_play(sample_frames):
    """Test playing named animation."""
    controller = AnimationController()
    anim = Animation(sample_frames, loop=True)
    
    controller.add_animation("test", anim)
    result = controller.play("test")
    
    assert result is True
    assert controller.current_animation_name == "test"
    assert anim.paused is False


def test_controller_play_nonexistent():
    """Test playing nonexistent animation returns False."""
    controller = AnimationController()
    result = controller.play("nonexistent")
    assert result is False
    assert controller.current_animation_name is None


def test_controller_play_with_reset(sample_frames):
    """Test playing animation with reset."""
    controller = AnimationController()
    anim = Animation(sample_frames, loop=True)
    
    controller.add_animation("test", anim)
    
    # Advance animation
    controller.play("test")
    controller.update(0.15)
    assert anim.current_frame_index == 1
    
    # Play with reset
    controller.play("test", reset=True)
    assert anim.current_frame_index == 0


def test_controller_play_without_reset(sample_frames):
    """Test playing animation without reset continues from current position."""
    controller = AnimationController()
    anim = Animation(sample_frames, loop=True)
    
    controller.add_animation("test", anim)
    
    # Advance animation
    controller.play("test")
    controller.update(0.15)
    frame_before = anim.current_frame_index
    
    # Play without reset
    controller.play("test", reset=False)
    assert anim.current_frame_index == frame_before


def test_controller_stop():
    """Test stopping current animation."""
    controller = AnimationController()
    controller.current_animation_name = "test"
    
    controller.stop()
    assert controller.current_animation_name is None


def test_controller_update_single_mode(sample_frames):
    """Test update in single-animation mode."""
    controller = AnimationController()
    anim1 = Animation(sample_frames, loop=True)
    anim2 = Animation(sample_frames, loop=True)
    
    controller.add_animation("anim1", anim1)
    controller.add_animation("anim2", anim2)
    
    # Play only anim1
    controller.play("anim1")
    controller.update(0.15)
    
    # Only anim1 should advance
    assert anim1.current_frame_index == 1
    assert anim2.current_frame_index == 0


def test_controller_update_multi_mode(sample_frames):
    """Test update in multi-animation mode (no current_animation_name)."""
    controller = AnimationController()
    anim1 = Animation(sample_frames, loop=True)
    anim2 = Animation(sample_frames, loop=True)
    
    controller.add_animation("anim1", anim1)
    controller.add_animation("anim2", anim2)
    
    # Don't set current_animation_name - stays in multi mode
    controller.update(0.15)
    
    # Both should advance
    assert anim1.current_frame_index == 1
    assert anim2.current_frame_index == 1


def test_controller_get_current_frame(sample_frames):
    """Test getting current frame from active animation."""
    controller = AnimationController()
    anim = Animation(sample_frames, loop=True)
    
    controller.add_animation("test", anim)
    controller.play("test")
    
    frame = controller.get_current_frame()
    assert frame == sample_frames[0].surface


def test_controller_get_current_frame_no_animation():
    """Test getting current frame when no animation is playing."""
    controller = AnimationController()
    frame = controller.get_current_frame()
    assert frame is None


def test_controller_get_current_frame_after_advance(sample_frames):
    """Test getting current frame after animation advances."""
    controller = AnimationController()
    anim = Animation(sample_frames, loop=True)
    
    controller.add_animation("test", anim)
    controller.play("test")
    controller.update(0.15)
    
    frame = controller.get_current_frame()
    assert frame == sample_frames[1].surface


def test_controller_on_animation_complete_callback(sample_frames):
    """Test on_animation_complete callback is triggered."""
    controller = AnimationController()
    anim = Animation(sample_frames, loop=False)
    
    callback_triggered = []
    
    def callback():
        callback_triggered.append(True)
    
    controller.add_animation("test", anim)
    controller.on_animation_complete = callback
    controller.play("test")
    
    # Finish the animation
    controller.update(0.5)
    
    assert len(callback_triggered) == 1


def test_controller_no_callback_without_setting():
    """Test that no error occurs when callback not set."""
    controller = AnimationController()
    
    # Create mock surface for test
    import pygame
    pygame.init()
    surface = pygame.Surface((10, 10))
    
    frames = [AnimationFrame(surface, 0.1)]
    anim = Animation(frames, loop=False)
    
    controller.add_animation("test", anim)
    controller.play("test")
    
    # Should not error even though on_animation_complete is None
    controller.update(0.2)
    
    pygame.quit()


def test_controller_remove_current_animation(sample_frames):
    """Test removing the currently playing animation."""
    controller = AnimationController()
    anim = Animation(sample_frames, loop=True)
    
    controller.add_animation("test", anim)
    controller.play("test")
    
    result = controller.remove_animation("test")
    
    assert result is True
    assert controller.current_animation_name is None
    assert controller.has_animation("test") is False


def test_controller_clear_with_current_animation(sample_frames):
    """Test clearing all animations including current one."""
    controller = AnimationController()
    anim = Animation(sample_frames, loop=True)
    
    controller.add_animation("test", anim)
    controller.play("test")
    
    controller.clear()
    
    assert controller.is_empty() is True
    assert controller.current_animation_name is None
