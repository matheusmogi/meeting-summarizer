# Meeting Recorder - Complete Solution

## 🎯 **Overview**

Professional audio recording system that captures **microphone + system audio** simultaneously using FFmpeg, automatically uploads to N8N webhook with authentication, and deletes files after successful upload.

## 📁 **File Structure**

```
meeting-recorder/
├── 📄 config.example.json             # Configuration template
├── 🎙️ tray_recorder.py                # System tray application ⭐
├── 🚀 start-tray-recorder.bat         # Tray launcher
├── 📚 TRAY_RECORDER_GUIDE.md          # System tray recorder guide
└── 📁 audio/                          # Output folder for recordings
```

## 🚀 **Quick Start**

### **System Tray Application** ⭐
```cmd
start-tray-recorder.bat
```
- **Microphone icon** in system tray
- **Hotkey:** Ctrl+F12 (or Ctrl+Fn+F12) to start/stop
- **Right-click** tray icon for menu options
- **Auto-upload** and delete after recording
- **All-in-one solution** - no need for separate utilities

## ⚙️ **Configuration**

1. **Copy the example config:**
   ```cmd
   copy config.example.json config.json
   ```

2. **Edit `config.json`:**
   ```json
   {
       "n8n_webhook_url": "https://n8n.mreis.uk/webhook/your-webhook-id",
       "watch_folder": "D:\\study\\AI\\meeting-recorder\\audio",
       "credentials": {
           "username": "your-username",
           "password": "your-password"
       }
   }
   ```

⚠️ **Important**: Never commit `config.json` to version control as it contains sensitive credentials!

## 🎵 **Audio Setup**

### **Requirements:**
- ✅ **FFmpeg**: Installed and in PATH
- ✅ **VB-Audio Virtual Cable**: For system audio capture
- ✅ **USB Microphone**: `Microphone (USB PnP Sound Device)`

### **Test Your Setup:**
```cmd
python test_ffmpeg_devices.py
```

## 📋 **How It Works**

### **FFmpeg Recording:**
```cmd
ffmpeg -f dshow 
  -i audio="Microphone (USB PnP Sound Device)" 
  -f dshow 
  -i audio="CABLE Output (VB-Audio Virtual Cable)" 
  -filter_complex "amix=inputs=2:duration=longest" 
  recording_YYYYMMDD_HHMMSS.wav
```

### **Workflow:**
1. **Record** → Both microphone and system audio mixed
2. **Stop** → Ctrl+C stops recording gracefully  
3. **Upload** → Automatic POST to N8N webhook with auth
4. **Delete** → File removed after successful upload
5. **Clean** → Audio folder stays organized

## 🔔 **N8N Webhook Integration**

**HTTP POST with Multipart Form Data:**
- `data` field: Binary WAV file
- `metadata` field: JSON with file info and timestamps
- **Authentication**: Basic Auth from config.json

## 🛠️ **Main Application**

| File | Purpose | Usage |
|------|---------|-------|
| `start-tray-recorder.bat` | **System tray app** ⭐ | Complete recording solution with hotkey |
| `tray_recorder.py` | **Core application** | Python script (launched by batch file) |

## ✅ **Features**

- ✅ **System Tray Integration**: Always-on with hotkey access
- ✅ **Global Hotkey**: Ctrl+F12 (Ctrl+Fn+F12) start/stop anywhere
- ✅ **Visual Feedback**: Tray icon changes during recording
- ✅ **Professional Quality**: FFmpeg audio mixing
- ✅ **Dual Audio Capture**: Microphone + system audio
- ✅ **Automatic Upload**: N8N webhook with authentication
- ✅ **Auto-delete**: Clean folder management
- ✅ **Manual Send**: Upload existing files
- ✅ **Error Handling**: Graceful failures, files preserved
- ✅ **Notifications**: System notifications for status updates
- ✅ **No Dependencies**: Just FFmpeg + VB-Audio Cable

## 🎯 **Perfect For**

- **Meeting Recording**: Capture conversation + screen audio
- **Tutorial Creation**: Record voice + application sounds  
- **Call Recording**: Get both sides of audio calls
- **Content Creation**: Professional multi-source recording

## 📖 **Detailed Documentation**

- **System Tray Recorder**: See `TRAY_RECORDER_GUIDE.md`

---

## 🚀 **Installation & Setup**

### **Prerequisites**
1. **FFmpeg**: [Download and install FFmpeg](https://ffmpeg.org/download.html)
2. **VB-Audio Virtual Cable**: [Download VB-Cable](https://vb-audio.com/Cable/)
3. **Python 3.7+**: [Download Python](https://python.org/downloads/)

### **Quick Setup**
1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/meeting-recorder.git
   cd meeting-recorder
   ```

2. **Install Python dependencies:**
   ```bash
   pip install requests keyboard pystray pillow plyer
   ```

3. **Configure the application:**
   ```cmd
   copy config.example.json config.json
   # Edit config.json with your N8N webhook URL and credentials
   ```

4. **Start recording:**
   ```cmd
   start-tray-recorder.bat
   ```

## 📦 **Dependencies**

- `requests` - HTTP requests for webhook uploads
- `keyboard` - Global hotkey support  
- `pystray` - System tray integration
- `pillow` - Image processing for tray icons
- `plyer` - Cross-platform notifications

Install all at once:
```bash
pip install requests keyboard pystray pillow plyer
```

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -am 'Add feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Ready to record professional-quality audio with automatic cloud upload!** 🎵✨
