"""Unit tests for character entities."""

import pytest
from src.entities.character import Character, Hero, Enemy


class TestCharacter:
    """Tests for Character class."""
    
    def test_character_initialization(self):
        """Test character initializes with correct attributes."""
        data = {
            "id": "test1",
            "name": "TestChar",
            "max_hp": 100,
            "max_mp": 50,
            "attack": 15,
            "defense": 10,
            "speed": 12,
            "atb_speed": 10
        }
        char = Character(data)
        
        assert char.id == "test1"
        assert char.name == "TestChar"
        assert char.max_hp == 100
        assert char.current_hp == 100
        assert char.max_mp == 50
        assert char.current_mp == 50
        assert char.attack == 15
        assert char.defense == 10
        assert char.speed == 12
        assert char.atb_speed == 10
        assert char.atb_value == 0.0
        assert char.is_alive is True
        assert char.is_defending is False
    
    def test_missing_required_field(self):
        """Test character initialization fails with missing field."""
        data = {"id": "test1", "name": "Test"}
        
        with pytest.raises(ValueError, match="Missing required field"):
            Character(data)
    
    def test_update_atb(self):
        """Test ATB gauge updates correctly."""
        data = {
            "id": "test1", "name": "Test", "max_hp": 100,
            "attack": 10, "defense": 10, "speed": 10, "atb_speed": 10
        }
        char = Character(data)
        
        char.update_atb(1.0)  # 1 second
        assert char.atb_value == 10.0
        
        char.update_atb(1.0)
        assert char.atb_value == 20.0
    
    def test_atb_clamped_at_max(self):
        """Test ATB gauge is clamped at 100."""
        data = {
            "id": "test1", "name": "Test", "max_hp": 100,
            "attack": 10, "defense": 10, "speed": 10, "atb_speed": 50
        }
        char = Character(data)
        
        char.update_atb(5.0)
        assert char.atb_value == 100.0
    
    def test_is_atb_ready(self):
        """Test ATB ready detection."""
        data = {
            "id": "test1", "name": "Test", "max_hp": 100,
            "attack": 10, "defense": 10, "speed": 10, "atb_speed": 100
        }
        char = Character(data)
        
        assert char.is_atb_ready() is False
        char.update_atb(1.0)
        assert char.is_atb_ready() is True
    
    def test_reset_atb(self):
        """Test ATB reset."""
        data = {
            "id": "test1", "name": "Test", "max_hp": 100,
            "attack": 10, "defense": 10, "speed": 10, "atb_speed": 50
        }
        char = Character(data)
        
        char.atb_value = 75.0
        char.reset_atb()
        assert char.atb_value == 0.0
    
    def test_take_damage(self):
        """Test taking damage."""
        data = {
            "id": "test1", "name": "Test", "max_hp": 100,
            "attack": 10, "defense": 10, "speed": 10, "atb_speed": 10
        }
        char = Character(data)
        
        damage = char.take_damage(30)
        assert damage == 30
        assert char.current_hp == 70
        assert char.is_alive is True
    
    def test_take_lethal_damage(self):
        """Test taking lethal damage."""
        data = {
            "id": "test1", "name": "Test", "max_hp": 100,
            "attack": 10, "defense": 10, "speed": 10, "atb_speed": 10
        }
        char = Character(data)
        
        char.take_damage(150)
        assert char.current_hp == 0
        assert char.is_alive is False
    
    def test_defending_reduces_damage(self):
        """Test defending state reduces damage."""
        data = {
            "id": "test1", "name": "Test", "max_hp": 100,
            "attack": 10, "defense": 10, "speed": 10, "atb_speed": 10
        }
        char = Character(data)
        
        char.set_defending(True)
        damage = char.take_damage(40)
        assert damage == 20  # 50% reduction
        assert char.current_hp == 80
    
    def test_heal(self):
        """Test healing."""
        data = {
            "id": "test1", "name": "Test", "max_hp": 100,
            "attack": 10, "defense": 10, "speed": 10, "atb_speed": 10
        }
        char = Character(data)
        
        char.current_hp = 50
        healed = char.heal(30)
        assert healed == 30
        assert char.current_hp == 80
    
    def test_heal_clamped_at_max(self):
        """Test healing is clamped at max HP."""
        data = {
            "id": "test1", "name": "Test", "max_hp": 100,
            "attack": 10, "defense": 10, "speed": 10, "atb_speed": 10
        }
        char = Character(data)
        
        char.current_hp = 90
        healed = char.heal(30)
        assert healed == 10
        assert char.current_hp == 100
    
    def test_use_mp(self):
        """Test using MP."""
        data = {
            "id": "test1", "name": "Test", "max_hp": 100, "max_mp": 50,
            "attack": 10, "defense": 10, "speed": 10, "atb_speed": 10
        }
        char = Character(data)
        
        assert char.use_mp(20) is True
        assert char.current_mp == 30
        
        assert char.use_mp(40) is False
        assert char.current_mp == 30
    
    def test_restore_mp(self):
        """Test restoring MP."""
        data = {
            "id": "test1", "name": "Test", "max_hp": 100, "max_mp": 50,
            "attack": 10, "defense": 10, "speed": 10, "atb_speed": 10
        }
        char = Character(data)
        
        char.current_mp = 20
        restored = char.restore_mp(15)
        assert restored == 15
        assert char.current_mp == 35
    
    def test_get_hp_percentage(self):
        """Test HP percentage calculation."""
        data = {
            "id": "test1", "name": "Test", "max_hp": 100,
            "attack": 10, "defense": 10, "speed": 10, "atb_speed": 10
        }
        char = Character(data)
        
        char.current_hp = 75
        assert char.get_hp_percentage() == 0.75
    
    def test_get_atb_percentage(self):
        """Test ATB percentage calculation."""
        data = {
            "id": "test1", "name": "Test", "max_hp": 100,
            "attack": 10, "defense": 10, "speed": 10, "atb_speed": 10
        }
        char = Character(data)
        
        char.atb_value = 50.0
        assert char.get_atb_percentage() == 0.5


class TestHero:
    """Tests for Hero class."""
    
    def test_hero_initialization(self):
        """Test hero initializes correctly."""
        data = {
            "id": "hero1", "name": "Mario", "max_hp": 100, "max_mp": 50,
            "attack": 15, "defense": 10, "speed": 12, "atb_speed": 10
        }
        hero = Hero(data)
        
        assert isinstance(hero, Character)
        assert hero.name == "Mario"


class TestEnemy:
    """Tests for Enemy class."""
    
    def test_enemy_initialization(self):
        """Test enemy initializes with rewards."""
        data = {
            "id": "enemy1", "name": "Goomba", "max_hp": 30,
            "attack": 8, "defense": 5, "speed": 8, "atb_speed": 8,
            "exp_reward": 10, "gold_reward": 5
        }
        enemy = Enemy(data)
        
        assert isinstance(enemy, Character)
        assert enemy.name == "Goomba"
        assert enemy.exp_reward == 10
        assert enemy.gold_reward == 5
