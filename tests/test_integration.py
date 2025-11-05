"""Integration test to verify the complete battle system works."""

import os
import sys

from src.entities.character import Hero, Enemy
from src.entities.move import Move
from src.battle.battle_system import BattleSystem, BattleState
from src.battle.timing import TimingResult
from src.utils.data_loader import load_characters, load_enemies, load_moves


def test_complete_battle_flow():
    """Integration test for complete battle flow."""
    print("Starting integration test...")
    
    # Load data
    print("Loading data files...")
    heroes_data = load_characters("assets/data/characters.json")
    enemies_data = load_enemies("assets/data/enemies.json")
    moves_data = load_moves("assets/data/moves.json")
    
    assert len(heroes_data) >= 2, "Should have at least 2 heroes"
    assert len(enemies_data) >= 1, "Should have at least 1 enemy"
    assert len(moves_data) >= 2, "Should have at least 2 moves"
    print(f"✓ Loaded {len(heroes_data)} heroes, {len(enemies_data)} enemies, {len(moves_data)} moves")
    
    # Create characters
    print("\nCreating characters...")
    heroes = [Hero(heroes_data[0])]
    enemies = [Enemy(enemies_data[0])]
    print(f"✓ Created hero '{heroes[0].name}' and enemy '{enemies[0].name}'")
    
    # Create moves
    print("\nCreating moves...")
    moves = [Move(data) for data in moves_data[:3]]
    print(f"✓ Created {len(moves)} moves")
    
    # Initialize battle
    print("\nInitializing battle system...")
    battle = BattleSystem(heroes, enemies)
    assert battle.state == BattleState.ACTIVE
    print(f"✓ Battle system initialized in {battle.state.value} state")
    
    # Simulate ATB filling
    print("\nSimulating ATB fill...")
    dt = 1.0
    for i in range(15):
        battle.update(dt)
        if battle.state == BattleState.PLAYER_TURN:
            print(f"✓ Hero ATB filled after {i+1} updates")
            break
    
    assert battle.state == BattleState.PLAYER_TURN, "Should be player turn after ATB fills"
    assert battle.active_character == heroes[0], "Active character should be the hero"
    print(f"✓ {battle.active_character.name}'s turn (ATB: {battle.active_character.atb_value})")
    
    # Select and execute a move
    print("\nExecuting move...")
    move = moves[0]  # First move
    target = enemies[0]
    
    initial_hp = target.current_hp
    success = battle.select_move_and_target(move, target)
    assert success, "Move selection should succeed"
    print(f"✓ Selected move '{move.name}' targeting '{target.name}'")
    
    # If timing is required, execute it
    if battle.state == BattleState.TIMING_COMMAND:
        print("✓ Timing window activated")
        result = battle.execute_timing_input()
        print(f"✓ Timing result: {result.value}")
    
    # Wait for animation to complete
    battle.update(1.0)
    
    # Check if enemy was defeated
    if target.current_hp <= 0:
        print(f"✓ Enemy defeated! ({target.current_hp}/{target.stats.max_hp} HP)")
        damage_dealt = initial_hp
    else:
        # Verify damage was dealt
        assert target.current_hp < initial_hp, "Target should have taken damage"
        damage_dealt = initial_hp - target.current_hp
        print(f"✓ Dealt {damage_dealt} damage ({target.current_hp}/{target.stats.max_hp} HP remaining)")
        
        # Verify turn completed
        assert battle.state == BattleState.ACTIVE or battle.state == BattleState.VICTORY, "Should return to active state or victory"
        assert battle.active_character is None, "Active character should be cleared"
        print(f"✓ Turn completed, returned to {battle.state.value} state")
    
    # Test battle end condition (if not already ended)
    print("\nTesting battle end condition...")
    if battle.state != BattleState.VICTORY:
        enemies[0].current_hp = 0
        enemies[0].is_alive = False
        battle._check_battle_end()
    assert battle.state == BattleState.VICTORY, "Battle should end in victory"
    print(f"✓ Battle ended in {battle.state.value}")
    
    # Get rewards
    exp, gold = battle.get_battle_rewards()
    assert exp > 0, "Should receive EXP reward"
    assert gold > 0, "Should receive gold reward"
    print(f"✓ Rewards: {exp} EXP, {gold} Gold")
    
    print("\n" + "="*50)
    print("✓ All integration tests passed!")
    print("="*50)


if __name__ == "__main__":
    try:
        test_complete_battle_flow()
        sys.exit(0)
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error during test: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
