"""Unit tests for state manager."""

import pytest
from src.states.state_manager import StateManager
from src.states.base_state import State


class DummyState(State):
    """Dummy state for testing state manager functionality."""
    
    def __init__(self) -> None:
        """Initialize dummy state with tracking flags."""
        self.entered = False
        self.exited = False
        self.paused = False
        self.resumed = False
    
    def enter(self) -> None:
        """Mark state as entered."""
        self.entered = True
    
    def exit(self) -> None:
        """Mark state as exited."""
        self.exited = True
    
    def pause(self) -> None:
        """Mark state as paused."""
        self.paused = True
    
    def resume(self) -> None:
        """Mark state as resumed."""
        self.resumed = True
    
    def update(self, dt: float) -> None:
        """Update (no-op for testing)."""
        pass
    
    def render(self, screen) -> None:
        """Render (no-op for testing)."""
        pass
    
    def handle_event(self, event) -> None:
        """Handle event (no-op for testing)."""
        pass


def test_push_calls_enter():
    """Test that pushing a state calls its enter method."""
    manager = StateManager()
    state = DummyState()
    manager.push(state)
    assert state.entered is True


def test_pop_calls_exit():
    """Test that popping a state calls its exit method."""
    manager = StateManager()
    state = DummyState()
    manager.push(state)
    manager.pop()
    assert state.exited is True


def test_push_pauses_previous():
    """Test that pushing a new state pauses the previous state."""
    manager = StateManager()
    state1 = DummyState()
    state2 = DummyState()
    manager.push(state1)
    manager.push(state2)
    assert state1.paused is True


def test_pop_resumes_previous():
    """Test that popping a state resumes the previous state."""
    manager = StateManager()
    state1 = DummyState()
    state2 = DummyState()
    manager.push(state1)
    manager.push(state2)
    manager.pop()
    assert state1.resumed is True


def test_current_returns_top_state():
    """Test that current returns the top state."""
    manager = StateManager()
    state1 = DummyState()
    state2 = DummyState()
    manager.push(state1)
    assert manager.current() == state1
    manager.push(state2)
    assert manager.current() == state2


def test_current_returns_none_when_empty():
    """Test that current returns None when stack is empty."""
    manager = StateManager()
    assert manager.current() is None


def test_is_empty():
    """Test is_empty method."""
    manager = StateManager()
    assert manager.is_empty() is True
    state = DummyState()
    manager.push(state)
    assert manager.is_empty() is False
    manager.pop()
    assert manager.is_empty() is True


def test_change_state():
    """Test changing state pops current and pushes new."""
    manager = StateManager()
    state1 = DummyState()
    state2 = DummyState()
    manager.push(state1)
    manager.change(state2)
    assert state1.exited is True
    assert state2.entered is True
    assert manager.current() == state2


def test_clear_all_states():
    """Test clearing all states."""
    manager = StateManager()
    state1 = DummyState()
    state2 = DummyState()
    manager.push(state1)
    manager.push(state2)
    manager.clear()
    assert state1.exited is True
    assert state2.exited is True
    assert manager.is_empty() is True


def test_push_none_raises_error():
    """Test that pushing None raises ValueError."""
    manager = StateManager()
    with pytest.raises(ValueError, match="Cannot push None state"):
        manager.push(None)


def test_change_none_raises_error():
    """Test that changing to None raises ValueError."""
    manager = StateManager()
    with pytest.raises(ValueError, match="Cannot change to None state"):
        manager.change(None)


def test_pop_empty_returns_none():
    """Test that popping empty stack returns None."""
    manager = StateManager()
    assert manager.pop() is None


def test_update_calls_current_state():
    """Test that update is called on current state."""
    manager = StateManager()
    
    class TrackingState(DummyState):
        def __init__(self):
            super().__init__()
            self.update_called = False
            self.update_dt = None
        
        def update(self, dt: float) -> None:
            self.update_called = True
            self.update_dt = dt
    
    state = TrackingState()
    manager.push(state)
    manager.update(0.016)
    assert state.update_called is True
    assert state.update_dt == 0.016


def test_render_calls_current_state():
    """Test that render is called on current state."""
    manager = StateManager()
    
    class TrackingState(DummyState):
        def __init__(self):
            super().__init__()
            self.render_called = False
        
        def render(self, screen) -> None:
            self.render_called = True
    
    state = TrackingState()
    manager.push(state)
    manager.render(None)
    assert state.render_called is True


def test_handle_event_calls_current_state():
    """Test that handle_event is called on current state."""
    manager = StateManager()
    
    class TrackingState(DummyState):
        def __init__(self):
            super().__init__()
            self.event_handled = False
        
        def handle_event(self, event) -> None:
            self.event_handled = True
    
    state = TrackingState()
    manager.push(state)
    manager.handle_event(None)
    assert state.event_handled is True
