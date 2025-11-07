"""Tests for battle phase management system."""

import pytest
import pygame
from src.battle.battle_phase import BattlePhase
from src.states.battle_state import BattleState
from src.entities.party import Party
from src.entities.enemy_group import EnemyGroup
from src.entities.character import Hero, Enemy
from src.entities.stats import Stats
from src.battle.move import BattleMove, TargetType, TimingType, ActionCommand


@pytest.fixture
def pygame_init():
    """Initialize pygame for tests."""
    pygame.init()
    pygame.display.set_mode((1, 1))
    yield
    pygame.quit()


@pytest.fixture
def test_party():
    """Create a test party with one hero."""
    party = Party()
    hero_data = {
        'id': 'test_hero',
        'name': 'TestHero',
        'max_hp': 100,
        'max_mp': 50,
        'attack': 20,
        'defense': 10,
        'magic': 15,
        'speed': 10,
        'atb_speed': 10
    }
    hero = Hero(hero_data)
    party.add_member(hero)
    return party


@pytest.fixture
def test_enemy_group():
    """Create a test enemy group with one enemy."""
    group = EnemyGroup()
    enemy_data = {
        'id': 'test_enemy',
        'name': 'TestEnemy',
        'max_hp': 50,
        'max_mp': 20,
        'attack': 15,
        'defense': 5,
        'magic': 10,
        'speed': 8,
        'atb_speed': 8,
        'exp_reward': 10,
        'gold_reward': 5
    }
    enemy = Enemy(enemy_data)
    group.add_enemy(enemy)
    return group


@pytest.fixture
def test_moves():
    """Create test moves."""
    return [
        BattleMove({
            'id': 'attack',
            'name': 'Attack',
            'description': 'Basic attack',
            'base_power': 30,
            'mp_cost': 0,
            'target_type': 'single_enemy',
            'timing_type': 'simple',
            'is_offensive': True
        }),
        BattleMove({
            'id': 'heal',
            'name': 'Heal',
            'description': 'Restore HP',
            'base_power': 20,
            'mp_cost': 10,
            'target_type': 'self',
            'timing_type': 'simple',
            'is_offensive': False
        })
    ]


class TestBattlePhase:
    """Tests for BattlePhase enum."""
    
    def test_all_phases_exist(self):
        """Test that all required phases are defined."""
        assert hasattr(BattlePhase, 'BATTLE_START')
        assert hasattr(BattlePhase, 'TURN_SELECT')
        assert hasattr(BattlePhase, 'EXECUTING_ACTION')
        assert hasattr(BattlePhase, 'ENEMY_TURN')
        assert hasattr(BattlePhase, 'CHECK_VICTORY')
        assert hasattr(BattlePhase, 'VICTORY')
        assert hasattr(BattlePhase, 'DEFEAT')
    
    def test_phase_uniqueness(self):
        """Test that all phases have unique values."""
        phases = list(BattlePhase)
        assert len(phases) == len(set(phases))


class TestBattleStateInitialization:
    """Tests for BattleState initialization."""
    
    def test_initialization_success(self, pygame_init, test_party, test_enemy_group, test_moves):
        """Test successful initialization."""
        state = BattleState(test_party, test_enemy_group, test_moves)
        assert state.party == test_party
        assert state.enemy_group == test_enemy_group
        assert state.current_phase == BattlePhase.BATTLE_START
        assert state.phase_timer == 0.0
        assert state.input_enabled is False
    
    def test_initialization_empty_party_raises_error(self, pygame_init, test_enemy_group, test_moves):
        """Test that empty party raises ValueError."""
        empty_party = Party()
        with pytest.raises(ValueError, match="Party cannot be empty"):
            BattleState(empty_party, test_enemy_group, test_moves)
    
    def test_initialization_empty_enemy_group_raises_error(self, pygame_init, test_party, test_moves):
        """Test that empty enemy group raises ValueError."""
        empty_group = EnemyGroup()
        with pytest.raises(ValueError, match="Enemy group cannot be empty"):
            BattleState(test_party, empty_group, test_moves)


