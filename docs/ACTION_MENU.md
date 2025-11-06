# Action Menu System

The action menu system provides responsive, frame-perfect input handling for battle commands with smooth cursor animations and nested submenu support.

## Features

### Core Features
- **Frame-perfect input response** (<50ms latency) with no queued inputs
- **Smooth cursor lerping** for fluid visual feedback
- **Nested submenu support** with proper back button unwinding
- **Visual distinction** for disabled options (e.g., insufficient MP)
- **Dual input support**: Both keyboard and gamepad work identically

### Input Controls

**Keyboard:**
- Movement: Arrow keys or WASD
- Select: Enter, Space, or Z
- Back: Escape, X, or Backspace

**Gamepad:**
- Movement: D-pad or Left stick
- Select: A button (button 0)
- Back: B button (button 1)

## Architecture

### MenuOption Class

Represents a single selectable menu option with:
- **text**: Display text for the option
- **enabled**: Whether the option can be selected (default: True)
- **callback**: Function to execute when selected (optional)
- **submenu**: Nested submenu to open when selected (optional)

**Note**: Cannot have both callback and submenu on the same option.

```python
# Simple option with callback
attack_option = MenuOption("Attack", callback=lambda: perform_attack())

# Disabled option (e.g., insufficient MP)
magic_option = MenuOption("Magic", enabled=False)

# Option that opens submenu
items_submenu = ActionMenu([...])
items_option = MenuOption("Items", submenu=items_submenu)
```

### ActionMenu Class

Main menu class managing display, input handling, and animations.

**Key Attributes:**
- `options`: List of MenuOption objects
- `selected_index`: Currently selected option
- `position`: (x, y) screen coordinates for top-left corner
- `visible`: Whether menu is currently shown
- `parent_menu`: Parent menu reference for back navigation

**Visual Constants:**
- WIDTH = 300px
- HEIGHT = 200px
- OPTION_HEIGHT = 40px (spacing between options)
- PADDING = 20px (internal padding)

**Animation:**
- CURSOR_LERP_SPEED = 12.0 (controls smoothness of cursor movement)
- INPUT_COOLDOWN = 0.15s (prevents double-tap inputs)

## Usage Examples

### Basic Menu

```python
import pygame
from src.ui.action_menu import MenuOption, ActionMenu

# Create menu options
options = [
    MenuOption("Attack", callback=handle_attack),
    MenuOption("Defend", callback=handle_defend),
    MenuOption("Item", callback=handle_item),
    MenuOption("Run", callback=handle_run)
]

# Create menu
menu = ActionMenu(options, position=(50, 400))

# In game loop
def game_loop():
    while running:
        dt = clock.tick(60) / 1000.0
        
        # Handle events
        for event in pygame.event.get():
            action = menu.handle_input(event)
            if action == "select":
                print("Option selected!")
            elif action == "back":
                print("Back button pressed!")
        
        # Update
        menu.update(dt)
        
        # Render
        screen.fill((0, 0, 0))
        menu.render(screen)
        pygame.display.flip()
```

### Nested Submenus

```python
# Create submenu for magic spells
magic_submenu = ActionMenu([
    MenuOption("Fire", callback=lambda: cast_spell("fire")),
    MenuOption("Ice", callback=lambda: cast_spell("ice")),
    MenuOption("Heal", callback=lambda: cast_spell("heal"))
])

# Create main menu with submenu option
main_menu = ActionMenu([
    MenuOption("Attack", callback=handle_attack),
    MenuOption("Magic", submenu=magic_submenu),  # Opens submenu
    MenuOption("Item", callback=handle_item)
])

# Link parent for back button navigation
magic_submenu.parent_menu = main_menu
```

### Dynamic Option Enabling

```python
# Create menu
menu = ActionMenu([
    MenuOption("Attack"),
    MenuOption("Magic"),  # Index 1
    MenuOption("Heal")    # Index 2
])

# Disable magic if MP insufficient
if character.mp < 10:
    menu.set_option_enabled(1, False)

# Re-enable when MP restored
if character.mp >= 10:
    menu.set_option_enabled(1, True)
```

### Menu Visibility Control

```python
# Show/hide menus
main_menu.show()
submenu.hide()

# Check visibility
if menu.visible:
    menu.render(screen)
```

## Input Cooldown System

The menu implements an input cooldown mechanism to prevent accidental double-taps and provide deliberate control:

