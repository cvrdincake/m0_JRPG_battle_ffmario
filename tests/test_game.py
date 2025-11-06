"""Tests for the Game class and main game loop."""

import pytest
import pygame
import json
import os
from unittest.mock import Mock, patch, MagicMock
from src.game import Game, DEFAULT_FPS, DEFAULT_WIDTH, DEFAULT_HEIGHT, FIXED_TIMESTEP


@pytest.fixture
def mock_pygame():
    """Mock Pygame initialization."""
    with patch('src.game.pygame') as mock_pg:
        mock_pg.init.return_value = None
        mock_pg.display.get_init.return_value = True
        mock_pg.display.set_mode.return_value = Mock()
        mock_pg.display.set_caption.return_value = None
        mock_pg.time.Clock.return_value = Mock()
        # Set pygame constants from real pygame module
        mock_pg.QUIT = pygame.QUIT
        mock_pg.KEYDOWN = pygame.KEYDOWN
        mock_pg.K_ESCAPE = pygame.K_ESCAPE
        yield mock_pg


@pytest.fixture
def temp_config_file(tmp_path):
    """Create a temporary config file."""
    config = {
        "display": {
            "width": 1280,
            "height": 720,
            "fps": 60,
            "title": "Test Game"
        },
        "debug": {
            "show_fps": True,
            "show_hitboxes": False,
            "god_mode": False
        },
        "paths": {
            "sprites": "assets/sprites",
            "animations": "assets/animations",
            "data": "assets/data"
        }
    }
    
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    config_file = config_dir / "settings.json"
    
    with open(config_file, 'w') as f:
        json.dump(config, f)
    
    return config_file


class TestGameInitialization:
    """Test Game class initialization."""
    
    def test_init_loads_config(self, mock_pygame, temp_config_file, monkeypatch):
        """Test that initialization loads configuration file."""
        # Adjust path to find temp config
        original_file = os.path.abspath(__file__)
        config_path = str(temp_config_file)
        
        with patch('os.path.join', return_value=config_path):
            with patch('os.path.abspath', return_value=config_path):
                with patch('os.path.exists', return_value=True):
                    with patch('src.game.Party'), patch('src.game.EnemyGroup'), \
                         patch('src.game.Hero'), patch('src.game.Enemy'), \
                         patch('src.game.StateManager'):
                        game = Game()
                        
                        assert game.config is not None
                        assert 'display' in game.config
                        assert game.config['display']['width'] == 1280
    
    def test_init_raises_on_missing_config(self, mock_pygame):
        """Test that initialization raises FileNotFoundError for missing config."""
        with patch('os.path.exists', return_value=False):
            with pytest.raises(FileNotFoundError):
                Game()
    
    def test_init_raises_on_invalid_json(self, mock_pygame, tmp_path, monkeypatch):
        """Test that initialization raises ValueError for invalid JSON."""
        # Create invalid JSON file
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        config_file = config_dir / "settings.json"
        
        with open(config_file, 'w') as f:
            f.write("{ invalid json }")
        
        config_path = str(config_file)
        
        with patch('os.path.join', return_value=config_path):
            with patch('os.path.abspath', return_value=config_path):
                with patch('os.path.exists', return_value=True):
                    with pytest.raises(ValueError, match="Invalid JSON"):
                        Game()
    
    def test_init_creates_display(self, mock_pygame, temp_config_file):
        """Test that initialization creates Pygame display."""
        config_path = str(temp_config_file)
        
        with patch('os.path.join', return_value=config_path):
            with patch('os.path.abspath', return_value=config_path):
                with patch('os.path.exists', return_value=True):
                    with patch('src.game.Party'), patch('src.game.EnemyGroup'), \
                         patch('src.game.Hero'), patch('src.game.Enemy'), \
                         patch('src.game.StateManager'):
                        game = Game()
                        
                        mock_pygame.display.set_mode.assert_called_once_with((1280, 720))
                        mock_pygame.display.set_caption.assert_called_once()
    
    def test_init_creates_clock(self, mock_pygame, temp_config_file):
        """Test that initialization creates Pygame clock."""
        config_path = str(temp_config_file)
        
        with patch('os.path.join', return_value=config_path):
            with patch('os.path.abspath', return_value=config_path):
                with patch('os.path.exists', return_value=True):
                    with patch('src.game.Party'), patch('src.game.EnemyGroup'), \
                         patch('src.game.Hero'), patch('src.game.Enemy'), \
                         patch('src.game.StateManager'):
                        game = Game()
                        
                        assert game.clock is not None
                        assert game.fixed_dt == FIXED_TIMESTEP
                        assert game.dt_accumulator == 0.0
    
    def test_init_creates_state_manager(self, mock_pygame, temp_config_file):
        """Test that initialization creates StateManager."""
        config_path = str(temp_config_file)
        
        with patch('os.path.join', return_value=config_path):
            with patch('os.path.abspath', return_value=config_path):
                with patch('os.path.exists', return_value=True):
                    with patch('src.game.Party'), patch('src.game.EnemyGroup'), \
                         patch('src.game.Hero'), patch('src.game.Enemy'):
                        with patch('src.game.StateManager') as mock_sm:
                            game = Game()
                            
                            mock_sm.assert_called_once()
                            assert hasattr(game, 'state_manager')


