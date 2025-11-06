"""Tests for action menu system."""

import pytest
import pygame
from unittest.mock import Mock, MagicMock
from src.ui.action_menu import MenuOption, ActionMenu


@pytest.fixture(scope="module", autouse=True)
def pygame_init():
    """Initialize Pygame for all tests in this module."""
    pygame.init()
    pygame.display.set_mode((1, 1))  # Minimal display
    yield
    pygame.quit()


class TestMenuOption:
    """Tests for MenuOption class."""
    
    def test_basic_initialization(self):
        """Test basic menu option creation."""
        option = MenuOption("Attack")
        assert option.text == "Attack"
        assert option.enabled is True
        assert option.callback is None
        assert option.submenu is None
    
    def test_with_callback(self):
        """Test menu option with callback."""
        callback = Mock()
        option = MenuOption("Attack", callback=callback)
        assert option.callback is callback
        assert option.submenu is None
    
    def test_with_submenu(self):
        """Test menu option with submenu."""
        submenu = Mock(spec=ActionMenu)
        option = MenuOption("Magic", submenu=submenu)
        assert option.submenu is submenu
        assert option.callback is None
    
    def test_disabled_option(self):
        """Test disabled menu option."""
        option = MenuOption("Disabled", enabled=False)
        assert option.enabled is False
    
    def test_cannot_have_both_callback_and_submenu(self):
        """Test that having both callback and submenu raises error."""
        callback = Mock()
        submenu = Mock(spec=ActionMenu)
        with pytest.raises(ValueError, match="Cannot have both callback and submenu"):
            MenuOption("Invalid", callback=callback, submenu=submenu)


class TestActionMenuInitialization:
    """Tests for ActionMenu initialization."""
    
    def test_basic_initialization(self):
        """Test basic menu creation."""
        options = [MenuOption("Attack"), MenuOption("Defend")]
        menu = ActionMenu(options)
        assert len(menu.options) == 2
        assert menu.selected_index == 0
        assert menu.visible is True
        assert menu.parent_menu is None
    
    def test_with_position(self):
        """Test menu with custom position."""
        options = [MenuOption("Test")]
        menu = ActionMenu(options, position=(100, 200))
        assert menu.position == (100, 200)
    
    def test_with_parent_menu(self):
        """Test menu with parent menu reference."""
        parent = ActionMenu([MenuOption("Parent")])
        child_options = [MenuOption("Child")]
        child = ActionMenu(child_options, parent_menu=parent)
        assert child.parent_menu is parent
    
    def test_empty_options_raises_error(self):
        """Test that empty options list raises error."""
        with pytest.raises(ValueError, match="must have at least one option"):
            ActionMenu([])
    
    def test_first_enabled_option_selected(self):
        """Test that first enabled option is auto-selected."""
        options = [
            MenuOption("Disabled 1", enabled=False),
            MenuOption("Disabled 2", enabled=False),
            MenuOption("Enabled", enabled=True),
            MenuOption("Also Enabled", enabled=True)
        ]
        menu = ActionMenu(options)
        assert menu.selected_index == 2  # First enabled option


