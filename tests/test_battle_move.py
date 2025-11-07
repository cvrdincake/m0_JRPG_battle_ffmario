"""Unit tests for enhanced battle move system."""

import pytest
from src.battle.move import (
    BattleMove, TargetType, TimingType, TimingWindow, ActionCommand,
    DEFAULT_TIMING_WINDOWS
)


class TestTargetType:
    """Tests for TargetType enum."""
    
    def test_all_target_types_exist(self):
        """Test that all target types are defined."""
        assert TargetType.SINGLE_ENEMY
        assert TargetType.ALL_ENEMIES
        assert TargetType.SINGLE_ALLY
        assert TargetType.ALL_ALLIES
        assert TargetType.SELF


class TestTimingType:
    """Tests for TimingType enum."""
    
    def test_all_timing_types_exist(self):
        """Test that all timing types are defined."""
        assert TimingType.SIMPLE
        assert TimingType.TIMED_PRESS
        assert TimingType.SEQUENCE
        assert TimingType.HOLD_RELEASE


class TestTimingWindow:
    """Tests for TimingWindow dataclass."""
    
    def test_evaluate_perfect(self):
        """Test evaluation returns perfect for perfect timing."""
        window = TimingWindow(
            perfect_min=450, perfect_max=550,
            good_min=350, good_max=650,
            early_min=200, early_max=800
        )
        
        assert window.evaluate(500) == "perfect"
        assert window.evaluate(450) == "perfect"
        assert window.evaluate(550) == "perfect"
    
    def test_evaluate_good(self):
        """Test evaluation returns good for good timing."""
        window = TimingWindow(
            perfect_min=450, perfect_max=550,
            good_min=350, good_max=650,
            early_min=200, early_max=800
        )
        
        assert window.evaluate(400) == "good"
        assert window.evaluate(600) == "good"
        assert window.evaluate(350) == "good"
        assert window.evaluate(650) == "good"
    
    def test_evaluate_early(self):
        """Test evaluation returns early for early timing."""
        window = TimingWindow(
            perfect_min=450, perfect_max=550,
            good_min=350, good_max=650,
            early_min=200, early_max=800
        )
        
        assert window.evaluate(250) == "early"
        assert window.evaluate(700) == "early"
        assert window.evaluate(200) == "early"
        assert window.evaluate(800) == "early"
    
    def test_evaluate_miss(self):
        """Test evaluation returns miss for missed timing."""
        window = TimingWindow(
            perfect_min=450, perfect_max=550,
            good_min=350, good_max=650,
            early_min=200, early_max=800
        )
        
        assert window.evaluate(100) == "miss"
        assert window.evaluate(900) == "miss"
        assert window.evaluate(0) == "miss"
        assert window.evaluate(1000) == "miss"
    
    def test_from_dict(self):
        """Test creating TimingWindow from dictionary."""
        data = {
            'perfect_min': 450,
            'perfect_max': 550,
            'good_min': 350,
            'good_max': 650,
            'early_min': 200,
            'early_max': 800
        }
        
        window = TimingWindow.from_dict(data)
        assert window.perfect_min == 450
        assert window.perfect_max == 550
        assert window.good_min == 350
    
    def test_from_dict_missing_field(self):
        """Test from_dict raises error for missing field."""
        data = {'perfect_min': 450, 'perfect_max': 550}
        
        with pytest.raises(ValueError, match="Missing required timing field"):
            TimingWindow.from_dict(data)


