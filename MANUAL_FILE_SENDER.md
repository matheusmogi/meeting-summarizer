# Manual File Sender - Quick Guide

## 🎯 **Purpose**
Send WAV files to your N8N webhook immediately without waiting for the automatic monitoring. Perfect for:
- Sending files before scheduled time
- Uploading older recordings
- Testing webhook functionality
- Batch uploading multiple files

## 🚀 **Quick Start**

### **Method 1: Simple Batch File** ⭐ *Easiest*
```cmd
send-files.bat
```
- Interactive menu with options
- Choose to send all files or specific files

### **Method 2: Command Line** ⭐ *Fast*
```cmd
# Send a specific file
python send_file_manually.py audio/recording.wav

# Send all files in audio folder  
python send_file_manually.py "audio/*.wav"

# Send multiple specific files
python send_file_manually.py file1.wav file2.wav
```

### **Method 3: Interactive Menu** ⭐ *Full Control*
```cmd
python send_file_manually.py
```
Then choose from menu options.

## 📋 **Available Options**

### **Interactive Menu:**
1. **List available WAV files** - See what's in your audio folder
2. **Send a specific file** - Upload one file by path
3. **Send all files in audio folder** - Batch upload everything
4. **Send files matching pattern** - Use wildcards like `*.wav`
5. **Test webhook connection** - Verify connectivity

## 📁 **Your Current Files**

Based on your audio folder, you have:
- `20250821_082306.wav` (6.2 MB) - Actual recording
- `sample_recording.wav` (176 KB) - Test file  
- `test_new_file.wav` (38 bytes) - Test file

## 💡 **Usage Examples**

### **Send Your Main Recording:**
```cmd
python send_file_manually.py audio/20250821_082306.wav
```

### **Send All Your Recordings:**
```cmd
python send_file_manually.py "audio/*.wav"
```

### **Interactive Mode:**
```cmd
python send_file_manually.py
# Then select option 1 to see all files
# Then select option 3 to send them all
```

## ✅ **What Happens**

When you send a file:
1. **Authentication** - Uses credentials from config.json
2. **Upload** - Sends WAV file in `data` field (as requested)
3. **Metadata** - Includes file info in `metadata` field
4. **Status** - Shows success/failure with detailed info
5. **Event Type** - Marked as `manual_upload` (vs `new_recording` for auto-detected)

## 🔧 **Status Messages**

- **✅ File sent successfully!** - Perfect, webhook received it
- **❌ Authentication failed** - Check credentials in config.json  
- **⚠ Server responded with status 404** - N8N webhook not active (click Execute in N8N)
- **❌ File not found** - Check file path
- **❌ Network error** - Check internet connection

## 🎉 **Ready to Use!**

Your authentication is working (we saw 200 responses), so you can now:

**Send your main recording:**
```cmd
python send_file_manually.py audio/20250821_082306.wav
```

**Or use the simple launcher:**
```cmd
send-files.bat
```

The system will send your files immediately to the N8N webhook without waiting for any time schedules! 🚀
