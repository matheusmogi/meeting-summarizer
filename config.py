import json
from pathlib import Path

def load_config():
    """Load configuration from JSON file"""
    try:
        config_path = Path(__file__).parent / "config.json"
        with open(config_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading config: {e}")
        return {}

