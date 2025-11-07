"""Timing system for action commands.

This module implements the Mario & Luigi style timing-based action command system
where players must press buttons at the right moment for bonus damage.
"""

from typing import Optional
from enum import Enum


# Constants
PERFECT_TIMING_THRESHOLD = 0.05  # Window for perfect timing (seconds)
GOOD_TIMING_THRESHOLD = 0.15     # Window for good timing (seconds)


class TimingResult(Enum):
    """Result of a timing-based action command."""
    PERFECT = "perfect"
    GOOD = "good"
    NORMAL = "normal"
    MISS = "miss"


class TimingSystem:
    """Manages timing-based action commands for moves.
    
    Attributes:
        is_active: Whether a timing window is currently active.
        elapsed_time: Time elapsed since timing window opened.
        window_duration: Total duration of the timing window.
        optimal_time: Optimal timing point within the window.
        perfect_threshold: Threshold for perfect timing result.
        good_threshold: Threshold for good timing result.
    """
    
    def __init__(self, perfect_threshold: float = PERFECT_TIMING_THRESHOLD,
                 good_threshold: float = GOOD_TIMING_THRESHOLD) -> None:
        """Initialize the timing system.
        
        Args:
            perfect_threshold: Time window for perfect timing (seconds).
            good_threshold: Time window for good timing (seconds).
        """
        self.is_active: bool = False
        self.elapsed_time: float = 0.0
        self.window_duration: float = 0.0
        self.optimal_time: float = 0.0
        self.perfect_threshold: float = perfect_threshold
        self.good_threshold: float = good_threshold
    
    def start_timing_window(self, duration: float, optimal_time: Optional[float] = None) -> None:
        """Start a new timing window.
        
        Args:
            duration: Total duration of the timing window in seconds.
            optimal_time: Optimal timing point (defaults to mid-window if None).
            
        Raises:
            ValueError: If duration is not positive.
        """
        if duration <= 0.0:
            raise ValueError("Timing window duration must be positive")
        
        self.is_active = True
        self.elapsed_time = 0.0
        self.window_duration = duration
        self.optimal_time = optimal_time if optimal_time is not None else duration / 2.0
    
    def update(self, dt: float) -> None:
        """Update the timing window.
        
        Args:
            dt: Delta time in seconds since last update.
        """
        if self.is_active:
            self.elapsed_time += dt
            if self.elapsed_time >= self.window_duration:
                self.is_active = False
    
    def check_input(self) -> TimingResult:
        """Check timing input and return result.
        
        Returns:
            TimingResult indicating quality of the timing.
        """
        if not self.is_active:
            return TimingResult.MISS
        
        # Calculate difference from optimal timing
        time_diff = abs(self.elapsed_time - self.optimal_time)
        
        # Determine result based on timing accuracy
        if time_diff <= self.perfect_threshold:
            result = TimingResult.PERFECT
        elif time_diff <= self.good_threshold:
            result = TimingResult.GOOD
        elif self.elapsed_time <= self.window_duration:
            result = TimingResult.NORMAL
        else:
            result = TimingResult.MISS
        
        self.is_active = False
        return result
    
    def cancel(self) -> None:
        """Cancel the current timing window."""
        self.is_active = False
        self.elapsed_time = 0.0
    
    def get_timing_multiplier(self, result: TimingResult, max_bonus: float) -> float:
        """Convert timing result to damage multiplier.
        
        Args:
            result: The timing result to convert.
            max_bonus: Maximum bonus multiplier for perfect timing.
            
        Returns:
            Damage multiplier based on timing result (1.0 to max_bonus).
        """
        if result == TimingResult.PERFECT:
            return max_bonus
        elif result == TimingResult.GOOD:
            # Good timing gets 75% of the bonus
            return 1.0 + (max_bonus - 1.0) * 0.75
        elif result == TimingResult.NORMAL:
            # Normal timing gets 25% of the bonus
            return 1.0 + (max_bonus - 1.0) * 0.25
        else:  # MISS
            return 1.0
    
    def get_progress(self) -> float:
        """Get current progress through timing window.
        
        Returns:
            Progress as a value from 0.0 to 1.0.
        """
        if not self.is_active or self.window_duration <= 0.0:
            return 0.0
        return min(1.0, self.elapsed_time / self.window_duration)
    
    def get_optimal_progress(self) -> float:
        """Get optimal timing point as progress value.
        
        Returns:
            Optimal timing as a value from 0.0 to 1.0.
        """
        if self.window_duration <= 0.0:
            return 0.5
        return self.optimal_time / self.window_duration
