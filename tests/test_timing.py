"""Unit tests for timing system."""

import pytest
from src.battle.timing import TimingSystem, TimingResult


class TestTimingSystem:
    """Tests for TimingSystem class."""
    
    def test_initialization(self):
        """Test timing system initializes correctly."""
        timing = TimingSystem()
        
        assert timing.is_active is False
        assert timing.elapsed_time == 0.0
        assert timing.window_duration == 0.0
    
    def test_start_timing_window(self):
        """Test starting a timing window."""
        timing = TimingSystem()
        timing.start_timing_window(1.0)
        
        assert timing.is_active is True
        assert timing.elapsed_time == 0.0
        assert timing.window_duration == 1.0
        assert timing.optimal_time == 0.5  # Default mid-window
    
    def test_start_timing_window_custom_optimal(self):
        """Test starting timing window with custom optimal time."""
        timing = TimingSystem()
        timing.start_timing_window(1.0, optimal_time=0.3)
        
        assert timing.optimal_time == 0.3
    
    def test_start_timing_window_invalid_duration(self):
        """Test starting timing window with invalid duration."""
        timing = TimingSystem()
        
        with pytest.raises(ValueError, match="duration must be positive"):
            timing.start_timing_window(0.0)
    
    def test_update(self):
        """Test updating the timing window."""
        timing = TimingSystem()
        timing.start_timing_window(1.0)
        
        timing.update(0.3)
        assert timing.elapsed_time == 0.3
        assert timing.is_active is True
        
        timing.update(0.5)
        assert timing.elapsed_time == 0.8
        assert timing.is_active is True
    
    def test_update_closes_window(self):
        """Test window closes after duration elapses."""
        timing = TimingSystem()
        timing.start_timing_window(1.0)
        
        timing.update(1.5)
        assert timing.is_active is False
    
    def test_check_input_perfect(self):
        """Test perfect timing input."""
        timing = TimingSystem(perfect_threshold=0.05, good_threshold=0.15)
        timing.start_timing_window(1.0, optimal_time=0.5)
        
        timing.elapsed_time = 0.52  # Within 0.05 of optimal
        result = timing.check_input()
        
        assert result == TimingResult.PERFECT
        assert timing.is_active is False
    
    def test_check_input_good(self):
        """Test good timing input."""
        timing = TimingSystem(perfect_threshold=0.05, good_threshold=0.15)
        timing.start_timing_window(1.0, optimal_time=0.5)
        
        timing.elapsed_time = 0.6  # Within 0.15 of optimal
        result = timing.check_input()
        
        assert result == TimingResult.GOOD
    
    def test_check_input_normal(self):
        """Test normal timing input."""
        timing = TimingSystem(perfect_threshold=0.05, good_threshold=0.15)
        timing.start_timing_window(1.0, optimal_time=0.5)
        
        timing.elapsed_time = 0.2  # Beyond good threshold but in window
        result = timing.check_input()
        
        assert result == TimingResult.NORMAL
    
    def test_check_input_miss_not_active(self):
        """Test miss when window not active."""
        timing = TimingSystem()
        
        result = timing.check_input()
        assert result == TimingResult.MISS
    
    def test_cancel(self):
        """Test canceling timing window."""
        timing = TimingSystem()
        timing.start_timing_window(1.0)
        timing.update(0.5)
        
        timing.cancel()
        assert timing.is_active is False
        assert timing.elapsed_time == 0.0
    
    def test_get_timing_multiplier_perfect(self):
        """Test timing multiplier for perfect result."""
        timing = TimingSystem()
        
        multiplier = timing.get_timing_multiplier(TimingResult.PERFECT, max_bonus=2.0)
        assert multiplier == 2.0
    
    def test_get_timing_multiplier_good(self):
        """Test timing multiplier for good result."""
        timing = TimingSystem()
        
        multiplier = timing.get_timing_multiplier(TimingResult.GOOD, max_bonus=2.0)
        assert multiplier == 1.75  # 1.0 + (2.0 - 1.0) * 0.75
    
    def test_get_timing_multiplier_normal(self):
        """Test timing multiplier for normal result."""
        timing = TimingSystem()
        
        multiplier = timing.get_timing_multiplier(TimingResult.NORMAL, max_bonus=2.0)
        assert multiplier == 1.25  # 1.0 + (2.0 - 1.0) * 0.25
    
    def test_get_timing_multiplier_miss(self):
        """Test timing multiplier for miss result."""
        timing = TimingSystem()
        
        multiplier = timing.get_timing_multiplier(TimingResult.MISS, max_bonus=2.0)
        assert multiplier == 1.0
    
    def test_get_progress(self):
        """Test getting progress through window."""
        timing = TimingSystem()
        timing.start_timing_window(1.0)
        
        timing.elapsed_time = 0.5
        assert timing.get_progress() == 0.5
        
        timing.elapsed_time = 0.75
        assert timing.get_progress() == 0.75
    
    def test_get_optimal_progress(self):
        """Test getting optimal timing as progress."""
        timing = TimingSystem()
        timing.start_timing_window(1.0, optimal_time=0.3)
        
        assert timing.get_optimal_progress() == 0.3