class TestGameLoop:
    """Test main game loop functionality."""
    
    def test_run_starts_game_loop(self, mock_pygame, temp_config_file):
        """Test that run() starts the game loop."""
        config_path = str(temp_config_file)
        
        with patch('os.path.join', return_value=config_path):
            with patch('os.path.abspath', return_value=config_path):
                with patch('os.path.exists', return_value=True):
                    with patch('src.game.Party'), patch('src.game.EnemyGroup'), \
                         patch('src.game.Hero'), patch('src.game.Enemy'), \
                         patch('src.game.StateManager'):
                        game = Game()
                        game.clock.tick = Mock(return_value=16.67)  # ~60 FPS
                        
                        # Simulate one iteration then exit
                        call_count = [0]
                        def mock_peek():
                            call_count[0] += 1
                            if call_count[0] > 1:
                                game.running = False
                            return None
                        
                        game.state_manager.peek = mock_peek
                        game.state_manager.is_empty = Mock(return_value=True)
                        
                        game.run()
                        
                        assert not game.running
    
    def test_fixed_timestep_accumulation(self, mock_pygame, temp_config_file):
        """Test fixed timestep accumulator pattern."""
        config_path = str(temp_config_file)
        
        with patch('os.path.join', return_value=config_path):
            with patch('os.path.abspath', return_value=config_path):
                with patch('os.path.exists', return_value=True):
                    with patch('src.game.Party'), patch('src.game.EnemyGroup'), \
                         patch('src.game.Hero'), patch('src.game.Enemy'), \
                         patch('src.game.StateManager'):
                        game = Game()
                        
                        # Simulate a large dt (slow frame)
                        game.update(0.1)  # 100ms
                        
                        # Should accumulate but not overflow
                        assert game.dt_accumulator < game.fixed_dt
    
    def test_delta_time_capping(self, mock_pygame, temp_config_file):
        """Test that delta time is capped to prevent spiral of death."""
        config_path = str(temp_config_file)
        
        with patch('os.path.join', return_value=config_path):
            with patch('os.path.abspath', return_value=config_path):
                with patch('os.path.exists', return_value=True):
                    with patch('src.game.Party'), patch('src.game.EnemyGroup'), \
                         patch('src.game.Hero'), patch('src.game.Enemy'), \
                         patch('src.game.StateManager'):
                        game = Game()
                        game.clock.tick = Mock(return_value=1000)  # 1 second (very slow)
                        
                        # Run one frame
                        game.running = True
                        call_count = [0]
                        def mock_peek():
                            call_count[0] += 1
                            if call_count[0] > 0:
                                game.running = False
                            return None
                        
                        game.state_manager.peek = mock_peek
                        game.state_manager.is_empty = Mock(return_value=True)
                        
                        with patch('src.game.pygame.event.get', return_value=[]):
                            game.run()
                        
                        # dt_accumulator should be capped, not 1.0
                        assert game.dt_accumulator <= 0.25


class TestEventHandling:
    """Test event handling."""
    
    def test_handle_events_processes_quit(self, mock_pygame, temp_config_file):
        """Test that QUIT event stops the game."""
        config_path = str(temp_config_file)
        
        with patch('os.path.join', return_value=config_path):
            with patch('os.path.abspath', return_value=config_path):
                with patch('os.path.exists', return_value=True):
                    with patch('src.game.Party'), patch('src.game.EnemyGroup'), \
                         patch('src.game.Hero'), patch('src.game.Enemy'), \
                         patch('src.game.StateManager'):
                        game = Game()
                        game.running = True
                        
                        quit_event = Mock()
                        quit_event.type = pygame.QUIT
                        
                        with patch('src.game.pygame.event.get', return_value=[quit_event]):
                            game.handle_events()
                        
                        assert not game.running
    
    def test_handle_events_processes_escape(self, mock_pygame, temp_config_file):
        """Test that ESC key stops the game."""
        config_path = str(temp_config_file)
        
        with patch('os.path.join', return_value=config_path):
            with patch('os.path.abspath', return_value=config_path):
                with patch('os.path.exists', return_value=True):
                    with patch('src.game.Party'), patch('src.game.EnemyGroup'), \
                         patch('src.game.Hero'), patch('src.game.Enemy'), \
                         patch('src.game.StateManager'):
                        game = Game()
                        game.running = True
                        
                        esc_event = Mock()
                        esc_event.type = pygame.KEYDOWN
                        esc_event.key = pygame.K_ESCAPE
                        
                        with patch('src.game.pygame.event.get', return_value=[esc_event]):
                            game.handle_events()
                        
                        assert not game.running
    
    def test_handle_events_delegates_to_state(self, mock_pygame, temp_config_file):
        """Test that events are delegated to current state."""
        config_path = str(temp_config_file)
        
        with patch('os.path.join', return_value=config_path):
            with patch('os.path.abspath', return_value=config_path):
                with patch('os.path.exists', return_value=True):
                    with patch('src.game.Party'), patch('src.game.EnemyGroup'), \
                         patch('src.game.Hero'), patch('src.game.Enemy'), \
                         patch('src.game.StateManager'):
                        game = Game()
                        
                        mock_state = Mock()
                        game.state_manager.peek = Mock(return_value=mock_state)
                        
                        test_event = Mock()
                        test_event.type = pygame.USEREVENT
                        
                        with patch('src.game.pygame.event.get', return_value=[test_event]):
                            game.handle_events()
                        
                        mock_state.handle_event.assert_called_once_with(test_event)


