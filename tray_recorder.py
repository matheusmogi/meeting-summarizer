#!/usr/bin/env python3
"""
Meeting Recorder - System Tray Application
System tray icon with Ctrl+Shift+R hotkey for quick recording control
"""

import sys
import os
import threading
import subprocess
import json
import time
import psutil
from datetime import datetime
from pathlib import Path

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
        self.recording = False
        self.ffmpeg_process = None
        self.recording_file = None
        self.icon = None
        
        # Load configuration
        self.config = self.load_config()
        self.webhook_url = self.config.get("n8n_webhook_url")
        self.credentials = self.config.get("credentials", {})
        self.audio_folder = Path(self.config.get("watch_folder", "D:\\study\\AI\\meeting-recorder\\audio"))
        
        # Ensure audio folder exists
        self.audio_folder.mkdir(parents=True, exist_ok=True)
        
        # Create tray icon
        self.create_icon()
        
    def load_config(self):
        """Load configuration from JSON file"""
        try:
            config_path = Path(__file__).parent / "config.json"
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            return {}
    
    def force_delete_file(self, file_path):
        """Force delete a file, even if it's locked by processes"""
        if not os.path.exists(file_path):
            print(f"✓ File doesn't exist: {file_path}")
            return True
        
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                # Try normal deletion first
                os.remove(file_path)
                print(f"🗑️ Successfully deleted: {Path(file_path).name}")
                return True
                
            except PermissionError as e:
                print(f"⚠ Attempt {attempt + 1}/{max_attempts}: File is locked - {e}")
                
                if attempt < max_attempts - 1:  # Not the last attempt
                    # Find and kill processes using this file
                    try:
                        killed_processes = []
                        for proc in psutil.process_iter(['pid', 'name', 'open_files']):
                            try:
                                if proc.info['open_files']:
                                    for file_info in proc.info['open_files']:
                                        if file_info.path == str(file_path):
                                            print(f"🔪 Killing process: {proc.info['name']} (PID: {proc.info['pid']})")
                                            proc.kill()
                                            killed_processes.append(proc.info['name'])
                                            break
                            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                                continue
                        
                        if killed_processes:
                            print(f"✓ Killed processes: {', '.join(killed_processes)}")
                            time.sleep(1)  # Wait for processes to die
                        else:
                            print("⚠ No processes found using the file")
                            
                    except Exception as kill_error:
                        print(f"⚠ Error finding/killing processes: {kill_error}")
                        time.sleep(2)  # Wait and retry
                else:
                    # Last attempt - try Windows-specific force delete
                    try:
                        import subprocess
                        result = subprocess.run(
                            ['cmd', '/c', 'del', '/f', '/q', str(file_path)],
                            capture_output=True,
                            text=True,
                            timeout=10
                        )
                        if result.returncode == 0:
                            print(f"🗑️ Force deleted via CMD: {Path(file_path).name}")
                            return True
                        else:
                            print(f"❌ CMD delete failed: {result.stderr}")
                    except Exception as cmd_error:
                        print(f"❌ CMD delete error: {cmd_error}")
                    
            except Exception as e:
                print(f"❌ Attempt {attempt + 1}/{max_attempts}: Unexpected error - {e}")
                if attempt < max_attempts - 1:
                    time.sleep(1)
        
        print(f"❌ Failed to delete file after {max_attempts} attempts: {file_path}")
        return False
    
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
    
    def create_icon(self):
        """Create the system tray icon"""
        image = self.create_icon_image(False)
        
        menu = pystray.Menu(
            item('Meeting Recorder', lambda icon, item: None, enabled=False),
            pystray.Menu.SEPARATOR,
            item('Start Recording (Ctrl+Shift+R)', self.start_recording, enabled=lambda item: not self.recording),
            item('Stop Recording', self.stop_recording, enabled=lambda item: self.recording),
            pystray.Menu.SEPARATOR,

            item('Test Audio Devices', self.test_audio_devices),
            item('Open Audio Folder', self.open_audio_folder),
            pystray.Menu.SEPARATOR,
            item('Status: Ready', lambda icon, item: None, enabled=False),
            pystray.Menu.SEPARATOR,
            item('Exit', self.quit_application)
        )
        
        self.icon = pystray.Icon("meeting_recorder", image, "Meeting Recorder", menu)
    
    def update_icon_status(self, recording=False, status_text="Ready"):
        """Update the icon and status"""
        if self.icon:
            # Update icon image
            self.icon.icon = self.create_icon_image(recording)
            
            # Update menu with new status
            menu = pystray.Menu(
                item('Meeting Recorder', lambda icon, item: None, enabled=False),
                pystray.Menu.SEPARATOR,
                item('Start Recording (Ctrl+Shift+R)', self.start_recording, enabled=lambda item: not self.recording),
                item('Stop Recording', self.stop_recording, enabled=lambda item: self.recording),
                pystray.Menu.SEPARATOR,
    
                item('Test Audio Devices', self.test_audio_devices),
                item('Open Audio Folder', self.open_audio_folder),
                pystray.Menu.SEPARATOR,
                item(f'Status: {status_text}', lambda icon, item: None, enabled=False),
                pystray.Menu.SEPARATOR,
                item('Exit', self.quit_application)
            )
            
            self.icon.menu = menu
            self.icon.update_menu()
    
    def setup_hotkey(self):
        """Setup global hotkey Ctrl+Shift+R"""
        try:
            # Register the hotkey
            keyboard.add_hotkey('ctrl+shift+r', self.toggle_recording)
            print("✓ Hotkey registered: Ctrl+Shift+R")
            return True
        except Exception as e:
            print(f"⚠ Could not register hotkey: {e}")
            return False
    
    def toggle_recording(self):
        """Toggle recording on/off"""
        if self.recording:
            self.stop_recording()
        else:
            self.start_recording()
    
    def generate_filename(self):
        """Generate filename with current datetime"""
        now = datetime.now()
        timestamp = now.strftime("%Y%m%d_%H%M%S")
        filename = f"recording_{timestamp}.wav"
        return self.audio_folder / filename
    
    def start_recording(self):
        """Start FFmpeg recording"""
        if self.recording:
            return
        
        # Generate output filename
        self.recording_file = self.generate_filename()
        
        # FFmpeg command
        ffmpeg_cmd = [
            'ffmpeg',
            '-f', 'dshow',
            '-i', 'audio=Microphone (USB PnP Sound Device)',
            '-f', 'dshow', 
            '-i', 'audio=CABLE Output (VB-Audio Virtual Cable)',
            '-filter_complex', 'amix=inputs=2:duration=longest',
            '-y',  # Overwrite output file if it exists
            str(self.recording_file)
        ]
        
        try:
            self.ffmpeg_process = subprocess.Popen(
                ffmpeg_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW  # Hide console window
            )
            
            self.recording = True
            self.update_icon_status(True, "Recording...")
            
            print(f"✓ Recording started: {self.recording_file.name}")
            
            # Show notification
            if self.icon:
                self.icon.notify("Recording Started", f"Saving to: {self.recording_file.name}")
            
        except Exception as e:
            print(f"❌ Failed to start recording: {e}")
            if self.icon:
                self.icon.notify("Recording Failed", str(e))
    
    def stop_recording(self):
        """Stop FFmpeg recording and upload"""
        if not self.recording:
            return
        
        self.recording = False
        self.update_icon_status(False, "Stopping...")
        
        # Stop FFmpeg process
        if self.ffmpeg_process:
            try:
                self.ffmpeg_process.terminate()
                
                # Wait for process to stop
                try:
                    self.ffmpeg_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self.ffmpeg_process.kill()
                    self.ffmpeg_process.wait()
                
                print("✓ Recording stopped")
                
            except Exception as e:
                print(f"Error stopping FFmpeg: {e}")
        
        # Upload in background thread
        if self.recording_file and os.path.exists(self.recording_file):
            file_size = os.path.getsize(self.recording_file)
            if file_size > 1024:  # Only upload if file has content
                self.update_icon_status(False, "Uploading...")
                threading.Thread(target=self.upload_file, daemon=True).start()
            else:
                print("⚠ Recording file too small, not uploading")
                self.update_icon_status(False, "Ready")
        else:
            self.update_icon_status(False, "Ready")
    
    def upload_file(self):
        """Upload recording to webhook"""
        try:
            file_info = Path(self.recording_file)
            file_size = file_info.stat().st_size
            
            print(f"📤 Uploading: {file_info.name} ({file_size / (1024 * 1024):.2f} MB)")
            
            # Prepare metadata
            metadata = {
                "event": "tray_recording",
                "timestamp": datetime.now().isoformat(),
                "file": {
                    "name": file_info.name,
                    "path": str(self.recording_file),
                    "size_bytes": file_size,
                    "size_mb": round(file_size / (1024 * 1024), 2),
                    "created": datetime.fromtimestamp(file_info.stat().st_ctime).isoformat(),
                    "modified": datetime.fromtimestamp(file_info.stat().st_mtime).isoformat()
                },
                "source": "tray_recorder"
            }
            
            # Get credentials
            username = self.credentials.get("username", "")
            password = self.credentials.get("password", "")
            
            # Upload with authentication
            with open(self.recording_file, 'rb') as f:
                files = {
                    'data': (file_info.name, f, 'audio/wav'),
                    'metadata': (None, json.dumps(metadata), 'application/json')
                }
                
                auth = (username, password) if username and password else None
                
                response = requests.post(
                    self.webhook_url,
                    files=files,
                    auth=auth,
                    timeout=60
                )
            
            if response.status_code == 200:
                print("✅ Upload successful")
                
                # Force delete file after successful upload
                if self.force_delete_file(self.recording_file):
                    if self.icon:
                        self.icon.notify("Upload Complete", f"File uploaded and deleted: {file_info.name}")
                else:
                    print(f"⚠ Could not delete file: {self.recording_file}")
                    if self.icon:
                        self.icon.notify("Upload Complete", f"File uploaded but not deleted: {file_info.name}")
                
            else:
                print(f"❌ Upload failed: {response.status_code}")
                
                if self.icon:
                    self.icon.notify("Upload Failed", f"Status: {response.status_code}")
            
        except Exception as e:
            print(f"❌ Upload error: {e}")
            
            if self.icon:
                self.icon.notify("Upload Error", str(e))
        
        finally:
            self.update_icon_status(False, "Ready")
    
    def test_audio_devices(self):
        """Audio device tester (feature removed for simplicity)"""
        self.show_notification("Audio Test", "Device testing feature was removed for simplicity")
    
    def open_audio_folder(self):
        """Open the audio output folder"""
        try:
            os.startfile(str(self.audio_folder))
        except Exception as e:
            print(f"Error opening folder: {e}")
    
    def quit_application(self):
        """Quit the application"""
        if self.recording:
            self.stop_recording()
            # Give it a moment to stop
            time.sleep(2)
        
        self.icon.stop()
    
    def run(self):
        """Run the tray application"""
        print("=" * 50)
        print("Meeting Recorder - System Tray")
        print("=" * 50)
        print(f"Webhook: {self.webhook_url}")
        print(f"Audio Folder: {self.audio_folder}")
        print("Hotkey: Ctrl+Shift+R")
        print("Right-click tray icon for menu")
        print("")
        
        # Setup hotkey
        self.setup_hotkey()
        
        # Run the tray icon
        try:
            self.icon.run()
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
