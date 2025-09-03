#!/usr/bin/env python3
"""
Configuration Manager for Meeting Recorder
Handles loading and managing application configuration
"""

import json
from pathlib import Path


class ConfigManager:
    """Manages application configuration loading and access"""
    
    def __init__(self, config_file="config.json"):
        self.config_file = config_file
        self.config = self.load_config()
    
    def load_config(self):
        """Load configuration from JSON file"""
        try:
            config_path = Path(__file__).parent / self.config_file
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            return {}
    
    def get_webhook_url(self):
        """Get the n8n webhook URL"""
        return self.config.get("n8n_webhook_url")
    
    def get_credentials(self):
        """Get authentication credentials"""
        return self.config.get("credentials", {})
    
    def get_audio_folder(self):
        """Get the audio folder path"""
        folder_path = self.config.get("watch_folder", "D:\\study\\AI\\meeting-recorder\\audio")
        return Path(folder_path)
    
    def get_config(self):
        """Get the full configuration dictionary"""
        return self.config
    
    def reload_config(self):
        """Reload configuration from file"""
        self.config = self.load_config()
        return self.config
