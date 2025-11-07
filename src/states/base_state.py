"""Base state class for game state management.

This module provides the abstract base class for all game states,
defining the interface that all states must implement.
"""

from abc import ABC, abstractmethod
import pygame


class State(ABC):
    """Abstract base class for game states.
    
    States represent different screens or modes in the game (menu, battle, etc.).
    Each state must implement lifecycle methods and update/render logic.
    """
    
    @abstractmethod
    def enter(self) -> None:
        """Called when the state is entered (becomes active).
        
        Use this to initialize state-specific resources.
        """
        pass
    
    @abstractmethod
    def exit(self) -> None:
        """Called when the state is exited (removed from stack).
        
        Use this to clean up state-specific resources.
        """
        pass
    
    @abstractmethod
    def pause(self) -> None:
        """Called when the state is paused (another state pushed on top).
        
        Use this to pause animations, sounds, or other active processes.
        """
        pass
    
    @abstractmethod
    def resume(self) -> None:
        """Called when the state is resumed (state above was popped).
        
        Use this to resume animations, sounds, or other processes.
        """
        pass
    
    @abstractmethod
    def update(self, dt: float) -> None:
        """Update the state logic.
        
        Args:
            dt: Delta time in seconds since last update.
        """
        pass
    
    @abstractmethod
    def render(self, screen: pygame.Surface) -> None:
        """Render the state to the screen.
        
        Args:
            screen: Pygame surface to render to.
        """
        pass
    
    @abstractmethod
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle a pygame event.
        
        Args:
            event: Pygame event to handle.
        """
        pass
