#!/usr/bin/env python3
"""
Audio Recorder for Meeting Recorder
Handles FFmpeg recording functionality
"""

import os
import subprocess
from datetime import datetime
from pathlib import Path


class AudioRecorder:
    """Manages audio recording using FFmpeg"""
    
    def __init__(self, audio_folder):
        """
        Initialize audio recorder
        
        Args:
            audio_folder: Path object for audio output directory
        """
        self.audio_folder = Path(audio_folder)
        self.recording = False
        self.ffmpeg_process = None
        self.recording_file = None
        
        # Ensure audio folder exists
        self.audio_folder.mkdir(parents=True, exist_ok=True)
    
    def generate_filename(self):
        """Generate filename with current datetime"""
        now = datetime.now()
        timestamp = now.strftime("%Y%m%d_%H%M%S")
        filename = f"recording_{timestamp}.wav"
        return self.audio_folder / filename
    
    def start_recording(self):
        """Start FFmpeg recording"""
        if self.recording:
            return False, "Already recording"
        
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
            print(f"✓ Recording started: {self.recording_file.name}")
            return True, f"Recording started: {self.recording_file.name}"
            
        except Exception as e:
            error_msg = f"Failed to start recording: {e}"
            print(f"❌ {error_msg}")
            return False, error_msg
    
    def stop_recording(self):
        """Stop FFmpeg recording"""
        if not self.recording:
            return False, "Not recording"
        
        self.recording = False
        
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
                
                # Check if file exists and has content
                if self.recording_file and os.path.exists(self.recording_file):
                    file_size = os.path.getsize(self.recording_file)
                    if file_size > 1024:  # Only consider valid if file has content
                        return True, f"Recording stopped: {self.recording_file.name}"
                    else:
                        return False, "Recording file too small"
                else:
                    return False, "Recording file not found"
                
            except Exception as e:
                error_msg = f"Error stopping FFmpeg: {e}"
                print(f"❌ {error_msg}")
                return False, error_msg
        
        return True, "Recording stopped"
    
    def is_recording(self):
        """Check if currently recording"""
        return self.recording
    
    def get_current_recording_file(self):
        """Get the path to the current recording file"""
        return self.recording_file
    
    def get_audio_folder(self):
        """Get the audio output folder path"""
        return self.audio_folder
