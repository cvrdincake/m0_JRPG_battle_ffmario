# Enhanced Move System Documentation

## Overview

The enhanced move system provides comprehensive support for battle actions with different timing mechanics inspired by Mario & Luigi RPG series. Each move can have unique targeting options and timing-based action commands.

## Core Components

### TargetType Enum

Defines who can be targeted by a move:

- **SINGLE_ENEMY**: Target one enemy
- **ALL_ENEMIES**: Target all enemies (AOE)
- **SINGLE_ALLY**: Target one ally
- **ALL_ALLIES**: Target all allies (group buff/heal)
- **SELF**: Target only the user

### TimingType Enum

Defines the type of action command:

- **SIMPLE**: No timing required, always 1.0x damage
- **TIMED_PRESS**: Single button press at the right moment
- **SEQUENCE**: Multiple button presses in rhythm (e.g., A, B, A, B)
- **HOLD_RELEASE**: Hold button and release at peak moment

### TimingWindow Dataclass

Defines millisecond thresholds for timing evaluation:

```python
TimingWindow(
    perfect_min=450, perfect_max=550,  # Perfect window (100ms)
    good_min=350, good_max=650,        # Good window (300ms)
    early_min=200, early_max=800       # Early window (600ms)
)
```

Evaluation returns:
- **"perfect"**: 2.0x damage multiplier
- **"good"**: 1.5x damage multiplier
- **"early"**: 1.2x damage multiplier
- **"miss"**: 1.0x damage (no bonus)

### ActionCommand Dataclass

Combines timing type with optional configuration:

```python
ActionCommand(
    timing_type=TimingType.TIMED_PRESS,
    timing_window=window,           # Optional
    sequence_buttons=['A', 'B'],    # For SEQUENCE type
    hold_duration_ms=1500           # For HOLD_RELEASE type
)
```

### BattleMove Class

Enhanced move with full timing support:

```python
move = BattleMove({
    'id': 'jump',
    'name': 'Jump',
    'description': 'Jump on enemy',
    'base_power': 30,
    'mp_cost': 0,
    'target_type': 'single_enemy',
    'timing_type': 'timed_press',
    'timing_window': {...}
})
```

## Timing Type Details

### 1. SIMPLE Timing

No timing required. Always succeeds at base damage.

**Use cases:**
- Basic attacks
- Defensive moves
- Simple spells

**Example:**
```json
{
  "timing_type": "simple"
}
```

### 2. TIMED_PRESS

Single button press at the right moment. Visual indicator moves across screen, player presses when it hits target zone.

**Difficulty:** Medium  
**Perfect window:** 100ms (450-550ms)  
**Good window:** 300ms (350-650ms)

**Use cases:**
- Jump attacks
- Hammer strikes
- Ranged shots

**Example:**
```json
{
  "timing_type": "timed_press",
  "timing_window": {
    "perfect_min": 450, "perfect_max": 550,
    "good_min": 350, "good_max": 650,
    "early_min": 200, "early_max": 800
  }
}
```

### 3. SEQUENCE

Multiple button presses in rhythm. Each press must be timed correctly.

**Difficulty:** Hard  
**Perfect window:** 50ms (475-525ms)  
**Good window:** 200ms (400-600ms)

**Use cases:**
- Combo attacks
- Special techniques
- Rhythm-based moves

**Example:**
```json
{
  "timing_type": "sequence",
  "sequence_buttons": ["A", "B", "A", "B"],
  "timing_window": {
    "perfect_min": 475, "perfect_max": 525,
    "good_min": 400, "good_max": 600,
    "early_min": 300, "early_max": 700
  }
}
```

### 4. HOLD_RELEASE

Hold button to charge, release at peak moment for maximum damage.

**Difficulty:** Very Hard  
**Perfect window:** 40ms (480-520ms)  
**Good window:** 160ms (420-580ms)

**Use cases:**
- Charged attacks
- Power moves
- Focus abilities

**Example:**
```json
{
  "timing_type": "hold_release",
  "hold_duration_ms": 1500,
  "timing_window": {
    "perfect_min": 480, "perfect_max": 520,
    "good_min": 420, "good_max": 580,
    "early_min": 350, "early_max": 650
  }
}
```

## Damage Calculation

The system uses deterministic damage formulas:

```python
# Base damage (attack vs defense ratio)
denominator = attacker_attack + defender_defense
attack_ratio = attacker_attack / denominator
base_damage = move.base_power * attack_ratio

# Apply timing multiplier
final_damage = base_damage * timing_multiplier

# Ensure minimum 1 damage
final_damage = max(1, int(final_damage))
```

### Timing Multipliers:
- Perfect: 2.0x
- Good: 1.5x
- Early: 1.2x
- Miss: 1.0x

## Example Moves

### Basic Attack (SIMPLE)
```json
{
  "id": "punch",
  "name": "Punch",
  "description": "A basic punch attack",
  "base_power": 20,
  "mp_cost": 0,
  "target_type": "single_enemy",
  "timing_type": "simple",
  "is_offensive": true
}
```

### Timed Attack (TIMED_PRESS)
```json
{
  "id": "jump",
  "name": "Jump",
  "description": "Jump on enemy with timing",
  "base_power": 30,
  "mp_cost": 0,
  "target_type": "single_enemy",
  "timing_type": "timed_press",
  "timing_window": {...}
}
```

### Combo Attack (SEQUENCE)
```json
{
  "id": "hammer_combo",
  "name": "Hammer Combo",
  "description": "Multiple hammer strikes in rhythm",
  "base_power": 45,
  "mp_cost": 5,
  "target_type": "single_enemy",
  "timing_type": "sequence",
  "sequence_buttons": ["A", "B", "A", "B"]
}
```

### AOE Spell
```json
{
  "id": "quake",
  "name": "Quake",
  "description": "Earth attack hitting all enemies",
  "base_power": 35,
  "mp_cost": 15,
  "target_type": "all_enemies",
  "timing_type": "simple"
}
```

### Healing Spell
```json
{
  "id": "heal",
  "name": "Heal",
  "description": "Restore HP to an ally",
  "base_power": 30,
  "mp_cost": 8,
  "target_type": "single_ally",
  "timing_type": "simple",
  "is_offensive": false
}
```

## Testing

Comprehensive test coverage includes:

- **Enum Tests**: All timing and target types defined
- **TimingWindow Tests**: Evaluation logic for all ratings
- **ActionCommand Tests**: Input requirements and multipliers
- **BattleMove Tests**: Initialization, validation, damage calculation
- **Integration Tests**: Complete move execution flow

Run tests:
```bash
python -m pytest tests/test_battle_move.py -v
```

## Integration with Battle System

The enhanced move system integrates with:

1. **Stats System**: Uses deterministic damage formulas
2. **Battle System**: Handles move execution and timing
3. **UI System**: Displays timing indicators and windows
4. **AI System**: Enemies select moves based on type and target

## Design Principles

1. **Immutability**: Move definitions are immutable after creation
2. **Deterministic**: Same inputs always produce same outputs
3. **Testable**: All components have comprehensive unit tests
4. **Extensible**: Easy to add new timing types or target patterns
5. **Data-Driven**: Moves defined in JSON for easy modding

## Future Enhancements

Potential additions:
- Status effect moves (poison, sleep, etc.)
- Multi-hit moves with independent timing per hit
- Counter moves that trigger on enemy attacks
- Cooperative moves requiring multiple party members
- Dynamic difficulty adjustment based on player performance
