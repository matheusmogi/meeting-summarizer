#!/usr/bin/env python3
"""
Audio Sender - Batch processor for sending audio files to n8n webhook

This script scans a target folder for audio files and sends them to n8n for processing.
It uses the existing WebhookUploader class for consistent file upload functionality.
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import List, Optional
import time

from webhook import WebhookUploader
from config import load_config


class AudioSender:
    """Handles batch sending of audio files to n8n webhook"""
    
    SUPPORTED_AUDIO_FORMATS = {'.wav', '.mp3', '.m4a', '.aac', '.flac', '.ogg', '.wma'}
    
    def __init__(self, webhook_url: str, credentials: dict, target_folder: str):
        """
        Initialize AudioSender
        
        Args:
            webhook_url: n8n webhook URL
            credentials: Authentication credentials dict
            target_folder: Path to folder containing audio files
        """
        self.webhook_url = webhook_url
        self.credentials = credentials
        self.target_folder = Path(target_folder)
        self.uploader = WebhookUploader(webhook_url, credentials)
        
        if not self.target_folder.exists():
            raise FileNotFoundError(f"Target folder does not exist: {target_folder}")
        
        if not self.target_folder.is_dir():
            raise NotADirectoryError(f"Target path is not a directory: {target_folder}")
    
    def find_audio_files(self, recursive: bool = False) -> List[Path]:
        """
        Find all audio files in the target folder
        
        Args:
            recursive: Whether to search subdirectories recursively
            
        Returns:
            List of Path objects for audio files
        """
        audio_files = []
        
        if recursive:
            # Search recursively using glob pattern
            for ext in self.SUPPORTED_AUDIO_FORMATS:
                pattern = f"**/*{ext}"
                audio_files.extend(self.target_folder.glob(pattern))
        else:
            # Search only in the target directory
            for file_path in self.target_folder.iterdir():
                if file_path.is_file() and file_path.suffix.lower() in self.SUPPORTED_AUDIO_FORMATS:
                    audio_files.append(file_path)
        
        # Sort by modification time (oldest first)
        audio_files.sort(key=lambda x: x.stat().st_mtime)
        
        return audio_files
    
    def send_audio_file(self, file_path: Path, delete_after_upload: bool = False) -> bool:
        """
        Send a single audio file to n8n
        
        Args:
            file_path: Path to the audio file
            delete_after_upload: Whether to delete file after successful upload
            
        Returns:
            True if upload was successful, False otherwise
        """
        try:
            print(f"\n📁 Processing: {file_path.name}")
            
            # Use existing webhook uploader
            if delete_after_upload:
                def delete_callback(file_to_delete):
                    try:
                        os.remove(file_to_delete)
                        print(f"🗑️  Deleted: {Path(file_to_delete).name}")
                        return True
                    except Exception as e:
                        print(f"❌ Failed to delete {Path(file_to_delete).name}: {e}")
                        return False
                
                self.uploader.upload_file(str(file_path), delete_callback)
            else:
                self.uploader.upload_file(str(file_path))
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to process {file_path.name}: {e}")
            return False
    
    def send_all_files(self, recursive: bool = False, delete_after_upload: bool = False, 
                       delay_between_uploads: float = 0, auto_confirm: bool = False) -> dict:
        """
        Send all audio files in the target folder to n8n
        
        Args:
            recursive: Whether to search subdirectories recursively
            delete_after_upload: Whether to delete files after successful upload
            delay_between_uploads: Seconds to wait between uploads (to avoid overwhelming n8n)
            auto_confirm: Skip user confirmation prompt (useful for tray integration)
            
        Returns:
            Dictionary with success/failure statistics
        """
        print(f"🔍 Scanning for audio files in: {self.target_folder}")
        print(f"📂 Recursive search: {'Yes' if recursive else 'No'}")
        print(f"🗑️  Delete after upload: {'Yes' if delete_after_upload else 'No'}")
        print(f"⏱️  Delay between uploads: {delay_between_uploads}s")
        
        audio_files = self.find_audio_files(recursive)
        
        if not audio_files:
            print("📭 No audio files found in the target folder")
            return {"total": 0, "successful": 0, "failed": 0, "files": []}
        
        print(f"\n📊 Found {len(audio_files)} audio file(s)")
        
        # Show file list
        for i, file_path in enumerate(audio_files, 1):
            file_size = file_path.stat().st_size / (1024 * 1024)  # MB
            print(f"  {i}. {file_path.name} ({file_size:.2f} MB)")
        
        # Confirm before proceeding (skip if auto_confirm is True)
        if len(audio_files) > 1 and not auto_confirm:
            response = input(f"\n❓ Proceed with uploading {len(audio_files)} files? (y/n): ").lower().strip()
            if response != 'y' and response != 'yes':
                print("🚫 Upload cancelled by user")
                return {"total": len(audio_files), "successful": 0, "failed": 0, "files": []}
        
        # Process files
        results = {"total": len(audio_files), "successful": 0, "failed": 0, "files": []}
        
        for i, file_path in enumerate(audio_files, 1):
            print(f"\n📋 Progress: {i}/{len(audio_files)}")
            
            success = self.send_audio_file(file_path, delete_after_upload)
            
            file_result = {
                "filename": file_path.name,
                "path": str(file_path),
                "success": success
            }
            results["files"].append(file_result)
            
            if success:
                results["successful"] += 1
            else:
                results["failed"] += 1
            
            # Add delay between uploads if specified
            if delay_between_uploads > 0 and i < len(audio_files):
                print(f"⏳ Waiting {delay_between_uploads}s before next upload...")
                time.sleep(delay_between_uploads)
        
        # Print summary
        print(f"\n📊 Upload Summary:")
        print(f"  ✅ Successful: {results['successful']}")
        print(f"  ❌ Failed: {results['failed']}")
        print(f"  📁 Total: {results['total']}")
        
        return results


def main():
    """Main entry point for the audio sender script"""
    parser = argparse.ArgumentParser(
        description="Send audio files from a folder to n8n webhook for processing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python audio_sender.py                           # Send files from config folder
  python audio_sender.py --folder ./recordings     # Send from specific folder
  python audio_sender.py --recursive               # Include subdirectories
  python audio_sender.py --delete                  # Delete after upload
  python audio_sender.py --delay 2                 # Wait 2s between uploads
        """
    )
    
    parser.add_argument(
        '--folder', '-f',
        type=str,
        help='Target folder containing audio files (default: from config)'
    )
    
    parser.add_argument(
        '--recursive', '-r',
        action='store_true',
        help='Search subdirectories recursively'
    )
    
    parser.add_argument(
        '--delete', '-d',
        action='store_true',
        help='Delete files after successful upload'
    )
    
    parser.add_argument(
        '--delay',
        type=float,
        default=0,
        help='Seconds to wait between uploads (default: 0)'
    )
    
    parser.add_argument(
        '--config', '-c',
        type=str,
        help='Path to config file (default: config.json)'
    )
    
    args = parser.parse_args()
    
    try:
        # Load configuration
        if args.config:
            config_path = Path(args.config)
            if not config_path.exists():
                print(f"❌ Config file not found: {args.config}")
                return 1
            with open(config_path, 'r') as f:
                config = json.load(f)
        else:
            config = load_config()
        
        if not config:
            print("❌ Failed to load configuration")
            print("💡 Make sure config.json exists and contains:")
            print("   - n8n_webhook_url")
            print("   - credentials (username/password)")
            print("   - watch_folder (if not using --folder)")
            return 1
        
        # Get configuration values
        webhook_url = config.get('n8n_webhook_url')
        credentials = config.get('credentials', {})
        
        if not webhook_url:
            print("❌ n8n_webhook_url not found in configuration")
            return 1
        
        # Determine target folder
        target_folder = args.folder
        if not target_folder:
            target_folder = config.get('watch_folder')
            if not target_folder:
                print("❌ No target folder specified and watch_folder not found in config")
                print("💡 Use --folder argument or add watch_folder to config.json")
                return 1
        
        print(f"🚀 Audio Sender starting...")
        print(f"🔗 Webhook URL: {webhook_url}")
        print(f"📁 Target folder: {target_folder}")
        
        # Create and run audio sender
        sender = AudioSender(webhook_url, credentials, target_folder)
        results = sender.send_all_files(
            recursive=args.recursive,
            delete_after_upload=args.delete,
            delay_between_uploads=args.delay
        )
        
        # Return appropriate exit code
        if results['failed'] > 0:
            return 1  # Some failures occurred
        elif results['successful'] == 0:
            return 0  # No files to process (not an error)
        else:
            return 0  # All successful
    
    except KeyboardInterrupt:
        print("\n🚫 Upload cancelled by user")
        return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