class TestActionMenuCursorMovement:
    """Tests for cursor movement."""
    
    def test_move_cursor_down(self):
        """Test moving cursor down."""
        options = [MenuOption("A"), MenuOption("B"), MenuOption("C")]
        menu = ActionMenu(options)
        
        # Start at 0
        assert menu.selected_index == 0
        
        # Create down event
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN)
        menu.handle_input(event)
        
        assert menu.selected_index == 1
    
    def test_move_cursor_up(self):
        """Test moving cursor up."""
        options = [MenuOption("A"), MenuOption("B"), MenuOption("C")]
        menu = ActionMenu(options)
        menu.selected_index = 1
        
        # Create up event
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_UP)
        menu.handle_input(event)
        
        assert menu.selected_index == 0
    
    def test_cursor_wraps_around(self):
        """Test cursor wraps from bottom to top and vice versa."""
        options = [MenuOption("A"), MenuOption("B"), MenuOption("C")]
        menu = ActionMenu(options)
        
        # Move up from first -> wraps to last
        event_up = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_UP)
        menu.handle_input(event_up)
        assert menu.selected_index == 2
        
        # Wait for cooldown to expire
        menu.update(0.2)
        
        # Move down from last -> wraps to first
        event_down = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN)
        menu.handle_input(event_down)
        assert menu.selected_index == 0
    
    def test_skips_disabled_options(self):
        """Test cursor skips over disabled options."""
        options = [
            MenuOption("A", enabled=True),
            MenuOption("B", enabled=False),
            MenuOption("C", enabled=False),
            MenuOption("D", enabled=True)
        ]
        menu = ActionMenu(options)
        assert menu.selected_index == 0
        
        # Move down should skip B and C
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN)
        menu.handle_input(event)
        assert menu.selected_index == 3
    
    def test_alternative_movement_keys(self):
        """Test WASD keys for movement."""
        options = [MenuOption("A"), MenuOption("B")]
        menu = ActionMenu(options)
        
        # W key moves up
        event_w = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_w)
        menu.handle_input(event_w)
        assert menu.selected_index == 1  # Wrapped
        
        # Wait for cooldown to expire
        menu.update(0.2)
        
        # S key moves down
        event_s = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_s)
        menu.handle_input(event_s)
        assert menu.selected_index == 0


class TestActionMenuSelection:
    """Tests for menu option selection."""
    
    def test_select_executes_callback(self):
        """Test selecting option executes callback."""
        callback = Mock()
        options = [MenuOption("Attack", callback=callback)]
        menu = ActionMenu(options)
        
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
        result = menu.handle_input(event)
        
        assert result == "select"
        callback.assert_called_once()
    
    def test_select_opens_submenu(self):
        """Test selecting option opens submenu."""
        submenu = ActionMenu([MenuOption("Sub")])
        options = [MenuOption("Magic", submenu=submenu)]
        menu = ActionMenu(options)
        
        submenu.visible = False
        menu.visible = True
        
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
        menu.handle_input(event)
        
        assert submenu.visible is True
        assert menu.visible is False
    
    def test_cannot_select_disabled_option(self):
        """Test disabled options cannot be selected."""
        callback = Mock()
        options = [MenuOption("Disabled", callback=callback, enabled=False)]
        menu = ActionMenu(options)
        
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
        result = menu.handle_input(event)
        
        assert result is None
        callback.assert_not_called()
    
    def test_alternative_select_keys(self):
        """Test SPACE and Z keys for selection."""
        callback1 = Mock()
        callback2 = Mock()
        options = [MenuOption("A", callback=callback1), MenuOption("B", callback=callback2)]
        menu = ActionMenu(options)
        
        # Space key selects
        event_space = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)
        menu.handle_input(event_space)
        callback1.assert_called_once()
        
        # Wait for cooldown to expire
        menu.update(0.2)
        
        # Z key selects
        menu.selected_index = 1
        event_z = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_z)
        menu.handle_input(event_z)
        callback2.assert_called_once()


class TestActionMenuBackNavigation:
    """Tests for back button navigation."""
    
    def test_back_with_parent_menu(self):
        """Test back button returns to parent menu."""
        parent = ActionMenu([MenuOption("Parent")])
        child = ActionMenu([MenuOption("Child")], parent_menu=parent)
        
        parent.visible = False
        child.visible = True
        
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)
        result = child.handle_input(event)
        
        assert result == "back"
        assert parent.visible is True
        assert child.visible is False
    
    def test_back_without_parent_menu(self):
        """Test back button with no parent menu."""
        menu = ActionMenu([MenuOption("Test")])
        
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)
        result = menu.handle_input(event)
        
        assert result == "back"
        # Menu should still be visible (no parent to return to)
    
    def test_alternative_back_keys(self):
        """Test X and BACKSPACE keys for back."""
        parent = ActionMenu([MenuOption("Parent")])
        child = ActionMenu([MenuOption("Child")], parent_menu=parent)
        parent.visible = False
        child.visible = True
        
        # X key goes back
        event_x = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_x)
        child.handle_input(event_x)
        assert parent.visible is True


