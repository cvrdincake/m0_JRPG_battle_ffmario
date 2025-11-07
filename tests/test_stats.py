"""Unit tests for Stats dataclass."""

import pytest
from src.entities.stats import Stats


class TestStats:
    """Tests for immutable Stats dataclass."""
    
    def test_stats_initialization(self):
        """Test stats can be initialized with valid values."""
        stats = Stats(
            max_hp=100,
            max_mp=50,
            attack=15,
            defense=10,
            magic=12,
            speed=14
        )
        
        assert stats.max_hp == 100
        assert stats.max_mp == 50
        assert stats.attack == 15
        assert stats.defense == 10
        assert stats.magic == 12
        assert stats.speed == 14
    
    def test_stats_immutable(self):
        """Test that stats cannot be modified after creation."""
        stats = Stats(
            max_hp=100,
            max_mp=50,
            attack=15,
            defense=10,
            magic=12,
            speed=14
        )
        
        # Attempting to modify should raise FrozenInstanceError
        with pytest.raises(Exception):  # dataclasses.FrozenInstanceError
            stats.max_hp = 200
    
    def test_negative_hp_raises_error(self):
        """Test that negative max_hp raises ValueError."""
        with pytest.raises(ValueError, match="max_hp cannot be negative"):
            Stats(
                max_hp=-10,
                max_mp=50,
                attack=15,
                defense=10,
                magic=12,
                speed=14
            )
    
    def test_negative_attack_raises_error(self):
        """Test that negative attack raises ValueError."""
        with pytest.raises(ValueError, match="attack cannot be negative"):
            Stats(
                max_hp=100,
                max_mp=50,
                attack=-5,
                defense=10,
                magic=12,
                speed=14
            )
    
    def test_zero_stats_allowed(self):
        """Test that zero values are allowed for stats."""
        stats = Stats(
            max_hp=0,
            max_mp=0,
            attack=0,
            defense=0,
            magic=0,
            speed=0
        )
        
        assert stats.max_hp == 0
        assert stats.attack == 0


