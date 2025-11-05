"""Test for Party.get_random_alive_member method."""

import pytest
from src.entities.party import Party
from src.entities.character import Hero


def test_get_random_alive_member():
    """Test getting random alive member."""
    party = Party()
    hero1_data = {
        'id': 'hero1',
        'name': 'Hero1',
        'max_hp': 100,
        'attack': 20,
        'defense': 10,
        'speed': 10,
        'atb_speed': 10
    }
    hero2_data = {
        'id': 'hero2',
        'name': 'Hero2',
        'max_hp': 100,
        'attack': 20,
        'defense': 10,
        'speed': 10,
        'atb_speed': 10
    }
    
    hero1 = Hero(hero1_data)
    hero2 = Hero(hero2_data)
    
    party.add_member(hero1)
    party.add_member(hero2)
    
    # Both alive
    random_member = party.get_random_alive_member()
    assert random_member in [hero1, hero2]
    
    # Kill hero1
    hero1.current_hp = 0
    hero1.is_alive = False
    
    # Should only return hero2
    for _ in range(10):  # Test multiple times
        assert party.get_random_alive_member() == hero2
    
    # Kill both
    hero2.current_hp = 0
    hero2.is_alive = False
    
    # Should return None
    assert party.get_random_alive_member() is None
