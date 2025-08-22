# FFmpeg Audio Recorder - Final Solution

## 🎯 **What This Does**

Records **microphone + system audio** simultaneously using FFmpeg, then automatically uploads to your N8N webhook and deletes the file after successful upload.

**No external apps needed** - just FFmpeg + VB-Audio Virtual Cable!

## ✅ **Your System Status**

- ✅ **FFmpeg**: Working (version 7.1.1)
- ✅ **USB Microphone**: `Microphone (USB PnP Sound Device)` 
- ✅ **System Audio**: `CABLE Output (VB-Audio Virtual Cable)`
- ✅ **N8N Webhook**: Working with authentication
- ✅ **Auto-delete**: Files deleted after successful upload

## 🚀 **How to Use**

### **Start Recording:**
```cmd
start-ffmpeg-recording.bat
```

### **Or direct Python:**
```cmd
python ffmpeg_recorder.py
```

### **Stop Recording:**
- Press **Ctrl+C** in the terminal
- Recording will stop, upload to N8N, and delete the file

## 🎵 **What Happens**

1. **FFmpeg starts** recording both audio sources
2. **Records to**: `D:\study\AI\meeting-recorder\audio\recording_YYYYMMDD_HHMMSS.wav`
3. **Shows progress** every 30 seconds
4. **When you press Ctrl+C**:
   - Stops recording gracefully
   - Uploads file to N8N webhook with authentication
   - **Deletes file** after successful upload
   - Shows completion status

## 📋 **FFmpeg Command Used**

```cmd
ffmpeg -f dshow -i audio="Microphone (USB PnP Sound Device)" -f dshow -i audio="CABLE Output (VB-Audio Virtual Cable)" -filter_complex "amix=inputs=2:duration=longest" recording_YYYYMMDD_HHMMSS.wav
```

This command:
- **Records microphone** from USB device
- **Records system audio** from VB-Audio Cable
- **Mixes both sources** into one stereo file
- **Saves with timestamp** for unique filenames

## 🔧 **Configuration**

Uses the same `config.json` as before:
```json
{
    "n8n_webhook_url": "https://n8n.mreis.uk/webhook/your-webhook-id",
    "watch_folder": "D:\\study\\AI\\meeting-recorder\\audio",
    "credentials": {
        "username": "local-recorder", 
        "password": "your-password"
    }
}
```

## 📊 **Status Messages**

During recording:
- `✓ FFmpeg recording started successfully`
- `🎵 Recording... 01:30` (every 30 seconds)

When stopping:
- `🛑 Stopping recording...`
- `✓ FFmpeg stopped gracefully`
- `📤 Uploading to N8N webhook...`
- `✅ File uploaded successfully!`
- `🗑️ Deleted file after successful upload: filename.wav`

## 🎯 **Perfect Solution**

This is exactly what you wanted:
- ✅ **No external app dependencies** (just FFmpeg)
- ✅ **Records both microphone and system audio**
- ✅ **Automatic upload** to N8N webhook
- ✅ **Auto-delete** after successful upload
- ✅ **Clean audio folder** - no file accumulation
- ✅ **Professional quality** recording with proper mixing

## 🚀 **Ready to Use**

Everything is configured and tested:
- Run `start-ffmpeg-recording.bat`
- Talk and play system audio
- Press Ctrl+C when done
- File automatically uploaded and deleted

**Your meeting recorder is now complete and professional!** 🎵✨