class TestPhysicalDamageCalculation:
    """Tests for physical damage formula."""
    
    def test_basic_damage_calculation(self):
        """Test basic damage calculation with equal stats."""
        attacker = Stats(
            max_hp=100, max_mp=50, attack=20, defense=10, magic=10, speed=10
        )
        defender = Stats(
            max_hp=100, max_mp=50, attack=10, defense=20, magic=10, speed=10
        )
        
        # Formula: move_power * (attack / (attack + defense))
        # 50 * (20 / (20 + 20)) = 50 * 0.5 = 25
        damage = Stats.calculate_physical_damage(attacker, defender, move_power=50)
        assert damage == 25
    
    def test_high_attack_vs_low_defense(self):
        """Test damage when attacker has much higher attack."""
        attacker = Stats(
            max_hp=100, max_mp=50, attack=50, defense=10, magic=10, speed=10
        )
        defender = Stats(
            max_hp=100, max_mp=50, attack=10, defense=10, magic=10, speed=10
        )
        
        # Formula: 100 * (50 / (50 + 10)) = 100 * (50/60) = 83.33... = 83
        damage = Stats.calculate_physical_damage(attacker, defender, move_power=100)
        assert damage == 83
    
    def test_low_attack_vs_high_defense(self):
        """Test damage when defender has much higher defense."""
        attacker = Stats(
            max_hp=100, max_mp=50, attack=10, defense=10, magic=10, speed=10
        )
        defender = Stats(
            max_hp=100, max_mp=50, attack=10, defense=50, magic=10, speed=10
        )
        
        # Formula: 100 * (10 / (10 + 50)) = 100 * (10/60) = 16.66... = 16
        damage = Stats.calculate_physical_damage(attacker, defender, move_power=100)
        assert damage == 16
    
    def test_minimum_damage_is_one(self):
        """Test that damage is always at least 1."""
        attacker = Stats(
            max_hp=100, max_mp=50, attack=1, defense=10, magic=10, speed=10
        )
        defender = Stats(
            max_hp=100, max_mp=50, attack=10, defense=100, magic=10, speed=10
        )
        
        # Even with very low attack vs high defense, should deal 1 damage
        damage = Stats.calculate_physical_damage(attacker, defender, move_power=1)
        assert damage == 1
    
    def test_zero_stats_returns_minimum_damage(self):
        """Test that zero attack and defense returns minimum damage."""
        attacker = Stats(
            max_hp=100, max_mp=50, attack=0, defense=10, magic=10, speed=10
        )
        defender = Stats(
            max_hp=100, max_mp=50, attack=10, defense=0, magic=10, speed=10
        )
        
        damage = Stats.calculate_physical_damage(attacker, defender, move_power=50)
        assert damage == 1
    
    def test_deterministic_damage(self):
        """Test that damage calculation is deterministic (same inputs = same output)."""
        attacker = Stats(
            max_hp=100, max_mp=50, attack=25, defense=10, magic=15, speed=12
        )
        defender = Stats(
            max_hp=100, max_mp=50, attack=15, defense=15, magic=10, speed=10
        )
        
        # Calculate damage multiple times
        damage1 = Stats.calculate_physical_damage(attacker, defender, move_power=60)
        damage2 = Stats.calculate_physical_damage(attacker, defender, move_power=60)
        damage3 = Stats.calculate_physical_damage(attacker, defender, move_power=60)
        
        # All should be identical
        assert damage1 == damage2 == damage3
    
    def test_different_move_powers(self):
        """Test that different move powers produce different damage."""
        attacker = Stats(
            max_hp=100, max_mp=50, attack=20, defense=10, magic=10, speed=10
        )
        defender = Stats(
            max_hp=100, max_mp=50, attack=10, defense=20, magic=10, speed=10
        )
        
        damage_weak = Stats.calculate_physical_damage(attacker, defender, move_power=30)
        damage_strong = Stats.calculate_physical_damage(attacker, defender, move_power=90)
        
        # Stronger move should deal more damage
        assert damage_strong > damage_weak
        # Should scale proportionally: 90/30 = 3x
        assert damage_strong == damage_weak * 3


class TestMagicalDamageCalculation:
    """Tests for magical damage formula."""
    
    def test_basic_magical_damage(self):
        """Test basic magical damage calculation."""
        attacker = Stats(
            max_hp=100, max_mp=50, attack=10, defense=10, magic=30, speed=10
        )
        defender = Stats(
            max_hp=100, max_mp=50, attack=10, defense=20, magic=10, speed=10
        )
        
        # Formula: move_power * (magic / (magic + defense))
        # 60 * (30 / (30 + 20)) = 60 * 0.6 = 36
        damage = Stats.calculate_magical_damage(attacker, defender, move_power=60)
        assert damage == 36
    
    def test_magical_minimum_damage(self):
        """Test that magical damage is always at least 1."""
        attacker = Stats(
            max_hp=100, max_mp=50, attack=10, defense=10, magic=1, speed=10
        )
        defender = Stats(
            max_hp=100, max_mp=50, attack=10, defense=100, magic=10, speed=10
        )
        
        damage = Stats.calculate_magical_damage(attacker, defender, move_power=1)
        assert damage == 1
    
    def test_high_magic_vs_low_defense(self):
        """Test magical damage with high magic vs low defense."""
        attacker = Stats(
            max_hp=100, max_mp=50, attack=10, defense=10, magic=60, speed=10
        )
        defender = Stats(
            max_hp=100, max_mp=50, attack=10, defense=15, magic=10, speed=10
        )
        
        # Formula: 100 * (60 / (60 + 15)) = 100 * 0.8 = 80
        damage = Stats.calculate_magical_damage(attacker, defender, move_power=100)
        assert damage == 80
