#!/usr/bin/env python3
"""
Icon Manager for Meeting Recorder
Handles system tray icon creation and management
"""

import pystray
from pystray import MenuItem as item
from PIL import Image, ImageDraw


class IconManager:
    """Manages system tray icon creation and updates"""
    
    def __init__(self, callbacks):
        """
        Initialize icon manager
        
        Args:
            callbacks: Dictionary of callback functions for menu items
                Expected keys: start_recording, stop_recording, test_audio_devices,
                             open_audio_folder, quit_application
        """
        self.callbacks = callbacks
        self.icon = None
        self.recording = False
        
    def create_icon_image(self, recording=False):
        """Create system tray icon image"""
        # Create a 64x64 image
        image = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        if recording:
            # Red circle for recording
            draw.ellipse([8, 8, 56, 56], fill=(220, 20, 20, 255), outline=(255, 255, 255, 255), width=3)
            # White dot in center
            draw.ellipse([26, 26, 38, 38], fill=(255, 255, 255, 255))
        else:
            # Blue microphone icon for idle
            draw.ellipse([8, 8, 56, 56], fill=(20, 100, 220, 255), outline=(255, 255, 255, 255), width=3)
            # Microphone shape
            draw.rectangle([28, 16, 36, 40], fill=(255, 255, 255, 255))
            draw.ellipse([24, 12, 40, 28], fill=(255, 255, 255, 255))
            draw.rectangle([30, 40, 34, 50], fill=(255, 255, 255, 255))
            draw.rectangle([24, 46, 40, 52], fill=(255, 255, 255, 255))
        
        return image
    
    def create_menu(self, status_text="Ready"):
        """Create the context menu for the tray icon"""
        return pystray.Menu(
            item('Meeting Recorder', lambda icon, item: None, enabled=False),
            pystray.Menu.SEPARATOR,
            item('Start Recording (Ctrl+Shift+M)', self.callbacks['start_recording'], 
                 enabled=lambda item: not self.recording),
            item('Stop Recording', self.callbacks['stop_recording'], 
                 enabled=lambda item: self.recording),
            pystray.Menu.SEPARATOR,
            item('Convert Latest WAV to MP3', self.callbacks['convert_latest_to_mp3']),
            item('Send MP3 Files Now', self.callbacks['send_mp3_files']),
            pystray.Menu.SEPARATOR,
            item('Test Audio Devices', self.callbacks['test_audio_devices']),
            item('Open Audio Folder', self.callbacks['open_audio_folder']),
            pystray.Menu.SEPARATOR,
            item(f'Status: {status_text}', lambda icon, item: None, enabled=False),
            pystray.Menu.SEPARATOR,
            item('Exit', self.callbacks['quit_application'])
        )
    
    def create_icon(self):
        """Create the system tray icon"""
        image = self.create_icon_image(False)
        menu = self.create_menu()
        self.icon = pystray.Icon("meeting_recorder", image, "Meeting Recorder", menu)
        return self.icon
    
    def update_icon_status(self, recording=False, status_text="Ready"):
        """Update the icon and status"""
        self.recording = recording
        
        if self.icon:
            # Update icon image
            self.icon.icon = self.create_icon_image(recording)
            
            # Update menu with new status
            self.icon.menu = self.create_menu(status_text)
            self.icon.update_menu()
    
    def notify(self, title, message):
        """Show a system notification"""
        if self.icon:
            self.icon.notify(title, message)
    
    def stop(self):
        """Stop the tray icon"""
        if self.icon:
            self.icon.stop()
    
    def run(self):
        """Run the tray icon (blocking)"""
        if self.icon:
            self.icon.run()
