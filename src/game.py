"""Main game class that manages the game loop and states.

This module provides the core Game class that initializes Pygame,
manages the game loop with fixed timestep, and handles state transitions
using the StateManager.
"""

import sys
import os
import json
import pygame
from typing import Optional, Dict, Any
from src.states.state_manager import StateManager
from src.states.battle_state import BattleState
from src.entities.party import Party
from src.entities.enemy_group import EnemyGroup
from src.entities.character import Hero, Enemy
from src.entities.stats import Stats


# Constants
DEFAULT_FPS = 60
DEFAULT_WIDTH = 1280
DEFAULT_HEIGHT = 720
DEFAULT_TITLE = "JRPG Battle Prototype"
FIXED_TIMESTEP = 1.0 / 60.0  # 60 updates per second


class Game:
    """Main game class managing the game loop and rendering.
    
    Uses fixed timestep accumulator pattern for consistent physics/game logic
    regardless of frame rate. Integrates with StateManager for state management.
    
    Attributes:
        config: Game configuration loaded from settings.json.
        screen: Pygame display surface.
        clock: Pygame clock for frame timing.
        running: Whether the game is running.
        fps: Target frames per second for rendering.
        fixed_dt: Fixed timestep for game logic updates.
        dt_accumulator: Accumulator for fixed timestep pattern.
        state_manager: Manages game states with stack-based pattern.
        show_fps: Whether to display FPS counter.
    """
    
    def __init__(self) -> None:
        """Initialize the game and Pygame.
        
        Raises:
            pygame.error: If Pygame initialization fails.
            FileNotFoundError: If settings.json not found.
        """
        # Initialize Pygame
        pygame.init()
        
        if not pygame.display.get_init():
            raise pygame.error("Failed to initialize Pygame display")
        
        # Load configuration
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'settings.json')
        config_path = os.path.abspath(config_path)
        
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        try:
            with open(config_path, 'r') as f:
                self.config: Dict[str, Any] = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in configuration file: {e}")
        
        # Extract display settings
        display_config = self.config.get('display', {})
        width = display_config.get('width', DEFAULT_WIDTH)
        height = display_config.get('height', DEFAULT_HEIGHT)
        self.fps = display_config.get('fps', DEFAULT_FPS)
        title = display_config.get('title', DEFAULT_TITLE)
        
        # Create display
        try:
            self.screen: pygame.Surface = pygame.display.set_mode((width, height))
            if self.screen is None:
                raise pygame.error("pygame.display.set_mode returned None")
            pygame.display.set_caption(title)
        except pygame.error as e:
            raise pygame.error(f"Failed to create display: {e}")
        
        # Initialize clock and timing
        self.clock: pygame.time.Clock = pygame.time.Clock()
        self.running: bool = False
        self.fixed_dt: float = FIXED_TIMESTEP
        self.dt_accumulator: float = 0.0
        
        # Debug settings
        debug_config = self.config.get('debug', {})
        self.show_fps: bool = debug_config.get('show_fps', True)
        
        # Ensure required directories exist
        self._ensure_directories()
        
        # Initialize state manager
        self.state_manager: StateManager = StateManager()
        
        # Create initial battle state
        self._create_initial_state()
    
    def _create_initial_state(self) -> None:
        """Create and push the initial game state.
        
        Creates a battle state with a party and enemy group for testing.
        """
        # Create party
        party = Party()
        hero1 = Hero(
            name="Warrior",
            stats=Stats(max_hp=100, max_mp=30, attack=25, defense=15, magic=10, speed=8)
        )
        hero2 = Hero(
            name="Mage",
            stats=Stats(max_hp=70, max_mp=80, attack=10, defense=8, magic=30, speed=12)
        )
        party.add_member(hero1)
        party.add_member(hero2)
        
        # Create enemy group
        enemy_group = EnemyGroup()
        enemy1 = Enemy(
            name="Slime",
            stats=Stats(max_hp=50, max_mp=10, attack=15, defense=8, magic=5, speed=6),
            exp_reward=25,
            gold_reward=10
        )
        enemy2 = Enemy(
            name="Goblin",
            stats=Stats(max_hp=60, max_mp=20, attack=18, defense=12, magic=8, speed=10),
            exp_reward=35,
            gold_reward=15
        )
        enemy_group.add_enemy(enemy1)
        enemy_group.add_enemy(enemy2)
        
        # Create and push battle state
        battle_state = BattleState(self.screen, party, enemy_group)
        self.state_manager.push(battle_state)
    
    def _ensure_directories(self) -> None:
        """Ensure all required directories exist."""
        base_path = os.path.dirname(os.path.dirname(__file__))
        paths = self.config.get('paths', {})
        
        for path_type, path in paths.items():
            full_path = os.path.join(base_path, path)
            try:
                os.makedirs(full_path, exist_ok=True)
            except OSError as e:
                print(f"Warning: Could not create directory {full_path}: {e}")
    
    def run(self) -> None:
        """Main game loop with fixed timestep accumulator pattern.
        
        Uses fixed timestep for game logic updates to ensure consistent
        physics/game behavior regardless of frame rate. Rendering runs
        at variable frame rate controlled by self.fps.
        """
        self.running = True
        
        print(f"Starting game at {self.config['display']['width']}x{self.config['display']['height']}")
        print(f"Target FPS: {self.fps}")
        print(f"Fixed timestep: {self.fixed_dt:.4f}s ({1.0/self.fixed_dt:.0f} updates/sec)")
        print("Press ESC or close window to exit")
        
        while self.running:
            # Calculate delta time (in seconds)
            dt = self.clock.tick(self.fps) / 1000.0
            
            # Cap delta time to prevent spiral of death
            if dt > 0.25:
                dt = 0.25
            
            # Handle events
            self.handle_events()
            
            # Update game state with fixed timestep
            self.update(dt)
            
            # Render
            self.render()
        
        print("Game ended")
    
    def handle_events(self) -> None:
        """Process all Pygame events.
        
        Handles QUIT event and ESC key, then passes other events to current state.
        """
        for event in pygame.event.get():
            # Check for quit events first
            if event.type == pygame.QUIT:
                self.running = False
                continue  # Don't pass QUIT to states
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.running = False
                continue  # Don't pass ESC to states
            
            # Pass all other events to current state
            current_state = self.state_manager.peek()
            if current_state is not None:
                current_state.handle_event(event)
    
    def update(self, dt: float) -> None:
        """Update current state with fixed timestep accumulator pattern.
        
        Accumulates delta time and updates game logic in fixed timesteps
        to ensure consistent behavior independent of frame rate.
        
        Args:
            dt: Delta time in seconds since last frame.
        """
        # Add to accumulator
        self.dt_accumulator += dt
        
        # Update with fixed timestep while accumulator has enough time
        while self.dt_accumulator >= self.fixed_dt:
            current_state = self.state_manager.peek()
            if current_state is not None:
                current_state.update(self.fixed_dt)
            
            self.dt_accumulator -= self.fixed_dt
        
        # Check if state stack is empty
        if self.state_manager.is_empty():
            print("No more states, exiting...")
            self.running = False
    
    def render(self) -> None:
        """Render current state to display.
        
        Clears screen, renders current state, optionally renders FPS,
        and flips display buffer.
        """
        # Clear screen with black background
        self.screen.fill((0, 0, 0))
        
        # Render current state
        current_state = self.state_manager.peek()
        if current_state is not None:
            current_state.render(self.screen)
        
        # Render FPS counter if enabled
        if self.show_fps:
            self._render_fps()
        
        # Flip display
        pygame.display.flip()
    
    def _render_fps(self) -> None:
        """Render FPS counter to screen."""
        try:
            font = pygame.font.Font(None, 36)
            fps_value = self.clock.get_fps()
            # Handle mock objects in tests
            if isinstance(fps_value, (int, float)):
                fps_text = f"FPS: {int(fps_value)}"
            else:
                fps_text = "FPS: --"
            fps_surface = font.render(fps_text, True, (255, 255, 0))
            if fps_surface is not None:
                self.screen.blit(fps_surface, (10, 10))
        except (pygame.error, TypeError, ValueError):
            # Silently fail if font rendering fails or invalid FPS value
            pass
