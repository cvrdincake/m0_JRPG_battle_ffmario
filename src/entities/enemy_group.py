"""Enemy group management system for battles.

This module manages groups of enemy characters including positioning
for battle rendering and group management.
"""

from typing import List, Optional, Iterator, Tuple
from src.entities.character import Enemy


# Constants for enemy positioning
ENEMY_X_MIN = 800
ENEMY_X_MAX = 1000
ENEMY_Y_CENTER = 360  # Half of 720 (screen height)
MIN_VERTICAL_SPACING = 100
MAX_ENEMY_GROUP_SIZE = 6


class EnemyGroup:
    """Manages group of enemy characters.
    
    The enemy group is positioned on the right side of the battle screen with
    enemies arranged vertically with proper spacing.
    
    Attributes:
        enemies: List of enemy characters (max 6).
        max_size: Maximum group size (6).
    """
    
    MAX_SIZE = MAX_ENEMY_GROUP_SIZE
    
    def __init__(self) -> None:
        """Initialize empty enemy group."""
        self.enemies: List[Enemy] = []
    
    def add_enemy(self, enemy: Enemy) -> bool:
        """Add enemy to group.
        
        Args:
            enemy: Enemy character to add.
        
        Returns:
            True if added successfully, False if group full.
        
        Raises:
            TypeError: If enemy is not an Enemy instance.
        """
        if not isinstance(enemy, Enemy):
            raise TypeError(f"EnemyGroup can only contain Enemy instances, got {type(enemy)}")
        
        if len(self.enemies) >= self.MAX_SIZE:
            return False
        
        self.enemies.append(enemy)
        return True
    
    def remove_enemy(self, enemy: Enemy) -> bool:
        """Remove enemy from group.
        
        Args:
            enemy: Enemy character to remove.
        
        Returns:
            True if removed successfully, False if not in group.
        """
        if enemy in self.enemies:
            self.enemies.remove(enemy)
            return True
        return False
    
    def get_enemy_by_id(self, enemy_id: str) -> Optional[Enemy]:
        """Get enemy by ID.
        
        Args:
            enemy_id: Enemy ID to search for.
        
        Returns:
            Enemy if found, None otherwise.
        """
        for enemy in self.enemies:
            if enemy.id == enemy_id:
                return enemy
        return None
    
    def get_alive_enemies(self) -> List[Enemy]:
        """Get all enemies with HP > 0.
        
        Returns:
            List of alive enemy characters.
        """
        return [enemy for enemy in self.enemies if enemy.is_alive]
    
    def all_dead(self) -> bool:
        """Check if entire enemy group is defeated.
        
        Returns:
            True if all enemies have 0 HP, False otherwise.
        """
        if not self.enemies:
            return True
        return len(self.get_alive_enemies()) == 0
    
    def is_full(self) -> bool:
        """Check if group is at maximum size.
        
        Returns:
            True if group has MAX_SIZE enemies.
        """
        return len(self.enemies) >= self.MAX_SIZE
    
    def size(self) -> int:
        """Get current group size.
        
        Returns:
            Number of enemies in group.
        """
        return len(self.enemies)
    
    def clear(self) -> None:
        """Remove all enemies from group."""
        self.enemies.clear()
    
    def get_positions(self) -> List[Tuple[int, int]]:
        """Calculate screen positions for all enemies.
        
        Positions are calculated on the right side of the screen with
        vertical centering and proper spacing between enemies.
        
        Enemy positioning:
        - X: 800-1000 (right side)
        - Y: Centered vertically with MIN_VERTICAL_SPACING between enemies
        
        Returns:
            List of (x, y) tuples for each enemy's position.
        """
        if not self.enemies:
            return []
        
        positions = []
        num_enemies = len(self.enemies)
        
        # Calculate total height needed
        total_height = (num_enemies - 1) * MIN_VERTICAL_SPACING
        
        # Calculate starting Y position (centered)
        start_y = ENEMY_Y_CENTER - (total_height // 2)
        
        # Calculate X position (center of enemy range)
        x_pos = (ENEMY_X_MIN + ENEMY_X_MAX) // 2
        
        # Generate positions
        for i in range(num_enemies):
            y_pos = start_y + (i * MIN_VERTICAL_SPACING)
            positions.append((x_pos, y_pos))
        
        return positions
    
    def get_enemy_position(self, enemy: Enemy) -> Optional[Tuple[int, int]]:
        """Get screen position for a specific enemy.
        
        Args:
            enemy: Enemy to get position for.
        
        Returns:
            (x, y) tuple if enemy in group, None otherwise.
        """
        try:
            index = self.enemies.index(enemy)
            positions = self.get_positions()
            return positions[index]
        except (ValueError, IndexError):
            return None
    
    def get_random_alive_enemy(self) -> Optional[Enemy]:
        """Get a random alive enemy for AI targeting.
        
        Returns:
            Random alive enemy, or None if all dead.
        """
        alive = self.get_alive_enemies()
        if not alive:
            return None
        
        # Simple selection: return first alive enemy
        # Can be enhanced with random selection later
        return alive[0]
    
    def __iter__(self) -> Iterator[Enemy]:
        """Iterate over enemies.
        
        Returns:
            Iterator over enemy characters.
        """
        return iter(self.enemies)
    
    def __len__(self) -> int:
        """Get group size.
        
        Returns:
            Number of enemies in group.
        """
        return len(self.enemies)
    
    def __contains__(self, enemy: Enemy) -> bool:
        """Check if enemy is in group.
        
        Args:
            enemy: Enemy to check.
        
        Returns:
            True if enemy in group.
        """
        return enemy in self.enemies
    
    def __getitem__(self, index: int) -> Enemy:
        """Get enemy by index.
        
        Args:
            index: Index of enemy to get.
        
        Returns:
            Enemy at given index.
        
        Raises:
            IndexError: If index out of range.
        """
        return self.enemies[index]
