#!/usr/bin/env python3
"""
Meeting Recorder - System Tray Application
System tray icon with Ctrl+Shift+R hotkey for quick recording control
"""

from config import load_config
from recorder import Recorder
from tray_icon import TrayIcon
from webhook import WebhookUploader
import threading
import os
import time

def main():
    config = load_config()
    webhook_url = config.get("n8n_webhook_url")
    credentials = config.get("credentials", {})
    audio_folder = config.get("watch_folder", "D:\\study\\AI\\meeting-recorder\\audio")

    recorder = Recorder(audio_folder)
    uploader = WebhookUploader(webhook_url, credentials)

    def on_start(icon=None, item=None):
        recorder.start_recording()
        tray.update_icon_status(True)

    def on_stop(icon=None, item=None):
        recorder.stop_recording()
        tray.update_icon_status(False)
        # Upload in background if file exists and is large enough
        if recorder.recording_file and os.path.exists(recorder.recording_file):
            file_size = os.path.getsize(recorder.recording_file)
            if file_size > 1024:
                threading.Thread(target=lambda: uploader.upload_file(recorder.recording_file, recorder.force_delete_file), daemon=True).start()

    def on_test(icon=None, item=None):
        tray.notify("Audio Test", "Device testing feature was removed for simplicity")

    def on_open(icon=None, item=None):
        try:
            os.startfile(str(recorder.audio_folder))
        except Exception as e:
            print(f"Error opening folder: {e}")

    def on_exit(icon=None, item=None):
        if recorder.recording:
            recorder.stop_recording()
            time.sleep(2)
        tray.stop()

    tray = TrayIcon(
        recorder=recorder,
        on_start=on_start,
        on_stop=on_stop,
        on_test=on_test,
        on_open=on_open,
        on_exit=on_exit
    )
    recorder.icon = tray
    uploader.icon = tray
    recorder.setup_hotkey(tray.recorder.toggle_recording)
    tray.run()

if __name__ == "__main__":
    main()