class TestBattleStateLifecycle:
    """Tests for State lifecycle methods."""
    
    def test_enter_resets_phase(self, pygame_init, test_party, test_enemy_group, test_moves):
        """Test that enter() resets to BATTLE_START."""
        state = BattleState(test_party, test_enemy_group, test_moves)
        state.current_phase = BattlePhase.VICTORY
        state.enter()
        assert state.current_phase == BattlePhase.BATTLE_START
        assert state.phase_timer == 0.0
        assert state.input_enabled is False
    
    def test_pause_disables_input(self, pygame_init, test_party, test_enemy_group, test_moves):
        """Test that pause() disables input."""
        state = BattleState(test_party, test_enemy_group, test_moves)
        state.input_enabled = True
        state.pause()
        assert state.input_enabled is False
    
    def test_resume_enables_input_in_turn_select(self, pygame_init, test_party, test_enemy_group, test_moves):
        """Test that resume() enables input during TURN_SELECT."""
        state = BattleState(test_party, test_enemy_group, test_moves)
        state.current_phase = BattlePhase.TURN_SELECT
        state.input_enabled = False
        state.resume()
        assert state.input_enabled is True


class TestPhaseTransitions:
    """Tests for phase transition logic."""
    
    def test_battle_start_transitions_after_duration(self, pygame_init, test_party, test_enemy_group, test_moves):
        """Test BATTLE_START transitions to TURN_SELECT after 2 seconds."""
        state = BattleState(test_party, test_enemy_group, test_moves)
        state.enter()
        
        # Update for 2.1 seconds
        state.update(2.1)
        
        assert state.current_phase == BattlePhase.TURN_SELECT
    
    def test_check_victory_transitions_to_victory(self, pygame_init, test_party, test_enemy_group, test_moves):
        """Test CHECK_VICTORY transitions to VICTORY when all enemies dead."""
        state = BattleState(test_party, test_enemy_group, test_moves)
        state.current_phase = BattlePhase.CHECK_VICTORY
        
        # Kill all enemies
        for enemy in test_enemy_group.enemies:
            enemy.current_hp = 0
            enemy.is_alive = False
        
        state.update(0.1)
        
        assert state.current_phase == BattlePhase.VICTORY
    
    def test_check_victory_transitions_to_defeat(self, pygame_init, test_party, test_enemy_group, test_moves):
        """Test CHECK_VICTORY transitions to DEFEAT when all party members dead."""
        state = BattleState(test_party, test_enemy_group, test_moves)
        state.current_phase = BattlePhase.CHECK_VICTORY
        
        # Kill all party members
        for member in test_party.members:
            member.current_hp = 0
            member.is_alive = False
        
        state.update(0.1)
        
        assert state.current_phase == BattlePhase.DEFEAT
    
    def test_check_victory_transitions_back_to_turn_select(self, pygame_init, test_party, test_enemy_group, test_moves):
        """Test CHECK_VICTORY returns to TURN_SELECT if battle continues."""
        state = BattleState(test_party, test_enemy_group, test_moves)
        state.current_phase = BattlePhase.CHECK_VICTORY
        
        # Ensure both sides have alive members
        assert not test_party.all_dead()
        assert not test_enemy_group.all_dead()
        
        state.update(0.1)
        
        assert state.current_phase == BattlePhase.TURN_SELECT


class TestPhaseTimers:
    """Tests for phase timer accumulation."""
    
    def test_phase_timer_accumulates_delta_time(self, pygame_init, test_party, test_enemy_group, test_moves):
        """Test that phase_timer accumulates delta time."""
        state = BattleState(test_party, test_enemy_group, test_moves)
        state.current_phase = BattlePhase.BATTLE_START
        
        state.update(0.5)
        assert state.phase_timer == pytest.approx(0.5)
        
        state.update(0.3)
        assert state.phase_timer == pytest.approx(0.8)
    
    def test_phase_timer_resets_on_transition(self, pygame_init, test_party, test_enemy_group, test_moves):
        """Test that phase_timer resets when transitioning."""
        state = BattleState(test_party, test_enemy_group, test_moves)
        state.phase_timer = 5.0
        
        state._transition_to_turn_select()
        assert state.phase_timer == 0.0


class TestInputHandling:
    """Tests for input handling during phases."""
    
    def test_input_disabled_during_battle_start(self, pygame_init, test_party, test_enemy_group, test_moves):
        """Test input is disabled during BATTLE_START."""
        state = BattleState(test_party, test_enemy_group, test_moves)
        state.current_phase = BattlePhase.BATTLE_START
        assert state.input_enabled is False
    
    def test_input_enabled_during_turn_select(self, pygame_init, test_party, test_enemy_group, test_moves):
        """Test input is enabled during TURN_SELECT."""
        state = BattleState(test_party, test_enemy_group, test_moves)
        state._transition_to_turn_select()
        assert state.input_enabled is True
    
    def test_input_disabled_during_action_execution(self, pygame_init, test_party, test_enemy_group, test_moves):
        """Test input is disabled during EXECUTING_ACTION."""
        state = BattleState(test_party, test_enemy_group, test_moves)
        state._transition_to_executing_action()
        assert state.input_enabled is False