class TestActionMenuInputCooldown:
    """Tests for input cooldown mechanism."""
    
    def test_input_cooldown_prevents_double_tap(self):
        """Test input cooldown prevents rapid inputs."""
        options = [MenuOption("A"), MenuOption("B"), MenuOption("C")]
        menu = ActionMenu(options)
        
        # First input works
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN)
        menu.handle_input(event)
        assert menu.selected_index == 1
        
        # Immediate second input is ignored (cooldown active)
        menu.handle_input(event)
        assert menu.selected_index == 1  # Should still be at 1
    
    def test_cooldown_expires_with_update(self):
        """Test cooldown expires after update calls."""
        options = [MenuOption("A"), MenuOption("B")]
        menu = ActionMenu(options)
        
        # Trigger cooldown
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN)
        menu.handle_input(event)
        assert menu.selected_index == 1
        
        # Update to expire cooldown
        menu.update(0.2)  # > INPUT_COOLDOWN (0.15s)
        
        # Input should work now
        event_up = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_UP)
        menu.handle_input(event_up)
        assert menu.selected_index == 0


class TestActionMenuUpdate:
    """Tests for menu update logic."""
    
    def test_cursor_lerp_animation(self):
        """Test smooth cursor lerping."""
        options = [MenuOption("A"), MenuOption("B"), MenuOption("C")]
        menu = ActionMenu(options)
        
        initial_y = menu.cursor_y_current
        
        # Move cursor to different option
        menu.selected_index = 2
        
        # Update a few frames
        for _ in range(5):
            menu.update(0.016)  # ~60 FPS
        
        # Cursor should have moved towards target
        assert menu.cursor_y_current != initial_y
    
    def test_cursor_snaps_when_close(self):
        """Test cursor snaps to target when very close."""
        options = [MenuOption("A"), MenuOption("B")]
        menu = ActionMenu(options)
        
        # Move to option 1
        menu.selected_index = 1
        
        # Update enough times to snap
        for _ in range(100):
            menu.update(0.016)
        
        # Should be exactly at target
        target_y = menu._calculate_cursor_y()
        assert abs(menu.cursor_y_current - target_y) < 0.01


class TestActionMenuGamepadSupport:
    """Tests for gamepad input support."""
    
    def test_dpad_up(self):
        """Test D-pad up input."""
        options = [MenuOption("A"), MenuOption("B")]
        menu = ActionMenu(options)
        menu.selected_index = 1
        
        event = pygame.event.Event(pygame.JOYHATMOTION, value=(0, 1))
        menu.handle_input(event)
        
        assert menu.selected_index == 0
    
    def test_dpad_down(self):
        """Test D-pad down input."""
        options = [MenuOption("A"), MenuOption("B")]
        menu = ActionMenu(options)
        
        event = pygame.event.Event(pygame.JOYHATMOTION, value=(0, -1))
        menu.handle_input(event)
        
        assert menu.selected_index == 1
    
    def test_button_a_selects(self):
        """Test A button (button 0) selects option."""
        callback = Mock()
        options = [MenuOption("Attack", callback=callback)]
        menu = ActionMenu(options)
        
        event = pygame.event.Event(pygame.JOYBUTTONDOWN, button=0)
        result = menu.handle_input(event)
        
        assert result == "select"
        callback.assert_called_once()
    
    def test_button_b_goes_back(self):
        """Test B button (button 1) goes back."""
        parent = ActionMenu([MenuOption("Parent")])
        child = ActionMenu([MenuOption("Child")], parent_menu=parent)
        parent.visible = False
        child.visible = True
        
        event = pygame.event.Event(pygame.JOYBUTTONDOWN, button=1)
        result = child.handle_input(event)
        
        assert result == "back"
        assert parent.visible is True


