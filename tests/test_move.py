"""Unit tests for move entities."""

import pytest
from src.entities.move import Move, MoveType


class TestMove:
    """Tests for Move class."""
    
    def test_move_initialization(self):
        """Test move initializes with correct attributes."""
        data = {
            "id": "jump",
            "name": "Jump",
            "type": "physical",
            "mp_cost": 0,
            "base_power": 20,
            "timing_window": 0.3,
            "timing_bonus": 1.5,
            "description": "Jump attack"
        }
        move = Move(data)
        
        assert move.id == "jump"
        assert move.name == "Jump"
        assert move.move_type == MoveType.PHYSICAL
        assert move.mp_cost == 0
        assert move.base_power == 20
        assert move.timing_window == 0.3
        assert move.timing_bonus == 1.5
        assert move.description == "Jump attack"
    
    def test_missing_required_field(self):
        """Test move initialization fails with missing field."""
        data = {"id": "move1", "name": "Test"}
        
        with pytest.raises(ValueError, match="Missing required field"):
            Move(data)
    
    def test_invalid_move_type(self):
        """Test move initialization fails with invalid type."""
        data = {
            "id": "move1", "name": "Test", "type": "invalid",
            "mp_cost": 0, "base_power": 10, "timing_window": 0.3,
            "timing_bonus": 1.5, "description": "Test"
        }
        
        with pytest.raises(ValueError, match="Invalid move type"):
            Move(data)
    
    def test_calculate_damage_basic(self):
        """Test basic damage calculation."""
        data = {
            "id": "jump", "name": "Jump", "type": "physical",
            "mp_cost": 0, "base_power": 20, "timing_window": 0.3,
            "timing_bonus": 1.5, "description": "Jump"
        }
        move = Move(data)
        
        damage = move.calculate_damage(attacker_attack=15, defender_defense=10)
        # Formula: (20 + 15 - 10/2) * 1.0 = (20 + 15 - 5) * 1.0 = 30
        assert damage == 30
    
    def test_calculate_damage_with_timing(self):
        """Test damage calculation with timing bonus."""
        data = {
            "id": "jump", "name": "Jump", "type": "physical",
            "mp_cost": 0, "base_power": 20, "timing_window": 0.3,
            "timing_bonus": 2.0, "description": "Jump"
        }
        move = Move(data)
        
        damage = move.calculate_damage(
            attacker_attack=15, 
            defender_defense=10, 
            timing_multiplier=2.0
        )
        # Formula: (20 + 15 - 5) * 2.0 = 60
        assert damage == 60
    
    def test_defend_move_no_damage(self):
        """Test defend move does no damage."""
        data = {
            "id": "defend", "name": "Defend", "type": "defend",
            "mp_cost": 0, "base_power": 0, "timing_window": 0.0,
            "timing_bonus": 1.0, "description": "Defend"
        }
        move = Move(data)
        
        damage = move.calculate_damage(attacker_attack=15, defender_defense=10)
        assert damage == 0
    
    def test_minimum_damage(self):
        """Test minimum damage is 1 for offensive moves."""
        data = {
            "id": "weak", "name": "Weak", "type": "physical",
            "mp_cost": 0, "base_power": 1, "timing_window": 0.0,
            "timing_bonus": 1.0, "description": "Weak attack"
        }
        move = Move(data)
        
        # Even with high defense, should deal at least 1 damage
        damage = move.calculate_damage(attacker_attack=1, defender_defense=100)
        assert damage >= 1
    
    def test_can_use_with_enough_mp(self):
        """Test can_use returns True with enough MP."""
        data = {
            "id": "spell", "name": "Spell", "type": "magic",
            "mp_cost": 10, "base_power": 30, "timing_window": 0.3,
            "timing_bonus": 1.5, "description": "Magic spell"
        }
        move = Move(data)
        
        assert move.can_use(user_mp=15) is True
        assert move.can_use(user_mp=10) is True
        assert move.can_use(user_mp=5) is False
    
    def test_is_offensive(self):
        """Test is_offensive detection."""
        physical = Move({
            "id": "p", "name": "P", "type": "physical",
            "mp_cost": 0, "base_power": 10, "timing_window": 0.0,
            "timing_bonus": 1.0, "description": "P"
        })
        
        magic = Move({
            "id": "m", "name": "M", "type": "magic",
            "mp_cost": 10, "base_power": 10, "timing_window": 0.0,
            "timing_bonus": 1.0, "description": "M"
        })
        
        defend = Move({
            "id": "d", "name": "D", "type": "defend",
            "mp_cost": 0, "base_power": 0, "timing_window": 0.0,
            "timing_bonus": 1.0, "description": "D"
        })
        
        assert physical.is_offensive() is True
        assert magic.is_offensive() is True
        assert defend.is_offensive() is False
    
    def test_requires_timing(self):
        """Test requires_timing detection."""
        with_timing = Move({
            "id": "t", "name": "T", "type": "physical",
            "mp_cost": 0, "base_power": 10, "timing_window": 0.3,
            "timing_bonus": 1.5, "description": "T"
        })
        
        without_timing = Move({
            "id": "n", "name": "N", "type": "defend",
            "mp_cost": 0, "base_power": 0, "timing_window": 0.0,
            "timing_bonus": 1.0, "description": "N"
        })
        
        assert with_timing.requires_timing() is True
        assert without_timing.requires_timing() is False