class TestRendering:
    """Test rendering functionality."""
    
    def test_render_clears_screen(self, mock_pygame, temp_config_file):
        """Test that render clears the screen."""
        config_path = str(temp_config_file)
        
        with patch('os.path.join', return_value=config_path):
            with patch('os.path.abspath', return_value=config_path):
                with patch('os.path.exists', return_value=True):
                    with patch('src.game.Party'), patch('src.game.EnemyGroup'), \
                         patch('src.game.Hero'), patch('src.game.Enemy'), \
                         patch('src.game.StateManager'):
                        game = Game()
                        game.screen = Mock()
                        game.state_manager.peek = Mock(return_value=None)
                        
                        game.render()
                        
                        game.screen.fill.assert_called_once_with((0, 0, 0))
    
    def test_render_delegates_to_state(self, mock_pygame, temp_config_file):
        """Test that render delegates to current state."""
        config_path = str(temp_config_file)
        
        with patch('os.path.join', return_value=config_path):
            with patch('os.path.abspath', return_value=config_path):
                with patch('os.path.exists', return_value=True):
                    with patch('src.game.Party'), patch('src.game.EnemyGroup'), \
                         patch('src.game.Hero'), patch('src.game.Enemy'), \
                         patch('src.game.StateManager'):
                        game = Game()
                        game.screen = Mock()
                        
                        mock_state = Mock()
                        game.state_manager.peek = Mock(return_value=mock_state)
                        
                        game.render()
                        
                        mock_state.render.assert_called_once_with(game.screen)
    
    def test_render_displays_fps_when_enabled(self, mock_pygame, temp_config_file):
        """Test that FPS counter is displayed when enabled."""
        config_path = str(temp_config_file)
        
        with patch('os.path.join', return_value=config_path):
            with patch('os.path.abspath', return_value=config_path):
                with patch('os.path.exists', return_value=True):
                    with patch('src.game.Party'), patch('src.game.EnemyGroup'), \
                         patch('src.game.Hero'), patch('src.game.Enemy'), \
                         patch('src.game.StateManager'):
                        game = Game()
                        game.screen = Mock()
                        game.show_fps = True
                        game.state_manager.peek = Mock(return_value=None)
                        game.clock.get_fps = Mock(return_value=60.0)
                        
                        mock_font = Mock()
                        mock_font.render = Mock(return_value=Mock())
                        
                        with patch('src.game.pygame.font.Font', return_value=mock_font):
                            game.render()
                        
                        mock_font.render.assert_called_once()
                        game.screen.blit.assert_called()


class TestStateManagerIntegration:
    """Test integration with StateManager."""
    
    def test_update_exits_when_state_stack_empty(self, mock_pygame, temp_config_file):
        """Test that game exits when state stack is empty."""
        config_path = str(temp_config_file)
        
        with patch('os.path.join', return_value=config_path):
            with patch('os.path.abspath', return_value=config_path):
                with patch('os.path.exists', return_value=True):
                    with patch('src.game.Party'), patch('src.game.EnemyGroup'), \
                         patch('src.game.Hero'), patch('src.game.Enemy'), \
                         patch('src.game.StateManager'):
                        game = Game()
                        game.running = True
                        game.state_manager.is_empty = Mock(return_value=True)
                        game.state_manager.peek = Mock(return_value=None)
                        
                        game.update(0.016)
                        
                        assert not game.running
    
    def test_update_calls_state_update_with_fixed_dt(self, mock_pygame, temp_config_file):
        """Test that state update is called with fixed_dt."""
        config_path = str(temp_config_file)
        
        with patch('os.path.join', return_value=config_path):
            with patch('os.path.abspath', return_value=config_path):
                with patch('os.path.exists', return_value=True):
                    with patch('src.game.Party'), patch('src.game.EnemyGroup'), \
                         patch('src.game.Hero'), patch('src.game.Enemy'), \
                         patch('src.game.StateManager'):
                        game = Game()
                        
                        mock_state = Mock()
                        game.state_manager.peek = Mock(return_value=mock_state)
                        game.state_manager.is_empty = Mock(return_value=False)
                        
                        # Provide enough dt for one fixed update
                        game.update(game.fixed_dt)
                        
                        # Should be called with fixed_dt
                        mock_state.update.assert_called_with(game.fixed_dt)
