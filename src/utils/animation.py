"""Animation system for battle visual effects.

This module provides frame-based sprite animations with delta time support.
Animations can be looping or non-looping, and multiple animation instances
can share the same frame data for memory efficiency.
"""

import pygame
from typing import List, Callable, Optional
from dataclasses import dataclass


@dataclass
class AnimationFrame:
    """Single frame of animation.
    
    Attributes:
        surface: Pygame surface for this frame.
        duration: How long to display this frame (seconds).
    """
    surface: pygame.Surface
    duration: float
    
    def __post_init__(self):
        """Validate frame data."""
        if self.duration <= 0:
            raise ValueError("Frame duration must be positive")


class Animation:
    """Frame-based sprite animation.
    
    This class provides frame-rate independent animations using delta time.
    Animations can loop continuously or play once and hold on the last frame.
    
    Attributes:
        frames: List of animation frames.
        loop: Whether animation repeats.
        current_frame_index: Current frame being displayed.
        time_in_frame: Time spent in current frame (seconds).
        finished: Whether animation completed (non-looping only).
        paused: Whether animation is paused.
        on_complete: Optional callback when animation finishes.
    """
    
    def __init__(self, frames: List[AnimationFrame], loop: bool = True,
                 on_complete: Optional[Callable[[], None]] = None):
        """Initialize animation.
        
        Args:
            frames: List of animation frames.
            loop: Whether to loop animation.
            on_complete: Optional callback when animation finishes (non-looping only).
        
        Raises:
            ValueError: If frames list is empty.
        """
        if not frames:
            raise ValueError("Animation must have at least one frame")
        
        self.frames = frames
        self.loop = loop
        self.current_frame_index = 0
        self.time_in_frame = 0.0
        self.finished = False
        self.paused = False
        self.on_complete = on_complete
    
    def update(self, dt: float) -> bool:
        """Update animation.
        
        Args:
            dt: Delta time in seconds since last update.
        
        Returns:
            True if frame changed, False otherwise.
        """
        if self.paused or self.finished:
            return False
        
        frame_changed = False
        self.time_in_frame += dt
        
        # Advance frames as needed
        while self.time_in_frame >= self.frames[self.current_frame_index].duration:
            self.time_in_frame -= self.frames[self.current_frame_index].duration
            self.current_frame_index += 1
            frame_changed = True
            
            # Handle end of animation
            if self.current_frame_index >= len(self.frames):
                if self.loop:
                    self.current_frame_index = 0
                else:
                    # Hold on last frame
                    self.current_frame_index = len(self.frames) - 1
                    self.finished = True
                    self.time_in_frame = 0.0
                    
                    # Call completion callback
                    if self.on_complete:
                        self.on_complete()
                    break
        
        return frame_changed
    
    def get_current_frame(self) -> pygame.Surface:
        """Get current animation frame surface.
        
        Returns:
            Current frame's pygame Surface.
        """
        return self.frames[self.current_frame_index].surface
    
    def reset(self) -> None:
        """Reset animation to first frame."""
        self.current_frame_index = 0
        self.time_in_frame = 0.0
        self.finished = False
    
    def pause(self) -> None:
        """Pause animation."""
        self.paused = True
    
    def resume(self) -> None:
        """Resume paused animation."""
        self.paused = False
    
    def is_finished(self) -> bool:
        """Check if animation is finished.
        
        Returns:
            True if non-looping animation completed, False otherwise.
        """
        return self.finished
    
    def get_progress(self) -> float:
        """Get animation progress as percentage.
        
        Returns:
            Progress from 0.0 to 1.0.
        """
        if not self.frames:
            return 1.0
        
        total_duration = sum(frame.duration for frame in self.frames)
        if total_duration == 0:
            return 1.0
        
        elapsed = sum(self.frames[i].duration for i in range(self.current_frame_index))
        elapsed += self.time_in_frame
        
        return min(1.0, elapsed / total_duration)


class AnimationController:
    """Manages multiple simultaneous animations.
    
    This controller allows composing multiple effects (e.g., flash + shake)
    without duplicating animation data. Each animation instance is updated
    independently.
    
    Attributes:
        animations: Dictionary of active animations by name.
    """
    
    def __init__(self):
        """Initialize animation controller."""
        self.animations: dict[str, Animation] = {}
    
    def add_animation(self, name: str, animation: Animation) -> None:
        """Add animation to controller.
        
        Args:
            name: Unique identifier for this animation.
            animation: Animation instance to add.
        
        Raises:
            ValueError: If animation with this name already exists.
        """
        if name in self.animations:
            raise ValueError(f"Animation '{name}' already exists")
        self.animations[name] = animation
    
    def remove_animation(self, name: str) -> bool:
        """Remove animation from controller.
        
        Args:
            name: Name of animation to remove.
        
        Returns:
            True if animation was removed, False if not found.
        """
        if name in self.animations:
            del self.animations[name]
            return True
        return False
    
    def update(self, dt: float) -> None:
        """Update all active animations.
        
        Args:
            dt: Delta time in seconds since last update.
        """
        # Remove finished non-looping animations
        finished = [name for name, anim in self.animations.items() 
                   if anim.is_finished()]
        for name in finished:
            del self.animations[name]
        
        # Update remaining animations
        for animation in self.animations.values():
            animation.update(dt)
    
    def get_animation(self, name: str) -> Optional[Animation]:
        """Get animation by name.
        
        Args:
            name: Name of animation.
        
        Returns:
            Animation instance or None if not found.
        """
        return self.animations.get(name)
    
    def has_animation(self, name: str) -> bool:
        """Check if animation exists.
        
        Args:
            name: Name of animation.
        
        Returns:
            True if animation exists, False otherwise.
        """
        return name in self.animations
    
    def clear(self) -> None:
        """Remove all animations."""
        self.animations.clear()
    
    def is_empty(self) -> bool:
        """Check if controller has no active animations.
        
        Returns:
            True if no animations active, False otherwise.
        """
        return len(self.animations) == 0