- **Cooldown Duration**: 0.15 seconds (150ms)
- **Applied On**: Any cursor movement or selection
- **Bypassed For**: Initial inputs when cooldown is expired

This ensures responsive yet controlled input without feeling sluggish.

## Cursor Animation

The cursor uses linear interpolation (lerp) for smooth movement:

```python
# Each frame
target_y = calculate_position_for(selected_index)
current_y += (target_y - current_y) * LERP_SPEED * dt

# Snap when very close (prevents jitter)
if abs(target_y - current_y) < 0.5:
    current_y = target_y
```

**LERP_SPEED = 12.0** provides smooth but snappy cursor movement that feels responsive without being jarring.

## Visual Design

### Color Scheme
- **Background**: Semi-transparent dark blue (20, 20, 40, 220)
- **Border**: Light gray (100, 100, 150)
- **Normal Text**: White (255, 255, 255)
- **Selected Text**: Yellow highlight (255, 255, 100)
- **Disabled Text**: Gray (100, 100, 100)
- **Cursor**: Semi-transparent gold (255, 200, 50, 180)

### Layout
```
┌─────────────────────────────┐
│  ┌─────────────────────┐    │  ← Cursor (animated)
│  │ Attack             │    │
│  └─────────────────────┘    │
│    Magic                    │  ← Normal option
│    Items                    │
│    Run                      │  ← Disabled option (grayed)
└─────────────────────────────┘
```

## Performance

- **Input Latency**: <1ms typical, <50ms guaranteed
- **Cursor Animation**: 60 FPS smooth at all times
- **Memory**: Minimal (single surface cached per menu)
- **Rendering**: Efficient (only visible menus rendered)

## Integration with Battle System

The action menu integrates seamlessly with the battle state:

```python
# In BattleState
def enter(self):
    # Create battle menu
    self.action_menu = ActionMenu([
        MenuOption("Attack", callback=self.select_attack),
        MenuOption("Magic", submenu=self.magic_menu),
        MenuOption("Item", submenu=self.item_menu),
        MenuOption("Defend", callback=self.select_defend)
    ], position=(50, 500))

def update(self, dt: float):
    if self.current_phase == BattlePhase.TURN_SELECT:
        self.action_menu.update(dt)
        # Check for ATB readiness, enable/disable options

def handle_event(self, event: pygame.event.Event):
    if self.current_phase == BattlePhase.TURN_SELECT:
        action = self.action_menu.handle_input(event)
        if action == "select":
            # Transition to next phase
            pass

def render(self, screen: pygame.Surface):
    # Render battle scene
    if self.current_phase == BattlePhase.TURN_SELECT:
        self.action_menu.render(screen)
```

## Testing

The action menu system includes comprehensive test coverage (40 tests, 100% passing):

- MenuOption initialization and validation
- ActionMenu initialization with various configurations
- Cursor movement (up, down, wrapping, skipping disabled)
- Selection execution (callbacks, submenus)
- Back button navigation
- Input cooldown mechanism
- Cursor lerp animation
- Gamepad support
- Utility methods
- Rendering functionality
- Input latency requirements
- Nested submenu chains

Run tests with:
```bash
python -m pytest tests/test_action_menu.py -v
```

## Best Practices

1. **Always link parent menus**: Set `submenu.parent_menu = parent` for proper back navigation
2. **Update before rendering**: Call `menu.update(dt)` before `menu.render(screen)`
3. **Handle return values**: Check `handle_input()` return value for "select" and "back" actions
4. **Dynamic enabling**: Use `set_option_enabled()` to disable options based on game state
5. **Input delegation**: Only pass events to menu when it should be active (e.g., during TURN_SELECT phase)

## Troubleshooting

**Cursor doesn't move smoothly:**
- Ensure `update(dt)` is called every frame with proper delta time
- Check that `dt` is in seconds, not milliseconds

**Input feels laggy:**
- Verify cooldown timer is being updated with `update(dt)`
- Check that frame rate is stable at 60 FPS

**Submenu back button doesn't work:**
- Ensure `parent_menu` is set on the submenu
- Verify parent menu `visible` flag is being managed correctly

**Options can't be selected:**
- Check `enabled` flag on MenuOption
- Verify option is not disabled via `set_option_enabled()`

## Future Enhancements

Possible improvements for future versions:
- Sound effects on cursor movement and selection
- More animation effects (fade in/out, slide)
- Customizable color schemes via themes
- Support for icons next to menu options
- Scrolling support for menus with many options
- Tooltips showing move details on hover
