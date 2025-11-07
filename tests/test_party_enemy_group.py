"""Unit tests for Party and EnemyGroup management."""

import pytest
from src.entities.party import Party, PARTY_X_MIN, PARTY_X_MAX, MIN_VERTICAL_SPACING
from src.entities.enemy_group import EnemyGroup, ENEMY_X_MIN, ENEMY_X_MAX
from src.entities.character import Hero, Enemy


class TestParty:
    """Tests for Party class."""
    
    def test_party_initialization(self):
        """Test party initializes empty."""
        party = Party()
        assert len(party) == 0
        assert party.size() == 0
        assert party.is_full() is False
    
    def test_add_member_success(self):
        """Test adding member to party."""
        party = Party()
        hero_data = {
            'id': 'hero1',
            'name': 'Hero',
            'max_hp': 100,
            'max_mp': 50,
            'attack': 15,
            'defense': 10,
            'speed': 12,
            'atb_speed': 10
        }
        hero = Hero(hero_data)
        
        assert party.add_member(hero) is True
        assert len(party) == 1
        assert hero in party
    
    def test_add_member_when_full(self):
        """Test adding member to full party returns False."""
        party = Party()
        
        # Fill party to max
        for i in range(Party.MAX_SIZE):
            hero_data = {
                'id': f'hero{i}',
                'name': f'Hero{i}',
                'max_hp': 100,
                'max_mp': 50,
                'attack': 15,
                'defense': 10,
                'speed': 12,
                'atb_speed': 10
            }
            hero = Hero(hero_data)
            party.add_member(hero)
        
        assert party.is_full() is True
        
        # Try to add one more
        extra_hero_data = {
            'id': 'extra',
            'name': 'Extra',
            'max_hp': 100,
            'max_mp': 50,
            'attack': 15,
            'defense': 10,
            'speed': 12,
            'atb_speed': 10
        }
        extra = Hero(extra_hero_data)
        assert party.add_member(extra) is False
        assert len(party) == Party.MAX_SIZE
    
    def test_add_non_hero_raises_error(self):
        """Test adding non-Hero raises TypeError."""
        party = Party()
        enemy_data = {
            'id': 'enemy1',
            'name': 'Enemy',
            'max_hp': 50,
            'attack': 10,
            'defense': 5,
            'speed': 8,
            'atb_speed': 8,
            'exp_reward': 10,
            'gold_reward': 5
        }
        enemy = Enemy(enemy_data)
        
        with pytest.raises(TypeError, match="Party can only contain Hero instances"):
            party.add_member(enemy)
    
    def test_remove_member(self):
        """Test removing member from party."""
        party = Party()
        hero_data = {
            'id': 'hero1',
            'name': 'Hero',
            'max_hp': 100,
            'max_mp': 50,
            'attack': 15,
            'defense': 10,
            'speed': 12,
            'atb_speed': 10
        }
        hero = Hero(hero_data)
        party.add_member(hero)
        
        assert party.remove_member(hero) is True
        assert len(party) == 0
        assert hero not in party
    
    def test_remove_nonexistent_member(self):
        """Test removing member not in party returns False."""
        party = Party()
        hero_data = {
            'id': 'hero1',
            'name': 'Hero',
            'max_hp': 100,
            'max_mp': 50,
            'attack': 15,
            'defense': 10,
            'speed': 12,
            'atb_speed': 10
        }
        hero = Hero(hero_data)
        
        assert party.remove_member(hero) is False
    
    def test_get_member_by_id(self):
        """Test getting member by ID."""
        party = Party()
        hero_data = {
            'id': 'hero1',
            'name': 'Hero',
            'max_hp': 100,
            'max_mp': 50,
            'attack': 15,
            'defense': 10,
            'speed': 12,
            'atb_speed': 10
        }
        hero = Hero(hero_data)
        party.add_member(hero)
        
        found = party.get_member_by_id('hero1')
        assert found is hero
    
    def test_get_member_by_id_not_found(self):
        """Test getting member by nonexistent ID returns None."""
        party = Party()
        assert party.get_member_by_id('nonexistent') is None
    
    def test_get_alive_members(self):
        """Test getting only alive members."""
        party = Party()
        
        # Add two heroes
        hero1_data = {
            'id': 'hero1',
            'name': 'Hero1',
            'max_hp': 100,
            'max_mp': 50,
            'attack': 15,
            'defense': 10,
            'speed': 12,
            'atb_speed': 10
        }
        hero1 = Hero(hero1_data)
        
        hero2_data = {
            'id': 'hero2',
            'name': 'Hero2',
            'max_hp': 100,
            'max_mp': 50,
            'attack': 15,
            'defense': 10,
            'speed': 12,
            'atb_speed': 10
        }
        hero2 = Hero(hero2_data)
        
        party.add_member(hero1)
        party.add_member(hero2)
        
        # Kill hero2
        hero2.take_damage(1000)
        
        alive = party.get_alive_members()
        assert len(alive) == 1
        assert hero1 in alive
        assert hero2 not in alive
    
    def test_all_dead(self):
        """Test checking if entire party is dead."""
        party = Party()
        
        hero_data = {
            'id': 'hero1',
            'name': 'Hero',
            'max_hp': 100,
            'max_mp': 50,
            'attack': 15,
            'defense': 10,
            'speed': 12,
            'atb_speed': 10
        }
        hero = Hero(hero_data)
        party.add_member(hero)
        
        assert party.all_dead() is False
        
        hero.take_damage(1000)
        assert party.all_dead() is True
    
    def test_all_dead_empty_party(self):
        """Test that empty party is considered all dead."""
        party = Party()
        assert party.all_dead() is True
    
    def test_clear(self):
        """Test clearing all members."""
        party = Party()
        
        for i in range(3):
            hero_data = {
                'id': f'hero{i}',
                'name': f'Hero{i}',
                'max_hp': 100,
                'max_mp': 50,
                'attack': 15,
                'defense': 10,
                'speed': 12,
                'atb_speed': 10
            }
            hero = Hero(hero_data)
            party.add_member(hero)
        
        party.clear()
        assert len(party) == 0
    
    def test_get_positions_single_member(self):
        """Test position calculation for single member."""
        party = Party()
        hero_data = {
            'id': 'hero1',
            'name': 'Hero',
            'max_hp': 100,
            'max_mp': 50,
            'attack': 15,
            'defense': 10,
            'speed': 12,
            'atb_speed': 10
        }
        hero = Hero(hero_data)
        party.add_member(hero)
        
        positions = party.get_positions()
        assert len(positions) == 1
        
        x, y = positions[0]
        # Should be centered in party X range
        assert PARTY_X_MIN <= x <= PARTY_X_MAX
        # Should be centered vertically (360 for single member)
        assert y == 360
    
    def test_get_positions_multiple_members(self):
        """Test position calculation for multiple members."""
        party = Party()
        
        for i in range(4):
            hero_data = {
                'id': f'hero{i}',
                'name': f'Hero{i}',
                'max_hp': 100,
                'max_mp': 50,
                'attack': 15,
                'defense': 10,
                'speed': 12,
                'atb_speed': 10
            }
            hero = Hero(hero_data)
            party.add_member(hero)
        
        positions = party.get_positions()
        assert len(positions) == 4
        
        # Check vertical spacing
        for i in range(len(positions) - 1):
            _, y1 = positions[i]
            _, y2 = positions[i + 1]
            assert y2 - y1 == MIN_VERTICAL_SPACING
        
        # Check X positions are in valid range
        for x, y in positions:
            assert PARTY_X_MIN <= x <= PARTY_X_MAX
    
    def test_get_positions_empty_party(self):
        """Test position calculation for empty party."""
        party = Party()
        positions = party.get_positions()
        assert positions == []
    
    def test_get_member_position(self):
        """Test getting position for specific member."""
        party = Party()
        hero_data = {
            'id': 'hero1',
            'name': 'Hero',
            'max_hp': 100,
            'max_mp': 50,
            'attack': 15,
            'defense': 10,
            'speed': 12,
            'atb_speed': 10
        }
        hero = Hero(hero_data)
        party.add_member(hero)
        
        pos = party.get_member_position(hero)
        assert pos is not None
        assert len(pos) == 2
    
    def test_get_member_position_not_in_party(self):
        """Test getting position for member not in party."""
        party = Party()
        hero_data = {
            'id': 'hero1',
            'name': 'Hero',
            'max_hp': 100,
            'max_mp': 50,
            'attack': 15,
            'defense': 10,
            'speed': 12,
            'atb_speed': 10
        }
        hero = Hero(hero_data)
        
        pos = party.get_member_position(hero)
        assert pos is None
    
    def test_iteration(self):
        """Test iterating over party members."""
        party = Party()
        
        heroes = []
        for i in range(3):
            hero_data = {
                'id': f'hero{i}',
                'name': f'Hero{i}',
                'max_hp': 100,
                'max_mp': 50,
                'attack': 15,
                'defense': 10,
                'speed': 12,
                'atb_speed': 10
            }
            hero = Hero(hero_data)
            heroes.append(hero)
            party.add_member(hero)
        
        for i, member in enumerate(party):
            assert member is heroes[i]
    
    def test_indexing(self):
        """Test indexing party members."""
        party = Party()
        hero_data = {
            'id': 'hero1',
            'name': 'Hero',
            'max_hp': 100,
            'max_mp': 50,
            'attack': 15,
            'defense': 10,
            'speed': 12,
            'atb_speed': 10
        }
        hero = Hero(hero_data)
        party.add_member(hero)
        
        assert party[0] is hero


