#!/usr/bin/env python3
"""
Hotkey Handler for Meeting Recorder
Handles global keyboard shortcuts and hotkey management
"""

import keyboard


class HotkeyHandler:
    """Manages global keyboard shortcuts"""
    
    def __init__(self, toggle_callback):
        """
        Initialize hotkey handler
        
        Args:
            toggle_callback: Function to call when hotkey is pressed
        """
        self.toggle_callback = toggle_callback
        self.hotkey_registered = False
    
    def setup_hotkey(self, hotkey='ctrl+shift+m'):
        """
        Setup global hotkey
        
        Args:
            hotkey: Hotkey combination string (default: 'ctrl+shift+r')
            
        Returns:
            bool: True if hotkey was registered successfully
        """
        try:
            # Register the hotkey
            keyboard.add_hotkey(hotkey, self.toggle_callback)
            print(f"✓ Hotkey registered: {hotkey}")
            self.hotkey_registered = True
            return True
        except Exception as e:
            print(f"⚠ Could not register hotkey: {e}")
            self.hotkey_registered = False
            return False
    
    def remove_hotkey(self, hotkey='ctrl+shift+m'):
        """
        Remove a registered hotkey
        
        Args:
            hotkey: Hotkey combination string to remove
            
        Returns:
            bool: True if hotkey was removed successfully
        """
        try:
            keyboard.remove_hotkey(hotkey)
            print(f"✓ Hotkey removed: {hotkey}")
            self.hotkey_registered = False
            return True
        except Exception as e:
            print(f"⚠ Could not remove hotkey: {e}")
            return False
    
    def is_hotkey_registered(self):
        """Check if hotkey is currently registered"""
        return self.hotkey_registered
    
    def cleanup(self):
        """Clean up all registered hotkeys"""
        try:
            keyboard.unhook_all_hotkeys()
            self.hotkey_registered = False
            print("✓ All hotkeys cleaned up")
            return True
        except Exception as e:
            print(f"⚠ Error cleaning up hotkeys: {e}")
            return False
