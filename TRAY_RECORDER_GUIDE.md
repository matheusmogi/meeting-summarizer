# System Tray Recorder - User Guide

## 🎯 **Overview**

The **System Tray Recorder** is the most convenient way to use the Meeting Recorder. It runs in the background with a microphone icon in your system tray and responds to the global hotkey **Ctrl+F12**.

## 🚀 **Quick Start**

### **Launch the Tray App:**
```cmd
start-tray-recorder.bat
```

### **What You'll See:**
- 🎤 **Blue microphone icon** appears in system tray
- **Console window** shows status (can be minimized)
- **Ready for recording** with hotkey

## ⌨️ **Hotkey Usage**

### **Global Hotkey: Ctrl+F12**
- **Press once** → Start recording
- **Press again** → Stop recording and upload

**Note:** On some laptops, use **Ctrl+Fn+F12**

### **Visual Feedback:**
- 🔵 **Blue microphone** = Ready/Idle
- 🔴 **Red recording dot** = Currently recording

## 🖱️ **Right-Click Menu**

Right-click the tray icon for options:

| Menu Item | Description |
|-----------|-------------|
| **Start Recording** | Begin new recording |
| **Stop Recording** | End current recording |
| **Send Files Manually** | Open manual file sender |
| **Test Audio Devices** | Check FFmpeg setup |
| **Open Audio Folder** | Browse output directory |
| **Status: Ready/Recording** | Current status |
| **Exit** | Close the application |

## 🔔 **Notifications**

The app shows Windows notifications for:
- ✅ **Recording Started**: Shows filename
- ✅ **Upload Complete**: File uploaded and deleted
- ❌ **Upload Failed**: Error occurred
- ❌ **Recording Failed**: Could not start

## 🎵 **Recording Workflow**

1. **Press Ctrl+F12** → Recording starts
   - Tray icon turns red with recording dot
   - Notification shows "Recording Started"
   - Audio saved to timestamped WAV file

2. **Press Ctrl+F12 again** → Recording stops
   - Tray icon changes to "Uploading..." status
   - File automatically uploaded to N8N webhook
   - File deleted after successful upload
   - Notification shows "Upload Complete"

## ⚙️ **Configuration**

Uses the same `config.json` as other tools:
```json
{
    "n8n_webhook_url": "https://n8n.mreis.uk/webhook/your-id",
    "watch_folder": "D:\\study\\AI\\meeting-recorder\\audio",
    "credentials": {
        "username": "your-username",
        "password": "your-password"
    }
}
```

## 🔄 **Windows Startup**

To start the tray recorder automatically with Windows:

1. **Run:** `python create_startup_shortcut.py`
2. **Choose option 1** to create startup shortcut
3. **Restart Windows** to test

The tray recorder will now start automatically and be ready for hotkey recording.

## 🛠️ **Troubleshooting**

### **Hotkey Not Working**
- Try **Ctrl+Fn+F12** on laptops
- Check if another app uses the same hotkey
- Restart the tray application

### **Icon Not Visible**
- Check Windows system tray settings
- Look in the "hidden icons" area
- Make sure app is running (check console)

### **Recording Fails**
- **Right-click** tray icon → **Test Audio Devices**
- Verify FFmpeg and VB-Audio Cable setup
- Check console window for error messages

### **Upload Fails**
- Check internet connection
- Verify N8N webhook URL and credentials
- File remains in audio folder for manual upload

## ✨ **Advantages**

- ✅ **Always Available**: Global hotkey works anywhere
- ✅ **Minimal Interface**: Just a tray icon
- ✅ **Visual Feedback**: Icon shows recording status
- ✅ **Background Operation**: Doesn't interrupt workflow
- ✅ **Auto-Upload**: Hands-free file management
- ✅ **Notifications**: Clear status updates

## 🎯 **Perfect For**

- **Frequent Recording**: Always ready with hotkey
- **Meeting Participants**: Quick start during calls
- **Content Creators**: Instant recording access
- **Productivity Users**: Minimal disruption workflow

---

**The most convenient way to record professional audio!** 🎵✨