class TestEnemyGroup:
    """Tests for EnemyGroup class."""
    
    def test_enemy_group_initialization(self):
        """Test enemy group initializes empty."""
        group = EnemyGroup()
        assert len(group) == 0
        assert group.size() == 0
        assert group.is_full() is False
    
    def test_add_enemy_success(self):
        """Test adding enemy to group."""
        group = EnemyGroup()
        enemy_data = {
            'id': 'enemy1',
            'name': 'Goblin',
            'max_hp': 50,
            'attack': 10,
            'defense': 5,
            'speed': 8,
            'atb_speed': 8,
            'exp_reward': 10,
            'gold_reward': 5
        }
        enemy = Enemy(enemy_data)
        
        assert group.add_enemy(enemy) is True
        assert len(group) == 1
        assert enemy in group
    
    def test_add_enemy_when_full(self):
        """Test adding enemy to full group returns False."""
        group = EnemyGroup()
        
        # Fill group to max
        for i in range(EnemyGroup.MAX_SIZE):
            enemy_data = {
                'id': f'enemy{i}',
                'name': f'Goblin{i}',
                'max_hp': 50,
                'attack': 10,
                'defense': 5,
                'speed': 8,
                'atb_speed': 8,
                'exp_reward': 10,
                'gold_reward': 5
            }
            enemy = Enemy(enemy_data)
            group.add_enemy(enemy)
        
        assert group.is_full() is True
        
        # Try to add one more
        extra_data = {
            'id': 'extra',
            'name': 'Extra',
            'max_hp': 50,
            'attack': 10,
            'defense': 5,
            'speed': 8,
            'atb_speed': 8,
            'exp_reward': 10,
            'gold_reward': 5
        }
        extra = Enemy(extra_data)
        assert group.add_enemy(extra) is False
        assert len(group) == EnemyGroup.MAX_SIZE
    
    def test_add_non_enemy_raises_error(self):
        """Test adding non-Enemy raises TypeError."""
        group = EnemyGroup()
        hero_data = {
            'id': 'hero1',
            'name': 'Hero',
            'max_hp': 100,
            'max_mp': 50,
            'attack': 15,
            'defense': 10,
            'speed': 12,
            'atb_speed': 10
        }
        hero = Hero(hero_data)
        
        with pytest.raises(TypeError, match="EnemyGroup can only contain Enemy instances"):
            group.add_enemy(hero)
    
    def test_get_positions_multiple_enemies(self):
        """Test position calculation for multiple enemies."""
        group = EnemyGroup()
        
        for i in range(6):
            enemy_data = {
                'id': f'enemy{i}',
                'name': f'Goblin{i}',
                'max_hp': 50,
                'attack': 10,
                'defense': 5,
                'speed': 8,
                'atb_speed': 8,
                'exp_reward': 10,
                'gold_reward': 5
            }
            enemy = Enemy(enemy_data)
            group.add_enemy(enemy)
        
        positions = group.get_positions()
        assert len(positions) == 6
        
        # Check vertical spacing
        for i in range(len(positions) - 1):
            _, y1 = positions[i]
            _, y2 = positions[i + 1]
            assert y2 - y1 == MIN_VERTICAL_SPACING
        
        # Check X positions are in valid range
        for x, y in positions:
            assert ENEMY_X_MIN <= x <= ENEMY_X_MAX
    
    def test_get_alive_enemies(self):
        """Test getting only alive enemies."""
        group = EnemyGroup()
        
        enemy1_data = {
            'id': 'enemy1',
            'name': 'Goblin1',
            'max_hp': 50,
            'attack': 10,
            'defense': 5,
            'speed': 8,
            'atb_speed': 8,
            'exp_reward': 10,
            'gold_reward': 5
        }
        enemy1 = Enemy(enemy1_data)
        
        enemy2_data = {
            'id': 'enemy2',
            'name': 'Goblin2',
            'max_hp': 50,
            'attack': 10,
            'defense': 5,
            'speed': 8,
            'atb_speed': 8,
            'exp_reward': 10,
            'gold_reward': 5
        }
        enemy2 = Enemy(enemy2_data)
        
        group.add_enemy(enemy1)
        group.add_enemy(enemy2)
        
        # Kill enemy2
        enemy2.take_damage(1000)
        
        alive = group.get_alive_enemies()
        assert len(alive) == 1
        assert enemy1 in alive
        assert enemy2 not in alive
    
    def test_all_dead(self):
        """Test checking if entire group is dead."""
        group = EnemyGroup()
        
        enemy_data = {
            'id': 'enemy1',
            'name': 'Goblin',
            'max_hp': 50,
            'attack': 10,
            'defense': 5,
            'speed': 8,
            'atb_speed': 8,
            'exp_reward': 10,
            'gold_reward': 5
        }
        enemy = Enemy(enemy_data)
        group.add_enemy(enemy)
        
        assert group.all_dead() is False
        
        enemy.take_damage(1000)
        assert group.all_dead() is True
    
    def test_get_random_alive_enemy(self):
        """Test getting random alive enemy."""
        group = EnemyGroup()
        
        enemy_data = {
            'id': 'enemy1',
            'name': 'Goblin',
            'max_hp': 50,
            'attack': 10,
            'defense': 5,
            'speed': 8,
            'atb_speed': 8,
            'exp_reward': 10,
            'gold_reward': 5
        }
        enemy = Enemy(enemy_data)
        group.add_enemy(enemy)
        
        random_enemy = group.get_random_alive_enemy()
        assert random_enemy is enemy
    
    def test_get_random_alive_enemy_all_dead(self):
        """Test getting random enemy when all dead returns None."""
        group = EnemyGroup()
        
        enemy_data = {
            'id': 'enemy1',
            'name': 'Goblin',
            'max_hp': 50,
            'attack': 10,
            'defense': 5,
            'speed': 8,
            'atb_speed': 8,
            'exp_reward': 10,
            'gold_reward': 5
        }
        enemy = Enemy(enemy_data)
        group.add_enemy(enemy)
        enemy.take_damage(1000)
        
        random_enemy = group.get_random_alive_enemy()
        assert random_enemy is None
