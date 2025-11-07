# Game Loop Architecture

## Overview

The `Game` class implements the core game loop with a **fixed timestep accumulator pattern** for consistent game logic updates independent of rendering frame rate. It integrates with the `StateManager` for stack-based state management.

## Key Features

### 1. Fixed Timestep Accumulator Pattern

Prevents physics/game logic inconsistencies by using a fixed time step for updates:

```python
# In Game.update() method
self.dt_accumulator += dt
while self.dt_accumulator >= self.fixed_dt:
    # Update game logic with fixed_dt (1/60 second)
    current_state.update(self.fixed_dt)
    self.dt_accumulator -= self.fixed_dt
```

**Benefits:**
- Deterministic game behavior regardless of frame rate
- No "spiral of death" with slow frames (dt is capped at 0.25s)
- Consistent physics calculations
- Smooth interpolation possible

### 2. StateManager Integration

Uses stack-based state management pattern:

- **Push**: Add state to stack, pause previous state
- **Pop**: Remove top state, resume previous state  
- **Change**: Replace top state
- **Peek**: Get current state without modifying stack

**Example Usage:**
```python
# Battle starts
battle_state = BattleState(screen, party, enemy_group)
state_manager.push(battle_state)

# Pause menu over battle
pause_menu = PauseMenuState()
state_manager.push(pause_menu)  # Battle paused automatically

# Resume battle
state_manager.pop()  # Battle resumed automatically
```

### 3. Frame Rate Management

```python
# Proper frame limiting with Pygame Clock
self.clock = pygame.time.Clock()

# In game loop
dt = self.clock.tick(self.fps) / 1000.0  # Convert ms to seconds
```

**Frame Rate Behavior:**
- Rendering: Variable rate up to target FPS (default: 60)
- Game Logic: Fixed rate at 60 updates/second
- Decoupled: Rendering and logic run independently

## Architecture

### Initialization

```
Game.__init__()
├── pygame.init()
├── Load settings.json (FileNotFoundError if missing)
├── Create display surface
├── Create Pygame clock
├── Initialize StateManager
└── Create initial BattleState
```

### Game Loop

```
Game.run()
while running:
    ├── dt = clock.tick(fps) / 1000.0
    ├── handle_events()
    │   ├── Process QUIT/ESC → running = False
    │   └── Delegate to current_state.handle_event()
    ├── update(dt)
    │   ├── dt_accumulator += dt
    │   ├── while dt_accumulator >= fixed_dt:
    │   │   ├── current_state.update(fixed_dt)
    │   │   └── dt_accumulator -= fixed_dt
    │   └── Check if state_manager.is_empty() → exit
    └── render()
        ├── screen.fill(black)
        ├── current_state.render(screen)
        ├── Render FPS counter (if enabled)
        └── pygame.display.flip()
```

## Implementation Details

### Delta Time Capping

Prevents "spiral of death" where updates take longer than real time:

```python
if dt > 0.25:
    dt = 0.25  # Cap at 250ms (4 FPS minimum)
```

### Fixed Timestep Constants

```python
FIXED_TIMESTEP = 1.0 / 60.0  # 60 updates per second
```

Why 60 Hz?
- Standard for game logic
- Matches common monitor refresh rates
- Good balance between responsiveness and performance

### State Lifecycle

Current state receives all events and updates:

```python
# Events
current_state.handle_event(event)

# Fixed timestep updates
current_state.update(fixed_dt)

# Variable rate rendering
current_state.render(screen)
```

## Error Handling

**Configuration Loading:**
- `FileNotFoundError`: If settings.json doesn't exist
- `ValueError`: If settings.json has invalid JSON

**Pygame Initialization:**
- `pygame.error`: If display creation fails
- `pygame.error`: If Pygame initialization fails

**State Management:**
- Game exits gracefully when state stack is empty
- `print()` statements for debugging state transitions

## Testing

The Game class has comprehensive unit tests covering:

1. **Initialization**
   - Config loading
   - Display creation
   - Clock creation
   - StateManager integration

2. **Game Loop**
   - Fixed timestep accumulation
   - Delta time capping
   - State stack empty handling

3. **Event Handling**
   - QUIT event
   - ESC key
   - Event delegation to states

4. **Rendering**
   - Screen clearing
   - State delegation
   - FPS counter display

5. **StateManager Integration**
   - Update with fixed_dt
   - Empty stack handling
   - State lifecycle

## Performance Characteristics

**Target Performance:**
- 60 FPS rendering
- 60 updates/second (fixed)
- < 16.67ms frame time for smooth gameplay

**Actual Performance:**
- Variable rendering up to target FPS
- Consistent game logic timing
- Graceful degradation on slow hardware (capped dt)

## Configuration

**settings.json structure:**
```json
{
  "display": {
    "width": 1280,
    "height": 720,
    "fps": 60,
    "title": "JRPG Battle Prototype"
  },
  "debug": {
    "show_fps": true,
    "show_hitboxes": false,
    "god_mode": false
  },
  "paths": {
    "sprites": "assets/sprites",
    "animations": "assets/animations",
    "data": "assets/data"
  }
}
```

## Best Practices

1. **Always use fixed_dt for game logic**
   - Character movement
   - Physics calculations
   - ATB gauge updates
   
2. **Use dt for visual effects only**
   - Particle systems
   - Smooth interpolation
   - Non-critical animations

3. **Handle state transitions carefully**
   - Push for overlays (pause, menus)
   - Pop to return to previous state
   - Change for full screen transitions

4. **Test with variable frame rates**
   - Verify fixed timestep behavior
   - Check dt capping
   - Ensure no frame-dependent logic

## Future Enhancements

1. **State transition effects** (fade in/out)
2. **Save state support** (serialize state stack)
3. **Performance profiling** (track update/render times)
4. **Audio system integration**
5. **Resource management** (preload assets per state)
6. **Debug overlay** (show dt_accumulator, update count)
