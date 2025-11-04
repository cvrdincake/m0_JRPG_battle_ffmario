"""Data loader utility for JSON game data files.

This module provides functions to load and parse game data from JSON files,
including characters, enemies, and moves.
"""

import json
import os
from typing import Dict, List, Any


class DataLoadError(Exception):
    """Exception raised when data loading fails."""
    pass


def load_json_file(filepath: str) -> Dict[str, Any]:
    """Load and parse a JSON file.
    
    Args:
        filepath: Path to the JSON file to load.
        
    Returns:
        Parsed JSON data as a dictionary.
        
    Raises:
        DataLoadError: If file doesn't exist or JSON is invalid.
    """
    if not os.path.exists(filepath):
        raise DataLoadError(f"Data file not found: {filepath}")
    
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            return json.load(file)
    except json.JSONDecodeError as e:
        raise DataLoadError(f"Invalid JSON in {filepath}: {e}")
    except IOError as e:
        raise DataLoadError(f"Error reading file {filepath}: {e}")


def load_characters(filepath: str) -> List[Dict[str, Any]]:
    """Load character data from JSON file.
    
    Args:
        filepath: Path to the characters JSON file.
        
    Returns:
        List of character data dictionaries.
        
    Raises:
        DataLoadError: If file loading fails or data is invalid.
    """
    data = load_json_file(filepath)
    if 'heroes' not in data:
        raise DataLoadError(f"Invalid character data: missing 'heroes' key")
    return data['heroes']


def load_enemies(filepath: str) -> List[Dict[str, Any]]:
    """Load enemy data from JSON file.
    
    Args:
        filepath: Path to the enemies JSON file.
        
    Returns:
        List of enemy data dictionaries.
        
    Raises:
        DataLoadError: If file loading fails or data is invalid.
    """
    data = load_json_file(filepath)
    if 'enemies' not in data:
        raise DataLoadError(f"Invalid enemy data: missing 'enemies' key")
    return data['enemies']


def load_moves(filepath: str) -> List[Dict[str, Any]]:
    """Load move data from JSON file.
    
    Args:
        filepath: Path to the moves JSON file.
        
    Returns:
        List of move data dictionaries.
        
    Raises:
        DataLoadError: If file loading fails or data is invalid.
    """
    data = load_json_file(filepath)
    if 'moves' not in data:
        raise DataLoadError(f"Invalid move data: missing 'moves' key")
    return data['moves']


def load_config(filepath: str) -> Dict[str, Any]:
    """Load game configuration from JSON file.
    
    Args:
        filepath: Path to the settings JSON file.
        
    Returns:
        Configuration data as a dictionary.
        
    Raises:
        DataLoadError: If file loading fails or data is invalid.
    """
    return load_json_file(filepath)
