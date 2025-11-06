# Animation System Documentation

## Overview

The animation system provides frame-based sprite animations with delta time support for the JRPG battle prototype. It enables smooth, frame-rate independent animations for battle effects, character sprites, and UI elements.

## Architecture

### Core Components

1. **AnimationFrame**: Single frame of animation with surface and duration
2. **Animation**: Complete animation sequence with frame advancement logic
3. **AnimationController**: Manages multiple simultaneous animations

### Key Features

- **Frame-rate independence**: All timing uses delta time (dt) parameter
- **Looping/Non-looping**: Animations can repeat or play once
- **Memory efficiency**: Multiple animations can share same frame data
- **Composable effects**: Run multiple animations simultaneously (flash + shake)
- **No visual pops**: Smooth transitions between animation states
- **Pause/Resume**: Full control over animation playback

## Usage Examples

### Creating a Simple Animation

```python
from src.utils.animation import AnimationFrame, Animation
import pygame

# Create frames
frames = [
    AnimationFrame(surface1, duration=0.1),  # 100ms per frame
    AnimationFrame(surface2, duration=0.1),
    AnimationFrame(surface3, duration=0.1),
]

# Create looping animation
anim = Animation(frames, loop=True)

# Update in game loop
def update(dt):
    anim.update(dt)
    current_surface = anim.get_current_frame()
    screen.blit(current_surface, position)
```

### Non-Looping Animation with Callback

```python
def on_explosion_complete():
    print("Explosion finished!")

explosion_anim = Animation(
    explosion_frames,
    loop=False,
    on_complete=on_explosion_complete
)

# Animation will call callback when it reaches the end
explosion_anim.update(dt)

# Check if finished
if explosion_anim.is_finished():
    # Animation is holding on last frame
    pass
```

### Managing Multiple Animations

```python
from src.utils.animation import AnimationController

controller = AnimationController()

# Add multiple effects
controller.add_animation("flash", flash_animation)
controller.add_animation("shake", shake_animation)
controller.add_animation("particles", particle_animation)

# Update all at once
def update(dt):
    controller.update(dt)
    
    # Get specific animation if needed
    flash_anim = controller.get_animation("flash")
    if flash_anim:
        surface = flash_anim.get_current_frame()

# Controller automatically removes finished non-looping animations
```

### Memory-Efficient Animation Sharing

```python
# Create shared frame data once
shared_frames = [
    AnimationFrame(explosion_surface1, 0.05),
    AnimationFrame(explosion_surface2, 0.05),
    AnimationFrame(explosion_surface3, 0.05),
]

# Create multiple animation instances sharing same frames
explosion1 = Animation(shared_frames, loop=False)
explosion2 = Animation(shared_frames, loop=False)
explosion3 = Animation(shared_frames, loop=False)

# Each animation maintains its own state but shares frame data
# This saves memory when you need many instances of the same animation
```

### Pause and Resume

```python
# Pause animation (e.g., when battle menu opens)
animation.pause()

# Resume when returning to battle
animation.resume()

# Reset to beginning if needed
animation.reset()
```

## Integration with Battle System

### Character Hit Animation

```python
class Character:
    def __init__(self):
        self.hit_frames = [
            AnimationFrame(self.sprite, 0.05),  # Normal
            AnimationFrame(white_flash_sprite, 0.05),  # Flash
            AnimationFrame(self.sprite, 0.05),  # Normal
        ]
        self.hit_animation = None
    
    def take_damage(self, amount):
        self.current_hp -= amount
        
        # Start hit animation
        self.hit_animation = Animation(
            self.hit_frames,
            loop=False,
            on_complete=self._hit_animation_complete
        )
    
    def _hit_animation_complete(self):
        self.hit_animation = None
    
    def update(self, dt):
        if self.hit_animation:
            self.hit_animation.update(dt)
    
    def render(self, screen, position):
        if self.hit_animation:
            surface = self.hit_animation.get_current_frame()
        else:
            surface = self.sprite
        screen.blit(surface, position)
```

### Attack Animation Sequence

```python
def execute_attack(attacker, target):
    # Create attack animation
    attack_anim = Animation(attack_frames, loop=False)
    
    # Track animation progress
    def check_damage_timing():
        progress = attack_anim.get_progress()
        if progress >= 0.5 and not damage_dealt:
            # Deal damage at 50% animation progress
            target.take_damage(calculate_damage())
    
    controller.add_animation("attack", attack_anim)
```

## Performance Characteristics

### Memory Usage

- **Frame Data**: Shared between animation instances (~10KB per unique animation)
- **Animation Instance**: ~200 bytes per instance
- **Controller Overhead**: ~50 bytes + dict overhead

### CPU Usage

