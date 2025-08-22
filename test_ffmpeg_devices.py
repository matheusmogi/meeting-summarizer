#!/usr/bin/env python3
"""
Test FFmpeg Audio Device Detection
"""

import subprocess

def test_ffmpeg_and_devices():
    """Test FFmpeg and list audio devices"""
    
    print("=" * 60)
    print("FFmpeg Device Test")
    print("=" * 60)
    
    # Test FFmpeg
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✓ FFmpeg is working")
        else:
            print("❌ FFmpeg not working properly")
            return False
    except FileNotFoundError:
        print("❌ FFmpeg not found")
        return False
    except Exception as e:
        print(f"❌ Error testing FFmpeg: {e}")
        return False
    
    print("")
    
    # List audio devices
    try:
        print("🎤 Detecting DirectShow audio devices...")
        result = subprocess.run([
            'ffmpeg', '-f', 'dshow', '-list_devices', 'true', '-i', 'dummy'
        ], capture_output=True, text=True, timeout=10)
        
        output = result.stderr
        print("")
        print("Raw FFmpeg output:")
        print("-" * 40)
        print(output)
        print("-" * 40)
        print("")
        
        print("Audio devices found:")
        lines = output.split('\n')
        audio_devices = []
        
        for line in lines:
            if 'DirectShow audio devices' in line:
                print("📋 DirectShow Audio Devices:")
                continue
            if '] "' in line and 'audio' in line.lower():
                # Extract device name
                start = line.find('"') + 1
                end = line.rfind('"')
                if start > 0 and end > start:
                    device_name = line[start:end]
                    audio_devices.append(device_name)
                    print(f"   • {device_name}")
        
        print("")
        print("Device Analysis:")
        print("-" * 40)
        
        # Check for required devices
        usb_mic_found = False
        cable_found = False
        
        for device in audio_devices:
            if 'usb' in device.lower() and 'microphone' in device.lower():
                print(f"✓ USB Microphone found: {device}")
                usb_mic_found = True
            elif 'cable' in device.lower() and 'output' in device.lower():
                print(f"✓ VB-Audio Cable found: {device}")
                cable_found = True
        
        if not usb_mic_found:
            print("⚠ USB Microphone not found")
            print("  Looking for: 'Microphone (USB PnP Sound Device)'")
        
        if not cable_found:
            print("⚠ VB-Audio Cable Output not found")
            print("  Looking for: 'CABLE Output (VB-Audio Virtual Cable)'")
            print("  Please install VB-Audio Virtual Cable")
        
        if usb_mic_found and cable_found:
            print("")
            print("✅ All required devices found!")
            print("   Ready for FFmpeg recording")
        else:
            print("")
            print("❌ Some required devices missing")
            print("   Please check device names and VB-Audio installation")
        
        return True
        
    except Exception as e:
        print(f"❌ Error listing devices: {e}")
        return False

if __name__ == "__main__":
    test_ffmpeg_and_devices()
    input("\nPress Enter to exit...")
