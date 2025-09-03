import json
from pathlib import Path
from datetime import datetime
import requests
import os

class WebhookUploader:
    def __init__(self, webhook_url, credentials, icon=None):
        self.webhook_url = webhook_url
        self.credentials = credentials
        self.icon = icon

    def upload_file(self, recording_file, force_delete_callback=None):
        try:
            file_info = Path(recording_file)
            file_size = file_info.stat().st_size
            print(f"📤 Uploading: {file_info.name} ({file_size / (1024 * 1024):.2f} MB)")
            metadata = {
                "event": "tray_recording",
                "timestamp": datetime.now().isoformat(),
                "file": {
                    "name": file_info.name,
                    "path": str(recording_file),
                    "size_bytes": file_size,
                    "size_mb": round(file_size / (1024 * 1024), 2),
                    "created": datetime.fromtimestamp(file_info.stat().st_ctime).isoformat(),
                    "modified": datetime.fromtimestamp(file_info.stat().st_mtime).isoformat()
                },
                "source": "tray_recorder"
            }
            username = self.credentials.get("username", "")
            password = self.credentials.get("password", "")
            with open(recording_file, 'rb') as f:
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
                if force_delete_callback:
                    if force_delete_callback(recording_file):
                        if self.icon:
                            self.icon.notify("Upload Complete", f"File uploaded and deleted: {file_info.name}")
                    else:
                        print(f"⚠ Could not delete file: {recording_file}")
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