- **Update Cost**: O(1) per animation per frame
- **Frame Advancement**: Amortized O(1) (usually 0-1 frames per update)
- **Controller Update**: O(n) where n = number of active animations

### Frame Timing Precision

- **Delta Time Resolution**: Microsecond precision (float seconds)
- **Frame Duration**: Minimum 0.001s (1ms) recommended
- **Typical Durations**: 0.05s - 0.2s per frame (50-200ms)

## Design Patterns

### State Machine Integration

```python
class BattleState:
    def __init__(self):
        self.anim_controller = AnimationController()
    
    def _transition_to_executing_action(self):
        # Start action animation
        anim = Animation(action_frames, loop=False, 
                        on_complete=self._action_complete)
        self.anim_controller.add_animation("action", anim)
    
    def _action_complete(self):
        # Animation finished, transition to next phase
        self._transition_to_check_victory()
    
    def update(self, dt):
        self.anim_controller.update(dt)
```

### Composing Multiple Effects

```python
def apply_critical_hit_effects(character):
    controller = AnimationController()
    
    # Flash effect (fast loop)
    flash_anim = Animation(flash_frames, loop=True)
    controller.add_animation("flash", flash_anim)
    
    # Shake effect (offset position)
    shake_anim = Animation(shake_frames, loop=False)
    controller.add_animation("shake", shake_anim)
    
    # Particles (one-shot)
    particle_anim = Animation(particle_frames, loop=False)
    controller.add_animation("particles", particle_anim)
    
    return controller
```

## Best Practices

### DO ✅

- Use delta time for frame-rate independence
- Share frame data between animation instances
- Use non-looping animations for one-shot effects
- Set meaningful callbacks for animation completion
- Reset animations before reusing them
- Use AnimationController for complex sequences

### DON'T ❌

- Don't create new frames for each animation instance (memory waste)
- Don't use extremely short durations (<1ms, timing precision limits)
- Don't modify frames while animation is playing (undefined behavior)
- Don't forget to update animations every frame
- Don't nest AnimationControllers (unnecessary complexity)

## Common Patterns

### Variable Speed Animation

```python
# Speed up animation by scaling time
fast_dt = dt * 2.0  # 2x speed
animation.update(fast_dt)

# Slow down animation
slow_dt = dt * 0.5  # 0.5x speed
animation.update(slow_dt)
```

### Synchronized Animations

```python
# Start multiple animations at same time
anim1 = Animation(frames1, loop=False)
anim2 = Animation(frames2, loop=False)

controller.add_animation("anim1", anim1)
controller.add_animation("anim2", anim2)

# They will stay synchronized as long as update is called consistently
```

### Animation Chaining

```python
def play_sequence():
    anim1 = Animation(frames1, loop=False, on_complete=play_anim2)
    controller.add_animation("seq1", anim1)

def play_anim2():
    anim2 = Animation(frames2, loop=False, on_complete=play_anim3)
    controller.add_animation("seq2", anim2)

def play_anim3():
    anim3 = Animation(frames3, loop=False)
    controller.add_animation("seq3", anim3)
```

## Troubleshooting

### Animation Not Playing

- Check that `update(dt)` is being called every frame
- Verify dt is not zero or negative
- Ensure animation is not paused
- Check that animation frames list is not empty

### Animation Too Fast/Slow

- Adjust frame durations (not dt scaling)
- Typical range: 0.05s - 0.2s per frame
- Verify dt is in seconds, not milliseconds

### Memory Growing Over Time

- Check for animation leaks (not removed when finished)
- Verify AnimationController auto-removes finished animations
- Ensure frame data is shared, not duplicated

### Visual Pops Between Frames

- This should not happen with proper delta time
- Check that frame durations are positive
- Verify update is called consistently

## Technical Details

### Frame Advancement Algorithm

```python
# Simplified algorithm
time_in_frame += dt
while time_in_frame >= current_frame.duration:
    time_in_frame -= current_frame.duration
    current_frame_index += 1
    
    if current_frame_index >= len(frames):
        if loop:
            current_frame_index = 0
        else:
            current_frame_index = len(frames) - 1
            finished = True
```

### Progress Calculation

```python
total_duration = sum(frame.duration for frame in frames)
elapsed = sum(frames[i].duration for i in range(current_index))
elapsed += time_in_frame
progress = elapsed / total_duration  # 0.0 to 1.0
```

## Related Systems

- **Battle System**: Uses animations for attack/damage effects
- **UI System**: Uses animations for menu transitions
- **Particle System**: Could be built on top of animation system
- **State Management**: Animations can trigger state transitions

## Future Enhancements

Potential additions (not currently implemented):

- Animation blending/crossfade
- Sprite sheet support
- Animation speed curves (ease-in/out)
- Frame event triggers
- Animation layers with priority
- Procedural animation generation
