#!/usr/bin/env python3
"""
Setup Windows Startup for Meeting Recorder
Multiple methods to add the tray recorder to Windows startup
"""

import os
import sys
import shutil
import winreg
from pathlib import Path

def method1_startup_folder():
    """Method 1: Copy batch file to Windows startup folder"""
    try:
        # Get paths
        script_dir = Path(__file__).parent
        batch_file = script_dir / "start-tray-recorder.bat"
        
        # Get Windows startup folder
        startup_folder = Path(os.environ['APPDATA']) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
        startup_batch = startup_folder / "start-tray-recorder.bat"
        
        # Copy batch file to startup folder
        shutil.copy2(batch_file, startup_batch)
        
        print("✅ Method 1: Batch file copied to startup folder")
        print(f"   Location: {startup_batch}")
        print("   Meeting Recorder will start with Windows")
        
        return True
        
    except Exception as e:
        print(f"❌ Method 1 failed: {e}")
        return False

def method2_registry():
    """Method 2: Add to Windows registry startup"""
    try:
        # Get paths
        script_dir = Path(__file__).parent
        batch_file = script_dir / "start-tray-recorder.bat"
        
        # Registry key for startup programs
        reg_key = winreg.HKEY_CURRENT_USER
        reg_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        
        # Open registry key
        with winreg.OpenKey(reg_key, reg_path, 0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, "MeetingRecorder", 0, winreg.REG_SZ, str(batch_file))
        
        print("✅ Method 2: Added to Windows registry startup")
        print(f"   Registry: HKCU\\{reg_path}")
        print(f"   Command: {batch_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ Method 2 failed: {e}")
        return False

def method3_shortcut():
    """Method 3: Create shortcut in startup folder (requires additional packages)"""
    try:
        import winshell
        from win32com.client import Dispatch
        
        # Get paths
        script_dir = Path(__file__).parent
        batch_file = script_dir / "start-tray-recorder.bat"
        
        # Get startup folder
        startup_folder = winshell.startup()
        shortcut_path = os.path.join(startup_folder, "Meeting Recorder.lnk")
        
        # Create shortcut
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.Targetpath = str(batch_file)
        shortcut.Arguments = ""
        shortcut.WorkingDirectory = str(script_dir)
        shortcut.IconLocation = sys.executable
        shortcut.Description = "Meeting Recorder - System Tray (Ctrl+Shift+R)"
        shortcut.save()
        
        print("✅ Method 3: Shortcut created in startup folder")
        print(f"   Location: {shortcut_path}")
        
        return True
        
    except ImportError:
        print("❌ Method 3 failed: Missing packages (winshell, pywin32)")
        print("   Install with: pip install winshell pywin32")
        return False
    except Exception as e:
        print(f"❌ Method 3 failed: {e}")
        return False

def remove_startup():
    """Remove from all startup methods"""
    removed_any = False
    
    # Remove from startup folder (batch file)
    try:
        startup_folder = Path(os.environ['APPDATA']) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
        startup_batch = startup_folder / "start-tray-recorder.bat"
        if startup_batch.exists():
            startup_batch.unlink()
            print("✅ Removed batch file from startup folder")
            removed_any = True
    except Exception as e:
        print(f"⚠ Could not remove from startup folder: {e}")
    
    # Remove from registry
    try:
        reg_key = winreg.HKEY_CURRENT_USER
        reg_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        with winreg.OpenKey(reg_key, reg_path, 0, winreg.KEY_SET_VALUE) as key:
            winreg.DeleteValue(key, "MeetingRecorder")
        print("✅ Removed from Windows registry")
        removed_any = True
    except FileNotFoundError:
        pass  # Value doesn't exist
    except Exception as e:
        print(f"⚠ Could not remove from registry: {e}")
    
    # Remove shortcut
    try:
        import winshell
        startup_folder = winshell.startup()
        shortcut_path = os.path.join(startup_folder, "Meeting Recorder.lnk")
        if os.path.exists(shortcut_path):
            os.remove(shortcut_path)
            print("✅ Removed shortcut from startup folder")
            removed_any = True
    except ImportError:
        pass  # winshell not available
    except Exception as e:
        print(f"⚠ Could not remove shortcut: {e}")
    
    if not removed_any:
        print("ℹ️  No startup entries found to remove")

def main():
    """Main function"""
    print("=" * 60)
    print("Meeting Recorder - Windows Startup Setup")
    print("=" * 60)
    print()
    
    # Check if batch file exists
    script_dir = Path(__file__).parent
    batch_file = script_dir / "start-tray-recorder.bat"
    
    if not batch_file.exists():
        print(f"❌ Batch file not found: {batch_file}")
        input("Press Enter to exit...")
        return
    
    print(f"Batch file found: {batch_file}")
    print()
    
    print("Choose an option:")
    print("1. Add to startup (Method 1: Copy to startup folder) - RECOMMENDED")
    print("2. Add to startup (Method 2: Windows registry)")
    print("3. Add to startup (Method 3: Create shortcut)")
    print("4. Try all methods")
    print("5. Remove from startup (all methods)")
    print("6. Exit")
    print()
    
    choice = input("Enter choice (1-6): ").strip()
    print()
    
    if choice == "1":
        method1_startup_folder()
    elif choice == "2":
        method2_registry()
    elif choice == "3":
        method3_shortcut()
    elif choice == "4":
        print("Trying all methods...")
        print()
        success_count = 0
        if method1_startup_folder():
            success_count += 1
        print()
        if method2_registry():
            success_count += 1
        print()
        if method3_shortcut():
            success_count += 1
        print()
        print(f"✅ {success_count}/3 methods succeeded")
    elif choice == "5":
        print("Removing from startup...")
        print()
        remove_startup()
    elif choice == "6":
        print("Exiting...")
        return
    else:
        print("Invalid choice")
    
    print()
    print("=" * 60)
    print("INSTRUCTIONS:")
    print("- The Meeting Recorder will now start automatically with Windows")
    print("- Look for the microphone icon in your system tray")
    print("- Use Ctrl+Shift+R hotkey to start/stop recording")
    print("- Right-click the tray icon for menu options")
    print("=" * 60)
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
