# Audio Sender Guide

The Audio Sender is a batch processing tool that sends all audio files in a target folder to your n8n webhook for processing. This is useful when you have multiple recorded audio files that need to be processed at once.

## Features

- **Batch Processing**: Send all audio files from a folder in one go
- **Multiple Audio Formats**: Supports WAV, MP3, M4A, AAC, FLAC, OGG, WMA
- **Recursive Search**: Optionally search subdirectories for audio files
- **Auto-Delete**: Option to delete files after successful upload
- **Progress Tracking**: Shows upload progress and statistics
- **Error Handling**: Graceful error handling with detailed feedback
- **Rate Limiting**: Optional delay between uploads to avoid overwhelming n8n

## Quick Start

### Windows (Easy Method)
1. Make sure you have `config.json` configured (copy from `config.example.json`)
2. Double-click `send-audio-files.bat`
3. Follow the prompts

### Command Line (All Platforms)

```bash
# Send all audio files from the default folder (from config.json)
python audio_sender.py

# Send files from a specific folder
python audio_sender.py --folder ./my-recordings

# Include subdirectories in the search
python audio_sender.py --recursive

# Delete files after successful upload
python audio_sender.py --delete

# Add delay between uploads (useful for large batches)
python audio_sender.py --delay 2

# Combine options
python audio_sender.py --folder ./recordings --recursive --delete --delay 1
```

## Configuration

The audio sender uses the same `config.json` file as the main meeting recorder:

```json
{
    "n8n_webhook_url": "https://n8n.mreis.uk/webhook/your-webhook-id",
    "credentials": {
        "username": "your-username",
        "password": "your-password"
    },
    "watch_folder": "D:\\study\\AI\\meeting-recorder\\audio"
}
```

### Configuration Options

- `n8n_webhook_url`: Your n8n webhook endpoint URL
- `credentials`: Authentication credentials for the webhook
- `watch_folder`: Default folder to scan for audio files

## Command Line Options

| Option | Short | Description |
|--------|-------|-------------|
| `--folder` | `-f` | Target folder containing audio files |
| `--recursive` | `-r` | Search subdirectories recursively |
| `--delete` | `-d` | Delete files after successful upload |
| `--delay` | | Seconds to wait between uploads |
| `--config` | `-c` | Path to config file (default: config.json) |

## Examples

### Basic Usage
```bash
# Send all audio files from the configured folder
python audio_sender.py
```

### Send from Specific Folder
```bash
# Send all .wav files from a recordings folder
python audio_sender.py --folder ./recordings
```

### Batch Process with Cleanup
```bash
# Send all files and delete them after successful upload
python audio_sender.py --delete
```

### Large Batch with Rate Limiting
```bash
# Process many files with 2-second delay between uploads
python audio_sender.py --recursive --delay 2
```

### Custom Configuration
```bash
# Use a different config file
python audio_sender.py --config ./production-config.json
```

## Supported Audio Formats

The audio sender automatically detects and processes these audio file formats:

- **WAV** (`.wav`) - Uncompressed audio
- **MP3** (`.mp3`) - MPEG audio
- **M4A** (`.m4a`) - MPEG-4 audio
- **AAC** (`.aac`) - Advanced Audio Coding
- **FLAC** (`.flac`) - Free Lossless Audio Codec
- **OGG** (`.ogg`) - Ogg Vorbis
- **WMA** (`.wma`) - Windows Media Audio

## Safety Features

### Confirmation Prompts
When processing multiple files, the audio sender will:
1. Show you all files it found
2. Display file sizes
3. Ask for confirmation before proceeding

### File Verification
- Checks that target folder exists
- Verifies files are actually audio files
- Provides detailed error messages

### Progress Tracking
- Shows current file being processed
- Displays progress (X of Y files)
- Provides success/failure statistics

## Troubleshooting

### Common Issues

**"No audio files found"**
- Check that the target folder exists
- Ensure files have supported extensions
- Try using `--recursive` if files are in subdirectories

**"Config file not found"**
- Make sure `config.json` exists
- Copy `config.example.json` to `config.json` and edit it
- Use `--config` to specify a different config file

**"Upload failed: 401"**
- Check your webhook URL in config.json
- Verify your username/password credentials
- Test the webhook URL in a browser

**"Upload failed: timeout"**
- Your files might be too large
- Try adding `--delay` to slow down uploads
- Check your internet connection

### Debug Mode

For more detailed error information, you can modify the script or check the console output for specific error messages.

## Integration with n8n

The audio sender uses the same upload format as the main meeting recorder, sending:

- **Audio File**: The actual audio data
- **Metadata**: JSON containing file information, timestamps, and source details

Your n8n workflow should be configured to handle the `tray_recording` event type, which is what the audio sender uses as the event identifier.

## Performance Tips

### Large Batches
- Use `--delay` to avoid overwhelming your n8n instance
- Consider processing files in smaller batches
- Monitor your n8n instance for resource usage

### Network Considerations
- Large audio files may take time to upload
- Consider your internet bandwidth when processing many files
- The script will timeout after 60 seconds per file

### Storage Management
- Use `--delete` to automatically clean up processed files
- Make sure you have backups before using auto-delete
- Monitor disk space when processing large batches
