# game/core/save_manager.py

import json
from pathlib import Path

# Define the path for our saves directory and the save file
SAVES_DIR = Path(__file__).parent.parent.parent / "saves"
SAVE_FILE = SAVES_DIR / "savegame.json"

def save_game(data):
    """Saves the given data dictionary to the save file as JSON."""
    try:
        # Ensure the 'saves' directory exists
        SAVES_DIR.mkdir(exist_ok=True)
        
        with open(SAVE_FILE, "w") as f:
            json.dump(data, f, indent=4)
        print(f"Game saved successfully to {SAVE_FILE}")
    except Exception as e:
        print(f"Error saving game: {e}")

def load_game():
    """Loads and returns data from the save file. Returns None if no save exists."""
    if not SAVE_FILE.is_file():
        print("No save file found.")
        return None
    
    try:
        with open(SAVE_FILE, "r") as f:
            data = json.load(f)
        print(f"Game loaded successfully from {SAVE_FILE}")
        return data
    except Exception as e:
        print(f"Error loading game: {e}")
        return None