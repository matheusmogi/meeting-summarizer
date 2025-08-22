#!/usr/bin/env python3
"""
Create Windows Startup Shortcut for Meeting Recorder
Adds the tray recorder to Windows startup folder
"""

import os
import sys
from pathlib import Path
import winshell
from win32com.client import Dispatch

def create_startup_shortcut():
    """Create a shortcut in Windows startup folder"""
    try:
        # Get paths
        script_dir = Path(__file__).parent
        batch_file = script_dir / "start-tray-recorder.bat"
        
        # Get startup folder
        startup_folder = winshell.startup()
        shortcut_path = os.path.join(startup_folder, "Meeting Recorder.lnk")
        
        # Create shortcut
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.Targetpath = str(batch_file)  # Batch file
        shortcut.Arguments = ""
        shortcut.WorkingDirectory = str(script_dir)
        shortcut.IconLocation = sys.executable  # Use Python icon
        shortcut.Description = "Meeting Recorder - System Tray (Ctrl+Shift+R)"
        shortcut.save()
        
        print("✅ Startup shortcut created successfully!")
        print(f"   Location: {shortcut_path}")
        print("   Meeting Recorder will now start with Windows")
        
        return True
        
    except ImportError:
        print("❌ Missing required packages")
        print("   Please install: pip install winshell pywin32")
        return False
    except Exception as e:
        print(f"❌ Error creating shortcut: {e}")
        return False

def remove_startup_shortcut():
    """Remove the startup shortcut"""
    try:
        startup_folder = winshell.startup()
        shortcut_path = os.path.join(startup_folder, "Meeting Recorder.lnk")
        
        if os.path.exists(shortcut_path):
            os.remove(shortcut_path)
            print("✅ Startup shortcut removed successfully!")
        else:
            print("ℹ️  No startup shortcut found")
        
        return True
        
    except Exception as e:
        print(f"❌ Error removing shortcut: {e}")
        return False

def main():
    """Main function"""
    print("=" * 50)
    print("Meeting Recorder - Startup Shortcut Creator")
    print("=" * 50)
    print()
    
    print("What would you like to do?")
    print("1. Create startup shortcut (start with Windows)")
    print("2. Remove startup shortcut")
    print("3. Exit")
    print()
    
    choice = input("Enter choice (1-3): ").strip()
    
    if choice == "1":
        create_startup_shortcut()
    elif choice == "2":
        remove_startup_shortcut()
    elif choice == "3":
        print("Exiting...")
    else:
        print("Invalid choice")
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
