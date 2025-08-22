#!/usr/bin/env python3
"""
Force cleanup audio folder - Delete all remaining files
Uses the same robust deletion method as the tray recorder
"""

import os
import time
import psutil
import subprocess
from pathlib import Path

def force_delete_file(file_path):
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

def cleanup_audio_folder():
    """Clean up all files in the audio folder"""
    print("=" * 60)
    print("Force Audio Folder Cleanup")
    print("=" * 60)
    
    # Get audio folder path
    script_dir = Path(__file__).parent
    audio_folder = script_dir / "audio"
    
    if not audio_folder.exists():
        print("✓ Audio folder doesn't exist")
        return
    
    # Get all files in audio folder
    audio_files = list(audio_folder.glob("*.wav"))
    
    if not audio_files:
        print("✓ Audio folder is already clean")
        return
    
    print(f"Found {len(audio_files)} files to delete:")
    for file_path in audio_files:
        print(f"  - {file_path.name}")
    
    print("\nStarting force deletion...")
    print()
    
    # Delete each file
    deleted_count = 0
    failed_count = 0
    
    for file_path in audio_files:
        print(f"Processing: {file_path.name}")
        if force_delete_file(file_path):
            deleted_count += 1
        else:
            failed_count += 1
        print()
    
    # Summary
    print("=" * 60)
    print("CLEANUP SUMMARY")
    print("=" * 60)
    print(f"✅ Successfully deleted: {deleted_count} files")
    if failed_count > 0:
        print(f"❌ Failed to delete: {failed_count} files")
    else:
        print("🎉 Audio folder is now completely clean!")
    print("=" * 60)

if __name__ == "__main__":
    try:
        cleanup_audio_folder()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        input("\nPress Enter to exit...")