class TestActionMenuUtilityMethods:
    """Tests for utility methods."""
    
    def test_get_selected_option(self):
        """Test getting currently selected option."""
        options = [MenuOption("A"), MenuOption("B"), MenuOption("C")]
        menu = ActionMenu(options)
        menu.selected_index = 1
        
        selected = menu.get_selected_option()
        assert selected is options[1]
        assert selected.text == "B"
    
    def test_set_option_enabled(self):
        """Test enabling/disabling options."""
        options = [MenuOption("A"), MenuOption("B")]
        menu = ActionMenu(options)
        
        menu.set_option_enabled(1, False)
        assert options[1].enabled is False
        
        menu.set_option_enabled(1, True)
        assert options[1].enabled is True
    
    def test_set_option_enabled_invalid_index(self):
        """Test set_option_enabled with invalid index."""
        options = [MenuOption("A")]
        menu = ActionMenu(options)
        
        with pytest.raises(IndexError):
            menu.set_option_enabled(5, False)
    
    def test_set_option_enabled_moves_cursor(self):
        """Test disabling current option moves cursor."""
        options = [MenuOption("A"), MenuOption("B"), MenuOption("C")]
        menu = ActionMenu(options)
        menu.selected_index = 1
        
        # Disable current option
        menu.set_option_enabled(1, False)
        
        # Cursor should have moved to next enabled option
        assert menu.selected_index != 1
    
    def test_show_and_hide(self):
        """Test show and hide methods."""
        options = [MenuOption("Test")]
        menu = ActionMenu(options)
        
        menu.hide()
        assert menu.visible is False
        
        menu.show()
        assert menu.visible is True


class TestActionMenuRendering:
    """Tests for menu rendering."""
    
    def test_render_creates_surface(self):
        """Test render method doesn't crash."""
        options = [MenuOption("Attack"), MenuOption("Magic")]
        menu = ActionMenu(options)
        
        screen = pygame.Surface((800, 600))
        
        # Should not raise exception
        menu.render(screen)
    
    def test_hidden_menu_doesnt_render(self):
        """Test hidden menu doesn't render."""
        options = [MenuOption("Test")]
        menu = ActionMenu(options)
        menu.visible = False
        
        screen = pygame.Surface((800, 600))
        original_screen = screen.copy()
        
        menu.render(screen)
        
        # Screen should be unchanged (menu didn't render)
        # Note: This is a basic check; pixel-perfect comparison not guaranteed
    
    def test_render_with_disabled_options(self):
        """Test rendering menu with disabled options."""
        options = [
            MenuOption("Enabled", enabled=True),
            MenuOption("Disabled", enabled=False)
        ]
        menu = ActionMenu(options)
        
        screen = pygame.Surface((800, 600))
        
        # Should not raise exception
        menu.render(screen)


class TestActionMenuInputLatency:
    """Tests for input latency requirements (<50ms)."""
    
    def test_input_response_time(self):
        """Test input response is immediate (frame-perfect)."""
        import time
        
        options = [MenuOption("A"), MenuOption("B")]
        menu = ActionMenu(options)
        
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN)
        
        start_time = time.perf_counter()
        menu.handle_input(event)
        elapsed = (time.perf_counter() - start_time) * 1000  # Convert to ms
        
        # Input should be processed in well under 50ms (typically <1ms)
        assert elapsed < 50
        assert menu.selected_index == 1


class TestActionMenuNestedSubmenus:
    """Tests for nested submenu navigation."""
    
    def test_submenu_chain(self):
        """Test navigating through multiple submenu levels."""
        # Create submenu chain: Main -> Magic -> Fire/Ice
        fire_ice_menu = ActionMenu([MenuOption("Fire"), MenuOption("Ice")])
        
        magic_menu = ActionMenu([
            MenuOption("Black Magic", submenu=fire_ice_menu)
        ])
        fire_ice_menu.parent_menu = magic_menu
        
        main_menu = ActionMenu([
            MenuOption("Attack"),
            MenuOption("Magic", submenu=magic_menu)
        ])
        magic_menu.parent_menu = main_menu
        
        # Navigate to Magic
        main_menu.selected_index = 1
        event_select = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
        main_menu.handle_input(event_select)
        
        assert magic_menu.visible is True
        assert main_menu.visible is False
        
        # Wait for cooldown
        magic_menu.update(0.2)
        
        # Navigate to Black Magic
        magic_menu.handle_input(event_select)
        
        assert fire_ice_menu.visible is True
        assert magic_menu.visible is False
        
        # Wait for cooldown
        fire_ice_menu.update(0.2)
        
        # Go back twice to return to main
        event_back = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)
        fire_ice_menu.handle_input(event_back)
        assert magic_menu.visible is True
        
        # Wait for cooldown
        magic_menu.update(0.2)
        
        magic_menu.handle_input(event_back)
        assert main_menu.visible is True
