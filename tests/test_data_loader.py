"""Unit tests for data_loader module."""

import pytest
import os
import json
import tempfile
from src.utils.data_loader import (
    load_json_file,
    load_characters,
    load_enemies,
    load_moves,
    load_config,
    DataLoadError
)


class TestLoadJsonFile:
    """Tests for load_json_file function."""
    
    def test_load_valid_json(self, tmp_path):
        """Test loading a valid JSON file."""
        test_file = tmp_path / "test.json"
        test_data = {"key": "value", "number": 42}
        test_file.write_text(json.dumps(test_data))
        
        result = load_json_file(str(test_file))
        assert result == test_data
    
    def test_file_not_found(self):
        """Test loading a non-existent file raises DataLoadError."""
        with pytest.raises(DataLoadError, match="Data file not found"):
            load_json_file("/nonexistent/file.json")
    
    def test_invalid_json(self, tmp_path):
        """Test loading invalid JSON raises DataLoadError."""
        test_file = tmp_path / "invalid.json"
        test_file.write_text("{invalid json}")
        
        with pytest.raises(DataLoadError, match="Invalid JSON"):
            load_json_file(str(test_file))


class TestLoadCharacters:
    """Tests for load_characters function."""
    
    def test_load_valid_characters(self, tmp_path):
        """Test loading valid character data."""
        test_file = tmp_path / "characters.json"
        test_data = {
            "heroes": [
                {"id": "hero1", "name": "Mario", "max_hp": 100}
            ]
        }
        test_file.write_text(json.dumps(test_data))
        
        result = load_characters(str(test_file))
        assert result == test_data["heroes"]
    
    def test_missing_heroes_key(self, tmp_path):
        """Test loading data without 'heroes' key raises DataLoadError."""
        test_file = tmp_path / "characters.json"
        test_data = {"wrong_key": []}
        test_file.write_text(json.dumps(test_data))
        
        with pytest.raises(DataLoadError, match="missing 'heroes' key"):
            load_characters(str(test_file))


class TestLoadEnemies:
    """Tests for load_enemies function."""
    
    def test_load_valid_enemies(self, tmp_path):
        """Test loading valid enemy data."""
        test_file = tmp_path / "enemies.json"
        test_data = {
            "enemies": [
                {"id": "enemy1", "name": "Goomba", "max_hp": 30}
            ]
        }
        test_file.write_text(json.dumps(test_data))
        
        result = load_enemies(str(test_file))
        assert result == test_data["enemies"]
    
    def test_missing_enemies_key(self, tmp_path):
        """Test loading data without 'enemies' key raises DataLoadError."""
        test_file = tmp_path / "enemies.json"
        test_data = {"wrong_key": []}
        test_file.write_text(json.dumps(test_data))
        
        with pytest.raises(DataLoadError, match="missing 'enemies' key"):
            load_enemies(str(test_file))


class TestLoadMoves:
    """Tests for load_moves function."""
    
    def test_load_valid_moves(self, tmp_path):
        """Test loading valid move data."""
        test_file = tmp_path / "moves.json"
        test_data = {
            "moves": [
                {"id": "move1", "name": "Jump", "type": "physical"}
            ]
        }
        test_file.write_text(json.dumps(test_data))
        
        result = load_moves(str(test_file))
        assert result == test_data["moves"]
    
    def test_missing_moves_key(self, tmp_path):
        """Test loading data without 'moves' key raises DataLoadError."""
        test_file = tmp_path / "moves.json"
        test_data = {"wrong_key": []}
        test_file.write_text(json.dumps(test_data))
        
        with pytest.raises(DataLoadError, match="missing 'moves' key"):
            load_moves(str(test_file))


class TestLoadConfig:
    """Tests for load_config function."""
    
    def test_load_valid_config(self, tmp_path):
        """Test loading valid configuration."""
        test_file = tmp_path / "settings.json"
        test_data = {
            "display": {"width": 1280, "height": 720}
        }
        test_file.write_text(json.dumps(test_data))
        
        result = load_config(str(test_file))
        assert result == test_data