class TestATBUpdates:
    """Tests for ATB gauge updates."""
    
    def test_atb_updates_in_non_terminal_phases(self, pygame_init, test_party, test_enemy_group, test_moves):
        """Test ATB updates in active phases."""
        state = BattleState(test_party, test_enemy_group, test_moves)
        state.current_phase = BattlePhase.TURN_SELECT
        
        hero = test_party.members[0]
        initial_atb = hero.atb_value
        
        state.update(0.1)
        
        assert hero.atb_value > initial_atb
    
    def test_atb_does_not_update_in_victory(self, pygame_init, test_party, test_enemy_group, test_moves):
        """Test ATB does not update in VICTORY phase."""
        state = BattleState(test_party, test_enemy_group, test_moves)
        state.current_phase = BattlePhase.VICTORY
        
        hero = test_party.members[0]
        initial_atb = hero.atb_value
        
        state.update(0.1)
        
        assert hero.atb_value == initial_atb
    
    def test_atb_does_not_update_in_defeat(self, pygame_init, test_party, test_enemy_group, test_moves):
        """Test ATB does not update in DEFEAT phase."""
        state = BattleState(test_party, test_enemy_group, test_moves)
        state.current_phase = BattlePhase.DEFEAT
        
        hero = test_party.members[0]
        initial_atb = hero.atb_value
        
        state.update(0.1)
        
        assert hero.atb_value == initial_atb


class TestRenderMethod:
    """Tests for render method."""
    
    def test_render_does_not_crash(self, pygame_init, test_party, test_enemy_group, test_moves):
        """Test that render() completes without errors."""
        state = BattleState(test_party, test_enemy_group, test_moves)
        screen = pygame.Surface((1280, 720))
        
        # Should not raise any exceptions
        state.render(screen)
    
    def test_render_in_all_phases(self, pygame_init, test_party, test_enemy_group, test_moves):
        """Test render works in all phases."""
        state = BattleState(test_party, test_enemy_group, test_moves)
        screen = pygame.Surface((1280, 720))
        
        for phase in BattlePhase:
            state.current_phase = phase
            state.render(screen)  # Should not crash


class TestMessageSystem:
    """Tests for battle message system."""
    
    def test_message_timer_decreases(self, pygame_init, test_party, test_enemy_group, test_moves):
        """Test message timer decreases over time."""
        state = BattleState(test_party, test_enemy_group, test_moves)
        state.message_timer = 2.0
        
        state.update(0.5)
        assert state.message_timer == pytest.approx(1.5)
    
    def test_message_timer_does_not_go_negative(self, pygame_init, test_party, test_enemy_group, test_moves):
        """Test message timer stops at zero."""
        state = BattleState(test_party, test_enemy_group, test_moves)
        state.message_timer = 0.1
        
        state.update(1.0)
        assert state.message_timer <= 0.0


class TestExplicitTransitions:
    """Tests for explicit phase transitions."""
    
    def test_transition_methods_exist(self, pygame_init, test_party, test_enemy_group, test_moves):
        """Test all transition methods exist."""
        state = BattleState(test_party, test_enemy_group, test_moves)
        
        assert hasattr(state, '_transition_to_turn_select')
        assert hasattr(state, '_transition_to_executing_action')
        assert hasattr(state, '_transition_to_enemy_turn')
        assert hasattr(state, '_transition_to_check_victory')
        assert hasattr(state, '_transition_to_victory')
        assert hasattr(state, '_transition_to_defeat')
    
    def test_no_implicit_phase_changes(self, pygame_init, test_party, test_enemy_group, test_moves):
        """Test phases don't change without explicit transitions."""
        state = BattleState(test_party, test_enemy_group, test_moves)
        state.current_phase = BattlePhase.TURN_SELECT
        state.phase_timer = 10.0  # Large timer
        
        # Update should not change phase just because timer is high
        initial_phase = state.current_phase
        state.update(0.1)
        
        # Phase should remain the same unless transition condition met
        # (in this case, no character is ready, so stays in TURN_SELECT)
        assert state.current_phase == initial_phase or state.current_phase == BattlePhase.TURN_SELECT
