import os
import subprocess
import time
from datetime import datetime
from pathlib import Path
import psutil
import keyboard

class Recorder:
    def __init__(self, audio_folder, icon=None):
        self.recording = False
        self.ffmpeg_process = None
        self.recording_file = None
        self.audio_folder = Path(audio_folder)
        self.audio_folder.mkdir(parents=True, exist_ok=True)
        self.icon = icon

    def force_delete_file(self, file_path):
        if not os.path.exists(file_path):
            print(f"✓ File doesn't exist: {file_path}")
            return True
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                os.remove(file_path)
                print(f"🗑️ Successfully deleted: {Path(file_path).name}")
                return True
            except PermissionError as e:
                print(f"⚠ Attempt {attempt + 1}/{max_attempts}: File is locked - {e}")
                if attempt < max_attempts - 1:
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
                            time.sleep(1)
                        else:
                            print("⚠ No processes found using the file")
                    except Exception as kill_error:
                        print(f"⚠ Error finding/killing processes: {kill_error}")
                        time.sleep(2)
                else:
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

    def generate_filename(self):
        now = datetime.now()
        timestamp = now.strftime("%Y%m%d_%H%M%S")
        filename = f"recording_{timestamp}.wav"
        return self.audio_folder / filename

    def start_recording(self):
        if self.recording:
            return
        self.recording_file = self.generate_filename()
        ffmpeg_cmd = [
            'ffmpeg',
            '-f', 'dshow',
            '-i', 'audio=Microphone (USB PnP Sound Device)',
            '-f', 'dshow',
            '-i', 'audio=CABLE Output (VB-Audio Virtual Cable)',
            '-filter_complex', 'amix=inputs=2:duration=longest',
            '-y',
            str(self.recording_file)
        ]
        try:
            self.ffmpeg_process = subprocess.Popen(
                ffmpeg_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            self.recording = True
            print(f"✓ Recording started: {self.recording_file.name}")
            if self.icon:
                self.icon.notify("Recording Started", f"Saving to: {self.recording_file.name}")
        except Exception as e:
            print(f"❌ Failed to start recording: {e}")
            if self.icon:
                self.icon.notify("Recording Failed", str(e))

    def stop_recording(self):
        if not self.recording:
            return
        self.recording = False
        if self.ffmpeg_process:
            try:
                self.ffmpeg_process.terminate()
                try:
                    self.ffmpeg_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self.ffmpeg_process.kill()
                    self.ffmpeg_process.wait()
                print("✓ Recording stopped")
            except Exception as e:
                print(f"Error stopping FFmpeg: {e}")

    def setup_hotkey(self, callback):
        try:
            keyboard.add_hotkey('ctrl+shift+r', callback)
            print("✓ Hotkey registered: Ctrl+Shift+R")
            return True
        except Exception as e:
            print(f"⚠ Could not register hotkey: {e}")
            return False

    def toggle_recording(self):
        if self.recording:
            self.stop_recording()
        else:
            self.start_recording()

