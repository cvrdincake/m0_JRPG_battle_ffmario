"""Battle phase enumeration.

This module defines the phases of battle using a state machine pattern.
Each phase represents a distinct stage in the battle flow.
"""

from enum import Enum, auto


class BattlePhase(Enum):
    """Battle state machine phases.
    
    The battle progresses through these phases in a controlled manner:
    - BATTLE_START: Initial setup and fade-in (2 seconds)
    - TURN_SELECT: Player selecting action (waits for input)
    - EXECUTING_ACTION: Animation and damage calculation
    - ENEMY_TURN: AI turn execution
    - CHECK_VICTORY: Check win/loss conditions (instant)
    - VICTORY: Player won (show results)
    - DEFEAT: Player lost (show results)
    """
    
    BATTLE_START = auto()      # Initial fade-in and setup
    TURN_SELECT = auto()       # Player selecting action
    EXECUTING_ACTION = auto()  # Animation and damage calculation
    ENEMY_TURN = auto()        # AI turn execution
    CHECK_VICTORY = auto()     # Check win/loss conditions
    VICTORY = auto()           # Player won
    DEFEAT = auto()            # Player lost
