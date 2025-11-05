"""Party management system for playable characters.

This module manages the party of playable characters including positioning
for battle rendering and member management.
"""

from typing import List, Optional, Iterator, Tuple
from src.entities.character import Hero


# Constants for party positioning
PARTY_X_MIN = 300
PARTY_X_MAX = 400
PARTY_Y_CENTER = 360  # Half of 720 (screen height)
MIN_VERTICAL_SPACING = 100
MAX_PARTY_SIZE = 4


class Party:
    """Manages party of playable characters.
    
    The party is positioned on the left side of the battle screen with
    members arranged vertically with proper spacing.
    
    Attributes:
        members: List of hero characters (max 4).
        max_size: Maximum party size (4).
    """
    
    MAX_SIZE = MAX_PARTY_SIZE
    
    def __init__(self) -> None:
        """Initialize empty party."""
        self.members: List[Hero] = []
    
    def add_member(self, character: Hero) -> bool:
        """Add character to party.
        
        Args:
            character: Hero character to add.
        
        Returns:
            True if added successfully, False if party full.
        
        Raises:
            TypeError: If character is not a Hero instance.
        """
        if not isinstance(character, Hero):
            raise TypeError(f"Party can only contain Hero instances, got {type(character)}")
        
        if len(self.members) >= self.MAX_SIZE:
            return False
        
        self.members.append(character)
        return True
    
    def remove_member(self, character: Hero) -> bool:
        """Remove character from party.
        
        Args:
            character: Hero character to remove.
        
        Returns:
            True if removed successfully, False if not in party.
        """
        if character in self.members:
            self.members.remove(character)
            return True
        return False
    
    def get_member_by_id(self, character_id: str) -> Optional[Hero]:
        """Get party member by ID.
        
        Args:
            character_id: Character ID to search for.
        
        Returns:
            Hero if found, None otherwise.
        """
        for member in self.members:
            if member.id == character_id:
                return member
        return None
    
    def get_alive_members(self) -> List[Hero]:
        """Get all party members with HP > 0.
        
        Returns:
            List of alive hero characters.
        """
        return [char for char in self.members if char.is_alive]
    
    def all_dead(self) -> bool:
        """Check if entire party is defeated.
        
        Returns:
            True if all members have 0 HP, False otherwise.
        """
        if not self.members:
            return True
        return len(self.get_alive_members()) == 0
    
    def is_full(self) -> bool:
        """Check if party is at maximum size.
        
        Returns:
            True if party has MAX_SIZE members.
        """
        return len(self.members) >= self.MAX_SIZE
    
    def size(self) -> int:
        """Get current party size.
        
        Returns:
            Number of members in party.
        """
        return len(self.members)
    
    def clear(self) -> None:
        """Remove all members from party."""
        self.members.clear()
    
    def get_positions(self) -> List[Tuple[int, int]]:
        """Calculate screen positions for all party members.
        
        Positions are calculated on the left side of the screen with
        vertical centering and proper spacing between members.
        
        Party positioning:
        - X: 300-400 (left side)
        - Y: Centered vertically with MIN_VERTICAL_SPACING between members
        
        Returns:
            List of (x, y) tuples for each member's position.
        """
        if not self.members:
            return []
        
        positions = []
        num_members = len(self.members)
        
        # Calculate total height needed
        total_height = (num_members - 1) * MIN_VERTICAL_SPACING
        
        # Calculate starting Y position (centered)
        start_y = PARTY_Y_CENTER - (total_height // 2)
        
        # Calculate X position (center of party range)
        x_pos = (PARTY_X_MIN + PARTY_X_MAX) // 2
        
        # Generate positions
        for i in range(num_members):
            y_pos = start_y + (i * MIN_VERTICAL_SPACING)
            positions.append((x_pos, y_pos))
        
        return positions
    
    def get_member_position(self, character: Hero) -> Optional[Tuple[int, int]]:
        """Get screen position for a specific party member.
        
        Args:
            character: Hero to get position for.
        
        Returns:
            (x, y) tuple if member in party, None otherwise.
        """
        try:
            index = self.members.index(character)
            positions = self.get_positions()
            return positions[index]
        except (ValueError, IndexError):
            return None
    
    def __iter__(self) -> Iterator[Hero]:
        """Iterate over party members.
        
        Returns:
            Iterator over hero members.
        """
        return iter(self.members)
    
    def __len__(self) -> int:
        """Get party size.
        
        Returns:
            Number of members in party.
        """
        return len(self.members)
    
    def __contains__(self, character: Hero) -> bool:
        """Check if character is in party.
        
        Args:
            character: Hero to check.
        
        Returns:
            True if character in party.
        """
        return character in self.members
    
    def __getitem__(self, index: int) -> Hero:
        """Get party member by index.
        
        Args:
            index: Index of member to get.
        
        Returns:
            Hero at given index.
        
        Raises:
            IndexError: If index out of range.
        """
        return self.members[index]