class TestActionCommand:
    """Tests for ActionCommand dataclass."""
    
    def test_simple_does_not_require_input(self):
        """Test that SIMPLE timing doesn't require input."""
        cmd = ActionCommand(timing_type=TimingType.SIMPLE)
        assert cmd.requires_input() is False
    
    def test_timed_press_requires_input(self):
        """Test that TIMED_PRESS requires input."""
        cmd = ActionCommand(timing_type=TimingType.TIMED_PRESS)
        assert cmd.requires_input() is True
    
    def test_get_multiplier_perfect(self):
        """Test perfect timing gives 2.0x multiplier."""
        cmd = ActionCommand(timing_type=TimingType.TIMED_PRESS)
        assert cmd.get_multiplier("perfect") == 2.0
    
    def test_get_multiplier_good(self):
        """Test good timing gives 1.5x multiplier."""
        cmd = ActionCommand(timing_type=TimingType.TIMED_PRESS)
        assert cmd.get_multiplier("good") == 1.5
    
    def test_get_multiplier_early(self):
        """Test early timing gives 1.2x multiplier."""
        cmd = ActionCommand(timing_type=TimingType.TIMED_PRESS)
        assert cmd.get_multiplier("early") == 1.2
    
    def test_get_multiplier_miss(self):
        """Test missed timing gives 1.0x multiplier."""
        cmd = ActionCommand(timing_type=TimingType.TIMED_PRESS)
        assert cmd.get_multiplier("miss") == 1.0


