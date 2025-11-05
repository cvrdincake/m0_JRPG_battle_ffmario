# Party and Enemy Group Positioning System

## Overview

The Party and EnemyGroup classes manage collections of characters and calculate their screen positions for battle rendering.

## Screen Layout (1280x720)

```
                    Screen: 1280x720
┌────────────────────────────────────────────────────────┐
│                                                        │
│   PARTY (Left)              ENEMY GROUP (Right)       │
│   X: 300-400                X: 800-1000               │
│                                                        │
│                                                        │
│     ◉ Hero 1                      Enemy 1 ◉           │
│     (350, 210)                    (900, 110)          │
│        ↓ 100px spacing              ↓ 100px           │
│     ◉ Hero 2                      Enemy 2 ◉           │
│     (350, 310)                    (900, 210)          │
│        ↓ 100px spacing              ↓ 100px           │
│     ◉ Hero 3                      Enemy 3 ◉           │
│     (350, 410)                    (900, 310)          │
│        ↓ 100px spacing              ↓ 100px           │
│     ◉ Hero 4                      Enemy 4 ◉           │
│     (350, 510)                    (900, 410)          │
│                                     ↓ 100px           │
│                                   Enemy 5 ◉           │
│                                   (900, 510)          │
│                                     ↓ 100px           │
│                                   Enemy 6 ◉           │
│                                   (900, 610)          │
│                                                        │
└────────────────────────────────────────────────────────┘

Center Y: 360 (half of 720)
```

## Party Class

**Purpose**: Manages up to 4 playable hero characters

**Position Calculation**:
- X Position: Center of range 300-400 = **350**
- Y Position: Vertically centered with 100px spacing
- For N members: Start at `360 - ((N-1) * 100) / 2`

**Example Positions**:
- 1 member: (350, 360)
- 2 members: (350, 310), (350, 410)
- 3 members: (350, 260), (350, 360), (350, 460)
- 4 members: (350, 210), (350, 310), (350, 410), (350, 510)

**Key Features**:
- Type enforcement: Only `Hero` instances allowed
- Maximum size: 4 members
- Methods: `add_member()`, `remove_member()`, `get_alive_members()`, `all_dead()`
- Position methods: `get_positions()`, `get_member_position()`
- Collection operations: Iteration, indexing, containment checks

## EnemyGroup Class

**Purpose**: Manages up to 6 enemy characters

**Position Calculation**:
- X Position: Center of range 800-1000 = **900**
- Y Position: Vertically centered with 100px spacing
- For N enemies: Start at `360 - ((N-1) * 100) / 2`

**Example Positions**:
- 1 enemy: (900, 360)
- 2 enemies: (900, 310), (900, 410)
- 3 enemies: (900, 260), (900, 360), (900, 460)
- 6 enemies: (900, 110), (900, 210), (900, 310), (900, 410), (900, 510), (900, 610)

**Key Features**:
- Type enforcement: Only `Enemy` instances allowed
- Maximum size: 6 enemies
- Methods: `add_enemy()`, `remove_enemy()`, `get_alive_enemies()`, `all_dead()`
- Position methods: `get_positions()`, `get_enemy_position()`
- AI helper: `get_random_alive_enemy()` for targeting
- Collection operations: Iteration, indexing, containment checks

## Position Calculation Details

### Vertical Centering Algorithm

```python
def get_positions():
    num_entities = len(members)
    
    # Calculate total height needed
    total_height = (num_entities - 1) * MIN_VERTICAL_SPACING  # 100px between each
    
    # Start Y position (centered around 360)
    start_y = 360 - (total_height // 2)
    
    # Generate positions
    positions = []
    for i in range(num_entities):
        y_pos = start_y + (i * MIN_VERTICAL_SPACING)
        positions.append((x_center, y_pos))
    
    return positions
```

### No Overlap Guarantee

With 100px minimum vertical spacing:
- Maximum party height: 3 * 100 = 300px (4 members)
- Maximum enemy height: 5 * 100 = 500px (6 enemies)
- Both fit comfortably in 720px screen height

### Horizontal Separation

- Party X center: 350
- Enemy X center: 900
- Separation: 550px (plenty of space for sprites and effects)

## Usage Examples

### Creating a Party

```python
from src.entities.party import Party
from src.entities.character import Hero

party = Party()

# Add heroes
hero_data = {
    'id': 'mario',
    'name': 'Mario',
    'max_hp': 100,
    'max_mp': 50,
    'attack': 20,
    'defense': 15,
    'speed': 18,
    'atb_speed': 12
}
hero = Hero(hero_data)
party.add_member(hero)

# Get positions for rendering
positions = party.get_positions()
for hero, (x, y) in zip(party, positions):
    render_sprite(hero.sprite, x, y)
```

### Creating an Enemy Group

```python
from src.entities.enemy_group import EnemyGroup
from src.entities.character import Enemy

group = EnemyGroup()

# Add enemies
enemy_data = {
    'id': 'goomba1',
    'name': 'Goomba',
    'max_hp': 30,
    'attack': 8,
    'defense': 5,
    'speed': 10,
    'atb_speed': 8,
    'exp_reward': 10,
    'gold_reward': 5
}
enemy = Enemy(enemy_data)
group.add_enemy(enemy)

# Get positions for rendering
positions = group.get_positions()
for enemy, (x, y) in zip(group, positions):
    render_sprite(enemy.sprite, x, y)
```

### Battle Victory/Defeat Check

```python
# Check battle end conditions
if party.all_dead():
    print("Game Over!")
elif enemy_group.all_dead():
    print("Victory!")
    exp, gold = calculate_rewards(enemy_group)
```

## Testing Coverage

The implementation includes 28 comprehensive tests covering:

1. **Initialization**: Empty collections
2. **Adding/Removing**: Member management with size limits
3. **Type Safety**: TypeError for wrong entity types
4. **Position Calculation**: Correct spacing and centering
5. **Status Checks**: Alive/dead status tracking
6. **Collection Operations**: Iteration, indexing, containment
7. **Edge Cases**: Empty groups, full groups, single members

All tests pass with 100% coverage of core functionality.

## Design Principles

1. **Type Safety**: Enforces Hero-only for Party, Enemy-only for EnemyGroup
2. **Immutable Positions**: Positions calculated on-demand, not stored
3. **Balanced Layout**: Both sides use same spacing logic for visual consistency
4. **Flexible Size**: Supports 1-4 party members, 1-6 enemies
5. **No Overlap**: Guaranteed minimum 100px spacing prevents overlapping sprites
6. **Centered Arrangement**: Groups are vertically centered around screen middle
7. **Iterator Support**: Standard Python collection protocols (iter, len, contains, getitem)
