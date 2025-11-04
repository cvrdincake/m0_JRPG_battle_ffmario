# JRPG Battle Prototype

A functional turn-based JRPG battle system combining Final Fantasy-style Active Time Battle (ATB) mechanics with Mario & Luigi timing-based action commands.

## Features

- **ATB System**: Characters' turn gauges fill in real-time based on their speed stats
- **Timing-Based Action Commands**: Press buttons at the right moment for bonus damage (Mario & Luigi style)
- **Complete Battle System**: Hero vs Enemy combat with HP, MP, Attack, Defense stats
- **Multiple Move Types**: Physical attacks, magic spells, and defend actions
- **JSON Data-Driven**: All characters, enemies, and moves are defined in JSON files
- **Full UI**: Health bars, MP bars, ATB gauges, timing indicators, and battle messages

## Technology Stack

- Python 3.12.3 (requires 3.10+)
- Pygame 2.5.2
- Pytest 7.4.3 for unit testing
- JSON for data storage

## Installation

1. Clone the repository:
```bash
git clone https://github.com/cvrdincake/m0_JRPG_battle_ffmario.git
cd m0_JRPG_battle_ffmario
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Game

```bash
python main.py
```

## Controls

- **Arrow Keys**: Navigate menus (Up/Down for moves, Left/Right for targets)
- **SPACE or ENTER**: Confirm selection / Execute timing input
- **ESC**: Exit game

## Project Structure

```
jrpg_battle/
├── main.py                 # Entry point
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── config/
│   └── settings.json      # Game configuration
├── src/
│   ├── game.py            # Main game loop
│   ├── states/
│   │   └── battle_state.py    # Battle scene management
│   ├── entities/
│   │   ├── character.py       # Character, Hero, Enemy classes
│   │   └── move.py           # Move/skill system
│   ├── ui/
│   │   └── battle_ui.py      # UI components (bars, panels, indicators)
│   ├── battle/
│   │   ├── battle_system.py  # Battle flow and turn management
│   │   └── timing.py         # Timing-based action command system
│   └── utils/
│       └── data_loader.py    # JSON data loading utilities
├── assets/
│   └── data/
│       ├── characters.json   # Hero data
│       ├── enemies.json      # Enemy data
│       └── moves.json        # Move/skill data
└── tests/                 # Unit tests
    ├── test_character.py
    ├── test_move.py
    ├── test_timing.py
    └── test_data_loader.py
```

## Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test file
pytest tests/test_character.py -v
```

## How It Works

### ATB System
Each character has an ATB gauge that fills based on their `atb_speed` stat. When the gauge reaches 100, the character can take their turn. This creates dynamic, real-time turn order rather than traditional turn-based systems.

### Timing System
When executing certain moves, a timing indicator appears with a moving marker and an optimal timing zone. Players must press SPACE at the right moment:
- **Perfect**: Hit within 0.05s of optimal time → Full bonus damage
- **Good**: Hit within 0.15s of optimal time → 75% bonus damage  
- **Normal**: Hit within the window → 25% bonus damage
- **Miss**: Hit outside the window → No bonus

### Battle Flow
1. ATB gauges fill for all characters
2. When a character's ATB is full, they can act
3. Player selects move and target
4. If move requires timing, timing window appears
5. Move executes with calculated damage
6. Battle continues until all heroes or enemies are defeated

## Configuration

Edit `config/settings.json` to customize:
- Display resolution and FPS
- Debug options (FPS counter, hitboxes)
- Asset paths

## Data Files

### Characters (`assets/data/characters.json`)
Define heroes with stats: HP, MP, Attack, Defense, Speed, ATB Speed

### Enemies (`assets/data/enemies.json`)
Define enemies with stats and rewards (EXP, Gold)

### Moves (`assets/data/moves.json`)
Define skills with power, MP cost, timing windows, and bonuses

## License

MIT License - See repository for details

## Contributors

- Game developed by cvrdincake
- Built with Python and Pygame