class TestBattleMove:
    """Tests for BattleMove class."""
    
    def test_basic_move_initialization(self):
        """Test creating a basic offensive move."""
        data = {
            'id': 'punch',
            'name': 'Punch',
            'description': 'A basic punch attack',
            'base_power': 20,
            'mp_cost': 0,
            'target_type': 'single_enemy',
            'timing_type': 'simple',
            'is_offensive': True
        }
        
        move = BattleMove(data)
        assert move.id == 'punch'
        assert move.name == 'Punch'
        assert move.base_power == 20
        assert move.mp_cost == 0
        assert move.target_type == TargetType.SINGLE_ENEMY
        assert move.action_command.timing_type == TimingType.SIMPLE
        assert move.is_offensive is True
    
    def test_move_with_timing_window(self):
        """Test creating move with timing window."""
        data = {
            'id': 'jump',
            'name': 'Jump',
            'description': 'Jump on enemy',
            'base_power': 30,
            'mp_cost': 0,
            'target_type': 'single_enemy',
            'timing_type': 'timed_press',
            'timing_window': {
                'perfect_min': 450,
                'perfect_max': 550,
                'good_min': 350,
                'good_max': 650,
                'early_min': 200,
                'early_max': 800
            }
        }
        
        move = BattleMove(data)
        assert move.action_command.timing_window is not None
        assert move.action_command.timing_window.perfect_min == 450
    
    def test_missing_required_field(self):
        """Test that missing required field raises ValueError."""
        data = {'id': 'test', 'name': 'Test'}
        
        with pytest.raises(ValueError, match="Missing required field"):
            BattleMove(data)
    
    def test_invalid_target_type(self):
        """Test that invalid target type raises ValueError."""
        data = {
            'id': 'test',
            'name': 'Test',
            'description': 'Test',
            'base_power': 10,
            'mp_cost': 0,
            'target_type': 'invalid',
            'timing_type': 'simple'
        }
        
        with pytest.raises(ValueError, match="Invalid target type"):
            BattleMove(data)
    
    def test_invalid_timing_type(self):
        """Test that invalid timing type raises ValueError."""
        data = {
            'id': 'test',
            'name': 'Test',
            'description': 'Test',
            'base_power': 10,
            'mp_cost': 0,
            'target_type': 'single_enemy',
            'timing_type': 'invalid'
        }
        
        with pytest.raises(ValueError, match="Invalid timing type"):
            BattleMove(data)
    
    def test_can_use_with_enough_mp(self):
        """Test can_use returns True with enough MP."""
        data = {
            'id': 'fireball',
            'name': 'Fireball',
            'description': 'Fire attack',
            'base_power': 50,
            'mp_cost': 10,
            'target_type': 'single_enemy',
            'timing_type': 'simple'
        }
        
        move = BattleMove(data)
        assert move.can_use(10) is True
        assert move.can_use(15) is True
    
    def test_can_use_without_enough_mp(self):
        """Test can_use returns False without enough MP."""
        data = {
            'id': 'fireball',
            'name': 'Fireball',
            'description': 'Fire attack',
            'base_power': 50,
            'mp_cost': 10,
            'target_type': 'single_enemy',
            'timing_type': 'simple'
        }
        
        move = BattleMove(data)
        assert move.can_use(5) is False
        assert move.can_use(9) is False
    
    def test_calculate_damage_basic(self):
        """Test basic damage calculation."""
        data = {
            'id': 'attack',
            'name': 'Attack',
            'description': 'Basic attack',
            'base_power': 40,
            'mp_cost': 0,
            'target_type': 'single_enemy',
            'timing_type': 'simple'
        }
        
        move = BattleMove(data)
        # Equal stats: 20 attack vs 20 defense
        damage = move.calculate_damage(20, 20, "miss")
        assert damage == 20  # 40 * (20/40) = 20
    
    def test_calculate_damage_with_perfect_timing(self):
        """Test damage with perfect timing bonus."""
        data = {
            'id': 'jump',
            'name': 'Jump',
            'description': 'Jump attack',
            'base_power': 40,
            'mp_cost': 0,
            'target_type': 'single_enemy',
            'timing_type': 'timed_press'
        }
        
        move = BattleMove(data)
        damage = move.calculate_damage(20, 20, "perfect")
        # Base: 40 * (20/40) = 20, with 2.0x = 40
        assert damage == 40
    
    def test_calculate_damage_minimum_one(self):
        """Test damage is always at least 1."""
        data = {
            'id': 'weak',
            'name': 'Weak',
            'description': 'Weak attack',
            'base_power': 1,
            'mp_cost': 0,
            'target_type': 'single_enemy',
            'timing_type': 'simple'
        }
        
        move = BattleMove(data)
        damage = move.calculate_damage(1, 100, "miss")
        assert damage == 1
    
    def test_targets_enemy(self):
        """Test targets_enemy for enemy-targeting moves."""
        data = {
            'id': 'attack',
            'name': 'Attack',
            'description': 'Attack',
            'base_power': 20,
            'mp_cost': 0,
            'target_type': 'single_enemy',
            'timing_type': 'simple'
        }
        
        move = BattleMove(data)
        assert move.targets_enemy() is True
        assert move.targets_ally() is False
    
    def test_targets_ally(self):
        """Test targets_ally for ally-targeting moves."""
        data = {
            'id': 'heal',
            'name': 'Heal',
            'description': 'Heal ally',
            'base_power': 30,
            'mp_cost': 5,
            'target_type': 'single_ally',
            'timing_type': 'simple',
            'is_offensive': False
        }
        
        move = BattleMove(data)
        assert move.targets_ally() is True
        assert move.targets_enemy() is False
    
    def test_is_multi_target(self):
        """Test is_multi_target for AOE moves."""
        data = {
            'id': 'quake',
            'name': 'Quake',
            'description': 'Earth attack',
            'base_power': 30,
            'mp_cost': 15,
            'target_type': 'all_enemies',
            'timing_type': 'simple'
        }
        
        move = BattleMove(data)
        assert move.is_multi_target() is True


class TestDefaultTimingWindows:
    """Tests for default timing windows."""
    
    def test_default_windows_exist(self):
        """Test that default windows are defined."""
        assert TimingType.TIMED_PRESS in DEFAULT_TIMING_WINDOWS
        assert TimingType.SEQUENCE in DEFAULT_TIMING_WINDOWS
        assert TimingType.HOLD_RELEASE in DEFAULT_TIMING_WINDOWS
    
    def test_sequence_harder_than_timed_press(self):
        """Test that sequence timing is harder (tighter window)."""
        timed = DEFAULT_TIMING_WINDOWS[TimingType.TIMED_PRESS]
        sequence = DEFAULT_TIMING_WINDOWS[TimingType.SEQUENCE]
        
        timed_perfect_range = timed.perfect_max - timed.perfect_min
        sequence_perfect_range = sequence.perfect_max - sequence.perfect_min
        
        assert sequence_perfect_range < timed_perfect_range
    
    def test_hold_release_hardest(self):
        """Test that hold_release is the hardest (tightest window)."""
        hold = DEFAULT_TIMING_WINDOWS[TimingType.HOLD_RELEASE]
        
        perfect_range = hold.perfect_max - hold.perfect_min
        assert perfect_range <= 40  # Very tight window
