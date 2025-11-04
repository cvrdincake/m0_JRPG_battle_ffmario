"""Main game class that manages the game loop and states.

This module provides the core Game class that initializes Pygame,
manages the game loop, and handles state transitions.
"""

import sys
import os
import pygame
from typing import Optional, Dict, Any
from src.utils.data_loader import load_config, DataLoadError


# Constants
DEFAULT_FPS = 60
DEFAULT_WIDTH = 1280
DEFAULT_HEIGHT = 720
DEFAULT_TITLE = "JRPG Battle Prototype"


class Game:
    """Main game class managing the game loop and rendering.
    
    Attributes:
        config: Game configuration loaded from settings.json.
        screen: Pygame display surface.
        clock: Pygame clock for frame timing.
        running: Whether the game is running.
        fps: Target frames per second.
        dt: Delta time for frame-rate independent updates.
    """
    
    def __init__(self) -> None:
        """Initialize the game and Pygame.
        
        Raises:
            RuntimeError: If Pygame initialization fails.
            DataLoadError: If configuration loading fails.
        """
        # Initialize Pygame
        pygame.init()
        
        if not pygame.display.get_init():
            raise RuntimeError("Failed to initialize Pygame display")
        
        # Load configuration
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'settings.json')
        config_path = os.path.abspath(config_path)
        
        try:
            self.config: Dict[str, Any] = load_config(config_path)
        except DataLoadError as e:
            print(f"Warning: Could not load config file: {e}")
            print("Using default settings")
            self.config = self._get_default_config()
        
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
                raise RuntimeError("pygame.display.set_mode returned None")
            pygame.display.set_caption(title)
        except pygame.error as e:
            raise RuntimeError(f"Failed to create display: {e}")
        
        # Initialize clock
        self.clock: pygame.time.Clock = pygame.time.Clock()
        self.running: bool = False
        self.dt: float = 0.0
        
        # Debug settings
        debug_config = self.config.get('debug', {})
        self.show_fps: bool = debug_config.get('show_fps', True)
        
        # Ensure required directories exist
        self._ensure_directories()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration.
        
        Returns:
            Default configuration dictionary.
        """
        return {
            'display': {
                'width': DEFAULT_WIDTH,
                'height': DEFAULT_HEIGHT,
                'fps': DEFAULT_FPS,
                'title': DEFAULT_TITLE
            },
            'debug': {
                'show_fps': True,
                'show_hitboxes': False,
                'god_mode': False
            },
            'paths': {
                'sprites': 'assets/sprites',
                'animations': 'assets/animations',
                'data': 'assets/data'
            }
        }
    
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
        """Main game loop."""
        self.running = True
        
        print(f"Starting game at {self.config['display']['width']}x{self.config['display']['height']}")
        print(f"Target FPS: {self.fps}")
        print("Press ESC or close window to exit")
        
        while self.running:
            # Calculate delta time (in seconds)
            self.dt = self.clock.tick(self.fps) / 1000.0
            
            # Handle events
            self._handle_events()
            
            # Update game state
            self._update(self.dt)
            
            # Render
            self._render()
        
        print("Game ended")
    
    def _handle_events(self) -> None:
        """Handle Pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
    
    def _update(self, dt: float) -> None:
        """Update game state.
        
        Args:
            dt: Delta time in seconds since last update.
        """
        # Game state updates will go here
        pass
    
    def _render(self) -> None:
        """Render the game."""
        # Clear screen with black background
        self.screen.fill((0, 0, 0))
        
        # Render FPS counter if enabled
        if self.show_fps:
            self._render_fps()
        
        # Flip display
        pygame.display.flip()
    
    def _render_fps(self) -> None:
        """Render FPS counter to screen."""
        try:
            font = pygame.font.Font(None, 36)
            fps_text = f"FPS: {int(self.clock.get_fps())}"
            fps_surface = font.render(fps_text, True, (255, 255, 255))
            if fps_surface is not None:
                self.screen.blit(fps_surface, (10, 10))
        except pygame.error as e:
            # Silently fail if font rendering fails
            pass
