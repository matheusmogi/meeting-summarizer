#!/usr/bin/env python3
"""
Manual File Sender for N8N Webhook
Send WAV files manually to the webhook without waiting for automatic monitoring
"""

import json
import requests
import os
import sys
import glob
from datetime import datetime
from pathlib import Path

class ManualFileSender:
    def __init__(self, config_file="config.json"):
        # Load configuration
        self.config = self.load_config(config_file)
        self.webhook_url = self.config.get("n8n_webhook_url")
        self.credentials = self.config.get("credentials", {})
        
    def load_config(self, config_file):
        """Load configuration from JSON file"""
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            return config
        except Exception as e:
            print(f"❌ Error loading config: {e}")
            return {}
    
    def send_file(self, file_path):
        """Send a single WAV file to the webhook"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            print(f"❌ File not found: {file_path}")
            return False
            
        file_size = file_path.stat().st_size
        
        print(f"📤 Sending file: {file_path.name}")
        print(f"   Size: {file_size / (1024 * 1024):.2f} MB")
        print(f"   Path: {file_path}")
        
        # Prepare metadata
        metadata = {
            "event": "manual_upload",
            "timestamp": datetime.now().isoformat(),
            "file": {
                "name": file_path.name,
                "path": str(file_path),
                "size_bytes": file_size,
                "size_mb": round(file_size / (1024 * 1024), 2),
                "created": datetime.fromtimestamp(file_path.stat().st_ctime).isoformat(),
                "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
            },
            "source": "manual_file_sender"
        }
        
        try:
            # Get credentials
            username = self.credentials.get("username", "")
            password = self.credentials.get("password", "")
            
            # Prepare multipart form data
            with open(file_path, 'rb') as f:
                files = {
                    'data': (file_path.name, f, 'audio/wav'),
                    'metadata': (None, json.dumps(metadata), 'application/json')
                }
                
                # Setup basic authentication
                auth = None
                if username and password:
                    auth = (username, password)
                    print(f"   Using auth: {username}")
                else:
                    print("   No authentication configured")
                
                print(f"   Posting to: {self.webhook_url}")
                
                response = requests.post(
                    self.webhook_url,
                    files=files,
                    auth=auth,
                    timeout=30
                )
            
            print(f"   Response: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ File sent successfully!")
                
                # Delete the file after successful upload
                try:
                    os.remove(file_path)
                    print(f"🗑️ Deleted file after successful upload: {file_path.name}")
                except Exception as delete_error:
                    print(f"⚠ Could not delete file: {delete_error}")
                    print(f"   File remains at: {file_path}")
                
                return True
            elif response.status_code == 403:
                print("❌ Authentication failed - check credentials")
                print(f"   Current user: {username}")
                print("   File NOT deleted (upload failed)")
            else:
                print(f"⚠ Server responded with status: {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                print("   File NOT deleted (upload failed)")
            
            return False
            
        except requests.RequestException as e:
            print(f"❌ Network error: {e}")
            print("   File NOT deleted (upload failed)")
            return False
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            print("   File NOT deleted (upload failed)")
            return False
    
    def send_multiple_files(self, file_patterns):
        """Send multiple files matching patterns"""
        all_files = []
        
        # Collect all matching files
        for pattern in file_patterns:
            matching_files = glob.glob(pattern)
            all_files.extend(matching_files)
        
        # Remove duplicates and sort
        all_files = sorted(list(set(all_files)))
        
        if not all_files:
            print("❌ No files found matching the patterns")
            return False
        
        print(f"📁 Found {len(all_files)} files to send:")
        for i, file_path in enumerate(all_files, 1):
            file_size = os.path.getsize(file_path) / (1024 * 1024)
            print(f"   {i}. {Path(file_path).name} ({file_size:.2f} MB)")
        
        print("")
        
        # Send each file
        success_count = 0
        for i, file_path in enumerate(all_files, 1):
            print(f"[{i}/{len(all_files)}] ", end="")
            if self.send_file(file_path):
                success_count += 1
            print("")
        
        print(f"📊 Results: {success_count}/{len(all_files)} files sent successfully")
        return success_count == len(all_files)
    
    def list_available_files(self, directory="audio"):
        """List available WAV files in the directory"""
        directory = Path(directory)
        
        if not directory.exists():
            print(f"❌ Directory not found: {directory}")
            return []
        
        wav_files = list(directory.glob("*.wav"))
        
        if not wav_files:
            print(f"📁 No WAV files found in: {directory}")
            return []
        
        print(f"📁 Available WAV files in {directory}:")
        for i, file_path in enumerate(wav_files, 1):
            file_size = file_path.stat().st_size / (1024 * 1024)
            modified = datetime.fromtimestamp(file_path.stat().st_mtime)
            print(f"   {i}. {file_path.name}")
            print(f"      Size: {file_size:.2f} MB")
            print(f"      Modified: {modified.strftime('%Y-%m-%d %H:%M:%S')}")
            print("")
        
        return wav_files

def main():
    """Main function with interactive menu"""
    sender = ManualFileSender()
    
    if not sender.webhook_url:
        print("❌ No webhook URL configured in config.json")
        sys.exit(1)
    
    print("=" * 60)
    print("Manual File Sender for N8N Webhook")
    print("=" * 60)
    print(f"Webhook: {sender.webhook_url}")
    print(f"Auth User: {sender.credentials.get('username', 'Not configured')}")
    print("")
    
    if len(sys.argv) > 1:
        # Command line mode
        file_patterns = sys.argv[1:]
        print(f"📤 Sending files: {file_patterns}")
        sender.send_multiple_files(file_patterns)
    else:
        # Interactive mode
        while True:
            print("What would you like to do?")
            print("")
            print("1. List available WAV files")
            print("2. Send a specific file")
            print("3. Send all files in audio folder")
            print("4. Send files matching pattern")
            print("5. Test webhook connection")
            print("Q. Quit")
            print("")
            
            choice = input("Enter your choice: ").strip().upper()
            print("")
            
            if choice == "1":
                sender.list_available_files()
                
            elif choice == "2":
                file_path = input("Enter file path: ").strip()
                if file_path:
                    sender.send_file(file_path)
                    
            elif choice == "3":
                sender.send_multiple_files(["audio/*.wav"])
                
            elif choice == "4":
                pattern = input("Enter file pattern (e.g., audio/*.wav): ").strip()
                if pattern:
                    sender.send_multiple_files([pattern])
                    
            elif choice == "5":
                # Test with a simple request
                try:
                    auth = (sender.credentials.get('username'), sender.credentials.get('password'))
                    response = requests.get(sender.webhook_url, auth=auth, timeout=10)
                    print(f"✅ Connection test: {response.status_code}")
                except Exception as e:
                    print(f"❌ Connection failed: {e}")
                    
            elif choice == "Q":
                break
                
            else:
                print("Invalid choice, please try again.")
                
            print("")
            input("Press Enter to continue...")
            print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nManual file sender stopped by user")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)
