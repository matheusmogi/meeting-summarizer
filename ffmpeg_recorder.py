#!/usr/bin/env python3
"""
FFmpeg Audio Recorder
Records microphone + system audio using FFmpeg and VB-Audio Virtual Cable
Automatically uploads to N8N webhook and deletes files after successful upload
"""

import subprocess
import os
import sys
import signal
import threading
import time
import json
import requests
from datetime import datetime
from pathlib import Path

class FFmpegRecorder:
    def __init__(self, config_file="config.json"):
        self.recording = False
        self.ffmpeg_process = None
        self.monitor_thread = None
        self.recording_file = None
        
        # Load configuration
        self.config = self.load_config(config_file)
        self.webhook_url = self.config.get("n8n_webhook_url")
        self.credentials = self.config.get("credentials", {})
        self.audio_folder = Path(self.config.get("watch_folder", "D:\\study\\AI\\meeting-recorder\\audio"))
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.stop_recording)
        signal.signal(signal.SIGTERM, self.stop_recording)
        
    def load_config(self, config_file):
        """Load configuration from JSON file"""
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            return config
        except Exception as e:
            print(f"❌ Error loading config: {e}")
            return {}
    
    def check_ffmpeg(self):
        """Check if FFmpeg is available"""
        try:
            result = subprocess.run(['ffmpeg', '-version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print("✓ FFmpeg found and working")
                return True
            else:
                print("❌ FFmpeg not working properly")
                return False
        except FileNotFoundError:
            print("❌ FFmpeg not found in PATH")
            print("   Please install FFmpeg: https://ffmpeg.org/download.html")
            return False
        except Exception as e:
            print(f"❌ Error checking FFmpeg: {e}")
            return False
    
    def list_audio_devices(self):
        """List available audio devices for user reference"""
        try:
            print("🎤 Detecting audio devices...")
            result = subprocess.run([
                'ffmpeg', '-f', 'dshow', '-list_devices', 'true', '-i', 'dummy'
            ], capture_output=True, text=True, timeout=10)
            
            # FFmpeg outputs device list to stderr
            output = result.stderr
            
            print("Available audio devices:")
            lines = output.split('\n')
            for line in lines:
                if 'audio' in line.lower() and '"' in line:
                    print(f"   {line.strip()}")
            
            return True
        except Exception as e:
            print(f"⚠ Could not list devices: {e}")
            return False
    
    def generate_filename(self):
        """Generate filename with current datetime"""
        now = datetime.now()
        timestamp = now.strftime("%Y%m%d_%H%M%S")
        filename = f"recording_{timestamp}.wav"
        return self.audio_folder / filename
    
    def start_ffmpeg_recording(self):
        """Start FFmpeg recording with microphone + system audio"""
        
        # Ensure audio folder exists
        self.audio_folder.mkdir(parents=True, exist_ok=True)
        
        # Generate output filename
        self.recording_file = self.generate_filename()
        
        # FFmpeg command to record both sources
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
        
        print(f"🎙️ Starting FFmpeg recording...")
        print(f"   Output: {self.recording_file}")
        print(f"   Command: {' '.join(ffmpeg_cmd)}")
        print("")
        
        try:
            self.ffmpeg_process = subprocess.Popen(
                ffmpeg_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            print("✓ FFmpeg recording started successfully")
            print("   Recording both microphone and system audio")
            print("   Press Ctrl+C to stop recording")
            print("")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to start FFmpeg recording: {e}")
            return False
    
    def monitor_recording(self):
        """Monitor FFmpeg process and show status"""
        start_time = time.time()
        
        while self.recording and self.ffmpeg_process:
            # Check if process is still running
            if self.ffmpeg_process.poll() is not None:
                print("⚠ FFmpeg process ended unexpectedly")
                break
            
            # Show elapsed time every 30 seconds
            elapsed = time.time() - start_time
            if int(elapsed) % 30 == 0 and int(elapsed) > 0:
                minutes, seconds = divmod(int(elapsed), 60)
                print(f"🎵 Recording... {minutes:02d}:{seconds:02d}")
            
            time.sleep(1)
    
    def upload_to_webhook(self, file_path):
        """Upload the recorded file to N8N webhook"""
        if not self.webhook_url:
            print("⚠ No webhook URL configured - skipping upload")
            return False
        
        file_info = Path(file_path)
        file_size = file_info.stat().st_size
        
        print(f"📤 Uploading to N8N webhook...")
        print(f"   File: {file_info.name} ({file_size / (1024 * 1024):.2f} MB)")
        
        # Prepare metadata
        metadata = {
            "event": "ffmpeg_recording",
            "timestamp": datetime.now().isoformat(),
            "file": {
                "name": file_info.name,
                "path": str(file_path),
                "size_bytes": file_size,
                "size_mb": round(file_size / (1024 * 1024), 2),
                "created": datetime.fromtimestamp(file_info.stat().st_ctime).isoformat(),
                "modified": datetime.fromtimestamp(file_info.stat().st_mtime).isoformat()
            },
            "source": "ffmpeg_recorder"
        }
        
        try:
            # Get credentials
            username = self.credentials.get("username", "")
            password = self.credentials.get("password", "")
            
            # Prepare multipart form data
            with open(file_path, 'rb') as f:
                files = {
                    'data': (file_info.name, f, 'audio/wav'),
                    'metadata': (None, json.dumps(metadata), 'application/json')
                }
                
                # Setup basic authentication
                auth = None
                if username and password:
                    auth = (username, password)
                    print(f"   Using auth: {username}")
                else:
                    print("   No authentication configured")
                
                response = requests.post(
                    self.webhook_url,
                    files=files,
                    auth=auth,
                    timeout=60  # Longer timeout for large files
                )
            
            print(f"   Response: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ File uploaded successfully!")
                
                # Delete the file after successful upload
                try:
                    os.remove(file_path)
                    print(f"🗑️ Deleted file after successful upload: {file_info.name}")
                    return True
                except Exception as delete_error:
                    print(f"⚠ Could not delete file: {delete_error}")
                    print(f"   File remains at: {file_path}")
                    return True
                    
            elif response.status_code == 403:
                print("❌ Authentication failed - check credentials")
                print("   File NOT deleted (upload failed)")
                return False
            else:
                print(f"⚠ Server responded with status: {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                print("   File NOT deleted (upload failed)")
                return False
                
        except requests.RequestException as e:
            print(f"❌ Upload error: {e}")
            print("   File NOT deleted (upload failed)")
            return False
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            print("   File NOT deleted (upload failed)")
            return False
    
    def stop_recording(self, sig=None, frame=None):
        """Stop recording and cleanup"""
        print("")
        print("🛑 Stopping recording...")
        self.recording = False
        
        # Stop FFmpeg process
        if self.ffmpeg_process:
            try:
                self.ffmpeg_process.terminate()
                
                # Give it a moment to terminate gracefully
                try:
                    self.ffmpeg_process.wait(timeout=5)
                    print("✓ FFmpeg stopped gracefully")
                except subprocess.TimeoutExpired:
                    print("⚠ Force killing FFmpeg...")
                    self.ffmpeg_process.kill()
                    self.ffmpeg_process.wait()
                
            except Exception as e:
                print(f"Error stopping FFmpeg: {e}")
        
        # Check if we have a recording file to upload
        if self.recording_file and os.path.exists(self.recording_file):
            file_size = os.path.getsize(self.recording_file)
            if file_size > 1024:  # Only upload if file has actual content
                print("")
                print("📁 Recording completed!")
                print(f"   File: {self.recording_file}")
                print(f"   Size: {file_size / (1024 * 1024):.2f} MB")
                
                # Upload to webhook
                self.upload_to_webhook(self.recording_file)
            else:
                print("⚠ Recording file is too small, not uploading")
        
        print("")
        print("✓ FFmpeg recorder finished")
    
    def run(self):
        """Main run function"""
        print("=" * 60)
        print("FFmpeg Audio Recorder")
        print("=" * 60)
        print(f"Webhook: {self.webhook_url}")
        print(f"Auth User: {self.credentials.get('username', 'Not configured')}")
        print(f"Output Folder: {self.audio_folder}")
        print("")
        
        # Check FFmpeg
        if not self.check_ffmpeg():
            return False
        
        # Show available devices
        self.list_audio_devices()
        print("")
        
        # Start recording
        if not self.start_ffmpeg_recording():
            return False
        
        # Start monitoring
        self.recording = True
        self.monitor_thread = threading.Thread(target=self.monitor_recording, daemon=True)
        self.monitor_thread.start()
        
        try:
            # Keep running until Ctrl+C
            while self.recording:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop_recording()
        
        return True


def main():
    """Main function"""
    try:
        recorder = FFmpegRecorder()
        success = recorder.run()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
