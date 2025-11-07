"""State manager for handling game state transitions.

This module provides a stack-based state manager that handles pushing,
popping, and transitioning between game states.
"""

from typing import List, Optional
import pygame
from src.states.base_state import State


class StateManager:
    """Manages a stack of game states.
    
    The state manager maintains a stack of states where only the top state
    is actively updating and rendering. When a new state is pushed, the
    previous state is paused. When a state is popped, the previous state
    is resumed.
    
    Attributes:
        states: Stack of active states (last element is current).
    """
    
    def __init__(self) -> None:
        """Initialize the state manager with an empty stack."""
        self.states: List[State] = []
    
    def push(self, state: State) -> None:
        """Push a new state onto the stack.
        
        Pauses the current state (if any) and enters the new state.
        
        Args:
            state: State to push onto the stack.
            
        Raises:
            ValueError: If state is None.
        """
        if state is None:
            raise ValueError("Cannot push None state")
        
        # Pause current state if exists
        if self.states:
            self.states[-1].pause()
        
        # Add and enter new state
        self.states.append(state)
        state.enter()
    
    def pop(self) -> Optional[State]:
        """Pop the current state from the stack.
        
        Exits the current state and resumes the previous state (if any).
        
        Returns:
            The popped state, or None if stack was empty.
        """
        if not self.states:
            return None
        
        # Pop and exit current state
        state = self.states.pop()
        state.exit()
        
        # Resume previous state if exists
        if self.states:
            self.states[-1].resume()
        
        return state
    
    def change(self, state: State) -> None:
        """Replace the current state with a new state.
        
        Pops the current state and pushes the new state.
        
        Args:
            state: State to change to.
            
        Raises:
            ValueError: If state is None.
        """
        if state is None:
            raise ValueError("Cannot change to None state")
        
        # Pop current state without resuming previous
        if self.states:
            old_state = self.states.pop()
            old_state.exit()
        
        # Push new state
        self.states.append(state)
        state.enter()
    
    def current(self) -> Optional[State]:
        """Get the current active state.
        
        Returns:
            The current state, or None if stack is empty.
        """
        return self.states[-1] if self.states else None
    
    def update(self, dt: float) -> None:
        """Update the current state.
        
        Args:
            dt: Delta time in seconds since last update.
        """
        if self.states:
            self.states[-1].update(dt)
    
    def render(self, screen: pygame.Surface) -> None:
        """Render the current state.
        
        Args:
            screen: Pygame surface to render to.
        """
        if self.states:
            self.states[-1].render(screen)
    
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle an event with the current state.
        
        Args:
            event: Pygame event to handle.
        """
        if self.states:
            self.states[-1].handle_event(event)
    
    def is_empty(self) -> bool:
        """Check if the state stack is empty.
        
        Returns:
            True if no states are active.
        """
        return len(self.states) == 0
    
    def clear(self) -> None:
        """Clear all states from the stack.
        
        Exits all states in reverse order.
        """
        while self.states:
            self.pop()
