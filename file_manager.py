#!/usr/bin/env python3
"""
File Manager for Meeting Recorder
Handles file operations, upload functionality, and file deletion
"""

import os
import json
import time
import psutil
import subprocess
import requests
from datetime import datetime
from pathlib import Path


class FileManager:
    """Manages file operations, uploads, and deletions"""
    
    def __init__(self, webhook_url, credentials):
        """
        Initialize file manager
        
        Args:
            webhook_url: URL for uploading files
            credentials: Dictionary with username/password for authentication
        """
        self.webhook_url = webhook_url
        self.credentials = credentials
    
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
    
    def upload_file(self, file_path):
        """
        Upload recording to webhook
        
        Args:
            file_path: Path to the file to upload
            
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            file_info = Path(file_path)
            file_size = file_info.stat().st_size
            
            print(f"📤 Uploading: {file_info.name} ({file_size / (1024 * 1024):.2f} MB)")
            
            # Prepare metadata
            metadata = {
                "event": "tray_recording",
                "timestamp": datetime.now().isoformat(),
                "file": {
                    "name": file_info.name,
                    "path": str(file_path),
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
            # Determine MIME type based on file extension
            extension = file_info.suffix.lower()
            if extension == '.mp3':
                mime_type = 'audio/mpeg'
            elif extension == '.wav':
                mime_type = 'audio/wav'
            else:
                mime_type = 'application/octet-stream'

            with open(file_path, 'rb') as f:
                files = {
                    'data': (file_info.name, f, mime_type),
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
                return True, "Upload successful"
            else:
                error_msg = f"Upload failed: {response.status_code}"
                print(f"❌ {error_msg}")
                return False, error_msg
            
        except Exception as e:
            error_msg = f"Upload error: {e}"
            print(f"❌ {error_msg}")
            return False, error_msg
    
    def upload_and_delete_file(self, file_path):
        """
        Upload a file and delete it after successful upload
        
        Args:
            file_path: Path to the file to upload and delete
            
        Returns:
            tuple: (success: bool, message: str)
        """
        # First upload the file
        upload_success, upload_message = self.upload_file(file_path)
        
        if upload_success:
            # Force delete file after successful upload
            if self.force_delete_file(file_path):
                return True, f"File uploaded and deleted: {Path(file_path).name}"
            else:
                return True, f"File uploaded but not deleted: {Path(file_path).name}"
        else:
            return False, upload_message

    def convert_wav_to_mp3(self, wav_path, bitrate='192k'):
        """
        Convert a WAV file to MP3 using FFmpeg.
        
        Args:
            wav_path: Path to the source WAV file (str or Path)
            bitrate: Audio bitrate for MP3 (e.g., '128k', '192k')
        
        Returns:
            tuple: (success: bool, mp3_path_or_none: str | None, message: str)
        """
        try:
            source_path = Path(wav_path)
            if not source_path.exists():
                return False, None, f"Source file not found: {wav_path}"
            if source_path.suffix.lower() != '.wav':
                return False, None, "Input file is not a WAV file"

            mp3_path = source_path.with_suffix('.mp3')

            # Build FFmpeg command
            ffmpeg_cmd = [
                'ffmpeg',
                '-y',  # overwrite output
                '-i', str(source_path),
                '-codec:a', 'libmp3lame',
                '-b:a', str(bitrate),
                str(mp3_path)
            ]

            result = subprocess.run(
                ffmpeg_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )

            if result.returncode != 0:
                return False, None, f"FFmpeg conversion failed: {result.stderr.strip()}"

            if not mp3_path.exists() or mp3_path.stat().st_size <= 1024:
                return False, None, "Converted MP3 file is missing or too small"

            return True, str(mp3_path), f"Converted to MP3: {mp3_path.name}"
        except Exception as e:
            return False, None, f"Conversion error: {e}"
    
    def open_folder(self, folder_path):
        """
        Open a folder in the file explorer
        
        Args:
            folder_path: Path to the folder to open
        """
        try:
            os.startfile(str(folder_path))
        except Exception as e:
            print(f"Error opening folder: {e}")
            return False
        return True
