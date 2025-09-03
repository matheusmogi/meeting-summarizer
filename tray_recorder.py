#!/usr/bin/env python3
"""
Meeting Recorder - System Tray Application
System tray icon with Ctrl+Shift+R hotkey for quick recording control
"""

import sys
import os
import threading
import time
from pathlib import Path

# Import our custom modules
from config_manager import ConfigManager
from icon_manager import IconManager
from audio_recorder import AudioRecorder
from file_manager import FileManager
from hotkey_handler import HotkeyHandler

try:
    import pystray
    from pystray import MenuItem as item
    from PIL import Image, ImageDraw
    import keyboard
    import requests
except ImportError as e:
    print(f"Missing required package: {e}")
    print("Please install required packages:")
    print("pip install pystray pillow keyboard requests")
    sys.exit(1)

class TrayRecorder:
    def __init__(self):
        # Initialize configuration manager
        self.config_manager = ConfigManager()
        
        # Initialize components
        self.audio_recorder = AudioRecorder(self.config_manager.get_audio_folder())
        self.file_manager = FileManager(
            self.config_manager.get_webhook_url(),
            self.config_manager.get_credentials()
        )
        
        # Setup callbacks for icon manager
        callbacks = {
            'start_recording': self.start_recording,
            'stop_recording': self.stop_recording,
            'convert_latest_to_mp3': self.convert_latest_to_mp3,
            'send_mp3_files': self.send_mp3_files,
            'test_audio_devices': self.test_audio_devices,
            'open_audio_folder': self.open_audio_folder,
            'quit_application': self.quit_application
        }
        
        self.icon_manager = IconManager(callbacks)
        self.hotkey_handler = HotkeyHandler(self.toggle_recording)
        
        # Create tray icon
        self.icon = self.icon_manager.create_icon()
        

    
    def toggle_recording(self):
        """Toggle recording on/off"""
        if self.audio_recorder.is_recording():
            self.stop_recording()
        else:
            self.start_recording()
    
    def start_recording(self):
        """Start FFmpeg recording"""
        success, message = self.audio_recorder.start_recording()
        
        if success:
            self.icon_manager.update_icon_status(True, "Recording...")
            self.icon_manager.notify("Recording Started", message)
        else:
            self.icon_manager.notify("Recording Failed", message)
    
    def stop_recording(self):
        """Stop FFmpeg recording and upload"""
        if not self.audio_recorder.is_recording():
            return
        
        self.icon_manager.update_icon_status(False, "Stopping...")
        
        success, message = self.audio_recorder.stop_recording()
        
        if success:
            # Get the recording file path
            recording_file = self.audio_recorder.get_current_recording_file()
            
            if recording_file and os.path.exists(recording_file):
                file_size = os.path.getsize(recording_file)
                if file_size > 1024:  # Only upload if file has content
                    self.icon_manager.update_icon_status(False, "Uploading...")
                    threading.Thread(target=self.upload_file, args=(recording_file,), daemon=True).start()
                else:
                    print("⚠ Recording file too small, not uploading")
                    self.icon_manager.update_icon_status(False, "Ready")
            else:
                self.icon_manager.update_icon_status(False, "Ready")
        else:
            self.icon_manager.notify("Stop Recording Failed", message)
            self.icon_manager.update_icon_status(False, "Ready")
    
    def upload_file(self, file_path):
        """Convert to MP3 if needed, upload to webhook, and clean up"""
        try:
            source_path = Path(file_path)
            target_path = source_path

            # If WAV, convert to MP3 first
            if source_path.suffix.lower() == '.wav':
                self.icon_manager.update_icon_status(False, "Converting to MP3...")
                converted, mp3_path, conv_msg = self.file_manager.convert_wav_to_mp3(str(source_path))
                if converted and mp3_path:
                    target_path = Path(mp3_path)
                    self.icon_manager.notify("Conversion Complete", conv_msg)
                    # Always delete the original WAV after successful conversion
                    try:
                        self.file_manager.force_delete_file(str(source_path))
                    except Exception:
                        pass
                else:
                    # Conversion failed; fallback to uploading WAV
                    self.icon_manager.notify("Conversion Failed", f"{conv_msg}. Uploading WAV.")

            # Upload target file (MP3 if converted, else original)
            self.icon_manager.update_icon_status(False, "Uploading...")
            success, message = self.file_manager.upload_and_delete_file(str(target_path))

            if success:
                self.icon_manager.notify("Upload Complete", message)
            else:
                self.icon_manager.notify("Upload Failed", message)
        except Exception as e:
            self.icon_manager.notify("Upload Error", str(e))
        finally:
            self.icon_manager.update_icon_status(False, "Ready")

    def convert_latest_to_mp3(self):
        """Convert the most recent WAV in the audio folder to MP3"""
        try:
            folder = self.audio_recorder.get_audio_folder()
            wav_files = list(Path(folder).glob('*.wav'))
            if not wav_files:
                self.icon_manager.notify("Convert to MP3", "No WAV files found")
                return
            latest_wav = max(wav_files, key=lambda p: p.stat().st_mtime)
            self.icon_manager.update_icon_status(False, "Converting to MP3...")
            success, mp3_path, message = self.file_manager.convert_wav_to_mp3(str(latest_wav))
            if success:
                # Delete the source WAV after successful conversion
                try:
                    self.file_manager.force_delete_file(str(latest_wav))
                except Exception:
                    pass
                self.icon_manager.notify("Conversion Complete", message)
                # Upload the converted MP3 to n8n
                self.icon_manager.update_icon_status(False, "Uploading...")
                up_ok, up_msg = self.file_manager.upload_and_delete_file(str(mp3_path))
                if up_ok:
                    self.icon_manager.notify("Upload Complete", up_msg)
                else:
                    self.icon_manager.notify("Upload Failed", up_msg)
            else:
                self.icon_manager.notify("Conversion Failed", message)
        except Exception as e:
            self.icon_manager.notify("Conversion Error", str(e))
        finally:
            self.icon_manager.update_icon_status(False, "Ready")

    def send_mp3_files(self):
        """Send all MP3 files in the audio folder to n8n (runs in background)"""
        threading.Thread(target=self._send_mp3_files_worker, daemon=True).start()

    def _send_mp3_files_worker(self):
        try:
            folder = self.audio_recorder.get_audio_folder()
            mp3_files = sorted(list(Path(folder).glob('*.mp3')), key=lambda p: p.stat().st_mtime)
            if not mp3_files:
                self.icon_manager.notify("Send MP3 Files", "No MP3 files found")
                return
            self.icon_manager.update_icon_status(False, "Uploading MP3 files...")
            for mp3_file in mp3_files:
                success, message = self.file_manager.upload_and_delete_file(str(mp3_file))
                if success:
                    self.icon_manager.notify("Upload Complete", f"{mp3_file.name}")
                else:
                    self.icon_manager.notify("Upload Failed", f"{mp3_file.name}: {message}")
        except Exception as e:
            self.icon_manager.notify("Upload Error", str(e))
        finally:
            self.icon_manager.update_icon_status(False, "Ready")
    
    def test_audio_devices(self):
        """Audio device tester (feature removed for simplicity)"""
        self.icon_manager.notify("Audio Test", "Device testing feature was removed for simplicity")
    
    def open_audio_folder(self):
        """Open the audio output folder"""
        self.file_manager.open_folder(self.audio_recorder.get_audio_folder())
    
    def quit_application(self):
        """Quit the application"""
        if self.audio_recorder.is_recording():
            self.stop_recording()
            # Give it a moment to stop
            time.sleep(2)
        
        # Clean up hotkeys
        self.hotkey_handler.cleanup()
        
        # Stop the icon
        self.icon_manager.stop()
    
    def run(self):
        """Run the tray application"""
        print("=" * 50)
        print("Meeting Recorder - System Tray")
        print("=" * 50)
        print(f"Webhook: {self.config_manager.get_webhook_url()}")
        print(f"Audio Folder: {self.audio_recorder.get_audio_folder()}")
        print("Hotkey: Ctrl+Shift+M")
        print("Right-click tray icon for menu")
        print("")
        
        # Setup hotkey
        self.hotkey_handler.setup_hotkey()
        
        # Run the tray icon
        try:
            self.icon_manager.run()
        except KeyboardInterrupt:
            print("\nShutting down...")
            self.quit_application()

def main():
    """Main function"""
    try:
        app = TrayRecorder()
        app.run()
    except Exception as e:
        print(f"Error: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()
